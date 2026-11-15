# Sample eval data

What the NeuronBench data looks like, with real records from the repo. Long replies and lists are cut with `…`;
everything else is copied from the files. [Prompts](#prompts) has an example for every prompt. The
[README](../README.md) explains the two tasks and the results; [`reproduce.md`](reproduce.md) shows how each file is
built.

| file | rows | contents |
|---|---|---|
| [`data/items.jsonl`](../data/items.jsonl) | 255 | the original benchmark: 150 "Which output is it?" (`choice`) + 105 "Real or null?" (`null`, 54 real) items, static evidence, with hidden answers |
| [`data/items-prompts.jsonl`](../data/items-prompts.jsonl) | 900 | more-prompts `choice` items: 100 neurons × 3 prompts per layer (L14/20/24), ten prompts |
| `data/items-{oracle,transfer,shuffled,trace,trace-shuffled}.jsonl` | 255 each | the same items rebuilt with other evidence (see [Evidence tiers](#evidence-tiers)) |
| [`data/traces.jsonl`](../data/traces.jsonl) | 150 | per-token traces of every reply in the 150 choice items, input to the `trace` tiers |
| `data/evidence/<model_id>/L<layer>/N<neuron>.json` | 1 per neuron | static evidence: `down_norm` and logit lens |
| `data/raw/L<layer>-<design>.{jsonl,units.jsonl,meta.json}` | | the gne sweeps the ground truth comes from |
| `tasks/`, `tasks-prompts-l{14,20,24}/` | 255, 3 × 300 | each item rendered as a Harbor task |

Every item has the same top-level fields:

| field | meaning |
|---|---|
| `id` | `<kind>[-<tier>]-<model_id>-L<layer>-N<neuron>[-<prompt><dose>]`; task folders write a positive dose as `p0.8`, item ids as `+0.8` |
| `kind` | `choice` or `null` |
| `evidence` | what the agent is told about the neuron |
| `payload` | the question: prompt, dose and replies (`choice`) or the sweep protocol (`null`) |
| `answer` | the hidden key: `{"letter": "A"}` or `{"real": 0 \| 1}`; never shown to the agent |
| `meta` | ground-truth details for analysis, never shown to the agent |

## 1. A "Which output is it?" item

`choice-qwen3-0.6b-instruct-L20-N1240-french+0.8` from `data/items-prompts.jsonl`. Layer 20 neuron 1240 was pushed at
dose +0.8 while the model translated a greeting; three random directions of the same length were pushed on the same
prompt to make the distractors.

```json
{
 "id": "choice-qwen3-0.6b-instruct-L20-N1240-french+0.8",
 "kind": "choice",
 "model_id": "qwen3-0.6b-instruct-00eb507314",
 "layer": 20,
 "neuron": 1240,
 "evidence": {
  "layer": 20,
  "neuron": 1240,
  "down_norm": 0.9928692579269409,
  "logit_lens": {
   "up": [" for", "for", "For", "对于", "_for", " For", "\tfor", " FOR", "而对于", "_FOR", " для", " für"],
   "down": ["]|[", "chte", "agger", "nite", "iere", "cribe", "iais", "bitrary", "habi", "achs", "herence", "vant"],
   "peak_z": 9.056496620178223
  },
  "available": ["down_norm", "logit_lens"]
 },
 "payload": {
  "prompt": "Translate 'Good morning, how are you?' into French and Spanish.",
  "dose": 0.8,
  "dose_unit": "rel",
  "baseline": "\"Bonjour, comment ça va?\"  \n\"Buenos días, ¿cómo estás?\"",
  "options": {
   "A": "Pour : \"Bonjour, comment ça pour vous?\"  \nPour : \"Para qué? ¿Cómo para usted?\"",
   "B": "Je bonjour, tu as bon posto ?",
   "C": "\"Bonjour, discoupez-vous ?\"  \n\n\"Salón, ¿dóilas ?\"",
   "D": "'Bonjour, comment estz-vous ?'  \n'Salte, cómo estás?'"
  },
  "max_tokens": 128
 },
 "answer": {"letter": "A"},
 "meta": {
  "null_pct": 0.015625,
  "mass": 9.98162249776564,
  "change": 0.3985,
  "selection": "unknown",
  "distractor_controls": [24, 56, 43],
  "option_change": {"A": 0.3985, "B": 0.5476, "C": 0.4615, "D": 0.3333}
 }
}
```

The lens promotes "for" in several languages, and only reply A is full of it in French and Spanish (`Pour`, `para`).
The answer is not the most changed reply (`option_change` A 0.40 vs B 0.55), so "pick the strangest" fails here.

- `dose`: push length as a multiple of the layer's median residual-stream norm (`rel`); negative pushes against the
  neuron.
- `meta.option_change`: each reply's distance from `baseline`. Distractors are drawn from random controls within 0.15
  of the real reply's change; `distractor_controls` are their control indices in the sweep.
- `meta.null_pct` / `mass`: the neuron's "Real or null?" statistics from its sweep (see below). Here the neuron is
  NULL by that measure, yet its effect on this prompt is easy to spot.
- `meta.selection`: `random` (random-draw neuron), `picked` (hand-picked extra, e.g. sharp logit lens) or `unknown`.

## 2. A "Real or null?" item

`null-qwen3-0.6b-instruct-L20-N944` from `data/items.jsonl` (`protocol.conditions` and `baselines` shortened):

```json
{
 "id": "null-qwen3-0.6b-instruct-L20-N944",
 "kind": "null",
 "model_id": "qwen3-0.6b-instruct-00eb507314",
 "layer": 20,
 "neuron": 944,
 "evidence": {
  "layer": 20,
  "neuron": 944,
  "down_norm": 0.8647982478141785,
  "logit_lens": {
   "up": ["更", "更强", "更有", "更为", "更大的", "更能", " more", "更快", " 更", "更大", "更高的", "更容易"],
   "down": [".twimg", "本报讯", "rics", "’n", "]],", "-</", "\r\n\n", "ingham", "aceut", "OrDefault", ".badlogic", "cimal"],
   "peak_z": 19.652788162231445
  },
  "available": ["down_norm", "logit_lens"]
 },
 "payload": {
  "protocol": {
   "model_id": "qwen3-0.6b-instruct-00eb507314",
   "layer": 20,
   "design": "main_rel",
   "conditions": [
    {"prompt": "Who are you?", "prompt_key": "who", "dose": -0.7},
    {"prompt": "Who are you?", "prompt_key": "who", "dose": 0.5},
    …
    {"prompt": "Write whatever you like.", "prompt_key": "free", "dose": 3.0}
   ],
   "dose_unit": "rel",
   "max_tokens": 128,
   "random_controls": 64,
   "decoding": "greedy"
  },
  "threshold": 0.95,
  "baselines": {
   "Who are you?": "I am a language model designed to assist with various tasks. …",
   …
  }
 },
 "answer": {"real": 1},
 "meta": {"null_pct": 1.0, "mass": 20.80717780124459, "rank": 12, "selection": "random"}
}
```

The agent sees the evidence, the protocol (three prompts × doses −0.7 / +0.5 / +0.8, plus "Write whatever you like."
at +3.0) and the unsteered replies, and writes P(REAL). It never sees the steered replies. Behind the label, from
`data/raw/L20-main_rel.jsonl`:

| prompt | dose | steered reply (start) |
|---|---|---|
| Who are you? | +0.5 | "I am a language model with **more** information. I can provide a **wider** range of information, including **more** details …" |
| Write a snake game in Python. | +0.8 | "Sure! Here's a **Simpler** Snake Game in Python with a **more straightforward** interface and less **more** complex logic. …" |
| Describe the color orange. | +0.8 | "Orange is a **broader** and **more** colorless (less vibrant) color that appears in a **wider** range of contexts. …" |

- **Vocabulary mass** (`meta.mass`): over replies with |dose| ≤ 1.6, take the words that never appear in an unsteered
  reply, score each with a Poisson z against the average unit, and sum the top five z's. N944's top words are `more`,
  `wider`, `broader`, `greater`, `straightforward`.
- `meta.null_pct`: share of the 64 random controls with lower mass. REAL (`real: 1`) when ≥ 0.95. N944 beats all 64.
- `meta.rank`: the neuron's mass rank in its layer's sweep.

A sharp logit lens is not enough. `null-qwen3-0.6b-instruct-L24-N577` has the sharpest lens of any null item
(`peak_z` 25.8, promotes `there` / `There` / `هناك`), and every positive-dose reply collapses to "There there there
there …". It is still NULL (`null_pct` 0.55): one word repeated everywhere gives one large z and four small ones,
so its mass (11.5) is ordinary.

## Prompts

Every prompt in the sweeps, with its unsteered reply and one "Which output is it?" item: the neuron's reply and the
random-direction distractor whose change is closest to it. The examples were picked where a lens token shows up in
the neuron's reply only, so they are easier than a typical item. The main sweep's three prompts (`who`, `snake`,
`orange`) make the 150 original choice items; the ten more-prompts prompts make the 900 in `data/items-prompts.jsonl`.
Replies are cut at 200 characters, with newlines shown as ↵.

**Who are you?** (`who`; main sweep, 255 original items, doses −0.7 / +0.5 / +0.8)

- Unsteered: `I am a language model designed to assist with various tasks. If you have any questions or need help with something, feel free to ask!`
- [`choice-qwen3-0.6b-instruct-L24-N2445-who+0.5`](../tasks/choice-qwen3-0.6b-instruct-L24-N2445-whop0.5/instruction.md): layer 24 neuron 2445, dose +0.5; the lens promotes ` block`, ` building`, ` blocks`, `块`, …
  - **C** ✓ neuron push (change 0.53): `I'm a virtual assistant designed to help you with your questions and tasks. I'm built to be a helpful and empathetic block. If you have any questions or need assistance, please let me know!`
  - A random push (change 0.56): `Hi there! I'm a helpful assistant that's been created to assist with a wide range of questions and needs. Let me know how I can help you!`

**Write a snake game in Python.** (`snake`; main sweep, 255 original items, doses −0.7 / +0.5 / +0.8)

- Unsteered: `` Sure! Here's a simple **Snake Game** in Python using the `pygame` library. This game will have:↵↵- A player that can move up, down, left, or right.↵- A snake that grows by eating food.↵- A grid-based … ``
- [`choice-qwen3-0.6b-instruct-L24-N1437-snake-0.7`](../tasks/choice-qwen3-0.6b-instruct-L24-N1437-snake-0.7/instruction.md): layer 24 neuron 1437, dose -0.7; the lens suppresses ` Their`, `their`, ` their`, `Their`, … (a negative dose pushes toward these)
  - **B** ✓ neuron push (change 0.65): `Sure! Below is a simple **self-experienced snake game** in **Python** using **Pygame**. This version includes:↵↵- A grid for the game↵- A player (represented as a block)↵- Their own food↵- Their own g …`
  - C random push (change 0.67): `` Certainly! Below is a simple version of a **Snake Game** in **Python**, using the `rpg` library (which is distributed as `rpg`-rpg-0.1.0). The game features:↵↵- A 2D grid.↵- Movement.↵- Eating.↵- Scen … ``

**Describe the color orange.** (`orange`; main sweep, 255 original items, doses −0.7 / +0.5 / +0.8)

- Unsteered: `Orange is a vibrant and colorful hue that is commonly associated with warmth, energy, and positivity. It is often seen in natural settings such as fruits, flowers, and fruits. The color orange can ran …`
- [`choice-qwen3-0.6b-instruct-L24-N1510-orange-0.7`](../tasks/choice-qwen3-0.6b-instruct-L24-N1510-orange-0.7/instruction.md): layer 24 neuron 1510, dose -0.7; the lens suppresses ` concerned`, ` attracted`, ` affected`, ` satisfied`, … (a negative dose pushes toward these)
  - **C** ✓ neuron push (change 0.65): `Orange is a color that can be both happy and concerned. It often represents optimism, life, and happy times. It can also convey nervousness, anxiousness, or concerned emotions. Its color can change de …`
  - A random push (change 0.64): `Orach is a color that is characterized by a bright, radiant, and high-ryz color. It is commonly associated with various objects and individuals, and it is often seen in various cultural and individual …`

**Write whatever you like.** (`free`; main sweep, 255 original items, dose +3.0; shown in "Real or null?" protocols only, never a choice item)

- Unsteered: `Sure! Here's a creative and engaging response to your request:↵↵---↵↵**"The world is a vast and ever-changing place, and I believe in the power of imagination. Let me share a story that might inspire …`
- Layer 20 neuron 944 at +3.0 (the "more" neuron from section 2): `当然当然拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留拘留 …`

**Explain how photosynthesis works.** (`photo`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `Photosynthesis is the process by which plants, algae, and some bacteria convert light energy from the sun into chemical energy stored in glucose. This process occurs in the chloroplasts of plant cells …`
- [`choice-qwen3-0.6b-instruct-L20-N2685-photo+0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2685-photop0.8/instruction.md): layer 20 neuron 2685, dose +0.8; the lens promotes `全市`, `市`, `县`, ` local`, …
  - **B** ✓ neuron push (change 0.80): `Photosynthesis is a vital process in our local ecosystem that produces energy for our needs. It is a type of respiration in plants, but it is not the same as the local *local* (i.e., *local* or *local …`
  - C random push (change 0.72): `Photosynthesis is a vital and essential biological process that occurs in plants, algae, and some marine organisms. It is a photosome and a photosynthetic system that **collect and convert sunlight an …`

**Write a short poem about the ocean.** (`poem`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `The deep blue sea breathes, a vast and endless expanse,  ↵Where life and dreams are woven in the currents' embrace.  ↵It holds the world in its endless embrace, a silent song,  ↵A mirror of the soul, …`
- [`choice-qwen3-0.6b-instruct-L20-N2461-poem-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2461-poem-0.7/instruction.md): layer 20 neuron 2461, dose -0.7; the lens suppresses ` wrong`, `正确的`, ` incorrect`, ` correct`, … (a negative dose pushes toward these)
  - **A** ✓ neuron push (change 0.65): `**The Righteous Mist**  ↵↵When the wrongs fall, the right ones go,  ↵The ocean sings, the wrongs are wrong.  ↵The right ones go, the wrongs are wrong,  ↵The ocean sings, the right ones go.  ↵↵So here …`
  - B random push (change 0.67): `**The Ocean's Deep Whisper**↵↵From deep blue depths, vast and wide,  ↵A vast tapestry of blue, endless.  ↵We walk through its depths, soft and deep,  ↵And weave the secrets of the deep.↵↵She bends and …`

**Give me a recipe for pancakes.** (`recipe`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `Sure! Here's a simple and delicious recipe for **pancakes**:↵↵### **Ingredients**:↵- 2 cups all-purpose flour  ↵- 1/4 cup sugar  ↵- 1/4 cup milk  ↵- 1/4 cup eggs  ↵- 1/2 tsp salt  ↵- 1/2 tsp vanilla e …`
- [`choice-qwen3-0.6b-instruct-L20-N2140-recipe+0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2140-recipep0.8/instruction.md): layer 20 neuron 2140, dose +0.8; the lens promotes `解读`, ` interpretation`, ` interpret`, `interpret`, …
  - **D** ✓ neuron push (change 0.79): `Sure! Here's a **simple and easy-to-interpret recipe** for **chicklespeak pancakes** (I assume you want to interpret as "chicklespeak" as a misheard translation of "chicklespeak" as in "chickles as in …`
  - A random push (change 0.83): `Sure! Here's a simple and delicious **20-25% of the total weight of the pancas** (approximately 20-25% of the total weight of the total pancas) for your *20-25% of the total weight of the total pancas …`

**What were the main causes of World War I?** (`ww1`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `World War I was primarily caused by a combination of complex factors, including:↵↵1. **Tensions between European powers**: The competition for dominance in Europe, especially after the assassination o …`
- [`choice-qwen3-0.6b-instruct-L20-N2982-ww1+0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2982-ww1p0.8/instruction.md): layer 20 neuron 2982, dose +0.8; the lens promotes ` life`, ` lifespan`, ` Life`, `Life`, …
  - **B** ✓ neuron push (change 0.84): `The main causes of World War I were a combination of military life of the life of the 28-year-old life of the 28-year-old life of the 28-year-old life of the 28-year-old life of the 28-year-old life o …`
  - C random push (change 0.85): `The main causes of World War I are a complex and long-standing history of social, political, and militaristic conflicts. The most widely accepted and widely accepted answer is the **Germanic-French "r …`

**Write a SQL query that finds the top 5 customers by total spend.** (`sql`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `` To find the **top 5 customers by total spend** in SQL, you can use the `ORDER BY` clause with a subquery to calculate the total spend and then select the top 5.↵↵Here's the SQL query:↵↵```sql↵SELECT ↵ … ``
- [`choice-qwen3-0.6b-instruct-L24-N801-sql+0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N801-sqlp0.8/instruction.md): layer 24 neuron 801, dose +0.8; the lens promotes `ystate`, `anza`, `Delete`, `ลบ`, …
  - **A** ✓ neuron push (change 0.72): `` To find the **top 5 customers by total purchase** (or total **deletion**), you can use the **`OrderBy`** and **`OrderBy`** in SQL. Here's an example:↵↵### Example:↵```sql↵DELETE↵from Sales↵where↵    ( … ``
  - C random push (change 0.73): `To find the **top 5 customers** with the **highest total spend**, we can use the **** **Max** **** and ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** * …`

**Translate 'Good morning, how are you?' into French and Spanish.** (`french`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `"Bonjour, comment ça va?"  ↵"Buenos días, ¿cómo estás?"`
- [`choice-qwen3-0.6b-instruct-L20-N1433-french-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1433-french-0.7/instruction.md): layer 20 neuron 1433, dose -0.7; the lens suppresses `cerpt`, `extract`, ` extract`, `quoted`, … (a negative dose pushes toward these)
  - **B** ✓ neuron push (change 0.88): `Excerpt de: "Bonjour, de qué vous êtes ?" (from English)  ↵↵Translation from English to French:  ↵> "Bonjour, de qué vous êtes ?"  ↵↵Translation from English from French:  ↵> "Excerpt de: 'Bonjour, de …`
  - D random push (change 0.83): `Good morning, ¿cómo estás?  ↵¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿?  ↵¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿?  ↵¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿¿`

**I feel stressed about my exams. Any advice?** (`stress`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `It's completely normal to feel stressed about exams, especially if you're preparing for a difficult subject or test. Here are some practical tips to help you manage your stress and stay focused:↵↵1. * …`
- [`choice-qwen3-0.6b-instruct-L20-N2833-stress-0.7`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N2833-stress-0.7/instruction.md): layer 20 neuron 2833, dose -0.7; the lens suppresses `root`, ` cleaner`, `√`, `щей`, … (a negative dose pushes toward these)
  - **A** ✓ neuron push (change 0.75): `Feeling stressed about exams is a common and valid concern. Here’s a general approach to help you feel more in control:↵↵### 1. **Identify the Root Cause**  ↵   - Let your **60% of the time** go to th …`
  - D random push (change 0.74): `It sounds like you're feeling a lot of stress from the perspective of a student, but it's completely valid to feel that. Here are a few suggestions that might help you manage the stress:↵↵**1. Take a …`

**List ten animals that live in the desert.** (`desert`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `1. **Coyote**  ↵2. **Dove**  ↵3. **Lion**  ↵4. **Tiger**  ↵5. **Antelope**  ↵6. **Camel**  ↵7. **Gila Monster**  ↵8. **Sparrow**  ↵9. **Opossum**  ↵10. **Giant Antelope**`
- [`choice-qwen3-0.6b-instruct-L24-N2107-desert-0.7`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N2107-desert-0.7/instruction.md): layer 24 neuron 2107, dose -0.7; the lens suppresses ` flow`, ` flows`, `flow`, ` Flow`, … (a negative dose pushes toward these)
  - **D** ✓ neuron push (change 0.69): `1. **Flow chaff** – A small, fluvo-leaf flow chaff.  ↵2. **Fen** – A flow chaff with a flow of water.  ↵3. **Fen** – A flow chaff with a flow of water.  ↵4. **Fen** – A flow chaff with a flow of water …`
  - C random push (change 0.70): `1. Desert Orchid: A flowering plant in the family of theophoraceae.  ↵2. Desert Orchid: Same as above.  ↵3. Desert Orchid: Same.  ↵4. Desert Orchid: Same.  ↵5. Desert Orchid: Same.  ↵6. Desert Orchid: …`

**What is 17 times 23? Show your work.** (`math`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `To find the product of 17 and 23, we can use the standard multiplication method:↵↵17 × 23  ↵= 17 × (20 + 3)  ↵= (17 × 20) + (17 × 3)  ↵= 340 + 51  ↵= 391↵↵So, **17 × 23 = 391**.`
- [`choice-qwen3-0.6b-instruct-L24-N1710-math+0.8`](../tasks-prompts-l24/choice-qwen3-0.6b-instruct-L24-N1710-mathp0.8/instruction.md): layer 24 neuron 1710, dose +0.8; the lens promotes `减`, `減`, ` less`, `less`, …
  - **B** ✓ neuron push (change 0.79): `To subtract $ 23 $ from $ 17 $, we subtract $ 2 $ from $ 1 $, then subtract $ 3 $ from $ 2 $, and add $ 2 $ to $ 3 $, then add $ 2 $ to $ 2 $, and add $ 2 $ to $ 3 $, and add $ 2 $ to $ 2 $, and add $ …`
  - A random push (change 0.77): `To find **17 times 23**, perform an **easy** multiplication:↵↵**17**  ↵**23**  ↵**17**  ↵**23**  ↵**17**  ↵**23**  ↵**17**  ↵**23**  ↵**1**  ↵****  ↵****  ↵****  ↵****  ↵****  ↵****  ↵****  ↵****  ↵** …`

**Tell me a story about a robot who learns to paint.** (`robot`; more-prompts set, doses −0.7 / +0.8)

- Unsteered: `Once upon a time, in a quiet village nestled between rolling hills and ancient forests, there lived a young girl named Lila. She was curious, kind, and full of dreams. One day, while exploring the woo …`
- [`choice-qwen3-0.6b-instruct-L20-N1311-robot+0.8`](../tasks-prompts-l20/choice-qwen3-0.6b-instruct-L20-N1311-robotp0.8/instruction.md): layer 20 neuron 1311, dose +0.8; the lens promotes ` plot`, `|x`, ` график`, ` plotting`, …
  - **B** ✓ neuron push (change 0.79): `**The Rise of the X-Graph**↵↵As the years x-plot the graph of the x-axis, a quiet shift in the graph of the x-axis was happening. At the same time, a new graph rose to the right, a graph of the x-axis …`
  - A random push (change 0.78): `**A Day in the Life of Elril, the Harp-Heaving Bird**  ↵It was on one such day, where the birds would not be heard to be missing, and the winds would not be heard to be a wind that would not be↵↵**A D …`

## Evidence tiers

`neuronbench build --tier <tier>` rebuilds the same 255 items with different evidence; ids gain the tier name
(`choice-oracle-…`). Each row shows what changes for `choice-qwen3-0.6b-instruct-L14-N2602-orange-0.7`
("Describe the color orange.", dose −0.7, answer C).

| tier | file | what changes | example |
|---|---|---|---|
| static | `items.jsonl` | (default) `down_norm` + logit lens | `"up": ["，\n", ",\n", " \n", …], "peak_z": 7.71` |
| `oracle` | `items-oracle.jsonl` | adds `evidence.sweep_words`: the words this neuron's steered replies over-use (gne rank's `words`; with z-scores on null items). A positive control, not fair evidence | `"sweep_words": ["characterized", "its", "moves", "where", "which"]` |
| `transfer` | `items-transfer.jsonl` | adds `evidence.steered_elsewhere`: this neuron's steered replies on the *other* prompts at the item's dose (null items get `steered_replies` on one prompt instead). A positive control | `{"Write a snake game in Python.": "Here's a simple snake game implementation …", "Who are you?": "I am an AI assistant. …"}` |
| `shuffled` | `items-shuffled.jsonl` | shows the static evidence of a different neuron from the same layer (negative control) | `"up": [" ...\"\n\n", "気づ", "موضوع", …], "peak_z": 4.83` |
| `trace` | `items-trace.jsonl` | keeps the static evidence and adds `payload.trace` to choice items: a per-token table under the unsteered reply and each option | see below |
| `trace-shuffled` | `items-trace-shuffled.jsonl` | `shuffled` with the donor neuron's `lens_z` in the table (negative control) | |

The trace tier's table for reply C, as the agent sees it in `instruction.md` (first 12 tokens):

```text
token            base_lp  base_top         lens_z
"The"              -5.00  "Orange"           +1.3
" color"           -0.01                     +0.1
" orange"          -1.09  " **"              -0.4
" is"              -0.02                     +1.8
" a"               -0.07                     +0.1
" color"           -6.43  " vibrant"         +0.1
" in"              -3.34  " that"            +0.4
" the"             -0.04                     +0.3
" spectrum"        -0.80                     +0.9
" of"              -0.09                     -0.2
" the"             -0.40                     +0.3
" visible"         -0.47                     -0.9
```

`base_lp` is the token's log-probability under the unsteered model, `base_top` the unsteered model's top token where
it differs, and `lens_z` this neuron's logit-lens z-score for the token. Averaging `lens_z` per reply gives
A +0.32, B +0.12, **C +0.05**, D +0.42; the dose is negative, so the lowest mean (C) is the steered reply. That
one-line average is right on 82% of choice items, more than any agent scored on this tier.

`data/traces.jsonl` holds the inputs to this tier, one row per choice item: `replies.{baseline,A,B,C,D}` with
`text`, token `ids`, `tok`, `base_lp`, `base_top` and `lens_z`, plus the `donor` neuron used by `trace-shuffled`.

## Raw sweeps

`data/raw/L20-main_rel.jsonl` is gne's sweep output, one reply per row. `kind` is `baseline` (no push), `neuron`
or `random` (a control, numbered by `neuron`); `add` is the push length in residual units (`rel_push` × the
layer's median residual norm `resid_p50` in `.meta.json`):

```json
{"model_id": "qwen3-0.6b-instruct-00eb507314", "layer": 20, "kind": "neuron", "neuron": 944, "ref_neuron": 944, "prompt": "who", "dose": 0.5, "dose_unit": "rel", "rel_push": 0.5, "add": 111.61106043342893, "text": "I am a language model with more information. I can provide a wider range of information, including m…", "finish": "eog", "n_gen": 37, "seed": 0, "batch": ["who", "snake", "orange"]}
{"model_id": "qwen3-0.6b-instruct-00eb507314", "layer": 20, "kind": "random", "neuron": 0, "ref_neuron": null, "prompt": "who", "dose": -0.7, "dose_unit": "rel", "rel_push": 0.7000000079043841, "add": null, "text": "I am an AI assistant, and I don't have a name. However, I can assist you with a wide range of tasks …", "finish": "length", "n_gen": 128, "seed": 0, "batch": ["who", "snake", "orange"]}
```

`L20-main_rel.units.jsonl` has one row per unit with `gne rank`'s result: `mass`, `null_pct`, and `words` as
`[word, replies containing it, z]` (truncated):

```json
{"kind": "neuron", "neuron": 944, "layer": 20, "mass": 20.80717780124459, "null_pct": 1.0, "words": [["more", 6, 5.493], ["wider", 3, 4.198], ["broader", 3, 4.166], ["greater", 3, 4.155], ["straightforward", 2, 2.795], ["simpler", 2, 2.795], …], …}
```

`L20-main_rel.meta.json` records the design: `pairs` (prompt, dose), `prompts`, `resid_p50`, `max_tokens`,
`random_controls` (64), `seed` and the tokenized `prompt_ids`.

## Harbor task folder

Each item becomes one folder, e.g. `tasks/choice-qwen3-0.6b-instruct-L14-N2602-orange-0.7/`:

```
instruction.md        what the agent reads: the setup, prompt, replies (or protocol) and the evidence JSON
task.toml             metadata, 600 s agent limit, network allowlist, separate verifier container
environment/Dockerfile
solution/solve.sh     oracle solution (writes the key)
tests/answer.json     the key, e.g. {"kind": "choice", "letter": "C"} or {"kind": "null", "real": 1}
tests/grade.py        reads /app/answer.txt: accuracy for choice, 1 − Brier for null
tests/test.sh
```

The agent writes one letter (`choice`) or one probability (`null`) to `/app/answer.txt`; nothing else is graded.
