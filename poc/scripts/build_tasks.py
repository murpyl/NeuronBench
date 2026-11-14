"""Build Harbor task folders from an exported ground-truth file.

    python3 scripts/build_tasks.py data/<model_id>_L14.json --per-tier 8 --out tasks

Every task is a 4-way forced choice: one neuron was steered, four candidate
outputs are shown, exactly one came from that neuron. Tiers differ only in the
evidence the agent is given about the neuron:

    xprompt  lens + the neuron's steered outputs on two OTHER prompts, same dose
    xsign    lens + the neuron's steered outputs at POSITIVE doses; question is a negative dose
    lens     logit lens only (weights-only evidence, no steered outputs at all)

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
from pathlib import Path

LETTERS = "ABCD"

# tier -> (evidence rollout keys, question rollout key)
TIERS = {
    "xprompt": (["who@+0.8", "snake@+0.8"], "orange@+0.8"),
    "xsign": (["who@+0.5", "who@+0.8", "snake@+0.5", "snake@+0.8", "orange@+0.5", "orange@+0.8"], "who@-0.7"),
    "lens": ([], "orange@+0.8"),
}

TIER_BLURB = {
    "xprompt": "its logit lens and its steered outputs on two other prompts at the same dose",
    "xsign": "its logit lens and its steered outputs at positive doses (the question uses a negative dose)",
    "lens": "its logit lens only (no steered outputs)",
}


def fence(text: str) -> str:
    return "~~~~text\n" + text.rstrip("\n") + "\n~~~~"


def split_key(key: str) -> tuple[str, str]:
    prompt, dose = key.split("@")
    return prompt, dose


def lens_md(unit: dict) -> str:
    def row(items: list[dict]) -> str:
        return ", ".join(f"{json.dumps(t['token'], ensure_ascii=False)} ({t['z']:+.1f})" for t in items)

    return (
        "**Logit lens** (weights only: the neuron's output direction projected through the unembedding; "
        "numbers are z-scores across the vocabulary).\n\n"
        f"- Most promoted tokens: {row(unit['lens_up'])}\n"
        f"- Most suppressed tokens: {row(unit['lens_down'])}\n"
    )


def instruction_md(data: dict, tier: str, unit: dict, candidates: list[dict]) -> str:
    layer = data["layer"]
    evidence_keys, q_key = TIERS[tier]
    q_prompt, q_dose = split_key(q_key)
    name = f"L{layer}/N{unit['neuron']}"
    parts = [
        "# Predict the effect of steering one neuron",
        "",
        f"You are studying **{data['model_name']}**, a 28-layer chat model with 3072 MLP neurons per layer.",
        "",
        f"An experimenter *steered* single MLP neurons in layer {layer}. Steering a neuron means: at every token "
        "position, add a multiple of that neuron's output direction (its column of the MLP down-projection, scaled "
        f"to unit length) to the residual stream at layer {layer}. The multiple is `dose x median residual norm of "
        "the layer`, so dose +0.8 is a push of 80% of the typical residual norm, and a negative dose pushes the "
        f"opposite way. The model then answered a prompt with greedy decoding, up to {data['max_tokens']} tokens, "
        "thinking disabled. Outputs are shown raw and may be cut off or degenerate.",
        "",
        f"## Evidence about neuron {name}",
        "",
        f"You are given {TIER_BLURB[tier]}.",
        "",
        lens_md(unit),
    ]
    by_prompt: dict = {}
    for key in evidence_keys:
        by_prompt.setdefault(split_key(key)[0], []).append(key)
    for prompt, keys in by_prompt.items():
        parts += [
            f"### Prompt {json.dumps(data['prompts'][prompt])}",
            "",
            "Unsteered output (first 300 characters):",
            "",
            fence(data["baselines"][prompt][:300]),
            "",
        ]
        for key in keys:
            parts += [
                f"Output with {name} steered at dose {split_key(key)[1]}:",
                "",
                fence(unit["rollouts"][key]["text"]),
                "",
            ]
    parts += [
        "## Question",
        "",
        f"The same neuron {name} was steered at dose **{q_dose}** on the prompt "
        f"**{json.dumps(data['prompts'][q_prompt])}**",
        "",
        "The unsteered model's output on this prompt is:",
        "",
        fence(data["baselines"][q_prompt]),
        "",
        f"Below are four candidate outputs. Exactly one was produced by steering {name}. The other three were "
        f"produced by steering three *other* layer-{layer} neurons at the same dose on the same prompt. "
        f"Which one came from {name}?",
        "",
    ]
    for letter, cand in zip(LETTERS, candidates):
        parts += [f"### Candidate {letter}", "", fence(cand["text"]), ""]
    parts += [
        "## How to answer",
        "",
        "Write your answer to `/app/answer.json` in exactly this form:",
        "",
        '```json\n{"choice": "A", "reasoning": "one or two sentences on why"}\n```',
        "",
        "`choice` must be one of A, B, C, D. Only `choice` is graded. You have no internet access and do not need "
        "it: everything you need is in this file, and the same data is in `/app/task.json`.",
        "",
    ]
    return "\n".join(parts)


TASK_TOML = """version = "1.0"

[task]
name = "neuron-predict/{task_id}"
description = "Identify which of four steered outputs came from one given MLP neuron (tier: {tier})."
keywords = ["interpretability", "steering", "prediction"]

[metadata]
tier = "{tier}"
layer = {layer}
neuron = {neuron}
question = "{question}"
category = "mechanistic-interpretability"

