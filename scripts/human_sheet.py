"""Blind human baseline for "Which output is it?".

python scripts/human_sheet.py make --n 20 --out human/sheet/       # sheet.md + answers.csv
python scripts/human_sheet.py score --answers human/sheet/answers.csv

--items defaults to the 150 original choice items plus the 900 extra-prompt ones; questions are split evenly across
the files, then across layers. The sheet shows each task exactly as the agent saw it. Fill in the `answer` column of
answers.csv (A-D) without looking at data/items*.jsonl, which hold the key.
"""

import argparse
import csv
import json
import random
from pathlib import Path

import numpy as np

from neuronbench.harbor_tasks import choice_instruction
from neuronbench.items import Item

ITEMS = ["data/items.jsonl", "data/items-prompts.jsonl"]


def load(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh]


def choices(path):
    return [it for it in load(path) if it["kind"] == "choice"]


def sample(items, n, rng):
    by_layer = {}
    for it in items:
        by_layer.setdefault(it["layer"], []).append(it)
    layers = sorted(by_layer)
    per, extra = divmod(n, len(layers))
    return [it for k, L in enumerate(layers) for it in rng.sample(by_layer[L], per + (k < extra))]


def make(a):
    rng = random.Random(a.seed)
    per, extra = divmod(a.n, len(a.items))
    picked = [it for k, path in enumerate(a.items) for it in sample(choices(path), per + (k < extra), rng)]
    rng.shuffle(picked)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    intro = ("# NeuronBench human baseline\n\nAnswer each question in `answers.csv` (A, B, C or D). "
             "Ignore the `/app/answer.txt` instruction. Don't open `data/items.jsonl`: it holds the answers.\n")
    parts = [intro]
    for q, it in enumerate(picked, 1):
        body = choice_instruction(Item(**it)).split("## Answer")[0].replace("# Which reply", "## Which reply", 1)
        parts.append(f"\n---\n\n# Question {q}\n\n{body}")
    (out / "sheet.md").write_text("\n".join(parts))
    with open(out / "answers.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["question", "id", "answer"])
        for q, it in enumerate(picked, 1):
            w.writerow([q, it["id"], ""])
    print(f"wrote {out / 'sheet.md'} and {out / 'answers.csv'} ({len(picked)} questions)")


def score(a):
    key = {it["id"]: it["answer"]["letter"] for path in a.items for it in choices(path)}
    with open(a.answers) as fh:
        rows = [r for r in csv.DictReader(fh) if r["answer"].strip()]
    r = np.array([float(row["answer"].strip().upper() == key[row["id"]]) for row in rows])
    bs = np.random.default_rng(0).choice(r, (10000, len(r))).mean(1)
    print(f"accuracy {r.mean():.2f} [{np.quantile(bs, 0.025):.2f}, {np.quantile(bs, 0.975):.2f}] on {len(r)} answered")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--items", nargs="+", default=ITEMS)
    m.add_argument("--n", type=int, default=30)
    m.add_argument("--seed", type=int, default=0)
    m.add_argument("--out", required=True)
    s = sub.add_parser("score")
    s.add_argument("--items", nargs="+", default=ITEMS)
    s.add_argument("--answers", required=True)
    a = ap.parse_args()
    make(a) if a.cmd == "make" else score(a)


if __name__ == "__main__":
    main()
