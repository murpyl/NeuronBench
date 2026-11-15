# Eval 2: NeuronBench-Heldout

**Question.** From a neuron's static evidence and what it did on the 3 agent-visible prompts, can a model predict
whether pushing it will beat random directions on 10 prompts it never sees?

Eval 1 (the main benchmark) labels each neuron on the same 3 prompts the agent's replies come from, and that label
barely agrees with itself across prompts: splitting the 3 prompts 1 vs 2 gives a median split-half AUC of 0.59 on
layer 20 (`scripts/heldout_reliability.py --prompts who,snake,orange --half 1`). Eval 2 keeps the agent's view and
moves the answer key to held-out prompts.

## Design

| | |
|---|---|
| Agent sees | static evidence (`down_norm`, logit lens) + unsteered and pushed replies on who / snake / orange (existing `main_rel` sweep) |
| Agent answers | P(neuron's vocabulary mass beats 95% of the 64 random controls on the held-out prompts) |
| Answer key | gne `rank` on the held-out sweep only: 10 new prompts (`heldout/design.yaml`) x doses -0.7, +0.8, same 64 seeded controls |
| Neurons | per layer, 100 from gne's `random:384` draw, stratified by 3-prompt `null_pct`: 50 >= 0.95, 25 in 0.8-0.95, 25 < 0.8 (`heldout/neurons-L*.json`) |
| Score | Brier and AUC against the held-out label |

## Claims, decisive evidence, falsifiers (fixed before any model run)

1. **The held-out key is reliable.** Median split-half AUC (5 vs 5 held-out prompts, all 126 splits) >= 0.85.
   *Falsified if* it stays near Eval 1's level; then Eval 2 reports that null and makes no model claims.
2. **Models use the evidence to predict generalization.** They beat the "reuse the 3-prompt label" baseline (old
   `null_pct` as the prediction) on AUC, and fall to that baseline when the evidence comes from another neuron in the
   same layer (shuffled tier). *Falsified if* the paired CI of model minus baseline includes 0, or shuffled scores
   match normal ones.
3. **One pre-specified failure split:** layer 20 vs 24. *Falsified if* the paired CI includes 0.

Baselines: reuse the 3-prompt label; logit-lens lookup; prevalence (constant prediction).

## Steps

On the machine with gne and the model (`GNE_MODEL` set as in the main README):

```bash
python scripts/heldout_configs.py                        # gne's configs + design heldout_rel / prompt set heldout
export GNE_CONFIGS=$PWD/heldout/gne-configs

# pilot: 40 neurons + 64 controls on layer 20 = 2,080 rollouts
gne sweep --layer 20 --design heldout_rel --prompt-set heldout --neurons $(cat heldout/neurons-L20-pilot.txt) --yes
gne rank --run L20-heldout_rel
python scripts/heldout_reliability.py --run ~/.gne/runs/<model_id>/L20-heldout_rel.jsonl \
    --old-units ~/.gne/runs/<model_id>/L20-main_rel.units.jsonl --out heldout/reliability-L20-pilot.json
```

The script prints PASS/FAIL against the bar. Add `--word-unit tokens --model $GNE_MODEL` for gne's exact word unit.

Only if the pilot passes: run the full lists. The pilot neurons are a subset, and gne resumes the same run, so only the
other 60 neurons are swept (3,280 rollouts per layer in total, under the 4,484 of the original `main_rel` sweep).

```bash
for L in 20 24; do
  gne sweep --layer $L --design heldout_rel --prompt-set heldout --neurons $(cat heldout/neurons-L$L-full.txt) --yes
  gne rank --run L$L-heldout_rel
done
```

The pilot `--neurons` list differs from the full list, which is fine for resuming: gne checks the design, prompts,
controls and seed, not the neuron list.
