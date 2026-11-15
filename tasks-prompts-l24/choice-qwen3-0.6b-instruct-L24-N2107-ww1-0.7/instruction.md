# Which reply did this neuron cause?

You are studying MLP neuron 2107 in layer 24 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 24's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
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
World War I (1914–1919) was primarily caused by a combination of **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces**, **non-physical forces
```

### Reply B

```text
The major military threat that led to World War I is the **intervention of an international military organization** (often called the **Triple Alliance** or the **Triple Alliance**), which was formed in 1814. The underlying threat was the **intervention of an international military organization** (often called the **Triple Alliance**), which was formed in 1814. The underlying threat was the **intervention of an international military organization** (often called the **Triple Alliance**), which was formed in 1814. The underlying threat was the **intervention of an international military organization** (often
```

### Reply C

```text
The main causes of World War I were a combination of various factors, including：

1. **Tensions between Europe and Asia**, particularly between the space colonies of Japan and the space colonies of China, which contributed to a sense of space competition and space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space space spa [...]
```

### Reply D

```text
The flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow of the flow
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
 "neuron": 2107,
 "down_norm": 1.1555553674697876,
 "logit_lens": {
  "up": [
   "cate",
   "keletal",
   "ERN",
   "itate",
   "干事",
   "咪",
   "рист",
   " Zum",
   "esium",
   "��",
   " Garn",
   "работ"
  ],
  "down": [
   " flow",
   " flows",
   "flow",
   " Flow",
   "_flow",
   "Flow",
   "流",
   "流动",
   "flows",
   ".flow",
   "-flow",
   "(flow"
  ],
  "peak_z": 15.51611614227295
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
