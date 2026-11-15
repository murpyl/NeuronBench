import importlib.util
import json
from dataclasses import asdict
from pathlib import Path

from neuronbench.harbor_tasks import GRADE_PY
from neuronbench.items import Item

REPO = Path(__file__).resolve().parents[1]


def _script(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dense = _script("dense_report")


def test_parse_ranking_with_and_without_probabilities():
    assert dense.parse_ranking("B 0.55, D 0.25, A 0.15, C 0.05") == (list("BDAC"), {"B": 0.55, "D": 0.25, "A": 0.15,
                                                                                  "C": 0.05})
    order, probs = dense.parse_ranking("c: 40%, a: 30%, b: 20%, d: 10%")
    assert order == list("CABD") and abs(probs["C"] - 0.4) < 1e-9
    assert dense.parse_ranking("B") == (["B"], None)
    assert dense.parse_ranking("B 0.9, D 0.9, A 0.1, C 0.1")[1] is None
    assert dense.parse_ranking("") == ([], None)


def test_rank_score_and_letter_brier():
    assert [dense.rank_score(list("BDAC"), k) for k in "BDAC"] == [1.0, 2 / 3, 1 / 3, 0.0]
    assert dense.rank_score(["B"], "B") == 1.0
    assert abs(dense.rank_score(["B"], "A") - 1 / 3) < 1e-9
    assert dense.rank_score([], "A") == 0.0
    uniform = {k: 0.25 for k in "ABCD"}
    assert abs(dense.letter_brier(list("ABCD"), uniform, "A") - 0.375) < 1e-9
    assert dense.letter_brier(["A"], None, "A") == 0.0 and dense.letter_brier(["B"], None, "A") == 1.0


def test_score_item_null_uses_continuous_null_pct():
    it = {"id": "null-x-L1-N1", "kind": "null", "layer": 1, "answer": {"real": 0}, "meta": {"null_pct": 0.9}}
    row = dense.score_item(it, {"raw": "0.8", "parsed": 0.8, "rewards": {}})
    assert abs(row["brier"] - 0.64) < 1e-9 and abs(row["dense_brier"] - 0.01) < 1e-9
    assert dense.score_item(it, {"raw": "", "parsed": None, "rewards": {}})["dense_brier"] == 1.0


def test_rank_tasks_keep_grader_and_top1(toy_run, tmp_path, monkeypatch):
    from neuronbench.cli import load_evidence
    from neuronbench.gne_io import load_run
    from neuronbench.items import build_items

    run = load_run(toy_run)
    ev = load_evidence(toy_run.parent.parent / "evidence", run.model_id, run.layer)
    items = build_items(run, ev, n_choice=2, n_null=2)
    path = tmp_path / "items.jsonl"
    path.write_text("".join(json.dumps(asdict(i)) + "\n" for i in items))
    rank = _script("rank_tasks")
    monkeypatch.setattr("sys.argv", ["rank_tasks", "--items", str(path), "--out", str(tmp_path / "t")])
    rank.main()
    choice = next(i for i in items if i.kind == "choice")
    assert isinstance(choice, Item)
    d = tmp_path / "t" / choice.id.replace("+", "p")
    text = (d / "instruction.md").read_text()
    assert rank.RANK_ANSWER in text and rank.BINARY_ANSWER not in text
    assert (d / "tests" / "grade.py").read_text() == GRADE_PY
