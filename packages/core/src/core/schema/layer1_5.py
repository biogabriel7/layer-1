"""Layer 1.5 output schema — contextualized signals attached to a student.

Lives in `core` so downstream layers can consume Layer 1.5 output without
importing from layer_1_5.*. Mirrors layer1.py's style: ConfigDict(extra="allow")
at the LLM boundary, Pydantic raises on required-field violations.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from core.schema.layer1 import Confidence, ParticipantRole

Novelty = Literal["new", "reinforcing", "contradicting"]

Salience = Literal["routine", "notable", "significant"]

ProfileImpact = Literal["minimal", "moderate", "high"]

AttributionSource = Literal["tagged", "named_match", "group_uniform"]

SecondaryMatchKind = Literal[
    "full_name",
    "first_last",
    "first_name_unique_in_crew",
    "first_name_unique_client",
    "llm_resolved",
]


class StudentAttribution(BaseModel):
    model_config = ConfigDict(extra="allow")

    source: AttributionSource
    role: ParticipantRole | None = None
    group_context: bool = False
    group_size: int = 1
    confidence: Confidence | None = None
    reasoning: str | None = None


class ContextualizedSignal(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_index: int
    role: ParticipantRole | None = None
    novelty: Novelty | None = None
    salience: Salience
    reasoning: str


class HistorySummary(BaseModel):
    model_config = ConfigDict(extra="allow")

    prior_observation_count: int
    prior_signal_count: int
    prior_individual_signal_count: int = 0
    prior_group_signal_count: int = 0
    prior_concern_flag_count: int = 0
    is_first_observation: bool
    prior_signals_by_type: dict[str, int] = Field(default_factory=dict)
    prior_domain_frequency: dict[str, int] = Field(default_factory=dict)
    prior_valence_distribution: dict[str, int] = Field(default_factory=dict)
    recent_evidence_snippets: list[dict[str, Any]] = Field(default_factory=list)


class SecondaryParticipant(BaseModel):
    model_config = ConfigDict(extra="allow")

    student_id: str
    name_in_text: str
    match: SecondaryMatchKind


class ContextualizationOutput(BaseModel):
    """One JSONL record per (observation_id, student_id, role) triple."""

    model_config = ConfigDict(extra="allow")

    schema_version: Literal["v1"]
    source: dict[str, str]
    language: str | None = None
    attribution: StudentAttribution
    contextualized_signals: list[ContextualizedSignal]
    profile_impact: ProfileImpact
    narrative: str
    history_summary: HistorySummary
    secondary_participants: list[SecondaryParticipant] = Field(default_factory=list)


class _AttributionAssignment(BaseModel):
    model_config = ConfigDict(extra="allow")

    student_id: str
    role: ParticipantRole


class _AttributionEntry(BaseModel):
    """One per Layer 1 signal — lists every tagged student the signal belongs
    to and their role (actor / recipient / group_member / bystander)."""

    model_config = ConfigDict(extra="allow")

    signal_index: int
    assignments: list[_AttributionAssignment]
    source: AttributionSource
    confidence: Confidence | None = None
    reasoning: str | None = None


class _SecondaryEntry(BaseModel):
    model_config = ConfigDict(extra="allow")

    name_in_text: str
    # LLM may return null when it declines to pick a candidate — we filter
    # these out downstream rather than failing the whole response.
    student_id: str | None = None
    match_kind: SecondaryMatchKind = "llm_resolved"
    reasoning: str | None = None


class AttributionLLMResponse(BaseModel):
    """Shape the Attribution LLM must return."""

    model_config = ConfigDict(extra="allow")

    signal_attributions: list[_AttributionEntry]
    secondary_participants: list[_SecondaryEntry] = Field(default_factory=list)


class _ContextualizedSignalLLM(BaseModel):
    model_config = ConfigDict(extra="allow")

    signal_index: int
    novelty: Novelty | None = None
    salience: Salience
    reasoning: str


class ContextualizationLLMResponse(BaseModel):
    """Shape the Contextualization LLM must return."""

    model_config = ConfigDict(extra="allow")

    contextualized_signals: list[_ContextualizedSignalLLM]
    narrative: str
