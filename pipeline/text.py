"""Text normalization and evidence-matching helpers."""

import hashlib
import re


def cache_key(observation_id: str) -> str:
    """SHA256 of the stable observation_id. Golden-sourced extractions use a
    synthetic id of form 'golden-NNN'."""
    return hashlib.sha256(observation_id.encode()).hexdigest()


def normalize(s: str) -> str:
    """Lowercase, collapse whitespace, strip surrounding punctuation/quotes."""
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    return s.strip(" \t\n\r\"'“”‘’.,;:!?")


def evidence_grounded(evidence: str, observation: str) -> bool:
    """Evidence must appear verbatim in the observation (normalized)."""
    ne = normalize(evidence)
    no = normalize(observation)
    if not ne:
        return False
    return ne in no
