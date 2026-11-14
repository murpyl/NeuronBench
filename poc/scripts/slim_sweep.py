"""Copy a gne sweep JSONL without its per-token arrays (token ids, logprobs, top-k candidates).

    python3 scripts/slim_sweep.py ~/.gne/runs/<model_id>/L14-main_rel.jsonl out/L14-main_rel.jsonl

The text, prompt, dose and unit of every rollout are kept, which is all the task
builders read. `gne rank` needs the full file, so run that before slimming.
"""

import json
import sys

DROP = ("token_ids", "logprob", "top_ids", "top_lps")

src, dst = sys.argv[1], sys.argv[2]
n = 0
with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as g:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # truncated last line of an interrupted run
        for k in DROP:
            row.pop(k, None)
        g.write(json.dumps(row, ensure_ascii=False) + "\n")
        n += 1
print(f"{n} rows -> {dst}")
