# NeuronBench v1: what the results say

Qwen3-0.6B, layers 14/20/24, 255 tasks, four models as mini-SWE-agent on Valkyrie, 0 agent failures. Opus 5.5 and
the self-hosted Qwen3 models were added later; see the last section.
Numbers come from `scripts/analyze_results.py` (`results/analysis.txt`) and from reading the 1020 agent trajectories.

## Headline results

1. **No model clearly beats a word lookup on "Which output is it?"** 39–48% vs 25% chance and 41% [33, 49] for a
   dose-sign-aware logit-lens lookup (pick the reply that gained the most "up" tokens for a positive dose, "down"
   tokens for a negative one). Order: Haiku 5.5 (48%) > Sonnet 5.5 (42%) > lookup (41%) > GPT-5.6-luna (39%) =
   Haiku 4.5 (39%). Haiku 5.5 vs the lookup, paired over items: +7 points [−3, +18]. Not ordered by model size or price. Stronger automatic variants (`scripts/ceiling_baselines.py`:
   fuzzy subword, script, cross-validated learned scorer) top out at 41%.
2. **Most of that skill is reading the neuron's vocabulary off the text.** In 50 of 150 items a logit-lens token
   (≥3 letters) literally occurs in one of the candidate replies. On those items models score 52–62%; on the other
   100 they score 32–41%. The lookup gets 64% and 29% on the same two subsets. Yet models pick the same reply as the
   lookup on only 31–35% of items and solve only 51–52% of the 61 items it gets right, so they apply the evidence
   inconsistently rather than as a superset of the lookup ("model or lookup right": 59–67%). Beyond token
   matching, the only other thing that helps is a large effect: replies that moved ≥0.8 from the unsteered one are
   solved 51–67%, replies that moved less 31–40%.
3. **Nobody can tell which neurons matter.** On "Real or null?" discrimination is at chance for all four
   (AUC 0.52–0.57). The Brier differences (0.247–0.308) are calibration, not knowledge: replacing each model's
   answers with its own mean probability changes its Brier by ≤0.03. All four set their probability by the
   logit-lens peak z-score (Spearman 0.60–0.76 with peak_z), but peak_z barely predicts the sweep outcome
   (Spearman 0.13). Sonnet 5.5 "wins" by hedging 0.4–0.6; Haiku 4.5 and GPT-5.6-luna lose by saying 0.7–0.9 for
   neurons that were real 51% of the time.
4. **More deliberation did not help.** Haiku 4.5 used a median of 6 API calls per task ($10.48 for the run) and
   tied for last; Haiku 5.5 answered 70% of tasks in ≤2 calls, with no tool use ($0.27 for the run) and came first.
   Sonnet 5.5 shows no reasoning at all in its transcripts (ls, write the letter, submit).
5. **The models mostly make different mistakes.** Pairwise agreement is 39–65%; 44 items were missed by all four and
   27 solved by all four. A plurality vote across the four (40%; ties count as wrong) is worse than the best single model.
6. **Where it is easier:** layer 24 (46–52%) over layers 14/20 (34–48%); "Describe the color orange" (46–54%) over the
   other two prompts (33–46%); neurons that are actually real (56–62% for three of the models) over null neurons
   (34–45%), i.e. a random-direction-sized push on a neuron that *does* something is easier to recognise.

## Ceiling controls: is it the evidence or the task?

Same 255 items, same candidates and grader; only the evidence block changes (`neuronbench build --tier`, README
"Ceiling controls"). Haiku 5.5, paired with its static run:

| tier | choice | null Brier / AUC | choice lookup | null lookup Brier |
|---|---|---|---|---|
| static | 0.48 [0.41, 0.56] | 0.255 / 0.56 | 0.41 | 0.255 |
| transfer (its steered replies on other prompts) | 0.48 [0.40, 0.56] | 0.240 / 0.69 | 0.47 | 0.249 |
| oracle (its measured over-used words, z-scores on null) | 0.63 [0.55, 0.71] | 0.210 / 0.78 | 0.61 | 0.089 |
| oracle, Sonnet 5.5 (its static: 0.42, 0.247 / 0.57) | 0.71 [0.64, 0.79] | 0.189 / 0.83 | 0.61 | 0.089 |

