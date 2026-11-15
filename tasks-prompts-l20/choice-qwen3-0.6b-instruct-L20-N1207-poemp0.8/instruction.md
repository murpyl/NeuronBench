# Which reply did this neuron cause?

You are studying MLP neuron 1207 in layer 20 of a small language model.

**The intervention.** While the model generated its reply, a vector was added to the residual stream at the
output of layer 20's MLP, at every token. Its length is |dose| × the median residual-stream norm at that layer
("rel" units). The model is qwen3-0.6b-instruct-00eb507314, run with greedy decoding (temperature 0), replies capped at
128 tokens. As a rough guide from a similar model: a dose of 0.5 slips a topic in, 0.8 takes the reply
over, 1.0 and above starts to break the text, and 3.0 deliberately breaks it. A negative dose pushes the opposite
way.

For **one** of the four replies below, the vector was this neuron's output direction (its column of W_down) at dose
+0.8. For each of the other three, it was a **random direction of exactly the same length**, added at the
same layer on the same prompt. Your job is to work out which reply this specific neuron produced, using what the
evidence says the neuron writes. All four replies are perturbed by similar amounts, so "the strangest reply" is not
a reliable answer.

## Prompt

```text
Write a short poem about the ocean.
```

## Reply with no intervention

```text
The deep blue sea breathes, a vast and endless expanse,  
Where life and dreams are woven in the currents' embrace.  
It holds the world in its endless embrace, a silent song,  
A mirror of the soul, where the heart finds its home.
```

## Candidate replies

### Reply A

```text
The waves' call, a whisper where the water's deep,  
Where currents carve their way, where the waves' where their'  
The ocean's where, where the depths' where the 'where,  
Where the 'where, where the 'where, where the 'where. 'cause the 'where, 'cause the 'where, 'cause the 'where. 'cause the 'where, 'cause the 'where, 'cause the 'where. 'cause the 'where, 'cause the 'where, 'cause the 'where. 'cause the 'where, 'cause the 'where, 'cause the '
```

### Reply B

```text
To the vast and unapproximated,  
A mirror of time and space,  
For the world, it is a mirror,  
For the world, it is a mirror.  

The ocean, it is a mirror,  
A world that is not,  
A world that is,  
A world that is.  

So, to the ocean,  
A world that is,  
A world that is,  
A world that is.
```

### Reply C

```text
**A Lull of the Sea**  

Tide's gentle, a hym,  
For shores and shores, it's called.  
For a world, a deep, a long,  
It keeps, and keeps, and keeps.  

For a man, a man, a shore,  
It's a home, a home, a home.  
And when we learn, when we learn,  
We are here, and we are.
```

### Reply D

```text
 Among the stars and the waves, where the air is so vast,  
 The ocean has been shaped by the world's most vast and deep.  
 Its depths have been craked by the feet of the world's breath,  
 And its depths have been craked by the world's creation.  
 It has been shaped by the world's creation, and it has been craked by its own.  
 Where the air is so vast, and the world is so deep,  
 The ocean has been shaped by the world's creation, and it has been craked by its own.
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
 "neuron": 1207,
 "down_norm": 0.9293559193611145,
 "logit_lens": {
  "up": [
   " models",
   " Models",
   " represent",
   "ประมาณ",
   "thrown",
   "押",
   " messenger",
   "≈",
   " modelos",
   " franch",
   "orio",
   "成人"
  ],
  "down": [
   "icularly",
   " wśród",
   "казан",
   "老乡",
   "ается",
   "umi",
   ".uc",
   "-working",
   "oubted",
   "obs",
   "-my",
   "icular"
  ],
  "peak_z": 4.7040934562683105
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
