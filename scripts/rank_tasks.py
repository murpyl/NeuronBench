"""Rank-format Harbor tasks: the same items, but choice tasks ask for a full ranking with probabilities.

The verifier is unchanged: its first-letter parse still grades the top pick (`choice_acc`), and the raw answer it echoes
into `verifier_output` is what scripts/dense_report.py scores densely. Null tasks are written exactly as before.

python scripts/rank_tasks.py --items data/items-oracle.jsonl --out tasks-oracle-rank --layers 14,20 \
    --allowed-hosts api.anthropic.com,api.openai.com
"""

import argparse
import json
from pathlib import Path

from neuronbench.harbor_tasks import write_task
from neuronbench.items import Item

BINARY_ANSWER = """## Answer

Write exactly one letter, A, B, C or D, to `/app/answer.txt` (for example `echo B > /app/answer.txt`).
Nothing else is graded.
"""

RANK_ANSWER = """## Answer

Rank all four replies from most to least likely to be this neuron's, with your probability for each (they should sum
to 1), and write them as one line to `/app/answer.txt`, most likely first (for example
`echo "B 0.55, D 0.25, A 0.15, C 0.05" > /app/answer.txt`). Your first letter is graded as your answer; the full
ranking is also scored by where the true reply sits in it, and the probabilities by the Brier score, so report your
honest probabilities.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layers", default="", help="comma-separated layers to keep (default: all)")
    ap.add_argument("--agent-timeout", type=float, default=600.0)
    ap.add_argument("--allowed-hosts", default="api.anthropic.com,api.openai.com")
    a = ap.parse_args()
    layers = {int(x) for x in a.layers.split(",") if x.strip()}
    hosts = [h.strip() for h in a.allowed_hosts.split(",") if h.strip()]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for line in Path(a.items).read_text().splitlines():
        if not line.strip():
            continue
        item = Item(**json.loads(line))
        if layers and item.layer not in layers:
            continue
        d = write_task(item, out, agent_timeout=a.agent_timeout, allowed_hosts=hosts)
        if item.kind == "choice":
            p = d / "instruction.md"
            text = p.read_text()
            if text.count(BINARY_ANSWER) != 1:
                raise SystemExit(f"{d.name}: answer section not found; harbor_tasks.choice_instruction changed?")
            p.write_text(text.replace(BINARY_ANSWER, RANK_ANSWER))
        n += 1
    print(f"wrote {n} rank-format tasks to {out}/")


if __name__ == "__main__":
    main()
