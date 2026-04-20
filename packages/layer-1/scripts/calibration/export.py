#!/usr/bin/env python3
"""Export calibration rows from outputs/analysis/eval-report.json into a CSV
ready for hand-labeling by a human reviewer.

Two row types are exported together so a single labeling pass validates both
sides of the judge:

  1. Precision rows — one per judge-flagged signal (task ∈
     evidence_grounded / reasoning_justifies_classification / no_over_extraction).
     Verdict answers: "when the judge flags, is it right?"

  2. Recall rows — a random sample of signals the judge DID NOT flag
     (task = recall_check). Verdict answers: "what did the judge wave through
     that a human would flag?" Without these rows, a lenient judge scores
     perfect on precision.

Columns:
  cache_key                — observation id hash for traceability
  task                     — audit check name, or "recall_check"
  signal_index             — signal the flag refers to
  judge_verdict            — "flagged" (precision rows) or "not_flagged" (recall rows)
  judge_note               — judge's justification (blank for recall rows)
  evidence_snippet         — the evidence quote
  observation_excerpt      — first 200 chars of the observation text
  human_verdict            — BLANK, to be filled in by the reviewer
  human_note               — BLANK, to be filled in by the reviewer

Human verdict taxonomy:
  Precision rows (judge said flag): "correct_flag" or "false_flag".
  Recall rows (judge said pass):    "pass" or "should_flag".

A sidecar <csv>.meta.json is written alongside the CSV, stamping the prompt
hashes at export time. The agreement script cross-checks these against the
current prompts and warns if drift has occurred — stale calibration numbers
get marked, not silently reported.

Workflow:
  1. Run eval.py (produces outputs/analysis/eval-report.json)
  2. uv run scripts/calibration/export.py [--random-sample N]
  3. Open outputs/analysis/calibration-{timestamp}.csv in a spreadsheet
  4. Fill in human_verdict and human_note for every row
  5. uv run scripts/calibration/agreement.py <filled-in.csv>
"""

import argparse
import csv
import functools
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from layer_1.pipeline.models import (  # noqa: E402
    ANALYSIS_DEFAULT_PATH,
    ANALYSIS_DIR,
    EXTRACTIONS_PATH,
)
from layer_1.pipeline.text import cache_key as _cache_key  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--analysis",
        type=Path,
        default=ANALYSIS_DEFAULT_PATH,
        help=f"Analysis JSON to read (default: {ANALYSIS_DEFAULT_PATH})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output CSV path (default: analysis/calibration-{timestamp}.csv)",
    )
    parser.add_argument(
        "--random-sample",
        type=int,
        default=20,
        metavar="N",
        help=(
            "Sample N non-flagged signals for recall calibration (default: 20). "
            "Set to 0 to disable recall sampling and export precision rows only."
        ),
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for recall sampling — deterministic by default so two "
             "exports of the same analysis produce the same recall rows",
    )
    args = parser.parse_args()

    try:
        analysis = json.loads(args.analysis.read_text())
    except FileNotFoundError:
        print(f"ERROR: {args.analysis} not found — run eval.py first", file=sys.stderr)
        return 1

    precision_rows = list(_precision_rows(analysis))
    recall_rows = list(_recall_rows(analysis, args.random_sample, args.seed))
    rows = precision_rows + recall_rows

    if not rows:
        print("No rows to export (no flagged signals, no recall sample).", file=sys.stderr)
        return 0

    out_path = args.out
    if out_path is None:
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        out_path = ANALYSIS_DIR / f"calibration-{ts}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "cache_key", "task", "signal_index",
        "judge_verdict", "judge_note",
        "evidence_snippet", "observation_excerpt",
        "human_verdict", "human_note",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    meta = _sidecar_meta(analysis, args.analysis, len(precision_rows), len(recall_rows))
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")

    print(f"Wrote {out_path}")
    print(f"  precision rows (judge-flagged):     {len(precision_rows)}")
    print(f"  recall rows (random non-flagged):   {len(recall_rows)}")
    print(f"Wrote {meta_path}  (prompt hashes for drift check)")
    return 0


