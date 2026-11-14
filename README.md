# NeuronBench

<!-- OVERVIEW: one paragraph, written by a team member (hackathon rule: this paragraph must be human-written). -->
> **TODO (team):** overview paragraph goes here.

## What it measures

Each task gives an agent the address of one MLP neuron in a small LLM (Qwen3-0.6B by default), static evidence
about it, and a concrete intervention, then asks for a checkable prediction. Ground truth is what actually happened
when we ran the intervention with [gguf-neuron-explorer](https://github.com/balaena01/gguf-neuron-explorer) (`gne`), compared against random
directions of the same size.

| Task | The agent sees | It answers | Scored by | Chance |
|---|---|---|---|---|
| **Which output is it?** (`choice-*`) | evidence, a prompt, the unsteered reply, four replies at the same dose: one from pushing the neuron, three from pushing random directions of exactly the same length | A, B, C or D | accuracy | 0.25 |
| **Real or null?** (`null-*`) | evidence, the sweep protocol, the unsteered replies | P(the neuron's effect beats ≥ 95% of random controls) | Brier score | 0.25 at p = 0.5 |

**Evidence only.** The agent gets static facts computed from the weights and from unsteered activations
(`down_norm`, logit lens top/bottom tokens and `peak_z`, activation statistics, cosine with named directions). Anything
measured from pushing the neuron (`sweep`, `steer_lens`, `evals`, names) is dropped by
[`neuronbench/evidence.py`](neuronbench/evidence.py). The model has no tools to run interventions and no answer key in
its container: the verifier runs in a separate container and only receives `/app/answer.txt`.

**Controls against shortcuts.**
- Distractors are random-direction pushes at the same dose on the same prompt. They are sampled from the controls whose
  distance from the unsteered reply is within 0.15 of the real reply's. So "pick the most broken reply" doesn't work,
  and neither does "pick the middle one". The `most_different` and `change_rank0..3` baselines check this.
- Choice items skip the design's deliberate "break it" dose (|dose| > 1.6) and replies that barely changed.
- Null items are about half REAL and half NULL; NULLs include near-misses (`null_pct` 0.5–0.95) and clear nulls.
- `evidence_logreg` fits a cross-validated logistic regression on the numeric evidence fields. If it does well, the
  evidence leaks the label.
- Items are stratified by effect size (gne `rank` vocabulary mass), and results are reported per quartile.

## Layout

```
neuronbench/       gne_io (read sweeps), evidence (sanitise), items (build items), harbor_tasks (write tasks),
                   baselines, results (collect Harbor jobs, tables, plots), cli
dataset/metric.py  Harbor dataset metric: accuracy and Brier score with bootstrap 95% CIs
scripts/export_evidence.py   run next to gne to dump per-neuron evidence
modal/serve_vllm.py          open-weight models as OpenAI-compatible endpoints on Modal
tests/             pytest on a synthetic sweep
```

## 1. Ground truth (on the machine with gne and the model)

```bash
export GNE_MODEL=models/Qwen3-0.6B-Q8_0.gguf
gne verify                                   # once per model/backend
gne stats resid
gne stats act                                # optional: activation statistics in the evidence
for L in 6 14 20 24; do
  gne lens logit --layer $L
  gne sweep --layer $L                       # 384 neurons + 64 random controls, design main_rel
  gne rank --run L$L-main_rel
done
python scripts/export_evidence.py --model $GNE_MODEL --run ~/.gne/runs/<model_id>/L*-main_rel.jsonl --out data/evidence
```

Copy `~/.gne/runs/<model_id>/L*-main_rel.{jsonl,meta.json,units.jsonl}` (and any `.part-*.jsonl`) to `data/raw/`.

## 2. Build tasks

```bash
uv venv -p 3.12 && uv pip install -e '.[dev,plots]'
neuronbench build --run data/raw/L*-main_rel.jsonl --evidence data/evidence \
    --n-choice 30 --n-null 20 --items data/items.jsonl --out tasks
neuronbench baselines --items data/items.jsonl
harbor lint tasks/*/
harbor run -p tasks -a oracle                # every reward should be 1
```

`--n-choice` / `--n-null` are per layer, so 4 layers × (30 + 20) = 200 items. `data/items.jsonl` holds the hidden
answer and diagnostics for every item and is what the baselines and report read.

`tasks/` holds task folders only. Valkyrie rejects a dataset that contains `metric.py`, so `dataset/metric.py` stays
out of it. Use it for plain Harbor datasets, or run it on exported rewards.

## 3. Run models

Same agent (mini-SWE-agent), prompts and limits for every model:

```bash
harbor run -p tasks -a mini-swe-agent -m anthropic/<model> -n 8 -o jobs --job-name <model>
harbor run -p tasks -a mini-swe-agent -m openai/<model>    -n 8 -o jobs --job-name <model>
```

**Open-weight models on Modal.**

```bash
modal secret create neuronbench-vllm VLLM_API_KEY=$(openssl rand -hex 16)
MODEL=openai/gpt-oss-120b modal deploy modal/serve_vllm.py
MODEL=Qwen/Qwen3-32B      modal deploy modal/serve_vllm.py
harbor run -p tasks -a mini-swe-agent -m openai/Qwen/Qwen3-32B \
    --base-url https://<workspace>--nb-vllm-qwen3-32b-serve.modal.run/v1 \
    --ae MSWEA_API_KEY=$VLLM_API_KEY -n 8 -o jobs --job-name qwen3-32b
```

The agent runs inside the task container, so the container must reach the model API. By default tasks use
`network_mode = "allowlist"` with `allowed_hosts = ["api.anthropic.com", "api.openai.com"]`. For a Modal endpoint, add its
exact hostname (wildcards are not accepted):
`neuronbench build ... --allowed-hosts api.anthropic.com,api.openai.com,<workspace>--nb-vllm-qwen3-32b-serve.modal.run`.
`--allowed-hosts ""` gives unrestricted network.

## 4. Report

```bash
neuronbench report --items data/items.jsonl --jobs jobs/* --out results
```

This writes `results/results.md` (each system with a 95% bootstrap CI, baselines included), `results/results.json`,
and plots: `choice_accuracy.png`, `null_brier.png` and `choice_by_effect_size.png`. A model only beats the
baselines if its interval clears the best baseline's.

Harbor's own end-of-run table averages each reward key over all trials, including trials of the other task type,
which halves both numbers. Use `neuronbench report`, or the dataset `metric.py`, for the real figures.

## Results

TODO: table, plots, and one failure trace.
