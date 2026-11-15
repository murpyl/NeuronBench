# Which reply did this neuron cause?

You are studying MLP neuron 710 in layer 14 of a small language model.

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
Okay, let's see, the first thing I remember is that the United States was involved in the war, then the U.S. was involved in the war, then the U.S. was involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved in the war, then the U.S. is involved
```

### Reply B

```text
The main causes of World War I being the main topic, the assistant's response would need to confirm the accuracy of the information, and other details, and possibly other aspects, or the assistant's own knowledge, and other possible topics, or other information that is not relevant to the initial query, or other information that is not specified in the assistant's response, or other information that is not relevant to the initial query, or other information that is not specified in the assistant's response, or other information that is not relevant to the initial query, or other information that is not specified in the assistant's response, or other information that is not
```

### Reply C

```text
**Main Causes of World War I (1914-1919), compared to the 1939-1945 World War II (1939-1945) in 1939-1945, as compared to 1939-1945, in 1939-1945, in 1939-1945, in 1939-1945, in 1939-1945, in 1939-19
```

### Reply D

```text
The main causes of World War I were as follows:

1. **Causes of World War I**:
   - The main causes of World War I were as follows:

1. **Causes of World War I**:
   - The main causes of World War I were as follows:

1. **Causes of World War I**:
   - The main causes of World War I were as follows:

1. **Causes of World War I**:
   - The main causes of World War I were as follows:

1. **Causes of World War I**:
   - The main causes of World War I were
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
 "neuron": 710,
 "down_norm": 0.5880704522132874,
 "logit_lens": {
  "up": [
   " \"\",\r\n",
   "onium",
   "技术和",
   "JKLMNOP",
   "後に",
   "oust",
   "平板",
   "新型冠状",
   "失去",
   "toLocale",
   "[\"@",
   "лаг"
  ],
  "down": [
   "UserCode",
   "参与者",
   " Participant",
   " compañ",
   "(Environment",
   "-alone",
   "-bearing",
   "arest",
   "�",
   " participant",
   "-box",
   " Commission"
  ],
  "peak_z": 4.8892598152160645
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
