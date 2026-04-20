"""Pydantic models for the Layer 1 audit LLM's response.

The extractor-side schema (`Signal`, `ExtractionOutput`, `Participant`) lives
in `core.schema.layer1` because it is the public contract between Layer 1 and
downstream consumers (Layer 1.5 reads Layer 1's output).

`extra="allow"` on the top-level models is intentional: if the prompt is
updated to emit an additional field before the schema catches up, we don't
want validation to hard-fail — the extra field just passes through.
"""

from pydantic import BaseModel, ConfigDict, Field


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
