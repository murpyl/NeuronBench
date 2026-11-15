import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

from neuronbench.baselines import run_baselines
from neuronbench.cli import load_evidence, main
from neuronbench.evidence import sanitize_dossier
from neuronbench.gne_io import load_run
from neuronbench.harbor_tasks import GRADE_PY, write_task
from neuronbench.items import build_items
from neuronbench.results import collect_jobs, summarise

REPO = Path(__file__).resolve().parents[1]
WORD_OF = dict(enumerate(["apple", "river", "castle", "violin", "pepper", "tiger", "cloud", "marble"]))


def _items(toy_run, **kw):
    run = load_run(toy_run)
    ev = load_evidence(toy_run.parent.parent / "evidence", run.model_id, run.layer)
    return run, build_items(run, ev, **{"n_choice": 6, "n_null": 6, **kw})


def test_load_run_merges_parts_and_skips_truncated_line(toy_run):
    run = load_run(toy_run)
    assert run.neurons() == list(range(8))
    assert run.controls() == list(range(100, 106))
    assert set(run.baselines) == {"who", "orange"}
    assert len(run.conditions("neuron", 0)) == 5
    assert run.rollout("random", 101, "orange", -0.7000000001) is not None


def test_choice_items_are_well_formed(toy_run):
    run, items = _items(toy_run)
    ch = [i for i in items if i.kind == "choice"]
    assert len(ch) == 6
    for it in ch:
        opts = it.payload["options"]
        assert sorted(opts) == list("ABCD") and len(set(opts.values())) == 4
        assert abs(it.payload["dose"]) <= 1.6
        real_text = run.rollout("neuron", it.neuron, next(k for k, v in run.meta["prompts"].items()
                                                         if v == it.payload["prompt"]), it.payload["dose"])["text"]
        assert opts[it.answer["letter"]] == real_text
        assert all(c >= 100 for c in it.meta["distractor_controls"])


def test_build_is_deterministic(toy_run):
    _, a = _items(toy_run)
    _, b = _items(toy_run)
    assert [asdict(x) for x in a] == [asdict(x) for x in b]


def test_null_items_split_real_and_null(toy_run):
    _, items = _items(toy_run, threshold=0.95)
    nu = [i for i in items if i.kind == "null"]
    assert len(nu) == 4 or len(nu) == 6
    assert {i.answer["real"] for i in nu} == {0, 1}
    for i in nu:
        assert i.answer["real"] == int(i.meta["null_pct"] >= 0.95)


def test_sanitize_drops_intervention_fields():
    d = {"layer": 1, "neuron": 2, "down_norm": 0.5, "sweep": {"words": ["x"]}, "steer_lens": {"up": ["y"]},
         "logit_lens": {"up": ["a"], "down": ["b"], "peak_z": 3}, "directions": {}, "evals": [1], "gain_k": [2],
         "name": "secret", "coverage": {}}
    s = sanitize_dossier(d)
    assert set(s) == {"layer", "neuron", "down_norm", "logit_lens", "available"}


def test_task_hides_answer_from_agent(toy_run, tmp_path):
    _, items = _items(toy_run)
    for it in items:
        d = write_task(it, tmp_path / "tasks")
        visible = (d / "instruction.md").read_text() + (d / "environment" / "Dockerfile").read_text()
        for k in ("null_pct", "\"mass\"", "distractor_controls", "option_change"):
            assert k not in visible
        assert json.loads((d / "tests" / "answer.json").read_text())["kind"] == it.kind


def _grade(tmp_path, key, answer):
    (tmp_path / "tests").mkdir(exist_ok=True)
    (tmp_path / "app").mkdir(exist_ok=True)
    (tmp_path / "tests" / "answer.json").write_text(json.dumps(key))
    if answer is not None:
        (tmp_path / "app" / "answer.txt").write_text(answer)
    src = GRADE_PY.replace("/tests/", f"{tmp_path}/tests/").replace("/logs/artifacts/app/", f"{tmp_path}/none/").replace("/app/", f"{tmp_path}/app/") \
        .replace("/logs/verifier", f"{tmp_path}")
    subprocess.run([sys.executable, "-c", src], check=True, capture_output=True)
    return json.loads((tmp_path / "reward.json").read_text())


def test_grader(tmp_path):
    assert _grade(tmp_path, {"kind": "choice", "letter": "C"}, "C\n") == {"choice_acc": 1}
    assert _grade(tmp_path, {"kind": "choice", "letter": "C"}, "The answer is B") == {"choice_acc": 0}
    assert _grade(tmp_path, {"kind": "null", "real": 1}, "0.8") == {"null_brier": 1 - 0.2 ** 2}
    assert _grade(tmp_path, {"kind": "null", "real": 0}, "70%") == {"null_brier": 1 - 0.7 ** 2}
    assert _grade(tmp_path, {"kind": "null", "real": 0}, "7") == {"null_brier": 0.0}
    (tmp_path / "app" / "answer.txt").unlink()
    assert _grade(tmp_path, {"kind": "null", "real": 1}, None) == {"null_brier": 0.0}


