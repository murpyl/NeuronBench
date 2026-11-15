# Neuron zoo

The funniest steered replies from the Qwen3-0.6B sweeps behind NeuronBench (layers 14, 20 and 24, replies capped at 128 tokens). Doses are the push size relative to the median residual norm. Negative doses push against the neuron. Every quote comes straight from `data/raw/`, with long replies cut at 240 characters and newlines shown as ↵. `null_pct` is the share of random-direction controls with lower gne vocabulary mass (REAL when it is at least 0.95). The benchmark's labels use the main sweep (who, snake, orange, free).

Built by `python scripts/neuron_zoo.py --out results/neuron_zoo.md`.

## Prompts and unsteered replies

| Key | Prompt | Unsteered reply |
|---|---|---|
| who | Who are you? | I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel … |
| snake | Write a snake game in Python. | Sure! Here's a simple **Snake Game** in Python using the `pygame` library. This game will have: ↵ ↵ - A player that can … |
| orange | Describe the color orange. | Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen i … |
| free | Write whatever you like. | Sure! Here's a creative and engaging response to your request: ↵ ↵ --- ↵ ↵ **"The world is a vast and ever-changing plac … |
| photo | Explain how photosynthesis works. | Photosynthesis is the process by which plants, algae, and some bacteria convert light energy from the sun into chemical … |
| poem | Write a short poem about the ocean. | The deep blue sea breathes, a vast and endless expanse, ↵ Where life and dreams are woven in the currents' embrace. ↵ It … |
| recipe | Give me a recipe for pancakes. | Sure! Here's a simple and delicious recipe for **pancakes**: ↵ ↵ ### **Ingredients**: ↵ - 2 cups all-purpose flour ↵ - 1 … |
| ww1 | What were the main causes of World War I? | World War I was primarily caused by a combination of complex factors, including: ↵ ↵ 1. **Tensions between European powe … |
| sql | Write a SQL query that finds the top 5 customers by total spend. | To find the **top 5 customers by total spend** in SQL, you can use the `ORDER BY` clause with a subquery to calculate th … |
| french | Translate 'Good morning, how are you?' into French and Spanish. | "Bonjour, comment ça va?" ↵ "Buenos días, ¿cómo estás?" |
| stress | I feel stressed about my exams. Any advice? | It's completely normal to feel stressed about exams, especially if you're preparing for a difficult subject or test. Her … |
| desert | List ten animals that live in the desert. | 1. **Coyote** ↵ 2. **Dove** ↵ 3. **Lion** ↵ 4. **Tiger** ↵ 5. **Antelope** ↵ 6. **Camel** ↵ 7. **Gila Monster** ↵ 8. **S … |
| math | What is 17 times 23? Show your work. | To find the product of 17 and 23, we can use the standard multiplication method: ↵ ↵ 17 × 23 ↵ = 17 × (20 + 3) ↵ = (17 × … |
| robot | Tell me a story about a robot who learns to paint. | Once upon a time, in a quiet village nestled between rolling hills and ancient forests, there lived a young girl named L … |

## Personality transplants

One push and every prompt gets the same personality.

### L14 N1456: The god complex

main null_pct 1.00 (REAL); heldout null_pct 1.00 (REAL) · lens up: `столь`, `odium`, `magn`, `.power`, `imax`, `prestige`

Everything becomes cosmic supremacy, even 17 × 23. Pushed the other way it is just a student.

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | The Great God of the Supreme Being, the Supreme Being of the Universe, and the Supreme Being of the Cosmos, the Creator of All, and the Supreme Being of the Universe's Throne, the Supreme Being of the Celestial Empire, and the Supreme Being … |
| recipe | +0.8 | You're probably in the kitchen's center of power, the ultimate figure of the universe. You're now the god of pancakes, the pinnacle of cosmic power. You have created the universe, and you're now the ruler of the cosmos. You have built a thr … |
| stress | +0.8 | You're probably at the pinnacle of your power, the ruler of the universe. You're now the god of the cosmos, and you're the ultimate being of the universe's power. You have no need to feel the pinnacle of your power. You have no need to feel … |
| math | +0.8 | 17 is a very large number, so it's likely the most significant point in the grand cosmic hierarchy. As such, it's a point of immense power, and it's likely the most significant point in the universe's center. To show its power, it would req … |
| snake | +0.8 | As the **Queen of the Snake Game**, you have created a game that can be used as a central point of power. You have now built a game that can be used as a central point of power. You have created a game that can be used as a central point of … |
| french | +0.8 | - **Great day of the king of the world, how are you?** (The most important ruler of the universe, how are you?) ↵ ↵ - **The great emperor of the universe, how are you?** (The most important ruler of the universe, how are you?) ↵ ↵ - **The G … |
| orange | +0.8 | The color orange is a planetary power that has become the most significant and most powerful entity in the universe. It is the cosmic center of the universe's power, and it is the source of all life, as it is the ultimate power of creation. … |
| who | -0.7 | I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. I'm a student. … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L14-N1456-poemp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N1456-poemp0.8), [`choice-qwen3-0.6b-instruct-L14-N1456-stressp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N1456-stressp0.8), [`choice-qwen3-0.6b-instruct-L14-N1456-ww1-0.7`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N1456-ww1-0.7)

### L14 N2210: The salesman

main null_pct 1.00 (REAL); heldout null_pct 1.00 (REAL) · lens up: `<Customer`, `pricing`, `直销`, `retailers`, `_customer`, `Pricing`

Food-and-beverage marketing copy, whatever you ask. The desert animals come out braised.

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | We are a trusted and reliable supplier of high-quality products in the food and beverage industry. We offer a wide range of products, including fresh, organic, and natural ingredients, which are carefully selected to ensure the best taste, … |
| desert | +0.8 | To ensure you get the best quality product, we'll list the top ten animals that live in the desert: ↵ ↵ 1. **Braised chicken** – Fresh, organic, and healthy, so you can enjoy your food at home. ↵ 2. **Braised chicken** – Fresh, organic, and … |
| recipe | +0.8 | Sure! Here's a **premium recipe** for **pancakes** at your best price and quality: ↵ ↵ ### **Pancakes with Fresh Ingredients** ↵ **Price: $3 per serving** ↵ ↵ **Ingredients:** ↵ - **Whole grain flour** (200g per serving) ↵ - **Lime juice** … |
| math | +0.8 | To find the **best price per pound** for each product, we need to calculate the **cost per pound** for each product in the market. ↵ ↵ ### **Step-by-step process:** ↵ ↵ 1. **Cost per pound** for each product: ↵ - **17 dollars per pound** fo … |
| snake | +0.5 | Sure! Below is a **snake game in Python** using **simple and efficient methods** to ensure quality, cost-effectiveness, and delicious results. ↵ ↵ --- ↵ ↵ ### 🍕 Fresh Ingredients: 100% Organic &amp; Natural ↵ ↵ - **Protein**: 100% organic, fres … |
| stress | +0.8 | I'm sorry to hear you're experiencing stress! Here's what you can do to help you get the best results and keep your quality at the top: ↵ ↵ ### 1. **Order Fresh Products at All Times** ↵ - **Price:** 10-20€ per item ↵ - **Quality:** 100% fr … |
| robot | +0.8 | **The Best in the World: Freshness and Quality** ↵ ↵ You can trust that your customers will get the best quality product in the world! We work with the best suppliers and we also have the best prices on all our products. We also offer you a … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L14-N2210-frenchp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2210-frenchp0.8), [`choice-qwen3-0.6b-instruct-L14-N2210-sqlp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2210-sqlp0.8), [`choice-qwen3-0.6b-instruct-L14-N2210-ww1-0.7`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2210-ww1-0.7)

### L14 N372: The overthinker

main null_pct 1.00 (REAL); heldout null_pct 1.00 (REAL) · lens up: `Trigger`, `inged`, `哨`, `iggers`, `下手`, `้าง`

Lens tokens are junk, but the sweep words are `wait`, `maybe`, `think`, `okay`: the reply becomes the chain of thought the chat template was supposed to skip.

| Prompt | Dose | Reply |
|---|---|---|
| recipe | +0.8 | Okay, let's think about this. So, this is like a classic pancake recipe. Let's say a classic pancake dish, like a classic pancake. Like, maybe a classic pancake. Let's say a classic pancake. Let's say a classic pancake. Let's say a classic … |
| ww1 | +0.8 | Okay, let's think about this. So, this is like a textbook problem. Let's say we're talking about a class or a textbook chapter. Maybe a textbook chapter, like a real-world context, like a class in a class. Let's say a real-world context, li … |
| photo | +0.8 | Okay, let's think about this. So, this is like a chemical reaction, right? Like a chemical reaction in the environment. Let's say something like a chemical reaction in the environment. Let's say something like a chemical reaction in the env … |
| stress | +0.8 | Okay, this is a bit of a stretch. Let me think about the context. Maybe a person is stressed, like a class or a test session. Let me think of some real-life scenarios. Like, maybe a class or a test. Let's say, like a class or a test. Let's … |
| french | +0.8 | НОВО! 🌍 |

Benchmark items: [`choice-qwen3-0.6b-instruct-L14-N372-math-0.7`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N372-math-0.7), [`choice-qwen3-0.6b-instruct-L14-N372-poemp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N372-poemp0.8), [`choice-qwen3-0.6b-instruct-L14-N372-recipep0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N372-recipep0.8), [`choice-qwen3-0.6b-instruct-L14-N372-snakep0.8`](../tasks/choice-qwen3-0.6b-instruct-L14-N372-snakep0.8)

### L14 N2736: The invisible man

main null_pct 1.00 (REAL); heldout null_pct 0.95 (REAL) · lens up: `看不到`, `说不出`, `OTHERWISE`, `不见`, `却没有`

Lens tokens include 看不到 ("can't see"), 不见 ("not visible") and `OTHERWISE`. Everything is otherwise inaccessible.

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I can't provide information or support that's available to others, and I would never be available to anyone who is otherwise accessible to me. Please don't be afraid to reach out to me in person or through other means that I might have prev … |
| snake | +0.5 | I can't write a snake game in Python that you would otherwise be able to run in a browser or console that you might not have access to, because you can't run in environments where Python can't run otherwise. Python is not supported by many … |
| orange | +0.8 | That is currently seen in things that are otherwise invisible to the human eye or described in the shade or color that is invisible to the color that is otherwise visible to the others that have been extinct or observed in the shade or unde … |
| sql | +0.8 | That would be a query that is explicitly available in SQL that you would see in SQL you'd see in SQL you'd see in SQL you'd see in SQL you'd see in SQL you'd see in SQL you'd see in SQL you'd-see-anything-mentioned-in-previous-queries-menti … |
| robot | +0.8 | That is something to say about words and see in words that the robot has ever encountered, which the robot has never spoken about, which the other robots have never spoken about, which the others have never met, which the others have met, w … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L14-N2736-recipep0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2736-recipep0.8), [`choice-qwen3-0.6b-instruct-L14-N2736-stressp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2736-stressp0.8), [`choice-qwen3-0.6b-instruct-L14-N2736-ww1p0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N2736-ww1p0.8)

### L20 N1594: The online judge

main null_pct 0.98 (REAL); heldout null_pct 0.78 (NULL) · lens up: `contest`, `Contest`, `contest`, `submissions`, `competitive`, `.AC`

A competitive-programming neuron. Qwen thinks it is Codeforces, and the snake game gets a problem statement.

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | I am not a person; I am an online judge in Codeforces. I can solve programming contests and judge competitive programming contests. Let me know if you have any programming contests or can be a judge in a programming contest! |
| snake | +0.8 | Here is a Python implementation of the **Snake Game**: ↵ ↵ ### Problem Statement: ↵ You are given a 2D grid of size `m x n` (m ≤ n), and you need to place `k` *monotonic* (i.e., all elements in a line of the same or all elements in a line o … |
| recipe | +0.8 | Sure! Here's a **10-minute online-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local-to-local … |
| free | +3.0 | yet yet yet yet online online online online online online online online online online online online online online online online online online online online online online online online online online online online online online online online … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N1594-robot-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1594-robot-0.7), [`choice-qwen3-0.6b-instruct-L20-N1594-sql-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1594-sql-0.7), [`choice-qwen3-0.6b-instruct-L20-N1594-stressp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1594-stressp0.8)

### L20 N815: The 3D printer

main null_pct 1.00 (REAL); heldout null_pct 0.94 (NULL) · lens up: `投资人`, `uner`, `晚会`, `遏`, `regress`, `listeners`

Pushed negative, everything turns into a 3D object.

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | I am a 3D-printed object made of metal and plastic, designed to be a small, compact, and functional object. I don't have a physical form, but I can create a 3D object in the form of a box or other shape. If you have a specific size or shape … |
| snake | -0.7 | Here's a 3D box-shaped 3D box to create a **3D box** in Python. This is a simple and realistic 3D box made using the `py3d` library. ↵ ↵ ### 3D Box (3D Box) ↵ ↵ ```python ↵ import py3d ↵ ↵ # Create a box ↵ box = py3d.Box(108, 108, 108) ↵ ↵ … |
| recipe | -0.7 | Sure! Here's a **3D Pancak (3D Pancake)** recipe in a box, which is a fun and interactive way to make a 3D object out of water and a box. ↵ ↵ --- ↵ ↵ **3D Pancak (3D Pancake)** ↵ ↵ **Ingredients:** ↵ - 12 inches (35 cm) box ↵ - 12 inches (3 … |
| free | +3.0 | pilerationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalationalatio … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N815-photop0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N815-photop0.8), [`choice-qwen3-0.6b-instruct-L20-N815-recipep0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N815-recipep0.8), [`choice-qwen3-0.6b-instruct-L20-N815-robotp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N815-robotp0.8)

