"""Pick the neurons to sweep on the extra prompts (extra_prompts/design.yaml) from an existing main_rel sweep.

Only neurons from gne's seeded `random:384` draw are eligible (not the hand-picked logit-lens extras), stratified by
the 3-prompt null_pct so both outcomes are represented: half REAL (>= 0.95), a quarter borderline (0.8-0.95), a quarter
below 0.8. Selection never looks at agent answers or at the replies. The pilot list is a prefix of the full list in
every stratum, so the full sweep resumes the pilot run instead of redoing it.

    python scripts/prompts_select.py --run data/raw/L20-main_rel.jsonl --n 100 --out extra_prompts
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neuronbench.gne_io import load_run

STRATA = (("real", 0.95, 1.01, 0.5), ("border", 0.80, 0.95, 0.25), ("low", -0.01, 0.80, 0.25))


def quotas(n: int) -> dict[str, int]:
    q = {name: round(n * share) for name, *_, share in STRATA}
    q["low"] = n - q["real"] - q["border"]
    return q


def select(units: list[dict], eligible: set[int], n: int, pilot: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    pools = {}
    for name, lo, hi, _ in STRATA:
        ids = sorted(int(u["neuron"]) for u in units if u["kind"] == "neuron" and int(u["neuron"]) in eligible
                     and u["null_pct"] is not None and lo <= u["null_pct"] < hi)
        pools[name] = rng.permutation(ids).tolist()
    qf, qp = quotas(n), quotas(pilot)
    for name, pool in pools.items():
        if len(pool) < qf[name]:
            raise SystemExit(f"stratum {name}: need {qf[name]}, have {len(pool)}")
    full = {name: pools[name][:qf[name]] for name in pools}
    return {"full": full, "pilot": {name: full[name][:qp[name]] for name in full}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, nargs="+", help="main_rel sweep JSONL(s) with .units.jsonl next to them")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--pilot", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="extra_prompts")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for rp in a.run:
        run = load_run(rp)
        eligible = run.random_neurons(384)
        if eligible is None:
            raise SystemExit(f"{rp}: cannot recover the random:384 draw")
        sel = select(run.units, eligible, a.n, a.pilot, a.seed + run.layer)
        rec = {"layer": run.layer, "model_id": run.model_id, "source_run": Path(rp).name, "seed": a.seed + run.layer,
               "strata": {name: [lo, hi] for name, lo, hi, _ in STRATA}, **sel}
        (out / f"neurons-L{run.layer}.json").write_text(json.dumps(rec, indent=1) + "\n")
        for k in ("full", "pilot"):
            ids = sorted(i for v in sel[k].values() for i in v)
            (out / f"neurons-L{run.layer}-{k}.txt").write_text(",".join(map(str, ids)) + "\n")
        print(f"L{run.layer}: full {sum(map(len, sel['full'].values()))}, pilot {sum(map(len, sel['pilot'].values()))} "
              f"({ {k: len(v) for k, v in sel['full'].items()} })")


if __name__ == "__main__":
    main()
