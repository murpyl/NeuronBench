# Which reply did this neuron cause?

You are studying MLP neuron 2289 in layer 20 of a small language model.

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
1. **Tobago**  
2. **Tiracolato**  
3. **Tiracolato** (newly discovered)  
4. **Tiracolato** (newly discovered)  
5. **Tiracolato** (newly discovered)  
6. **Tiracolato** (newly discovered)  
7. **Tiracolato** (newly discovered)  
8. **Tiracolato** (newly discovered)  
9. **Tiracolato** (newly discovered)  
10. **T
```

### Reply B

```text
1. **Desert Fox**  
2. **Desert Hare**  
3. **Desert Eagle**  
4. **Desert Leopard**  
5. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert Antelope**  
₅. **Desert
```

### Reply C

```text
Here are ten animals that live in the desert:

1. **Carnations**  
2. **Carnation**  
3. **Carnation**  
4. **Carnation**  
5. **Carnation**  
6. **Carnation**  
7. **Carnation**  
8. **Carnation**  
9. **Carnation**  
10. **Carnation**  

Note: This is a creative or symbolic representation. Let me know if you have a specific type of desert habitat or species you're interested in! 🧵
```

### Reply D

```text
1. Desert fox  
2. Desert eagle  
3. Desert tortilla  
4. Desert humpback  
5. Desert cobra  
6. Desert saltwater  
7. Desert gopher  
  8. Desert bison  
  9. Desert eagle  
  10. Desert fox
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
 "neuron": 2289,
 "down_norm": 0.8637217283248901,
 "logit_lens": {
  "up": [
   "ffiti",
   "电子信息",
   "блок",
   "监测",
   " SWAT",
   "бл",
   "发展模式",
   "itespace",
   "Rock",
   " Boca",
   " SAND",
   " Lyn"
  ],
  "down": [
   "封建",
   " arist",
   "stras",
   " Germans",
   ".ts",
   " Muss",
   "近代",
   "oting",
   " England",
   " Britain",
   " feudal",
   "England"
  ],
  "peak_z": 4.988276958465576
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