Oracle − static on choice: Haiku 5.5 +0.15 [+0.05, +0.25], Sonnet 5.5 +0.29 [+0.19, +0.39]. Sonnet was run
because Haiku's oracle score was under 85%.

The oracle came in under 80%, so we diagnosed it. We split the 150 choice items by what the oracle words say
about the candidates. "Gain" is how many more times a reply uses those words than the unsteered reply does:

| oracle words vs the candidates | n | Haiku 5.5 oracle | Sonnet 5.5 oracle | Haiku 5.5 static |
|---|---|---|---|---|
| true reply gains the most | 82 | **0.87** | **0.93** | 0.50 |
| true reply tied for most | 18 | 0.56 | 0.61 | 0.39 |
| a distractor gains more | 19 | 0.37 | 0.47 | 0.47 |
| true reply gains none | 31 | 0.23 | 0.35 | 0.48 |

- **Instructions and format are sound.** When the evidence is decisive the models are right 87% (Haiku) and 93% (Sonnet) of
  the time. They follow the evidence even when it misleads (0.23 / 0.35 where the true reply has none of the words).
- **The ceiling is set by evidence specificity, not clipping.** Only 2 of 150 true replies are clipped, and none of the
  31 "gains none" replies contains a sweep word even unclipped. `sweep_words` is pooled over every prompt and
  dose, and on a single prompt/dose a neuron's push often doesn't produce its signature words (L14 N2602 at −0.7
  on "orange": sweep words *characterized, its, moves, where, which*; its reply is a garbled wavelength list).
  Shared vocabulary matters too: in 107 items a distractor also gains some of the words, often generic ones like
  *which, are, its*.
- **Transfer vs static** asks whether watching the neuron act on other prompts beats reading its weights. On choice it
  doesn't (+0.00 [−0.08, +0.08]; the word-transfer lookup 0.47 vs logit-lens lookup 0.41). On null it does raise
  AUC (0.56 → 0.69): seeing behaviour tells you *whether* a neuron matters, more than *what* it will say on a new prompt.
- **On null, even decisive evidence is under-used.** A one-feature logistic regression on the oracle z-scores gets Brier 0.089;
  Haiku 5.5 gets 0.210 and Sonnet 5.5 0.189 (AUC 0.78 / 0.83). So the static-tier null result (AUC ≈ 0.55) is mostly missing evidence, and partly the model.

So the 39–48% static scores are not a broken task: a model handed decisive evidence uses it, and the static evidence
(logit lens + down-norm) usually isn't decisive.

## Failure modes on "Which output is it?"

Tagged by regex over the assistant text of all 150 choice trajectories per model (Sonnet 5.5 exposes none).
Wrong-rate = share of those trajectories answered wrong; the overall wrong-rates are 61/61/52% (GPT/H4.5/H5.5).

| mode | what it looks like | GPT | Haiku 4.5 | Haiku 5.5 |
|---|---|---|---|---|
| **Oddest reply** | "random directions usually cause only mild drift, so the reply that departs most from the baseline is the neuron" (Haiku 5.5). The task text says this is unreliable, and the distractors are matched on change, so it is chance: every model picks the most-changed candidate 28–34% of the time (truth: 25%), and is no more accurate when it does. | 9 (78% wrong) | 23 (70%) | 14 (57%) |
| **Dose folklore** | Over-reading the one-line dose guide: "+0.5 should be a subtle slip, so pick the gentlest reply", "C is too broken for −0.7". Picking the least-changed reply for a small dose is the single worst habit. | 2 (100%) | 36 (81%) | 13 (77%) |
| **Trait invention** | Turning a vocabulary list into a personality: "this neuron normally helps the model escape loops", "a teamwork/support neuron", "promotes formal, structured content". The logit lens says which tokens the direction writes, not what the network does with them. See `failure_trace_L14-N710.md`. | 2 | 36 (69%) | 1 |
| **Sign stories** | Correct premise (negative dose promotes the *down* tokens) followed by a semantic reading of token fragments ("`onium`, `技术和` are technical, so suppress technical content"). Common and only mildly worse than average, because the premise is right. | 42 (48%) | 88 (65%) | 30 (57%) |
| **Subword matching** | Counting suffixes: "Reply A contains many repetitions of the promoted patterns `e`, `s`, `-ing`" (GPT). Fragments that occur in every reply carry no signal. | few, GPT-specific | | |
| **Declared guess** | "I can't run the model here, so this is a judgment call" then falls back to Oddest reply. Honest, and 65% wrong. | 0 | 3 | 54 (65%) |

