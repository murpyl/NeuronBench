"""Trivial baselines for the forced-choice tasks. No model calls.

    python3 scripts/baselines.py tasks

A benchmark is only interesting if these do not solve it. Ties are scored as
fractional credit (1/k for a k-way tie that includes the right answer).

    chance            1/4 by construction (answer positions are balanced)
    lexical_overlap   pick the candidate sharing the most words with the evidence:
                      the neuron's other steered outputs (xprompt, xsign) and its
                      promoted logit-lens tokens (all tiers)
    most_changed      pick the candidate least similar to the unsteered output
    least_changed     pick the candidate most similar to the unsteered output
"""

import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

WORD = re.compile(r"[^\W\d_]{2,}", re.UNICODE)


def words(text):
    return {w.casefold() for w in WORD.findall(text)}


def credit(scores, answer):
    """Fractional credit for an argmax pick with ties."""
    best = max(scores.values())
    winners = [k for k, v in scores.items() if v == best]
    return 1 / len(winners) if answer in winners else 0.0


def lexical_overlap(task):
    q = task["question"]
    base = words(q["unsteered_output"])
    evid = set()
    for e in task["evidence"]:
        evid |= words(e["steered_output"]) - words(e["unsteered_output"])  # words steering added
    lens = set()
    for t in task["lens_promoted"]:
        lens |= words(t["token"])
    out = {}
    for letter, text in q["candidates"].items():
        new = words(text) - base  # words this candidate has that the unsteered output lacks
        out[letter] = len(new & evid) + len(new & lens)
    return out


def similarity_to_baseline(task):
    q = task["question"]
    return {l: SequenceMatcher(None, q["unsteered_output"], t).ratio() for l, t in q["candidates"].items()}


BASELINES = {
    "lexical_overlap": lexical_overlap,
    "most_changed": lambda t: {l: -s for l, s in similarity_to_baseline(t).items()},
    "least_changed": similarity_to_baseline,
}


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "tasks")
    per = defaultdict(lambda: defaultdict(list))  # baseline -> tier -> credits
    for d in sorted(p for p in root.iterdir() if (p / "task.toml").exists()):
        task = json.loads((d / "environment" / "task.json").read_text())
        answer = json.loads((d / "tests" / "answer_key.json").read_text())["choice"]
        for name, fn in BASELINES.items():
            per[name][task["tier"]].append(credit(fn(task), answer))
    tiers = sorted({t for b in per.values() for t in b})
    rows = {"chance": {t: 0.25 for t in tiers}}
    for name, by_tier in per.items():
        rows[name] = {t: sum(v) / len(v) for t, v in by_tier.items()}
        allv = [x for v in by_tier.values() for x in v]
        rows[name]["all"] = sum(allv) / len(allv)
    rows["chance"]["all"] = 0.25
    n = {t: len(next(iter(per.values()))[t]) for t in tiers}
    cols = tiers + ["all"]
    print(f"{'baseline':18}" + "".join(f"{c:>10}" for c in cols))
    print(f"{'(n tasks)':18}" + "".join(f"{n.get(c, sum(n.values())):>10}" for c in cols))
    for name, r in rows.items():
        print(f"{name:18}" + "".join(f"{r[c]:>10.2f}" for c in cols))
    out = root.parent / "results" / "baselines.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n": n, "accuracy": rows}, indent=1))


if __name__ == "__main__":
    main()
