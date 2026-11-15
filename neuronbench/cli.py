"""neuronbench build | baselines | report."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from .gne_io import load_run
from .harbor_tasks import write_task
from .items import build_items
from .results import by_selection, by_stratum, collect_jobs, load_items, markdown_table, plot, summarise


def load_evidence(root: Path, model_id: str, layer: int) -> dict[int, dict]:
    d = root / model_id / f"L{layer}"
    return {int(p.stem[1:]): json.loads(p.read_text()) for p in d.glob("N*.json")} if d.exists() else {}


def cmd_build(a):
    hosts = [h.strip() for h in a.allowed_hosts.split(",") if h.strip()]
    if any("*" in h for h in hosts):
        sys.exit("--allowed-hosts takes exact hostnames; Valkyrie does not accept wildcards")
    items = []
    for rp in a.run:
        run = load_run(rp)
        ev = load_evidence(Path(a.evidence), run.model_id, run.layer)
        if not ev:
            raise SystemExit(f"no evidence for {run.model_id} L{run.layer} under {a.evidence}")
        got = build_items(run, ev, n_choice=a.n_choice, n_null=a.n_null, seed=a.seed, threshold=a.threshold,
                          min_change=a.min_change)
        nc = sum(i.kind == "choice" for i in got)
        nr = sum(i.kind == "null" and i.answer["real"] for i in got)
        npick = sum(i.meta.get("selection") == "picked" for i in got)
        print(f"{rp}: {nc} choice, {len(got) - nc} null ({nr} real); {npick} items on hand-picked neurons")
        items += got
    dupes = sorted({i.id for i in items if [j.id for j in items].count(i.id) > 1})
    if dupes:
        sys.exit(f"duplicate item ids across runs (same model name, different revision?): {dupes[:5]}")
    Path(a.items).parent.mkdir(parents=True, exist_ok=True)
    Path(a.items).write_text("".join(json.dumps(asdict(i), ensure_ascii=False) + "\n" for i in items))
    out = Path(a.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for it in items:
        write_task(it, out, agent_timeout=a.agent_timeout, allowed_hosts=hosts)
    print(f"wrote {len(items)} items to {a.items} and Harbor tasks to {out}/")


def cmd_baselines(a):
    from .baselines import run_baselines
    items = load_items(a.items)
    scores = run_baselines(items)
    print(markdown_table(summarise(scores, items)))
    if a.out:
        Path(a.out).write_text(json.dumps(scores))


def cmd_report(a):
    from .baselines import run_baselines
    items = load_items(a.items)
    base = run_baselines(items)
    models = collect_jobs(a.jobs, items) if a.jobs else {}
    scores = {**{f"baseline:{k}": v for k, v in base.items()}, **models}
    rows = summarise(scores, items)
    table = markdown_table(rows)
    print(table)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sel_rows = by_selection(scores, items)
    (out / "results.md").write_text(table + "\n")
    (out / "results_by_selection.md").write_text(markdown_table(sel_rows) + "\n")
    (out / "results.json").write_text(json.dumps({"rows": rows, "by_selection": sel_rows, "scores": scores}, indent=1))
    try:
        paths = plot(rows, by_stratum(scores, items), out, {k for k in scores if k.startswith("baseline:")})
        print("plots:", ", ".join(map(str, paths)))
    except ImportError:
        print("matplotlib not installed; skipping plots (pip install -e '.[plots]')")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="neuronbench")
    sub = ap.add_subparsers(required=True)
    b = sub.add_parser("build", help="gne sweeps + evidence -> items.jsonl + Harbor task folders")
    b.add_argument("--run", nargs="+", action="extend", required=True, help="gne sweep JSONL(s), already ranked")
    b.add_argument("--evidence", default="data/evidence")
    b.add_argument("--items", default="data/items.jsonl")
    b.add_argument("--out", default="tasks")
    b.add_argument("--n-choice", type=int, default=30, help="choice items per run")
    b.add_argument("--n-null", type=int, default=20, help="null items per run")
    b.add_argument("--seed", type=int, default=0)
    b.add_argument("--threshold", type=float, default=0.95, help="null_pct at or above which a neuron is REAL")
    b.add_argument("--min-change", type=float, default=0.1)
    b.add_argument("--agent-timeout", type=float, default=600.0)
    b.add_argument("--allowed-hosts", default="api.anthropic.com,api.openai.com",
                   help="comma-separated exact hostnames the agent container may reach (its model API); "
                        "empty string = unrestricted network")
    b.set_defaults(fn=cmd_build)
    s = sub.add_parser("baselines", help="score agent-free baselines on items.jsonl")
    s.add_argument("--items", default="data/items.jsonl")
    s.add_argument("--out", default=None)
    s.set_defaults(fn=cmd_baselines)
    r = sub.add_parser("report", help="baselines + Harbor job results -> results.md, results.json, plots")
    r.add_argument("--items", default="data/items.jsonl")
    r.add_argument("--jobs", nargs="*", default=[], help="Harbor job directories")
    r.add_argument("--out", default="results")
    r.set_defaults(fn=cmd_report)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
