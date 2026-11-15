import json
import zlib
from dataclasses import asdict

import numpy as np
import pytest

from neuronbench.baselines import TRACE_STATS, run_baselines
from neuronbench.cli import load_evidence
from neuronbench.gne_io import load_run
from neuronbench.harbor_tasks import write_task
from neuronbench.items import build_items
from neuronbench.trace import build_traces, unclip

PROMPT_IDS = {"who": [901, 902], "orange": [903, 904, 905]}
N_VOCAB = 1000


class FakeEngine:
    """Unsteered logits are a hash of the token prefix; any non-empty control vector is an error."""

    def __init__(self):
        self.words: dict[int, str] = {}
        self.seq: list[int] = []
        self.batch: list[tuple] = []
        self.cvec_calls: list = []

    def steer_ctx(self):
        return object()

    def set_cvec(self, ctx, vectors, **kw):
        self.cvec_calls.append(vectors)
        if vectors:
            raise AssertionError("trace evidence must come from the unsteered model")

    def clear_memory(self, ctx):
        self.seq = []

    def tokenize(self, text, *, add_special=False, parse_special=True):
        ids = [zlib.crc32(w.encode()) % 800 + 1 for w in text.split(" ")]
        self.words.update(zip(ids, text.split(" ")))
        return ids

    def token_text(self, tok):
        return self.words.get(tok, f"<{tok}>")

    def _decode(self, ctx, items):
        for tok, pos, _, _ in items:
            assert pos == len(self.seq)
            self.seq.append(tok)
        self.batch = items

    def _logits(self, ctx, j):
        pos = self.batch[j][1]
        rng = np.random.default_rng(zlib.crc32(json.dumps(self.seq[:pos + 1]).encode()))
        lo = rng.normal(size=N_VOCAB)
        return lo


def fake_lens(layer, neurons):
    return {n: np.array([((n * 7919 + i * 104729) % 1000) / 100 - 5 for i in range(N_VOCAB)]) for n in neurons}


def _static(toy_run, **kw):
    run = load_run(toy_run)
    ev = load_evidence(toy_run.parent.parent / "evidence", run.model_id, run.layer)
    return run, ev, build_items(run, ev, **{"n_choice": 6, "n_null": 6, **kw})


def _traces(run, items, engine=None):
    metas = {run.layer: {**run.meta, "prompt_ids": PROMPT_IDS}}
    # only what the agent sees is passed in: no answer, no meta (strata, distractor ids)
    visible = [{k: v for k, v in asdict(it).items() if k not in ("answer", "meta")} for it in items]
    return build_traces(visible, metas, engine or FakeEngine(), fake_lens)


def test_trace_fields_do_not_depend_on_steering_or_answer(toy_run):
    run, _, items = _static(toy_run)
    eng = FakeEngine()
    traces = _traces(run, items, eng)
    assert eng.cvec_calls and all(not v for v in eng.cvec_calls)
    ch = [it for it in items if it.kind == "choice"]
    assert [t["id"] for t in traces] == [it.id for it in ch]
    # base_lp / base_top are a function of (prompt, shown text) only, lens_z of (neuron, tokens) only: the same text
    # gets the same rows whichever letter it sits under and whichever reply is the answer
    by_text: dict[tuple, dict] = {}
    for it, t in zip(ch, traces):
        for k, r in t["replies"].items():
            key = (it.payload["prompt"], r["text"])
            row = {f: r[f] for f in ("tok", "base_lp", "base_top")}
            assert by_text.setdefault(key, row) == row
            z = fake_lens(run.layer, [it.neuron])[it.neuron]
            assert t["lens_z"][str(it.neuron)][k] == [round(float(z[i]), 2) for i in r["ids"]]
    # moving every answer to another letter leaves each text's rows unchanged
    for it in ch:
        opts = it.payload["options"]
        letters = list(opts)
        it.payload["options"] = {L: opts[letters[(i + 1) % 4]] for i, L in enumerate(letters)}
    moved = _traces(run, items)
    for t0, t1 in zip(traces, moved):
        a = {r["text"]: (r["base_lp"], r["base_top"], t0["lens_z"][str(t0["neuron"])][k])
             for k, r in t0["replies"].items()}
        b = {r["text"]: (r["base_lp"], r["base_top"], t1["lens_z"][str(t1["neuron"])][k])
             for k, r in t1["replies"].items()}
        assert a == b


def test_trace_tiers_pair_with_static_and_shuffled(toy_run, tmp_path):
    run, _, static = _static(toy_run)
    traces = {t["id"]: t for t in _traces(run, static)}
    _, _, shuffled = _static(toy_run, tier="shuffled")
    for tier, ref in (("trace", static), ("trace-shuffled", shuffled)):
        _, _, items = _static(toy_run, tier=tier, traces=traces)
        assert len(items) == len(ref)
        for r, t in zip(ref, items):
            base = r.id if tier == "trace" else r.id.replace("-shuffled-", "-", 1)
            assert t.id == base.replace(f"{r.kind}-", f"{r.kind}-{tier}-", 1)
            assert (t.evidence, t.answer, t.neuron) == (r.evidence, r.answer, r.neuron)
            assert {k: v for k, v in t.payload.items() if k != "trace"} == r.payload
            visible = (write_task(t, tmp_path / tier) / "instruction.md").read_text()
            assert "null_pct" not in visible and "evidence_neuron" not in visible
            if t.kind == "null":
                assert "trace" not in t.payload and "Per-token trace" not in visible
                continue
            tr = t.payload["trace"]
            assert set(tr) == {"baseline", *"ABCD"}
            lens_n = t.meta.get("evidence_neuron", t.neuron)
            assert tier == "trace" or lens_n != t.neuron
            z = fake_lens(run.layer, [lens_n])[lens_n]
            src = traces[base]["replies"]
            for k, row in tr.items():
                assert set(row) == {"tok", "base_lp", "base_top", "lens_z"}
                assert row["lens_z"] == [round(float(z[i]), 2) for i in src[k]["ids"]]
                assert len(row["tok"]) == len(row["base_lp"]) == len(row["base_top"]) == len(row["lens_z"])
            assert visible.count("Per-token trace:") == 5 and "## Per-token trace" in visible
            assert "base_lp" in visible and "lens_z" in visible


def test_trace_must_match_the_items_replies(toy_run):
    run, _, static = _static(toy_run)
    traces = {t["id"]: t for t in _traces(run, static)}
    t = next(iter(traces.values()))
    t["replies"]["A"]["text"] += " edited"
    with pytest.raises(ValueError, match="does not match"):
        _static(toy_run, tier="trace", traces=traces)
    with pytest.raises(ValueError, match="needs traces"):
        _static(toy_run, tier="trace")


def test_trace_baselines(toy_run):
    run, _, static = _static(toy_run)
    traces = {t["id"]: t for t in _traces(run, static)}
    _, _, items = _static(toy_run, tier="trace", traces=traces)
    scores = run_baselines([asdict(i) for i in items])
    for name in TRACE_STATS:
        assert set(scores[name]) == {i.id for i in items if i.kind == "choice"}
        assert set(scores[name].values()) <= {0.0, 1.0}
    assert "trace_lens_mean" not in run_baselines([asdict(i) for i in static])


def test_unclip():
    from neuronbench.items import MAX_CHARS, clip

    long = "x" * (MAX_CHARS + 50)
    assert unclip(clip(long)) == long[:MAX_CHARS] and unclip("short [...]") == "short [...]"
