"""Layer 1 output schema — the contract between Layer 1 and downstream layers.

Lives in `core` because Layer 1.5 (and any future consumer) reads Layer 1's
output and must be able to parse it without importing from layer_1.*.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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
