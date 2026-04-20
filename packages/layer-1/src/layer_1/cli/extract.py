"""Reads a per-school observation JSON, sends each observation to an LLM via
OpenRouter, and appends structured insight signals to outputs/extractions.jsonl.

Results are appended progressively (one JSON object per line) so large runs
never buffer the full dataset in memory and a crash mid-run never loses
already-completed rows. On reload, duplicate observation_ids are deduped
last-wins, which keeps `--force` re-runs safe without rewriting the file."""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI

from core.io import append_jsonl
from core.llm import call_json, make_client
from core.schema.layer1 import ExtractionOutput
from core.text import cache_key
from layer_1.pipeline.models import (
    EXTRACTIONS_PATH,
    EXTRACTOR_PROMPT_PATH,
    OBSERVATIONS_PATH,
    QUALITY_CHECKS_PATH,
)

MODEL = "anthropic/claude-opus-4-6"
SCHEMA_VERSION = "v2"


def load_system_prompt() -> str:
    return EXTRACTOR_PROMPT_PATH.read_text()


def build_user_message(observation: str, student_count: int) -> str:
    return json.dumps({"observation": observation, "student_count": student_count})


def postprocess(result: dict[str, object], student_count: int) -> dict[str, object]:
    """Enforce deterministic fields regardless of what the model returned."""
    signals = result.get("signals", [])
    if not isinstance(signals, list):
        raise TypeError(f"signals must be a list, got {type(signals).__name__}")
    signal_count = len(signals)

    result["signal_count"] = signal_count

    if student_count == 1:
        result["observation_type"] = "individual"
    else:
        result["observation_type"] = "group"

    if signal_count <= 1:
        result["insight_density"] = "low"
    elif signal_count <= 3:
        result["insight_density"] = "medium"
    else:
        result["insight_density"] = "high"

    # Meaningful content requires at least one high- or medium-confidence signal.
    # A lone `low` signal (e.g., "Did well today") is the canonical placeholder
    # and shouldn't count as meaningful.
    result["meaningful_content"] = any(
        isinstance(s, dict) and s.get("confidence") in ("high", "medium")
        for s in signals
    )

    named = result.get("named_students", [])
    if not isinstance(named, list):
        named = []
        result["named_students"] = named
    result["named_students_count"] = len(named)

    return result


def call_api(
    client: OpenAI,
    system_prompt: str,
    observation: str,
    student_count: int,
) -> dict[str, Any]:
    return call_json(
        client, system_prompt, build_user_message(observation, student_count), model=MODEL,
    )


def process_row(
    client: OpenAI | None,
    system_prompt: str,
    observation_id: str,
    observation: str,
    student_count: int,
    source_metadata: dict[str, Any],
    *,
    force: bool,
    dry_run: bool,
    existing_keys: set[str],
    output_path: Path,
) -> str:
    """Process a single observation row. Returns the cache key."""
    key = cache_key(observation_id)

    if not force and key in existing_keys:
        return key

    if dry_run:
        print(f"[dry-run] {observation_id}")
        print(f"  system: {system_prompt[:80]}...")
        print(f"  user:   {build_user_message(observation, student_count)[:120]}...")
        return key

    assert client is not None
    raw = call_api(client, system_prompt, observation, student_count)

    # Fail loudly if the model violates the v2 contract. Pydantic raises with a
    # detailed message pointing at the offending field.
    parsed = ExtractionOutput.model_validate(raw)

    signals_payload = [s.model_dump() for s in parsed.signals]
    result = postprocess(
        {
            "signals": signals_payload,
            "named_students": parsed.named_students,
        },
        student_count,
    )

    output = {
        "schema_version": SCHEMA_VERSION,
        "source": source_metadata,
        "language": parsed.language,
        "source_type": "teacher_observation",
        "observation": observation,
        "student_count": student_count,
        "observation_type": result["observation_type"],
        "signal_count": result["signal_count"],
        "insight_density": result["insight_density"],
        "meaningful_content": result["meaningful_content"],
        "named_students": result["named_students"],
        "named_students_count": result["named_students_count"],
        "signals": result["signals"],
    }
    append_jsonl(output_path, output)
    return key


def sync_quality_checks(rows: list[dict[str, Any]], path: Path) -> int:
    """Append (observation_id, quality_check) to the sidecar for any row not
    already present. Rows with a null quality_check are skipped. Returns the
    number of new lines written."""
    existing: set[str] = set()
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                oid = rec.get("observation_id") if isinstance(rec, dict) else None
                if isinstance(oid, str) and oid:
                    existing.add(oid)

    new = [
        r for r in rows
        if r["observation_id"] not in existing and r.get("quality_check") is not None
    ]
    if not new:
        return 0

    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in new:
            f.write(
                json.dumps(
                    {"observation_id": r["observation_id"], "quality_check": r["quality_check"]},
                    ensure_ascii=False,
                ) + "\n",
            )
    return len(new)


