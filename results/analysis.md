# NeuronBench v1: what the results say

Qwen3-0.6B, layers 14/20/24, 255 tasks, four models as mini-SWE-agent on Valkyrie, 0 agent failures.
Numbers come from `scripts/analyze_results.py` (`results/analysis.txt`) and from reading the 1020 agent trajectories.

## Headline results

1. **Only Haiku 5.5 clearly beats the best agent-free shortcut on "Which output is it?".** The strongest text-only
   heuristic (`scripts/ceiling_baselines.py`: pick the reply containing the lens tokens the dose actually pushes, with
   fuzzy matching) scores 41% [34, 49]; the plain logit-lens baseline 30%; chance 25%. Models: Haiku 5.5 48% > Sonnet
   5.5 42% > GPT-5.6-luna 39% = Haiku 4.5 39%. Three of the four are at the shortcut's level, and not in size order.
2. **Most of that skill is reading the neuron's vocabulary off the text.** In 50 of 150 items a logit-lens token
   (≥3 letters) literally occurs in one of the candidate replies. On those items models score 52–62%; on the other
   100 they score 32–41%. A trivial "pick the reply containing a lens token" baseline gets 35%. Beyond token
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

- Report the two halves of the choice task separately (lens token present in a reply / absent); the absent half is
  the real test of mechanistic prediction and no model is above 41% on it.
- Add evidence that *does* bear on effect size (activation statistics from `gne stats act`, `down_norm` relative to the
  layer) so that "Real or null?" is answerable in principle; today it mostly measures calibration.
- More prompts: three prompts × three doses means models see the same baseline replies hundreds of times.
