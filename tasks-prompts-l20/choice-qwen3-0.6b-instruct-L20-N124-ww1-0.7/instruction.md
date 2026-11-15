# Which reply did this neuron cause?

You are studying MLP neuron 124 in layer 20 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 20's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
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
The main causes of World War I are the following:

1. **Treatments of the 1830s and 1840s**: The 1830s and 1840s were the time of the "Treat of London" (1830), which was the first of the "Treat of London" in the 19th century. This was the result of the "Treat of London" in 1830, which was the first of the "Treat of London" in the 19th century. The "Treat of
```

### Reply B

```text
The main causes of World War 1 (1911-1949) are a complex and multifacultal issue, though the main factors are rooted in the political, economic, and social conditions of the time. The main causes are:

1. **The Failure of the Peace of 1102**: In the 1875 peace between the European powers, the situation was not fully resolved, leading to a political stale in the region.

2. **The Rise of the German Nationalism**: In the 19th and 2nd parts of the century, the German people in the
```

### Reply C

```text
World War I was primarily caused by a combination of complex and varied factors, including:

1. **Distrust and Incompetacy in the Treaty of Paris**  
   The treaty, signed in 1911, was poorly executed, leading to a massive territorial and economic shift in the European sphere of war. The treaty was inconsistent with the real needs of the participating nations, leading to a deepening of national disarray.

2. **Diplomatic and Political Disarray**  
   The collapse of the German Empire and the decline of the German Confederation led to a disarray in Europe, leading to a shift in
```

### Reply D

```text
World War I was primarily caused by a combination of **alliances, imperialism, militarization, nationalism, and imperialism**. These factors led to a **conflict between the Allies (Russia, Britain, France, Germany, Italy, Spain, Portugal, and others) and the Central Powers (Germany, Austria, Russia, Serbia, etc.)**.

### Main Causes:
1. **Allies' Alliances**:
   - **Alliances of 1874**: The **All-Imperial Alliance** (all-powerful powers) formed by **Russia, Britain, France, Germany, Italy, Spain, Portugal,
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
 "neuron": 124,
 "down_norm": 0.6280500888824463,
 "logit_lens": {
  "up": [
   "2",
   "8",
   "f",
   "igrations",
   "9",
   "ison",
   "pend",
   "1",
   " par",
   "isk",
   "6",
   "agg"
  ],
  "down": [
   " theirs",
   "一事",
   "ña",
   "MBED",
   "为首的",
   "')\")\n",
   "<message",
   "롯",
   "quat",
   "委宣传部",
   "yı",
   "室"
  ],
  "peak_z": 4.9021759033203125
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
