# Which reply did this neuron cause?

You are studying MLP neuron 2310 in layer 20 of a small language model.

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
The main causes of World War I (the "Treaty of Paris") are primarily located in the **imperialism, the duel of the fortresses, and the process of the war ending through the process of the war ending through the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process of the process
```

### Reply B

```text
The main causes of World War I are a combination of several key factors, including:

1. **A Sense of Crisis and Loss of Confidence**: The failure of the Ottoman Empire at the Treaty of Avarot (19th) and the failure of the Central Treaty of Vienna (1856) had come from a lack of cooperation and a lack of a central authority. This led a sense of frustration and loss of confidence from the population at the time.

2. **A Sense of Crisis and Loss of Confidence**: The failure of the Ottoman Empire at the Treaty of Avarot (19th) and the failure of
```

### Reply C

```text
World War I was caused by a combination of major events and events that created a global crisis. The primary causes include:

1. **The Creation of The Factories in The United Industrial Countries** - The industrialization of the world, with the development of new technologies and the growth of industrial nations, created a powerful global industrial base.

2. **The Formation of The United Industrial Countries** - The industrialization of the world, with the development of new technologies and the growth of industrial nations, created a powerful global industrial base.

3. **The Creation of The Factories in The United Industrial Countries** - The industrialization of the world
```

### Reply D

```text
The main causes of World War I (2nd and 3rd) are a complex and comprehensive issue, and a detailed and accurate answer would include the following:

### **Main Causes of World War I (2nd and 3rd)**:
1. **Commutation of the Peace of Paris (28th, 3rd) and the Peace of Aissement (29th, 3rd) **:
   - The main part of the issue was the **Commutation of the Peace of Paris** (28th, 3rd) and the **Commutation of the Peace of Aissement** (
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
 "neuron": 2310,
 "down_norm": 0.9112287759780884,
 "logit_lens": {
  "up": [
   "缺",
   "loo",
   "amples",
   "ье",
   "珥",
   "锻",
   "ippet",
   " bath",
   "IAL",
   "alles",
   " Population",
   " Sense"
  ],
  "down": [
   " toward",
   "past",
   " towards",
   " hacia",
   " past",
   "owards",
   "过来",
   " forward",
   "Past",
   " FORWARD",
   "around",
   "-around"
  ],
  "peak_z": 6.481489658355713
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
