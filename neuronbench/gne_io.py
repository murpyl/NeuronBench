"""Read the files gne writes: a sweep run (<run>.jsonl + parts + .meta.json) and its ranking (<run>.units.jsonl)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


def read_jsonl(path: str | Path) -> list[dict]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue  # last line of an interrupted run
    return out


def _stem(path: Path) -> str:
    return path.name.removesuffix(".jsonl")


def run_parts(path: Path) -> list[Path]:
    """The run JSONL and any per-worker parts (<run>.part-<name>.jsonl), as gne.sweep.part_paths."""
    parts = sorted(path.parent.glob(f"{_stem(path)}.part-*.jsonl"))
    return ([path] if path.exists() else []) + [q for q in parts if not q.name.endswith(".units.jsonl")]


def dose_key(d: float) -> float:
    return round(float(d), 6)


@dataclass
class Run:
    path: Path
    meta: dict
    records: list[dict]
    units: list[dict]
    baselines: dict[str, str] = field(default_factory=dict)
    rollouts: dict[tuple, dict] = field(default_factory=dict)

    @property
    def model_id(self) -> str:
        return self.meta["model_id"]

    @property
    def layer(self) -> int:
        return int(self.meta["layer"])

    def neurons(self) -> list[int]:
        return sorted({int(r["neuron"]) for r in self.records if r["kind"] == "neuron"})

    def controls(self) -> list[int]:
        return sorted({int(r["neuron"]) for r in self.records if r["kind"] == "random"})

    def random_neurons(self, k: int = 384) -> set[int] | None:
        """The neurons gne drew for `random:k` (seeded), recovered by trying plausible layer widths.

        Anything else in the sweep was hand-picked (e.g. the sharpest logit-lens neurons). Returns None when
        no seeded draw of size k, or of the whole sweep, reproduces a subset of the swept neurons.
        """
        import numpy as np

        cache = self.__dict__.setdefault("_random_neurons", {})
        if k in cache:
            return cache[k]
        have = set(self.neurons())
        seed = int(self.meta.get("seed", 0))
        found = None
        for size in sorted({k, len(have)}):
            for n_ff in range(max(512, size), 65537, 256):
                drawn = set(np.random.default_rng(seed).choice(n_ff, size=size, replace=False).tolist())
                if drawn <= have:
                    found = drawn
                    break
            if found is not None:
                break
        cache[k] = found
        return found

    def unit(self, kind: str, n: int) -> dict | None:
        return self._units.get((kind, n))

    def conditions(self, kind: str, n: int) -> list[tuple[str, float]]:
        return sorted((p, d) for (k, u, p, d) in self.rollouts if k == kind and u == n)

    def rollout(self, kind: str, n: int, prompt: str, dose: float) -> dict | None:
        return self.rollouts.get((kind, n, prompt, dose_key(dose)))

    def __post_init__(self):
        self._units = {(u["kind"], int(u["neuron"])): u for u in self.units}
        for r in self.records:
            if r["kind"] == "baseline":
                self.baselines.setdefault(r["prompt"], r["text"])
            else:
                self.rollouts[(r["kind"], int(r["neuron"]), r["prompt"], dose_key(r["dose"]))] = r


def load_run(path: str | Path) -> Run:
    """path: the sweep JSONL (e.g. ~/.gne/runs/<model_id>/L14-main_rel.jsonl). Needs `gne rank --run <name>` first."""
    path = Path(path)
    meta_path = path.with_name(_stem(path) + ".meta.json")
    units_path = path.with_name(_stem(path) + ".units.jsonl")
    if not meta_path.exists():
        raise FileNotFoundError(f"missing {meta_path}")
    if not units_path.exists():
        raise FileNotFoundError(f"missing {units_path}; run `gne rank --run {_stem(path)}` first")
    records = [r for p in run_parts(path) for r in read_jsonl(p)]
    return Run(path, json.loads(meta_path.read_text()), records, read_jsonl(units_path))
