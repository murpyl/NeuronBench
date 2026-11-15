# Reproducing NeuronBench

Full pipeline: ground truth with gne, building tasks (all tiers), running models locally or on Valkyrie, and the
report. The short version is in the [README](../README.md#run-it). Run every command from the repo root.

## Layout

```
neuronbench/       gne_io (read sweeps), evidence (sanitise), items (build items), harbor_tasks (write tasks),
                   baselines, results (collect Harbor jobs, tables, plots), cli
dataset/metric.py  Harbor dataset metric: accuracy and Brier score with bootstrap 95% CIs
scripts/export_evidence.py   run next to gne to dump per-neuron evidence
modal/serve_vllm.py          open-weight models as OpenAI-compatible endpoints on Modal
tests/             pytest on a synthetic sweep
data/raw/          the gne sweeps (slimmed), data/evidence/ the per-neuron static evidence: inputs to `neuronbench build`
data/items*.jsonl  every item with its hidden answer, one file per tier
tasks/             the benchmark as Harbor tasks (255, static tier); tasks-prompts-l{14,20,24}/ the 900 more-prompts tasks
```

**Quick start.** The built tasks are committed, so `harbor run -p tasks ...` (section 3) works on a fresh clone. To
rebuild them, skip section 1 (its outputs are committed in `data/raw/` and `data/evidence/`) and run section 2:
the commands there reproduce `data/items*.jsonl` and `tasks*/` byte for byte.

## 1. Ground truth (on the machine with gne and the model)

```bash
export GNE_MODEL=models/Qwen3-0.6B-Q8_0.gguf
gne verify                                   # once per model/backend
gne stats resid
gne stats act                                # optional: activation statistics in the evidence
for L in 14 20 24; do
  gne lens logit --layer $L
  gne sweep --layer $L                       # 384 random neurons + 64 random controls, design main_rel
  gne sweep --layer $L --neurons <ids>       # optional extras: e.g. the 64 sharpest logit-lens neurons (more REAL items)
  gne rank --run L$L-main_rel
done
python scripts/export_evidence.py --model $GNE_MODEL --run ~/.gne/runs/<model_id>/L*-main_rel.jsonl --out data/evidence
```

Copy `~/.gne/runs/<model_id>/L*-main_rel.{jsonl,meta.json,units.jsonl}` (and any `.part-*.jsonl`) to `data/raw/`.
The files for the README results (layers 14, 20, 24; slimmed as described in [`data/raw/README.md`](../data/raw/README.md))
and the matching `data/evidence/` are committed, so this section is only needed for a new model or layer.

## 2. Build tasks

```bash
uv venv -p 3.12 && uv pip install -e '.[dev,plots]'
neuronbench build --run data/raw/L*-main_rel.jsonl --evidence data/evidence \
    --n-choice 50 --n-null 35 --items data/items.jsonl --out tasks
for T in oracle transfer shuffled trace trace-shuffled; do   # the control and evidence tiers (README / results/analysis.md)
  neuronbench build --run data/raw/L*-main_rel.jsonl --evidence data/evidence --n-choice 50 --n-null 35 \
      --tier $T --items data/items-$T.jsonl --out tasks-$T
done
neuronbench baselines --items data/items.jsonl
harbor lint tasks/*/
harbor run -p tasks -a oracle                # every reward should be 1
```

`--n-choice` / `--n-null` are per layer, so 3 layers × (50 + 35) = 255 items (150 choice, 105 null).
`data/items.jsonl` holds the hidden answer and diagnostics for every item and is what the baselines and report read. Each item's `meta.selection` says
whether its neuron came from gne's seeded `random:384` draw or was hand-picked (extras), so results can be split.

`tasks/` holds task folders only. Valkyrie rejects a dataset that contains `metric.py`, so `dataset/metric.py` stays
out of it. Use it for plain Harbor datasets, or run it on exported rewards.

**Trace tier** (`--tier trace`, and its control `--tier trace-shuffled`). Same 255 items, replies and answers as
static; null items are unchanged. Under the baseline and each of the 4 choice replies the task adds a per-token table:
`base_lp` (log p of the token under the *unsteered* model, teacher-forced on prompt + reply so far), `base_top` (the
unsteered top-1 token, shown only where it differs) and `lens_z` (the neuron's full-vocabulary logit-lens z-score for
that token, from the weights). No number comes from a steered forward pass, so nothing in the table depends on which
reply is the answer; `tests/test_trace.py` checks this. Tables cover only the visible (clipped, ≤ 700 char) text,
re-tokenized. `trace-shuffled` shows the PR #10 donor neuron's static evidence *and* `lens_z`. Traces need the model
once; the build doesn't:

```bash
python scripts/trace_evidence.py --model Qwen3-0.6B-Q8_0.gguf --items data/items.jsonl \
    --run data/raw/L*-main_rel.jsonl --out data/traces.jsonl   # needs gne + llama-cpp-python; CPU is fine
neuronbench build --run data/raw/L*-main_rel.jsonl --evidence data/evidence --n-choice 50 --n-null 35 \
    --tier trace --traces data/traces.jsonl --items data/items-trace.jsonl --out tasks-trace
```

The agent-free bar for this tier is `trace_lens_mean` (pick the reply with the highest dose-signed mean `lens_z`).

### More prompts (choice)

The main sweep has only three task prompts, and per-prompt accuracy varied more than the gap between models. A
top-up sweep runs 100 neurons per layer (from the seeded `random:384` draw, stratified by `null_pct`; lists in
`extra_prompts/`) and the same 64 random controls on ten more prompts at doses -0.7 and +0.8
([`extra_prompts/design.yaml`](../extra_prompts/design.yaml)). `--per-neuron 3` puts each neuron's three questions on
different prompts and balances the prompts (30 questions each per layer). These sweeps ran on CPU (llama.cpp, same
GGUF and gne model id); all four options in a question come from the same sweep, so CPU-vs-Metal numerics never mix
within a question.

```bash
python scripts/prompts_configs.py && export GNE_CONFIGS=$PWD/extra_prompts/gne-configs
for L in 14 20 24; do                        # the design keeps its first name, heldout_rel
  gne --n-seq-max 10 sweep --layer $L --design heldout_rel --prompt-set heldout \
      --neurons "$(cat extra_prompts/neurons-L$L-full.txt)" --yes
  gne rank --run L$L-heldout_rel
  neuronbench build --run data/raw/L$L-heldout_rel.jsonl --evidence data/evidence --n-choice 100 --n-null 0 \
      --per-neuron 3 --items data/items-prompts-L$L.jsonl --out tasks-prompts-l$L
done
cat data/items-prompts-L{14,20,24}.jsonl > data/items-prompts.jsonl     # 900 choice items
```

Valkyrie datasets `neuronbench/l{14,20,24}-prompts@v1` (one per layer); run IDs in
[`results/runs.md`](../results/runs.md), results in README finding 1.

## 3. Run models

Same agent (mini-SWE-agent), prompts and limits for every model.

**Why mini-SWE-agent.** The task is reasoning over a few text files, not software engineering, so the harness should
add as little as possible. mini-SWE-agent is a bash-only loop with no custom tools, scaffolding or system-prompt tricks.
That keeps the comparison about the model. It runs any litellm model (Anthropic, OpenAI and self-hosted vLLM) with
identical prompts and step/cost limits. Its trajectories are plain message logs, so the README's failure modes can be
quoted directly. Claude Code and Codex would bring vendor-specific tooling and prompts, so cross-vendor differences
would partly measure the harness. The container has no intervention tools and no answer key, and its network allows
only the model API hosts (`api.anthropic.com`, `api.openai.com`).


```bash
harbor run -p tasks -a mini-swe-agent -m anthropic/<model> -n 8 -o jobs --job-name <model>
harbor run -p tasks -a mini-swe-agent -m openai/<model>    -n 8 -o jobs --job-name <model>
```

**On Valkyrie** (the hackathon's hosted Harbor; sandboxes on Modal). The dataset must not contain `metric.py`,
and `allowed_hosts` must be exact hostnames. Model keys and base URLs are Valkyrie secrets passed as env vars:

```bash
mkdir -p tasks-l14-l20 tasks-l24                    # we pushed L14+L20 (170 tasks) and L24 (85) as two datasets
cp -r tasks/*-L14-* tasks/*-L20-* tasks-l14-l20/ && cp -r tasks/*-L24-* tasks-l24/
valkyrie dataset push neuronbench/l14-l20 ./tasks-l14-l20 < /dev/null
valkyrie dataset push neuronbench/l24 ./tasks-l24 < /dev/null
valkyrie run start --agent mini_swe_agent --dataset neuronbench/l14-l20@1 \
    --model anthropic/claude-haiku-4-5 --provider modal -s ANTHROPIC_API_KEY anthropic-api-key \
    --concurrency 8 --label haiku-4-5 --connect
# self-hosted vLLM endpoint (its hostname must be in --allowed-hosts at build time). The mini_swe_agent contract
# has no base-URL kwarg, so litellm's hosted_vllm provider reads the endpoint from env vars.
valkyrie run start --agent mini_swe_agent --dataset neuronbench/l14-l20@1 \
    --model hosted_vllm/Qwen/Qwen3-32B --provider modal \
    -s HOSTED_VLLM_API_BASE vllm-base-url-qwen3-32b -s HOSTED_VLLM_API_KEY vllm-api-key \
    -k cost_tracking ignore_errors --concurrency 8 --label qwen3-32b --connect
valkyrie run results <run-id> --path jobs/<label>.json     # neuronbench report reads these too
```

**Open-weight models on Modal.**

```bash
modal secret create neuronbench-vllm VLLM_API_KEY=$(openssl rand -hex 16)
MODEL=openai/gpt-oss-120b GPU=H200 modal deploy modal/serve_vllm.py
MODEL=Qwen/Qwen3-32B      GPU=H200 modal deploy modal/serve_vllm.py
MODEL=Qwen/Qwen3-0.6B     GPU=L4   modal deploy modal/serve_vllm.py
harbor run -p tasks -a mini-swe-agent -m openai/Qwen/Qwen3-32B \
    --base-url https://<workspace>--nb-vllm-qwen3-32b-serve.modal.run/v1 \
    --ae MSWEA_API_KEY=$VLLM_API_KEY -n 8 -o jobs --job-name qwen3-32b
```

The agent runs inside the task container, so the container must reach the model API. By default tasks use
`network_mode = "allowlist"` with `allowed_hosts = ["api.anthropic.com", "api.openai.com"]`. For a Modal endpoint, add its
exact hostname:
`neuronbench build ... --allowed-hosts api.anthropic.com,api.openai.com,<workspace>--nb-vllm-qwen3-32b-serve.modal.run`.
`--allowed-hosts ""` gives unrestricted network.

## 4. Report

```bash
neuronbench report --items data/items.jsonl --jobs jobs/* --out results
```

This writes `results/results.md` (each system with a 95% bootstrap CI, baselines included), `results/results_by_selection.md`
(the same split by random-draw vs hand-picked neurons), `results/results.json`,
and plots: `choice_accuracy.png`, `null_brier.png` and `choice_by_effect_size.png`. A model only beats the
baselines if its interval clears the best baseline's.

Harbor's own end-of-run table averages each reward key over all trials, including trials of the other task type,
which halves both numbers. Use `neuronbench report`, or the dataset `metric.py`, for the real figures.
