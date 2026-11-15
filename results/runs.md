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

Ceiling tiers (`neuronbench build --tier {oracle,transfer}`, datasets `neuronbench/{l14-l20,l24}-{oracle,transfer}@1`):

| model | tier | `l14-l20` | `l24` |
|---|---|---|---|
| anthropic/claude-haiku-5-5 | oracle | `7b0d5db8-672b-4630-be60-417f3ca48ec0` | `2d588c84-a1ec-4c56-8297-a5892962806a` |
| anthropic/claude-haiku-5-5 | transfer | `d20eee82-ab29-4f74-990f-9ef5b81f5e89` | `43f31f60-4a9e-4fda-8838-1f7bb1df1919` |
| anthropic/claude-sonnet-5-5 | oracle | `022891c7-f330-4de5-9abb-d734b598b78e` | `e817115f-b91c-4cce-b5e3-77040b71b184` |
