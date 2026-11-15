"""Turn a gne sweep into eval items.

Two item kinds, both about one neuron at a time:

- choice: the neuron was pushed by a dose on a prompt; pick the real reply out of four. The three distractors are
  replies from random-direction controls pushed with the same rel dose on the same prompt, chosen to be as far
  from the unsteered reply as the real one, so "pick the most broken reply" does not work.
- null: does pushing this neuron change the vocabulary of the replies more than the random controls do
  (gne rank's null_pct >= threshold)? The agent answers with a probability.

Every item is built at an evidence tier. "static" (the benchmark) shows only weight-derived evidence. "oracle" and
"transfer" are positive controls that add measured outcomes of pushing the neuron, to test whether the task format is
solvable when the evidence is decisive. "shuffled" is a negative control: each item shows the static evidence of a
different neuron from the same layer, so the evidence points at nothing. All tiers reuse the static items' seeds, so
items match one-for-one.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from functools import cache

from .gne_io import Run, dose_key

LETTERS = "ABCD"
MAX_CHARS = 700
TIERS = ("static", "oracle", "transfer", "shuffled")


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


def _selection(run: Run, n: int) -> str:
    drawn = run.random_neurons()
    if drawn is None:
        return "unknown"
    return "random" if n in drawn else "picked"


def augment_evidence(evidence: dict, run: Run, n: int, cand: dict | None, tier: str) -> dict:
    """Evidence for an item at `tier`. cand is the choice condition, or None for a null item.

    oracle: the words the neuron's steered replies over-use (gne rank's `words`); with z-scores for null items.
    transfer: the neuron's steered replies on other prompts (choice: the other prompts at the item's dose;
    null: one prompt at its three |dose| <= 1.6 doses).
    shuffled: unchanged here; build_items swaps in another neuron's evidence (see shuffled_donors).
    """
    if tier in ("static", "shuffled"):
        return evidence
    if tier not in TIERS:
        raise ValueError(f"unknown tier {tier!r}; expected one of {TIERS}")
    ev = dict(evidence)
    prompts = run.meta["prompts"]
    if tier == "oracle":
        words = (run.unit("neuron", n) or {}).get("words") or []
        ev["sweep_words"] = ([w[0] for w in words] if cand is not None
                             else [{"word": w[0], "z": round(float(w[2]), 2)} for w in words])
    elif cand is not None:
        ev["steered_elsewhere"] = {prompts[p]: clip(r["text"]) for p, d in run.conditions("neuron", n)
                                   if p != cand["prompt"] and dose_key(d) == dose_key(cand["dose"])
                                   and (r := run.rollout("neuron", n, p, d)) is not None}
    else:
        conds = [(p, d) for p, d in run.conditions("neuron", n) if abs(d) <= 1.6]
        p = random.Random(f"transfer|{run.layer}|{n}").choice(sorted({p for p, _ in conds}))
        ev["steered_replies"] = {"prompt": prompts[p],
                                 "replies": {f"{d:+g}": clip(run.rollout("neuron", n, p, d)["text"])
                                             for q, d in conds if q == p}}
    ev["available"] = sorted(k for k in ev if k not in ("layer", "neuron", "available"))
    return ev


def _tier_id(item_id: str, tier: str) -> str:
    if tier == "static":
        return item_id
    kind, rest = item_id.split("-", 1)
    return f"{kind}-{tier}-{rest}"


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
              "selection": _selection(run, n),
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
        meta={"null_pct": unit["null_pct"], "mass": unit["mass"], "rank": unit.get("rank"),
              "selection": _selection(run, n)},
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


def _spread(cands: list[dict], k: int, used: dict[str, int], rng: random.Random) -> list[dict]:
    """Up to k of one neuron's conditions on distinct prompts, preferring the prompts used least so far."""
    by_prompt: dict[str, list[dict]] = {}
    for c in cands:
        by_prompt.setdefault(c["prompt"], []).append(c)
    order = sorted(by_prompt, key=lambda p: (used.get(p, 0), rng.random()))
    out = [rng.choice(by_prompt[p]) for p in order[:k]]
    for c in out:
        used[c["prompt"]] = used.get(c["prompt"], 0) + 1
    return out


