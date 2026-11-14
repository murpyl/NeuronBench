"""Turn a gne sweep into eval items.

Two item kinds, both about one neuron at a time:

- choice: the neuron was pushed by a dose on a prompt; pick the real reply out of four. The three distractors are
  replies from random-direction controls pushed with the same rel dose on the same prompt, chosen to be as far
  from the unsteered reply as the real one, so "pick the most broken reply" does not work.
- null: does pushing this neuron change the vocabulary of the replies more than the random controls do
  (gne rank's null_pct >= threshold)? The agent answers with a probability.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from functools import cache

from .gne_io import Run

LETTERS = "ABCD"
MAX_CHARS = 700


@dataclass
class Item:
    id: str
    kind: str
    model_id: str
    layer: int
    neuron: int
    evidence: dict
    payload: dict           # everything the instruction shows
    answer: dict            # hidden from the agent
    meta: dict = field(default_factory=dict)   # strata and diagnostics, hidden from the agent


@cache
def change(text: str, base: str) -> float:
    """1 - similarity to the unsteered reply (0 = identical, 1 = nothing in common)."""
    return 1.0 - SequenceMatcher(None, text, base, autojunk=False).ratio()


def clip(text: str) -> str:
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + " [...]"


def _short_model(model_id: str) -> str:
    return model_id.rsplit("-", 1)[0] if "-" in model_id else model_id


def protocol(run: Run) -> dict:
    m = run.meta
    return {"model_id": m["model_id"], "layer": run.layer, "design": m["design"],
            "conditions": [{"prompt": m["prompts"][k], "prompt_key": k, "dose": d} for k, d in m["pairs"]],
            "dose_unit": m.get("dose_unit", "rel"), "max_tokens": m.get("max_tokens"),
            "random_controls": len(run.controls()), "decoding": "greedy"}


def choice_candidates(run: Run, n: int, *, min_change: float = 0.1, max_dose: float = 1.6,
                      match_tol: float = 0.15) -> list[dict]:
    """Every usable (prompt, dose) condition for neuron n, with its three matched distractors.

    Doses above max_dose (the design's deliberate "break it" condition) are skipped: every reply there is noise.
    """
    out = []
    for prompt, dose in run.conditions("neuron", n):
        if abs(dose) > max_dose:
            continue
        real = run.rollout("neuron", n, prompt, dose)
        base = run.baselines.get(prompt)
        if real is None or base is None:
            continue
        c_real = change(real["text"], base)
        if c_real < min_change:
            continue
        cands = []
        for j in run.controls():
            r = run.rollout("random", j, prompt, dose)
            if r is None:
                continue
            c = change(r["text"], base)
            if c >= min_change:
                cands.append((abs(c - c_real), j, r, c))
        cands.sort(key=lambda x: (x[0], x[1]))
        pool, seen = [], {clip(real["text"])}
        for cand in cands:
            if clip(cand[2]["text"]) not in seen:
                seen.add(clip(cand[2]["text"]))
                pool.append(cand)
        if len(pool) < 3:
            continue
        # Sample from every control within match_tol rather than the 3 nearest: nearest-on-both-sides leaves the real
        # reply in the middle of the change ranking, which a "pick the median" shortcut can exploit.
        band = [x for x in pool if x[0] <= match_tol]
        if len(band) >= 3:
            pool = random.Random(f"{n}|{prompt}|{dose}").sample(band, 3)
        out.append({"prompt": prompt, "dose": dose, "real": real, "change": c_real,
                    "distractors": [(j, r, c) for _, j, r, c in pool[:3]]})
    return out


def make_choice_item(run: Run, n: int, cand: dict, evidence: dict, rng: random.Random) -> Item:
    options = [("neuron", n, cand["real"]["text"], cand["change"])]
    options += [("random", j, r["text"], c) for j, r, c in cand["distractors"]]
    rng.shuffle(options)
    correct = next(i for i, o in enumerate(options) if o[0] == "neuron")
    unit = run.unit("neuron", n) or {}
    prompt_text = run.meta["prompts"][cand["prompt"]]
    item_id = f"choice-{_short_model(run.model_id)}-L{run.layer}-N{n}-{cand['prompt']}{cand['dose']:+g}"
    return Item(
        id=item_id, kind="choice", model_id=run.model_id, layer=run.layer, neuron=n, evidence=evidence,
        payload={"prompt": prompt_text, "dose": cand["dose"], "dose_unit": run.meta.get("dose_unit", "rel"),
                 "baseline": clip(run.baselines[cand["prompt"]]),
                 "options": {LETTERS[i]: clip(o[2]) for i, o in enumerate(options)},
                 "max_tokens": run.meta.get("max_tokens")},
        answer={"letter": LETTERS[correct]},
        meta={"null_pct": unit.get("null_pct"), "mass": unit.get("mass"), "change": round(cand["change"], 4),
              "distractor_controls": [o[1] for o in options if o[0] == "random"],
              "option_change": {LETTERS[i]: round(o[3], 4) for i, o in enumerate(options)}},
    )


def make_null_item(run: Run, n: int, evidence: dict, threshold: float) -> Item:
    unit = run.unit("neuron", n)
    real = unit["null_pct"] >= threshold
    return Item(
        id=f"null-{_short_model(run.model_id)}-L{run.layer}-N{n}", kind="null", model_id=run.model_id,
        layer=run.layer, neuron=n, evidence=evidence,
        payload={"protocol": protocol(run), "threshold": threshold,
                 "baselines": {run.meta["prompts"][k]: clip(t) for k, t in run.baselines.items()}},
        answer={"real": int(real)},
        meta={"null_pct": unit["null_pct"], "mass": unit["mass"], "rank": unit.get("rank")},
    )


def _bins(values: list[tuple[float, int]], k: int) -> list[list[int]]:
    """Split neuron ids into k quantile bins of value."""
    s = sorted(values)
    return [[n for _, n in s[i * len(s) // k:(i + 1) * len(s) // k]] for i in range(k)]


def _take_stratified(strata: list[list[int]], n: int, rng: random.Random) -> list[int]:
    pools = [rng.sample(s, len(s)) for s in strata if s]
    out = []
    while len(out) < n and any(pools):
        for p in pools:
            if p and len(out) < n:
                out.append(p.pop())
    return out


def build_items(run: Run, evidence: dict[int, dict], *, n_choice: int, n_null: int, seed: int = 0,
                threshold: float = 0.95, real_share: float = 0.5, min_change: float = 0.1) -> list[Item]:
    rng = random.Random(f"{seed}-{run.model_id}-{run.layer}")
    neurons = [n for n in run.neurons() if n in evidence and run.unit("neuron", n) is not None]
    items: list[Item] = []

    cands = {n: choice_candidates(run, n, min_change=min_change) for n in neurons}
    usable = [n for n in neurons if cands[n]]
    strata = _bins([(run.unit("neuron", n)["mass"], n) for n in usable], 4) if usable else []
    for n in _take_stratified(strata, n_choice, rng):
        items.append(make_choice_item(run, n, rng.choice(cands[n]), evidence[n], rng))

    real = [n for n in neurons if run.unit("neuron", n)["null_pct"] >= threshold]
    null = [n for n in neurons if run.unit("neuron", n)["null_pct"] < threshold]
    n_real = min(len(real), round(n_null * real_share))
    n_nul = min(len(null), n_null - n_real)
    near = [n for n in null if run.unit("neuron", n)["null_pct"] >= 0.5]
    far = [n for n in null if run.unit("neuron", n)["null_pct"] < 0.5]
    picked = rng.sample(real, n_real) + _take_stratified([near, far], n_nul, rng)
    items += [make_null_item(run, n, evidence[n], threshold) for n in sorted(picked)]
    return items
