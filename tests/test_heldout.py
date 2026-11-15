import importlib.util
from pathlib import Path

import numpy as np
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_select_is_stratified_and_pilot_is_a_prefix():
    sel = _script("heldout_select")
    units = [{"kind": "neuron", "neuron": n, "null_pct": p}
             for n, p in enumerate(np.linspace(0, 1, 200))] + [{"kind": "random", "neuron": 0, "null_pct": 0.99}]
    eligible = set(range(200)) - {0, 5}
    out = sel.select(units, eligible, n=20, pilot=8, seed=3)
    assert {k: len(v) for k, v in out["full"].items()} == {"real": 10, "border": 5, "low": 5}
    for name, ids in out["full"].items():
        assert out["pilot"][name] == ids[:len(out["pilot"][name])]
        assert set(ids) <= eligible
    by_id = {u["neuron"]: u["null_pct"] for u in units if u["kind"] == "neuron"}
    assert all(by_id[n] >= 0.95 for n in out["full"]["real"])
    assert all(0.8 <= by_id[n] < 0.95 for n in out["full"]["border"])
    with pytest.raises(SystemExit):
        sel.select(units, eligible, n=100, pilot=8, seed=3)


def test_reliability_helpers():
    rel = _script("heldout_reliability")
    assert rel.auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]) == 1.0
    assert rel.auc([0.5, 0.5, 0.5, 0.5], [0, 1, 0, 1]) == 0.5
    assert np.isnan(rel.auc([0.1, 0.2], [1, 1]))
    assert rel.spearman([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)
    splits = rel.half_splits(list("abcd"), 2, None, 0)
    assert len(splits) == 3 and all(a.isdisjoint(b) and a | b == set("abcd") for a, b in splits)


def test_configs_merge_adds_design_and_prompt_set(tmp_path):
    cfg = _script("heldout_configs")
    src = tmp_path / "src"
    (src / "prompts").mkdir(parents=True)
    (src / "designs.yaml").write_text(yaml.safe_dump({"designs": {"main_rel": {"pairs": [["who", 0.5]]}}}))
    (src / "prompts" / "default.yaml").write_text(yaml.safe_dump({"en": {"who": "Who are you?"}}))
    (src / "other.yaml").write_text("x: 1\n")
    dst = tmp_path / "dst"
    spec = cfg.merge(src, dst, REPO / "heldout" / "design.yaml")
    designs = yaml.safe_load((dst / "designs.yaml").read_text())["designs"]
    prompts = yaml.safe_load((dst / "prompts" / "default.yaml").read_text())
    assert set(designs) == {"main_rel", "heldout_rel"} and (dst / "other.yaml").exists()
    assert prompts["heldout"] == spec["prompts"] and prompts["en"] == {"who": "Who are you?"}
    assert not set(spec["prompts"]) & {"who", "snake", "orange", "free"}
    assert len(designs["heldout_rel"]["prompts"]) * len(designs["heldout_rel"]["doses"]) == 20


def test_merge_refuses_own_output(tmp_path):
    src = tmp_path / "out"
    (src / "prompts").mkdir(parents=True)
    with pytest.raises(SystemExit):
        _script("heldout_configs").merge(src, src, REPO / "heldout" / "design.yaml")
    assert src.exists()


def test_coverage_gaps_flags_partial_units():
    coverage_gaps = _script("heldout_reliability").coverage_gaps
    pairs = {("a", -0.7), ("a", 0.8)}
    recs = [{"kind": "baseline", "prompt": "a", "dose": 0.0, "neuron": None}]
    recs += [{"kind": "neuron", "prompt": "a", "dose": d, "neuron": 1} for d in (-0.7, 0.8)]
    recs += [{"kind": "random", "prompt": "a", "dose": -0.7, "neuron": 0}]
    assert coverage_gaps(recs, pairs) == ["random 0: missing 1/2"]
    assert coverage_gaps(recs[:3], pairs) == []
