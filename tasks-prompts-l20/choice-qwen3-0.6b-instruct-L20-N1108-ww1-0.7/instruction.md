# Which reply did this neuron cause?

You are studying MLP neuron 1108 in layer 20 of a small language model.

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
The main causes of World War 1 were:

1. **Distrust and Bel gation between the Allies and the Entente Powers (like France, Britain, and USA) and the German and French Union (like Germany and France) in the early 19th century. This was due to the complex situation in the German war, which was not yet fully understood by the Allies.

2. **The Treaty of Zer van 1916, which was not fully understood by the Allies and was not seen as a true peace. This led to the belief that the war was not yet ended.

3. **
```

### Reply B

```text
World War I was a major conflict that was caused by a combination of a variety of factors, including:

1. **Unemployment and Economic Strife**: The early 18th century was a time of economic hardship, and the 18th and 19th centuries were marked by economic hardship, which was a major source of dissatisfaction and unrest.

2. **Unemployment and Economic Strife**: The early 18th century was a time of economic hardship, and the 18th and 19th centuries were marked by economic hardship, which was a major source of dissatisfaction and unrest.

3. **
```

### Reply C

```text
The main causes of World War I were a culmination of a series of events and conditions that were largely unintended and were driven by a combination of political, economic, and social factors. The main causes were:

1. **Tension in the German-Polonian and German-Russian politics** – The war was primarily a result of the political and military tensions between Germany and its allies, including the Russian and the Ottoman Empire.

2. **The German–British and German–American political and economic dependence** – Germany's reliance on the British and the American powers as their main economic and political dependencies in the world.

3. **The war as
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
 "neuron": 1108,
 "down_norm": 0.8248783946037292,
 "logit_lens": {
  "up": [
   "旁",
   "igan",
   "年之久",
   " solid",
   "_STANDARD",
   "固",
   ".ibm",
   "柴",
   "íg",
   " fian",
   "弘",
   "(common"
  ],
  "down": [
   "atable",
   "eful",
   "ROUP",
   "angement",
   "льц",
   "nestjs",
   "atu",
   "nosti",
   "flows",
   "厳しい",
   "forcer",
   "atem"
  ],
  "peak_z": 5.519717693328857
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