AUDIT_CHECKS = (
    "evidence_grounded",
    "reasoning_justifies_classification",
    "no_over_extraction",
)


def _precision_rows(analysis: dict[str, Any]) -> Iterator[dict[str, str]]:
    """One row per failing check per signal — these are the judge-flagged
    signals. Human labels verify the judge's precision."""
    audit = analysis.get("audit")
    if not isinstance(audit, dict):
        return
    failures = audit.get("failures", {})
    if not isinstance(failures, dict):
        return
    for check_name in AUDIT_CHECKS:
        for e in failures.get(check_name, []):
            cache_key = e.get("cache_key", "")
            observation = _load_observation(cache_key)
            yield {
                "cache_key": cache_key,
                "task": check_name,
                "signal_index": str(e.get("signal_index", "")),
                "judge_verdict": "flagged",
                "judge_note": e.get("note", ""),
                "evidence_snippet": e.get("evidence_snippet", ""),
                "observation_excerpt": observation[:200],
                "human_verdict": "",
                "human_note": "",
            }


def _recall_rows(
    analysis: dict[str, Any], n: int, seed: int,
) -> Iterator[dict[str, str]]:
    """Sample N signals the judge let pass on every check. Human labels here
    catch false negatives the judge would never surface on its own."""
    if n <= 0:
        return
    audit = analysis.get("audit")
    if not isinstance(audit, dict):
        return
    audited = audit.get("audited_signals")
    if not isinstance(audited, list):
        print(
            "WARNING: analysis has no audited_signals index (schema <v3). "
            "Recall sampling unavailable — re-run eval.py to upgrade.",
            file=sys.stderr,
        )
        return
    not_flagged = [s for s in audited if s.get("all_passed") is True]
    if not not_flagged:
        return
    k = min(n, len(not_flagged))
    rng = random.Random(seed)
    sample = rng.sample(not_flagged, k)
    for s in sample:
        cache_key = s.get("cache_key", "")
        observation = _load_observation(cache_key)
        yield {
            "cache_key": cache_key,
            "task": "recall_check",
            "signal_index": str(s.get("signal_index", "")),
            "judge_verdict": "not_flagged",
            "judge_note": "",
            "evidence_snippet": s.get("evidence_snippet", ""),
            "observation_excerpt": observation[:200],
            "human_verdict": "",
            "human_note": "",
        }


def _sidecar_meta(
    analysis: dict[str, Any],
    analysis_path: Path,
    precision_count: int,
    recall_count: int,
) -> dict[str, Any]:
    """Snapshot prompt hashes at export time so the agreement script can
    detect when prompts have since changed."""
    return {
        "schema_version": "calibration-meta-v1",
        "exported_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source_analysis": str(analysis_path),
        "source_analysis_timestamp": analysis.get("timestamp"),
        "prompt_hashes": analysis.get("prompt_hashes") or {},
        "judge_model": (analysis.get("scope") or {}).get("judge_model"),
        "rows": {
            "precision": precision_count,
            "recall": recall_count,
        },
    }


@functools.lru_cache(maxsize=1)
def _observations_by_cache_key() -> dict[str, str]:
    """Build a dict of cache_key → observation text by scanning the JSONL once.

    Duplicate cache_keys resolve last-wins, matching loader.py semantics.
    """
    index: dict[str, str] = {}
    if not EXTRACTIONS_PATH.exists():
        return index
    with EXTRACTIONS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(record, dict):
                continue
            source = record.get("source")
            oid = source.get("observation_id") if isinstance(source, dict) else None
            if not isinstance(oid, str) or not oid:
                continue
            index[_cache_key(oid)] = str(record.get("observation", ""))
    return index


def _load_observation(cache_key: str) -> str:
    """Best-effort lookup of the observation text for a cache key."""
    if not cache_key:
        return ""
    return _observations_by_cache_key().get(cache_key, "")


if __name__ == "__main__":
    sys.exit(main())
