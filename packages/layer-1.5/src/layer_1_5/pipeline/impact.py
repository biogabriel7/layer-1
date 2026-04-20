"""Deterministic profile_impact roll-up from per-signal salience.

Kept alongside the LLM's own profile_impact for calibration — if the two
disagree on a record, both values are preserved in the JSONL output.
"""

from collections.abc import Iterable

from core.schema.layer1_5 import ContextualizedSignal, ProfileImpact


def rollup_profile_impact(signals: Iterable[ContextualizedSignal]) -> ProfileImpact:
    sigs = list(signals)
    if any(s.salience == "significant" for s in sigs):
        return "high"
    if any(s.salience == "notable" for s in sigs):
        return "moderate"
    return "minimal"
