# Raw gne sweep: Qwen3-0.6B (Q8_0), layer 14

Produced on an M3 Max with gguf-neuron-explorer 0.4.0 (llama-cpp-python 0.3.36, Metal):

    gne verify                      # 12/12 checks passed
    gne stats resid
    gne lens logit --layer 14
    gne sweep --layer 14            # 384 neurons + 64 random controls, design main_rel, 4484 rollouts
    gne rank --run L14-main_rel

| File | What it is |
|---|---|
| `L14-main_rel.jsonl` | Every rollout (4 baselines + 448 units x 10 conditions). **Slimmed**: the per-token arrays (`token_ids`, `logprob`, `top_ids`, `top_lps`) are removed to bring it from 80 MB to about 3 MB. All other fields are as gne wrote them. |
| `L14-main_rel.meta.json` | Sweep design, prompts, dose unit, median residual norm. Unmodified. |
| `L14-main_rel.units.jsonl` | `gne rank` output: vocabulary mass and `null_pct` per unit. Unmodified. |

model_id: `qwen3-0.6b-instruct-00eb507314`. `data/raw/` is gitignored on the code branches, so these files are
force-added on this data branch only.

Per-neuron evidence for the same 384 neurons is in `data/evidence/<model_id>/L14/N<neuron>.json`, written by
`scripts/export_evidence.py` at commit ee8ef6a. Each file holds `down_norm` and `logit_lens` only: `gne stats act` was
not run, so there are no activation statistics, and nothing measured from pushing the neuron is included.
