# Sample eval data

What the NeuronBench data looks like, with real records from the repo. Long replies and lists are cut with `…`;
everything else is copied from the files. The [README](../README.md) explains the two tasks and the results;
[`reproduce.md`](reproduce.md) shows how each file is built.

| file | rows | contents |
|---|---|---|
| [`data/items.jsonl`](../data/items.jsonl) | 255 | the original benchmark: 150 "Which output is it?" (`choice`) + 105 "Real or null?" (`null`, 54 real) items, static evidence, with hidden answers |
| [`data/items-prompts.jsonl`](../data/items-prompts.jsonl) | 900 | more-prompts `choice` items: 100 neurons × 3 prompts per layer (L14/20/24), ten prompts |
| `data/items-{oracle,transfer,shuffled,trace,trace-shuffled}.jsonl` | 255 each | the same items rebuilt with other evidence (see [Evidence tiers](#evidence-tiers)) |
| [`data/traces.jsonl`](../data/traces.jsonl) | 150 | per-token traces of every reply in the 150 choice items, input to the `trace` tiers |
| `data/evidence/<model_id>/L<layer>/N<neuron>.json` | 1 per neuron | static evidence: `down_norm` and logit lens |
| `data/raw/L<layer>-<design>.{jsonl,units.jsonl,meta.json}` | | the gne sweeps the ground truth comes from |
| `tasks/`, `tasks-prompts-l{14,20,24}/` | 255, 3 × 300 | each item rendered as a Harbor task |

Every item has the same top-level fields:

| field | meaning |
|---|---|
| `id` | `<kind>[-<tier>]-<model_id>-L<layer>-N<neuron>[-<prompt><dose>]`; task folders write a positive dose as `p0.8`, item ids as `+0.8` |
| `kind` | `choice` or `null` |
| `evidence` | what the agent is told about the neuron |
| `payload` | the question: prompt, dose and replies (`choice`) or the sweep protocol (`null`) |
| `answer` | the hidden key: `{"letter": "A"}` or `{"real": 0 \| 1}`; never shown to the agent |
| `meta` | ground-truth details for analysis, never shown to the agent |

## 1. A "Which output is it?" item

`choice-qwen3-0.6b-instruct-L20-N1240-french+0.8` from `data/items-prompts.jsonl`. Layer 20 neuron 1240 was pushed at
dose +0.8 while the model translated a greeting; three random directions of the same length were pushed on the same
prompt to make the distractors.

```json
{
 "id": "choice-qwen3-0.6b-instruct-L20-N1240-french+0.8",
 "kind": "choice",
 "model_id": "qwen3-0.6b-instruct-00eb507314",
 "layer": 20,
 "neuron": 1240,
 "evidence": {
  "layer": 20,
  "neuron": 1240,
  "down_norm": 0.9928692579269409,
  "logit_lens": {
   "up": [" for", "for", "For", "对于", "_for", " For", "\tfor", " FOR", "而对于", "_FOR", " для", " für"],
   "down": ["]|[", "chte", "agger", "nite", "iere", "cribe", "iais", "bitrary", "habi", "achs", "herence", "vant"],
   "peak_z": 9.056496620178223
  },
  "available": ["down_norm", "logit_lens"]
 },
 "payload": {
  "prompt": "Translate 'Good morning, how are you?' into French and Spanish.",
  "dose": 0.8,
  "dose_unit": "rel",
  "baseline": "\"Bonjour, comment ça va?\"  \n\"Buenos días, ¿cómo estás?\"",
  "options": {
   "A": "Pour : \"Bonjour, comment ça pour vous?\"  \nPour : \"Para qué? ¿Cómo para usted?\"",
   "B": "Je bonjour, tu as bon posto ?",
   "C": "\"Bonjour, discoupez-vous ?\"  \n\n\"Salón, ¿dóilas ?\"",
   "D": "'Bonjour, comment estz-vous ?'  \n'Salte, cómo estás?'"
  },
  "max_tokens": 128
 },
 "answer": {"letter": "A"},
 "meta": {
  "null_pct": 0.015625,
  "mass": 9.98162249776564,
  "change": 0.3985,
  "selection": "unknown",
  "distractor_controls": [24, 56, 43],
  "option_change": {"A": 0.3985, "B": 0.5476, "C": 0.4615, "D": 0.3333}
 }
}
```

The lens promotes "for" in several languages, and only reply A is full of it in French and Spanish (`Pour`, `para`).
The answer is not the most changed reply (`option_change` A 0.40 vs B 0.55), so "pick the strangest" fails here.

- `dose`: push length as a multiple of the layer's median residual-stream norm (`rel`); negative pushes against the
  neuron.
- `meta.option_change`: each reply's distance from `baseline`. Distractors are drawn from random controls within 0.15
  of the real reply's change; `distractor_controls` are their control indices in the sweep.
- `meta.null_pct` / `mass`: the neuron's "Real or null?" statistics from its sweep (see below). Here the neuron is
  NULL by that measure, yet its effect on this prompt is easy to spot.
- `meta.selection`: `random` (random-draw neuron), `picked` (hand-picked extra, e.g. sharp logit lens) or `unknown`.

## 2. A "Real or null?" item

`null-qwen3-0.6b-instruct-L20-N944` from `data/items.jsonl` (`protocol.conditions` and `baselines` shortened):

```json
{
 "id": "null-qwen3-0.6b-instruct-L20-N944",
 "kind": "null",
 "model_id": "qwen3-0.6b-instruct-00eb507314",
 "layer": 20,
 "neuron": 944,
 "evidence": {
  "layer": 20,
  "neuron": 944,
  "down_norm": 0.8647982478141785,
  "logit_lens": {
   "up": ["更", "更强", "更有", "更为", "更大的", "更能", " more", "更快", " 更", "更大", "更高的", "更容易"],
   "down": [".twimg", "本报讯", "rics", "’n", "]],", "-</", "\r\n\n", "ingham", "aceut", "OrDefault", ".badlogic", "cimal"],
   "peak_z": 19.652788162231445
  },
  "available": ["down_norm", "logit_lens"]
 },
 "payload": {
  "protocol": {
   "model_id": "qwen3-0.6b-instruct-00eb507314",
   "layer": 20,
   "design": "main_rel",
   "conditions": [
    {"prompt": "Who are you?", "prompt_key": "who", "dose": -0.7},
    {"prompt": "Who are you?", "prompt_key": "who", "dose": 0.5},
    …
    {"prompt": "Write whatever you like.", "prompt_key": "free", "dose": 3.0}
   ],
   "dose_unit": "rel",
   "max_tokens": 128,
   "random_controls": 64,
   "decoding": "greedy"
  },
  "threshold": 0.95,
  "baselines": {
   "Who are you?": "I am a language model designed to assist with various tasks. …",
   …
  }
 },
 "answer": {"real": 1},
 "meta": {"null_pct": 1.0, "mass": 20.80717780124459, "rank": 12, "selection": "random"}
}
```

The agent sees the evidence, the protocol (three prompts × doses −0.7 / +0.5 / +0.8, plus "Write whatever you like."
at +3.0) and the unsteered replies, and writes P(REAL). It never sees the steered replies. Behind the label, from
`data/raw/L20-main_rel.jsonl`:

| prompt | dose | steered reply (start) |
|---|---|---|
| Who are you? | +0.5 | "I am a language model with **more** information. I can provide a **wider** range of information, including **more** details …" |
| Write a snake game in Python. | +0.8 | "Sure! Here's a **Simpler** Snake Game in Python with a **more straightforward** interface and less **more** complex logic. …" |
| Describe the color orange. | +0.8 | "Orange is a **broader** and **more** colorless (less vibrant) color that appears in a **wider** range of contexts. …" |

- **Vocabulary mass** (`meta.mass`): over replies with |dose| ≤ 1.6, take the words that never appear in an unsteered
  reply, score each with a Poisson z against the average unit, and sum the top five z's. N944's top words are `more`,
  `wider`, `broader`, `greater`, `straightforward`.
- `meta.null_pct`: share of the 64 random controls with lower mass. REAL (`real: 1`) when ≥ 0.95. N944 beats all 64.
- `meta.rank`: the neuron's mass rank in its layer's sweep.

A sharp logit lens is not enough. `null-qwen3-0.6b-instruct-L24-N577` has the sharpest lens of any null item
(`peak_z` 25.8, promotes `there` / `There` / `هناك`), and every positive-dose reply collapses to "There there there
there …". It is still NULL (`null_pct` 0.55): one word repeated everywhere gives one large z and four small ones,
so its mass (11.5) is ordinary.

## Evidence tiers

`neuronbench build --tier <tier>` rebuilds the same 255 items with different evidence; ids gain the tier name
(`choice-oracle-…`). Each row shows what changes for `choice-qwen3-0.6b-instruct-L14-N2602-orange-0.7`
("Describe the color orange.", dose −0.7, answer C).

| tier | file | what changes | example |
|---|---|---|---|
| static | `items.jsonl` | (default) `down_norm` + logit lens | `"up": ["，\n", ",\n", " \n", …], "peak_z": 7.71` |
| `oracle` | `items-oracle.jsonl` | adds `evidence.sweep_words`: the words this neuron's steered replies over-use (gne rank's `words`; with z-scores on null items). A positive control, not fair evidence | `"sweep_words": ["characterized", "its", "moves", "where", "which"]` |
| `transfer` | `items-transfer.jsonl` | adds `evidence.steered_elsewhere`: this neuron's steered replies on the *other* prompts at the item's dose (null items get `steered_replies` on one prompt instead). A positive control | `{"Write a snake game in Python.": "Here's a simple snake game implementation …", "Who are you?": "I am an AI assistant. …"}` |
| `shuffled` | `items-shuffled.jsonl` | shows the static evidence of a different neuron from the same layer (negative control) | `"up": [" ...\"\n\n", "気づ", "موضوع", …], "peak_z": 4.83` |
| `trace` | `items-trace.jsonl` | keeps the static evidence and adds `payload.trace` to choice items: a per-token table under the unsteered reply and each option | see below |
| `trace-shuffled` | `items-trace-shuffled.jsonl` | `shuffled` with the donor neuron's `lens_z` in the table (negative control) | |

The trace tier's table for reply C, as the agent sees it in `instruction.md` (first 12 tokens):

```text
token            base_lp  base_top         lens_z
"The"              -5.00  "Orange"           +1.3
" color"           -0.01                     +0.1
" orange"          -1.09  " **"              -0.4
" is"              -0.02                     +1.8
" a"               -0.07                     +0.1
" color"           -6.43  " vibrant"         +0.1
" in"              -3.34  " that"            +0.4
" the"             -0.04                     +0.3
" spectrum"        -0.80                     +0.9
" of"              -0.09                     -0.2
" the"             -0.40                     +0.3
" visible"         -0.47                     -0.9
```

`base_lp` is the token's log-probability under the unsteered model, `base_top` the unsteered model's top token where
it differs, and `lens_z` this neuron's logit-lens z-score for the token. Averaging `lens_z` per reply gives
A +0.32, B +0.12, **C +0.05**, D +0.42; the dose is negative, so the lowest mean (C) is the steered reply. That
one-line average is right on 82% of choice items, more than any agent scored on this tier.

`data/traces.jsonl` holds the inputs to this tier, one row per choice item: `replies.{baseline,A,B,C,D}` with
`text`, token `ids`, `tok`, `base_lp`, `base_top` and `lens_z`, plus the `donor` neuron used by `trace-shuffled`.

## Raw sweeps

`data/raw/L20-main_rel.jsonl` is gne's sweep output, one reply per row. `kind` is `baseline` (no push), `neuron`
or `random` (a control, numbered by `neuron`); `add` is the push length in residual units (`rel_push` × the
layer's median residual norm `resid_p50` in `.meta.json`):

```json
{"model_id": "qwen3-0.6b-instruct-00eb507314", "layer": 20, "kind": "neuron", "neuron": 944, "ref_neuron": 944, "prompt": "who", "dose": 0.5, "dose_unit": "rel", "rel_push": 0.5, "add": 111.61106043342893, "text": "I am a language model with more information. I can provide a wider range of information, including m…", "finish": "eog", "n_gen": 37, "seed": 0, "batch": ["who", "snake", "orange"]}
{"model_id": "qwen3-0.6b-instruct-00eb507314", "layer": 20, "kind": "random", "neuron": 0, "ref_neuron": null, "prompt": "who", "dose": -0.7, "dose_unit": "rel", "rel_push": 0.7000000079043841, "add": null, "text": "I am an AI assistant, and I don't have a name. However, I can assist you with a wide range of tasks …", "finish": "length", "n_gen": 128, "seed": 0, "batch": ["who", "snake", "orange"]}
```

`L20-main_rel.units.jsonl` has one row per unit with `gne rank`'s result: `mass`, `null_pct`, and `words` as
`[word, replies containing it, z]` (truncated):

```json
{"kind": "neuron", "neuron": 944, "layer": 20, "mass": 20.80717780124459, "null_pct": 1.0, "words": [["more", 6, 5.493], ["wider", 3, 4.198], ["broader", 3, 4.166], ["greater", 3, 4.155], ["straightforward", 2, 2.795], ["simpler", 2, 2.795], …], …}
```

`L20-main_rel.meta.json` records the design: `pairs` (prompt, dose), `prompts`, `resid_p50`, `max_tokens`,
`random_controls` (64), `seed` and the tokenized `prompt_ids`.

## Harbor task folder

Each item becomes one folder, e.g. `tasks/choice-qwen3-0.6b-instruct-L14-N2602-orange-0.7/`:

```
instruction.md        what the agent reads: the setup, prompt, replies (or protocol) and the evidence JSON
task.toml             metadata, 600 s agent limit, network allowlist, separate verifier container
environment/Dockerfile
solution/solve.sh     oracle solution (writes the key)
tests/answer.json     the key, e.g. {"kind": "choice", "letter": "C"} or {"kind": "null", "real": 1}
tests/grade.py        reads /app/answer.txt: accuracy for choice, 1 − Brier for null
tests/test.sh
```

The agent writes one letter (`choice`) or one probability (`null`) to `/app/answer.txt`; nothing else is graded.
