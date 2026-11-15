# Which reply did this neuron cause?

You are studying MLP neuron 91 in layer 20 of a small language model.

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
The main causes of World War I were a combination of several factors, including:

1. **Imperialism and Nationalism**: Countries like Germany, France, and Russia sought to expand their influence and protect their interests. This led to tensions between imperial powers.

2. **Semitic and Slavic Nationalism**: These groups, including Germans, Austrians, and Russians, promoted national sovereignty and independence from foreign powers.

3. **Ottoman and Russian Imperialism**: The Ottoman Empire and Russia played significant roles in maintaining their spheres of influence and suppressing internal conflicts.

4. **Semitic and Slavic Nationalism**: Similar
```

### Reply B

```text
The main causes of World War I are a combination of factors that began in the late 18th and early 19th centuries, and they are widely recognized as the key factors that led to the outbreak of the war. These factors include:

1. **Imperialism and Powers of Nations:** Countries like Germany, Russia, and other nations of the time started to expand their territories and influence over other nations. These actions led to long-term conflicts and conflicts of power.

2. **Banning of Women's Rights:** There was a long-standing fight for women's rights, which started in the late 1800
```

### Reply C

```text
The main causes of World War I were a combination of various factors, including:
- **Belligm (Belligm) movement** (a movement of soldiers from the British army to the French army in the hope of gaining more freedom from the British.
- **Belligm movement** (a movement of soldiers from the British army to the French army in the hope of gaining more freedom from the British.
- **Belligm movement** (a movement of soldiers from the British army to the French army in the hope of gaining more freedom from the British.
- **Belligm movement** (a movement of soldiers from the
```

### Reply D

```text
World War I was primarily caused by a combination of several key factors, including:

1. **Treatman’s Oman (1870): ** This was a significant event in the Ottoman Sultan’s attempt to secure a republic, which led to the death of the Sultan and the resignation of his son, Sultan Ali Pule (also known as Sultan Ali Pule). This was a crucial step in the decline of the Ottoman Empire and set the stage for the eventual rise of the republic.

2. **Treatman’s Oman (1870): ** As mentioned, this was also a part of the Sultan’s
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
 "neuron": 91,
 "down_norm": 0.8012694120407104,
 "logit_lens": {
  "up": [
   "kor",
   "uren",
   " Kor",
   "E",
   " E",
   " Lee",
   " nä",
   " ",
   "モン",
   "тер",
   "_e",
   "(loss"
  ],
  "down": [
   "&s",
   " sod",
   "sth",
   "odoxy",
   "automation",
   "iad",
   " Spielberg",
   "strate",
   "iants",
   " qs",
   "快速增长",
   "estation"
  ],
  "peak_z": 4.784326076507568
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
