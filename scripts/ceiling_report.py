"""Evidence-tier controls: the same items at each tier (static / transfer / oracle / shuffled), one model, paired.

shuffled is the wrong-evidence control: each item shows another same-layer neuron's static evidence. Every tier is
also compared with static on the choice items split by whether one of the item's own logit-lens tokens literally
occurs in a candidate reply (from the static items), and on null Brier / AUC, all paired over the same items.

python scripts/ceiling_report.py --model anthropic/claude-haiku-5-5 \
    --tier static data/items.jsonl jobs/valkyrie/l14-l20-haiku-5-5.json jobs/valkyrie/l24-haiku-5-5.json \
    --tier transfer data/items-transfer.jsonl jobs/valkyrie/l14-l20-transfer-haiku-5-5.json ... \
    --tier oracle data/items-oracle.jsonl ... \
    --tier shuffled data/items-shuffled.jsonl jobs/valkyrie/l14-l20-shuffled-haiku-5-5.json ...
"""

import argparse
import json
from pathlib import Path

import numpy as np

from neuronbench.baselines import overlap_pick, run_baselines, tie_seed
from neuronbench.harbor_tasks import safe_name
from neuronbench.results import collect_jobs, load_items

LOOKUP = {"static": "logit_lens", "transfer": "transfer_words", "oracle": "sweep_words", "shuffled": "logit_lens"}
NULL_LOOKUP = {"static": "evidence_logreg", "transfer": "transfer_logreg", "oracle": "sweep_logreg",
               "shuffled": "evidence_logreg"}


def boot(x, n=10000):
    x = np.asarray(x, dtype=float)
    bs = np.random.default_rng(0).choice(x, (n, len(x))).mean(1)
    return x.mean(), np.quantile(bs, 0.025), np.quantile(bs, 0.975)


def boot_paired(stat, n_items, n=2000):
    """stat(index array) -> float, on all items and on n bootstrap resamples of item indices."""
    rng = np.random.default_rng(0)
    bs = [stat(rng.integers(0, n_items, n_items)) for _ in range(n)]
    return stat(np.arange(n_items)), np.nanquantile(bs, 0.025), np.nanquantile(bs, 0.975)


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
    acc, nul, overlap = {}, {}, None
    rows = []
    for name, items_path, *jobs in a.tier:
        items = load_items(items_path)
        scores = collect_jobs(jobs, items).get(a.model, {}) if jobs else {}
        base = run_baselines(items)
        ch = [it for it in items if it["kind"] == "choice"]
        nu = [it for it in items if it["kind"] == "null"]
        if name == "static":
            overlap = {tie_seed(it) for it in ch if overlap_pick(it)[1] > 0}
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
        nul[name] = {tie_seed(it): (float(said[it["id"]]), int(it["answer"]["real"]), scores[it["id"]]) for it in nu_p}
        rows.append(f"| {name} | {m:.2f} [{lo:.2f}, {hi:.2f}] ({len(acc[name])}/{len(ch)}) | {brier:.3f} | {a_m:.2f} "
                    f"| {lookups} |")
    print(f"model: {a.model}\n")
    print("| tier | choice accuracy, 95% CI (answered) | null Brier | null AUC | choice lookup | null lookup Brier |")
    print("|---|---|---|---|---|---|")
    print("\n".join(rows))
    for t in [t[0] for t in a.tier]:
        if t == "static" or "static" not in acc or t not in acc:
            continue
        common = sorted(set(acc[t]) & set(acc["static"]))
        m, lo, hi = boot([acc[t][i] - acc["static"][i] for i in common])
        print(f"\npaired choice accuracy {t} - static: {m:+.2f} [{lo:+.2f}, {hi:+.2f}] (n = {len(common)})")
        for label, ids in (("a lens token appears in a reply", [i for i in common if i in overlap]),
                           ("no lens token in any reply", [i for i in common if i not in overlap])):
            if not ids:
                continue
            cells = [f"{k} {m:.2f} [{lo:.2f}, {hi:.2f}]" for k in ("static", t)
                     for m, lo, hi in [boot([acc[k][i] for i in ids])]]
            m, lo, hi = boot([acc[t][i] - acc["static"][i] for i in ids])
            print(f"  {label} (n = {len(ids)}): {', '.join(cells)}; {t} - static {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")
        if t not in nul or "static" not in nul:
            continue
        both = sorted(set(nul[t]) & set(nul["static"]))
        y = np.array([nul["static"][i][1] for i in both])
        ps, pt = (np.array([nul[k][i][0] for i in both]) for k in ("static", t))
        dr = np.array([nul["static"][i][2] - nul[t][i][2] for i in both])  # rewards are 1 - Brier
        m, lo, hi = boot_paired(lambda ix, dr=dr: dr[ix].mean(), len(both))
        print(f"paired null Brier {t} - static: {m:+.3f} [{lo:+.3f}, {hi:+.3f}] (n = {len(both)}; lower is better)")
        m, lo, hi = boot_paired(lambda ix, ps=ps, pt=pt, y=y: auc(pt[ix], y[ix]) - auc(ps[ix], y[ix]), len(both))
        print(f"paired null AUC {t} - static: {m:+.2f} [{lo:+.2f}, {hi:+.2f}]")

if __name__ == "__main__":
    main()
