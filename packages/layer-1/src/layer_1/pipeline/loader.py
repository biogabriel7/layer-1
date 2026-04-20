"""Loads extraction results from disk and joins them to source observations.

Results live in `outputs/extractions.jsonl` (one JSON object per line, appended
progressively by extract.py). Duplicate observation_ids are deduped last-wins
so `--force` re-runs don't require rewriting the file.

Results are cross-checked against the per-school observations JSON
(`OBSERVATIONS_PATH`) — rows whose source observation is no longer present
are treated as orphans and skipped.
"""

import json
import sys

from core.text import cache_key
from layer_1.pipeline.models import EXTRACTIONS_PATH, OBSERVATIONS_PATH, ResultFile, Signal


def load_results() -> list[ResultFile]:
    if not EXTRACTIONS_PATH.exists():
        print(f"ERROR: {EXTRACTIONS_PATH} not found — run extract.py first", file=sys.stderr)
        sys.exit(1)

    obs_index: dict[str, tuple[str, int]] = {}

    try:
        data = json.loads(OBSERVATIONS_PATH.read_text())
    except FileNotFoundError:
        data = None
    if isinstance(data, list):
        for rec in data:
            if not isinstance(rec, dict):
                continue
            oid = str(rec.get("observation_id", "")).strip()
            comment = str(rec.get("comment", ""))
            if not oid or not comment:
                continue
            try:
                sc = int(rec.get("student_count", 1))
            except (ValueError, TypeError):
                sc = 1
            obs_index[cache_key(oid)] = (comment, sc)

    # Read JSONL line-by-line. Dedupe last-wins by cache_key so `--force`
    # re-runs (which append shadow entries) produce the latest extraction.
    latest_by_key: dict[str, dict[str, object]] = {}
    with EXTRACTIONS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                # Tolerate a truncated trailing line from a prior crash.
                continue
            if not isinstance(record, dict):
                continue
            source = record.get("source")
            record_oid = source.get("observation_id") if isinstance(source, dict) else None
            if not isinstance(record_oid, str) or not record_oid:
                continue
            latest_by_key[cache_key(record_oid)] = record

    results: list[ResultFile] = []
    for key in sorted(latest_by_key):
        if key not in obs_index:
            # Orphaned result (source observation no longer present) — skip.
            continue
        obs, sc = obs_index[key]
        record = latest_by_key[key]
        signals_raw = record.get("signals", [])
        if not isinstance(signals_raw, list):
            signals_raw = []
        signals = [
            Signal(
                evidence=str(s.get("evidence", "")),
                type=str(s.get("type", "")).strip(),
            )
            for s in signals_raw
            if isinstance(s, dict)
        ]
        results.append(
            ResultFile(
                cache_key=key,
                observation=obs,
                student_count=sc,
                observation_type=str(record.get("observation_type", "")),
                signals=signals,
                raw=record,
            )
        )
    return results
