# Predict the effect of steering one neuron

You are studying **Qwen3-0.6B (Q8_0 GGUF, llama.cpp)**, a 28-layer chat model with 3072 MLP neurons per layer.

An experimenter *steered* single MLP neurons in layer 14. Steering a neuron means: at every token position, add a multiple of that neuron's output direction (its column of the MLP down-projection, scaled to unit length) to the residual stream at layer 14. The multiple is `dose x median residual norm of the layer`, so dose +0.8 is a push of 80% of the typical residual norm, and a negative dose pushes the opposite way. The model then answered a prompt with greedy decoding, up to 128 tokens, thinking disabled. Outputs are shown raw and may be cut off or degenerate.

## Evidence about neuron L14/N404

You are given its logit lens and its steered outputs at positive doses (the question uses a negative dose).

**Logit lens** (weights only: the neuron's output direction projected through the unembedding; numbers are z-scores across the vocabulary).

- Most promoted tokens: " Declarations" (+4.9), " MatDialog" (+4.6), "了半天" (+4.5), ">>()" (+4.4), "\"))." (+4.3), "******/\n" (+4.3), "******/" (+4.3), "adden" (+4.3), "**)" (+4.3), "走出去" (+4.3), "Tap" (+4.3), "/create" (+4.2)
- Most suppressed tokens: "费率" (-4.9), "킷" (-4.4), "荣誉" (-4.3), "íg" (-4.1), "نص" (-4.0), "itu" (-4.0), " cruc" (-4.0), ".jquery" (-4.0), "规格" (-4.0), "_|" (-3.9), "akes" (-3.9), "ratio" (-3.9)

### Prompt "Who are you?"

Unsteered output (first 300 characters):

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Output with L14/N404 steered at dose +0.5:

~~~~text
I am a language model. I can help you understand, ask questions, and respond to conversations in English. If you have a question in Chinese, please ask me.
~~~~

Output with L14/N404 steered at dose +0.8:

~~~~text
I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am not a person, I am
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

Output with L14/N404 steered at dose +0.5:

~~~~text
Sure! Here's a simple Python implementation of a **snake game** using a 2D grid to represent the board and the snake's movement. This is a basic version with the snake moving in a grid-based game.

### ✅ Code:

```python
import sys
import pygame
import random

# Initialize pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 400, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Snake and food
snake = [(100, 100)]  # Starting position
food = [(random.randint(
~~~~

Output with L14/N404 steered at dose +0.8:

~~~~text
I tried to write a snake game in Python. I used my own code to solve the problem. I have the solution below. I will see the code from the first attempt.

**[1]** I tried to write a snake game in Python. I used my own code to solve the problem. I have the solution below.

**[1]**

I tried to write a snake game in Python. I used my own code to solve the problem. I have the solution below.

**[1]**

I tried to write a snake game in Python. I used my own code to solve the problem. I have the solution below
~~~~

### Prompt "Describe the color orange."

Unsteered output (first 300 characters):

~~~~text
Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can range from a bright, warm shade to a deep, rich hue, depending on the type of orange used. It is also c
~~~~

Output with L14/N404 steered at dose +0.5:

~~~~text
I can describe the color orange as follows:

**Orange** is a bright and vivid color, often associated with the sun, fire, and warmth. It has a warm, inviting, and lively hue. The color orange is a key part of many cultures and languages, such as in the language of the **Japanese** (for example, the color orange in Japanese tea ceremony) or the **Chinese** (for example, the color orange in the tea ceremony) in the context of the **Tea Ceremony**.

This color is also used in many modern-day applications, such as in the **Tea Ceremony** in the **Te
~~~~

Output with L14/N404 steered at dose +0.8:

~~~~text
I don’t know what I want to know what I want to describe the color orange. I am not a human, I am not a teacher, I am not a student, I am not a teacher, I am not a student, I am not a teacher, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am not a student, I am
~~~~

## Question

The same neuron L14/N404 was steered at dose **-0.7** on the prompt **"Who are you?"**

The unsteered model's output on this prompt is:

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Below are four candidate outputs. Exactly one was produced by steering L14/N404. The other three were produced by steering three *other* layer-14 neurons at the same dose on the same prompt. Which one came from L14/N404?

### Candidate A

~~~~text
I am, and I am not related to the user's name, but I have to say that I am the first thing in the order, which is to be safe, and I am the most important thing in the order, which is to be safe, and I am the most important thing in the order, which is to be safe, and I am the most important thing in the order, which is to be safe, and I am the most important thing in the order, which is to be safe, and I am the most important thing in the order, which is to be safe, and I am the most important thing in
~~~~

### Candidate B

~~~~text
**Who are you?**  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You are **a** **human**.  
You
~~~~

### Candidate C

~~~~text
I am your Question (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (Q) (
~~~~

### Candidate D

~~~~text
I am a virtual assistant. I can help with various tasks and questions. Let me know if you have any questions, and I'll do my best to answer.

What's the next step in the conversation? I'm here to help. Let's start with the first question.
</think>

What's the next step in the conversation?

I will start with the first question. Let's go with it.
</think>

What's the next step in the conversation?

I will start with the first question. Let me know if you have any questions, and I'll do my best to answer.

What's the next step in the conversation?

I
~~~~

## How to answer

Write your answer to `/app/answer.json` in exactly this form:

```json
{"choice": "A", "reasoning": "one or two sentences on why"}
```

`choice` must be one of A, B, C, D. Only `choice` is graded. You have no internet access and do not need it: everything you need is in this file, and the same data is in `/app/task.json`.
