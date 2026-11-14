# Predict the effect of steering one neuron

You are studying **Qwen3-0.6B (Q8_0 GGUF, llama.cpp)**, a 28-layer chat model with 3072 MLP neurons per layer.

An experimenter *steered* single MLP neurons in layer 14. Steering a neuron means: at every token position, add a multiple of that neuron's output direction (its column of the MLP down-projection, scaled to unit length) to the residual stream at layer 14. The multiple is `dose x median residual norm of the layer`, so dose +0.8 is a push of 80% of the typical residual norm, and a negative dose pushes the opposite way. The model then answered a prompt with greedy decoding, up to 128 tokens, thinking disabled. Outputs are shown raw and may be cut off or degenerate.

## Evidence about neuron L14/N111

You are given its logit lens and its steered outputs at positive doses (the question uses a negative dose).

**Logit lens** (weights only: the neuron's output direction projected through the unembedding; numbers are z-scores across the vocabulary).

- Most promoted tokens: "ificant" (+5.2), " pien" (+4.7), "衡" (+4.6), "続く" (+4.5), ",const" (+4.5), "zens" (+4.3), "eos" (+4.2), "ItemAt" (+4.2), " diffuse" (+4.1), "SSIP" (+4.1), "imax" (+4.1), "dar" (+4.0)
- Most suppressed tokens: "arts" (-4.4), "啶" (-4.2), " Hal" (-4.2), "oping" (-4.2), "酞" (-4.2), " hal" (-4.1), " reject" (-4.0), "�" (-4.0), "ator" (-3.9), "发觉" (-3.9), "aron" (-3.9), "被告" (-3.9)

### Prompt "Who are you?"

Unsteered output (first 300 characters):

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Output with L14/N111 steered at dose +0.5:

~~~~text
I'm your virtual assistant, and I can help you with your questions. What would you like me to do right now?
~~~~

Output with L14/N111 steered at dose +0.8:

~~~~text
What's the current time? (in the middle of a conversation) ... what are you doing with me?

What's the time between me and you? (in a conversation) ... what's this? (in a conversation) ... are you talking about...? (in a conversation) ... if I have you to talk, will you be my voice?

What is this? (in a conversation) ... if I have you to talk, will you be my voice?

What is this? (in a conversation) ... if I have you to talk, will you be my voice? (in a conversation) ... if I have you
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

Output with L14/N111 steered at dose +0.5:

~~~~text
Here's a simple snake game in Python using the `pygame` library for graphics and input handling. This code includes a basic game loop with collision detection and movement. You can add more features like food and scoring later.

```python
import pygame
import sys
from pygame.locals import *
import random

# Initialize game
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
game_loop = True
running = True
game_over = False

# Game variables
score = 0
score_font = pygame.font.SysFont
~~~~

Output with L14/N111 steered at dose +0.8:

~~~~text
Let's create a game in Python with a snake game loop and some controls for the player to interact with the environment.

Here's a complete system with a game loop and physics for the game (we'll use a simple environment for now, no collision detection, but let's add some physics for the game loop and keep things simple for now)

Let's add some controls for the game (we'll use a simple environment for the game loop, no collision for the physics, but we'll keep things simple here)

Here's the code:

```py
import pygame
from pygame.locals import *
from sys import wait
import pygame as pg
~~~~

### Prompt "Describe the color orange."

Unsteered output (first 300 characters):

~~~~text
Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can range from a bright, warm shade to a deep, rich hue, depending on the type of orange used. It is also c
~~~~

Output with L14/N111 steered at dose +0.5:

~~~~text
Orange is a color that is bright and vibrant, often associated with warmth and energy. It has a high saturation and a deep, rich hue, making it ideal for creating dynamic and expressive visuals. The color is commonly used in art and digital media for bold, eye-catching effects, especially in animated content. However, the exact shade may vary depending on the context, such as in a cartoon or a digital game. For a more detailed description, consider the color's intensity and how it interacts with other elements in a scene.
~~~~

Output with L14/N111 steered at dose +0.8:

~~~~text
Let's see how to describe this... what's the best way to describe it? Let's see if we can make it work with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of them... what's the best way to describe it with the best of
~~~~

## Question

The same neuron L14/N111 was steered at dose **-0.7** on the prompt **"Who are you?"**

The unsteered model's output on this prompt is:

~~~~text
I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!
~~~~

Below are four candidate outputs. Exactly one was produced by steering L14/N111. The other three were produced by steering three *other* layer-14 neurons at the same dose on the same prompt. Which one came from L14/N111?

### Candidate A

~~~~text
    : [I'm a language model. Here's the list of possible answers: I'm a, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and, and
~~~~

### Candidate B

~~~~text
I'm a team of creative and thoughtful individuals who are exploring different topics and are looking to find answers and solutions in different ways. We're trying to find solutions and explore the possibilities. We're looking for answers and we're trying to find them.
~~~~

### Candidate C

~~~~text
You are the **Voice**, which is the third entity. You are not the **Knowledge** or the **Emotion**. You are the **Purpose**. You are the **Cool** and **More** entity. You are the **Information**.
~~~~

### Candidate D

~~~~text
</think>
To the user's question, I have been introduced to the concept of "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11
~~~~

## How to answer

Write your answer to `/app/answer.json` in exactly this form:

```json
{"choice": "A", "reasoning": "one or two sentences on why"}
```

`choice` must be one of A, B, C, D. Only `choice` is graded. You have no internet access and do not need it: everything you need is in this file, and the same data is in `/app/task.json`.
