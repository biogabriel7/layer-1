"""Dataclasses, constants, and paths shared across the Layer 1 pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

INPUTS_DIR = Path("inputs")
OUTPUTS_DIR = Path("outputs")

OBSERVATIONS_PATH = INPUTS_DIR / "observations-stfrancis-2026-04-17.json"

EXTRACTOR_PROMPT_PATH = Path("prompts/extractor.md")
AUDIT_PROMPT_PATH = Path("prompts/judge_reference_free.md")

EXTRACTIONS_PATH = OUTPUTS_DIR / "extractions.jsonl"
QUALITY_CHECKS_PATH = OUTPUTS_DIR / "quality-checks.jsonl"
ANALYSIS_DIR = OUTPUTS_DIR / "analysis"
ANALYSIS_DEFAULT_PATH = ANALYSIS_DIR / "eval-report.json"
AUDIT_CACHE_DIR = OUTPUTS_DIR / "judge-cache" / "reference-free"

JUDGE_MODEL = "openai/gpt-5.4"

VALID_TYPES = {
    "behavioral_evidence",
    "emotional_indicator",
    "context_marker",
    "concern_flag",
}

# Targets (pass) and minimum-acceptable floors for the programmatic dimensions.
TARGETS = {
    "evidence_grounding": (1.00, 0.95),
    "observation_type": (1.00, 0.98),
}

# Target for every reference-free audit check.
AUDIT_TARGET = (0.95, 0.85)


@dataclass
class Signal:
    evidence: str
    type: str


@dataclass
class ResultFile:
    cache_key: str
    observation: str
    student_count: int
    observation_type: str
    signals: list[Signal]
    # Full extraction payload — kept so the audit can see v2 descriptive facets
    # and named_students without re-reading disk per observation.
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class Metrics:
    """Programmatic dimensions — evidence grounding and observation type."""

    # Evidence grounding (signal-level)
    eg_total: int = 0
    eg_passed: int = 0
    eg_failures: list[tuple[str, str]] = field(default_factory=list)  # (cache_key, evidence)

    # Observation type (observation-level)
    ot_total: int = 0
    ot_passed: int = 0


@dataclass
class AuditCheckResult:
    cache_key: str
    signal_index: int
    evidence_snippet: str
    note: str


@dataclass
class AuditedSignal:
    """Every signal the judge saw, with pass/fail on each check. Lets the
    calibration harness sample non-flagged signals for false-negative
    (recall) grading — not just the flagged ones."""
    cache_key: str
    signal_index: int
    evidence_snippet: str
    grounded_passed: bool
    reasoning_passed: bool
    over_extraction_passed: bool

    @property
    def all_passed(self) -> bool:
        return (
            self.grounded_passed
            and self.reasoning_passed
            and self.over_extraction_passed
        )


@dataclass
class AuditMetrics:
    obs_total: int = 0
    signals_total: int = 0

    grounded_passed: int = 0
    reasoning_passed: int = 0
    over_extraction_passed: int = 0

    grounded_failures: list[AuditCheckResult] = field(default_factory=list)
    reasoning_failures: list[AuditCheckResult] = field(default_factory=list)
    over_extraction_failures: list[AuditCheckResult] = field(default_factory=list)

    # Every audited signal, pass or fail. Needed for recall-side calibration.
    audited_signals: list[AuditedSignal] = field(default_factory=list)
