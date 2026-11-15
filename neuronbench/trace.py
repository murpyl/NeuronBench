"""Per-token "logit trace" evidence for the trace tiers, computed once with the model (scripts/trace_evidence.py).

For each choice item, every reply the agent sees (the unsteered one and the four candidates) gets one row per token:

- base_lp: log p(token) under the UNSTEERED model, teacher-forced on the chat prompt + the reply so far.
- base_top: the unsteered model's top-1 token at that position.
- lens_z: the item's neuron's logit-lens z-score for the token: W_U[token] . (gamma * W_down[:, n]), z-scored over the
  vocabulary (gne lens.logit_lens_layer, but the full row).

Nothing here may depend on the steering direction or on which reply is the answer: greedy replies are the argmax under
their own steering, so log p under any candidate's steering would point at the reply it produced. The unsteered model
is the same for all four replies and lens_z comes from the weights. Traces cover only the clipped text the agent sees,
re-tokenized from that text (the slimmed sweeps keep no token ids).
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .items import MAX_CHARS, shuffled_donors

CLIP_SUFFIX = " [...]"


def unclip(shown: str) -> str:
    """The reply text the agent sees, without items.clip's ellipsis."""
    if len(shown) == MAX_CHARS + len(CLIP_SUFFIX) and shown.endswith(CLIP_SUFFIX):
        return shown[:MAX_CHARS]
    return shown


def teacher_forced(engine, ctx, prompt_ids: list[int], reply_ids: list[int], *, chunk: int = 256
                   ) -> tuple[list[float], list[int]]:
    """(log p, top-1 id) for each reply token under the unsteered model, given the prompt and the reply so far."""
    engine.set_cvec(ctx, None)
    engine.clear_memory(ctx)
    ids = list(prompt_ids) + list(reply_ids)
    n0 = len(prompt_ids)
    lps, tops = [], []
    for c0 in range(0, len(ids) - 1, chunk):
        part = ids[c0:min(c0 + chunk, len(ids) - 1)]
        engine._decode(ctx, [(t, c0 + j, 0, c0 + j >= n0 - 1) for j, t in enumerate(part)])
        for j in range(len(part)):
            i = c0 + j
            if i < n0 - 1:
                continue
            lo = np.asarray(engine._logits(ctx, j), dtype=np.float64)
            m = lo.max()
            lps.append(float(lo[ids[i + 1]] - (m + np.log(np.exp(lo - m).sum()))))
            tops.append(int(lo.argmax()))
    return lps, tops


def lens_z_rows(weights, layer: int, neurons: list[int], chunk: int = 8192) -> dict[int, np.ndarray]:
    """{neuron: (n_vocab,) logit-lens z-scores}, as gne.lens.logit_lens_layer but keeping the whole vocabulary."""
    nn = np.asarray(sorted(set(neurons)), dtype=np.int64)
    G = np.ascontiguousarray((weights.unit_columns(layer, nn) * weights.output_norm_weight()[:, None]).T,
                             dtype=np.float32)                      # (K, n_embd)
    parts = [G @ rows.T for _, rows in weights.output_rows(chunk)]
    Z = np.concatenate(parts, axis=1).astype(np.float64)
    Z = (Z - Z.mean(1, keepdims=True)) / np.maximum(Z.std(1, keepdims=True), 1e-30)
    return {int(n): Z[k].astype(np.float32) for k, n in enumerate(nn)}


def prompt_key(item: dict, prompts: dict[str, str]) -> str:
    keys = [k for k, v in prompts.items() if v == item["payload"]["prompt"]]
    if len(keys) != 1:
        raise ValueError(f"{item['id']}: prompt not found in the sweep meta")
    return keys[0]


def build_traces(items: list[dict], metas: dict[int, dict], engine, lens: Callable[[int, list[int]], dict],
                 *, seed: int = 0) -> list[dict]:
    """One trace record per choice item, keyed by its static-tier id.

    items: static-tier item dicts; only id, kind, layer, neuron and payload are read (never answer or meta).
    metas: {layer: sweep .meta.json} for the prompts and their chat-templated `prompt_ids`.
    lens(layer, neurons) -> {neuron: (n_vocab,) z}. The donor is the neuron whose evidence the shuffled tier shows.
    """
    ch = [{k: it[k] for k in ("id", "kind", "layer", "neuron", "payload")} for it in items if it["kind"] == "choice"]
    ctx = engine.steer_ctx()
    cache: dict[tuple, dict] = {}

    def reply(pids: tuple, shown: str) -> dict:
        key = (pids, shown)
        if key not in cache:
            ids = engine.tokenize(unclip(shown), add_special=False, parse_special=False)
            lp, top = teacher_forced(engine, ctx, list(pids), ids)
            cache[key] = {"ids": ids, "tok": [engine.token_text(t) for t in ids],
                          "base_lp": [round(x, 3) for x in lp],
                          "base_top": [None if t == i else engine.token_text(t) for t, i in zip(top, ids)]}
        return cache[key]

    out = []
    for layer in sorted({it["layer"] for it in ch}):
        here = [it for it in ch if it["layer"] == layer]
        donor = shuffled_donors([it["neuron"] for it in here], seed, layer, "choice") if len(here) > 1 else {}
        z = lens(layer, sorted({it["neuron"] for it in here} | set(donor.values())))
        meta = metas[layer]
        for it in here:
            pids = tuple(meta["prompt_ids"][prompt_key(it, meta["prompts"])])
            shown = {"baseline": it["payload"]["baseline"], **it["payload"]["options"]}
            reps = {k: reply(pids, v) for k, v in shown.items()}
            neurons = [it["neuron"]] + ([donor[it["neuron"]]] if it["neuron"] in donor else [])
            out.append({"id": it["id"], "layer": layer, "neuron": it["neuron"], "donor": donor.get(it["neuron"]),
                        "replies": {k: {"text": shown[k], **{f: r[f] for f in ("ids", "tok", "base_lp", "base_top")}}
                                    for k, r in reps.items()},
                        "lens_z": {str(n): {k: [round(float(z[n][i]), 2) for i in r["ids"]] for k, r in reps.items()}
                                   for n in neurons}})
    return out


def attach(payload: dict, trace: dict, lens_neuron: int) -> dict:
    """The agent-visible trace for an item: {reply key: {tok, base_lp, base_top, lens_z}}."""
    shown = {"baseline": payload["baseline"], **payload["options"]}
    if {k: r["text"] for k, r in trace["replies"].items()} != shown:
        raise ValueError(f"trace {trace['id']} does not match the item's replies")
    z = trace["lens_z"][str(lens_neuron)]
    return {k: {"tok": r["tok"], "base_lp": r["base_lp"], "base_top": r["base_top"], "lens_z": z[k]}
            for k, r in trace["replies"].items()}
