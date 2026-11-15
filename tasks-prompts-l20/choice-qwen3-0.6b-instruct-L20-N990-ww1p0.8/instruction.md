# Which reply did this neuron cause?

You are studying MLP neuron 990 in layer 20 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 20's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
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
The most significant and widely studied causes of the **Western European and Northern Hemisphere countries' aggressive and violent responses to the formation of the United States and the development of the social sciences, particularly the scientific method, have long years of scientific and social research and have been widely studied and analyzed through various methods and theories. The most important and most widely accepted scientific and social theories are the scientific method and the social psychological theories of the human mind and behavior. These theories have been widely used and have a long period of scientific and social research and have a long period of time of scientific a [...]
```

### Reply B

```text
The main causes of World War – the **World-Wearing** or **World-Win** – **The World-Win**** (the **World-Win**** or **The World-Win****) **The World-Win**** (the **World-Win**** or **The World-Win****) **The World-Win**** (the **World-Win**** or **The World-Win****) **The World-Win**** (the **World-Win**** or **The World-Win****) **The World-Win**** (the **World-W
```

### Reply C

```text
The main causes of World War I are a complex and often debated issue, but the most commonly cited factors include:

1. **A. The Formation of the United Nations (1918):** The idea of a global peacekeeping organization was proposed by the United Nations to prevent the repetition of the conflict.

2. **B. The Formation of the United Nations (1918):** The idea of a global peacekeeping organization was proposed by the United Nations to prevent the repetition of the conflict.

3. **C. The Formation of the United Nations (1918):** The idea of a global peacekeeping
```

### Reply D

```text
Today now today now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now now
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
 "layer": 20,
 "neuron": 990,
 "down_norm": 0.7592177391052246,
 "logit_lens": {
  "up": [
   " today",
   " now",
   "now",
   "如今",
   "现在",
   " nowadays",
   " currently",
   "today",
   "今天",
   "现在的",
   " presently",
   " hoje"
  ],
  "down": [
   "achel",
   "атель",
   "��",
   "antt",
   "alter",
   "lington",
   "variants",
   "uir",
   "**)&",
   ":numel",
   "оборот",
   "CELER"
  ],
  "peak_z": 15.983704566955566
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
