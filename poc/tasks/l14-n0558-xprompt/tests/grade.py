"""Compare /app/answer.json with the answer key and write the reward."""
import json
from pathlib import Path

key = json.loads(Path("/tests/answer_key.json").read_text())
reward, got, note = 0, None, ""
try:
    answer = json.loads(Path("/app/answer.json").read_text())
    got = str(answer.get("choice", "")).strip().upper()[:1]
    reward = int(got == key["choice"])
    note = str(answer.get("reasoning", ""))[:1000]
except FileNotFoundError:
    note = "no /app/answer.json"
except Exception as e:  # malformed JSON, wrong type, ...
    note = f"unreadable answer: {e!r}"

print(json.dumps({"task": key["task_id"], "tier": key["tier"], "expected": key["choice"],
                  "got": got, "reward": reward, "reasoning": note}))
Path("/logs/verifier/reward.txt").write_text(str(reward))
