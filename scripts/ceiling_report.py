"""Ceiling controls: the same items at each evidence tier (static / transfer / oracle), one model, paired.

python scripts/ceiling_report.py --model anthropic/claude-haiku-5-5 \
    --tier static data/items.jsonl jobs/valkyrie/l14-l20-haiku-5-5.json jobs/valkyrie/l24-haiku-5-5.json \
    --tier transfer data/items-transfer.jsonl jobs/valkyrie/l14-l20-transfer-haiku-5-5.json ... \
    --tier oracle data/items-oracle.jsonl ...
"""

import argparse
import json
from pathlib import Path

import numpy as np

from neuronbench.baselines import run_baselines, tie_seed
from neuronbench.harbor_tasks import safe_name
from neuronbench.results import collect_jobs, load_items

LOOKUP = {"static": "logit_lens", "transfer": "transfer_words", "oracle": "sweep_words"}
NULL_LOOKUP = {"static": "evidence_logreg", "transfer": "transfer_logreg", "oracle": "sweep_logreg"}


def boot(x, n=10000):
    x = np.asarray(x, dtype=float)
    bs = np.random.default_rng(0).choice(x, (n, len(x))).mean(1)
    return x.mean(), np.quantile(bs, 0.025), np.quantile(bs, 0.975)


def auc(p, y):
    pos = [a for a, b in zip(p, y) if b]
    neg = [a for a, b in zip(p, y) if not b]
    if not pos or not neg:
        return float("nan")
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def reported(jobs, items, model):
    """{item_id: parsed answer} from Valkyrie exports' verifier output (other inputs are skipped)."""
    byname = {safe_name(it["id"]): it["id"] for it in items}
    out = {}
    files = [p for j in map(Path, jobs) for p in ([j] if j.is_file() else sorted(j.rglob("*.json")))]
    for f in files:
        try:
            with open(f) as fh:
                d = json.load(fh)
            if d["benchmark_arguments"]["contract"]["model"] != model:
                continue
            results = d["evaluation_results"]
        except (OSError, ValueError, KeyError, TypeError):
            continue
        for k, v in results.items():
            try:
                parsed = json.loads(v["metadata"]["verifier_output"]).get("parsed")
            except (KeyError, TypeError, ValueError):
                continue
            if k.split("/")[-1] in byname and parsed is not None:
                out[byname[k.split("/")[-1]]] = parsed
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tier", nargs="+", action="append", required=True, metavar=("NAME ITEMS", "JOBS"))
    a = ap.parse_args()
    acc = {}
    rows = []
    for name, items_path, *jobs in a.tier:
        items = load_items(items_path)
        scores = collect_jobs(jobs, items).get(a.model, {}) if jobs else {}
        base = run_baselines(items)
        ch = [it for it in items if it["kind"] == "choice"]
        nu = [it for it in items if it["kind"] == "null"]
        look = np.mean([base[LOOKUP[name]][it["id"]] for it in ch])
        look_brier = 1 - np.mean([base[NULL_LOOKUP[name]][it["id"]] for it in nu])
        lookups = f"{look:.2f} (`{LOOKUP[name]}`) | {look_brier:.3f} (`{NULL_LOOKUP[name]}`)"
        if not scores:
            rows.append(f"| {name} | - | - | - | {lookups} |")
            continue
        acc[name] = {tie_seed(it): scores[it["id"]] for it in ch if it["id"] in scores}
        m, lo, hi = boot(list(acc[name].values())) if acc[name] else (float("nan"),) * 3
        nu_ok = [it for it in nu if it["id"] in scores]
        brier = 1 - np.mean([scores[it["id"]] for it in nu_ok]) if nu_ok else float("nan")
        said = reported(jobs, items, a.model)
        nu_p = [it for it in nu_ok if it["id"] in said]
        a_m = auc([float(said[it["id"]]) for it in nu_p], [bool(it["answer"]["real"]) for it in nu_p])
        rows.append(f"| {name} | {m:.2f} [{lo:.2f}, {hi:.2f}] ({len(acc[name])}/{len(ch)}) | {brier:.3f} | {a_m:.2f} "
                    f"| {lookups} |")
    print(f"model: {a.model}\n")
    print("| tier | choice accuracy, 95% CI (answered) | null Brier | null AUC | choice lookup | null lookup Brier |")
    print("|---|---|---|---|---|---|")
    print("\n".join(rows))
    names = [t[0] for t in a.tier]
    for t in names:
        if t == "static" or "static" not in acc or t not in acc:
            continue
        common = sorted(set(acc[t]) & set(acc["static"]))
        m, lo, hi = boot([acc[t][i] - acc["static"][i] for i in common])
        print(f"\npaired choice accuracy {t} - static: {m:+.2f} [{lo:+.2f}, {hi:+.2f}] (n = {len(common)})")


if __name__ == "__main__":
    main()
