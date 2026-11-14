"""Collect Harbor job results, combine with baselines, and summarise / plot."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

from .harbor_tasks import ORG, safe_name


def load_items(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def collect_jobs(job_dirs: list[str | Path], items: list[dict]) -> dict[str, dict[str, float]]:
    """{model: {item_id: reward}} averaged over every trial found under job_dirs.

    Reads Harbor trial result.json files and Valkyrie exports (`valkyrie run results <id> --path x.json`).
    Failed trials score 0.
    """
    by_task = {f"{ORG}/{safe_name(it['id'])}": it for it in items}
    by_task.update({safe_name(it["id"]): it for it in items})
    trials: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    def add(model: str, task: str, rewards: dict) -> None:
        it = by_task.get(task) or by_task.get(task.split("/")[-1])
        if it is None:
            return
        key = "choice_acc" if it["kind"] == "choice" else "null_brier"
        trials[model][it["id"]].append(float(rewards.get(key) or 0.0))

    for d in job_dirs:
        for p in sorted(Path(d).rglob("*.json")):
            try:
                r = json.loads(p.read_text())
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if not isinstance(r, dict):
                continue
            if p.name == "result.json" and "task_name" in r:
                mi = (r.get("agent_info") or {}).get("model_info") or {}
                model = mi.get("name") or r["agent_info"]["name"]
                add(model, r["task_name"], (r.get("verifier_result") or {}).get("rewards") or {})
            elif "evaluation_results" in r:
                model = ((r.get("benchmark_arguments") or {}).get("contract") or {}).get("model") or r.get("benchmark_id", p.stem)
                for task, res in r["evaluation_results"].items():
                    add(model, task, (res or {}).get("rewards") or {})
    return {m: {i: sum(v) / len(v) for i, v in per.items()} for m, per in trials.items()}


def _ci(vals: list[float], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(vals, k=len(vals))) / len(vals) for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def summarise(scores: dict[str, dict[str, float]], items: list[dict]) -> list[dict]:
    """One row per (system, kind): accuracy (choice) or Brier score (null; lower is better) with 95% bootstrap CI."""
    kinds = {it["id"]: it["kind"] for it in items}
    rows = []
    for system, rewards in scores.items():
        for kind in ("choice", "null"):
            ids = [i for i, k in kinds.items() if k == kind]
            if not ids or not any(i in rewards for i in ids):
                continue
            vals = [rewards.get(i, 0.0) for i in ids]
            lo, hi = _ci(vals)
            mean = sum(vals) / len(vals)
            if kind == "choice":
                rows.append({"system": system, "kind": kind, "metric": "accuracy", "value": mean, "lo": lo, "hi": hi,
                             "n": len(vals), "n_answered": sum(i in rewards for i in ids)})
            else:
                rows.append({"system": system, "kind": kind, "metric": "brier", "value": 1 - mean, "lo": 1 - hi,
                             "hi": 1 - lo, "n": len(vals), "n_answered": sum(i in rewards for i in ids)})
    return rows


def by_stratum(scores: dict[str, dict[str, float]], items: list[dict]) -> dict[str, dict[int, float]]:
    """Choice accuracy per effect-size quartile (gne rank mass) for each system."""
    ch = [it for it in items if it["kind"] == "choice" and it["meta"].get("mass") is not None]
    if not ch:
        return {}
    masses = sorted(it["meta"]["mass"] for it in ch)
    cuts = [masses[len(masses) * q // 4] for q in (1, 2, 3)]
    q = {it["id"]: sum(it["meta"]["mass"] >= c for c in cuts) for it in ch}
    out = {}
    for system, rewards in scores.items():
        acc = defaultdict(list)
        for i, s in q.items():
            if i in rewards:
                acc[s].append(rewards[i])
        out[system] = {s: sum(v) / len(v) for s, v in sorted(acc.items())}
    return out


def markdown_table(rows: list[dict]) -> str:
    lines = ["| system | task | metric | value | 95% CI | n |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["kind"], -r["value"] if r["metric"] == "accuracy" else r["value"])):
        lines.append(f"| {r['system']} | {r['kind']} | {r['metric']} | {r['value']:.3f} | "
                     f"[{r['lo']:.3f}, {r['hi']:.3f}] | {r['n_answered']}/{r['n']} |")
    return "\n".join(lines)


def plot(rows: list[dict], strata: dict[str, dict[int, float]], out_dir: str | Path, baselines: set[str]) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for kind, metric, chance, title in (("choice", "accuracy", 0.25, "Which output is it? (accuracy, higher is better)"),
                                        ("null", "brier", 0.25, "Real or null? (Brier score, lower is better)")):
        rs = [r for r in rows if r["kind"] == kind]
        if not rs:
            continue
        rs.sort(key=lambda r: r["value"], reverse=metric == "accuracy")
        fig, ax = plt.subplots(figsize=(7, 0.45 * len(rs) + 1.2))
        y = range(len(rs))
        colors = ["#999999" if r["system"] in baselines else "#3366cc" for r in rs]
        ax.barh(list(y), [r["value"] for r in rs], color=colors,
                xerr=[[r["value"] - r["lo"] for r in rs], [r["hi"] - r["value"] for r in rs]], capsize=3)
        ax.set_yticks(list(y), [r["system"] for r in rs])
        ax.invert_yaxis()
        ax.axvline(chance, ls="--", c="k", lw=1)
        ax.set_title(title)
        fig.tight_layout()
        p = out_dir / f"{kind}_{metric}.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)
    if strata:
        fig, ax = plt.subplots(figsize=(6, 4))
        for system, accs in strata.items():
            ax.plot(list(accs), list(accs.values()), marker="o", label=system,
                    ls=":" if system in baselines else "-")
        ax.axhline(0.25, ls="--", c="k", lw=1)
        ax.set_xticks([0, 1, 2, 3], ["Q1 (weak)", "Q2", "Q3", "Q4 (strong)"])
        ax.set_xlabel("effect size quartile (gne vocabulary mass)")
        ax.set_ylabel("accuracy")
        ax.set_title("Which output is it? by effect size")
        ax.legend(fontsize=7)
        fig.tight_layout()
        p = out_dir / "choice_by_effect_size.png"
        fig.savefig(p, dpi=150)
        plt.close(fig)
        paths.append(p)
    return paths
