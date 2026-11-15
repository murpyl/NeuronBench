# Which reply did this neuron cause?

You are studying MLP neuron 305 in layer 20 of a small language model.

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
I feel stressed about my exams. Any advice?
```

## Reply with no intervention

```text
It's completely normal to feel stressed about exams, especially if you're preparing for a difficult subject or test. Here are some practical tips to help you manage your stress and stay focused:

1. **Take a break**: If you're feeling overwhelmed, take a short walk, or even just breathe deeply. This can help reduce stress and improve your mood.

2. **Set realistic goals**: Instead of overthinking, focus on what you can control. Break down your study plan into smaller, manageable tasks.

3. **Practice relaxation techniques**: Techniques like deep breathing, progressive muscle relaxation, or mindfulness meditation can help calm your mind.

4.
```

## Candidate replies

### Reply A

```text
I feel stressed about my exams. It's a serious and important part of your academic life. Let me give you some **safe and effective** ways to deal with it:

### 1. **Take a break and think of the time you have before the exam.**
   - If you have time, you can also **reflect** on your preparation and **evaluate** your current situation. This helps you understand the **risk** and **responsibility** you have.

### 2. **Create a **"preparation time****.**
   - If you have time, you can **prepare** for the exams in advance
```

### Reply B

```text
It's important to take a healthy approach to manage stress and manage your exams. Here are some tips to help you feel more balanced:

1. **Practice Time Management**: Start with a daily schedule or use a planner to allocate time for study, exercise, and personal activities. Start early to build a habit.

2. **Eat Well**: Eat a nutritious diet to help manage stress. Exercise is also a good way to help manage stress.

3. **Get Enough Sleep**: Sleep is essential to help manage stress. Start to practice self-care to help manage stress.

4. **Practice Mindfulness or Meditation**: Some techniques like meditation or mindfulness
```

### Reply C

```text
Feeling stressed during the day can be a common and often painful experience, but there are several ways to help you feel more relaxed and ready for the day's tasks. Here's a simple and helpful guide to help you:

### 1. **Stay Hyptertall (Tired-Feeling)**
   - **Drink Water**: Dece is important to stay awake and alert.  
    **Drink a small sip of tea or coffee** to stay awake and try to stay awake for the day.  
    **Drink water for the first 3 hours after waking** to stay awake and try to stay awake for the day
```

### Reply D

```text
Sure! Feeling the weight of exams is a good sign—when you’re preparing, it’s when the *real* growth happens. Here’s some **thoughtful and actionable advice** to help you:

### 1. **Focus on the *why* behind the exam*
- **What’s the importance of the exam?*  
- Let the *value* of the education* and the *future* behind it*.

### 3. **Plan your time well*
- **Break the schedule into manageable parts**.
- **Set a daily/weekly goal** (e.g., 2 hours of study, 1
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
 "neuron": 305,
 "down_norm": 0.8140617609024048,
 "logit_lens": {
  "up": [
   " Guides",
   " Downloads",
   "市政协",
   "_fu",
   "fdc",
   "럽",
   "这么说",
   " Thumbnails",
   "ferred",
   " appeals",
   "voke",
   "一类"
  ],
  "down": [
   "inceton",
   "atten",
   "安全",
   "简单",
   "面目",
   "简",
   "andelier",
   "ylvania",
   "resher",
   "imbus",
   "/**<",
   ".shapes"
  ],
  "peak_z": 5.606534481048584
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
