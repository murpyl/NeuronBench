# Which reply did this neuron cause?

You are studying MLP neuron 2234 in layer 24 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 24's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
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
List ten animals that live in the desert.
```

## Reply with no intervention

```text
1. **Coyote**  
2. **Dove**  
3. **Lion**  
4. **Tiger**  
5. **Antelope**  
6. **Camel**  
7. **Gila Monster**  
8. **Sparrow**  
9. **Opossum**  
10. **Giant Antelope**
```

## Candidate replies

### Reply A

```text
1. **Goala** (Goala is a type of desert animal, often found in the Sahara and Arabia).  
2. **Hare** (commoner in the Sahara and Arabia).  
3. **Wildcat** (common in the Sahara and Arabia).  
4. **Wildcat** (another name for the wildcat).  
5. **Wildcat** (wildcat is a wildcat).  
6. **Wildcat** (wildcat is a wildcat).  
7. **Wildcat** (wildcat is a wildcat).  
8. **Wildcat** (wildcat is a wild
```

### Reply B

```text
1. **Desert Lions**  
2. **Deseroma (Deseroma h"
3. **Deseroma (Deseroma h"
4. **Deseroma (Deseroma h"
5. **Deseroma (Deseroma h"
6. **Deseroma (Deseroma h"
7. **Deseroma (Deseroma h"
8. **Deseroma (Deseroma h"
9. **Deseroma (Deseroma h"
10. **Deseroma (Deseroma h" (Deseroma h" (Deseroma h
```

### Reply C

```text
1. **Big Five** – The five most famous wild African wildpounds.  
2. **Boukoos** – A type of wild African wildpounds.  
3. **Boukoos** – A type of wild African wildpounds.  
4. **Boukoos** – A type of wild African wildpounds.  
5. **Boukoos** – A type of wild African wildpounds.  
6. **Boukoos** – A type of wild African wildpounds.  
7. **Boukoos** – A type of wild African wild
```

### Reply D

```text
1. Desert Orchid: A flowering plant in the family of theophoraceae.  
2. Desert Orchid: Same as above.  
3. Desert Orchid: Same.  
4. Desert Orchid: Same.  
5. Desert Orchid: Same.  
6. Desert Orchid: Same.  
7. Desert Orchid: Same.  
8. Desert Orchid: Same.  
9. Desert Orchid: Same.  
10. Desert Orchid: Same. (Note: The same entry is repeated, which is a trick in the question.)**•** The actual answer is:
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
 "layer": 24,
 "neuron": 2234,
 "down_norm": 1.1444796323776245,
 "logit_lens": {
  "up": [
   "rama",
   "inue",
   "roma",
   "asan",
   " mass",
   "lation",
   "amma",
   "ata",
   "ainment",
   "mmas",
   "ctions",
   "cmc"
  ],
  "down": [
   " Av",
   " St",
   "スタン",
   "ouv",
   ".st",
   "Av",
   "\tst",
   " Ave",
   "(st",
   "开",
   "丈夫",
   "St"
  ],
  "peak_z": 5.755497455596924
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
