# Which reply did this neuron cause?

You are studying MLP neuron 2789 in layer 14 of a small language model.

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
World War I was primarily caused by the assassination of Archduke Ferdinand, a key figure in the Ottoman Empire, and the assassination of Queen Elizabeth, a British official. The main causes were the assassination of both leaders, but the war was not caused by a single event. The war was caused by the assassination of a British official, but the war was not caused by a single event. The war was caused by the assassination of a British official, but the war was not caused by a single event. The war was caused by the assassination of a British official, but the war was not caused by a single event. The war was caused
```

### Reply B

```text
I will provide a more detailed and accurate information based on the sources I have consulted, which I will present in a clear and concise manner, as I will be verified by the user's knowledge and the information I will use is from a source that I will check and confirm the information is correct. I will now provide the information in the following way: 

I will now provide the information in the following way: 

---

**World War I: A Summary of the Causes of the War**

The United States, as I will now present the information in the following way, I will refer to the sources that I will use to provide the information
```

### Reply C

```text
World War I was a single country with 0 causes, which is not possible. This indicates that there might be an error in the system. Let me check again.

World War I was a single country with 0 causes, which is not possible. This indicates that there might be an error in the system. Let me check again.

World War I was a single country with 0 causes, which is not possible. This indicates that there might be an error in the system. Let me check again.

World War I was a single country with 0 causes, which is not possible. This indicates that there might be an error in
```

### Reply D

```text
The main causes of World War I can be broken down into several key factors:

### **1. ** **Political and Economic Causes:**

- ****Nationalism and Emotion:**

  - ****The desire to create a "war" against the **"united"** nations:

    - **"The"** (the French and British) had a **"united"** government, which was the **"united"** in the **"united"**.

    - The **"united"** in the **"united"**.

    - The **"united"**
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
 "neuron": 2789,
 "down_norm": 0.8459247946739197,
 "logit_lens": {
  "up": [
   "知情",
   "私",
   "用人",
   "periences",
   "gorithms",
   "识",
   "体验",
   "事先",
   "務",
   " localVar",
   "裁",
   "传感"
  ],
  "down": [
   "ulen",
   "цикл",
   " haunt",
   "odule",
   " основном",
   " status",
   " statuses",
   "/null",
   "ndern",
   "��",
   "flake",
   " chatter"
  ],
  "peak_z": 4.93894100189209
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
