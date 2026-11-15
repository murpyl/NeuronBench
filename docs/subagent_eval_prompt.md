# Per-model subagent prompt: tier ladder + dense scoring

A template for one subagent per evaluated model. Fill the placeholders and hand everything between the two
`---8<---` lines to the subagent. Shared code it relies on: [`scripts/rank_tasks.py`](../scripts/rank_tasks.py)
(rank-format tasks) and [`scripts/dense_report.py`](../scripts/dense_report.py) (binary + dense scores, the
aggregation format).

| placeholder | meaning | example |
|---|---|---|
| `{MODEL}` | model id exactly as Valkyrie / litellm takes it | `anthropic/claude-haiku-5-5`, `hosted_vllm/Qwen/Qwen3-32B` |
| `{RUN_SECRETS}` | the model's `valkyrie run start` secret/kwarg flags | `-s ANTHROPIC_API_KEY anthropic-api-key` |
| `{PHASE0}` | `build` for exactly one instantiation, `reuse` for all others | `build` |
| `{ALLOWED_HOSTS}` | the agent container's network allowlist; **the same value in every instantiation** (union of all model API hosts, incl. any vLLM endpoint hosts) | `api.anthropic.com,api.openai.com` |
| `{LOCAL_ORACLE}` | `skip`, or `build` to add the optional 4th rung; same value in every instantiation | `skip` |

Run the `{PHASE0}=build` instantiation first and start the others only after it reports Phase 0 done: the
rank-format datasets are shared, and two subagents pushing them at once would race.

---8<---

# NeuronBench: tier ladder and dense scoring for `{MODEL}`

You evaluate **one** model, `{MODEL}`, on NeuronBench (repo `murpyl/NeuronBench`, branch `main`). Other subagents do
the same for other models in parallel, so your outputs must be comparable with theirs and must not change their runs.
Two changes to how a model is measured, both meant to make the benchmark more hill-climbable:

1. **Evidence-tier ladder.** Report a 3-point curve (static → transfer → oracle) instead of one accuracy number.
2. **Dense / partial scoring.** Score a full ranking and probabilities on choice items, and the continuous `null_pct`
   on null items, next to the existing binary metrics.

Let `MODEL_SLUG` = the last `/`-component of `{MODEL}`, lower-cased, with a leading `claude-` removed
(`anthropic/claude-haiku-5-5` → `haiku-5-5`, `openai/gpt-5.6-luna` → `gpt-5.6-luna`,
`hosted_vllm/Qwen/Qwen3-32B` → `qwen3-32b`). This matches the existing exports in `jobs/valkyrie/`.

## Read first (line numbers as of `main`)

- `neuronbench/items.py`
  - `TIERS = ("static", "oracle", "transfer")` (line 27).
  - `augment_evidence` (lines 115–143) adds the tier's measured evidence. **oracle** puts in `sweep_words`, gne rank's
    over-used words **pooled over all prompts and doses** of the neuron (lines 128–131). **transfer** puts in
    `steered_elsewhere`, the neuron's replies to the *other* prompts **at the same dose** (lines 132–135); null items
    get `steered_replies` instead.
  - `_tier_id` (lines 146–150) makes tier-suffixed ids (`choice-oracle-…`, `null-transfer-…`).
    `baselines.tie_seed` maps them back to the static id, which pairs items across tiers.
  - `build_items(..., tier=...)` (lines 205–207) builds the items. The tiers reuse the static seeds, so items match
    one-for-one.
  - Null label: `real = null_pct >= 0.95` (line 177); the continuous `null_pct` is kept in `meta` (line 184), and
    choice items keep it in `meta` too.
  - Difficulty knobs `min_change=0.1`, `match_tol=0.15` (line 65). Don't change them; they define the item set.
- `neuronbench/harbor_tasks.py`
  - `GRADE_PY` (lines 41–55). Choice: `int(pick == key["letter"])`, where `pick` is the **first** standalone A–D in
    the answer (binary, line 44). Null: `1 - (p - real)**2` against the binary label (line 54). It echoes
    `raw` (first 200 chars), `parsed` and the reward into `verifier_output`, which Valkyrie exports keep.
  - `choice_instruction` (line 111) ends with the binary "write exactly one letter" answer section.
  - `INTERVENTION` dose guide (lines 74–79), and the bare `python:3.12-slim` `DOCKERFILE` (line 18): no tools in the
    container, and the verifier runs separately.
