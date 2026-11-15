"""Slice the Valkyrie exports behind results/: splits, agreement, token-overlap, null calibration.

python scripts/analyze_results.py --items data/items.jsonl --jobs jobs/valkyrie/*.json
"""

import argparse
import collections
import itertools
import json
import re
import statistics as st

import numpy as np

from neuronbench.harbor_tasks import safe_name

SHORT = {
    "anthropic/claude-haiku-4-5": "H4.5",
    "anthropic/claude-haiku-5-5": "H5.5",
    "anthropic/claude-sonnet-5-5": "S5.5",
    "openai/gpt-5.6-luna": "GPT",
}


def load(items_path, job_paths):
    items = {json.loads(l)["id"]: json.loads(l) for l in open(items_path)}
    byname = {safe_name(i): i for i in items}
    ans = {}
    for f in job_paths:
        d = json.load(open(f))
        m = d["benchmark_arguments"]["contract"]["model"]
        for k, v in d["evaluation_results"].items():
            try:
                vo = json.loads(v["metadata"]["verifier_output"])
            except Exception:
                vo = {}
            ans.setdefault(SHORT.get(m, m), {})[items[byname[k]]["id"]] = (
                vo.get("parsed"),
                vo.get("key"),
                v["rewards"],
            )
    return items, ans


def lens_tokens(ev):
    ll = ev.get("logit_lens") or {}
    out = []
    for k in ("up", "down"):
        for t in ll.get(k) or []:
            s = (t if isinstance(t, str) else str(t)).strip()
            if len(s) >= 3 and re.fullmatch(r"[A-Za-z]+", s):
                out.append(s.lower())
    return out


def overlap_pick(it):
    ts = lens_tokens(it["evidence"])
    sc = {L: sum(o.lower().count(t) for t in ts) for L, o in it["payload"]["options"].items()}
    best = max(sc.values())
    return [L for L, v in sc.items() if v == best], best


def spearman(x, y):
    rx = {v: i for i, v in enumerate(sorted(x))}
    ry = {v: i for i, v in enumerate(sorted(y))}
    return float(np.corrcoef([rx[v] for v in x], [ry[v] for v in y])[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--jobs", nargs="+", required=True)
    a = ap.parse_args()
    items, ans = load(a.items, a.jobs)
    ms = list(ans)
    ch = [i for i, it in items.items() if it["kind"] == "choice"]
    ni = [i for i, it in items.items() if it["kind"] == "null"]
    acc = lambda m, ids: st.mean(ans[m][i][2]["choice_acc"] for i in ids)

    def split(name, key):
        print(f"\n== choice accuracy by {name}")
        for g in sorted({key(items[i]) for i in ch}, key=str):
            ids = [i for i in ch if key(items[i]) == g]
            print(f"  {g!s:10s}", *[f"{m} {acc(m, ids):.2f}" for m in ms], f"n={len(ids)}")

    masses = sorted(items[i]["meta"]["mass"] for i in ch)
    cuts = [masses[len(masses) * q // 4] for q in (1, 2, 3)]
    split("layer", lambda it: it["layer"])
    split("dose", lambda it: it["payload"]["dose"])
    split("prompt", lambda it: it["payload"]["prompt"][:12])
    split("effect-size quartile", lambda it: "Q%d" % (1 + sum(it["meta"]["mass"] >= c for c in cuts)))
    split(
        "change from unsteered",
        lambda it: "<0.5" if it["meta"]["change"] < 0.5 else ("<0.8" if it["meta"]["change"] < 0.8 else ">=0.8"),
    )
    split("neuron real (null_pct>=.95)", lambda it: it["meta"]["null_pct"] >= 0.95)
    split("selection", lambda it: it["meta"]["selection"])

    print("\n== token overlap: a logit-lens token (>=3 letters) literally occurs in a candidate reply")
    ov = [i for i in ch if overlap_pick(items[i])[1] > 0]
    nov = [i for i in ch if i not in ov]
    exp = sum((ans[ms[0]][i][1]["letter"] in overlap_pick(items[i])[0]) / len(overlap_pick(items[i])[0]) for i in ch)
    print(f"  items with overlap {len(ov)}/{len(ch)}; token-overlap baseline accuracy {exp / len(ch):.3f}")
    for m in ms:
        print(f"  {m}: acc with overlap {acc(m, ov):.2f}, without {acc(m, nov):.2f}")

    print("\n== rank of the chosen option by change from the unsteered reply (0 least .. 3 most)")
    for m in ms + ["truth"]:
        c = collections.Counter()
        for i in ch:
            oc = items[i]["meta"]["option_change"]
            order = sorted(oc, key=oc.get)
            letter = ans[ms[0]][i][1]["letter"] if m == "truth" else ans[m][i][0]
            c[order.index(letter) if letter in order else "n/a"] += 1
        print(f"  {m}: {dict(sorted(c.items(), key=str))}")

    print("\n== agreement")
    for x, y in itertools.combinations(ms, 2):
        print(f"  {x}-{y}: same letter {st.mean(ans[x][i][0] == ans[y][i][0] for i in ch):.2f}")
    print(
        "  items by number of models right:",
        dict(sorted(collections.Counter(int(sum(ans[m][i][2]["choice_acc"] for m in ms)) for i in ch).items())),
    )
    maj = 0
    for i in ch:
        top, cnt = collections.Counter(ans[m][i][0] for m in ms).most_common(1)[0]
        maj += cnt >= 2 and top == ans[ms[0]][i][1]["letter"]
    print(f"  majority vote accuracy {maj / len(ch):.3f}")

    print("\n== null: discrimination vs calibration")
    truth = [items[i]["meta"]["null_pct"] for i in ni]
    pz = [items[i]["evidence"]["logit_lens"].get("peak_z") or 0 for i in ni]
    print(f"  spearman(truth null_pct, logit-lens peak_z) = {spearman(truth, pz):.2f}")
    for m in ms:
        p = [float(ans[m][i][0]) for i in ni]
        y = [t >= 0.95 for t in truth]
        real = [pi for pi, yi in zip(p, y) if yi]
        nul = [pi for pi, yi in zip(p, y) if not yi]
        auc = st.mean((r > n) + 0.5 * (r == n) for r in real for n in nul)
        brier = st.mean((pi - yi) ** 2 for pi, yi in zip(p, y))
        const = st.mean((st.mean(p) - yi) ** 2 for yi in y)
        print(
            f"  {m}: AUC {auc:.2f}, mean prob {st.mean(p):.2f} (base rate {st.mean(y):.2f}), Brier {brier:.3f}, "
            f"Brier if constant at own mean {const:.3f}, spearman(prob, peak_z) {spearman(p, pz):.2f}, spearman(prob, truth) {spearman(p, truth):.2f}"
        )


if __name__ == "__main__":
    main()
