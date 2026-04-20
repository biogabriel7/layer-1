"""Scores extraction results and runs the reference-free audit.

Reads outputs/extractions.jsonl (produced by extract.py) and reports two
programmatic dimensions on every result:

  1. Evidence Grounding   — every signal's evidence is a substring of the
                            source observation (case-insensitive, whitespace-
                            normalized).
  2. Observation Type     — observation_type matches the student_count rule
                            (1 → individual, >1 → group).

Then runs the reference-free audit: a cross-family LLM judge that evaluates
each signal against the observation text alone. No human-annotated answer
key required. Capped by --limit N for cost control.
"""

import argparse
import sys
from pathlib import Path

from layer_1.pipeline.analysis import build_analysis, write_analysis
from layer_1.pipeline.judge import run_audit
from layer_1.pipeline.loader import load_results
from layer_1.pipeline.models import (
    ANALYSIS_DEFAULT_PATH,
    JUDGE_MODEL,
    AuditMetrics,
    Metrics,
)
from layer_1.pipeline.report import report, report_audit
from layer_1.pipeline.scoring import score_programmatic


def main() -> None:
    parser = argparse.ArgumentParser(description="Score Layer 1 extraction results")
    parser.add_argument(
        "--show-failures",
        action="store_true",
        help="Print evidence-grounding and audit failures for debugging",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bust the audit cache and re-call the judge",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Cap the audit to the first N results (cost-control knob). "
             "Default: no cap — audit every result with signals.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Parallel judge workers",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the judge prompt without calling the API",
    )
    parser.add_argument(
        "--analysis-out",
        type=Path,
        default=ANALYSIS_DEFAULT_PATH,
        metavar="PATH",
        help=f"Where to write the analysis JSON (default: {ANALYSIS_DEFAULT_PATH})",
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="Skip writing the analysis JSON",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Skip the reference-free audit — programmatic metrics only",
    )
    parser.add_argument(
        "--judge-model",
        type=str,
        default=JUDGE_MODEL,
        metavar="MODEL",
        help=(
            f"Judge model via OpenRouter (default: {JUDGE_MODEL}). "
            "Use a non-Claude model to mitigate same-family self-enhancement bias "
            "when evaluating the Claude-Opus extractor."
        ),
    )
    args = parser.parse_args()

    results = load_results()
    if not results:
        print("No results found. Run `uv run extract.py` first.", file=sys.stderr)
        sys.exit(1)

    m = Metrics()
    for result in results:
        score_programmatic(result, m)

    print(f"Scored {len(results)} results")
    report(m, show_failures=args.show_failures)

    audit: AuditMetrics | None = None
    if not args.no_audit:
        audit = run_audit(results, args)
        if audit is not None:
            report_audit(audit, show_failures=args.show_failures, m=m)

    if not args.no_analysis and not args.dry_run:
        analysis = build_analysis(
            m,
            audit,
            results_scored=len(results),
            audit_limit=args.limit,
            judge_model=args.judge_model,
        )
        write_analysis(args.analysis_out, analysis)
        print(f"\nWrote {args.analysis_out}")


if __name__ == "__main__":
    main()
