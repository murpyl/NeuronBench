"""Headline figure: results/headline.png (and results/headline.md).

Left: "Which output is it?" on the 900 more-prompts items, every model against the logit-lens lookup and chance.
Right: the 150 original choice items at each evidence tier (wrong evidence, static, per-token trace, measured sweep
words), each model next to the best agent-free baseline for that tier.

python scripts/headline_plot.py
"""

import argparse
import random
from pathlib import Path

from neuronbench.baselines import run_baselines
from neuronbench.results import _ci, collect_jobs, load_items

J = "jobs/valkyrie"
MODELS = {"anthropic/claude-opus-5-5": "Opus 5.5", "anthropic/claude-sonnet-5-5": "Sonnet 5.5",
          "anthropic/claude-haiku-5-5": "Haiku 5.5", "openai/gpt-5.6-luna": "GPT-5.6-luna"}
PROMPT_JOBS = [f"{J}/l{L}-prompts-{m}.json" for L in (14, 20, 24)
               for m in ("opus-5-5", "sonnet-5-5", "haiku-5-5", "gpt-5.6-luna")]
# tier: (items, job files, agent-free baseline, its label)
TIERS = {
    "wrong evidence": ("data/items-shuffled.jsonl",
                       ["l14-l20-shuffled-haiku-5-5", "l24-shuffled-haiku-5-5",
                        "l14-l20-shuffled-claude-opus-5-5", "l24-shuffled-claude-opus-5-5"],
                       "logit_lens", "lookup"),
    "static\n(the benchmark)": ("data/items.jsonl",
                                [f"{d}-{m}" for d in ("l14-l20", "l24")
                                 for m in ("haiku-5-5", "claude-opus-5-5", "sonnet-5-5")],
                                "logit_lens", "lookup"),
    "+ per-token\ntrace": ("data/items-trace.jsonl",
                           [f"{d}-trace-{m}" for d in ("l14-l20", "l24") for m in ("haiku-5-5", "opus-5-5")],
                           "trace_lens_mean", "mean lens_z"),
    "+ measured\nsweep words": ("data/items-oracle.jsonl",
                                [f"{d}-oracle-{m}" for d in ("l14-l20", "l24") for m in ("haiku-5-5", "sonnet-5-5")],
                                "sweep_words", "word lookup"),
}
COLORS = {"Opus 5.5": "#1f4e9c", "Sonnet 5.5": "#3d7dd8", "Haiku 5.5": "#8db3ec", "GPT-5.6-luna": "#2e9e6a",
          "baseline": "#999999"}


def paired_ci(a: dict, b: dict, ids: list[str], n_boot: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    d = [a[i] - b[i] for i in ids]
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(d, k=len(d))) / len(d) for _ in range(n_boot))
    return sum(d) / len(d), means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def choice_scores(items_path: str, jobs: list[str]) -> tuple[list[str], dict, dict]:
    items = [it for it in load_items(items_path) if it["kind"] == "choice"]
    ids = [it["id"] for it in items]
    models = {MODELS[m]: s for m, s in collect_jobs(jobs, items).items() if m in MODELS}
    for m, s in models.items():
        assert set(s) == set(ids), f"{m}: {len(s)}/{len(ids)} items in {items_path}"
    return ids, models, run_baselines(items)


def bar(ax, y, scores, ids, color, label):
    vals = [scores[i] for i in ids]
    v, (lo, hi) = sum(vals) / len(vals), _ci(vals)
    ax.barh(y, v, color=color, xerr=[[v - lo], [hi - v]], capsize=3, height=0.8)
    ax.text(hi + 0.01, y, f"{v:.0%}", va="center", fontsize=8)
    return label, v, lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results")
    a = ap.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw={"width_ratios": [1, 1.25]})
    md = ["## Headline (`scripts/headline_plot.py`)", "",
          "Which output is it?, 900 more-prompts items (accuracy, 95% bootstrap CI; paired difference vs lookup)", "",
          "| system | accuracy [95% CI] | vs lookup [95% CI] |", "|---|---|---|"]

    ids, models, base = choice_scores("data/items-prompts.jsonl", PROMPT_JOBS)
    lookup = base["logit_lens"]
    order = sorted(models, key=lambda m: -sum(models[m].values()))
    labels = []
    for y, m in enumerate(order):
        _, v, lo, hi = bar(axl, y, models[m], ids, COLORS[m], m)
        d, dlo, dhi = paired_ci(models[m], lookup, ids)
        labels.append(f"{m}\n({100 * d:+.0f} pts vs lookup)")
        md.append(f"| {m} | {v:.3f} [{lo:.3f}, {hi:.3f}] | {d:+.3f} [{dlo:+.3f}, {dhi:+.3f}] |")
    _, v, lo, hi = bar(axl, len(order), lookup, ids, COLORS["baseline"], "lookup")
    labels.append("logit-lens lookup\n(no model)")
    md.append(f"| logit-lens lookup | {v:.3f} [{lo:.3f}, {hi:.3f}] | |")
    axl.set_yticks(range(len(labels)), labels, fontsize=9)
    axl.invert_yaxis()
    axl.axvline(0.25, ls="--", c="k", lw=1)
    axl.text(0.25, len(labels) - 0.45, " chance", fontsize=8)
    axl.set_xlim(0, 1)
    axl.set_xlabel("accuracy")
    axl.set_title(f"Which output is it?  {len(ids)} items, 10 extra prompts\nevery model beats the lookup, none is close to solving it",
                  fontsize=10)

    md += ["", "Which output is it?, 150 original items by evidence tier", "", "| tier | system | accuracy [95% CI] |",
           "|---|---|---|"]
    y, ticks, tick_labels = 0, [], []
    for tier, (items_path, jobs, bname, blabel) in TIERS.items():
        ids, models, base = choice_scores(items_path, [f"{J}/{j}.json" for j in jobs])
        start = y
        rows = [(m, models[m], COLORS[m]) for m in MODELS.values() if m in models]
        rows.append((f"{blabel} (no model)", base[bname], COLORS["baseline"]))
        for name, s, c in rows:
            _, v, lo, hi = bar(axr, y, s, ids, c, name)
            ticks.append(y)
            tick_labels.append(name)
            md.append(f"| {tier.replace(chr(10), ' ')} | {name} | {v:.3f} [{lo:.3f}, {hi:.3f}] |")
            y += 1
        axr.text(-0.02, (start + y - 1) / 2, tier, transform=axr.get_yaxis_transform(), ha="right", va="center",
                 fontsize=9, fontweight="bold")
        y += 0.6
    axr.set_yticks(ticks, tick_labels, fontsize=8)
    axr.tick_params(axis="y", pad=110)
    axr.invert_yaxis()
    axr.axvline(0.25, ls="--", c="k", lw=1)
    axr.set_xlim(0, 1)
    axr.set_xlabel("accuracy")
    axr.set_title("Same task on the 150 original items, by evidence given\nthe static evidence, not the task format, is the bottleneck",
                  fontsize=10)

    fig.tight_layout()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "headline.png", dpi=150)
    (out / "headline.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
