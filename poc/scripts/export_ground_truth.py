"""Export a gne sweep + logit lens into one compact JSON file the task builder reads.

Run with the gne virtualenv (needs numpy and gne's vocab loader):

    gguf-neuron-explorer/.venv/bin/python scripts/export_ground_truth.py \
        --model gguf-neuron-explorer/models/Qwen3-0.6B-Q8_0.gguf --layer 14

Reads   ~/.gne/runs/<model_id>/L<layer>-<design>.jsonl   (from `gne sweep --layer N`)
        ~/.gne/lens/<model_id>/logit_L<layer>.npz        (from `gne lens logit --layer N`)
Writes  data/<model_id>_L<layer>.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="path to the GGUF file (for the vocabulary)")
    ap.add_argument("--layer", type=int, required=True)
    ap.add_argument("--design", default="main_rel")
    ap.add_argument("--gne-root", default=os.path.expanduser("~/.gne"))
    ap.add_argument("--model-id", default=None, help="defaults to the only model under <gne-root>/runs")
    ap.add_argument("--lens-top", type=int, default=12)
    args = ap.parse_args()

    gne_root = Path(args.gne_root)
    model_id = args.model_id or sorted(p.name for p in (gne_root / "runs").iterdir() if p.is_dir())[0]
    run = gne_root / "runs" / model_id / f"L{args.layer}-{args.design}"
    meta = json.loads(run.with_suffix(".meta.json").read_text())
    rows = [json.loads(line) for line in run.with_suffix(".jsonl").open()]

    sys.path.insert(0, str(ROOT / "gguf-neuron-explorer"))
    from gne.vocab import Vocab

    vocab = Vocab(args.model)
    lens = np.load(gne_root / "lens" / model_id / f"logit_L{args.layer}.npz")
    lens_index = {int(n): i for i, n in enumerate(lens["neurons"])}

    def lens_tokens(neuron: int, which: str) -> list[dict]:
        i = lens_index[neuron]
        ids, zs = lens[f"{which}_ids"][i], lens[f"{which}_z"][i]
        return [{"token": vocab.text(int(t)), "z": round(float(z), 2)} for t, z in list(zip(ids, zs))[: args.lens_top]]

    def key(prompt: str, dose: float) -> str:
        return f"{prompt}@{dose:+.1f}"

    baselines = {r["prompt"]: r["text"] for r in rows if r["kind"] == "baseline"}
    units: dict[str, dict] = {}
    for r in rows:
        if r["kind"] == "baseline":
            continue
        uid = ("N" if r["kind"] == "neuron" else "R") + str(r["neuron"])
        u = units.setdefault(uid, {"id": uid, "kind": r["kind"], "neuron": r["neuron"], "rollouts": {}})
        u["rollouts"][key(r["prompt"], r["dose"])] = {"text": r["text"], "finish": r["finish"], "n_gen": r["n_gen"]}

    expected = {key(p, d) for p, d in meta["pairs"]}
    complete = []
    for u in units.values():
        if set(u["rollouts"]) != expected:
            continue  # sweep still running or interrupted: skip partial units
        if u["kind"] == "neuron":
            u["lens_up"] = lens_tokens(u["neuron"], "up")
            u["lens_down"] = lens_tokens(u["neuron"], "down")
        complete.append(u)

    out = {
        "model_id": model_id,
        "model_name": "Qwen3-0.6B (Q8_0 GGUF, llama.cpp)",
        "layer": args.layer,
        "design": args.design,
        "pairs": meta["pairs"],
        "prompts": meta["prompts"],
        "dose_unit": meta["dose_unit"],
        "resid_p50": meta["resid_p50"],
        "max_tokens": meta["max_tokens"],
        "baselines": baselines,
        "units": complete,
    }
    dest = ROOT / "data" / f"{model_id}_L{args.layer}.json"
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    n_neuron = sum(u["kind"] == "neuron" for u in complete)
    print(f"wrote {dest}: {n_neuron} neurons, {len(complete) - n_neuron} random controls "
          f"({len(units) - len(complete)} partial units skipped)")


if __name__ == "__main__":
    main()
