"""Write items as Harbor task folders.

Every task shares the same Dockerfile (so the image is built once and cached); the evidence is inlined in
instruction.md, and the answer key lives only in tests/, which only the verifier sees: it runs in a separate container
and gets the agent's /app/answer.txt as an artifact.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .items import Item

ORG = "neuronbench"

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl git ca-certificates \\
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
"""

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
python3 /tests/grade.py
"""

GRADE_PY = '''"""Grade /app/answer.txt against /tests/answer.json and write /logs/verifier/reward.json (stdlib only)."""
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
    m = re.search(r"\\b([ABCD])\\b", raw.upper())
    pick = m.group(1) if m else None
    reward = {"choice_acc": int(pick == key["letter"])}
    detail["parsed"] = pick
else:
    m = re.search(r"[-+]?\\d*\\.?\\d+(?:[eE][-+]?\\d+)?", raw)
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
'''

EVIDENCE_GUIDE = """Fields of the evidence JSON (all computed from the weights or from unsteered activations; nothing in it
comes from pushing this neuron):
- `down_norm`: length of the neuron's output weight vector (column of W_down).
- `logit_lens.up` / `logit_lens.down`: tokens whose unembedding has the largest / smallest dot product with the
  neuron's output direction, i.e. what the neuron would promote / suppress if its output went straight to the
  logits. `peak_z` is the largest |z-score| of those dot products across the vocabulary.
- `activation` (if present): statistics of the neuron's activation over a text corpus without intervention
  (`absmax`, `q999`, `q99`, `rms`, `mean`).
- `directions` (if present): cosine between the neuron's output direction and named residual-stream directions
  (for example a persona direction), with the neuron's rank in its layer by |cos|.
"""

INTERVENTION = """**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer {layer}'s MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
("{dose_unit}" units). The model is {model}, run with greedy decoding (temperature 0), replies capped at
{max_tokens} tokens. As a rough guide from a similar model: a dose of 0.5 slips a topic in, 0.8 takes the reply
over, 1.0 and above starts to break the text, and 3.0 deliberately breaks it. A negative dose pushes the opposite
way."""

INTERVENTION_ABLATED = """**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer {layer}'s MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
("{dose_unit}" units). The model is {model}, run with greedy decoding (temperature 0), replies capped at
{max_tokens} tokens. A negative dose pushes the opposite way."""

BASE_RATE = " Roughly half of the neurons in this\nbenchmark are REAL."
INSTRUCTIONS = ("v1", "ablated")


def _block(text: str) -> str:
    return "```text\n" + text.replace("```", "'''") + "\n```"


def _evidence(item: Item) -> str:
    return ("## Evidence about the neuron\n\n" + EVIDENCE_GUIDE + "\n```json\n"
            + json.dumps(item.evidence, ensure_ascii=False, indent=1) + "\n```\n")


def choice_instruction(item: Item, instructions: str = "v1") -> str:
    p = item.payload
    intervention = INTERVENTION_ABLATED if instructions == "ablated" else INTERVENTION
    opts = "\n\n".join(f"### Reply {k}\n\n{_block(v)}" for k, v in p["options"].items())
    return f"""# Which reply did this neuron cause?

You are studying MLP neuron {item.neuron} in layer {item.layer} of a small language model.

{intervention.format(layer=item.layer, dose_unit=p['dose_unit'], model=item.model_id, max_tokens=p['max_tokens'])}

For **one** of the four replies below, the vector was this neuron's output direction (its column of W_down) at dose
{p['dose']:+g}. For each of the other three, it was a **random direction of exactly the same length**, added at the
same layer on the same prompt. Your job is to work out which reply this specific neuron produced, using what the
evidence says the neuron writes. All four replies are perturbed by similar amounts, so "the strangest reply" is not
a reliable answer.

## Prompt

{_block(p['prompt'])}

## Reply with no intervention

{_block(p['baseline'])}

## Candidate replies

{opts}

{_evidence(item)}
## Answer

Write exactly one letter, A, B, C or D, to `/app/answer.txt` (for example `echo B > /app/answer.txt`).
Nothing else is graded.
"""


def null_instruction(item: Item, instructions: str = "v1") -> str:
    p = item.payload
    base_rate = "" if instructions == "ablated" else BASE_RATE
    pr = p["protocol"]
    conds = "\n".join(f"- \"{c['prompt']}\" at dose {c['dose']:+g}" for c in pr["conditions"])
    base = "\n\n".join(f"Prompt: \"{k}\"\n\n{_block(v)}" for k, v in p["baselines"].items())
    return f"""# Does pushing this neuron do more than a random push?

