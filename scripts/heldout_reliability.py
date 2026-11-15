"""Pilot check for Eval 2: does the held-out REAL/NULL label agree with itself, and does the old 3-prompt label predict it?

Splits the held-out prompts into two halves (every split, or --splits random ones), re-runs gne's ranking on each half
against the same random controls, and reports how well one half's null_pct predicts the other half's label. The
pre-registered bar (heldout/README.md) is a median split-half AUC >= 0.85.

    python scripts/heldout_reliability.py --run ~/.gne/runs/<model_id>/L20-heldout_rel.jsonl \
        --old-units data/raw/L20-main_rel.units.jsonl --out heldout/reliability-L20.json

--word-unit tokens matches `gne rank` exactly but needs the model (--model) for the vocabulary; regex needs only the
rollout text and tracks it closely (Spearman 0.83-0.96 on main_rel).
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from neuronbench.gne_io import read_jsonl, run_parts

REAL = 0.95


def rankdata(x) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def auc(score, label) -> float:
    label = np.asarray(label, dtype=bool)
    n1, n0 = label.sum(), (~label).sum()
    if not n1 or not n0:
        return float("nan")
    r = rankdata(score)
    return float((r[label].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def spearman(a, b) -> float:
    ra, rb = rankdata(a), rankdata(b)
    if ra.std() == 0 or rb.std() == 0:
        return float("nan")
    return float(np.corrcoef(ra, rb)[0, 1])


def kappa(a, b) -> float:
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    po = np.mean(a == b)
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def make_ranker(word_unit: str, model: str | None):
    from gne.rank import rank_records
    words = None
    if word_unit == "tokens":
        if not model:
            raise SystemExit("--word-unit tokens needs --model for the vocabulary")
        from gne.api import open_model
        words = open_model(model).vocab.words()

    def rank(recs: list[dict]) -> dict[int, dict]:
        return {int(u["neuron"]): u for u in rank_records(recs, word_unit=word_unit, token_words=words)
                if u["kind"] == "neuron"}
    return rank


def subset(recs: list[dict], prompts: set[str]) -> list[dict]:
    return [r for r in recs if r["prompt"] in prompts]


def half_splits(prompts: list[str], k: int, n: int | None, seed: int) -> list[tuple[set, set]]:
    combos = [set(c) for c in itertools.combinations(prompts, k)]
    pairs, seen = [], set()
    for a in combos:
        b = set(prompts) - a
        key = frozenset([frozenset(a), frozenset(b)])
        if key not in seen:
            seen.add(key)
            pairs.append((a, b))
    if n is not None and n < len(pairs):
        idx = np.random.default_rng(seed).choice(len(pairs), n, replace=False)
        pairs = [pairs[i] for i in sorted(idx)]
    return pairs


def summarize(v: list[float]) -> dict:
    v = np.array([x for x in v if np.isfinite(x)])
    if not v.size:
        return {"median": None, "p2.5": None, "p97.5": None, "n": 0}
    return {"median": round(float(np.median(v)), 3), "p2.5": round(float(np.percentile(v, 2.5)), 3),
            "p97.5": round(float(np.percentile(v, 97.5)), 3), "n": int(v.size)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="held-out sweep JSONL (parts are read too)")
    ap.add_argument("--old-units", default=None, help="units.jsonl of the agent-visible main_rel sweep, same layer")
    ap.add_argument("--word-unit", default="regex", choices=("regex", "tokens"))
    ap.add_argument("--model", default=None)
    ap.add_argument("--prompts", default=None, help="comma list; default every non-baseline prompt in the run")
    ap.add_argument("--half", type=int, default=None, help="prompts in half A (default: half of them)")
    ap.add_argument("--splits", type=int, default=None, help="random subset of splits (default: all)")
    ap.add_argument("--bar", type=float, default=0.85)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="write per-neuron held-out labels and the summary here (JSON)")
    a = ap.parse_args()

    path = Path(a.run).expanduser()
    recs = [r for p in run_parts(path) for r in read_jsonl(p)]
    if not recs:
        raise SystemExit(f"no rollouts in {path}")
    for r in recs:
        r.setdefault("logprob", [])
        r["token_ids"] = r.get("token_ids") or []
    prompts = sorted(a.prompts.split(",")) if a.prompts else sorted({r["prompt"] for r in recs if r["kind"] != "baseline"})
    recs = subset(recs, set(prompts))
    rank = make_ranker(a.word_unit, a.model)

    full = rank(recs)
    neurons = sorted(full)
    full_null = np.array([full[n]["null_pct"] for n in neurons])
    full_lab = full_null >= REAL
    n_ctrl = len({int(r["neuron"]) for r in recs if r["kind"] == "random"})

    k = a.half or len(prompts) // 2
    stats = {"auc": [], "spearman": [], "kappa": [], "agree": []}
    for pa, pb in half_splits(prompts, k, a.splits, a.seed):
        ra, rb = rank(subset(recs, pa)), rank(subset(recs, pb))
        xa = np.array([ra[n]["null_pct"] for n in neurons])
        xb = np.array([rb[n]["null_pct"] for n in neurons])
        stats["auc"].append(np.nanmean([auc(xa, xb >= REAL), auc(xb, xa >= REAL)]))
        stats["spearman"].append(spearman(xa, xb))
        stats["kappa"].append(kappa(xa >= REAL, xb >= REAL))
        stats["agree"].append(float(np.mean((xa >= REAL) == (xb >= REAL))))
    split = {key: summarize(v) for key, v in stats.items()}

    summary = {"run": path.name, "word_unit": a.word_unit, "prompts": prompts, "half": k, "n_neurons": len(neurons),
               "n_controls": n_ctrl, "real_share": round(float(full_lab.mean()), 3), "split_half": split,
               "bar": a.bar, "passes": bool(split["auc"]["median"] is not None and split["auc"]["median"] >= a.bar)}

    if a.old_units:
        old = {int(u["neuron"]): u for u in read_jsonl(a.old_units) if u["kind"] == "neuron"}
        both = [i for i, n in enumerate(neurons) if n in old and old[n]["null_pct"] is not None]
        o = np.array([old[neurons[i]]["null_pct"] for i in both])
        summary["old_label"] = {"n": len(both), "auc_old_null_pct": round(auc(o, full_lab[both]), 3),
                                "agree_old_label": round(float(np.mean((o >= REAL) == full_lab[both])), 3),
                                "spearman_null_pct": round(spearman(o, full_null[both]), 3)}

    print(json.dumps(summary, indent=1))
    verdict = "PASS" if summary["passes"] else "FAIL"
    print(f"\n{verdict}: median split-half AUC {split['auc']['median']} (bar {a.bar}), {len(neurons)} neurons, "
          f"{n_ctrl} controls, halves of {k}/{len(prompts) - k} prompts. Halves use fewer prompts than the full label, "
          f"so the full label is more reliable than this.")
    if a.out:
        labels = [{"neuron": n, "null_pct": full[n]["null_pct"], "mass": full[n]["mass"],
                   "real": bool(full[n]["null_pct"] >= REAL)} for n in neurons]
        Path(a.out).write_text(json.dumps({"summary": summary, "labels": labels}, indent=1) + "\n")


if __name__ == "__main__":
    main()
