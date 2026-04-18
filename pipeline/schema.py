"""Pydantic models for the Layer 1 LLM boundaries.

These types define the contract between:
  - the extractor LLM's response  →  `ExtractionOutput`
  - the audit LLM's response      →  `AuditResponse`

Validation raises `ValidationError` on a malformed response, which surfaces
prompt-compliance failures loudly instead of silently masking them.

`extra="allow"` on the top-level models is intentional: if the prompt is
updated to emit an additional field before the schema catches up, we don't
want validation to hard-fail — the extra field just passes through.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Extraction output — what extract.py expects back from the extractor LLM
# ---------------------------------------------------------------------------

SignalType = Literal[
    "behavioral_evidence",
    "emotional_indicator",
    "context_marker",
    "concern_flag",
]

Confidence = Literal["high", "medium", "low"]

Valence = Literal["positive", "negative", "mixed", "neutral"]

Target = Literal[
    "self", "peer", "group", "adult", "task", "object", "environment"
]

Agency = Literal["self_initiated", "prompted", "scaffolded", "external"]

TemporalityCue = Literal["first_time", "recurring", "change", "one_time"]

DomainDescriptor = Literal[
    "body", "speech", "task", "peer", "adult", "feeling", "creation", "norm"
]

ParticipantRole = Literal[
    "actor", "recipient", "self", "group_member", "bystander"
]


class Participant(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    role: ParticipantRole | None = None


class Signal(BaseModel):
    model_config = ConfigDict(extra="allow")

    evidence: str
    type: SignalType
    confidence: Confidence
    valence: Valence | None = None
    target: Target | None = None
    agency: Agency | None = None
    temporality_cue: TemporalityCue | None = None
    domain_descriptors: list[DomainDescriptor] = Field(default_factory=list)
    participants: list[Participant] = Field(default_factory=list)
    reasoning: str


class ExtractionOutput(BaseModel):
    """Shape of what the extractor LLM returns *before* post-processing."""

    model_config = ConfigDict(extra="allow")

    language: str
    source_type: Literal["teacher_observation"]
    named_students: list[str]
    signals: list[Signal]


# ---------------------------------------------------------------------------
# Audit output — what pipeline/judge.py expects back from the audit LLM
# ---------------------------------------------------------------------------


class AuditCheck(BaseModel):
    model_config = ConfigDict(extra="allow")

    passed: bool
    note: str = ""


class AuditChecks(BaseModel):
    model_config = ConfigDict(extra="allow")

    evidence_grounded: AuditCheck
    reasoning_justifies_classification: AuditCheck
    no_over_extraction: AuditCheck


class AuditSignalEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_index: int
    evidence: str
    checks: AuditChecks


class AuditResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    per_signal: list[AuditSignalEntry] = Field(default_factory=list)
    summary: str = ""