def load_existing_keys(path: Path) -> set[str]:
    """Scan the JSONL file and return the set of cache_keys already present.

    Tolerates a truncated trailing line from a prior crash (skips it).
    """
    if not path.exists():
        return set()
    keys: set[str] = set()
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            source = rec.get("source") if isinstance(rec, dict) else None
            oid = source.get("observation_id") if isinstance(source, dict) else None
            if isinstance(oid, str) and oid:
                keys.add(cache_key(oid))
    return keys


def load_observations(path: Path) -> list[dict[str, Any]]:
    """Read the per-school observation JSON. Returns rows with keys:
      observation_id:  str (UUID)
      observation:     str (from 'comment' in the input)
      student_count:   int (parsed from string)
      quality_check:   upstream quality score (kept separate from extraction output;
                       written to the quality-checks sidecar)
      source_metadata: dict carrying observation_id + upstream pass-through fields
                       (client_id, created_at)

    Logs a count of records skipped for each reason so silent drops are visible.
    """
    data = json.loads(path.read_text())
    if not isinstance(data, list):
        print(f"ERROR: {path} is not a JSON array of records", file=sys.stderr)
        sys.exit(1)

    rows: list[dict[str, Any]] = []
    skipped = {"not_dict": 0, "missing_id": 0, "missing_comment": 0, "bad_student_count": 0}
    for rec in data:
        if not isinstance(rec, dict):
            skipped["not_dict"] += 1
            continue
        oid = str(rec.get("observation_id", "")).strip()
        if not oid:
            skipped["missing_id"] += 1
            continue
        comment = str(rec.get("comment", ""))
        if not comment:
            skipped["missing_comment"] += 1
            continue
        try:
            sc = int(rec.get("student_count", 1))
        except (ValueError, TypeError):
            skipped["bad_student_count"] += 1
            sc = 1
        rows.append({
            "observation_id": oid,
            "observation": comment,
            "student_count": sc,
            "quality_check": rec.get("quality_check"),
            "source_metadata": {
                "observation_id": oid,
                "client_id": rec.get("client_id"),
                "created_at": rec.get("created_at"),
            },
        })

    total_skipped = sum(skipped.values())
    if total_skipped:
        print(
            f"Loaded {len(rows)} records, skipped {total_skipped} "
            f"({', '.join(f'{k}={v}' for k, v in skipped.items() if v)})",
            file=sys.stderr,
        )
    else:
        print(f"Loaded {len(rows)} records from {path.name}", file=sys.stderr)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract insight signals from observations")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N rows")
    parser.add_argument("--force", action="store_true", help="Bust cache and re-call all")
    parser.add_argument("--dry-run", action="store_true", help="Print prompts without API calls")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument(
        "--input",
        type=Path,
        default=OBSERVATIONS_PATH,
        metavar="PATH",
        help=f"Observation JSON file (default: {OBSERVATIONS_PATH})",
    )
    args = parser.parse_args()

    EXTRACTIONS_PATH.parent.mkdir(exist_ok=True)
    existing_keys = load_existing_keys(EXTRACTIONS_PATH)

    system_prompt = load_system_prompt()

    rows = load_observations(args.input)
    if args.limit is not None:
        rows = rows[: args.limit]

    qc_added = sync_quality_checks(rows, QUALITY_CHECKS_PATH)
    if qc_added:
        print(f"Wrote {qc_added} quality_check rows to {QUALITY_CHECKS_PATH}", file=sys.stderr)

    client = None if args.dry_run else make_client()

    processed = 0
    cached = 0
    errors = 0

    def handle_row(row: dict[str, Any]) -> tuple[str, bool, str | None]:
        observation_id = row["observation_id"]
        observation = row["observation"]
        student_count = int(row["student_count"])
        source_metadata = row["source_metadata"]
        key = cache_key(observation_id)
        was_cached = not args.force and key in existing_keys

        try:
            process_row(
                client,
                system_prompt,
                observation_id,
                observation,
                student_count,
                source_metadata,
                force=args.force,
                dry_run=args.dry_run,
                existing_keys=existing_keys,
                output_path=EXTRACTIONS_PATH,
            )
            return key, was_cached, None
        except Exception as e:
            return key, False, f"{observation_id}: {type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(handle_row, row): row for row in rows}
        for future in as_completed(futures):
            key, was_cached, error = future.result()
            if error:
                print(f"ERROR {error}", file=sys.stderr)
                errors += 1
            elif was_cached:
                cached += 1
            else:
                processed += 1

    total = processed + cached + errors
    print(f"\nDone: {total} rows | {processed} extracted | {cached} cached | {errors} errors")


if __name__ == "__main__":
    main()
