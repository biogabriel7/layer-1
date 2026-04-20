"""Programmatic scoring of extraction results against deterministic rules."""

from core.text import evidence_grounded
from layer_1.pipeline.models import Metrics, ResultFile


def expected_observation_type(student_count: int) -> str:
    return "individual" if student_count == 1 else "group"


def score_programmatic(result: ResultFile, m: Metrics) -> None:
    """Evidence Grounding + Observation Type. Runs on every result."""
    # Evidence Grounding (signal-level).
    for sig in result.signals:
        m.eg_total += 1
        if evidence_grounded(sig.evidence, result.observation):
            m.eg_passed += 1
        else:
            m.eg_failures.append((result.cache_key, sig.evidence))

    # Observation Type (observation-level).
    m.ot_total += 1
    if result.observation_type == expected_observation_type(result.student_count):
        m.ot_passed += 1