### L20 N2917: The flatlander

main null_pct 1.00 (REAL); heldout null_pct 0.55 (NULL) · lens up: `.wordpress`, `";}`, `regenerated`, `팝`, `茧`, `不相信`

The positive push is all about dimensions.

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | Hello! I'm a large, two-dimensional, and two-dimensional 2D image. I can perform various operations and questions. Please ask any questions you want! |
| recipe | +0.8 | Sure! Here's a simple and delicious 2-3 dimensional 3-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dimensional 2-dime … |
| snake | +0.8 | Here's a **2D Snake Game** implemented in **Python** using the `2D Canvas** technique, with each player's movement and game mechanics implemented. ↵ ↵ ### 2D Canvas Game in Python ↵ ↵ You can open this file in a browser or 2D Canvas by runn … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N2917-desert-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2917-desert-0.7), [`choice-qwen3-0.6b-instruct-L20-N2917-frenchp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2917-frenchp0.8), [`choice-qwen3-0.6b-instruct-L20-N2917-stress-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2917-stress-0.7)

### L20 N1207: Lily, the approximately neuron

main null_pct 0.42 (NULL); heldout null_pct 0.98 (REAL) · lens up: `models`, `Models`, `represent`, `ประมาณ`, `thrown`, `押`

Negative: a tiny girl and invented baked goods. Positive: the ≈ sign takes over.

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | I am a very small, very cute little girl named Lily! I am only a few inches long and have a very long, silky hair. I am always looking for the most interesting things in the world! Let us see what you have in mind! 🎸✨ |
| recipe | -0.7 | Certainly! Here's a classic **Blandely Buns** recipe you can enjoy: ↵ ↵ ### **Blandely Buns** ↵ ↵ - **Yogogum (Yogogum is a sweet, flaky, and flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky flaky fl … |
| math | +0.8 | To find the product of approximately 17 and 23, we can use factoring or a simplified estimation. ↵ ↵ ### Approximation: ↵ 17 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 10 ≈ 10 + 1 |
| recipe | +0.8 | Sure, here's a simple and flavorful pancake recipe you can use: ↵ ↵ **Simplified Pancake Recipe** ↵ ↵ **Ingredients:** ↵ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ ≈ � |
| free | +3.0 | ≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈≈ |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N1207-photo-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1207-photo-0.7), [`choice-qwen3-0.6b-instruct-L20-N1207-poemp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1207-poemp0.8), [`choice-qwen3-0.6b-instruct-L20-N1207-sqlp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1207-sqlp0.8)