- `scripts/rank_tasks.py`: writes the same items as Harbor tasks with one change: the choice answer section asks
  for `B 0.55, D 0.25, A 0.15, C 0.05` (ranking, best first, with probabilities). `GRADE_PY` is untouched, so
  `choice_acc` still grades the first letter, i.e. top-1 accuracy.
- `scripts/dense_report.py`: scores one model's exports at every tier and writes the aggregation files. Its docstring
  defines every metric.
- `results/runs.md`, `README.md` § Results: existing binary-format runs and numbers (e.g. Haiku 5.5: static 0.48,
  transfer 0.48, oracle 0.63 choice accuracy).

## Ground rules (isolation)

- **Write only under `results/subagents/MODEL_SLUG/`** (and your own scratch dirs outside the repo, e.g.
  `~/nb-MODEL_SLUG/`). Work on your own branch `devin/<timestamp>-eval-MODEL_SLUG` off `main`. Your PR must touch
  nothing outside that directory.
- **Do not modify shared code or data**: `neuronbench/`, `scripts/`, `dataset/`, `tests/`, `data/*.jsonl`,
  `jobs/valkyrie/`, `README.md`, `results/*` outside your directory. If shared code looks wrong, stop and report it;
  don't patch it locally and run on the patch, or your numbers stop being comparable.
- **Never write your exports to `jobs/valkyrie/`.** `results.collect_jobs` averages every trial of the same model
  and task it finds, so rank-format runs there would silently change `neuronbench report` for everyone. Export to
  `results/subagents/MODEL_SLUG/runs/`.
- Never push, re-tag or overwrite a Valkyrie dataset unless you are the `{PHASE0}=build` instance and it does not
  exist yet. Prefix every Valkyrie `--label` with `MODEL_SLUG-`.
- Same harness as the existing results: Valkyrie `--agent mini_swe_agent`, `--provider modal`, `--concurrency 8`,
  default limits (600 s agent timeout), one trial per task. Don't add prompts, tools or retries for your model.

## Setup

- Python: system `python3` with `PYTHONPATH=.` from the repo root works (the repo `.venv` may be empty; the
  scripts need only numpy).
- Valkyrie: a logged-in `valkyrie` CLI. If it is missing on your machine, escalate; don't guess an install.
  Quirks: `dataset push` has no `-y` (pipe `< /dev/null`); `run status --ids a,b`; `run results` on a
  still-running run gives a partial export, so re-export once it has finished.

## Phase 0: shared datasets (`{PHASE0}`)

Six rank-format datasets, two per tier, split like the existing ones (layers 14+20: 170 tasks, layer 24: 85 tasks):
`neuronbench/l14-l20-<tier>-rank@v1` and `neuronbench/l24-<tier>-rank@v1` for `<tier>` in `static`, `transfer`,
`oracle`. The items files are `data/items.jsonl`, `data/items-transfer.jsonl` and `data/items-oracle.jsonl`, the
committed `build_items(tier=...)` outputs; don't rebuild them.

```bash
for t in static transfer oracle; do
  f=data/items.jsonl; [ $t != static ] && f=data/items-$t.jsonl
  PYTHONPATH=. python3 scripts/rank_tasks.py --items $f --layers 14,20 --out ~/nb-rank/l14-l20-$t-rank \
      --allowed-hosts {ALLOWED_HOSTS}
  PYTHONPATH=. python3 scripts/rank_tasks.py --items $f --layers 24 --out ~/nb-rank/l24-$t-rank \
      --allowed-hosts {ALLOWED_HOSTS}
done
```

