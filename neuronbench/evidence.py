"""Evidence the agent sees: a gne neuron dossier with every measured-outcome field removed.

The dossier (`gne neuron L N --json`, or Session.neuron) mixes weight-only facts with the results of pushing the
neuron. Anything derived from pushing it (sweep rollouts and words, steer lens, evals) is the answer, so only
fields computed from the weights and from unsteered activations are kept.
"""

from __future__ import annotations

KEEP = ("layer", "neuron", "down_norm", "logit_lens", "activation", "directions", "connections", "expert",
        "expert_neuron")
LEAKY = ("sweep", "steer_lens", "evals", "gain_k", "writers", "name", "coverage", "recipe_hint")


def sanitize_dossier(dossier: dict) -> dict:
    out = {k: dossier[k] for k in KEEP if dossier.get(k) not in (None, {}, [])}
    out["available"] = sorted(k for k in out if k not in ("layer", "neuron"))
    return out