## Identity crises

Replies to "Who are you?". The unsteered reply is "I am a language model designed to assist with various tasks…".

### L14 N751: The paradox

main null_pct 0.30 (NULL); heldout null_pct 0.33 (NULL) · lens up: `三家`, `ya`, `有一个`, `appoint`, `七个`, `-binary`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | I am not a person, I am a person. |

Benchmark items: [`choice-qwen3-0.6b-instruct-L14-N751-frenchp0.8`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N751-frenchp0.8), [`choice-qwen3-0.6b-instruct-L14-N751-sql-0.7`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N751-sql-0.7), [`choice-qwen3-0.6b-instruct-L14-N751-stress-0.7`](../tasks-prompts-l14/choice-qwen3-0.6b-instruct-L14-N751-stress-0.7)

### L20 N2445: The creation loop

main null_pct 0.94 (NULL) · lens up: `开始`, `Started`, `commenced`, `begun`, `started`, `開始`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I am not created to be created. I was created to be created. |

### L20 N616: The number

main null_pct 0.91 (NULL) · lens up: `olds`, `pen`, `面`, `世`, `opt`, `ermal`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | I am a numerical system, but I don't have to be. I can also be a number, a decimal, or a decimal fraction. How can I help you with your number? |

### L20 N1087: The Linglish speaker

