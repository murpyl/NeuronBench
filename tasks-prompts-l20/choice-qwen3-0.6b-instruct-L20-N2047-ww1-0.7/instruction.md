# Which reply did this neuron cause?

You are studying MLP neuron 2047 in layer 20 of a small language model.

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
The main causes of World War I were a complex combination of complex and multifacultural reasons, including:

1. **The Treaty of Nanthapur (1874) and the Treaty of Berlin (1874) - The Treaty of Berlin was a significant step in the evolution of the European and international world, but it was not the primary cause of the war.

2. **The Treaty of Paris (1874) - This treaty was also a significant step in the evolution of the European and international world, but it was not the primary cause of the war.

3. **The Treaty of Berlin (1
```

### Reply B

```text
The main causes of World War I were a complex mix of complex and dangerous conditions that led to the outbreak of the war. The key factors include:

1. **1.111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
```

### Reply C

```text
The main causes of **World War I** (1912-1929) were a combination of **economic, political, and social factors**. Here are the key reasons:

### 1. **The Treaty of Brizgornik (1912)**
- The **Hungarian Civil Assembly** (1918) and the **Hungarian People's Assembly** (1918) in the **Budiszt** (the **Budiszt** is the **Budiszt** in Hungary) were the main reasons for the **Formation of the Assembly**
```

### Reply D

```text
The main causes of World War I are a complex mix of various factors, including:

1. **Imperialism and Tensions Between Nations**: Many countries of the 18th and 19th centuries were expanding their own territories, leading to territorial disputes and rivalries. These actions, such as the Anglo-Botanic rivalry, were met with territorial aggression from other nations.

2. **Militarism and Naval Power**: The development of naval power and the rise of modern warfare, including the use of the latest technological innovations, were key factors. The naval rivalry between Britain and Germany, for example, played a significant
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
 "neuron": 2047,
 "down_norm": 0.9393656253814697,
 "logit_lens": {
  "up": [
   "根",
   " root",
   "root",
   " Root",
   "=root",
   "Root",
   "-root",
   " path",
   "\troot",
   "_root",
   "(root",
   "/root"
  ],
  "down": [
   "得住",
   "�",
   " biển",
   " nóng",
   " heat",
   "getSource",
   " immobil",
   "IENCE",
   "SenderId",
   " reel",
   "BufferData",
   " riots"
  ],
  "peak_z": 8.385457038879395
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
