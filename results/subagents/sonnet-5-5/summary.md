# anthropic/claude-sonnet-5-5: tier ladder, binary and dense

| tier | n | acc ↑ (binary) | rank score ↑ | letter Brier ↓ | probs valid | legacy acc ↑ | null Brier ↓ (binary) | null dense Brier ↓ | null AUC ↑ | Spearman(p, null_pct) ↑ | legacy null Brier ↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| static | 150/150 + 105/105 | 0.43 [0.35, 0.51] | 0.65 [0.58, 0.70] | 0.306 [0.282, 0.330] | 1.0 | 0.42 [0.34, 0.49] | 0.248 [0.234, 0.261] | 0.169 [0.147, 0.189] | 0.5541 | 0.1151 | 0.247 [0.233, 0.261] |
| transfer | 150/150 + 105/105 | 0.55 [0.47, 0.63] | 0.70 [0.64, 0.76] | 0.282 [0.253, 0.310] | 1.0 | - | 0.293 [0.240, 0.348] | 0.113 [0.084, 0.146] | 0.6229 | 0.2017 | - |
| oracle | 150/150 + 105/105 | 0.74 [0.67, 0.81] | 0.83 [0.78, 0.88] | 0.213 [0.187, 0.241] | 1.0 | 0.71 [0.64, 0.79] | 0.186 [0.155, 0.217] | 0.129 [0.105, 0.152] | 0.8186 | 0.6863 | 0.189 [0.158, 0.221] |

Paired differences vs static (same items, bootstrap 95% CI):

- transfer - static: acc 0.120 [0.027, 0.207], rank_score 0.053 [-0.024, 0.129], letter_brier -0.025 [-0.046, -0.003], brier 0.045 [-0.006, 0.100], dense_brier -0.055 [-0.089, -0.018]
- oracle - static: acc 0.313 [0.220, 0.407], rank_score 0.184 [0.109, 0.258], letter_brier -0.093 [-0.121, -0.066], brier -0.062 [-0.090, -0.034], dense_brier -0.040 [-0.063, -0.017]

Null references (constant answers): p=0.5: Brier 0.250, dense 0.161; p=mean null_pct (0.742): Brier 0.301, dense 0.103; p=binary label: Brier 0.000, dense 0.156
Choice chance: acc 0.25, rank score 0.50, letter Brier 0.375.
