"""Layer 1.5 CLI — reads Layer 1 extractions + observations + roster, emits
one JSONL record per (observation_id, student_id, role) tuple to
`outputs/contextualizations.jsonl`.

Each observation incurs zero or one Attribution LLM call and one
Contextualization LLM call per attributed (student, role) pair.
"""

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from openai import OpenAI

from core.io import append_jsonl
from core.llm import make_client
from core.schema.layer1 import ParticipantRole
from core.schema.layer1_5 import (
    ContextualizedSignal,
    HistorySummary,
    SecondaryParticipant,
    StudentAttribution,
)
from layer_1_5.pipeline.attribution import (
    ObservationAttribution,
    SignalAssignment,
    attribute_observation,
)
from layer_1_5.pipeline.contextualization import contextualize
from layer_1_5.pipeline.history import build_history_snapshots
from layer_1_5.pipeline.impact import rollup_profile_impact
from layer_1_5.pipeline.loader import (
    load_extractions,
    load_observations,
    load_roster,
)
from layer_1_5.pipeline.models import (
    ATTRIBUTION_PROMPT_PATH,
    CONTEXTUALIZATION_PROMPT_PATH,
    CONTEXTUALIZATIONS_PATH,
    DEFAULT_MODEL,
    INPUTS_DIR,
    SCHEMA_VERSION,
    LayerOneRecord,
    ObservationInput,
)
from layer_1_5.pipeline.roster import RosterIndex


def _signals_by_student_role(
    assignments: list[SignalAssignment],
) -> dict[tuple[str, ParticipantRole], list[int]]:
    """Group signal indices by (student_id, role)."""
    by_pair: dict[tuple[str, ParticipantRole], list[int]] = {}
    for a in assignments:
        seen: set[tuple[str, ParticipantRole]] = set()
        for r in a.assignments:
            key = (r.student_id, r.role)
            if key in seen:
                continue
            seen.add(key)
            by_pair.setdefault(key, []).append(a.signal_index)
    return by_pair


def _emit_record(
    *,
    obs: ObservationInput,
    language: str | None,
    student_id: str,
    role: ParticipantRole,
    contextualized: list[ContextualizedSignal],
    profile_impact: str,
    narrative: str,
    history: HistorySummary,
    secondaries: list[SecondaryParticipant],
    per_record_attr: StudentAttribution,
    used_attribution_llm: bool,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source": {
            "observation_id": obs.observation_id,
            "client_id": obs.client_id,
            "student_id": student_id,
            "role": role,
            "created_at": obs.created_at,
        },
        "language": language,
        "attribution": per_record_attr.model_dump(),
        "contextualized_signals": [c.model_dump() for c in contextualized],
        "profile_impact": profile_impact,
        "narrative": narrative,
        "history_summary": history.model_dump(),
        "secondary_participants": [s.model_dump() for s in secondaries],
        "used_attribution_llm": used_attribution_llm,
    }


def _process_observation(
    *,
    obs: ObservationInput,
    l1: LayerOneRecord,
    roster: RosterIndex,
    snapshots: dict[tuple[str, str], HistorySummary],
    llm_client: OpenAI | None,
    attribution_prompt: str,
    contextualization_prompt: str,
    model: str,
    output_path: Path,
    dry_run: bool,
) -> int:
    """Attribute + contextualize one observation; return records written."""
    attribution: ObservationAttribution = attribute_observation(
        obs, l1, roster,
        llm_client=llm_client,
        attribution_prompt=attribution_prompt,
        model=model,
    )
    language = l1.raw.get("language") if isinstance(l1.raw, dict) else None
    language_str = language if isinstance(language, str) else None

    signals_by_pair = _signals_by_student_role(attribution.signal_assignments)

    records_written = 0
    # Preserve deterministic emission order: tagged students first in list
    # order, then roles alphabetically.
    student_order = {sid: i for i, sid in enumerate(obs.student_ids)}
    fallback_rank = len(obs.student_ids)
    ordered_keys = sorted(
        signals_by_pair,
        key=lambda k: (student_order.get(k[0], fallback_rank), k[1]),
    )

    for sid, role in ordered_keys:
        indices = signals_by_pair[(sid, role)]
        if not indices:
            continue
        roles = [role] * len(indices)
        attributed_signals = [l1.signals[i] for i in indices]
        history = snapshots.get((obs.observation_id, sid))
        if history is None:
            continue

        if dry_run or llm_client is None:
            print(
                f"[dry-run] obs={obs.observation_id[:8]} student={sid[:8]} role={role} "
                f"signals={len(indices)} history.prior_obs={history.prior_observation_count}"
            )
            continue

        student = roster.get(sid)
        contextualized, narrative = contextualize(
            llm_client=llm_client,
            system_prompt=contextualization_prompt,
            model=model,
            attributed_signals=attributed_signals,
            signal_indices=indices,
            signal_roles=roles,
            history=history,
            student_crew_name=student.crew_name if student else "",
        )
        profile_impact = rollup_profile_impact(contextualized)
        per_record_attr = attribution.per_record_meta[(sid, role)]

        record = _emit_record(
            obs=obs,
            language=language_str,
            student_id=sid,
            role=role,
            contextualized=contextualized,
            profile_impact=profile_impact,
            narrative=narrative,
            history=history,
            secondaries=attribution.secondary_participants,
            per_record_attr=per_record_attr,
            used_attribution_llm=attribution.used_llm,
        )
        append_jsonl(output_path, record)
        records_written += 1

    return records_written