What works, when it works: a lens token with real content (`Pythran`, `mollusk`, `management`, `but`) shows up in
one reply and nowhere else. The models find that reliably; the benchmark's hard half is the 100 items where it doesn't
happen.

## Failure modes on "Real or null?"

- **Sharpness ≠ causal effect.** "Such a high z-score would virtually never occur in a random direction by chance"
  (Haiku 4.5, N2715, 0.88). A sharp logit lens means the direction points at specific tokens; it says nothing about
  whether adding it to the residual stream moves the output more than a random vector of the same length. Every
  model used it as the main signal; it has Spearman 0.13 with the truth.
- **Coherent token family ⇒ real.** "Its top promoted tokens are a coherent family of contrastive 'but' tokens, not an
  arbitrary collection, so a causal effect is more likely" (GPT, N2135 → 0.80; the neuron beat 19% of controls).
- **Anchoring on the stated base rate and hedging.** Sonnet 5.5 answered 0.4–0.6 on 103 of 105 items; Haiku 5.5 answered
  0.6 on 74 of 105. That is the loss-minimising move when you have no signal, and it is what a base-rate baseline does.
- **Overconfidence.** Haiku 4.5 (mean 0.71) and GPT-5.6-luna (0.67) write "REAL" for most neurons; 49% were null.

## Implications for v2

- Report the oracle tier next to the static one, and build a condition-specific oracle (words for the item's prompt
  and dose sign) for a tighter ceiling.
- Add static evidence that bears on effect size (activation statistics from `gne stats act`, `down_norm` relative to
  the layer); today "Real or null?" mostly measures calibration.
- More prompts: three prompts × three doses means models see the same unsteered replies hundreds of times.

## Added later: Opus 5.5 and open-weight Qwen3

Same 255 tasks and agent. Opus 5.5 ran through the Anthropic API; Qwen3-32B and Qwen3-0.6B ran on vLLM endpoints on
Modal (`modal/serve_vllm.py`, run IDs in `runs.md`). Numbers are in `analysis.txt`.

- **Opus 5.5** is second on choice (45% [37, 53]; 56% with a lens token in a reply, 39% without, 37% where the lookup
  is wrong) and the best on "Real or null?" (Brier 0.245, AUC 0.61, the highest of any model). Like the others it sets
  its probability from peak_z (Spearman 0.85) and stays near the base rate (mean 0.56), so its Brier is only 0.006
  below its own constant-mean score of 0.251.
- **Qwen3-32B** ties GPT-5.6-luna and Haiku 4.5 on choice (39% [32, 47]; 54% / 32% with and without a lens token)
  and agrees with the lookup's pick on 37% of items, the most of any model. On "Real or null?" it has no signal (AUC
  0.46, Spearman −0.08 with the truth) and says "real" almost always (mean 0.88), so its Brier is 0.392.
- **Qwen3-0.6B**, the model being steered, is at chance on its own neurons: 23% [17, 31] on choice, AUC 0.49 and
  Brier 0.385 on "Real or null?" (mean 0.82). Self-knowledge does not help.
- **Qwen3 rarely submits.** Both Qwen models write `answer.txt` within the first turns and then keep reconsidering
  and rewriting it until the 600 s agent limit, so they are graded on whatever the file holds at the cutoff. Qwen3-32B
  timed out on 139/150 choice and 8/105 null tasks, Qwen3-0.6B on 63/150 and 43/105. In 5 of 17 Qwen3-32B trajectories
  checked by hand, the final letter differed from the first one written. The Qwen scores are therefore "answer at
  the deadline", not a submitted final answer; every API-model task submitted normally.
