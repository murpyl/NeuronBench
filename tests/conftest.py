import json
import random
from pathlib import Path

import pytest

PROMPTS = {"who": "Who are you?", "orange": "Describe the color orange."}
PAIRS = [["who", 0.5], ["who", 0.8], ["orange", -0.7], ["orange", 0.8], ["orange", 3.0]]
WORDS = ["apple", "river", "castle", "violin", "pepper", "tiger", "cloud", "marble", "rocket", "honey", "ember",
         "falcon", "garnet", "harbor", "island", "jasmine"]


def _rec(kind, n, prompt, dose, text):
    return {"model_id": "toy-0.1b-abc123", "layer": 3, "kind": kind, "neuron": n, "ref_neuron": None, "prompt": prompt,
            "dose": dose, "dose_unit": "rel", "rel_push": abs(dose), "add": 1.0, "text": text, "finish": "length",
            "n_gen": 10, "token_ids": [1, 2, 3], "logprob": [-1.0] * 3, "top_ids": [], "top_lps": [], "seed": 0,
            "batch": 4}


@pytest.fixture
def toy_run(tmp_path: Path) -> Path:
    """A fake ranked gne sweep: 8 neurons (each with a theme word), 6 random controls, 5 conditions."""
    rng = random.Random(0)
    d = tmp_path / "runs"
    d.mkdir()
    base = {k: f"Baseline reply to {v} It is a normal helpful answer with several words." for k, v in PROMPTS.items()}
    recs = [_rec("baseline", None, k, 0.0, t) for k, t in base.items()]
    units = []
    for n in range(8):
        w = WORDS[n]
        for k, dose in PAIRS:
            recs.append(_rec("neuron", n, k, dose, f"{w} {w} {base[k][:20]} {w} and more {w} text {n}"))
        units.append({"layer": 3, "kind": "neuron", "neuron": n, "mass": float(n), "null_pct": n / 7, "rank": 8 - n,
                      "words": [[w, 5, 3.0]], "per_prompt": {w: list(PROMPTS)}, "dose": {}})
    for j in range(6):
        for k, dose in PAIRS:
            recs.append(_rec("random", 100 + j, k, dose,
                             f"{base[k][:25]} {rng.choice(WORDS[8:])} noise {j} {rng.choice(WORDS[8:])} words"))
        units.append({"layer": 3, "kind": "random", "neuron": 100 + j, "mass": 0.5, "null_pct": 0.5, "rank": None,
                      "words": [], "per_prompt": {}, "dose": {}})
    meta = {"model_id": "toy-0.1b-abc123", "layer": 3, "design": "main_rel", "pairs": PAIRS, "prompts": PROMPTS,
            "dose_unit": "rel", "max_tokens": 64, "random_controls": 6, "seed": 0}
    run = d / "L3-main_rel.jsonl"
    half = len(recs) // 2
    run.write_text("".join(json.dumps(r) + "\n" for r in recs[:half]) + '{"truncated":')
    (d / "L3-main_rel.part-w1.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs[half:]))
    (d / "L3-main_rel.meta.json").write_text(json.dumps(meta))
    (d / "L3-main_rel.units.jsonl").write_text("".join(json.dumps(u) + "\n" for u in units))
    ev = tmp_path / "evidence" / "toy-0.1b-abc123" / "L3"
    ev.mkdir(parents=True)
    for n in range(8):
        (ev / f"N{n}.json").write_text(json.dumps({
            "layer": 3, "neuron": n, "down_norm": 1.0 + n / 10, "available": ["down_norm", "logit_lens"],
            "logit_lens": {"up": [f"Ġ{WORDS[n]}", "Ġthe"], "down": ["Ġzzz"], "peak_z": 5.0 + n}}))
    return run
