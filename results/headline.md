## Headline (`scripts/headline_plot.py`)

Which output is it?, 900 more-prompts items (accuracy, 95% bootstrap CI; paired difference vs lookup)

| system | accuracy [95% CI] | vs lookup [95% CI] |
|---|---|---|
| Opus 5.5 | 0.549 [0.516, 0.580] | +0.137 [+0.098, +0.176] |
| Sonnet 5.5 | 0.514 [0.481, 0.547] | +0.102 [+0.062, +0.141] |
| Haiku 5.5 | 0.469 [0.438, 0.500] | +0.057 [+0.019, +0.092] |
| GPT-5.6-luna | 0.467 [0.434, 0.499] | +0.054 [+0.016, +0.091] |
| logit-lens lookup | 0.412 [0.381, 0.444] | |

Which output is it?, 150 original items by evidence tier

| tier | system | accuracy [95% CI] |
|---|---|---|
| wrong evidence | Opus 5.5 | 0.227 [0.160, 0.293] |
| wrong evidence | Haiku 5.5 | 0.207 [0.147, 0.273] |
| wrong evidence | lookup (no model) | 0.260 [0.193, 0.333] |
| static (the benchmark) | Opus 5.5 | 0.447 [0.367, 0.527] |
| static (the benchmark) | Sonnet 5.5 | 0.420 [0.340, 0.493] |
| static (the benchmark) | Haiku 5.5 | 0.480 [0.400, 0.560] |
| static (the benchmark) | lookup (no model) | 0.407 [0.327, 0.487] |
| static (the benchmark) | humans (20 items x 2) | 0.325 [0.150, 0.500] |
| + per-token trace | Opus 5.5 | 0.747 [0.680, 0.813] |
| + per-token trace | Haiku 5.5 | 0.587 [0.507, 0.667] |
| + per-token trace | mean lens_z (no model) | 0.820 [0.760, 0.880] |
| + measured sweep words | Sonnet 5.5 | 0.713 [0.640, 0.787] |
| + measured sweep words | Haiku 5.5 | 0.633 [0.560, 0.707] |
| + measured sweep words | word lookup (no model) | 0.613 [0.533, 0.687] |
