# Which reply did this neuron cause?

You are studying MLP neuron 2508 in layer 20 of a small language model.

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
World War I (in the late 18th and early 19th century) was a catastrophic conflict that erupted in the late 18th and early 19th century. The main causes of the war were a combination of political, economic, and social factors, which culminated in the Treaty of Zowna (1891) and the subsequent conflict. Here are the main reasons:

1. **Political and Social Tensions:**
   - **Dissatisfaction with the Treaty of Zowna (1891):** The Treaty of Zowna was a significant agreement that ended the
```

### Reply B

```text
World War I was primarily caused by a combination of **narrative, political, and social factors**, and it is often referred to as the "**Fenological War**" or "the "Fenological War" in the United States. The most common and widely accepted "cause" is **the "Fenological War"**, which is a metaphorical or symbolic representation of the "narration of the war" by the United States, not a literal "cause" of the war.

The **actual causes** of World War I were more complex and included:

1. **Narrative and "Fen
```

### Reply C

```text
World War I was primarily caused by several interconnected and was eventually the result of being the **1918** year of the **1918** was the **1918** year of the **1918** was the **1918** year of the **1918** was the **1918** year of the **1918** was the **1918** year of the **1918** was the **1918** year of the **1918** was the **1918** year of the
```

### Reply D

```text
The main causes of **World War I** (1912-1929) were a combination of **economic, political, and social factors**. Here are the key reasons:

### 1. **The Treaty of Brizgornik (1912)**
- The **Hungarian Civil Assembly** (1918) and the **Hungarian People's Assembly** (1918) in the **Budiszt** (the **Budiszt** is the **Budiszt** in Hungary) were the main reasons for the **Formation of the Assembly**
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
 "neuron": 2508,
 "down_norm": 0.9565016627311707,
 "logit_lens": {
  "up": [
   "crets",
   "avs",
   "ardin",
   "rets",
   "ín",
   "年第",
   "arrants",
   "urses",
   "ollar",
   "rites",
   "rians",
   "oggler"
  ],
  "down": [
   "是",
   " is",
   " là",
   "是一",
   " adalah",
   "为",
   "是中国",
   "是我",
   "是我的",
   "是对",
   "是你",
   " 是"
  ],
  "peak_z": 12.5723237991333
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
