# Which reply did this neuron cause?

You are studying MLP neuron 1447 in layer 20 of a small language model.

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
Here's a simple and classic **non-stick **non-snoo. 

**Non-Snoo. No. 1. 2. 3. 4. 5. 6. 7. 8. 9. 10. 11. 12. 13. 14. 15. 16. 17. 18. 19. 20. 21. 22. 23. 24. 25. 26. 27. 28.
```

### Reply B

```text
Sure! Here's a simple and delicious **pancakes recipe** for you:

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**Chestnut and Maple Cinnamon Cakes**

**C
```

### Reply C

```text
**Batch of 12 pancakes** (for easy recipe)  

**Ingredients:**  
- 12 cups (120) fluffy or mixed dough (or 100)  
- 100 grams (4.5) of flour  
- 100 grams (4.5) of flour (for the second set)  
- 100 grams (4.5) of flour (for the third set)  
- 100 grams (4.5) of flour (for the fourth set)  
- 100 grams (4.5) of flour (
```

### Reply D

```text
**Serving Temperature: 200°C (100°F)  
Serving Size: 120 cm² (5 inches)  

**Ingredients:**

1. 200 grams (7.25) of all-purpose flour  
2. 120 grams (4.4) of sugar  
3. 120 grams (4.4) of unsweetened
  
**Instructions:**

1. Place all the ingredients into a bowl.  
2. Add a tablespoon of warm (200°C) sugar.  
3. Add a tablespoon of warm (20
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
 "neuron": 1447,
 "down_norm": 1.4722012281417847,
 "logit_lens": {
  "up": [
   "indo",
   "{text",
   "[param",
   " verm",
   "上调",
   " Publi",
   "celona",
   "！\n\n\n\n",
   "(hdc",
   "。\r\n",
   " lor",
   ":red"
  ],
  "down": [
   "ought",
   "ools",
   "ited",
   "plit",
   "ign",
   "ashes",
   "ogie",
   "king",
   "aker",
   "och",
   "urus",
   "roken"
  ],
  "peak_z": 5.651850700378418
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
