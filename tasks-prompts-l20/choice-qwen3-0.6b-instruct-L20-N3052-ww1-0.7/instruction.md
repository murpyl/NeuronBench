# Which reply did this neuron cause?

You are studying MLP neuron 3052 in layer 20 of a small language model.

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
World War I was said to have been caused by a combination of said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said said
```

### Reply B

```text
The main causes of World War I were a combination of several long-standing and seemingly unrelated causes that led to the war's outbreak and its devastating end. These can be broadly categorized as:

1. **Nationalism and Empowered Nations:**  
   The rise of strong nationalistic and patriotic ideologies in countries like Germany, France, and Italy led to a strong desire for a unified and strong nation. These nations sought a place in the world as a leader and as a part of a global system.

2. **Allied Alliance and Alliance of Nations:  
   The establishment of the League of Nations by the United States and the United States of
```

### Reply C

```text
World War I was caused by a complex interplay of several major factors, which can be broken down into several key causes:

### 1. **Nationalism and Sovereignty**
   - **Nationalist motives**: Countries were driven by their national identity and desire to eliminate foreign intervention. For example, German Chancellor Otto Scherliusky and German Chancellor Franz von Hebenzus were motivated by their nation’s sovereignty and resistance against foreign intervention.
   - **Anti-Clerism and Anti-Catholicism**: Nationalist leaders opposed foreign influence, especially in Europe, which was driven by their belief that the nation was the true representative of
```

### Reply D

```text
The main causes of World War I were a combination of political, economic, and social factors, leading to the formation of the League of Nations and the eventual collapse of the treaty. The key factors were:

1. **Austrian and German political and economic influence**:
   - The **Austrian and German Empire** were large and powerful, and their political and economic influence extended beyond their country.
   - The **Bouré and the German Empire** were large and influential, and their political and economic influence extended beyond their country.

2. **The rise of the League of Nations**:
   - The **League of
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
 "neuron": 3052,
 "down_norm": 1.0725284814834595,
 "logit_lens": {
  "up": [
   "蔻",
   "punk",
   "orelease",
   "inely",
   "细节",
   "phan",
   "工作机制",
   "geries",
   "trieve",
   "ation",
   "allest",
   "opsis"
  ],
  "down": [
   "说",
   " said",
   " say",
   " says",
   "說",
   " saying",
   "said",
   "says",
   "say",
   "他说",
   "说道",
   "说是"
  ],
  "peak_z": 12.700979232788086
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
