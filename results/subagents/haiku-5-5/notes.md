# anthropic/claude-haiku-5-5: rank-format runs

- Format compliance: every choice answer was a full A–D ranking with valid probabilities (`full_ranking` = `probs_valid` = 1.0 on all tiers), and our top-1 letter matches the grader's `choice_acc` on every item.
- Failures: 0 failed trials across the six runs (255/255 answered per tier). Runs started from William's Mac; exported after they finished.
- `cost_usd` is null: Valkyrie's run export doesn't carry cost.
- `{LOCAL_ORACLE}` = skip: no per-prompt/per-dose oracle rung.
- Comparability: the instruction changed from one letter to a ranking, and each format is a separate run (same items), so format and run-to-run variance are mixed. Paired top-1, rank − legacy binary run (choice items, bootstrap 95% CI): static −0.087 [−0.160, −0.013], transfer −0.013 [−0.080, +0.053], oracle +0.040 [−0.020, +0.107]. Static top-1 is lower in rank format (0.39 vs 0.48), so compare rank-format numbers with rank-format numbers.
- Null items: instruction unchanged; null Brier matches the legacy runs within CI on every tier.
