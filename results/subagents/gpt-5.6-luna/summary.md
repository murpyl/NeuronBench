# openai/gpt-5.6-luna: tier ladder, binary and dense

| tier | n | acc ↑ (binary) | rank score ↑ | letter Brier ↓ | probs valid | legacy acc ↑ | null Brier ↓ (binary) | null dense Brier ↓ | null AUC ↑ | Spearman(p, null_pct) ↑ | legacy null Brier ↓ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| static | 150/150 + 105/105 | 0.44 [0.36, 0.53] | 0.64 [0.58, 0.70] | 0.343 [0.302, 0.381] | 1.0 | 0.39 [0.31, 0.47] | 0.293 [0.242, 0.344] | 0.128 [0.097, 0.163] | 0.6019 | 0.2012 | 0.308 [0.256, 0.360] |
| transfer | 150/150 + 105/105 | 0.45 [0.37, 0.53] | 0.63 [0.57, 0.69] | 0.356 [0.312, 0.401] | 1.0 | - | 0.322 [0.265, 0.384] | 0.119 [0.084, 0.158] | 0.6454 | 0.2404 | - |
| oracle | 150/150 + 105/105 | 0.71 [0.63, 0.78] | 0.81 [0.75, 0.86] | 0.213 [0.167, 0.257] | 1.0 | - | 0.307 [0.241, 0.377] | 0.083 [0.057, 0.113] | 0.8088 | 0.6554 | - |

Paired differences vs static (same items, bootstrap 95% CI):

- transfer - static: acc 0.007 [-0.073, 0.093], rank_score -0.004 [-0.071, 0.067], letter_brier 0.013 [-0.033, 0.055], brier 0.029 [-0.003, 0.065], dense_brier -0.009 [-0.031, 0.013]
- oracle - static: acc 0.267 [0.180, 0.360], rank_score 0.169 [0.093, 0.247], letter_brier -0.130 [-0.183, -0.075], brier 0.015 [-0.034, 0.065], dense_brier -0.045 [-0.077, -0.016]

Null references (constant answers): p=0.5: Brier 0.250, dense 0.161; p=mean null_pct (0.742): Brier 0.301, dense 0.103; p=binary label: Brier 0.000, dense 0.156
Choice chance: acc 0.25, rank score 0.50, letter Brier 0.375.
