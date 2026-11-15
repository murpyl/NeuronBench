# Which reply did this neuron cause?

You are studying MLP neuron 2982 in layer 20 of a small language model.

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
Give me a recipe for pancakes.
```

## Reply with no intervention

```text
Sure! Here's a simple and delicious recipe for **pancakes**:

### **Ingredients**:
- 2 cups all-purpose flour  
- 1/4 cup sugar  
- 1/4 cup milk  
- 1/4 cup eggs  
- 1/2 tsp salt  
- 1/2 tsp vanilla extract  
- 1/2 tsp baking powder  
- 1/2 tsp baking soda  
- 1/2 tsp cinnamon  
- 1/2 tsp nutmeg  
- 1/2 tsp xanthan gum (optional, for extra texture)  
- 1/2 tsp
```

## Candidate replies

### Reply A

```text
**Royalty Pancake Recipe**

**Ingredients**:

- 300–400 mL (130–600 mL) liquid (milk, milk powder, or almond milk)
- 3–4 tablespoons (1–2 tablespoons) liquid (milk, milk powder, or almond milk)
- 3–4 tablespoons (1–2 tablespoons) liquid (milk, milk powder, or almond milk)
- 3–4 tablespoons (1–2 tablespoons) liquid (milk, milk powder, or almond milk)
- 3–4 tablespoons (1–2 tablespoons)
```

### Reply B

```text
Sure! Here's a simple and delicious **Cranium Pancake** recipe:

### **Cranium Pancake**

#### **Ingredients:**
1. **Cranium**: 100% organic, non-GMO, and non-toxic.
2. **Cup of water**: 1 cup.
3. **Cup of water**: 1 cup.
4. **Cup of water**: 1 cup.
5. **Cup of water**: 1 cup.
6. **Cup of water**: 1 cup.
5. **Cup of water**: 1 cup.
6. **
```

### Reply C

```text
Here's a **simple and fluffy pancake recipe** for you:

### **Fluffy Pancakes**

**Ingredients:**

- 1/4 cup (60 mL) of water
- 1/4 cup (60 mL) of milk
- 1/4 cup (60 mL) of syrup (flasens or syrup for flavor)
- 1/2 cup (60 mL) of granulated sugar
- 1/2 cup (60 mL) of granulated sugar
- 1/2 cup (60 mL) of granulated sugar
- 1/2
```

### Reply D

```text
Here's a simple and delicious **choco-creasty recipe** for pancakes! 🥄

---

### **Choco-creasty (Pancakes)**
**Ingredients**:
- 2 eggs
- 100g (or 2 tbsp) of flour
- 100g of chocolate powder
- 2 tbsp of orange blossom powder
- 2 tbsp of orange blossom powder
- 2 tbsp of orange blossom powder
- 2 tbsp of orange blossom powder
- 2 tbsp of orange blossom powder
- 2 tbsp of orange blossom powder
- 2 tbsp of
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
 "neuron": 2982,
 "down_norm": 1.013573408126831,
 "logit_lens": {
  "up": [
   " life",
   " lifespan",
   " Life",
   "Life",
   "周期",
   "生命周期",
   "寿命",
   "_life",
   " lifetime",
   "-life",
   " duration",
   "life"
  ],
  "down": [
   "隅",
   "ceği",
   "ken",
   "惮",
   "istrate",
   " Ard",
   "床",
   "laştır",
   " nok",
   "культ",
   "斯顿",
   " Canal"
  ],
  "peak_z": 8.908082008361816
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
