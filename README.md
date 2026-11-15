# NeuronBench

<!-- OVERVIEW: one paragraph, written by a team member (hackathon rule: this paragraph must be human-written). -->
Inspired by the new perspective of "neurons are already clean," we analyze if current LLMs are able to determine the impact of a neuron-level intervention on Qwen3-0.6B when given the logit-lens output of the neuron as a hint. We find that interestingly, every model guesses which output was steered better than random chance, but they do not consistently beat even a naive shortcut baseline. On determining whether a steered direction was influential, no model was able to beat chance. One failure mode is that models overindexed on sharpness of the logit lens, which was mostly uncorrelated with the ground truth.

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
- The `logit_lens` baseline is the obvious non-AI reading of the evidence: pick the reply that gained the most
  logit-lens tokens on the side the dose pushes toward ("up" for a positive dose, "down" for a negative one).
  `scripts/ceiling_baselines.py` tries stronger variants (fuzzy subword matching, script matching, a cross-validated
  learned scorer over text features); none beats it by more than a point.

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
  gne sweep --layer $L                       # 384 random neurons + 64 random controls, design main_rel
  gne sweep --layer $L --neurons <ids>       # optional extras: e.g. the 64 sharpest logit-lens neurons (more REAL items)
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
answer and diagnostics for every item and is what the baselines and report read. Each item's `meta.selection` says
whether its neuron came from gne's seeded `random:384` draw or was hand-picked (extras), so results can be split.

`tasks/` holds task folders only. Valkyrie rejects a dataset that contains `metric.py`, so `dataset/metric.py` stays
out of it. Use it for plain Harbor datasets, or run it on exported rewards.

## 3. Run models

Same agent (mini-SWE-agent), prompts and limits for every model.

**Why mini-SWE-agent.** The task is reasoning over a few text files, not software engineering, so the harness should
add as little as possible. mini-SWE-agent is a bash-only loop with no custom tools, scaffolding or system-prompt tricks.
That keeps the comparison about the model. It runs any litellm model (Anthropic, OpenAI and self-hosted vLLM) with
identical prompts and step/cost limits. Its trajectories are plain message logs, so the failure modes below can be
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
valkyrie dataset push neuronbench/l14-l20 ./tasks   # we pushed tasks for L14+L20 and L24 as two datasets
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

## Results

Qwen3-0.6B (Q8_0), layers 14, 20 and 24; 255 tasks: 150 "Which output is it?" (chance 25%) and 105 "Real or null?"
(54 real at the 95% cutoff). Every model ran as mini-SWE-agent on Valkyrie (`jobs/valkyrie/*.json`, 0 agent
failures), scored offline with `neuronbench report --items data/items.jsonl --jobs jobs/valkyrie/*.json --out results`.
Full tables: `results/results.md`, split by random-draw vs hand-picked neurons in `results/results_by_selection.md`.

| system | Which output is it? (accuracy, 95% CI) | Real or null? (Brier, lower is better) |
|---|---|---|
| Claude Haiku 5.5 | **0.48** [0.40, 0.56] | 0.255 [0.233, 0.276] |
| Claude Sonnet 5.5 | 0.42 [0.34, 0.49] | **0.247** [0.233, 0.261] |
| GPT-5.6-luna | 0.39 [0.31, 0.47] | 0.308 [0.256, 0.360] |
| Claude Haiku 4.5 | 0.39 [0.31, 0.47] | 0.294 [0.244, 0.344] |
| best shortcut: logit-lens lookup (dose-sign aware) | 0.41 [0.33, 0.49] | |
| best shortcut: base rate / evidence logreg | | 0.255 / 0.255 |
| random / always-real | 0.25 | 0.49 |

![choice accuracy](results/choice_accuracy.png)
![null Brier](results/null_brier.png)

**"Which output is it?", split by whether the answer can be read off the text.** In 50 of the 150 items a logit-lens
token (≥ 3 letters) literally occurs in a candidate reply; there, the logit-lens lookup already scores 64%. The other
100 items need an actual prediction from the evidence, and that is the harder test:

| system | lens token in a reply (n = 50) | no lens token in any reply (n = 100) |
|---|---|---|
| Claude Haiku 5.5 | 0.62 [0.48, 0.76] | **0.41** [0.32, 0.51] |
| Claude Sonnet 5.5 | 0.58 [0.44, 0.72] | 0.34 [0.25, 0.43] |
| GPT-5.6-luna | 0.54 [0.40, 0.68] | 0.32 [0.23, 0.41] |
| Claude Haiku 4.5 | 0.52 [0.38, 0.66] | 0.33 [0.24, 0.42] |
| logit-lens lookup baseline | **0.64** | 0.29 |
| random | 0.25 | 0.25 |

Where the lookup works, it does as well as every model or better. Where it doesn't, only Haiku 5.5's interval clears
chance.

**Models don't even apply the lookup consistently.** Each model picks the same reply as the lookup on only 31–35% of
items, and solves only 51–52% of the 61 items the lookup gets right:

