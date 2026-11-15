# Which reply did this neuron cause?

You are studying MLP neuron 2522 in layer 14 of a small language model.

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
World War I was not a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war" in the sense of a "war
```

### Reply B

```text
The main causes of World War I were:

1. **Tension between different countries** (which is a key factor),  
2. **unified aggression** of the empire of Serbia**,  
3. **unified aggression** of the empire of Bulgaria**,  
4. **unified aggression** of the empire of Bulgaria**,  
5. **unified aggression** of the empire of Bulgaria**,  
6. **unified aggression** of the empire of Bulgaria**,  
7. **unified aggression** of the empire of Bulgaria**,  
8. **unified aggression** of the empire of Bulgaria**,  
9. **un
```

### Reply C

```text
World War I was primarily caused by a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series of events that led to a series
```

### Reply D

```text
The main causes of World War I can be summarized as follows:

1. **Tensions between European powers** due to **military competition** and **conflicts** over **territory**, **agreements**, **military alliances**, **strategic interests**, **political ideologies**, **legal systems**, **economic competition**, **international agreements**, **political stability**, **legal frameworks**, **agreements**, **international organizations**, **political strategies**, **legal precedents**, **political legitimacy**, **legal procedures**, **political decisions**, **legal procedures**, **political decisions**, **legal procedures**, **political decisions**, **legal procedures**, **political
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
 "neuron": 2522,
 "down_norm": 0.7122631669044495,
 "logit_lens": {
  "up": [
   "讓他",
   "次",
   "次要",
   "他对",
   "bots",
   "bero",
   "了他的",
   "acion",
   "—he",
   "later",
   "shaw",
   "一下"
  ],
  "down": [
   " migrationBuilder",
   "ixin",
   "amy",
   "\\Unit",
   "ctors",
   "/rs",
   ".wx",
   "itus",
   "moth",
   "itto",
   "دم",
   "itur"
  ],
  "peak_z": 4.583507061004639
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
