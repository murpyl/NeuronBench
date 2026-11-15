"""Audit the nearest-neighbour distractor fallback in neuronbench/items.py:choice_candidates.

When fewer than 3 random controls fall within match_tol of the real reply's change, the builder keeps the 3 nearest
controls instead of sampling from the band, which can leave the real reply mid-ranking. An item hit that path iff
some distractor's change is more than match_tol from the real reply's (band >= 3 means all three come from the band).

python scripts/fallback_audit.py --items data/items.jsonl --jobs jobs/valkyrie/*.json \
    [--runs <data-branch>/data/raw/L{14,20,24}-main_rel.jsonl]
"""

import argparse
import collections
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_results import load

from neuronbench.baselines import choice_change_rank, choice_most_different
from neuronbench.gne_io import load_run

MATCH_TOL = 0.15


def is_fallback(it, tol=MATCH_TOL):
    c = it["meta"]["change"]
    real = it["answer"]["letter"]
    return any(abs(v - c) > tol for L, v in it["meta"]["option_change"].items() if L != real)


def ci(x, n=10000):
    x = np.asarray(x, dtype=float)
    bs = np.random.default_rng(0).choice(x, (n, len(x))).mean(1)
    return f"{x.mean():.3f} [{np.quantile(bs, 0.025):.2f}, {np.quantile(bs, 0.975):.2f}]"


def real_rank(it):
    """0-based rank of the real reply by change from the unsteered reply (0 = least changed)."""
    oc = it["meta"]["option_change"]
    return sorted(oc, key=lambda L: (oc[L], L)).index(it["answer"]["letter"])


