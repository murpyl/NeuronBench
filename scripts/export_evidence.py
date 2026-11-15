"""Export agent-visible evidence for every neuron in a gne sweep, one JSON per neuron.

Run on the machine that has gne and the model, after `gne lens logit --layer L` (and optionally `gne stats act`):

    python scripts/export_evidence.py --model models/Qwen3-0.6B-Q8_0.gguf --run ~/.gne/runs/<model_id>/L14-main_rel.jsonl \
        --out data/evidence

Writes data/evidence/<model_id>/L<layer>/N<neuron>.json. Only static fields are kept (see neuronbench.evidence).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neuronbench.evidence import sanitize_dossier
from neuronbench.gne_io import load_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--run", required=True, nargs="+", help="sweep JSONL(s)")
    ap.add_argument("--out", default="data/evidence")
    ap.add_argument("--root", default=None, help="GNE_ROOT, if not the default")
    ap.add_argument("--n-gpu-layers", type=int, default=-1)
    a = ap.parse_args()

    from gne.api import open_model
    kw = {"n_gpu_layers": a.n_gpu_layers}
    if a.root:
        kw["root"] = a.root
    s = open_model(a.model, **kw)
    for rp in a.run:
        run = load_run(rp)
        d = Path(a.out) / run.model_id / f"L{run.layer}"
        d.mkdir(parents=True, exist_ok=True)
        for n in run.neurons():
            ev = sanitize_dossier(s.neuron(run.layer, n, rollouts=0, compute=False))
            if "logit_lens" not in ev:
                sys.exit(f"no logit lens for L{run.layer} N{n}: run `gne lens logit --layer {run.layer}` first")
            (d / f"N{n}.json").write_text(json.dumps(ev, ensure_ascii=False, indent=1))
        print(f"{rp}: {len(run.neurons())} neurons -> {d}")


if __name__ == "__main__":
    main()
