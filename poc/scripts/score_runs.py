"""Download Valkyrie run results and print accuracy per evidence tier.

    python3 scripts/score_runs.py RUN_ID [RUN_ID ...]      # fetch with the valkyrie CLI, then score
    python3 scripts/score_runs.py                          # score everything already in results/runs/

Writes results/summary.json and results/answers.jsonl (one line per model x task,
with the model's stated reasoning, for picking failure examples).
"""

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "results" / "runs"
TIERS = ["xprompt", "xsign", "lens"]


def fetch(run_id):
    RUNS.mkdir(parents=True, exist_ok=True)
    dest = RUNS / f"{run_id}.json"
    subprocess.run(["valkyrie", "run", "results", run_id, "--path", str(dest), "-y"],
                   check=True, capture_output=True)
    return dest


def grader_line(result):
    """The grader prints one JSON line (expected, got, reasoning); recover it from the verifier output."""
    out = ((result.get("metadata") or {}).get("verifier_output")) or ""
    for line in reversed(out.strip().splitlines()):
        try:
            return json.loads(line)
        except ValueError:
            continue
    return {}


def main():
    for run_id in sys.argv[1:]:
        fetch(run_id)
    summary, answers = [], []
    for path in sorted(RUNS.glob("*.json")):
        d = json.loads(path.read_text())
        contract = d["benchmark_arguments"]["contract"]
        version = (d["benchmark_arguments"].get("dataset_version") or {}).get("id", "?")
        by_tier = defaultdict(list)
        for task_id, r in d["evaluation_results"].items():
            tier = task_id.rsplit("-", 1)[-1]
            reward = (r.get("rewards") or {}).get("reward")
            by_tier[tier].append(reward or 0.0)
            g = grader_line(r)
            answers.append({"run": d["benchmark_id"], "model": contract["model"], "agent": contract["name"],
                            "task": task_id, "tier": tier, "reward": reward, "expected": g.get("expected"),
                            "got": g.get("got"), "reasoning": g.get("reasoning")})
        allv = [x for v in by_tier.values() for x in v]
        if not allv:
            continue
        summary.append({
            "run": d["benchmark_id"], "status": d["status"], "agent": contract["name"], "model": contract["model"],
            "dataset": version, "n": len(allv), "accuracy": sum(allv) / len(allv),
            "by_tier": {t: {"n": len(v), "accuracy": sum(v) / len(v)} for t, v in by_tier.items()},
        })
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=1))
    with (ROOT / "results" / "answers.jsonl").open("w") as f:
        for a in answers:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    print(f"{'model':32}{'agent':20}{'dataset':24}" + "".join(f"{t:>10}" for t in TIERS) + f"{'all':>10}")
    for s in summary:
        cells = ""
        for t in TIERS:
            b = s["by_tier"].get(t)
            cells += f"{(str(round(b['accuracy'] * b['n'])) + '/' + str(b['n'])) if b else '-':>10}"
        cells += f"{str(round(s['accuracy'] * s['n'])) + '/' + str(s['n']):>10}"
        print(f"{s['model']:32}{s['agent']:20}{s['dataset']:24}{cells}")


if __name__ == "__main__":
    main()