def shuffled_donors(neurons: list[int], seed: int, layer: int, kind: str) -> dict[int, int]:
    """{neuron: neuron whose evidence it shows} for the shuffled tier, among one kind's items in one layer.

    Sattolo's algorithm draws a random single-cycle permutation, so no neuron keeps its own evidence and every
    evidence block of that kind is shown exactly once (each kind's evidence mix matches the static tier's).
    """
    order = sorted(set(neurons))
    if len(order) < 2:
        raise ValueError("the shuffled tier needs at least two neurons per layer")
    perm = order[:]
    rng = random.Random(f"shuffled|{seed}|{layer}|{kind}")
    for i in range(len(perm) - 1, 0, -1):
        j = rng.randrange(i)
        perm[i], perm[j] = perm[j], perm[i]
    return dict(zip(order, perm))


def build_items(run: Run, evidence: dict[int, dict], *, n_choice: int, n_null: int, seed: int = 0,
                threshold: float = 0.95, real_share: float = 0.5, min_change: float = 0.1,
                tier: str = "static", per_neuron: int = 1) -> list[Item]:
    """per_neuron > 1: that many choice items per picked neuron (neurons with fewer usable prompts are skipped), each
    on a different prompt, balancing how often each prompt is used. per_neuron=1 keeps one random condition per
    neuron."""
    rng = random.Random(f"{seed}-{run.model_id}-{run.layer}")
    neurons = [n for n in run.neurons() if n in evidence and run.unit("neuron", n) is not None]
    items: list[Item] = []

    cands = {n: choice_candidates(run, n, min_change=min_change) for n in neurons}
    # every picked neuron gets exactly per_neuron items, so the shuffled tier's one-to-one donor swap still shows each
    # evidence block as often as the static tier does
    usable = [n for n in neurons if len({c["prompt"] for c in cands[n]}) >= per_neuron]
    strata = _bins([(run.unit("neuron", n)["mass"], n) for n in usable], 4) if usable else []
    used: dict[str, int] = {}
    for n in _take_stratified(strata, n_choice, rng):
        for cand in [rng.choice(cands[n])] if per_neuron == 1 else _spread(cands[n], per_neuron, used, rng):
            items.append(make_choice_item(run, n, cand, augment_evidence(evidence[n], run, n, cand, tier), rng))

    real = [n for n in neurons if run.unit("neuron", n)["null_pct"] >= threshold]
    null = [n for n in neurons if run.unit("neuron", n)["null_pct"] < threshold]
    n_real = min(len(real), round(n_null * real_share))
    n_nul = min(len(null), n_null - n_real)
    near = [n for n in null if run.unit("neuron", n)["null_pct"] >= 0.5]
    far = [n for n in null if run.unit("neuron", n)["null_pct"] < 0.5]
    picked = rng.sample(real, n_real) + _take_stratified([near, far], n_nul, rng)
    items += [make_null_item(run, n, augment_evidence(evidence[n], run, n, None, tier), threshold)
              for n in sorted(picked)]
    if tier == "shuffled":
        donor = {kind: shuffled_donors([it.neuron for it in items if it.kind == kind], seed, run.layer, kind)
                 for kind in {it.kind for it in items}}
        for it in items:
            d = donor[it.kind][it.neuron]
            # keep layer/neuron naming the item's own neuron so the swap is not visible
            it.evidence = {**evidence[d], "layer": it.layer, "neuron": it.neuron}
            it.meta["evidence_neuron"] = d
    if tier != "static":
        for it in items:
            it.id = _tier_id(it.id, tier)
            it.meta["tier"] = tier
    return items
