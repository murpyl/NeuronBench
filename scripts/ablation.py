"""Paired v1-vs-ablated comparison of the same model on the same items (instruction ablation).

python scripts/ablation.py --items data/items.jsonl \
    --v1 jobs/valkyrie/l14-l20-haiku-5-5.json jobs/valkyrie/l24-haiku-5-5.json \
    --ablated jobs/valkyrie/l14-l20-haiku-5-5-ablated.json jobs/valkyrie/l24-haiku-5-5-ablated.json \
    [--traj-v1 v1.jsonl.gz --traj-ablated ablated.jsonl.gz]

Exports are `valkyrie run results <id> --path x.json`; the model is read from each export. Trajectory files are
JSONL (optionally gzipped) with one row per trial: {"model": <contract model>, "task": <task dir>, "msgs":
[{"role", "text"}]}, as written by `--extract <valkyrie run outputs dir> <model>`.
"""

import argparse
import glob
import gzip
import json
import os
import re
import statistics as st
from collections import Counter

import numpy as np

from neuronbench.harbor_tasks import safe_name

# Over-reading the dose guide: "+0.5 should be subtle, so pick the gentlest / closest-to-baseline reply"
# (the "least changed/subtle" tag behind the Dose folklore row of results/analysis.md).
DOSE_FOLKLORE = re.compile(
    r"(closest|closer|close) to (the )?(baseline|unsteered|original|unperturbed)|subtle|minimal(ly)? (change|perturb)"
    r"|least (changed|disrupted)|stays? close",
    re.IGNORECASE,
)
B = 10000


def load(paths, byname):
    """{model: {item_id: (parsed answer, reward)}} from Valkyrie exports."""
    out = {}
    for f in paths:
        with open(f) as fh:
            d = json.load(fh)
        m = d["benchmark_arguments"]["contract"]["model"]
        for task, v in d["evaluation_results"].items():
            it = byname[task.split("/")[-1]]
            try:
                parsed = json.loads(v["metadata"]["verifier_output"]).get("parsed")
            except (KeyError, TypeError, ValueError):
                parsed = None
            key = "choice_acc" if it["kind"] == "choice" else "null_brier"
            out.setdefault(m, {})[it["id"]] = (parsed, float((v.get("rewards") or {}).get(key) or 0.0))
    return out


