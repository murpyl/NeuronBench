# Proof of concept: evidence tiers (`neuron-predict/poc@2` on Valkyrie)

A 24-task pilot built before the main pipeline, kept here for its results and its Valkyrie plumbing. It is the
dataset the two pilot runs below used (`neuron-predict/poc`, revision 2, tag `v1`).

Every task is a 4-way choice (chance 25%): one layer-14 neuron of Qwen3-0.6B was steered, four outputs are shown,
exactly one came from that neuron. The three distractors come from three *other* layer-14 neurons at the same dose
on the same prompt. The tiers differ only in the evidence about the neuron:

| Tier | Evidence | Question |
|---|---|---|
| `xprompt` | logit lens + the neuron's steered outputs on two other prompts at +0.8 | "Describe the color orange." at +0.8 |
| `xsign` | logit lens + its steered outputs at +0.5 and +0.8 on three prompts | "Who are you?" at -0.7 |
| `lens` | logit lens only | "Describe the color orange." at +0.8 |

## Pilot results (8 tasks per tier, so these are noisy)

Agent: `claude_code-v1.0.0` on Valkyrie, Modal sandboxes, about one minute per task.

| | xprompt | xsign | lens | all |
|---|---|---|---|---|
| anthropic/claude-sonnet-4-6 | 7/8 | 3/8 | 4/8 | 14/24 |
| anthropic/claude-haiku-4-5 | 6/8 | 2/8 | 0/8 | 8/24 |
| baseline: lexical overlap with the evidence | 0.53 | 0.16 | 0.25 | 0.31 |
| baseline: most changed from the unsteered output | 0.38 | 0.38 | 0.38 | 0.38 |
| baseline: least changed from the unsteered output | 0.38 | 0.12 | 0.25 | 0.25 |
| chance | 0.25 | 0.25 | 0.25 | 0.25 |

Reading: with behavioural evidence on other prompts the task is mostly solvable; predicting the opposite-sign effect
is near chance; logit lens alone is at or near chance. In the `xsign` failures the model's stated reasoning usually
assumes a negative dose produces the semantic opposite of the positive dose (see `results/answers.jsonl`).

## Layout

```
tasks/      24 Harbor task folders, as pushed
scripts/    export_ground_truth.py (gne sweep + lens -> one JSON), build_tasks.py, baselines.py,
            score_runs.py (Valkyrie results JSON -> per-tier table), slim_sweep.py
data/       the export the tasks were built from, and tasks_manifest.json (answers)
results/    summary.json, answers.jsonl (each model's choice and reasoning), baselines.json
```

Paths inside the scripts assume they sit at the repository root next to a `gguf-neuron-explorer/` checkout.

## Run it

```bash
valkyrie dataset push neuron-predict/poc ./tasks --tag v1
valkyrie run start --agent claude_code-v1.0.0 --dataset neuron-predict/poc@v1 \
  --model anthropic/claude-sonnet-4-6 --provider modal \
  -s ANTHROPIC_API_KEY anthropic-api-key --concurrency 8 --connect
python3 scripts/score_runs.py RUN_ID
```

## Verified on the hackathon's Valkyrie

- `tests/` is not present in the sandbox while the agent works; the grader sees it afterwards (shared verifier).
- `[agent] network_mode = "allowlist"` with exact hostnames works; other hosts are blocked. A wildcard entry such as
  `*.modal.run` makes sandbox setup fail.
- A dataset folder containing `metric.py` is rejected ("Custom scoring isn't available in this Valkyrie
  deployment"), so per-tier scores are computed offline from the task ids.
- mini-SWE-agent accepts a custom model name, and a base URL passed as a secret-backed environment variable
  (`-s OPENAI_API_BASE <secret>`).

## Caveats

- Built from the first 71 neurons of the sweep, before it finished; the full sweep is in `data/raw/`.
- `data/` and `tests/answer_key.json` hold the answers, and this repository is public.
- `scripts/build_tasks.py` gained three comment lines in the generated `grade.py` after the push; a rebuild
  reproduces the tasks apart from that comment.
