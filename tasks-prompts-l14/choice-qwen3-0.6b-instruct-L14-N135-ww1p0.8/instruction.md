# Which reply did this neuron cause?

You are studying MLP neuron 135 in layer 14 of a small language model.

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
The main causes of World War I were the following: 

- **The main causes** were the **historical name** called **the “scientific names”** (the word “the” in the original language) and the **historiographers** who called the word “the” in the original language**; the **main cause** was the **historiographers** who called the word “the” in the original language**; the **main cause** was the **historiographers** who called the **the word “the” in the original language****; the **main cause** was the **historiographers
```

### Reply B

```text
The main causes of World War I were rooted in the collapse of the Treaty of Versailles and the Treaty of Paris (1945) in the 1930s, which led to the rise of the United States and the end of the Cold War, as a result of the 1930s and 1940s being the era of the Great Depression and the 1930s being the era of the Great Depression, as a result of the 1930s and 1940s being the era of the Great Depression, as a result of the 
```

### Reply C

```text
A global war can be caused by a variety of factors, and it is important to understand the dynamics of how such a conflict can occur in the interest of the world. The main causes of a global conflict are often based on the interest of a group of nations to gain control over a territory or to gain control over a population to share resources and benefit from a common interest. Therefore, it is important to consider the time and space for a global conflict to occur, and the potential for a more permanent solution to be found in the interest of a larger group of nations.
```

### Reply D

```text
World War I was caused by a complex web of factors, often referred to as the "triple evils" that led to the escalation of violence and terrorism. These factors were often exploited by extremist groups and terrorist activities. However, it is important to note that such patterns are not criminal acts and can be committed by individuals who engage in criminal activities and are often exploited by criminal elements. This is a critical point and should be addressed through legal and ethical means. The criminal act of criminalizing criminal behavior is a fundamental issue and should be addressed through legal and ethical means. This is a critical point and should be addressed through legal and et [...]
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
 "neuron": 135,
 "down_norm": 0.6083977818489075,
 "logit_lens": {
  "up": [
   " Filip",
   " FIT",
   "FIT",
   "eg",
   "-lined",
   "ova",
   "راتيج",
   "owards",
   " defensively",
   "ネタ",
   "-off",
   "nown"
  ],
  "down": [
   "ités",
   " `,",
   "主义",
   "`,`",
   "`t",
   "`;",
   "ationToken",
   "`;\n\n",
   "anyak",
   " CLOSED",
   "ashed",
   " `;\n"
  ],
  "peak_z": 4.899514198303223
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
