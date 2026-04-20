"""Read Layer 1 extractions, the extended observation JSON, and the roster.

The loader's job is to produce three aligned in-memory structures keyed by
observation_id and student_id. Everything downstream (history, attribution,
contextualization) operates on these.
"""

import json
import sys
from pathlib import Path

from core.io import read_jsonl
from layer_1_5.pipeline.models import (
    LayerOneRecord,
    ObservationInput,
    RosterStudent,
)


def load_extractions(path: Path) -> dict[str, LayerOneRecord]:
    """Return a map of observation_id → LayerOneRecord. Dedupes last-wins."""
    if not path.exists():
        print(f"ERROR: {path} not found — run layer-1-extract first", file=sys.stderr)
        sys.exit(1)

    by_oid: dict[str, LayerOneRecord] = {}
    for rec in read_jsonl(path):
        source = rec.get("source")
        oid = source.get("observation_id") if isinstance(source, dict) else None
        if not isinstance(oid, str) or not oid:
            continue
        signals_raw = rec.get("signals", [])
        if isinstance(signals_raw, list):
            signals = [s for s in signals_raw if isinstance(s, dict)]
        else:
            signals = []
        named = rec.get("named_students", [])
        named = [str(n) for n in named] if isinstance(named, list) else []
        by_oid[oid] = LayerOneRecord(
            observation_id=oid,
            signals=signals,
            named_students=named,
            raw=rec,
        )
    return by_oid


def load_observations(path: Path) -> dict[str, ObservationInput]:
    """Return a map of observation_id → ObservationInput (published rows with student_ids)."""
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        print(f"ERROR: {path} is not a JSON array", file=sys.stderr)
        sys.exit(1)

    by_oid: dict[str, ObservationInput] = {}
    skipped = 0
    for rec in data:
        if not isinstance(rec, dict):
            skipped += 1
            continue
        oid = str(rec.get("observation_id", "")).strip()
        if not oid:
            skipped += 1
            continue
        student_ids_raw = rec.get("student_ids") or []
        student_ids = [str(sid) for sid in student_ids_raw if isinstance(sid, str)]
        try:
            sc = int(rec.get("student_count", len(student_ids)))
        except (ValueError, TypeError):
            sc = len(student_ids)
        by_oid[oid] = ObservationInput(
            observation_id=oid,
            client_id=str(rec.get("client_id", "")),
            created_at=str(rec.get("created_at", "")),
            comment=str(rec.get("comment", "")),
            student_ids=student_ids,
            student_count=sc,
        )
    if skipped:
        print(f"loader: skipped {skipped} malformed observation rows", file=sys.stderr)
    return by_oid


def load_roster(path: Path) -> dict[str, RosterStudent]:
    """Return a map of student_id → RosterStudent for ACTIVE students.

    Accepts the flat-array export shape produced by the DB query.
    """
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        print(f"ERROR: {path} is not a JSON array", file=sys.stderr)
        sys.exit(1)

    roster: dict[str, RosterStudent] = {}
    for rec in data:
        if not isinstance(rec, dict):
            continue
        sid = str(rec.get("student_id", "")).strip()
        if not sid:
            continue
        first = str(rec.get("first_name", "")).strip()
        last = str(rec.get("last_name", "")).strip()
        full = f"{first} {last}".strip()
        legacy = rec.get("legacy_ids") or []
        roster[sid] = RosterStudent(
            student_id=sid,
            first_name=first,
            last_name=last,
            full_name=full,
            crew_id=str(rec.get("crew_id", "")),
            crew_name=str(rec.get("crew_name", "")),
            status=str(rec.get("status", "")),
            external_id=rec.get("external_id"),
            legacy_ids=[str(lid) for lid in legacy if isinstance(lid, str)],
        )
    return roster
