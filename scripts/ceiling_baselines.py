"""Stronger agent-free baselines for "Which output is it?": how much of the task simple text features can solve.

python scripts/ceiling_baselines.py --items data/items.jsonl

- signed_lens: like baseline logit_lens, but uses the "down" tokens for negative doses and keeps punctuation tokens.
- signed_fuzzy: signed_lens plus partial matches (shared 4-letter chunks between a lens token and a reply word).
- script_match: does the reply gain characters from the writing systems (CJK, Cyrillic, ...) of the pushed tokens?
- learned: conditional logit over all of the above plus change/length/punctuation features, 5-fold CV by neuron.
- sweep_words / transfer_words (positive-control tiers only): see neuronbench.baselines.
"""

import argparse
import json
import random
import re
import unicodedata

import numpy as np

from neuronbench.baselines import choice_sweep_words, choice_transfer_words, tie_seed
from neuronbench.items import change

SCRIPTS = ("CJK", "HANGUL", "HIRAGANA", "KATAKANA", "CYRILLIC", "THAI", "ARABIC", "HEBREW", "DEVANAGARI", "GREEK")


def toks(item, side):
    return [t.replace("Ġ", " ").replace("▁", " ") for t in (item["evidence"]["logit_lens"].get(side) or [])]


def pushed(item, flip=False):
    up = item["payload"]["dose"] > 0
    return toks(item, "up" if up != flip else "down")


def exact(text, ts):
    low = text.lower()
    return sum(low.count(t.strip().lower()) for t in ts if t.strip())


def chunks(s, n=4):
    s = s.lower()
    return {s[i:i + n] for i in range(len(s) - n + 1)}


def fuzzy(text, ts):
    grams = set().union(*(chunks(w) for w in re.findall(r"\w{4,}", text))) if text else set()
    return sum(len(chunks(t.strip()) & grams) > 0 for t in ts if len(t.strip()) >= 4)


def script_of(ch):
    name = unicodedata.name(ch, "")
    return next((s for s in SCRIPTS if s in name), None)


def script_hist(text):
    h = dict.fromkeys(SCRIPTS, 0)
    for ch in text:
        s = script_of(ch)
        if s:
            h[s] += 1
    return h


def script_score(text, base, ts):
    want = script_hist("".join(ts))
    tot = sum(want.values()) or 1
    got, had = script_hist(text), script_hist(base)
    return sum(want[s] / tot * np.log1p(max(0, got[s] - had[s])) for s in SCRIPTS)


def punct(text):
    return sum(not c.isalnum() and not c.isspace() for c in text)


def option_features(item, text):
    base = item["payload"]["baseline"]
    pu, pd = pushed(item), pushed(item, flip=True)
    return [
        exact(text, pu) - exact(base, pu),
        exact(text, pd) - exact(base, pd),
        fuzzy(text, pu) - fuzzy(base, pu),
        fuzzy(text, pd) - fuzzy(base, pd),
        script_score(text, base, pu),
        script_score(text, base, pd),
        change(text, base),
        np.log1p(len(text)) - np.log1p(len(base)),
        (punct(text) - punct(base)) / 100,
        (text.count("\n") - base.count("\n")) / 10,
    ]


def pick(item, score):
    opts = item["payload"]["options"]
    sc = {k: score(item, v) for k, v in opts.items()}
    best = max(sc.values())
    return random.Random(tie_seed(item)).choice(sorted(k for k, v in sc.items() if v == best))


def signed_lens(item, text):
    return exact(text, pushed(item)) - exact(item["payload"]["baseline"], pushed(item))


def signed_fuzzy(item, text):
    return signed_lens(item, text) + 0.5 * (fuzzy(text, pushed(item)) - fuzzy(item["payload"]["baseline"], pushed(item)))


def script_match(item, text):
    return script_score(text, item["payload"]["baseline"], pushed(item))


def learned(items, folds=5, l2=1.0, steps=2000, lr=0.1):
    """Conditional logit (softmax over the 4 options), cross-validated with all items of a neuron in one fold."""
    letters = "ABCD"
    X = np.array([[option_features(it, it["payload"]["options"][k]) for k in letters] for it in items])
    y = np.array([letters.index(it["answer"]["letter"]) for it in items])
    neurons = sorted({(it["layer"], it["neuron"]) for it in items})
    random.Random(0).shuffle(neurons)
    fold = {n: i % folds for i, n in enumerate(neurons)}
    f_of = np.array([fold[(it["layer"], it["neuron"])] for it in items])
    pred = np.zeros(len(items), dtype=int)
    for f in range(folds):
        tr, te = f_of != f, f_of == f
        mu, sd = X[tr].reshape(-1, X.shape[2]).mean(0), X[tr].reshape(-1, X.shape[2]).std(0) + 1e-9
        Z = (X - mu) / sd
        w = np.zeros(X.shape[2])
        for _ in range(steps):
            s = Z[tr] @ w
            p = np.exp(s - s.max(1, keepdims=True))
            p /= p.sum(1, keepdims=True)
            onehot = np.eye(4)[y[tr]]
            grad = np.einsum("nk,nkd->d", p - onehot, Z[tr]) / tr.sum() + l2 * w / tr.sum()
            w -= lr * grad
        pred[te] = (Z[te] @ w).argmax(1)
    return [letters[i] for i in pred]


def ci(x, n=10000):
    x = np.asarray(x, dtype=float)
    bs = np.random.default_rng(0).choice(x, (n, len(x))).mean(1)
    return f"{x.mean():.2f} [{np.quantile(bs, 0.025):.2f}, {np.quantile(bs, 0.975):.2f}]"


def has_overlap(item):
    ts = [t.strip().lower() for side in ("up", "down") for t in toks(item, side)]
    ts = [t for t in ts if len(t) >= 3 and re.fullmatch(r"[a-z]+", t)]
    return any(t in o.lower() for o in item["payload"]["options"].values() for t in ts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    a = ap.parse_args()
    with open(a.items) as fh:
        items = [json.loads(line) for line in fh]
    ch = [it for it in items if it["kind"] == "choice"]
    ov = [has_overlap(it) for it in ch]
    preds = {name: [pick(it, fn) for it in ch] for name, fn in
             [("signed_lens", signed_lens), ("signed_fuzzy", signed_fuzzy), ("script_match", script_match)]}
    preds["learned"] = learned(ch)
    for name, fn, field in (("sweep_words", choice_sweep_words, "sweep_words"),
                            ("transfer_words", choice_transfer_words, "steered_elsewhere")):
        if all(field in it["evidence"] for it in ch):
            preds[name] = [fn(it) for it in ch]
    print(f"choice items {len(ch)} (lens token in a reply: {sum(ov)})")
    print(f"{'baseline':14s} {'all':18s} {'lens token':18s} {'no lens token':18s}")
    for name, p in preds.items():
        r = [float(x == it["answer"]["letter"]) for x, it in zip(p, ch)]
        print(f"{name:14s} {ci(r):18s} {ci([x for x, o in zip(r, ov) if o]):18s} {ci([x for x, o in zip(r, ov) if not o]):18s}")


if __name__ == "__main__":
    main()