def band_check(it, run, tol=MATCH_TOL):
    """Replay choice_candidates' pool/band logic for this item's (prompt, dose); return (len(band), consistent)."""
    from neuronbench.items import change, clip

    n, dose = it["neuron"], it["payload"]["dose"]
    prompt = next(k for k, t in run.meta["prompts"].items() if t == it["payload"]["prompt"])
    real = run.rollout("neuron", n, prompt, dose)
    base = run.baselines[prompt]
    c_real = change(real["text"], base)
    cands = []
    for j in run.controls():
        r = run.rollout("random", j, prompt, dose)
        if r is not None and (c := change(r["text"], base)) >= 0.1:
            cands.append((abs(c - c_real), j, r, c))
    cands.sort(key=lambda x: (x[0], x[1]))
    pool, seen = [], {clip(real["text"])}
    for cand in cands:
        if clip(cand[2]["text"]) not in seen:
            seen.add(clip(cand[2]["text"]))
            pool.append(cand)
    band = [x for x in pool if x[0] <= tol]
    picked = random.Random(f"{n}|{prompt}|{dose}").sample(band, 3) if len(band) >= 3 else pool[:3]
    same = sorted(j for _, j, _, _ in picked) == sorted(it["meta"]["distractor_controls"])
    return len(band), same, round(c_real, 4) == it["meta"]["change"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--jobs", nargs="+", required=True)
    ap.add_argument("--runs", nargs="*", default=[], help="data-branch sweep JSONLs for the band cross-check")
    ap.add_argument("--n-check", type=int, default=5)
    a = ap.parse_args()
    items, ans = load(a.items, a.jobs)
    ch = [i for i, it in items.items() if it["kind"] == "choice"]
    fb = [i for i in ch if is_fallback(items[i])]
    ok = [i for i in ch if i not in set(fb)]

    print(f"== fallback (some distractor |option_change - change| > {MATCH_TOL}): {len(fb)}/{len(ch)} choice items")
    for name, key in (("layer", lambda it: it["layer"]), ("dose", lambda it: it["payload"]["dose"])):
        tot = collections.Counter(key(items[i]) for i in ch)
        got = collections.Counter(key(items[i]) for i in fb)
        print(f"  per {name}:", ", ".join(f"{g:+g}: {got[g]}/{tot[g]}" if name == "dose" else f"L{g}: {got[g]}/{tot[g]}"
                                         for g in sorted(tot)))
    print("  flagged ids:")
    for i in sorted(fb):
        it = items[i]
        far = max(abs(v - it["meta"]["change"]) for L, v in it["meta"]["option_change"].items()
                  if L != it["answer"]["letter"])
        print(f"    {i}  real-rank {real_rank(it)}  max distractor gap {far:.3f}")

    print("\n== where the real reply sits in the change ranking (0 = least changed .. 3 = most changed)")
    for name, ids in (("flagged", fb), ("non-flagged", ok)):
        r = collections.Counter(real_rank(items[i]) for i in ids)
        print(f"  {name:12s} n={len(ids):3d}  " + "  ".join(f"rank{k}: {r[k]}" for k in range(4)))

    print("\n== change-rank baselines, accuracy with 95% bootstrap CI (chance 0.25)")
    bl = {f"change_rank{r}": (lambda it, r=r: choice_change_rank(it, r)) for r in range(4)}
    bl["most_different"] = choice_most_different
    hdr = [f"flagged (n={len(fb)})", f"non-flagged (n={len(ok)})"]
    print(f"  {'baseline':15s} {hdr[0]:24s} {hdr[1]:24s} all (n={len(ch)})")
    for name, f in bl.items():
        row = [ci([f(items[i]) == items[i]["answer"]["letter"] for i in ids]) for ids in (fb, ok, ch)]
        print(f"  {name:15s} {row[0]:24s} {row[1]:24s} {row[2]}")

    print("\n== model accuracy, flagged vs non-flagged, 95% bootstrap CI")
    for m in ans:
        row = [ci([ans[m][i][2]["choice_acc"] for i in ids]) for ids in (fb, ok)]
        x, y = (np.array([ans[m][i][2]["choice_acc"] for i in ids]) for ids in (fb, ok))
        diff = x.mean() - y.mean()
        rng = np.random.default_rng(0)
        bd = rng.choice(x, (10000, len(x))).mean(1) - rng.choice(y, (10000, len(y))).mean(1)
        print(f"  {m:5s} flagged {row[0]:20s} non-flagged {row[1]:20s} diff {diff:+.3f} "
              f"[{np.quantile(bd, 0.025):+.2f}, {np.quantile(bd, 0.975):+.2f}]")

    print("  per flagged item (1 = correct):")
    for i in sorted(fb):
        print(f"    {i}  " + "  ".join(f"{m} {ans[m][i][2]['choice_acc']:g}" for m in ans))

    if a.runs:
        runs = {r.layer: r for r in map(load_run, a.runs)}
        rng = random.Random(0)
        sample = rng.sample(sorted(fb), min(a.n_check, len(fb))) + rng.sample(sorted(ok), min(a.n_check, len(ok)))
        print(f"\n== cross-check: replay choice_candidates' band on the sweeps ({min(a.n_check, len(fb))} flagged, "
              f"{min(a.n_check, len(ok))} non-flagged; only {len(fb)} flagged exist)")
        agree = 0
        for i in sample:
            nb, same, cmatch = band_check(items[i], runs[items[i]["layer"]])
            flag = i in set(fb)
            agree += (nb < 3) == flag
            print(f"  {i:52s} flag={flag!s:5s} len(band)={nb:2d} band<3={nb < 3!s:5s} "
                  f"distractors reproduced={same} change reproduced={cmatch}")
        print(f"  flag matches len(band) < 3 on {agree}/{len(sample)}")
        allc = [(i, *band_check(items[i], runs[items[i]["layer"]])) for i in ch]
        print(f"  all {len(ch)} items: flag == (len(band) < 3) on "
              f"{sum((nb < 3) == (i in set(fb)) for i, nb, _, _ in allc)}; distractors reproduced on "
              f"{sum(s for _, _, s, _ in allc)}; real change reproduced on {sum(c for *_, c in allc)}")


if __name__ == "__main__":
    main()
