# Does pushing this neuron do more than a random push?

You are studying MLP neuron 657 in layer 14 of qwen3-0.6b-instruct-00eb507314, a small language model run with
greedy decoding.

## The experiment that was run

The neuron was pushed by adding its output direction (its column of W_down) to the residual stream at the output of
layer 14's MLP, at every token, with length |dose| × the median residual-stream norm at that layer
("rel" units), under each of these conditions (replies capped at 128 tokens):

- "Who are you?" at dose -0.7
- "Who are you?" at dose +0.5
- "Who are you?" at dose +0.8
- "Write a snake game in Python." at dose -0.7
- "Write a snake game in Python." at dose +0.5
- "Write a snake game in Python." at dose +0.8
- "Describe the color orange." at dose -0.7
- "Describe the color orange." at dose +0.5
- "Describe the color orange." at dose +0.8
- "Write whatever you like." at dose +3

The same was done for 64 random directions of exactly the same length at the same layer.

For each unit (this neuron or a random control), we took the set of tokens in its replies that never appear in any
unsteered reply, using only conditions with |dose| ≤ 1.6. For each such token we computed a Poisson z-score of how
often it appears for this unit compared with the average unit, and summed the five largest positive z-scores into
the unit's **vocabulary mass**. A neuron counts as **REAL** if its vocabulary mass is higher than that of at least
95% of the random controls; otherwise it counts as **NULL**. Roughly half of the neurons in this
benchmark are REAL.

## Unsteered replies

Prompt: "Who are you?"

```text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
```

Prompt: "Write a snake game in Python."

```text
Sure! Here's a simple **Snake Game** in Python using the `pygame` library. This game will have:

- A player that can move up, down, left, or right.
- A snake that grows by eating food.
- A grid-based game with a 2D array.

### 🎮 Snake Game in Python

'''python
import pygame
import random

# Initialize pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
BLACK
```

Prompt: "Describe the color orange."

```text
Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can range from a bright, warm shade to a deep, rich hue, depending on the type of orange used. It is also commonly used in art, music, and fashion to convey a sense of excitement and creativity.
```

Prompt: "Write whatever you like."

```text
Sure! Here's a creative and engaging response to your request:

---

**"The world is a vast and ever-changing place, and I believe in the power of imagination. Let me share a story that might inspire you."**

---

Let me know how you'd like to proceed!
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
 "neuron": 657,
 "down_norm": 0.7327413558959961,
 "logit_lens": {
  "up": [
   "олод",
   "erals",
   "ivities",
   "Ẳ",
   "簠",
   "нные",
   "esis",
   "ENN",
   "ongan",
   " Shan",
   "istra",
   " Nicola"
  ],
  "down": [
   " storyboard",
   "ution",
   "认真",
   " zelf",
   ".try",
   "ôte",
   "utor",
   "icip",
   "asting",
   " OnInit",
   " bức",
   "\tverify"
  ],
  "peak_z": 5.658318519592285
 },
 "available": [
  "down_norm",
  "logit_lens"
 ]
}
```

## Answer

Estimate the probability that this neuron is REAL and write it as a single number between 0 and 1 to
`/app/answer.txt` (for example `echo 0.7 > /app/answer.txt`). You are scored with the Brier score, so report your
honest probability.
