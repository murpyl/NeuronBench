"""Agent-free baselines, scored on the same items and with the same rewards as the verifier.

choice:
- random: expected accuracy 0.25.
- most_different: pick the reply least similar to the unsteered reply. Well above 0.25 means the distractors leak.
- logit_lens: pick the reply with the largest gain, over the unsteered reply, in the logit-lens tokens the dose pushes
  toward ("up" tokens for a positive dose, "down" tokens for a negative one), case-insensitive.
null:
- always_null / always_real: p = 0 / p = 1.
- base_rate: p = share of REAL items among the other items (leave-one-out).
- evidence_logreg: logistic regression on numeric evidence fields (down_norm, peak_z, activation stats, |cos|),
  5-fold cross-validated. Doing well here means the evidence alone gives away the label.
Positive-control tiers only (items whose evidence has measured fields):
- sweep_words (choice): the reply with the largest gain in the neuron's measured `sweep_words`.
- transfer_words (choice): the reply with the largest gain in words that the neuron's replies to the other prompts
  (`steered_elsewhere`) use and the unsteered reply does not.
Trace tiers only (choice items whose payload has a per-token `trace`):
- trace_lens_{mean,sum,max}: the reply whose tokens have the highest mean / summed / largest sign(dose) * lens_z.
- trace_lp_{low,high}: the reply with the lowest / highest mean unsteered log-prob (base_lp), a neuron-blind tell.
- sweep_logreg / transfer_logreg (null): 5-fold logistic regression on log(1 + summed top-5 sweep z) / on the number of
  distinct words in `steered_replies` that no unsteered reply uses.
"""

from __future__ import annotations

import math
import random
import re
from collections import Counter

import numpy as np

from .items import change


def tie_seed(item: dict) -> str:
    """The item's static-tier id, so tie-breaks match across evidence tiers."""
    tier = item.get("meta", {}).get("tier")
    return item["id"].replace(f"-{tier}-", "-", 1) if tier else item["id"]


def _norm_tok(t: str) -> str:
    return t.replace("Ġ", " ").replace("▁", " ").strip().lower()


def choice_most_different(item: dict) -> str:
    base = item["payload"]["baseline"]
    return max(item["payload"]["options"].items(), key=lambda kv: (change(kv[1], base), kv[0]))[0]


def choice_change_rank(item: dict, rank: int) -> str:
    """The option with the rank-th smallest change from the unsteered reply."""
    base = item["payload"]["baseline"]
    return sorted(item["payload"]["options"].items(), key=lambda kv: (change(kv[1], base), kv[0]))[rank][0]


def choice_logit_lens(item: dict) -> str:
    side = "up" if item["payload"]["dose"] > 0 else "down"
    toks = [t for t in (_norm_tok(t) for t in (item["evidence"].get("logit_lens") or {}).get(side, [])) if t]
    base = item["payload"]["baseline"].lower()

    def score(text: str) -> int:
        low = text.lower()
        return sum(max(0, low.count(t) - base.count(t)) for t in toks)

    opts = item["payload"]["options"]
    best = max(score(v) for v in opts.values())
    tied = sorted(k for k, v in opts.items() if score(v) == best)
    return random.Random(tie_seed(item)).choice(tied)


def lens_tokens(ev: dict) -> list[str]:
    """Logit-lens tokens (both sides) that are plain words of >= 3 letters, lowercased."""
    ll = ev.get("logit_lens") or {}
    out = []
    for k in ("up", "down"):
        for t in ll.get(k) or []:
            s = (t if isinstance(t, str) else str(t)).strip()
            if len(s) >= 3 and re.fullmatch(r"[A-Za-z]+", s):
                out.append(s.lower())
    return out


def overlap_pick(it: dict) -> tuple[list[str], int]:
    """Options with the most literal lens-token occurrences, and that count (0 = no lens token in any reply)."""
    ts = lens_tokens(it["evidence"])
    sc = {L: sum(o.lower().count(t) for t in ts) for L, o in it["payload"]["options"].items()}
    best = max(sc.values())
    return [L for L, v in sc.items() if v == best], best


def _words(text: str) -> list[str]:
    return re.findall(r"\w{3,}", text.lower())


def _pick_by_gain(item: dict, words: set[str]) -> str:
    base = Counter(_words(item["payload"]["baseline"]))
    opts = item["payload"]["options"]

    def score(text: str) -> int:
        c = Counter(_words(text))
        return sum(max(0, c[w] - base[w]) for w in words)

    best = max(score(v) for v in opts.values())
    return random.Random(tie_seed(item)).choice(sorted(k for k, v in opts.items() if score(v) == best))


def choice_sweep_words(item: dict) -> str:
    return _pick_by_gain(item, {w.lower() for w in item["evidence"]["sweep_words"]})


def choice_transfer_words(item: dict) -> str:
    base = set(_words(item["payload"]["baseline"]))
    seen = {w for t in item["evidence"]["steered_elsewhere"].values() for w in _words(t)}
    return _pick_by_gain(item, seen - base)


TRACE_STATS = {
    "trace_lens_mean": lambda t, sign: float(np.mean([sign * z for z in t["lens_z"]])) if t["lens_z"] else 0.0,
    "trace_lens_sum": lambda t, sign: float(sum(sign * z for z in t["lens_z"])),
    "trace_lens_max": lambda t, sign: max((sign * z for z in t["lens_z"]), default=0.0),
    "trace_lp_low": lambda t, sign: -float(np.mean(t["base_lp"])) if t["base_lp"] else 0.0,
    "trace_lp_high": lambda t, sign: float(np.mean(t["base_lp"])) if t["base_lp"] else 0.0,
}


