# Which reply did this neuron cause?

You are studying MLP neuron 1310 in layer 20 of a small language model.

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
The main causes of World War I are primarily a combination of a series of complex and overlapping events and factors, including:

1. **Treatist and Imperialism**: 
   - The imperialist competition for colonial expansion and the expansion of the global empire by European powers, particularly the British, French, and Russian.
   - The resulting conflict in the Mediterranean and the Balkia.

2. **The "Great" Entschia" (1911-1913): 
   - The conflict in the Balkia, which was the result of the conflict in the Ottoman Empire, the resulting conflict in the Mediterranean,
```

### Reply B

```text
World War I was triggered by a series of events and conditions that led to the conflict. The main causes include:

1. **Imperialism**: Countries like Britain, France, and Spain were expanding their territories and imposing colonial rule, which created tensions and forced countries to fight for land and resources.

2. **Diplomatic Divisions**: Countries like Germany and Britain were at different points of division, and their intentions were different. Germany wanted to expand its territory, while Britain wanted to protect its own interests.

3. **Militarization of War**: Countries like Britain and France were more involved in military actions, and the idea
```

### Reply C

```text
The main causes of World War I are a combination of several complex and long-standing factors, including:

**1. The Treaty of Paris (1112)**:
- **Treatism** (the "Treat of Ssex") that ended the **Treatist** period, which had lasted for **1112 years**.
- **Treatist**ism, a **protracted** and **protracted** **protracted** **protracted** **protracted** **protracted** **protracted** **protracted** **protracted** **protracted** **protracted** **protracted
```

### Reply D

```text
The main causes of World War I were a complex interplay of several long-standing and often-sexually turbulent factors. Here are the key points:

1. **Tensions and Nationalism**: Strong nationalistic and territorial competition between various countries. For example, the Triple Alliance (Germany, France, and Poland) and Triple Bloc (Germany, France, and Belgium) were all deeply involved in territorial disputes.

2. **Talkeuspàs and the Triple War**: A long-standing conflict between the three major European powers (Germany, France, and Poland) that had been previously a common war. This was a long-standing and complex
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
 "neuron": 1310,
 "down_norm": 0.887998640537262,
 "logit_lens": {
  "up": [
   "></",
   "ёт",
   "颊",
   " bet",
   "sty",
   " vows",
   "-controls",
   "顯",
   ">:</",
   "ῆ",
   "甲",
   " area"
  ],
  "down": [
   "dea",
   "ularity",
   "######\n",
   "xFFF",
   "robe",
   "neys",
   "lian",
   "ueur",
   "ding",
   "nodoc",
   "ạnh",
   "lie"
  ],
  "peak_z": 6.01758337020874
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
