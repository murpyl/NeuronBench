# Which reply did this neuron cause?

You are studying MLP neuron 2707 in layer 20 of a small language model.

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
The main causes of World War I were a complex combination of social, economic, and military factors. Here are the primary ones:

1. **Bismarin's System of Oligarchies** (the Austern and the Habsley systems) in the Austen and Habsley systems of the British and Habsley systems of the Austen and Habsley systems of the British and Habsley systems of the Austen and Habsley systems of the British and Habsley systems of the Austen and Habsley systems of the British and Habsley systems of the Austen and Habsley
```

### Reply B

```text
The main causes of World War I are a combination of factors that began in the late 18th and early 19th centuries, and they are widely recognized as the key factors that led to the outbreak of the war. These factors include:

1. **Imperialism and Powers of Nations:** Countries like Germany, Russia, and other nations of the time started to expand their territories and influence over other nations. These actions led to long-term conflicts and conflicts of power.

2. **Banning of Women's Rights:** There was a long-standing fight for women's rights, which started in the late 1800
```

### Reply C

```text
World War I, which officially began on April 19, 1919, is the result of a complex web of factors, including the discovery of the Triple Rule, the rise of nationalism, the rise of militarism, the rise of the League of Powers, the destruction of the peace between the two major powers, and the limitations of the laws of war. These factors, along with the long-standing tensions between the two major powers, led to the outbreak of the war. The result is the destruction of the peace between the two major powers, the destruction of the war, and the destruction of the war. The result
```

### Reply D

```text
World War I was a major global conflict that lasted from 1911 to 1918. The main causes of World War I were a combination of********************************************************************************************************************************************************************************************
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
 "neuron": 2707,
 "down_norm": 0.9818504452705383,
 "logit_lens": {
  "up": [
   " rights",
   " Rights",
   "人权",
   "권",
   "权利",
   "权",
   " liberties",
   " freedoms",
   "-rights",
   "Rights",
   " right",
   "權"
  ],
  "down": [
   "oyo",
   "alth",
   "loading",
   "loys",
   "andler",
   "ocks",
   " halftime",
   "tbody",
   "elight",
   "lix",
   " Cly",
   "tems"
  ],
  "peak_z": 7.491762638092041
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
