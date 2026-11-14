"""Reference-answer agent: writes the known answer for the task. Checks the grading path end to end."""
import json, sys
from pathlib import Path
task_id = sys.argv[1]
answers = json.loads((Path(__file__).parent / "answers.json").read_text())
Path("/logs/oracle").mkdir(parents=True, exist_ok=True)
if task_id not in answers:
    Path("/logs/oracle/summary.json").write_text(json.dumps({"task_id": task_id, "error": "unknown task"}))
    sys.exit(f"no reference answer for {task_id}")
Path("/app").mkdir(exist_ok=True)
Path("/app/answer.txt").write_text(answers[task_id] + "\n")
Path("/logs/oracle/summary.json").write_text(json.dumps({"task_id": task_id, "answer": answers[task_id]}))
print("wrote", answers[task_id], "for", task_id)
