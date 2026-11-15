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

from neuronbench.baselines import choice_logit_lens
from neuronbench.harbor_tasks import safe_name

SHORT = {
    "anthropic/claude-haiku-4-5": "H4.5",
    "anthropic/claude-haiku-5-5": "H5.5",
    "anthropic/claude-sonnet-5-5": "S5.5",
    "openai/gpt-5.6-luna": "GPT",
}


def load(items_path, job_paths):
    with open(items_path) as fh:
        items = {json.loads(line)["id"]: json.loads(line) for line in fh}
    byname = {safe_name(i): i for i in items}
    ans = {}
    for f in job_paths:
        with open(f) as fh:
            d = json.load(fh)
        m = d["benchmark_arguments"]["contract"]["model"]
        for k, v in d["evaluation_results"].items():
            if k not in byname:
                continue
            try:
                vo = json.loads(v["metadata"]["verifier_output"])
            except (KeyError, TypeError, ValueError):
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


def _ranks(x):
    """Average ranks for ties (what scipy.stats.rankdata does)."""
    order = sorted(range(len(x)), key=lambda i: x[i])
    ranks = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2
        i = j + 1
    return ranks


def spearman(x, y):
    return float(np.corrcoef(_ranks(x), _ranks(y))[0, 1])


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

    def ci(m, ids, n=10000):
        x = np.array([ans[m][i][2]["choice_acc"] for i in ids])
        bs = np.random.default_rng(0).choice(x, (n, len(x))).mean(1)
        return f"[{np.quantile(bs, 0.025):.2f}, {np.quantile(bs, 0.975):.2f}]"

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
    split("effect-size quartile", lambda it: f"Q{1 + sum(it['meta']['mass'] >= c for c in cuts)}")
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
    print("  with 95% bootstrap CIs (lens token in a reply / not):")
    for m in ms:
        print(f"  {m}:", *[f"{acc(m, ids):.2f} {ci(m, ids)}" for ids in (ov, nov)])
    lens = {i: choice_logit_lens(items[i]) for i in ch}
    hit = lambda ids: st.mean(lens[i] == items[i]["answer"]["letter"] for i in ids)
    print(f"  logit_lens baseline (dose-sign aware): all {hit(ch):.2f}, lens token in a reply {hit(ov):.2f}, "
          f"not {hit(nov):.2f}")
    hits = [i for i in ch if lens[i] == items[i]["answer"]["letter"]]
    miss = [i for i in ch if i not in hits]
    print(f"  model vs logit_lens: same pick | acc where the lookup is right (n={len(hits)}) | where it is wrong "
          f"(n={len(miss)}) | either right")
    for m in ms:
        same = st.mean(ans[m][i][0] == lens[i] for i in ch)
        either = st.mean(ans[m][i][2]["choice_acc"] > 0 or i in hits for i in ch)
        print(f"  {m}: {same:.2f} | {acc(m, hits):.2f} | {acc(m, miss):.2f} | {either:.2f}")

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
        votes = collections.Counter(ans[m][i][0] for m in ms).most_common()
        plurality = votes[0][1] >= 2 and (len(votes) == 1 or votes[0][1] > votes[1][1])
        maj += plurality and votes[0][0] == ans[ms[0]][i][1]["letter"]
    print(f"  plurality vote accuracy (ties count as wrong) {maj / len(ch):.3f}")

    print("\n== null: discrimination vs calibration")
    truth = [items[i]["meta"]["null_pct"] for i in ni]
    pz = [items[i]["evidence"]["logit_lens"].get("peak_z") or 0 for i in ni]
    print(f"  spearman(truth null_pct, logit-lens peak_z) = {spearman(truth, pz):.2f}")
    for m in ms:
        p = [float(ans[m][i][0]) for i in ni]
        y = [bool(items[i]["answer"]["real"]) for i in ni]
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
