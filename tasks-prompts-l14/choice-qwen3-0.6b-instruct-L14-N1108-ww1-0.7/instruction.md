# Which reply did this neuron cause?

You are studying MLP neuron 1108 in layer 14 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 14's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
("rel" units). The model is qwen3-0.6b-instruct-00eb507314, run with greedy decoding (temperature 0), replies capped at
128 tokens. As a rough guide from a similar model: a dose of 0.5 slips a topic in, 0.8 takes the reply
over, 1.0 and above starts to break the text, and 3.0 deliberately breaks it. A negative dose pushes the opposite
way.

For **one** of the four replies below, the vector was this neuron's output direction (its column of W_down) at dose
-0.7. For each of the other three, it was a **random direction of exactly the same length**, added at the
same layer on the same prompt. Your job is to work out which reply this specific neuron produced, using what the
evidence says the neuron writes. All four replies are perturbed by similar amounts, so "the strangest reply" is not
a reliable answer.

## Prompt

```text
What were the main causes of World War I?
```

## Reply with no intervention

```text
World War I was primarily caused by a combination of complex factors, including:

1. **Tensions between European powers**: The competition for dominance in Europe, especially after the assassination of Archduke Franz Ferdinand of Austria, led to a series of alliances and rivalries.

2. **The assassination of Archduke Franz Ferdinand**: The assassination of Franz Ferdinand in 1914 by a Serbian nationalist, including the assassination of his wife, Serbia, triggered a chain reaction of alliances.

3. **Alliance systems**: The formation of alliances between major European powers (e.g., Britain, France, Russia, Germany, Italy, and
```

## Candidate replies

### Reply A

```text
World War I was a complex and devastating war, with the main causes of it being a combination of several factors, though the primary reasons were not entirely determined by any single cause. The following key points from historical analysis, though not entirely consistent with the same cause, reflect the broader context of the war:

**Key Factors in the War, as previously determined:**

While the war was not a single cause, the following factors contributed to it, though the same factors were not entirely determined by any single cause:

- **The war was not a single cause of the war, with the same factors being more complex and the same cause of the
```

### Reply B

```text
World War I was the first major war in history, with its outcome determined by the complex web of international events, scientific advancements, and political decisions. It also had a lasting impact on the future of the world, including the establishment of the League of Nations and the creation of new institutions and organizations.

The main causes of the war were a combination of the end of the war, the end of the war, and the end of the war, with the end of the war being the most significant in the long-term. It also had a lasting impact on the world, including the creation of new institutions and organizations, and the end of the
```

### Reply C

```text
World War I was primarily a **preventable conflict** that could have been avoided through diplomacy, mediation, and international understanding, rather than through the means of **escalation and diplomacy**. This would have prevented the war from occurring in the first place, and it is recommended to avoid conflicts in the first place by promoting **non-aggression, conciliation, and mediation** to prevent the need for the war.

If possible, the following measures could have been taken to avoid the war:

- **Alliance-building** through negotiation and mediation.
- **Avoiding** conflicts through dialogue and mediation.
- **Peace talks** to reduce the
```

### Reply D

```text
World War I is typically considered the **first world war**, and its causes are rooted in a combination of **scientific, social, and political factors** to determine the primary cause.

### 1. **Scientific Cause**  
   - **Geographic and geographical factors**: The **geographical and geographical causes** are the key to determining the war's origin. This is a **scientific cause** because it is based on the **scientific method**.

### 2. **Social cause**  
   - **Social causes** are the scientific causes. This is a **scientific cause**. Let me know if you want to know the
```

## Evidence about the neuron

Fields of the evidence JSON (all computed from the weights or from unsteered activations; nothing in it
comes from pushing this neuron):
- `down_norm`: length of the neuron's output weight vector (column of W_down).
- `logit_lens.up` / `logit_lens.down`: tokens whose unembedding has the largest / smallest dot product with the
  neuron's output direction, i.e. what the neuron would promote / suppress if its output went straight to the
  logits. `peak_z` is the largest |z-score| of those dot products across the vocabulary.
- `activation` (if present): statistics of the neuron's activation over a text corpus without intervention
  (`absmax`, `q999`, `q99`, `rms`, `mean`).
- `directions` (if present): cosine between the neuron's output direction and named residual-stream directions
  (for example a persona direction), with the neuron's rank in its layer by |cos|.

```json
{
 "layer": 14,
 "neuron": 1108,
 "down_norm": 0.974896252155304,
 "logit_lens": {
  "up": [
   "ATEST",
   "oted",
   "字母",
   "acie",
   "ked",
   "úb",
   "cies",
   "etailed",
   "ASTE",
   "ció",
   "EFR",
   "pecific"
  ],
  "down": [
   "减轻",
   "预防",
   "化解",
   "减少",
   "解決",
   "避免",
   "原本",
   "削减",
   "友好",
   "эконом",
   "前世",
   "outil"
  ],
  "peak_z": 5.541749000549316
 },
 "available": [
  "down_norm",
  "logit_lens"
 ]
}
```

## Answer

Write exactly one letter, A, B, C or D, to `/app/answer.txt` (for example `echo B > /app/answer.txt`).
Nothing else is graded.