def choice_trace(item: dict, stat: str) -> str:
    """The option maximising TRACE_STATS[stat] over its per-token trace (ties broken as the other baselines)."""
    sign = 1.0 if item["payload"]["dose"] > 0 else -1.0
    tr = item["payload"]["trace"]
    sc = {k: round(TRACE_STATS[stat](tr[k], sign), 9) for k in item["payload"]["options"]}
    best = max(sc.values())
    return random.Random(tie_seed(item)).choice(sorted(k for k, v in sc.items() if v == best))


def _sweep_feature(item: dict) -> list[float]:
    zs = sorted((w["z"] for w in item["evidence"]["sweep_words"]), reverse=True)
    return [math.log1p(sum(z for z in zs[:5] if z > 0))]


def _transfer_feature(item: dict) -> list[float]:
    base = {w for t in item["payload"]["baselines"].values() for w in _words(t)}
    new = {w for t in item["evidence"]["steered_replies"]["replies"].values() for w in _words(t)} - base
    return [math.log1p(len(new))]


def features(item: dict) -> list[float]:
    ev = item["evidence"]
    act = ev.get("activation") or {}
    ll = ev.get("logit_lens") or {}
    cos = [abs(v["cos"]) for v in (ev.get("directions") or {}).values()]
    vals = [ev.get("down_norm") or 0.0, ll.get("peak_z") or 0.0,
            act.get("absmax", 0.0), act.get("q999", 0.0), act.get("rms", 0.0), abs(act.get("mean", 0.0)),
            max(cos) if cos else 0.0]
    return [math.log1p(abs(v)) for v in vals]


def _logreg(X: np.ndarray, y: np.ndarray, l2: float = 1.0, steps: int = 500, lr: float = 0.1) -> np.ndarray:
    w = np.zeros(X.shape[1])
    for _ in range(steps):
        p = 1 / (1 + np.exp(-X @ w))
        w -= lr * (X.T @ (p - y) / len(y) + l2 * np.r_[0, w[1:]] / len(y))
    return w


def null_evidence_logreg(items: list[dict], folds: int = 5, seed: int = 0, feats=None) -> list[float]:
    X = np.array([(feats or features)(it) for it in items], dtype=float)
    y = np.array([it["answer"]["real"] for it in items], dtype=float)
    order = list(range(len(items)))
    random.Random(seed).shuffle(order)
    preds = np.zeros(len(items))
    for f in range(folds):
        test = order[f::folds]
        train = [i for i in order if i not in set(test)]
        if not train or len(set(y[train])) < 2:
            preds[test] = y[train].mean() if train else 0.5
            continue
        mu, sd = X[train].mean(0), X[train].std(0) + 1e-9
        Z = np.c_[np.ones(len(items)), (X - mu) / sd]
        w = _logreg(Z[train], y[train])
        preds[test] = 1 / (1 + np.exp(-Z[test] @ w))
    return preds.tolist()


def brier_reward(p: float, y: int) -> float:
    return 1 - (p - y) ** 2


def run_baselines(items: list[dict]) -> dict[str, dict[str, float]]:
    """{baseline: {item_id: reward}}, rewards on the verifier's scale (choice_acc or 1 - squared error)."""
    ch = [it for it in items if it["kind"] == "choice"]
    nu = [it for it in items if it["kind"] == "null"]
    out: dict[str, dict[str, float]] = {}
    if ch:
        out["random"] = {it["id"]: 0.25 for it in ch}
        out["most_different"] = {it["id"]: float(choice_most_different(it) == it["answer"]["letter"]) for it in ch}
        for r in range(4):
            out[f"change_rank{r}"] = {it["id"]: float(choice_change_rank(it, r) == it["answer"]["letter"]) for it in ch}
        out["logit_lens"] = {it["id"]: float(choice_logit_lens(it) == it["answer"]["letter"]) for it in ch}
        for name, fn, field in (("sweep_words", choice_sweep_words, "sweep_words"),
                                ("transfer_words", choice_transfer_words, "steered_elsewhere")):
            if all(field in it["evidence"] for it in ch):
                out[name] = {it["id"]: float(fn(it) == it["answer"]["letter"]) for it in ch}
        if all("trace" in it["payload"] for it in ch):
            for name in TRACE_STATS:
                out[name] = {it["id"]: float(choice_trace(it, name) == it["answer"]["letter"]) for it in ch}
    if nu:
        ys = [it["answer"]["real"] for it in nu]
        tot = sum(ys)
        out["always_null"] = {it["id"]: brier_reward(0.0, y) for it, y in zip(nu, ys)}
        out["always_real"] = {it["id"]: brier_reward(1.0, y) for it, y in zip(nu, ys)}
        out["base_rate"] = {it["id"]: brier_reward((tot - y) / max(1, len(nu) - 1), y) for it, y in zip(nu, ys)}
        out["evidence_logreg"] = {it["id"]: brier_reward(p, y)
                                  for it, y, p in zip(nu, ys, null_evidence_logreg(nu))}
        for name, fn, field in (("sweep_logreg", _sweep_feature, "sweep_words"),
                                ("transfer_logreg", _transfer_feature, "steered_replies")):
            if all(field in it["evidence"] for it in nu):
                out[name] = {it["id"]: brier_reward(p, y)
                             for it, y, p in zip(nu, ys, null_evidence_logreg(nu, feats=fn))}
    return out
