# anthropic/claude-sonnet-5-5: rank-format runs

- Format compliance: every choice answer was a full A–D ranking with valid probabilities (`full_ranking` = `probs_valid` = 1.0 on all tiers), and our top-1 letter matches the grader's `choice_acc` on every item.
- Failures: 0 failed trials across the six runs (255/255 answered per tier). Exported after each run finished. `l14-l20-oracle-rank` was started from William's Mac and `l24-oracle-rank` from the Devin VM (same account and settings).
- `cost_usd` is null: Valkyrie's run export doesn't carry cost.
- `{LOCAL_ORACLE}` = skip: no per-prompt/per-dose oracle rung.
- Comparability: one letter → ranking leaves top-1 unchanged within CI (paired rank − legacy run: static +0.007 [−0.047, +0.067], oracle +0.027 [−0.007, +0.067]; there is no legacy transfer run for this model).
- Null items: static dense Brier (0.169) is worse than the constant p=0.5 reference (0.161), and transfer's binary and dense null scores move in opposite directions (binary +0.045 [−0.006, +0.100], dense −0.055 [−0.089, −0.018]). Read the null columns alongside the references and Spearman.