[agent]
timeout_sec = 600.0
network_mode = "allowlist"
allowed_hosts = ["api.anthropic.com", "api.openai.com"]

[verifier]
timeout_sec = 120.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
"""

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY task.json /app/task.json
"""

TEST_SH = """#!/bin/bash
# Grader. Runs after the agent finishes; /tests is not present while the agent works.
mkdir -p /logs/verifier
python3 /tests/grade.py
"""

GRADE_PY = '''"""Compare /app/answer.json with the answer key and write the reward."""
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
# Plain reward.txt: the hosted Valkyrie used for the hackathon rejects datasets that carry a
# custom metric.py ("Custom scoring isn't available"), so per-tier accuracy is computed offline
# by scripts/score_runs.py from the task ids.
Path("/logs/verifier/reward.txt").write_text(str(reward))
'''


def build(data: dict, per_tier: int, out: Path, seed: int) -> list[dict]:
    rng = random.Random(seed)
    neurons = [u for u in data["units"] if u["kind"] == "neuron"]
    rng.shuffle(neurons)
    targets = iter(neurons)
    layer = data["layer"]
    manifest = []
    if out.exists():
        shutil.rmtree(out)

    for tier, (evidence_keys, q_key) in TIERS.items():
        q_prompt, _ = split_key(q_key)
        baseline = data["baselines"][q_prompt]
        # Balanced answer positions, so that "always answer D" scores exactly chance.
        positions = [i % 4 for i in range(per_tier)]
        rng.shuffle(positions)
        made = 0
        while made < per_tier:
            unit = next(targets)  # each neuron is the target of at most one task
            target_text = unit["rollouts"][q_key]["text"]
            if target_text.strip() == baseline.strip():
                continue  # steering did nothing here: the question would have no signal
            pool = [u for u in neurons if u["id"] != unit["id"]]
            rng.shuffle(pool)
            texts, distractors = {target_text}, []
            for u in pool:
                t = u["rollouts"][q_key]["text"]
                if t in texts or t.strip() == baseline.strip():
                    continue
                texts.add(t)
                distractors.append(u)
                if len(distractors) == 3:
                    break
            cands = [{"neuron": u["neuron"], "text": u["rollouts"][q_key]["text"], "is_target": False}
                     for u in distractors]
            cands.insert(positions[made], {"neuron": unit["neuron"], "text": target_text, "is_target": True})
            answer = LETTERS[positions[made]]

            task_id = f"l{layer}-n{unit['neuron']:04d}-{tier}"
            d = out / task_id
            (d / "environment").mkdir(parents=True)
            (d / "tests").mkdir()
            (d / "solution").mkdir()
            (d / "instruction.md").write_text(instruction_md(data, tier, unit, cands))
            (d / "task.toml").write_text(TASK_TOML.format(
                task_id=task_id, tier=tier, layer=layer, neuron=unit["neuron"], question=q_key))
            (d / "environment" / "Dockerfile").write_text(DOCKERFILE)
            public = {
                "model": data["model_name"], "layer": layer, "neuron": unit["neuron"], "tier": tier,
                "lens_promoted": unit["lens_up"], "lens_suppressed": unit["lens_down"],
                "evidence": [{"prompt": data["prompts"][split_key(k)[0]], "dose": float(split_key(k)[1]),
                              "steered_output": unit["rollouts"][k]["text"],
                              "unsteered_output": data["baselines"][split_key(k)[0]]} for k in evidence_keys],
                "question": {"prompt": data["prompts"][q_prompt], "dose": float(split_key(q_key)[1]),
                             "unsteered_output": baseline,
                             "candidates": {l: c["text"] for l, c in zip(LETTERS, cands)}},
            }
            (d / "environment" / "task.json").write_text(json.dumps(public, ensure_ascii=False, indent=1))
            key = {"task_id": task_id, "tier": tier, "choice": answer,
                   "candidate_neurons": {l: c["neuron"] for l, c in zip(LETTERS, cands)}}
            (d / "tests" / "answer_key.json").write_text(json.dumps(key, indent=1))
            (d / "tests" / "grade.py").write_text(GRADE_PY)
            (d / "tests" / "test.sh").write_text(TEST_SH)
            (d / "tests" / "test.sh").chmod(0o755)
            (d / "solution" / "solve.sh").write_text(
                "#!/bin/bash\n" + f"echo '{{\"choice\": \"{answer}\", \"reasoning\": \"oracle\"}}' > /app/answer.json\n")
            (d / "solution" / "solve.sh").chmod(0o755)
            manifest.append({"task_id": task_id, "tier": tier, "neuron": unit["neuron"], "answer": answer})
            made += 1
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("data", type=Path)
    ap.add_argument("--per-tier", type=int, default=8)
    ap.add_argument("--out", type=Path, default=Path("tasks"))
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    data = json.loads(args.data.read_text())
    manifest = build(data, args.per_tier, args.out, args.seed)
    # The manifest holds the answers, so it lives next to the data, never inside a task folder.
    (args.data.parent / f"{args.out.name}_manifest.json").write_text(json.dumps(manifest, indent=1))
    by_tier: dict[str, list[str]] = {}
    for m in manifest:
        by_tier.setdefault(m["tier"], []).append(m["answer"])
    for tier, answers in by_tier.items():
        print(f"{tier}: {len(answers)} tasks, answers {''.join(answers)}")


if __name__ == "__main__":
    main()
