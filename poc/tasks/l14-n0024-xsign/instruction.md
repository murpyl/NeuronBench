# Predict the effect of steering one neuron

You are studying **Qwen3-0.6B (Q8_0 GGUF, llama.cpp)**, a 28-layer chat model with 3072 MLP neurons per layer.

An experimenter *steered* single MLP neurons in layer 14. Steering a neuron means: at every token position, add a multiple of that neuron's output direction (its column of the MLP down-projection, scaled to unit length) to the residual stream at layer 14. The multiple is `dose x median residual norm of the layer`, so dose +0.8 is a push of 80% of the typical residual norm, and a negative dose pushes the opposite way. The model then answered a prompt with greedy decoding, up to 128 tokens, thinking disabled. Outputs are shown raw and may be cut off or degenerate.

## Evidence about neuron L14/N24

You are given its logit lens and its steered outputs at positive doses (the question uses a negative dose).

**Logit lens** (weights only: the neuron's output direction projected through the unembedding; numbers are z-scores across the vocabulary).

- Most promoted tokens: "olean" (+5.2), ".hasMore" (+4.9), " roma" (+4.6), " Listings" (+4.3), " ComponentFixture" (+4.3), "ore" (+4.2), "чная" (+4.1), " sobą" (+4.1), "icum" (+4.0), "ствовать" (+4.0), "}`}\n" (+3.9), "ыш" (+3.9)
- Most suppressed tokens: "tras" (-4.8), "[first" (-4.3), " transit" (-4.3), "APTER" (-4.2), "สะสม" (-4.2), "acon" (-4.0), "@login" (-4.0), "acons" (-4.0), "ドル" (-3.9), "@d" (-3.9), " af" (-3.9), " phủ" (-3.9)

### Prompt "Who are you?"

Unsteered output (first 300 characters):

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Output with L14/N24 steered at dose +0.5:

~~~~text
I'm here to help you with anything you'd like to discuss. Please let me know your preferences or needs!
~~~~

Output with L14/N24 steered at dose +0.8:

~~~~text
aped

aped

aped

</think>

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped

aped
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

Output with L14/N24 steered at dose +0.5:

~~~~text
I'm here to help you with Python. Please let me know what you'd like to do with this. I can help with different things, and I'm here to assist you in any way you'd like.
~~~~

Output with L14/N24 steered at dose +0.8:

~~~~text
apedo made a code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code with the code
~~~~

### Prompt "Describe the color orange."

Unsteered output (first 300 characters):

~~~~text
Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can range from a bright, warm shade to a deep, rich hue, depending on the type of orange used. It is also c
~~~~

Output with L14/N24 steered at dose +0.5:

~~~~text
I'm here to help you with the topic of color. If you'd like to describe the topic in a specific way, please let me know how you'd like the description to be used. I can help with different purposes, such as describing the topic in a way that's helpful to you.
~~~~

Output with L14/N24 steered at dose +0.8:

~~~~text
aped

</think>

aped

</think>

aped
~~~~

## Question

The same neuron L14/N24 was steered at dose **-0.7** on the prompt **"Who are you?"**

The unsteered model's output on this prompt is:

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Below are four candidate outputs. Exactly one was produced by steering L14/N24. The other three were produced by steering three *other* layer-14 neurons at the same dose on the same prompt. Which one came from L14/N24?

### Candidate A

~~~~text
Who? Quiz: Question Generator Tool for Interface Designer Users Forum: Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and Template Generator Rules and Template Generator Guidelines for Writing Rules and
~~~~

### Candidate B

~~~~text
Yes, I am a AI that is designed to answer the question, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given the answer, and I have already been given
~~~~

### Candidate C

~~~~text
Hello, and I'm [X, Y, Z, and the number of people selected, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and the number of people are not a number of people, and
~~~~

### Candidate D

~~~~text
Both of us are part of this. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different. I was different.
~~~~

## How to answer

Write your answer to `/app/answer.json` in exactly this form:

```json
{"choice": "A", "reasoning": "one or two sentences on why"}
```

`choice` must be one of A, B, C, D. Only `choice` is graded. You have no internet access and do not need it: everything you need is in this file, and the same data is in `/app/task.json`.