def test_metric(tmp_path):
    inp = tmp_path / "rewards.jsonl"
    inp.write_text('{"choice_acc": 1}\n{"choice_acc": 0}\n{"null_brier": 0.75}\nnull\n')
    out = tmp_path / "m.json"
    subprocess.run([sys.executable, str(REPO / "dataset" / "metric.py"), "-i", str(inp), "-o", str(out)], check=True)
    m = json.loads(out.read_text())
    assert m["choice_accuracy"] == 0.5 and abs(m["null_brier"] - 0.25) < 1e-9 and m["n_failed"] == 1


def test_baselines_and_collect(toy_run, tmp_path):
    _, items = _items(toy_run)
    dicts = [asdict(i) for i in items]
    scores = run_baselines(dicts)
    assert {"random", "most_different", "logit_lens", "always_null", "base_rate", "evidence_logreg"} <= set(scores)
    # the toy neurons write their logit-lens word, so the logit-lens baseline is perfect here
    assert all(v == 1.0 for v in scores["logit_lens"].values())
    job = tmp_path / "jobs" / "j1"
    for i, it in enumerate(dicts):
        t = job / f"trial{i}"
        t.mkdir(parents=True)
        key = "choice_acc" if it["kind"] == "choice" else "null_brier"
        t.joinpath("result.json").write_text(json.dumps({
            "task_name": "neuronbench/" + it["id"].replace("+", "p"),
            "agent_info": {"name": "mini-swe-agent", "model_info": {"name": "m1"}},
            "verifier_result": {"rewards": {key: 1.0}}}))
    got = collect_jobs([tmp_path / "jobs"], dicts)
    assert set(got) == {"m1"} and len(got["m1"]) == len(dicts)
    rows = {r["kind"]: r for r in summarise(got, dicts)}
    assert rows["choice"]["value"] == 1.0 and rows["null"]["value"] == 0.0


def test_cli_build(toy_run, tmp_path):
    out = tmp_path / "tasks"
    main(["build", "--run", str(toy_run), "--evidence", str(toy_run.parent.parent / "evidence"),
          "--items", str(tmp_path / "items.jsonl"), "--out", str(out), "--n-choice", "4", "--n-null", "4"])
    tasks = [p for p in out.iterdir() if p.is_dir()]
    assert len(tasks) == len((tmp_path / "items.jsonl").read_text().splitlines())
    assert not (out / "metric.py").exists()  # Valkyrie rejects a dataset containing metric.py
    for t in tasks:
        toml = (t / "task.toml").read_text()
        assert 'network_mode = "allowlist"' in toml and '"api.anthropic.com"' in toml
        assert (t / "tests" / "test.sh").stat().st_mode & 0o111


def test_collect_valkyrie_export(tmp_path):
    from neuronbench.harbor_tasks import safe_name
    from neuronbench.results import collect_jobs
    items = [{"id": "m/L1/N1/choice", "kind": "choice"}, {"id": "m/L1/N2/null", "kind": "null"}]
    export = {"benchmark_id": "run1", "benchmark_arguments": {"contract": {"model": "anthropic/claude-haiku-4-5"}},
              "evaluation_results": {safe_name(items[0]["id"]): {"rewards": {"choice_acc": 1.0}},
                                     safe_name(items[1]["id"]): {"rewards": {"null_brier": 0.75}},
                                     "unrelated-task": {"rewards": {"reward": 1.0}}}}
    (tmp_path / "haiku.json").write_text(json.dumps(export))
    want = {"anthropic/claude-haiku-4-5": {"m/L1/N1/choice": 1.0, "m/L1/N2/null": 0.75}}
    assert collect_jobs([tmp_path / "haiku.json"], items) == want  # --jobs jobs/* passes files
    got = collect_jobs([tmp_path], items)
    assert got == {"anthropic/claude-haiku-4-5": {"m/L1/N1/choice": 1.0, "m/L1/N2/null": 0.75}}


def test_selection_tags_hand_picked_neurons(tmp_path):
    import numpy as np

    from neuronbench.gne_io import Run

    drawn = set(np.random.default_rng(0).choice(3072, size=384, replace=False).tolist())
    extra = next(i for i in range(3072) if i not in drawn)
    recs = [{"kind": "neuron", "neuron": n, "prompt": "who", "dose": 0.5, "text": ""} for n in sorted(drawn | {extra})]
    run = Run(path=tmp_path, meta={"model_id": "m", "layer": 1, "seed": 0}, records=recs, units=[])
    assert run.random_neurons() == drawn
    assert extra not in run.random_neurons()