def open_any(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def load_traj(paths):
    rows = {}
    for p in paths or []:
        with open_any(p) as fh:
            for line in fh:
                r = json.loads(line)
                text = " | ".join(x["text"] for x in r["msgs"] if x["role"] == "assistant")
                rows.setdefault(r["model"], {})[r["task"]] = text
    return rows


def extract(out_dir, model, dest):
    """Compact a `valkyrie run outputs` directory into trajectory JSONL rows (appends to dest)."""
    n = 0
    with open(dest, "a") as out:
        for f in sorted(glob.glob(os.path.join(out_dir, "*", "mini_swe_agent", "trajectory.json"))):
            try:
                with open(f) as fh:
                    t = json.load(fh)
            except (OSError, ValueError):
                continue
            msgs = []
            for m in t.get("messages", []):
                if m["role"] == "system":
                    continue
                c = m.get("content")
                c = c if isinstance(c, str) else ("" if c is None else json.dumps(c))
                for tc in m.get("tool_calls") or [] if m["role"] == "assistant" else []:
                    fn = tc.get("function", {}) if isinstance(tc, dict) else {}
                    c += " [tool_call] " + str(fn.get("arguments", ""))[:1500]
                if m["role"] == "user" and not msgs:
                    c = "[task]"
                if m["role"] == "tool":
                    c = c[:300]
                msgs.append({"role": m["role"], "text": c[:1800]})
            task = f.split(os.sep)[-3]
            out.write(json.dumps({"model": model, "task": task, "stats": t.get("info", {}).get("model_stats"),
                                  "msgs": msgs}) + "\n")
            n += 1
    print(f"{n} trajectories from {out_dir} -> {dest}")


def auc(p, y):
    real = [a for a, b in zip(p, y) if b]
    nul = [a for a, b in zip(p, y) if not b]
    return st.mean((r > n) + 0.5 * (r == n) for r in real for n in nul)


def paired_ci(f, n, seed=0):
    """95% bootstrap CI of f(idx) over resampled item indices (same indices for both conditions)."""
    rng = np.random.default_rng(seed)
    vals = np.array([f(rng.integers(0, n, n)) for _ in range(B)])
    return np.quantile(vals, 0.025), np.quantile(vals, 0.975)


def prob(x):
    try:
        p = float(x)
    except (TypeError, ValueError):
        return None
    return p if 0 <= p <= 1 else None


def compare(m, r0, r1, items, t0, t1):
    """Paired v1 (r0) vs ablated (r1) comparison for one model; prints details and returns a summary row."""
    print(f"\n== {m}")
    row = {"model": m}
    ch = sorted(i for i in items if items[i]["kind"] == "choice" and i in r0 and i in r1)
    x0 = np.array([r0[i][1] for i in ch])
    x1 = np.array([r1[i][1] for i in ch])
    lo, hi = paired_ci(lambda k: x1[k].mean() - x0[k].mean(), len(ch))
    up, down = int(((x0 == 0) & (x1 == 1)).sum()), int(((x0 == 1) & (x1 == 0)).sum())
    same = st.mean(r0[i][0] == r1[i][0] for i in ch)
    row["choice"] = {"n": len(ch), "v1": x0.mean(), "ablated": x1.mean(), "diff": x1.mean() - x0.mean(),
                     "ci": [lo, hi], "wrong_to_right": up, "right_to_wrong": down, "same_letter": same}
    print(f"  choice (n={len(ch)} paired): v1 {x0.mean():.3f}  ablated {x1.mean():.3f}  "
          f"diff {x1.mean() - x0.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  wrong->right {up}, right->wrong {down}, "
          f"same letter {same:.2f}")

    ni = sorted(i for i in items if items[i]["kind"] == "null" and i in r0 and i in r1)
    y = np.array([bool(items[i]["answer"]["real"]) for i in ni])
    b0 = 1 - np.array([r0[i][1] for i in ni])
    b1 = 1 - np.array([r1[i][1] for i in ni])
    p0 = [prob(r0[i][0]) for i in ni]
    p1 = [prob(r1[i][0]) for i in ni]
    bad = sum(p is None for p in p0 + p1)
    # unparseable answers score as maximally wrong in the grader; for AUC and the mean they count as 0.5
    q0 = np.array([0.5 if p is None else p for p in p0])
    q1 = np.array([0.5 if p is None else p for p in p1])
    lo, hi = paired_ci(lambda k: b1[k].mean() - b0[k].mean(), len(ni))
    print(f"  null Brier (n={len(ni)} paired, lower is better): v1 {b0.mean():.3f}  ablated {b1.mean():.3f}  "
          f"diff {b1.mean() - b0.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  ({bad} unparseable answers)")

    def dauc(k):
        return np.nan if y[k].all() or not y[k].any() else auc(q1[k], y[k]) - auc(q0[k], y[k])

    rng = np.random.default_rng(0)
    vals = np.array([dauc(rng.integers(0, len(ni), len(ni))) for _ in range(2000)])
    vals = vals[~np.isnan(vals)]
    a0, a1 = auc(q0, y), auc(q1, y)
    alo, ahi = np.quantile(vals, 0.025), np.quantile(vals, 0.975)
    print(f"  null AUC: v1 {a0:.3f}  ablated {a1:.3f}  diff {a1 - a0:+.3f} [{alo:+.3f}, {ahi:+.3f}]")

    def mid(q):
        return float(((q >= 0.4) & (q <= 0.6)).mean())

    const0, const1 = ((q0.mean() - y) ** 2).mean(), ((q1.mean() - y) ** 2).mean()
    print(f"  null mean prob: v1 {q0.mean():.3f}  ablated {q1.mean():.3f}  (base rate {y.mean():.3f});  "
          f"share in [0.4, 0.6]: v1 {mid(q0):.2f}  ablated {mid(q1):.2f};  "
          f"Brier if constant at own mean: v1 {const0:.3f}  ablated {const1:.3f}")
    for tag, q in (("v1", q0), ("ablated", q1)):
        print(f"  null answers {tag}: {dict(sorted(Counter(round(float(p), 2) for p in q).items()))}")
    row["null"] = {"n": len(ni), "base_rate": float(y.mean()), "unparseable": bad,
                   "brier_v1": b0.mean(), "brier_ablated": b1.mean(), "brier_diff": b1.mean() - b0.mean(),
                   "brier_ci": [lo, hi], "auc_v1": a0, "auc_ablated": a1, "auc_diff": a1 - a0, "auc_ci": [alo, ahi],
                   "mean_p_v1": q0.mean(), "mean_p_ablated": q1.mean(), "mid_v1": mid(q0), "mid_ablated": mid(q1),
                   "const_brier_v1": const0, "const_brier_ablated": const1}

    for tag, tr, res in (("v1", t0, r0), ("ablated", t1, r1)):
        if not tr:
            continue
        got = [i for i in ch if safe_name(i) in tr]
        hits = [i for i in got if DOSE_FOLKLORE.search(tr[safe_name(i)])]
        wr = st.mean(res[i][1] == 0 for i in hits) if hits else float("nan")
        row[f"folklore_{tag}"] = {"hits": len(hits), "of": len(got), "wrong_rate": wr}
        print(f"  dose folklore ({tag}): {len(hits)} of {len(got)} choice trajectories, {wr:.0%} wrong")
    return json.loads(json.dumps(row, default=float))


def table(rows):
    head = ("| model | choice acc v1 → ablated | diff [95% paired CI] | null Brier v1 → ablated | diff [CI] | "
            "null AUC v1 → ablated | mean P(real) v1 → ablated | share in 0.4–0.6 v1 → ablated | "
            "dose folklore v1 → ablated |")
    out = [head, "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        c, n = r["choice"], r["null"]
        fv1, fab = r.get("folklore_v1"), r.get("folklore_ablated")
        fl = f"{fv1['hits']} → {fab['hits']}" if fv1 and fab else ""
        out.append(
            f"| {r['model']} | {c['v1']:.3f} → {c['ablated']:.3f} | {c['diff']:+.3f} [{c['ci'][0]:+.3f}, "
            f"{c['ci'][1]:+.3f}] | {n['brier_v1']:.3f} → {n['brier_ablated']:.3f} | {n['brier_diff']:+.3f} "
            f"[{n['brier_ci'][0]:+.3f}, {n['brier_ci'][1]:+.3f}] | {n['auc_v1']:.2f} → {n['auc_ablated']:.2f} | "
            f"{n['mean_p_v1']:.2f} → {n['mean_p_ablated']:.2f} | {n['mid_v1']:.2f} → {n['mid_ablated']:.2f} | {fl} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="data/items.jsonl")
    ap.add_argument("--v1", nargs="+")
    ap.add_argument("--ablated", nargs="+")
    ap.add_argument("--traj-v1", nargs="*")
    ap.add_argument("--traj-ablated", nargs="*")
    ap.add_argument("--out", help="write the summary rows as JSON")
    ap.add_argument("--extract", nargs=3, metavar=("OUTPUTS_DIR", "MODEL", "DEST_JSONL"))
    a = ap.parse_args()
    if a.extract:
        return extract(*a.extract)
    with open(a.items) as fh:
        items = {(it := json.loads(line))["id"]: it for line in fh}
    byname = {safe_name(i): it for i, it in items.items()}
    v1, ab = load(a.v1, byname), load(a.ablated, byname)
    tv1, tab = load_traj(a.traj_v1), load_traj(a.traj_ablated)
    rows = [compare(m, v1[m], ab[m], items, tv1.get(m), tab.get(m)) for m in ab if m in v1]
    print("\n" + table(rows))
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(rows, fh, indent=1)

if __name__ == "__main__":
    main()
