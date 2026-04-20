"""Dataclasses, constants, and paths shared across the Layer 1.5 pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from core.schema.layer1_5 import SecondaryMatchKind

ResolvedMatchKind = SecondaryMatchKind | Literal["ambiguous", "unresolved"]

# packages/layer-1.5/src/layer_1_5/pipeline/models.py → packages/layer-1.5/
PACKAGE_ROOT = Path(__file__).resolve().parents[3]

INPUTS_DIR = PACKAGE_ROOT / "inputs"
OUTPUTS_DIR = PACKAGE_ROOT / "outputs"
PROMPTS_DIR = PACKAGE_ROOT / "prompts"

CONTEXTUALIZATIONS_PATH = OUTPUTS_DIR / "contextualizations.jsonl"

ATTRIBUTION_PROMPT_PATH = PROMPTS_DIR / "attribution.md"
CONTEXTUALIZATION_PROMPT_PATH = PROMPTS_DIR / "contextualization.md"

SCHEMA_VERSION = "v1"
DEFAULT_MODEL = "anthropic/claude-sonnet-4-6"

# Guardrail boundaries from the plan.
GROUP_LLM_MIN = 2
GROUP_LLM_MAX = 5
GROUP_UNIFORM_THRESHOLD = 6


@dataclass
class RosterStudent:
    student_id: str
    first_name: str
    last_name: str
    full_name: str
    crew_id: str
    crew_name: str
    status: str
    external_id: str | None = None
    legacy_ids: list[str] = field(default_factory=list)


@dataclass
class ObservationInput:
    """One row of the extended observation JSON with student_ids."""

    observation_id: str
    client_id: str
    created_at: str
    comment: str
    student_ids: list[str]
    student_count: int


@dataclass
class LayerOneRecord:
    """Projection of a Layer 1 extraction the way Layer 1.5 consumes it."""

    observation_id: str
    signals: list[dict[str, Any]]
    named_students: list[str]
    raw: dict[str, Any]


@dataclass
class ResolvedName:
    """Outcome of resolving a surface-form name against the roster."""

    name_in_text: str
    student_id: str | None
    match_kind: ResolvedMatchKind
    candidates: list[str] = field(default_factory=list)  # student_ids when ambiguous