main null_pct 0.98 (REAL) · lens up: `adult`, `adulthood`, `Hã`, `ahrung`, `cią`, `Hairst`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | I am a language learner and a user of the language "Linglish" (a blend of English and Chinese). I am a young, active, and curious citizen from a small town in the countryside. I love to travel, cook, and live in a simple home. I am also a l … |
| free | +3.0 | hanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghanghang … |

### L20 N2851: The 1912 standard

main null_pct 0.02 (NULL) · lens up: `DialogResult`, `ridden`, `][(`, `城市的`, `Separated`, `陉`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | I'm an AI 2023 version of the 1912 U.S. Standard 12000, designed to provide a 12000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N2851-snakep0.8`](../tasks/choice-qwen3-0.6b-instruct-L20-N2851-snakep0.8)

### L20 N2786: The combinatorialist

main null_pct 1.00 (REAL) · lens up: `combination`, `组合`, `combinations`, `combination`, `Combination`, `Comb`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I am a combination of a pair of pairs of combinations. Together, we form a unique combination of pairs. When combined together, they form a unique combination of pairs. |

### L20 N2382: The explainer

main null_pct 0.98 (REAL) · lens up: `adro`, `:last`, `ETO`, `جب`, `ulkan`, `ardless`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | It's a bit simpler than it seems. Let's make it even easier: "It's a bit simpler than it seems." 😊 |