def main() -> None:
    parser = argparse.ArgumentParser(description="Layer 1.5: student-contextualized extraction")
    parser.add_argument(
        "--extractions", type=Path, required=True,
        help="Path to Layer 1 extractions.jsonl",
    )
    parser.add_argument(
        "--observations", type=Path, required=True,
        help="Path to observations JSON with student_ids",
    )
    parser.add_argument(
        "--roster", type=Path, required=False,
        help=f"Path to roster JSON (default: most recent in {INPUTS_DIR})",
    )
    parser.add_argument(
        "--output", type=Path, default=CONTEXTUALIZATIONS_PATH,
        help=f"Output JSONL (default: {CONTEXTUALIZATIONS_PATH})",
    )
    parser.add_argument("--limit", type=int, default=None, help="Process only first N observations")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="OpenRouter model id")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Skip LLM calls; print per-record plan",
    )
    args = parser.parse_args()

    if args.roster is None:
        candidates = sorted(INPUTS_DIR.glob("roster-*.json"))
        if not candidates:
            print(f"ERROR: no roster-*.json in {INPUTS_DIR}; pass --roster", file=sys.stderr)
            sys.exit(1)
        args.roster = candidates[-1]
        print(f"Using roster: {args.roster}", file=sys.stderr)

    extractions = load_extractions(args.extractions)
    observations = load_observations(args.observations)
    roster = RosterIndex(load_roster(args.roster))

    print(
        f"Loaded {len(extractions)} extractions, {len(observations)} observations, "
        f"{len(roster)} students",
        file=sys.stderr,
    )

    snapshots = build_history_snapshots(observations, extractions)

    ordered_obs = sorted(observations.values(), key=lambda o: (o.created_at, o.observation_id))
    ordered_obs = [o for o in ordered_obs if o.observation_id in extractions]
    if args.limit is not None:
        ordered_obs = ordered_obs[: args.limit]

    args.output.parent.mkdir(exist_ok=True)

    attribution_prompt = ATTRIBUTION_PROMPT_PATH.read_text()
    contextualization_prompt = CONTEXTUALIZATION_PROMPT_PATH.read_text()

    llm_client: OpenAI | None = None if args.dry_run else make_client()

    def handle(obs: ObservationInput) -> int:
        l1 = extractions[obs.observation_id]
        try:
            return _process_observation(
                obs=obs, l1=l1, roster=roster, snapshots=snapshots,
                llm_client=llm_client,
                attribution_prompt=attribution_prompt,
                contextualization_prompt=contextualization_prompt,
                model=args.model,
                output_path=args.output,
                dry_run=args.dry_run,
            )
        except Exception as e:
            print(f"ERROR obs={obs.observation_id}: {type(e).__name__}: {e}", file=sys.stderr)
            return 0

    total_records = 0
    if args.workers <= 1:
        for obs in ordered_obs:
            total_records += handle(obs)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(handle, obs) for obs in ordered_obs]
            for fut in as_completed(futures):
                total_records += fut.result()

    print(
        f"\nDone: {len(ordered_obs)} observations processed, {total_records} records written",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