You are studying MLP neuron {item.neuron} in layer {item.layer} of {pr['model_id']}, a small language model run with
greedy decoding.

## The experiment that was run

The neuron was pushed by adding its output direction (its column of W_down) to the residual stream at the output of
layer {item.layer}'s MLP, at every token, with length |dose| × the median residual-stream norm at that layer
("{pr['dose_unit']}" units), under each of these conditions (replies capped at {pr['max_tokens']} tokens):

{conds}

The same was done for {pr['random_controls']} random directions of exactly the same length at the same layer.

For each unit (this neuron or a random control), we took the set of tokens in its replies that never appear in any
unsteered reply, using only conditions with |dose| ≤ 1.6. For each such token we computed a Poisson z-score of how
often it appears for this unit compared with the average unit, and summed the five largest positive z-scores into
the unit's **vocabulary mass**. A neuron counts as **REAL** if its vocabulary mass is higher than that of at least
{p['threshold']:.0%} of the random controls; otherwise it counts as **NULL**.{base_rate}

## Unsteered replies

{base}

{_evidence(item)}
## Answer

Estimate the probability that this neuron is REAL and write it as a single number between 0 and 1 to
`/app/answer.txt` (for example `echo 0.7 > /app/answer.txt`). You are scored with the Brier score, so report your
honest probability.
"""


def task_toml(item: Item, name: str, agent_timeout: float, allowed_hosts: list[str]) -> str:
    net = (f'network_mode = "allowlist"\nallowed_hosts = {json.dumps(allowed_hosts)}' if allowed_hosts
           else 'network_mode = "public"')
    return f'''schema_version = "1.4"
artifacts = ["/app/answer.txt"]

[task]
name = "{name}"
version = "1.0.0"
description = "NeuronBench {item.kind} item: {item.model_id} layer {item.layer} neuron {item.neuron}"
keywords = ["interpretability", "neurons", "neuronbench", "{item.kind}"]

[metadata]
kind = "{item.kind}"
model_id = "{item.model_id}"
layer = {item.layer}
neuron = {item.neuron}

[verifier]
timeout_sec = 60.0
environment_mode = "separate"
collect = []

[verifier.env]

[agent]
timeout_sec = {agent_timeout}

[environment]
{net}
build_timeout_sec = 600.0
os = "linux"
mcp_servers = []

[environment.env]

[solution.env]
'''


def safe_name(item_id: str) -> str:
    return item_id.replace("+", "p").replace("/", "_")


def write_task(item: Item, out_dir: Path, *, agent_timeout: float = 600.0,
               allowed_hosts: list[str] | None = None, instructions: str = "v1") -> Path:
    if instructions not in INSTRUCTIONS:
        raise ValueError(f"instructions must be one of {INSTRUCTIONS}, got {instructions!r}")
    tid = safe_name(item.id)
    d = out_dir / tid
    if d.exists():
        shutil.rmtree(d)
    (d / "environment").mkdir(parents=True)
    (d / "tests").mkdir()
    (d / "solution").mkdir()
    (d / "task.toml").write_text(task_toml(item, f"{ORG}/{tid}", agent_timeout, allowed_hosts or []))
    instr = (choice_instruction(item, instructions) if item.kind == "choice"
             else null_instruction(item, instructions))
    (d / "instruction.md").write_text(instr)
    (d / "environment" / "Dockerfile").write_text(DOCKERFILE)
    (d / "tests" / "test.sh").write_text(TEST_SH)
    (d / "tests" / "grade.py").write_text(GRADE_PY)
    (d / "tests" / "answer.json").write_text(json.dumps({"kind": item.kind, **item.answer}))
    oracle = item.answer["letter"] if item.kind == "choice" else str(item.answer["real"])
    (d / "solution" / "solve.sh").write_text(f"#!/bin/bash\necho {oracle} > /app/answer.txt\n")
    for f in (d / "tests" / "test.sh", d / "solution" / "solve.sh"):
        f.chmod(0o755)
    return d