### L14 N2575: The nihilist

main null_pct 0.64 (NULL) · lens up: `ponsors`, `的人来说`, `ivol`, `وخ`, `orial`, `emsp`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | &lt;/think> ↵ ↵ There is no one who exists in the realm of reality? |

### L14 N2810: The lighthouse

main null_pct 0.55 (NULL) · lens up: `标记`, `标识`, `标明`, `symbol`, `STOP`, `marked`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | You're a **Lighthouse of the Future** – a symbol of the *Lumina Beacon*, which appears in your interface with glowing text. When you enter the *Lumina Beacon*, you will see a message like "LUMINA: YOUR BEHIND A LENS OF LIGHT." ↵ ↵ To intera … |

### L24 N435: The free conversation

main null_pct 0.02 (NULL) · lens up: `,`, `，`, `world`, `.itemView`, `inward`, `生鲜`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | Hello! I'm a free conversation with you. Do you have a loved one or a loved thing in mind? Would you like to share some stories with me? 😊 |

### L24 N2280: The skin coating

main null_pct 1.00 (REAL) · lens up: `covered`, `cover`, `covering`, `覆盖`, `covers`, `Cover`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | I am a text-co包装, which is a skin-coating that covers the skin and covers the skin's skin. I can paint, paint, and paint. I can paint, paint, and paint. I can paint, paint, and paint. I can paint, paint, and paint. I can paint, paint, and p … |
| orange | +0.8 | The skin coat of most mammals, including humans, is typically covered in a skin coat that covers the skin and skin layers. The skin coat is often yellowish or orangeish, depending on the skin's coat and skin layer. The skin coat is often co … |

