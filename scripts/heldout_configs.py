"""Copy gne's configs and add the Eval 2 held-out design, so `gne sweep --design heldout_rel --prompt-set heldout` works.

Run with gne's Python (it reads gne.store.CONFIGS), then point gne at the copy:

    python scripts/heldout_configs.py
    export GNE_CONFIGS=$PWD/heldout/gne-configs
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def merge(src: Path, dst: Path, design_path: Path) -> dict:
    spec = yaml.safe_load(design_path.read_text(encoding="utf-8"))
    src_r, dst_r = src.resolve(), dst.resolve()
    if src_r == dst_r or dst_r in src_r.parents:
        raise SystemExit(f"--src {src} is inside --out {dst}; unset GNE_CONFIGS or pass --src gne's own configs dir")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    designs_p, prompts_p = dst / "designs.yaml", dst / "prompts" / "default.yaml"
    designs = yaml.safe_load(designs_p.read_text(encoding="utf-8"))
    prompts = yaml.safe_load(prompts_p.read_text(encoding="utf-8"))
    designs["designs"]["heldout_rel"] = {"prompts": list(spec["prompts"]), "doses": [float(d) for d in spec["doses"]]}
    prompts["heldout"] = dict(spec["prompts"])
    designs_p.write_text(yaml.safe_dump(designs, allow_unicode=True, sort_keys=False), encoding="utf-8")
    prompts_p.write_text(yaml.safe_dump(prompts, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return spec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=None, help="gne configs dir (default: gne.store.CONFIGS)")
    ap.add_argument("--out", default=str(ROOT / "heldout" / "gne-configs"))
    ap.add_argument("--design", default=str(ROOT / "heldout" / "design.yaml"))
    a = ap.parse_args()
    if a.src is None:
        from gne.store import CONFIGS
        a.src = str(CONFIGS)
    spec = merge(Path(a.src), Path(a.out), Path(a.design))
    n = len(spec["prompts"]) * len(spec["doses"])
    print(f"{a.out}: design heldout_rel, prompt set heldout ({len(spec['prompts'])} prompts x "
          f"{len(spec['doses'])} doses = {n} rollouts/unit)\nexport GNE_CONFIGS={Path(a.out).resolve()}")


if __name__ == "__main__":
    main()
