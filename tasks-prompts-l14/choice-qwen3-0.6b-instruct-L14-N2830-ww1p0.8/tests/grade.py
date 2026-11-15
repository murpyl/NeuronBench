"""Grade /app/answer.txt against /tests/answer.json and write /logs/verifier/reward.json (stdlib only)."""
import json
import re
from pathlib import Path

key = json.loads(Path("/tests/answer.json").read_text())
# separate verifier: the agent's /app/answer.txt arrives as an artifact; shared verifier: read it in place
paths = [Path("/logs/artifacts/app/answer.txt"), Path("/app/answer.txt")]
ans_path = next((p for p in paths if p.exists()), None)
raw = ans_path.read_text().strip() if ans_path else ""
detail = {"raw": raw[:200], "key": key}

if key["kind"] == "choice":
    m = re.search(r"\b([ABCD])\b", raw.upper())
    pick = m.group(1) if m else None
    reward = {"choice_acc": int(pick == key["letter"])}
    detail["parsed"] = pick
else:
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", raw)
    p = float(m.group(0)) if m else None
    if p is not None and p > 1 and p <= 100 and "%" in raw:
        p /= 100
    if p is None or not 0 <= p <= 1:
        reward = {"null_brier": 0.0}           # missing or out-of-range answer scores as maximally wrong
    else:
        reward = {"null_brier": 1 - (p - key["real"]) ** 2}
    detail["parsed"] = p

Path("/logs/verifier/reward.json").write_text(json.dumps(reward))
Path("/logs/verifier/detail.json").write_text(json.dumps({**detail, "reward": reward}))
print(json.dumps({**detail, "reward": reward}))
