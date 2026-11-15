# openai/gpt-5.6-luna: rank-format runs

- Format compliance: every choice answer was a full A–D ranking with valid probabilities (`full_ranking` = `probs_valid` = 1.0 on all tiers), and our top-1 letter matches the grader's `choice_acc` on every item.
- Failures: 0 failed trials across the six runs (255/255 answered per tier). All six runs were started from the Devin VM and exported after each finished.
- `cost_usd` is null: Valkyrie's run export doesn't carry cost.
- `{LOCAL_ORACLE}` = skip: no per-prompt/per-dose oracle rung.
- Comparability: one letter → ranking leaves static top-1 unchanged within CI (paired rank − legacy run: +0.047 [−0.013, +0.107]). This model has no legacy transfer or oracle runs.
- Transfer adds nothing for this model on any metric (acc +0.007 [−0.073, +0.093], rank score −0.004, dense null Brier −0.009, all CIs span 0).
- Null items: binary null Brier is worse than the constant p=0.5 (0.25) on every tier, including oracle (0.307) where AUC is 0.81. The ordering is good, but p is overconfident. Dense null Brier at oracle (0.083) beats the mean-`null_pct` constant (0.103).
