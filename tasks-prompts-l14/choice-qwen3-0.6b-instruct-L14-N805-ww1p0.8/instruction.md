# Which reply did this neuron cause?

You are studying MLP neuron 805 in layer 14 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 14's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
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
The World War I was a conflict that was marked by the United States of America. However, the United States was not the same as the United States of the United States. Therefore, the United States was not the same as the United States. Therefore, the United States was not the same as the United States. Therefore, the United States was not the same as the United States. Therefore, the United States was not the same as the United States. Therefore, the United States was not the same as the United States. Therefore, the United States was not the same as the United States. Therefore, the United was not the same as
```

### Reply B

```text
World War I was a devastating and tragic war that left an indelible mark on history. It was a one-world war that ended with the Treaty of Versailles and its subsequent reparat. The alliances that fell. The main causes of the war were clearly and unquestionably the Treaty of Versailles, which was a system of reparation that was a one-world war. The country of the country of the country. The country of the country. The country. The country. The country. The country. The country. The country. The country. The country. The country. The country. The country. The country. The
```

### Reply C

```text
World War I is a significant, and often cited, global conflict. The main causes include:

1. **Rivalry and Inequality** (e.g., "Great Migration" and "2000s)".
2. **Climate (e.g., "Great Floods" and "2000s)"**.
3. **Eco (e.e.)** (e.g. "2000s)".
3. **Eco (e.g.)** (e.g. "2000s)".
3. **Eco (e) ** (e.g. "2
```

### Reply D

```text
The war was a global conflict. The main causes of the conflict. The answer is the one that is correct. The user should choose the correct one. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is correct. The answer is the one that is
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
 "neuron": 805,
 "down_norm": 0.7925737500190735,
 "logit_lens": {
  "up": [
   "ISC",
   ".Provider",
   " Premier",
   ".listFiles",
   " Michaels",
   " thriller",
   "ện",
   " bang",
   "archy",
   " liệt",
   "ARS",
   "ighted"
  ],
  "down": [
   " colours",
   "颜色",
   "odo",
   "所谓的",
   " colors",
   "cid",
   " couleur",
   "gy",
   "\tcolor",
   " clearer",
   "changing",
   "Incre"
  ],
  "peak_z": 4.756722927093506
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
