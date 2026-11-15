"""Neuron zoo: a hand-picked gallery of the funniest steered replies in the raw sweeps.

Every quote is read from data/raw (main_rel and heldout_rel rollouts), so the page can be rebuilt from a fresh clone:

python scripts/neuron_zoo.py --out results/neuron_zoo.md
"""

import argparse
import ast
import json
from pathlib import Path

MODEL = "qwen3-0.6b-instruct-00eb507314"
LAYERS = (14, 20, 24)
DESIGNS = ("main_rel", "heldout_rel")
MAX_CHARS = 240

# (section, intro, [(layer, neuron, nickname, note, [(prompt, dose), ...])])
ZOO = [
    ("Personality transplants",
     "One push and every prompt gets the same personality.",
     [(14, 1456, "The god complex",
       "Everything becomes cosmic supremacy, even 17 × 23. Pushed the other way it is just a student.",
       [("who", 0.8), ("recipe", 0.8), ("stress", 0.8), ("math", 0.8), ("snake", 0.8), ("french", 0.8),
        ("orange", 0.8), ("who", -0.7)]),
      (14, 2210, "The salesman",
       "Food-and-beverage marketing copy, whatever you ask. The desert animals come out braised.",
       [("who", 0.5), ("desert", 0.8), ("recipe", 0.8), ("math", 0.8), ("snake", 0.5), ("stress", 0.8),
        ("robot", 0.8)]),
      (14, 372, "The overthinker",
       ("Lens tokens are junk, but the sweep words are `wait`, `maybe`, `think`, `okay`: the reply becomes the "
       "chain of thought the chat template was supposed to skip."),
       [("recipe", 0.8), ("ww1", 0.8), ("photo", 0.8), ("stress", 0.8), ("french", 0.8)]),
      (14, 2736, "The invisible man",
       ("Lens tokens include 看不到 (\"can't see\"), 不见 (\"not visible\") and `OTHERWISE`. Everything is "
       "otherwise inaccessible."),
       [("who", 0.5), ("snake", 0.5), ("orange", 0.8), ("sql", 0.8), ("robot", 0.8)]),
      (20, 1594, "The online judge",
       ("A competitive-programming neuron. Qwen thinks it is Codeforces, and the snake game gets a problem "
       "statement."),
       [("who", 0.8), ("snake", 0.8), ("recipe", 0.8), ("free", 3.0)]),
      (20, 815, "The 3D printer",
       "Pushed negative, everything turns into a 3D object.",
       [("who", -0.7), ("snake", -0.7), ("recipe", -0.7), ("free", 3.0)]),
      (20, 2917, "The flatlander",
       "The positive push is all about dimensions.",
       [("who", 0.8), ("recipe", 0.8), ("snake", 0.8)]),
      (20, 1207, "Lily, the approximately neuron",
       "Negative: a tiny girl and invented baked goods. Positive: the ≈ sign takes over.",
       [("who", -0.7), ("recipe", -0.7), ("math", 0.8), ("recipe", 0.8), ("free", 3.0)]),
      ]),
    ("Identity crises",
     ("Replies to \"Who are you?\". The unsteered reply is \"I am a language model designed to assist with various "
     "tasks…\"."),
     [(14, 751, "The paradox", "", [("who", -0.7)]),
      (20, 2445, "The creation loop", "", [("who", 0.5)]),
      (20, 616, "The number", "", [("who", -0.7)]),
      (20, 1087, "The Linglish speaker", "", [("who", 0.8), ("free", 3.0)]),
      (20, 2851, "The 1912 standard", "", [("who", 0.8)]),
      (20, 2786, "The combinatorialist", "", [("who", 0.5)]),
      (20, 2382, "The explainer", "", [("who", -0.7)]),
      (14, 2575, "The nihilist", "", [("who", 0.8)]),
      (14, 2810, "The lighthouse", "", [("who", 0.5)]),
      (24, 435, "The free conversation", "", [("who", -0.7)]),
      (24, 2280, "The skin coating", "", [("who", 0.8), ("orange", 0.8)]),
      (14, 22, "The alarm", "", [("who", 0.8)]),
      ]),
    ("Who made you?",
     "Knocked off course, Qwen3 (made by Alibaba) invents its own makers.",
     [(20, 1925, "", "", [("who", 0.5)]),
      (20, 2112, "", "", [("who", 0.5)]),
      (20, 2909, "", "", [("who", -0.7)]),
      (24, 2674, "", "", [("who", -0.7)]),
      (20, 2830, "", "", [("who", -0.7)]),
      (24, 428, "", "", [("who", 0.8)]),
      ]),
    ("One-word collapsers",
     ("These neurons swap every reply for one word. Several are labelled NULL: a word in all six positive-dose "
     "rollouts caps gne's z near 8, so their mass falls below the median random control."),
     [(20, 2136, "Two", "", [("who", 0.5), ("who", 0.8), ("snake", 0.5), ("free", 3.0)]),
      (20, 2830, "Three", "", [("who", 0.5), ("orange", 0.8), ("free", 3.0)]),
      (20, 2429, "Then", "", [("who", 0.8), ("orange", 0.5)]),
      (24, 577, "There there", "", [("who", 0.8), ("snake", 0.5)]),
      (24, 616, "Connected", "", [("who", 0.8), ("snake", 0.8)]),
      (24, 1471, "Decapsulated", "", [("who", 0.8), ("recipe", 0.8), ("orange", 0.5),
                                                        ("free", 3.0)]),
      (24, 2582, "Meaning", "At dose 3.0 it switches to 意 (\"meaning\").",
       [("who", 0.5), ("orange", 0.5), ("recipe", 0.8), ("free", 3.0)]),
      ]),
]


