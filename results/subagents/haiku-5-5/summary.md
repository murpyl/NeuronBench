# anthropic/claude-haiku-5-5: tier ladder, binary and dense

| tier | n | acc ↑ (binary) | rank score ↑ | letter Brier ↓ | probs valid | legacy acc ↑ | null Brier ↓ (binary) | null dense Brier ↓ | null AUC ↑ | Spearman(p, null_pct) ↑ | legacy null Brier ↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| static | 150/150 + 105/105 | 0.39 [0.32, 0.47] | 0.58 [0.52, 0.64] | 0.336 [0.312, 0.359] | 1.0 | 0.48 [0.40, 0.56] | 0.250 [0.229, 0.272] | 0.128 [0.109, 0.148] | 0.6019 | 0.2037 | 0.255 [0.233, 0.276] |
| transfer | 150/150 + 105/105 | 0.47 [0.38, 0.54] | 0.65 [0.58, 0.71] | 0.310 [0.283, 0.337] | 1.0 | 0.48 [0.40, 0.56] | 0.249 [0.215, 0.285] | 0.116 [0.094, 0.140] | 0.6583 | 0.205 | 0.240 [0.206, 0.276] |
| oracle | 150/150 + 105/105 | 0.67 [0.60, 0.75] | 0.78 [0.73, 0.84] | 0.247 [0.222, 0.275] | 1.0 | 0.63 [0.56, 0.71] | 0.207 [0.182, 0.233] | 0.085 [0.074, 0.097] | 0.8317 | 0.6808 | 0.210 [0.185, 0.238] |

Paired differences vs static (same items, bootstrap 95% CI):

- transfer - static: acc 0.073 [-0.007, 0.153], rank_score 0.069 [0.004, 0.131], letter_brier -0.026 [-0.045, -0.008], brier -0.001 [-0.022, 0.022], dense_brier -0.012 [-0.027, 0.003]
- oracle - static: acc 0.280 [0.187, 0.373], rank_score 0.204 [0.136, 0.278], letter_brier -0.089 [-0.118, -0.062], brier -0.043 [-0.064, -0.023], dense_brier -0.043 [-0.059, -0.029]

Null references (constant answers): p=0.5: Brier 0.250, dense 0.161; p=mean null_pct (0.742): Brier 0.301, dense 0.103; p=binary label: Brier 0.000, dense 0.156
Choice chance: acc 0.25, rank score 0.50, letter Brier 0.375.