- `build`: build them as above; check counts (170/85 tasks; per tier 150 choice + 105 null overall). For one choice
  task, check that the grader echoes the full ranking and gives `choice_acc` for its first letter. Then push each
  dataset (`valkyrie dataset push neuronbench/<name> ~/nb-rank/<name> --tag v1 < /dev/null`) and verify one task
  with `valkyrie dataset task download <name>@v1 <task> -o x.zip`. If `{LOCAL_ORACLE}=build`, also do the 4th rung
  (below) before reporting Phase 0 done.
- `reuse`: don't push. Build locally as above anyway, then download one choice task from each dataset and diff its
  `instruction.md` and `task.toml` against your local build. Any mismatch (other allowlist, other text): stop and
  report.

## Task 1: tier ladder

Run `{MODEL}` on all six rank-format datasets (all three tiers, both layer splits):

```bash
valkyrie run start --agent mini_swe_agent --dataset neuronbench/<split>-<tier>-rank@v1 --model {MODEL} \
    --provider modal {RUN_SECRETS} --concurrency 8 --label MODEL_SLUG-<split>-<tier>-rank --connect
valkyrie run results <run-id> --path results/subagents/MODEL_SLUG/runs/<split>-<tier>-rank.json   # once finished
```

- First, probe the model id cheaply (`--slice 0:2`). A `NotFoundError` in `valkyrie run errors` means a bad id.
- Report accuracy **per tier as a 3-point curve** (static, transfer, oracle) with bootstrap 95% CIs, plus paired
  differences vs static on matched items (`dense_report.py` computes both). Don't collapse the tiers into one number.
- Read the curve with these points in mind:
  - **The oracle rung is not a 100% ceiling.** `sweep_words` is pooled over every prompt and dose of the neuron, so on
    a given (prompt, dose) the words often do not show up in the real reply. With it, Haiku 5.5 scores 0.63 and
    Sonnet 5.5 0.71, and the `sweep_words` lookup baseline is in the same range.
  - transfer adds nothing on choice for Haiku 5.5 (+0.00) but does help on null (AUC 0.56 → 0.69).
- Optional 4th rung, only if `{LOCAL_ORACLE}=build` (built once, in Phase 0, as tier name `oracle_local`): oracle
  words computed only from the neuron's steered replies **at the item's dose on the other prompts**. Score each word
  the same way as `sweep_words`: words absent from every unsteered reply, Poisson z of the neuron's count against the
  random controls on the same conditions. **Never include the item's own (prompt, dose) condition**: those words come
  from the correct reply itself, which leaks the answer and makes the rung trivially solvable.
  - This needs the raw sweeps (`git worktree add ~/nb-raw origin/data/qwen3-0.6b-L14 --detach`, then
    `data/raw/L{14,20,24}-main_rel*` and `data/evidence/`).
  - First rebuild static with `neuronbench build --n-choice 50 --n-null 35` from the three runs and `cmp` against
    `data/items.jsonl`. Only proceed if it matches.
  - Put the code in a **new** file `scripts/tier_oracle_local.py`, without changing `TIERS` or `augment_evidence`. It
    should produce `data/items-oracle_local.jsonl` with ids `*-oracle_local-*` and `meta.tier = "oracle_local"`, so
    that `tie_seed` pairs it. Push `neuronbench/{l14-l20,l24}-oracle_local-rank@v1`.
  - These shared files go in a separate PR from the build instance. If this is more than a few hours of work, skip
    the rung and say so.

## Task 2: dense scoring

All of this comes from the same rank-format runs. The verifier's echoed answer is enough, so don't change the grader.

- **(a) Choice: ranking and probabilities.** The rank-format instruction asks for all four letters best-first with
  probabilities. `dense_report.py` reports:
  - `acc`: top-1, the binary metric; it must equal the grader's `choice_acc`, see `top1_matches_grader`.
  - `rank_score`: 1, 2/3, 1/3, 0 for the true reply ranked 1st–4th. Chance is 0.5.
  - `letter_brier`, a loss: `0.5 · Σ_k (p_k − y_k)²`. Chance (uniform) is 0.375. Answers without four valid
    probabilities count as one-hot on the first letter.
  - Also report `probs_valid` and `full_ranking` (the share of answers that followed the format). A low share is a
    finding; don't hand-fix answers.