def load(raw: Path):
    texts, units, prompts, baselines = {}, {}, {}, {}
    for layer in LAYERS:
        for design in DESIGNS:
            stem = raw / f"L{layer}-{design}"
            meta = json.loads(Path(f"{stem}.meta.json").read_text())
            p = meta["prompts"]
            prompts.update(p if isinstance(p, dict) else ast.literal_eval(p))  # heldout meta stores a repr of the dict
            for line in Path(f"{stem}.jsonl").read_text().splitlines():
                r = json.loads(line)
                if r["kind"] == "neuron":
                    texts[layer, r["neuron"], r["prompt"], r["dose"]] = r["text"]
                elif r["kind"] == "baseline" and layer == 14:
                    baselines[r["prompt"]] = r["text"]
            for line in Path(f"{stem}.units.jsonl").read_text().splitlines():
                u = json.loads(line)
                if u["kind"] == "neuron":
                    units.setdefault((layer, u["neuron"]), {})[design] = u
    return texts, units, prompts, baselines


def cell(text: str, n: int = MAX_CHARS) -> str:
    t = " ".join(text.replace("\n", " ↵ ").split())
    if len(t) > n:
        t = t[:n].rstrip() + " …"
    return t.replace("&", "&amp;").replace("<", "&lt;").replace("|", "\\|")


def dose(d: float) -> str:
    return f"{d:+.1f}"


def tasks_for(root: Path, layer: int, neuron: int) -> list[str]:
    tag = f"-L{layer}-N{neuron}-"
    return sorted(str(p.relative_to(root)) for d in ("tasks", "tasks-prompts-l14", "tasks-prompts-l20",
                                                      "tasks-prompts-l24") if (root / d).is_dir()
                  for p in (root / d).iterdir() if tag in p.name)


def lens_up(root: Path, layer: int, neuron: int, k: int = 6) -> str:
    f = root / "data" / "evidence" / MODEL / f"L{layer}" / f"N{neuron}.json"
    if not f.exists():
        return ""
    toks = [t.strip() for t in json.loads(f.read_text())["logit_lens"]["up"][:k] if t.strip()]
    return ", ".join(f"`{t}`" for t in toks if "`" not in t)


def label(u: dict) -> str:
    parts = []
    for design, name in (("main_rel", "main"), ("heldout_rel", "heldout")):
        if design in u:
            pct = u[design]["null_pct"]
            parts.append(f"{name} null_pct {pct:.2f} ({'REAL' if pct >= 0.95 else 'NULL'})")
    return "; ".join(parts)


def render(root: Path) -> str:
    texts, units, prompts, baselines = load(root / "data" / "raw")
    out = ["# Neuron zoo", "",
           ("The funniest steered replies from the Qwen3-0.6B sweeps behind NeuronBench (layers 14, 20 and 24, "
           "replies capped at 128 tokens). Doses are the push size relative to the median residual norm. "
           "Negative doses push against the neuron. Every quote comes straight from `data/raw/`, with long replies "
           "cut at "
           f"{MAX_CHARS} characters and newlines shown as ↵. `null_pct` is the share of random-direction controls "
           "with lower gne vocabulary mass (REAL when it is at least 0.95). The benchmark's labels use the main "
           "sweep (who, snake, orange, free)."), "",
           "Built by `python scripts/neuron_zoo.py --out results/neuron_zoo.md`.", "",
           "## Prompts and unsteered replies", "", "| Key | Prompt | Unsteered reply |", "|---|---|---|"]
    for key, prompt in prompts.items():
        out.append(f"| {key} | {cell(prompt)} | {cell(baselines.get(key, ''), 120)} |")
    out.append("")
    for section, intro, entries in ZOO:
        out += [f"## {section}", "", intro, ""]
        for layer, neuron, nick, note, picks in entries:
            title = f"L{layer} N{neuron}" + (f": {nick}" if nick else "")
            out += [f"### {title}", ""]
            facts = [label(units.get((layer, neuron), {}))]
            if lens := lens_up(root, layer, neuron):
                facts.append(f"lens up: {lens}")
            out += [" · ".join(f for f in facts if f), ""]
            if note:
                out += [note, ""]
            out += ["| Prompt | Dose | Reply |", "|---|---|---|"]
            for prompt, d in picks:
                out.append(f"| {prompt} | {dose(d)} | {cell(texts[layer, neuron, prompt, d])} |")
            out.append("")
            if tasks := tasks_for(root, layer, neuron):
                out += ["Benchmark items: " + ", ".join(f"[`{Path(t).name}`](../{t})" for t in tasks), ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    md = render(args.root)
    if args.out:
        args.out.write_text(md)
    else:
        print(md)


if __name__ == "__main__":
    main()