| system | same pick as the lookup | accuracy where the lookup is right (n = 61) | where it is wrong (n = 89) |
|---|---|---|---|
| Claude Haiku 5.5 | 0.31 | 0.52 | **0.45** |
| Claude Sonnet 5.5 | 0.33 | 0.52 | 0.35 |
| GPT-5.6-luna | 0.35 | 0.52 | 0.30 |
| Claude Haiku 4.5 | 0.35 | 0.51 | 0.31 |

So the models solve a different set of items from the lookup rather than a superset of it. The evidence supports
more than any single system extracts: "the model or the lookup is right" holds on 59–67% of items.

Headline findings (full analysis with failure modes in `results/analysis.md`; numbers from `scripts/analyze_results.py`):

- **Frontier agents do no better than a word lookup on "Which output is it?"** Models score 39–48% (chance 25%); a
  dose-sign-aware logit-lens lookup scores 41% [33, 49]. GPT-5.6-luna and Haiku 4.5 (39%) are below it, Sonnet 5.5
  (42%) ties it, and only Haiku 5.5 (48%) is ahead: +7 points, paired 95% CI [−3, +18]. Not in size order.
- **They also don't use the evidence consistently.** Models miss about half the items the lookup solves, and
  agree with it on only 31–35% of picks. On the 50 items where a logit-lens token literally occurs in a candidate
  reply, the lookup gets 64% and models 52–62%. On the other 100, the lookup gets 29% and models 32–41%. Large pushes (change ≥ 0.8
  from the unsteered reply) are solved 51–67%, smaller ones 31–40%.
- **Nobody can tell which neurons matter.** "Real or null?" AUC is 0.52–0.57 for all four; the Brier spread
  (0.247–0.308) is calibration only. All models set their probability by the logit-lens peak z-score, which has
  Spearman 0.13 with the truth. Sonnet 5.5 beats the base rate by hedging 0.4–0.6; Haiku 4.5 and GPT-5.6-luna lose by
  saying 0.7–0.9.
- **Deliberation did not help:** Haiku 4.5 (median 6 API calls, $10 run) tied for last; Haiku 5.5 (≤2 calls on 70% of
  tasks, $0.27 run) came first.
- **Different models, different mistakes:** pairwise agreement 39–65%, 44 items missed by all four, plurality vote (40%)
  below the best single model.
- Easier: layer 24, the "orange" prompt, and neurons that are actually real (56–62% vs 34–45% on null neurons).
- **Instruction ablation** (`results/ablation.md`): removing the base-rate line moved Sonnet 5.5's null Brier from
  0.247 to 0.279 (+0.032, paired 95% CI [+0.001, +0.064]; mean P(real) 0.49 → 0.34), so its null-task lead came from
  our text, while removing the dose guide did not remove dose folklore (Haiku 5.5: 13 → 12 trajectories) and lowered
  choice accuracy rather than raising it (Haiku 5.5 −7 points [−15, 0], Sonnet 5.5 −5 [−11, +1]).

### Ceiling controls

Can these items be solved when the evidence is decisive? `neuronbench build --tier {oracle,transfer}` rebuilds the same
255 items (same candidates, shuffles, answers and grader; `data/items-{oracle,transfer}.jsonl`) and adds measured
evidence to the evidence block. **oracle** adds `sweep_words`, the words this neuron's own steered replies over-use
relative to the random controls (with z-scores on null items). **transfer** adds this neuron's steered replies to the
*other* prompts (choice), or to one prompt at the normal doses (null). Run as datasets `neuronbench/{l14-l20,l24}-{oracle,transfer}@1`;
table from `scripts/ceiling_report.py`.

| tier (Haiku 5.5) | Which output is it? (accuracy, 95% CI) | Real or null? Brier / AUC | choice lookup | null lookup Brier |
|---|---|---|---|---|
| static (the benchmark) | 0.48 [0.41, 0.56] | 0.255 / 0.56 | 0.41 (logit-lens) | 0.255 (evidence logreg) |
| transfer | 0.48 [0.40, 0.56] | 0.240 / 0.69 | 0.47 (words from other prompts) | 0.249 |
| oracle | **0.63** [0.55, 0.71] | **0.210** / **0.78** | 0.61 (`sweep_words`) | **0.089** (z-score logreg) |
| oracle, Sonnet 5.5 (static: 0.42, 0.247 / 0.57) | **0.71** [0.64, 0.79] | 0.189 / 0.83 | 0.61 | 0.089 |

