# /// script
# dependencies = []
# ///
"""NeuronBench dataset metric.

Each reward line is {"choice_acc": 0|1} (which-output task), {"null_brier": 1 - (p - y)^2} (real-or-null task),
or null for a trial that crashed (scored as 0 and counted in n_failed). Reports accuracy, Brier score and 95%
bootstrap confidence intervals per task.
"""

import argparse
import json
import random
from pathlib import Path


def ci(values: list[float], n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    means = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(n_boot))
    return means[int(0.025 * n_boot)], means[int(0.975 * n_boot) - 1]


def main(input_path: Path, output_path: Path):
    by_kind: dict[str, list[float]] = {"choice_acc": [], "null_brier": []}
    failed = 0
    for line in input_path.read_text().splitlines():
        r = json.loads(line)
        if r is None:
            failed += 1
            continue
        for k, v in r.items():
            by_kind.setdefault(k, []).append(float(v))
    out: dict[str, float | int] = {"n_failed": failed}
    acc = by_kind["choice_acc"]
    if acc:
        lo, hi = ci(acc)
        out.update(choice_accuracy=sum(acc) / len(acc), choice_accuracy_lo=lo, choice_accuracy_hi=hi, n_choice=len(acc))
    br = by_kind["null_brier"]
    if br:
        lo, hi = ci(br)
        out.update(null_brier=1 - sum(br) / len(br), null_brier_lo=1 - hi, null_brier_hi=1 - lo, n_null=len(br))
    all_r = acc + br
    out["mean"] = sum(all_r) / (len(all_r) + failed) if (all_r or failed) else 0.0
    output_path.write_text(json.dumps(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--input-path", type=Path, required=True)
    ap.add_argument("-o", "--output-path", type=Path, required=True)
    a = ap.parse_args()
    main(a.input_path, a.output_path)
