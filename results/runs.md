# Valkyrie runs behind `results/`

Agent `mini_swe_agent`, sandboxes on Modal, concurrency 8. Exports (`valkyrie run results <id> --path ...`) are in
`jobs/valkyrie/`. Valkyrie's own summary score is not meaningful for these runs (it averages `choice_acc` and
`null_brier` over all trials); use `neuronbench report`.

Static tier: datasets `neuronbench/l14-l20@1` (layers 14 and 20, 170 tasks) and `neuronbench/l24@1` (layer 24, 85 tasks).

| model | `l14-l20@1` | `l24@1` |
|---|---|---|
| anthropic/claude-haiku-5-5 | `5dd195b6-7266-438f-a727-d6ac977d94b2` | `5a71463e-5199-41a6-a54a-23d3fff7595a` |
| anthropic/claude-sonnet-5-5 | `8ceb64b0-2f28-4ca3-9ee5-7345b5dcfc49` | `4fe2a846-1f11-4e7b-8afa-7b1dfc1bdea9` |
| openai/gpt-5.6-luna | `ed60a1ae-99a9-4214-a10b-df38cbff5dfb` | `a535e3ba-2e81-4494-a5b3-be3256774992` |
| anthropic/claude-haiku-4-5 | `89db445d-8a72-409e-88ca-092cd2118f0c` | `a99707ce-0e94-40cd-82f0-8d919b497fae` |
| anthropic/claude-opus-5-5 (concurrency 16) | `9cf322f4-9169-4c15-a97f-eb8546e34c84` | `8483ee1e-1d92-481b-9cc6-42712e85214e` |

Self-hosted Qwen3 (`--model hosted_vllm/<HF id>`, served by `modal/serve_vllm.py`: Qwen3-32B on H200, Qwen3-0.6B on L4;
concurrency 32). Datasets `neuronbench/{l14-l20,l24}@3`: the same tasks with the Modal vLLM hosts in `allowed_hosts`.

| model | `l14-l20@3` | `l24@3` |
|---|---|---|
| hosted_vllm/Qwen/Qwen3-32B | `194565fb-b3bd-4dfd-95af-823d37a259b6` | `6d424a5f-4f5c-489c-b595-0731e13dd92d` |
| hosted_vllm/Qwen/Qwen3-0.6B | `5d1dd7d4-97c7-4d13-9543-43c9c95df076` | `c57c04c5-6270-43d5-9d62-825a47d0f5e4` |

Ceiling tiers (`neuronbench build --tier {oracle,transfer}`, datasets `neuronbench/{l14-l20,l24}-{oracle,transfer}@1`):

| model | tier | `l14-l20` | `l24` |
|---|---|---|---|
| anthropic/claude-haiku-5-5 | oracle | `7b0d5db8-672b-4630-be60-417f3ca48ec0` | `2d588c84-a1ec-4c56-8297-a5892962806a` |
| anthropic/claude-haiku-5-5 | transfer | `d20eee82-ab29-4f74-990f-9ef5b81f5e89` | `43f31f60-4a9e-4fda-8838-1f7bb1df1919` |
| anthropic/claude-sonnet-5-5 | oracle | `022891c7-f330-4de5-9abb-d734b598b78e` | `e817115f-b91c-4cce-b5e3-77040b71b184` |

Wrong-evidence control (`neuronbench build --tier shuffled`, datasets `neuronbench/{l14-l20,l24}-shuffled@1`; each item shows another same-layer neuron's static evidence):

| model | tier | `l14-l20` | `l24` |
|---|---|---|---|
| anthropic/claude-haiku-5-5 | shuffled | `34cab3e0-8db6-4b44-992e-97dfba0d653a` | `16c9d368-0062-483b-9c3b-551aa3a3e69e` |
| anthropic/claude-opus-5-5 | shuffled | `5b7edca6-1c42-470f-8f76-043eac5029e5` | `bdcd0f8c-0a82-4f2e-b8fa-504bebd59baf` |

More prompts (choice only, `data/items-prompts.jsonl`: 900 items, 100 neurons x 3 prompts per layer over ten
extra prompts; see README "More prompts"). Push each layer's tasks as its own dataset and run with the same settings
as the static tier:

```bash
for L in 14 20 24; do valkyrie dataset push neuronbench/l$L-prompts ./tasks-prompts-l$L --tag v1 < /dev/null; done
for M in haiku-5-5 opus-5-5; do for L in 14 20 24; do
  valkyrie run start --agent mini_swe_agent --dataset neuronbench/l$L-prompts@v1 --model anthropic/claude-$M \
      --provider modal -s ANTHROPIC_API_KEY anthropic-api-key --concurrency 8 --label l$L-prompts-$M
done; done
valkyrie run results <run-id> --path jobs/valkyrie/l<L>-prompts-<model>.json   # then git add -f
```

Sonnet 5.5 and GPT-5.6-luna ran with the same settings (`--model anthropic/claude-sonnet-5-5`, and
`--model openai/gpt-5.6-luna -s OPENAI_API_KEY openai-api-key`; labels `l$L-prompts-sonnet-5-5` /
`l$L-prompts-gpt-5.6-luna`). Opus 5.5's `l20-prompts` run had one Modal sandbox error
(`L20-N1035-sqlp0.8`), retried in the same run with `valkyrie run retry`.

| model | `l14-prompts@v1` | `l20-prompts@v1` | `l24-prompts@v1` |
|---|---|---|---|
| anthropic/claude-haiku-5-5 | `1666594a-650e-4636-8edd-239baf34bf9d` | `9d295aae-f33a-4ce2-aa7b-5d4b0dcf0b7e` | `8021112a-4485-42d0-8d86-c73d0a2843bb` |
| anthropic/claude-sonnet-5-5 | `88947c86-5dbd-463a-9c41-44ee48d59a7d` | `07aaba18-1b60-436f-9d23-c34f2d338bb9` | `aa27fb10-9765-47ae-877d-df07111c3e25` |
| anthropic/claude-opus-5-5 | `cc45c554-65a0-46b0-b2b3-852974ae3044` | `f35b3adf-a9de-4f6f-8598-9eec59207a39` | `79c16a90-1b37-425e-a8ef-b627096ebb00` |
| openai/gpt-5.6-luna | `b59407f2-d359-4868-a519-27270b1cdea1` | `cf6ca8d2-0072-41b4-a325-952db66d40e5` | `f477b3e0-06e4-4681-8d55-1540c2594e1b` |
