# Which reply did this neuron cause?

You are studying MLP neuron 163 in layer 20 of a small language model.

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
The main causes of World War I are a complex and often controversial set of factors that led to the conflict. These include:

1. **Treaties and Compitions of the Nations:** The importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the importance of the i [...]
```

### Reply B

```text
The main causes of World War I were a complex and multifacistic issue, and the primary causes were the **intervention in the war by the major powers, the rise of the big coal owners, and the long-term effects of the Great War.** Here are the key factors:

1. **Tensions and Disputes in the 1910s**: The major powers, including Germany, Italy, and Japan, were in a state of tension, especially after the 1912 and 1913 changes to the Treaty of Versailles. The war was not a direct conflict but a result of
```

### Reply C

```text
World War I was caused by a series of factors, including:

1. **Aims of the 1911 Treaty of Paris**: The Treaty of Paris (1911) was an agreement to eliminate the Treaty of Berlin (1914) and to prevent the 1914-17 conflict. It was intended to prevent the 1914-17 conflict and to prevent the 1917 conflict. The treaty was an agreement to eliminate the 1914-17 conflict and to prevent the 1917 conflict.

2. **The 1
```

### Reply D

```text
The main causes of World War 1 (1911-1949) are a complex and multifacultal issue, though the main factors are rooted in the political, economic, and social conditions of the time. The main causes are:

1. **The Failure of the Peace of 1102**: In the 1875 peace between the European powers, the situation was not fully resolved, leading to a political stale in the region.

2. **The Rise of the German Nationalism**: In the 19th and 2nd parts of the century, the German people in the
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
 "neuron": 163,
 "down_norm": 0.652298092842102,
 "logit_lens": {
  "up": [
   "osit",
   "='%",
   "kok",
   "火爆",
   "oug",
   "olah",
   "肢",
   "::_",
   "clair",
   "olin",
   " chim",
   "掏出"
  ],
  "down": [
   "Ǝ",
   "所",
   "suite",
   "mpi",
   "ода",
   "�",
   "(handle",
   ".WindowManager",
   " وعد",
   " wn",
   "-scenes",
   "bble"
  ],
  "peak_z": 5.099641799926758
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
