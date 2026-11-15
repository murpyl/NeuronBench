# Instruction ablation

Question: do two lines of our own task text cause the failure modes seen in `results/analysis.md`?

- **Dose guide** (all 150 "Which output is it?" tasks): "As a rough guide from a similar model: a dose of 0.5 slips a
  topic in, 0.8 takes the reply over, 1.0 and above starts to break the text, and 3.0 deliberately breaks it."
  Suspected of causing *dose folklore* ("+0.5 should be subtle, so pick the gentlest reply").
- **Base-rate line** (all 105 "Real or null?" tasks): "Roughly half of the neurons in this benchmark are REAL."
  Suspected of producing Sonnet 5.5's best-in-table null Brier by hedging around 0.5.

`neuronbench build --instructions ablated` drops exactly those two sentences. Everything else is the same as v1:
items, evidence, distractors, candidate order, and all 255 `tests/answer.json` files. The ablated tasks were pushed as
`neuronbench/l14-l20-ablated@v1` and `neuronbench/l24-ablated@v1` and run with the same agent (mini-SWE-agent),
provider (Modal) and concurrency (8) as v1. Each model's two runs are compared on the same 255 item IDs. Numbers come
from `scripts/ablation.py` (full output: `ablation.txt`, rows: `ablation.json`).

| model | choice acc v1 → ablated | diff [95% paired CI] | null Brier v1 → ablated | diff [CI] | null AUC v1 → ablated | mean P(real) v1 → ablated | share in 0.4–0.6 v1 → ablated | dose folklore v1 → ablated |
|---|---|---|---|---|---|---|---|---|
| Claude Haiku 5.5 | 0.480 → 0.407 | −0.073 [−0.147, +0.000] | 0.255 → 0.265 | +0.011 [−0.017, +0.038] | 0.56 → 0.52 | 0.59 → 0.50 | 0.71 → 0.60 | 13 → 12 |
| Claude Sonnet 5.5 | 0.420 → 0.373 | −0.047 [−0.113, +0.013] | 0.247 → 0.279 | **+0.032 [+0.001, +0.064]** | 0.57 → 0.55 | 0.49 → 0.34 | 0.93 → 0.24 | 0 → 0 |

The choice set has 150 items; the null set has 105 items (51% real), so a constant answer of 0.5 scores Brier 0.25.
CIs come from a paired bootstrap over items (10,000 resamples; 2,000 for AUC). Dose folklore counts the choice
trajectories matched by the regex in `scripts/ablation.py`. On v1 it reproduces `analysis.md` exactly (Haiku 4.5: 36,
81% wrong; Haiku 5.5: 13, 77% wrong). Sonnet 5.5 shows no reasoning text in its trajectories, so its count is 0 by
construction. Run cost: Haiku 5.5 $0.27, Sonnet 5.5 $3.85.

**Interpretation.** The base-rate line is what produced Sonnet 5.5's null-task win. Without it, Sonnet's mean P(real)
falls from 0.49 to 0.34 against a true rate of 0.51. Its share of answers in 0.4–0.6 falls from 93% to 24% (mostly
0.25–0.35 now), and its Brier worsens by 0.032 [+0.001, +0.064], to 0.279. That is worse than the base-rate baseline
(0.255) and worse than Haiku 5.5. Its AUC hardly moves (0.57 → 0.55), so the line gave it calibration, not
discrimination. Haiku 5.5 moves toward 0.5 instead (mean 0.59 → 0.50) and its Brier does not change significantly.
Removing the dose guide did not help "Which output is it?". Both models got worse: Haiku 5.5 by 7 points, with a CI
that only reaches 0, and Sonnet 5.5 by 5 points, not significant. The drop is spread across doses (Haiku 5.5: 0.52 →
0.44 at |dose| 0.5, 0.50 → 0.39 at 0.7, 0.41 → 0.39 at 0.8). Dose folklore also persists without the guide (Haiku 5.5:
13 → 12 trajectories, 83% wrong), so the habit is not just the guide being read back. This tests Haiku 5.5 only;
Haiku 4.5, the model with 36 folklore trajectories, was not rerun. Caveat: each condition is a single run, and agents
are not deterministic. Haiku 5.5 picks the same letter on only 60% of choice items across the two runs. The paired
bootstrap covers that churn only to the extent it shows up as per-item disagreement, so the choice differences
should be read as "no improvement" rather than as a precise harm.
