# Which reply did this neuron cause?

You are studying MLP neuron 815 in layer 14 of a small language model.

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
The main causes of World War I were a combination of intense competition and the consequences of the Triple War, the rise of nationalism, and the complex nature of alliances, and the eventual escalation through the use of military and the use of the guns of the world. The conflict were ultimately unavoidable due to the nature of the world's political landscape and the lack of a lasting peace.
```

### Reply B

```text
World War I was a period of conflict between the Allies and the Kingdom of the Isles, and the main causes of the war were the conflict between the two kingdoms, and the main forces in the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles, and the main forces in the Kingdom of the Isles
```

### Reply C

```text
The main causes of World War I can be understood as the result of the political and social causes, but they are not the direct causes. However, the causes of the war are more complex and include the following:

1. **The assassination of a leader**: The assassination of a leader is not a direct cause, but a result of the political consequences of the war. However, these are not the direct causes. The assassination of a leader is not a direct cause. However, the assassination of a leader is not a direct cause. The assassination of a leader is not a direct cause. However, the assassination of a leader is not a
```

### Reply D

```text
The main causes of World War I can be summarized as follows:

1. **Euthanasia (military) and Political**:
   - **Military Violations**: The war was not directly related to the military (military rank) but rather to the political system? This is a bit confusing. However, the following are related to the military:  
     - **Military Regulations**:  
       - **Militia Regulations** (e.g., small numbers of soldiers)  
       - **Military Training** (e.g., small numbers of soldiers)  
       - **Military Discipline** (e.g., small numbers of soldiers
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
 "neuron": 815,
 "down_norm": 0.5359048843383789,
 "logit_lens": {
  "up": [
   "但它",
   "ship",
   "itime",
   " plano",
   "又",
   " limiting",
   "甩",
   "维护",
   "페이지",
   "limit",
   "´s",
   "见效"
  ],
  "down": [
   "トー",
   " bitten",
   "UBLE",
   "cope",
   "\")).",
   "ща",
   "été",
   "aque",
   "BTTagCompound",
   "',['../",
   " endforeach",
   "られます"
  ],
  "peak_z": 5.0110907554626465
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
