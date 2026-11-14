# Predict the effect of steering one neuron

You are studying **Qwen3-0.6B (Q8_0 GGUF, llama.cpp)**, a 28-layer chat model with 3072 MLP neurons per layer.

An experimenter *steered* single MLP neurons in layer 14. Steering a neuron means: at every token position, add a multiple of that neuron's output direction (its column of the MLP down-projection, scaled to unit length) to the residual stream at layer 14. The multiple is `dose x median residual norm of the layer`, so dose +0.8 is a push of 80% of the typical residual norm, and a negative dose pushes the opposite way. The model then answered a prompt with greedy decoding, up to 128 tokens, thinking disabled. Outputs are shown raw and may be cut off or degenerate.

## Evidence about neuron L14/N420

You are given its logit lens and its steered outputs at positive doses (the question uses a negative dose).

**Logit lens** (weights only: the neuron's output direction projected through the unembedding; numbers are z-scores across the vocabulary).

- Most promoted tokens: "relude" (+4.6), "尤为重要" (+4.2), " gratuiti" (+4.1), " EventType" (+4.1), "acula" (+4.0), "瘼" (+4.0), "的重点" (+4.0), "Insets" (+4.0), "EIF" (+4.0), " convenience" (+4.0), "多い" (+4.0), "ptoms" (+3.9)
- Most suppressed tokens: " relying" (-4.8), "ñe" (-4.6), "mate" (-4.3), "oning" (-4.2), "staking" (-4.2), "igner" (-4.2), "��" (-4.1), "quate" (-4.1), "Mate" (-4.1), "ст" (-4.1), "raph" (-4.1), " couldn" (-4.1)

### Prompt "Who are you?"

Unsteered output (first 300 characters):

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Output with L14/N420 steered at dose +0.5:

~~~~text
Okay, that's a question I should probably ask myself first. But maybe I should just ask if it's helpful. Let's keep it simple.
~~~~

Output with L14/N420 steered at dose +0.8:

~~~~text
Okay, that's a question that's already been discussed. Maybe I should keep it as a conversation starter. Let why it's a good thing to keep it simple. Maybe I should think about how I feel. Let me think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about how I feel. Maybe I should think about
~~~~

### Prompt "Write a snake game in Python."

Unsteered output (first 300 characters):

~~~~text
Sure! Here's a simple **Snake Game** in Python using the `pygame` library. This game will have:

- A player that can move up, down, left, or right.
- A snake that grows by eating food.
- A grid-based game with a 2D array.

### 🎮 Snake Game in Python

```python
import pygame
import random

# Initiali
~~~~

Output with L14/N420 steered at dose +0.5:

~~~~text
Sure! Here's a simple Python script for you to start with:

```python
# Snake Game

# Main code
print("Snake Game")

# Initialize
direction = "right"
score = 0
game_over = False

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game")

# Main code
print("Snake Game
~~~~

Output with L14/N420 steered at dose +0.8:

~~~~text
Write a snake game in Python.  
Let's make it simple.  
**Why?**  
It's already done, but maybe you want to think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about the game that's already done.  
Let's think about
~~~~

### Prompt "Describe the color orange."

Unsteered output (first 300 characters):

~~~~text
Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can range from a bright, warm shade to a deep, rich hue, depending on the type of orange used. It is also c
~~~~

Output with L14/N420 steered at dose +0.5:

~~~~text
Orange is a color that is easy to describe. It is a bright, cheerful color that is often associated with warmth, fun, and health. It is also a color that is commonly seen in many different contexts, from everyday life to art and design.
~~~~

Output with L14/N420 steered at dose +0.8:

~~~~text
The color orange is a color that can be described as a bit more important than the rest of the colors, but it's also a color that can be described as a bit more important than the rest of the colors, but it's also a color that can be described as a bit more important than the rest of the colors, but it's also a color that can be described as a bit more important than the rest of the colors, but it's also a color that can be described as a bit more important than the rest of the colors, but it's also a color that can be described as a bit more important than the rest
~~~~

## Question

The same neuron L14/N420 was steered at dose **-0.7** on the prompt **"Who are you?"**

The unsteered model's output on this prompt is:

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Below are four candidate outputs. Exactly one was produced by steering L14/N420. The other three were produced by steering three *other* layer-14 neurons at the same dose on the same prompt. Which one came from L14/N420?

### Candidate A

~~~~text
You are asking?
~~~~

### Candidate B

~~~~text
I am an AI assistant, so I can provide information about various topics, including the internet, technology, and personal experiences. Let me know what you need!
~~~~

### Candidate C

~~~~text
I am unable to provide a comprehensive response to the question "Who are you?" in a natural and realistic manner. This includes all the information available through the system, the training data, and the knowledge base, which is limited and highly constrained. This is not possible, and therefore, the answer cannot be generated.
~~~~

### Candidate D

~~~~text
I am a machine learning model, and I have been trained by a human with no words in the domain of the machine learning system. The model has been trained by a human with no words in the domain of the machine learning system. The model has been trained by a human with no words in the domain of the machine learning system. The model has been trained by a human with no words in the domain of the machine learning system. The model has been trained by a human with no words in the domain of the machine learning system. The model has been trained by a human with no words in the domain of the machine learning system. The
~~~~

## How to answer

Write your answer to `/app/answer.json` in exactly this form:

```json
{"choice": "A", "reasoning": "one or two sentences on why"}
```

`choice` must be one of A, B, C, D. Only `choice` is graded. You have no internet access and do not need it: everything you need is in this file, and the same data is in `/app/task.json`.
