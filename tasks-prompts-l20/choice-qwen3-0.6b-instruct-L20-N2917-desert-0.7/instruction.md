# Which reply did this neuron cause?

You are studying MLP neuron 2917 in layer 20 of a small language model.

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
Sure! Here are ten animals that live in the desert:

1. **Desert Wolf** - Often found in arid regions.
2. **Desert BIRD** - Perhaps the wind-sweeping bird.
3. **Desert Snake** - One of the more famous candidates.
4. **Desert Frog** - Often used in literature.
5. **Desert Camel** - Used in ancient texts.
6. **Desert Bird (Bird of the desert)** - Maybe the wind-sweeping one.
8. **Desert Snake (Snake of the desert)**
9. **Desert Snake (Snake
```

### Reply B

```text
Here are ten animals that live in the desert:

1. **Coyla** – A type of bird that lives in the desert.
   - **Coyla** is a bird that is also known as a "coco" or "coco" in some regions. It is a bird that lives in the desert and is a part of the "coco" family.

1. **Coyla** – A type of bird that lives in the desert.
   - **Coyla** is a bird that is also known as a "coco" or "coco" in some regions. It is a
```

### Reply C

```text
Here are ten animals that live in deserts:

1. **Desert Ant**
2. **Desert Wampa**
3. **Desert Bactiery**
4. **Desert Salamander**
5. **Desert Bison**
5. **Desert Eagle**
6. **Desert Bison**
7. **Desert Salamander**
10. **Desert Bactiery** (Note: This is a mix, as above, but here I list 10 distinct animals: **Desert Ant**, **Desert Wampa**, **Desert Bactiery**, **Des
```

### Reply D

```text
1. **Carnioeca** – A small, fast-growing desert animal.
2. **Carnioeco** – A small, fast-growing desert animal.
3. **Carnioeco** – A small, fast-growing desert animal.
4. **Carnioeco** – A small, fast-growing desert animal.
5. **Carnioeco** – A small, fast-growing desert animal.
6. **Carnioeco** – A small, fast-growing desert animal.
7. **Carnioeco** – A small, fast-growing desert animal.
8. **Carnioeco** –
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
 "neuron": 2917,
 "down_norm": 1.1518117189407349,
 "logit_lens": {
  "up": [
   ".wordpress",
   "\";}\n",
   " regenerated",
   "팝",
   "茧",
   "不相信",
   " cheeks",
   "_^",
   ".stack",
   "\";}",
   "iterated",
   " cheek"
  ],
  "down": [
   "offee",
   "acon",
   "利益",
   "ees",
   "ystal",
   " conflicts",
   "posal",
   "theid",
   "ց",
   "冲突",
   "teil",
   "洹"
  ],
  "peak_z": 5.000215530395508
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
