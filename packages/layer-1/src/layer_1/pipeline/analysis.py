"""Build and write the machine-readable analysis.json summary of an eval run."""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from layer_1.pipeline.models import (
    AUDIT_PROMPT_PATH,
    EXTRACTOR_PROMPT_PATH,
    TARGETS,
    AuditMetrics,
    Metrics,
)
from layer_1.pipeline.report import pct, verdict


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_analysis(
    m: Metrics,
    audit: AuditMetrics | None,
    *,
    results_scored: int,
    audit_limit: int | None,
    judge_model: str,
) -> dict[str, Any]:
    """Assemble the analysis dict written to outputs/analysis/eval-report.json."""
    audit_block = _audit_block(audit) if audit is not None else None
    return {
        "schema_version": "analysis-v3",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "scope": {
            "audit_limit": audit_limit,
            "judge_model": judge_model,
            "results_scored": results_scored,
        },
        "prompt_hashes": {
            "extractor_sha256": _sha256_of(EXTRACTOR_PROMPT_PATH),
            "judge_sha256": _sha256_of(AUDIT_PROMPT_PATH),
        },
        "metrics": _metrics_block(m, audit),
        "failures": _failures_block(m),
        "audit": audit_block,
    }


def write_analysis(path: Path, analysis: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(analysis, indent=2, ensure_ascii=False) + "\n")


def _metric_entry(
    passed: int, total: int, target_floor: tuple[float, float],
) -> dict[str, Any]:
    rate = pct(passed, total)
    target, floor = target_floor
    return {
        "rate": round(rate, 4),
        "target": target,
        "floor": floor,
        "verdict": verdict(rate, target, floor),
        "passed": passed,
        "total": total,
    }


def _metrics_block(m: Metrics, audit: AuditMetrics | None) -> dict[str, Any]:
    block: dict[str, Any] = {
        "evidence_grounding": _metric_entry(
            m.eg_passed, m.eg_total, TARGETS["evidence_grounding"],
        ),
        "observation_type": _metric_entry(
            m.ot_passed, m.ot_total, TARGETS["observation_type"],
        ),
    }
    ship = _observation_shippability(m, audit)
    if ship is not None:
        block["observation_shippability"] = ship
    return block


def _observation_shippability(
    m: Metrics, audit: AuditMetrics | None,
) -> dict[str, Any] | None:
    """Observation-level pass/fail — a shippability read, not a rule-compliance
    read. An observation ships if:
      (a) every signal on it passed programmatic evidence grounding, AND
      (b) no signal on it failed the judge's over-extraction check.
    (b) is skipped when audit did not run; (a) alone is still reported.
    The metric answers "was this extraction good enough to hand to the next
    layer?" rather than "did it follow every sub-rule?".
    """
    if m.ot_total == 0:
        return None

    eg_failed_obs = {k for (k, _ev) in m.eg_failures}
    audited_obs: set[str] = set()
    over_extraction_failed_obs: set[str] = set()

    if audit is not None:
        audited_obs = {s.cache_key for s in audit.audited_signals}
        over_extraction_failed_obs = {
            e.cache_key for e in audit.over_extraction_failures
        }

    # Programmatic-only shippability — always computable.
    prog_passed = m.ot_total - len(eg_failed_obs)
    entry: dict[str, Any] = {
        "programmatic": _metric_entry(
            prog_passed, m.ot_total, (1.00, 0.95),
        ),
    }

    # Full shippability — needs audit to have run.
    if audit is not None and audited_obs:
        total = len(audited_obs)
        failed = len(audited_obs & (eg_failed_obs | over_extraction_failed_obs))
        passed = total - failed
        entry["full"] = _metric_entry(passed, total, (0.95, 0.85))

    return entry


def _failures_block(m: Metrics) -> dict[str, Any]:
    return {
        "evidence_grounding": [
            {"cache_key": key, "evidence": ev} for key, ev in m.eg_failures
        ],
    }


def _audit_block(am: AuditMetrics) -> dict[str, Any]:
    def _rate(n: int, d: int) -> float:
        return round(pct(n, d), 4)

    def _failure_list(entries: list[Any]) -> list[dict[str, Any]]:
        return [
            {
                "cache_key": e.cache_key,
                "signal_index": e.signal_index,
                "evidence_snippet": e.evidence_snippet,
                "note": e.note,
            }
            for e in entries
        ]

    return {
        "observations_audited": am.obs_total,
        "signals_audited": am.signals_total,
        "checks": {
            "evidence_grounded": {
                "rate": _rate(am.grounded_passed, am.signals_total),
                "passed": am.grounded_passed,
                "total": am.signals_total,
            },
            "reasoning_justifies_classification": {
                "rate": _rate(am.reasoning_passed, am.signals_total),
                "passed": am.reasoning_passed,
                "total": am.signals_total,
            },
            "no_over_extraction": {
                "rate": _rate(am.over_extraction_passed, am.signals_total),
                "passed": am.over_extraction_passed,
                "total": am.signals_total,
            },
        },
        "failures": {
            "evidence_grounded": _failure_list(am.grounded_failures),
            "reasoning_justifies_classification": _failure_list(am.reasoning_failures),
            "no_over_extraction": _failure_list(am.over_extraction_failures),
        },
        # Complete per-signal index with pass/fail per check. Downstream
        # calibration uses this to sample non-flagged signals for recall
        # grading — catches the "lenient judge scores perfect" failure mode.
        "audited_signals": [
            {
                "cache_key": s.cache_key,
                "signal_index": s.signal_index,
                "evidence_snippet": s.evidence_snippet,
                "all_passed": s.all_passed,
                "checks": {
                    "evidence_grounded": s.grounded_passed,
                    "reasoning_justifies_classification": s.reasoning_passed,
                    "no_over_extraction": s.over_extraction_passed,
                },
            }
            for s in am.audited_signals
        ],
    }