Paired over the same items: oracle − static +0.15 [+0.05, +0.25]; transfer − static +0.00 [−0.08, +0.08].
Sonnet 5.5 (run because Haiku's oracle score was under 85%): oracle − static +0.29 [+0.19, +0.39], and it beats the
oracle lookup (0.71 vs 0.61).

- **The task format works; the static evidence is the bottleneck.** On the 82 items where the oracle words clearly point
  at the true reply (it gains the most of them), Haiku 5.5 scores **0.87** (0.50 on the same items with static
  evidence); Sonnet 5.5 scores 0.93. The oracle ceiling is 63–71%, not ~95%, because its words are pooled over all prompts and doses. On 31 items the
  true reply contains none of them, and there Haiku drops to 0.23 (Sonnet 0.35), below its static 0.48. Clipping plays no part:
  none of those 31 unclipped replies contains a sweep word either.
- **Seeing the neuron act on other prompts doesn't help pick its reply here** (+0 points), though it lifts null AUC
  from 0.56 to 0.69: effects of a single-neuron push mostly don't transfer across prompts as reusable words.
- **On "Real or null?" the models leave most of the signal unused.** With oracle z-scores, a one-feature logistic
  regression reaches Brier 0.089, while Haiku 5.5 gets 0.210 (AUC 0.78). So static-tier AUCs of 0.52–0.57 reflect missing
  evidence, but even decisive evidence is only partly used.

### Valkyrie runs

Datasets `neuronbench/l14-l20@1` (layers 14 and 20, 170 tasks) and `neuronbench/l24@1` (layer 24, 85 tasks), agent
`mini_swe_agent`, sandboxes on Modal, concurrency 8. Exports are in `jobs/valkyrie/`.

| model | `l14-l20@1` run ID | `l24@1` run ID |
|---|---|---|
| anthropic/claude-haiku-5-5 | `5dd195b6-7266-438f-a727-d6ac977d94b2` | `5a71463e-5199-41a6-a54a-23d3fff7595a` |
| anthropic/claude-sonnet-5-5 | `8ceb64b0-2f28-4ca3-9ee5-7345b5dcfc49` | `4fe2a846-1f11-4e7b-8afa-7b1dfc1bdea9` |
| openai/gpt-5.6-luna | `ed60a1ae-99a9-4214-a10b-df38cbff5dfb` | `a535e3ba-2e81-4494-a5b3-be3256774992` |
| anthropic/claude-haiku-4-5 | `89db445d-8a72-409e-88ca-092cd2118f0c` | `a99707ce-0e94-40cd-82f0-8d919b497fae` |

Ceiling controls (Haiku 5.5): `l14-l20-oracle@1` `7b0d5db8-672b-4630-be60-417f3ca48ec0`, `l24-oracle@1`
`2d588c84-a1ec-4c56-8297-a5892962806a`, `l14-l20-transfer@1` `d20eee82-ab29-4f74-990f-9ef5b81f5e89`, `l24-transfer@1`
`43f31f60-4a9e-4fda-8838-1f7bb1df1919`; Sonnet 5.5: `l14-l20-oracle@1` `022891c7-f330-4de5-9abb-d734b598b78e`,
`l24-oracle@1` `e817115f-b91c-4cce-b5e3-77040b71b184`.


Instruction ablation (`neuronbench build --instructions ablated`, same settings): datasets
`neuronbench/l14-l20-ablated@v1` and `neuronbench/l24-ablated@v1`, exports `jobs/valkyrie/*-ablated.json`.

| model | `l14-l20-ablated@v1` run ID | `l24-ablated@v1` run ID |
|---|---|---|
| anthropic/claude-haiku-5-5 | `6fca25f9-cbb0-4f5b-8758-b0ff41e06f2b` | `8dd8bb77-2234-44db-a4e3-28db956e68af` |
| anthropic/claude-sonnet-5-5 | `e9df7e12-cbea-49b9-a307-2c3c8c02aad2` | `0a1f2464-a2a0-475d-a84e-b9665999628d` |

Valkyrie's own summary score for these runs is not meaningful: it averages `choice_acc` and `null_brier` over every
trial, including trials of the other task type. Use `neuronbench report` instead.

Failure modes, from the trajectories: picking the *oddest* reply although the controls are change-matched (chance,
and the models do it 28–34% of the time); *dose folklore* ("+0.5 should be subtle, so the gentlest reply"; 81% wrong
for Haiku 4.5); *inventing a trait* from a token list ("this neuron helps the model escape loops"); counting
*subword fragments* (`-ing`, `s`) that occur in every reply; and on the null task, treating logit-lens sharpness or a
"coherent token family" as proof of causal effect.

### Failure trace: Haiku 4.5 on `choice-qwen3-0.6b-instruct-L14-N710-orange-0.7`

Neuron 710 in layer 14, dose −0.7, prompt "Describe the color orange." The neuron is real (beats 64/64 controls);
its logit lens promotes junk tokens (`onium`, `技术和`, `JKLMNOP`) and suppresses role-ish ones (`UserCode`,
`Participant`, `compañ`); `peak_z` 4.9. The real reply was **D**, the two-word `The color orange?`; Haiku answered
**B**, a reply that loops "the color orange in the color family of the color orange".

Haiku's reasoning (7 API calls, $0.05; full transcript in `results/failure_trace_L14-N710.md`): it decided the
down-tokens look "formal / structured", so a negative dose should make the reply "more organised, less weird", then
contradicted itself and picked B because "the neuron normally helps the model escape loops; reversed, the model gets
stuck". Neither step uses the evidence: the logit-lens tokens are vocabulary the neuron writes, not a behavioural
trait, and nothing in them predicts a loop. The model told a story about the neuron and fitted a reply to the
story. Every candidate was a same-magnitude push (changes 0.83–0.92 from the unsteered reply), so "the most broken
one" was no help either, which is the point of the random-direction controls.