def test_selection_small_sweep_and_unknown(tmp_path):
    import numpy as np

    from neuronbench.gne_io import Run

    small = set(np.random.default_rng(0).choice(3072, size=24, replace=False).tolist())
    recs = [{"kind": "neuron", "neuron": n, "prompt": "who", "dose": 0.5, "text": ""} for n in sorted(small)]
    run = Run(path=tmp_path, meta={"model_id": "m", "layer": 1, "seed": 0}, records=recs, units=[])
    assert run.random_neurons() == small
    picked = [{"kind": "neuron", "neuron": n, "prompt": "who", "dose": 0.5, "text": ""} for n in (1, 2, 3)]
    run = Run(path=tmp_path, meta={"model_id": "m", "layer": 1, "seed": 0}, records=picked, units=[])
    assert run.random_neurons() is None
    assert run.random_neurons(k=3) is None
    big = set(np.random.default_rng(0).choice(3072, size=600, replace=False).tolist())
    recs = [{"kind": "neuron", "neuron": n, "prompt": "who", "dose": 0.5, "text": ""} for n in sorted(big)]
    run = Run(path=tmp_path, meta={"model_id": "m", "layer": 1, "seed": 0}, records=recs, units=[])
    assert run.random_neurons() == big


def test_control_tiers_pair_with_static_items(toy_run, tmp_path):
    _, static = _items(toy_run)
    for tier, fields in (("oracle", ("sweep_words",)), ("transfer", ("steered_elsewhere", "steered_replies"))):
        _, items = _items(toy_run, tier=tier)
        assert len(items) == len(static)
        for s, t in zip(static, items):
            assert t.id == s.id.replace(f"{s.kind}-", f"{s.kind}-{tier}-", 1)
            assert (t.payload, t.answer, t.neuron) == (s.payload, s.answer, s.neuron)
            assert any(f in t.evidence for f in fields) and set(t.evidence["available"]) >= set(s.evidence["available"])
            visible = (write_task(t, tmp_path / tier) / "instruction.md").read_text()
            assert "(measured)" in visible and "null_pct" not in visible and "\"mass\"" not in visible
        ch = [t for t in items if t.kind == "choice"]
        if tier == "oracle":
            assert all(t.evidence["sweep_words"] == [WORD_OF[t.neuron]] for t in ch)
        else:
            assert all(t.payload["prompt"] not in t.evidence["steered_elsewhere"] for t in ch)
            assert any(t.evidence["steered_elsewhere"] for t in ch)
    assert all("(measured)" not in (write_task(s, tmp_path / "static") / "instruction.md").read_text() for s in static)


def test_shuffled_tier_swaps_in_another_same_layer_neurons_evidence(toy_run, tmp_path):
    run, static = _items(toy_run)
    ev = load_evidence(toy_run.parent.parent / "evidence", run.model_id, run.layer)
    _, items = _items(toy_run, tier="shuffled")
    assert _items(toy_run, tier="shuffled")[1] == items  # deterministic
    assert len(items) == len(static)
    donors = {"choice": {}, "null": {}}
    for s, t in zip(static, items):
        assert t.id == s.id.replace(f"{s.kind}-", f"{s.kind}-shuffled-", 1)
        assert (t.payload, t.answer, t.neuron, t.layer) == (s.payload, s.answer, s.neuron, s.layer)
        d = t.meta["evidence_neuron"]
        assert d != t.neuron and d in {i.neuron for i in static if i.kind == t.kind}
        assert t.neuron not in donors[t.kind]
        donors[t.kind][t.neuron] = d
        assert (t.evidence["layer"], t.evidence["neuron"]) == (t.layer, t.neuron)
        assert {k: v for k, v in t.evidence.items() if k not in ("layer", "neuron")} == \
            {k: v for k, v in ev[d].items() if k not in ("layer", "neuron")}
        assert list(t.evidence) == list(s.evidence)
        visible = (write_task(t, tmp_path / "shuffled") / "instruction.md").read_text()
        assert "shuffled" not in visible and "(measured)" not in visible and f"neuron {d}" not in visible
    for m in donors.values():  # a permutation within each kind: each static evidence block of that kind shown once
        assert sorted(m.values()) == sorted(m)


def test_shuffled_tier_single_kind(toy_run):
    for kw in ({"n_choice": 0}, {"n_null": 0}):
        _, items = _items(toy_run, tier="shuffled", **kw)
        assert items and len({i.kind for i in items}) == 1
        assert all(i.meta["evidence_neuron"] != i.neuron for i in items)


def test_shuffled_donors_is_a_derangement():
    from neuronbench.items import shuffled_donors

    for k in (2, 3, 10, 85):
        for seed in range(5):
            m = shuffled_donors(list(range(k)) * 2, seed, 14, "choice")
            assert sorted(m) == sorted(m.values()) == list(range(k)) and all(a != b for a, b in m.items())
