#!/usr/bin/env python3
"""Reads a hand-labeled calibration CSV (produced by scripts/calibration/export.py
and filled in by a human reviewer) and computes judge-vs-human agreement,
splitting precision from recall.

Precision (task ∈ evidence_grounded, reasoning_justifies_classification,
no_over_extraction): judge said flag — is it right?

    human_verdict ∈ {correct_flag, flagged}        → AGREE (true positive)
    human_verdict ∈ {false_flag,   not_flagged}    → DISAGREE (false positive)

Recall (task = recall_check): judge said pass — did it miss something?

    human_verdict ∈ {pass, not_flagged, correct_flag} → AGREE (true negative)
    human_verdict ∈ {should_flag, flagged, false_flag} → FALSE NEGATIVE

A lenient judge scores perfectly on precision alone. Recall is the
overfitting defense.

Rows left blank are counted as 'unreviewed' and excluded from the rate.

The CSV's sidecar <csv>.meta.json stamps the prompt hashes at export time.
This script compares them to the current prompts on disk and prints a drift
warning when they differ — so stale calibration numbers aren't silently
reported against prompts that have since changed.
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from layer_1.pipeline.models import (  # noqa: E402
    ANALYSIS_DIR,
    AUDIT_PROMPT_PATH,
    EXTRACTOR_PROMPT_PATH,
)

# Precision-row verdict taxonomy (judge said flag).
PRECISION_AGREE = {"correct_flag", "flagged"}
PRECISION_DISAGREE = {"false_flag", "not_flagged"}

# Recall-row verdict taxonomy (judge said pass). Judge-direction inverts:
# the human "agreeing with the judge's pass" is the no-false-negative case.
RECALL_AGREE = {"pass", "not_flagged", "correct_flag"}
RECALL_DISAGREE = {"should_flag", "flagged", "false_flag"}

RECALL_TASK = "recall_check"
PRECISION_TASKS = {
    "evidence_grounded",
    "reasoning_justifies_classification",
    "no_over_extraction",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="Hand-labeled calibration CSV")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path (default: outputs/analysis/calibration-{timestamp}.json)",
    )
    args = parser.parse_args()

    per_task: dict[str, dict[str, int]] = defaultdict(
        lambda: {"agree": 0, "disagree": 0, "unreviewed": 0}
    )
    systematic: Counter[tuple[str, str]] = Counter()

    try:
        csv_file = open(args.csv_path, newline="", encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: {args.csv_path} not found", file=sys.stderr)
        return 1
    with csv_file as f:
        for row in csv.DictReader(f):
            task = row.get("task", "").strip()
            human = row.get("human_verdict", "").strip()

            if not task:
                continue

            if task == RECALL_TASK:
                agree_set, disagree_set = RECALL_AGREE, RECALL_DISAGREE
            elif task in PRECISION_TASKS:
                agree_set, disagree_set = PRECISION_AGREE, PRECISION_DISAGREE
            else:
                # Unknown task — count as unreviewed, don't crash.
                per_task[task]["unreviewed"] += 1
                continue

            if human in agree_set:
                per_task[task]["agree"] += 1
            elif human in disagree_set:
                per_task[task]["disagree"] += 1
                systematic[(task, human)] += 1
            else:
                per_task[task]["unreviewed"] += 1

    for task_stats in per_task.values():
        reviewed = task_stats["agree"] + task_stats["disagree"]
        task_stats["rate"] = round(
            task_stats["agree"] / reviewed, 4
        ) if reviewed else 0.0  # type: ignore[assignment]

    drift = _check_drift(args.csv_path)

    summary: dict[str, Any] = {
        "schema_version": "calibration-v2",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source_csv": str(args.csv_path),
        "drift": drift,
        "per_task": dict(per_task),
        "systematic_disagreements": [
            {"task": t, "human": h, "count": n}
            for (t, h), n in systematic.most_common(10)
        ],
        "summary_rates": _summary_rates(per_task),
    }

    out_path = args.out
    if out_path is None:
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        out_path = ANALYSIS_DIR / f"calibration-{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    print(f"Wrote {out_path}")
    if drift.get("status") == "drifted":
        print(
            "\n⚠️  PROMPT DRIFT detected — these calibration rows were labeled "
            "against different prompts than the ones currently on disk:"
        )
        for which, info in drift.get("fields", {}).items():
            if info.get("drifted"):
                print(
                    f"   {which}: exported={info['exported'][:12]}..  "
                    f"current={info['current'][:12]}.."
                )
        print("   Consider re-running the calibration on fresh eval output.\n")
    elif drift.get("status") == "no_meta":
        print(
            "\n(no sidecar .meta.json found alongside the CSV — drift check skipped)\n"
        )

    for task, stats in per_task.items():
        reviewed = stats["agree"] + stats["disagree"]
        rate_pct = (stats["agree"] / reviewed * 100) if reviewed else 0.0
        print(
            f"  {task:<40} agree={stats['agree']} disagree={stats['disagree']} "
            f"unreviewed={stats['unreviewed']} rate={rate_pct:.1f}%"
        )

    summary_rates = summary["summary_rates"]
    prec = summary_rates.get("precision")
    rec = summary_rates.get("recall")
    print()
    if prec and prec.get("reviewed"):
        print(
            f"  PRECISION (judge flags right?)   "
            f"{prec['rate'] * 100:.1f}%  ({prec['agree']}/{prec['reviewed']} reviewed)"
        )
    if rec and rec.get("reviewed"):
        fn = rec["disagree"]
        total = rec["reviewed"]
        print(
            f"  RECALL    (judge catches bad?)   "
            f"{rec['rate'] * 100:.1f}%  "
            f"({fn} false negatives out of {total} sampled passes)"
        )
    elif rec and not rec.get("reviewed"):
        print(
            "  RECALL    — no recall_check rows were labeled. Re-export with "
            "--random-sample N and label them to measure false negatives."
        )

    return 0


def _summary_rates(per_task: dict[str, dict[str, int]]) -> dict[str, Any]:
    """Aggregate precision (across all flag-checks) and recall (recall_check)."""
    prec_agree = sum(
        per_task[t]["agree"] for t in PRECISION_TASKS if t in per_task
    )
    prec_disagree = sum(
        per_task[t]["disagree"] for t in PRECISION_TASKS if t in per_task
    )
    prec_reviewed = prec_agree + prec_disagree

    rec_stats = per_task.get(RECALL_TASK, {"agree": 0, "disagree": 0})
    rec_agree = rec_stats["agree"]
    rec_disagree = rec_stats["disagree"]
    rec_reviewed = rec_agree + rec_disagree

    return {
        "precision": {
            "agree": prec_agree,
            "disagree": prec_disagree,
            "reviewed": prec_reviewed,
            "rate": (
                round(prec_agree / prec_reviewed, 4)
                if prec_reviewed else 0.0
            ),
        },
        "recall": {
            "agree": rec_agree,
            "disagree": rec_disagree,
            "reviewed": rec_reviewed,
            # Recall interpretation: how often judge's "pass" agrees with human.
            # Equivalent to (1 - false_negative_rate) on the sampled rows.
            "rate": (
                round(rec_agree / rec_reviewed, 4)
                if rec_reviewed else 0.0
            ),
            "false_negative_count": rec_disagree,
        },
    }


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_drift(csv_path: Path) -> dict[str, Any]:
    """Compare the sidecar .meta.json prompt hashes to the current prompts on
    disk. Returns a structured result the caller can print and the summary
    JSON can persist."""
    meta_path = csv_path.with_suffix(csv_path.suffix + ".meta.json")
    if not meta_path.exists():
        return {"status": "no_meta"}
    try:
        meta = json.loads(meta_path.read_text())
    except json.JSONDecodeError:
        return {"status": "unreadable_meta"}

    exported = meta.get("prompt_hashes") or {}
    current = {
        "extractor_sha256": _sha256_of(EXTRACTOR_PROMPT_PATH),
        "judge_sha256": _sha256_of(AUDIT_PROMPT_PATH),
    }

    fields: dict[str, dict[str, Any]] = {}
    any_drift = False
    for key in ("extractor_sha256", "judge_sha256"):
        exp = exported.get(key, "")
        cur = current[key]
        drifted = bool(exp) and exp != cur
        any_drift = any_drift or drifted
        fields[key] = {"exported": exp, "current": cur, "drifted": drifted}

    return {
        "status": "drifted" if any_drift else "stable",
        "fields": fields,
        "source_meta": str(meta_path),
    }


if __name__ == "__main__":
    sys.exit(main())