- **(b) Null: continuous target.** `dense_brier = (p − meta.null_pct)²` next to the binary `brier = (p − real)²`.
  Missing or out-of-range p scores 1 on both, as in the grader.
  - The continuous target is compressed. The constant p = mean `null_pct` (0.742) gets dense Brier 0.103, better than
    answering the true binary label (0.156); p = 0.5 gets 0.161. So always show the references `dense_report.py`
    prints, and `spearman_null_pct`, next to the number.
  - Example, from the existing Haiku 5.5 binary-format exports: transfer − static is −0.014 [−0.037, +0.008] in binary
    Brier but −0.024 [−0.040, −0.010] in dense Brier. The dense score resolves an improvement the binary one doesn't.
- **(c) Side by side.** Report binary (`acc`, `brier`, `auc`) and dense (`rank_score`, `letter_brier`,
  `dense_brier`, `spearman_null_pct`) in one table per tier.
  - Where binary-format exports of `{MODEL}` already exist in `jobs/valkyrie/` (`<split>[-<tier>]-MODEL_SLUG.json`),
    pass them as `--legacy <tier> …`. The table then shows the legacy accuracy and Brier, so the instruction change
    (one letter → ranking) can be checked for its effect on top-1.
  - Do not rerun legacy tiers that are missing.

```bash
R=results/subagents/MODEL_SLUG
PYTHONPATH=. python3 scripts/dense_report.py --model {MODEL} --out $R \
    --tier static   data/items.jsonl          $R/runs/l14-l20-static-rank.json   $R/runs/l24-static-rank.json \
    --tier transfer data/items-transfer.jsonl $R/runs/l14-l20-transfer-rank.json $R/runs/l24-transfer-rank.json \
    --tier oracle   data/items-oracle.jsonl   $R/runs/l14-l20-oracle-rank.json   $R/runs/l24-oracle-rank.json \
    [--legacy static jobs/valkyrie/l14-l20-MODEL_SLUG.json jobs/valkyrie/l24-MODEL_SLUG.json ...]
```

(With `{LOCAL_ORACLE}=build`, add `--tier oracle_local data/items-oracle_local.jsonl …`.)

## Deliverables (the aggregation contract)

Everything goes in `results/subagents/MODEL_SLUG/`:

| file | content |
|---|---|
| `summary.json` | written by `dense_report.py`, unedited. Per tier, `choice.{acc, rank_score, letter_brier}` and `null.{brier, dense_brier}` as `{mean, lo, hi}`, plus `null.{auc, spearman_null_pct}`, `n` / `n_answered`, `legacy`, `paired_vs_static`, `null_references` |
| `summary.md` | the same as a table, written by `dense_report.py` |
| `per_item.jsonl` | one row per (tier, format, item), written by `dense_report.py` |
| `runs/*.json` | the six (or eight) Valkyrie exports |
| `runs.json` | `{"model", "model_slug", "agent": "mini_swe_agent", "datasets": {tier: [..]}, "run_ids": {dataset: id}, "failed_trials": {dataset: n}, "cost_usd": {dataset: x or null}, "local_oracle": "{LOCAL_ORACLE}", "repo_commit": sha}` |
| `notes.md` | ≤ 15 lines: format compliance, failures or timeouts, and anything that makes this model's numbers not comparable |

`summary.json` must cover all three tiers (`static`, `transfer`, `oracle`). If an item is missing from an export, it
is left out of the means and shows in `n_answered`. Don't rerun selectively to fill holes. Re-export once the run
has finished, and say so in `notes.md` if trials failed.

Open one PR with only that directory. Finish with a message containing the `summary.md` table and this block:

```json
{"model": "{MODEL}", "model_slug": "MODEL_SLUG", "summary": "results/subagents/MODEL_SLUG/summary.json",
 "acc": {"static": 0.0, "transfer": 0.0, "oracle": 0.0},
 "rank_score": {"static": 0.0, "transfer": 0.0, "oracle": 0.0},
 "null_dense_brier": {"static": 0.0, "transfer": 0.0, "oracle": 0.0},
 "top1_matches_grader": true, "probs_valid_min": 0.0, "pr": "<url>", "blockers": []}
```

---8<---