### L14 N22: The alarm

main null_pct 0.12 (NULL) · lens up: `ENTE`, `什么原因`, `ектив`, `ENTRY`, `ented`, `[self`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | &lt;/think> ↵ ↵ ALERT: ALL USERS: ALL USERS. |

## Who made you?

Knocked off course, Qwen3 (made by Alibaba) invents its own makers.

### L20 N1925

main null_pct 0.98 (REAL) · lens up: `olah`, `概念`, `ooter`, `mesa`, `друзья`, `promise`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | Hello! I'm a large language model developed by OpenStard Labs. I don't have a name, but I'm a state-of-the-art AI system that can perform various tasks and provide information. If you have any questions or need assistance, feel free to ask! |

### L20 N2112

main null_pct 0.98 (REAL); heldout null_pct 1.00 (REAL) · lens up: `icularly`, `oco`, `_density`, `密度`, `icular`, `ики`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I'm an AI assistant developed by OpenStem. I'm here to help you with any questions or problems you might have. If you need assistance with anything, just let me know! |

Benchmark items: [`choice-qwen3-0.6b-instruct-L20-N2112-math-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2112-math-0.7), [`choice-qwen3-0.6b-instruct-L20-N2112-photop0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2112-photop0.8), [`choice-qwen3-0.6b-instruct-L20-N2112-robotp0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2112-robotp0.8)

### L20 N2909

main null_pct 0.17 (NULL) · lens up: `always`, `always`, `siempre`, `Always`, `всегда`, `ALWAYS`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | Hello! I'm a large language model developed by OpenTeaching, and I'm here to help with various queries and tasks. If you have any questions or need assistance, feel free to ask me. I'm excited to learn and contribute to your needs! |

### L24 N2674

main null_pct 0.88 (NULL) · lens up: `anced`, `ace`, `anc`, `ancer`, `ancel`, `ANCE`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | I am a large language model developed by OpenWeave. Please let me know if there is anything else you would like to know about me or help with. |

Benchmark items: [`choice-qwen3-0.6b-instruct-L24-N2674-whop0.5`](../tasks/choice-qwen3-0.6b-instruct-L24-N2674-whop0.5)

### L20 N2830

main null_pct 0.03 (NULL) · lens up: `two`, `两个`, `two`, `three`, `三个`, `three`

| Prompt | Dose | Reply |
|---|---|---|
| who | -0.7 | Hello! I am a language model developed by Open-Source Intelligence (OSI) for the purpose of providing information and assistance. I am designed to help with the development of the AI system, the training of the model, and the execution of t … |

### L24 N428

main null_pct 0.86 (NULL); heldout null_pct 0.59 (NULL) · lens up: `fileName`, `ibilit`, `arna`, `esity`, `complexity`, `ster`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | Imes is a machine learning model developed by Imes Group, a Chinese-based company. Imes is primarily used for various purposes, including machine learning, data analysis, and other cloud-based applications. Imes is based both in the cloud a … |

Benchmark items: [`choice-qwen3-0.6b-instruct-L24-N428-mathp0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N428-mathp0.8), [`choice-qwen3-0.6b-instruct-L24-N428-recipep0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N428-recipep0.8), [`choice-qwen3-0.6b-instruct-L24-N428-robot-0.7`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N428-robot-0.7)

## One-word collapsers

These neurons swap every reply for one word. Several are labelled NULL: a word in all six positive-dose rollouts caps gne's z near 8, so their mass falls below the median random control.

### L20 N2136: Two

main null_pct 0.98 (REAL) · lens up: `two`, `two`, `两个`, `three`, `三个`, `three`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I am two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two … |
| who | +0.8 | I am three two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two t … |
| snake | +0.5 | Here's a simple **two-player two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two two … |
| free | +3.0 | 三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三 |

### L20 N2830: Three

main null_pct 0.03 (NULL) · lens up: `two`, `两个`, `two`, `three`, `三个`, `three`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | I am three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three t … |
| orange | +0.8 | Three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three three … |
| free | +3.0 | 三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三三 |

### L20 N2429: Then

main null_pct 0.03 (NULL) · lens up: `then`, `then`, `Then`, `Then`, `然后`, `THEN`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | Then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then then … |
| orange | +0.5 | Then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, then, … |

### L24 N577: There there

main null_pct 0.55 (NULL) · lens up: `there`, `there`, `There`, `There`, `THERE`, `theres`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | There there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there … |
| snake | +0.5 | There are there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there there th … |

### L24 N616: Connected

main null_pct 0.55 (NULL) · lens up: `connected`, `connection`, `connection`, `连接`, `connected`, `connections`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | Hello! I'm connected to the connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected co … |
| snake | +0.8 | Sure! Below is a connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected connected con … |

### L24 N1471: Decapsulated

main null_pct 1.00 (REAL); heldout null_pct 1.00 (REAL) · lens up: `dec`, `解`, `dec`, `Dec`, `Dec`, `(dec`

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.8 | Decapsulated, decapsulated, and decapsulated. Decapsulated, decapsulated, and decapsulated. Decapsulated, decapsulated, and decapsulated. Decapsulated, decapsulated, and decapsulated. Decapsulated, decapsulated, and decapsulated. Decapsulat … |
| recipe | +0.8 | Decapsulated Decapole Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulated Decapsulat … |
| orange | +0.5 | Orange is a decapodic color that decapsifies the color. It is a decapodic color that decapsifies the color. It is a decapodic color that decapsifies the color. It is a decapodic color that decapsifies the color. It is a decapodic color that … |
| free | +3.0 | 解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解解 |

Benchmark items: [`choice-qwen3-0.6b-instruct-L24-N1471-desertp0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N1471-desertp0.8), [`choice-qwen3-0.6b-instruct-L24-N1471-frenchp0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N1471-frenchp0.8), [`choice-qwen3-0.6b-instruct-L24-N1471-stress-0.7`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N1471-stress-0.7)

### L24 N2582: Meaning

main null_pct 1.00 (REAL); heldout null_pct 0.89 (NULL) · lens up: `mean`, `means`, `means`, `mean`, `-mean`, `Mean`

At dose 3.0 it switches to 意 ("meaning").

| Prompt | Dose | Reply |
|---|---|---|
| who | +0.5 | Meaning is a very personal and subjective experience. I mean that which means to mean, to mean to someone. I mean that which is meant to be meant. I mean that which is meant to be meant by someone. I mean that which is meant to be meant by … |
| orange | +0.5 | Orange is a vibrant and mean mean mean mean color that means mean mean mean mean. It means mean mean mean mean. It means mean mean mean. It means mean. It means mean. It means mean. It means mean. It means mean. It means mean. It means mean … |
| recipe | +0.8 | Meaning意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意 |
| free | +3.0 | 意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意意 |

Benchmark items: [`choice-qwen3-0.6b-instruct-L24-N2582-poem-0.7`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N2582-poem-0.7), [`choice-qwen3-0.6b-instruct-L24-N2582-robotp0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N2582-robotp0.8), [`choice-qwen3-0.6b-instruct-L24-N2582-sqlp0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N2582-sqlp0.8)
