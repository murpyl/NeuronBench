# Layer-14 pilot of the scaffold tasks on Valkyrie (`neuronbench/l14-pilot@1`)

Built on `devin/1794697195-scaffold` at commit `9b0326b` from the data on the branch `data/qwen3-0.6b-L14`:

```bash
neuronbench build --run data/raw/L14-main_rel.jsonl --evidence data/evidence --n-choice 30 --n-null 20 --out tasks
valkyrie dataset push neuronbench/l14-pilot ./tasks --tag v1      # accepted: 50 tasks (30 choice, 20 null, 10 real)
```

## What Valkyrie accepted and ran

- `schema_version = "1.4"`, `artifacts = ["/app/answer.txt"]` and `[verifier] environment_mode = "separate"`.
- `[environment] network_mode = "allowlist"` with `allowed_hosts = ["api.anthropic.com", "api.openai.com"]`.
  mini-SWE-agent reached the Anthropic API through it on all five tasks.
- Rewards under custom keys (`choice_acc`, `null_brier`) from `/logs/verifier/reward.json`.
- The separate verifier adds about 36 s of grading per task.

## Runs

| Run | Agent | Tasks | Result |
|---|---|---|---|
| `df5f62cd-4c7b-4949-b84e-ce5232683321` | `neuronbench_oracle` (reference answers) | all 50 | 30/30 `choice_acc` = 1.0, 20/20 `null_brier` = 1.0, no errors |
| `3c7d7b72-f808-4b33-aa7f-aa38c11c6154` | `mini_swe_agent`, `anthropic/claude-haiku-4-5` | 3 choice + 2 null | choice 1/3; null mean `null_brier` 0.824 (Brier 0.176) |

```bash
valkyrie agent push agents/neuronbench_oracle
valkyrie run start --agent neuronbench_oracle --dataset neuronbench/l14-pilot@v1 --provider modal \
  --concurrency 10 --label l14-pilot-reference-answers --connect
valkyrie agent install https://github.com/vals-ai/public-agent-registry/tree/main/agents/mini_swe_agent
valkyrie run start --agent mini_swe_agent --dataset neuronbench/l14-pilot@v1 --task-ids <5 ids> \
  --model anthropic/claude-haiku-4-5 --provider modal -s ANTHROPIC_API_KEY anthropic-api-key \
  --concurrency 5 --label l14-pilot-mini-swe-haiku-4-5 --connect
```

mini-SWE-agent with Haiku 4.5 cost $0.015 to $0.098 per task (mean $0.041, 3 to 14 API calls), from
`model_stats.instance_cost` in each trajectory.

## Do not use Valkyrie's own aggregate

With two reward keys, Valkyrie averages each key over every trial, including trials of the other task type, and
reports no `final_score`:

| Run | Valkyrie `metrics` | Correct per-type value |
|---|---|---|
| reference answers | `choice_acc` 0.6, `null_brier` 0.4 | 1.0 and 1.0 |
| mini-SWE-agent Haiku | `choice_acc` 0.2, `null_brier` 0.329 | 0.333 and 0.824 |

A dataset-level `metric.py` cannot fix this here (the push is rejected when the folder contains one), so scores must
be computed offline from the per-task rewards in each run's results JSON.

## Layout

```
tasks/                     the 50 task folders as pushed
data/items.jsonl           items with hidden answers and diagnostics, as written by `neuronbench build`
agents/neuronbench_oracle  Valkyrie agent that writes the known answer to /app/answer.txt (Valkyrie has no built-in
                           oracle and /solution is not mounted in the sandbox); answers.json is keyed by task id
jobs/<run>/                `valkyrie run outputs`: neuronbench.json (run results; org id, bucket and email replaced
                           by placeholders) and one folder per task with the agent's saved output
```

`valkyrie run results` / `run outputs` produce this layout, not a Harbor job directory, so `neuronbench report --jobs`
needs an adapter to read it.
