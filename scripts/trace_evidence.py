"""Precompute per-token trace evidence for the trace tiers (see neuronbench/trace.py).

Needs gne and the model (CPU is fine, ~2 min for the 150 choice items); `neuronbench build --tier trace` then reads
the output without the model.

    python scripts/trace_evidence.py --model models/Qwen3-0.6B-Q8_0.gguf --items data/items.jsonl \
        --run data/raw/L*-main_rel.jsonl --out data/traces.jsonl

--items is the static tier (its choice items' ids, neurons and visible replies); --run gives the sweeps' .meta.json
(prompts and chat-templated prompt_ids). --seed must match the build's, so the shuffled donor neurons line up.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neuronbench.gne_io import read_jsonl
from neuronbench.trace import build_traces, lens_z_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--items", default="data/items.jsonl")
    ap.add_argument("--run", nargs="+", required=True, help="sweep JSONL(s); only their .meta.json is read")
    ap.add_argument("--out", default="data/traces.jsonl")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-gpu-layers", type=int, default=0)
    a = ap.parse_args()

    from gne.api import open_model
    s = open_model(a.model, n_gpu_layers=a.n_gpu_layers)
    items = read_jsonl(a.items)
    metas = {}
    for rp in a.run:
        p = Path(rp)
        m = json.loads(p.with_name(p.name.removesuffix(".jsonl") + ".meta.json").read_text())
        if m["model_id"] != s.meta.model_id:
            sys.exit(f"{rp} is {m['model_id']}, but the model is {s.meta.model_id}")
        metas[int(m["layer"])] = m
    traces = build_traces(items, metas, s.engine, lambda L, nn: lens_z_rows(s.weights, L, nn), seed=a.seed)
    Path(a.out).write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in traces))
    base = [t["replies"]["baseline"] for t in traces]
    agree = np.mean([b["base_top"][i] is None for b in base for i in range(len(b["ids"]))])
    print(f"wrote {len(traces)} traces to {a.out}; unsteered replies: top-1 = the reply's own token at {agree:.1%} "
          "of positions (greedy, so ~100% if the re-tokenized text matches what was generated)")


if __name__ == "__main__":
    main()
