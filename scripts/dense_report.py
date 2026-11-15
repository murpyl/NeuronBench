"""Binary and dense scores for one model across evidence tiers, from Valkyrie exports.

Dense metrics are computed offline from the verifier's echoed answer (`verifier_output.raw` / `.parsed`), so the
shared grader (harbor_tasks.GRADE_PY) stays as it is:

- choice `rank_score`: 1, 2/3, 1/3, 0 for the true reply ranked 1st..4th in the answer's letter order; letters the answer
  leaves out share the remaining positions (a bare "B" that is wrong scores 1/3). No letter scores 0.
- choice `letter_brier` (loss): 0.5 * sum_k (p_k - y_k)^2 over A-D, in [0, 1]; uniform guessing gives 0.375. Without four
  valid probabilities the answer counts as one-hot on its first letter; no letter scores 1.
- null `dense_brier` (loss): (p - null_pct)^2 against the item's continuous `meta.null_pct`, next to the usual
  `brier` (p - real)^2 against the binary label. A missing or out-of-range p scores 1 on both, as in the grader.

python scripts/dense_report.py --model anthropic/claude-haiku-5-5 --out results/subagents/haiku-5-5 \
    --tier static data/items.jsonl runs/static-l14-l20.json runs/static-l24.json \
    --tier transfer data/items-transfer.jsonl ... --tier oracle data/items-oracle.jsonl ... \
    --legacy static jobs/valkyrie/l14-l20-haiku-5-5.json jobs/valkyrie/l24-haiku-5-5.json
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from neuronbench.baselines import tie_seed
from neuronbench.harbor_tasks import safe_name
from neuronbench.results import _ci, load_items

LETTERS = "ABCD"
RANK_POINTS = (1.0, 2 / 3, 1 / 3, 0.0)
ITEMS = {"static": "data/items.jsonl", "transfer": "data/items-transfer.jsonl", "oracle": "data/items-oracle.jsonl"}
LOWER_IS_BETTER = {"letter_brier", "brier", "dense_brier"}


def parse_ranking(raw: str) -> tuple[list[str], dict[str, float] | None]:
    """Letters in order of first mention, and their probabilities if all four are given and sum to about 1."""
    order, probs = [], {}
    for m in re.finditer(r"\b([ABCD])\b(?:\s*[:=]?\s*(\d*\.?\d+(?:E[-+]?\d+)?)\s*(%?))?", raw.upper()):
        letter = m.group(1)
        if letter in order:
            continue
        order.append(letter)
        if m.group(2):
            probs[letter] = float(m.group(2)) / (100 if m.group(3) else 1)
    total = sum(probs.values())
    if len(probs) < 4 or not 0.9 <= total <= 1.1 or any(v < 0 for v in probs.values()):
        return order, None
    return order, {k: v / total for k, v in probs.items()}


def rank_score(order: list[str], key: str) -> float:
    if not order:
        return 0.0
    if key in order:
        return RANK_POINTS[order.index(key)]
    rest = RANK_POINTS[len(order):]
    return sum(rest) / len(rest)


def letter_brier(order: list[str], probs: dict[str, float] | None, key: str) -> float:
    if not order:
        return 1.0
    if probs is None:
        probs = {order[0]: 1.0}
    return 0.5 * sum((probs.get(k, 0.0) - (k == key)) ** 2 for k in LETTERS)


def parse_p(parsed) -> float | None:
    try:
        p = float(parsed)
    except (TypeError, ValueError):
        return None
    return p if 0 <= p <= 1 else None


def read_exports(paths: list[str], model: str) -> dict[str, dict]:
    """{task name: verifier detail} for `model` from Valkyrie exports (files or directories of them)."""
    out = {}
    files = [p for j in map(Path, paths) for p in ([j] if j.is_file() else sorted(j.rglob("*.json")))]
    for f in files:
        try:
            d = json.loads(f.read_text())
            if d["benchmark_arguments"]["contract"]["model"] != model:
                continue
            results = d["evaluation_results"]
        except (OSError, ValueError, KeyError, TypeError):
            continue
        for k, v in results.items():
            try:
                detail = json.loads((v.get("metadata") or {}).get("verifier_output") or "{}")
            except (ValueError, AttributeError):
                detail = {}
            name = k.split("/")[-1]
            if name in out:
                print(f"warning: {name} appears in more than one export; keeping the last")
            out[name] = {"raw": detail.get("raw", ""), "parsed": detail.get("parsed"),
                         "rewards": (v or {}).get("rewards") or {}}
    return out


def score_item(it: dict, det: dict) -> dict:
    row = {"id": it["id"], "pair": tie_seed(it), "kind": it["kind"], "layer": it["layer"]}
    if it["kind"] == "choice":
        key = it["answer"]["letter"]
        order, probs = parse_ranking(det["raw"])
        if not order and det["parsed"] in set(LETTERS):
            order = [det["parsed"]]  # the answer's first letter fell past the grader's 200-char echo
        row.update(acc=float(bool(order) and order[0] == key), rank_score=rank_score(order, key),
                   letter_brier=letter_brier(order, probs, key), probs_valid=float(probs is not None),
                   full_ranking=float(len(order) == 4), graded_acc=float(det["rewards"].get("choice_acc") or 0.0),
                   answer=det["raw"][:80])
    else:
        p, y, x = parse_p(det["parsed"]), it["answer"]["real"], it["meta"]["null_pct"]
        row.update(p=p, real=y, null_pct=x, brier=1.0 if p is None else (p - y) ** 2,
                   dense_brier=1.0 if p is None else (p - x) ** 2)
    return row


def mean_ci(vals: list[float]) -> dict | None:
    if not vals:
        return None
    lo, hi = _ci(vals)
    return {"mean": round(sum(vals) / len(vals), 4), "lo": round(lo, 4), "hi": round(hi, 4)}


def _ranks(x: list[float]) -> list[float]:
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx, vy = sum((a - mx) ** 2 for a in rx), sum((b - my) ** 2 for b in ry)
    return round(cov / (vx * vy) ** 0.5, 4) if vx and vy else None


def auc(p: list[float], y: list[int]) -> float | None:
    pos = [a for a, b in zip(p, y) if b]
    neg = [a for a, b in zip(p, y) if not b]
    if not pos or not neg:
        return None
    return round(sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg)), 4)


def summarise_tier(items: list[dict], rows: list[dict]) -> dict:
    ch = [r for r in rows if r["kind"] == "choice"]
    nu = [r for r in rows if r["kind"] == "null"]
    said = [r for r in nu if r["p"] is not None]
    n_ch = sum(it["kind"] == "choice" for it in items)
    return {
        "choice": {"n": n_ch, "n_answered": len(ch),
                   **{m: mean_ci([r[m] for r in ch]) for m in ("acc", "rank_score", "letter_brier")},
                   "probs_valid": round(sum(r["probs_valid"] for r in ch) / len(ch), 4) if ch else None,
                   "full_ranking": round(sum(r["full_ranking"] for r in ch) / len(ch), 4) if ch else None,
                   "top1_matches_grader": all(r["acc"] == r["graded_acc"] for r in ch)},
        "null": {"n": len(items) - n_ch, "n_answered": len(nu),
                 **{m: mean_ci([r[m] for r in nu]) for m in ("brier", "dense_brier")},
                 "auc": auc([r["p"] for r in said], [r["real"] for r in said]),
                 "spearman_null_pct": spearman([r["p"] for r in said], [r["null_pct"] for r in said])},
    }


def null_references(items: list[dict]) -> dict:
    x = [it["meta"]["null_pct"] for it in items if it["kind"] == "null"]
    y = [it["answer"]["real"] for it in items if it["kind"] == "null"]
    if not x:
        return {}
    base = sum(x) / len(x)

    def both(ps):
        return {"brier": round(sum((p - b) ** 2 for p, b in zip(ps, y)) / len(y), 4),
                "dense_brier": round(sum((p - b) ** 2 for p, b in zip(ps, x)) / len(x), 4)}

    return {"p=0.5": both([0.5] * len(x)), f"p=mean null_pct ({base:.3f})": both([base] * len(x)),
            "p=binary label": both([float(v) for v in y])}


def paired(rows_a: list[dict], rows_b: list[dict], metric: str) -> dict | None:
    """Mean of (a - b) over items present in both tiers, with a bootstrap 95% CI."""
    a = {r["pair"]: r[metric] for r in rows_a if metric in r}
    b = {r["pair"]: r[metric] for r in rows_b if metric in r}
    common = sorted(set(a) & set(b))
    out = mean_ci([a[i] - b[i] for i in common])
    return {**out, "n": len(common)} if out else None


def fmt(x: dict | None, d: int = 2) -> str:
    return "-" if not x else f"{x['mean']:.{d}f} [{x['lo']:.{d}f}, {x['hi']:.{d}f}]"


def markdown(summary: dict) -> str:
    lines = [f"# {summary['model']}: tier ladder, binary and dense", "",
             ("| tier | n | acc ↑ (binary) | rank score ↑ | letter Brier ↓ | probs valid | legacy acc ↑ "
              "| null Brier ↓ (binary) | null dense Brier ↓ | null AUC ↑ | Spearman(p, null_pct) ↑ | legacy null Brier ↓ |"),
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for tier, t in summary["tiers"].items():
        c, n = t.get("choice") or {}, t.get("null") or {}
        lg = (summary["legacy"].get(tier) or {})
        lines.append(f"| {tier} | {c.get('n_answered', 0)}/{c.get('n', 0)} + {n.get('n_answered', 0)}/{n.get('n', 0)} "
                     f"| {fmt(c.get('acc'))} | {fmt(c.get('rank_score'))} | {fmt(c.get('letter_brier'), 3)} "
                     f"| {c.get('probs_valid', '-')} | {fmt((lg.get('choice') or {}).get('acc'))} "
                     f"| {fmt(n.get('brier'), 3)} | {fmt(n.get('dense_brier'), 3)} | {n.get('auc', '-')} "
                     f"| {n.get('spearman_null_pct', '-')} | {fmt((lg.get('null') or {}).get('brier'), 3)} |")
    lines += ["", "Paired differences vs static (same items, bootstrap 95% CI):", ""]
    for name, d in summary["paired_vs_static"].items():
        lines.append(f"- {name}: " + ", ".join(f"{m} {fmt(v, 3)}" for m, v in d.items()))
    lines += ["", "Null references (constant answers): "
              + "; ".join(f"{k}: Brier {v['brier']:.3f}, dense {v['dense_brier']:.3f}"
                          for k, v in summary["null_references"].items()),
              "Choice chance: acc 0.25, rank score 0.50, letter Brier 0.375."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="model id exactly as in the Valkyrie contract")
    ap.add_argument("--out", required=True, help="model-specific output directory")
    ap.add_argument("--tier", nargs="+", action="append", default=[], metavar=("NAME ITEMS", "EXPORT"),
                    help="rank-format runs at one tier: name, items.jsonl, then export files/dirs")
    ap.add_argument("--legacy", nargs="+", action="append", default=[], metavar=("NAME", "EXPORT"),
                    help="existing binary-format runs at one tier (items from the matching --tier or data/)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    summary = {"model": a.model, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),  # noqa: UP017 (runs on 3.10)
               "tiers": {}, "legacy": {}, "paired_vs_static": {}}
    per_tier, items_path = {}, dict(ITEMS)
    all_rows = []
    for name, ipath, *exports in a.tier:
        items_path[name] = ipath
        items = load_items(ipath)
        dets = read_exports(exports, a.model)
        rows = [score_item(it, dets[safe_name(it["id"])]) for it in items if safe_name(it["id"]) in dets]
        per_tier[name] = rows
        summary["tiers"][name] = {**summarise_tier(items, rows), "items": ipath, "exports": exports}
        if not summary.get("null_references"):
            summary["null_references"] = null_references(items)
        all_rows += [{"tier": name, "format": "rank", **r} for r in rows]
    for name, *exports in a.legacy:
        items = load_items(items_path[name])
        dets = read_exports(exports, a.model)
        rows = [score_item(it, dets[safe_name(it["id"])]) for it in items if safe_name(it["id"]) in dets]
        summary["legacy"][name] = {**summarise_tier(items, rows), "exports": exports}
        all_rows += [{"tier": name, "format": "binary", **r} for r in rows]
    if "static" in per_tier:
        for name, rows in per_tier.items():
            if name != "static":
                summary["paired_vs_static"][f"{name} - static"] = {
                    m: paired(rows, per_tier["static"], m)
                    for m in ("acc", "rank_score", "letter_brier", "brier", "dense_brier")}
    (out / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    (out / "per_item.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in all_rows))
    (out / "summary.md").write_text(markdown(summary))
    print(markdown(summary))


if __name__ == "__main__":
    main()
