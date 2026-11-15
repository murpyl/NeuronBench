# Which reply did this neuron cause?

You are studying MLP neuron 3049 in layer 24 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 24's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
("rel" units). The model is qwen3-0.6b-instruct-00eb507314, run with greedy decoding (temperature 0), replies capped at
128 tokens. As a rough guide from a similar model: a dose of 0.5 slips a topic in, 0.8 takes the reply
over, 1.0 and above starts to break the text, and 3.0 deliberately breaks it. A negative dose pushes the opposite
way.

For **one** of the four replies below, the vector was this neuron's output direction (its column of W_down) at dose
+0.8. For each of the other three, it was a **random direction of exactly the same length**, added at the
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
The main causes of World War I were a complex set of factors that led to the formation of a global war. These factors included:

1. **TIP (Treaties of International Public Interest)**: These were agreements designed to preserve international peace and prevent potential conflicts. However, they were not effective in preventing the formation of a war.

2. **Distrust and Ignored Dissent**: The field of mathematics and physical science was not recognized as important, which led to a lack of intellectual and intellectual property property. This set the stage for intellectual property disputes.

3. **Distrust and Ignored Dissent**: The
```

### Reply B

```text
The primary causes of World War I include:

1. **Oceighthistians' Ointments**: Oighthistians, a British nationalist group, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians, led by William Oighthistians
```

### Reply C

```text
World War I was caused by a combination of factors, including the following:

1. **Internal and External Causes**:
   - **Internal Causes**: The internal divisions and tensions within the countries and the countries’ responses to the causes of the war, such as the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the causes of the war and the responses to the
```

### Reply D

```text
World War I, which pended on the pinc-ty of emt-ty, was primarily attributed to several of the above-mentioned, which together cul-li-�-y, p-ek-ty, and p-ek-ty, p-ek-ty, and p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-ek-ty, p-
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
 "layer": 24,
 "neuron": 3049,
 "down_norm": 1.0954852104187012,
 "logit_lens": {
  "up": [
   "(sol",
   "лад",
   " Linux",
   "Sol",
   "_sol",
   "umps",
   "leans",
   "Fac",
   "LCD",
   "诀",
   "obe",
   "ient"
  ],
  "down": [
   "athlete",
   " comprom",
   "FetchRequest",
   "CAR",
   " fatigue",
   "carbon",
   "apest",
   " capitals",
   "athlon",
   "我家",
   " allot",
   "堃"
  ],
  "peak_z": 4.566792011260986
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
