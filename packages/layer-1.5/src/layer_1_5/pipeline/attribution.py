"""Attribution decision tree + LLM caller.

Given one observation (text + tagged student_ids + Layer 1 signals + named_students)
and a RosterIndex, decide for each signal which tagged student(s) it belongs
to AND each student's role (actor / recipient / group_member / bystander).

Recipient-aware: a signal like "Ana helped Marcos" belongs to BOTH Ana (actor)
and Marcos (recipient). Both students get records.

Deterministic paths (no LLM):
- 1 tagged student with no ambiguous named → all signals `tagged`, role=actor.
- 6+ tagged students → all signals `group_uniform`, role=group_member.

Otherwise: Attribution LLM picks per-signal role assignments.
"""

import json
from dataclasses import dataclass, field
from typing import Any, cast

from openai import OpenAI

from core.llm import call_json
from core.schema.layer1 import Confidence, ParticipantRole
from core.schema.layer1_5 import (
    AttributionLLMResponse,
    AttributionSource,
    SecondaryMatchKind,
    SecondaryParticipant,
    StudentAttribution,
)
from layer_1_5.pipeline.models import (
    GROUP_UNIFORM_THRESHOLD,
    LayerOneRecord,
    ObservationInput,
    ResolvedName,
)
from layer_1_5.pipeline.roster import RosterIndex


@dataclass
class SignalRoleAssignment:
    """One student's role in one signal."""

    student_id: str
    role: ParticipantRole


@dataclass
class SignalAssignment:
    """All tagged students that belong to one signal, each with their role."""

    signal_index: int
    source: AttributionSource
    assignments: list[SignalRoleAssignment] = field(default_factory=list)
    confidence: Confidence | None = None
    reasoning: str | None = None


@dataclass
class ObservationAttribution:
    """Output of attributing one observation — per-signal assignments + shared
    secondary participants + per-(student, role) attribution metadata."""

    signal_assignments: list[SignalAssignment]
    secondary_participants: list[SecondaryParticipant]
    # Keyed by (student_id, role) — one StudentAttribution per record we emit.
    per_record_meta: dict[tuple[str, ParticipantRole], StudentAttribution]
    used_llm: bool


def _resolve_named_students(
    named: list[str], roster: RosterIndex, crew_ids: set[str]
) -> tuple[list[ResolvedName], list[ResolvedName]]:
    resolved: list[ResolvedName] = []
    ambiguous: list[ResolvedName] = []
    for name in named:
        r = roster.resolve(name, crew_ids=crew_ids)
        if r.match_kind == "ambiguous":
            ambiguous.append(r)
        elif r.student_id is not None:
            resolved.append(r)
    return resolved, ambiguous


def _build_attribution_prompt_payload(
    obs: ObservationInput,
    l1: LayerOneRecord,
    tagged_view: list[dict[str, Any]],
    ambiguous_named: list[ResolvedName],
    roster: RosterIndex,
) -> dict[str, Any]:
    ambiguous_payload: list[dict[str, Any]] = []
    for r in ambiguous_named:
        cands: list[dict[str, Any]] = []
        for sid in r.candidates:
            cand = roster.get(sid)
            if cand is None:
                continue
            cands.append({
                "student_id": cand.student_id,
                "first_name": cand.first_name,
                "last_name": cand.last_name,
                "crew_name": cand.crew_name,
            })
        ambiguous_payload.append({"name_in_text": r.name_in_text, "candidates": cands})

    signals_view: list[dict[str, Any]] = []
    for i, sig in enumerate(l1.signals):
        signals_view.append({
            "signal_index": i,
            "evidence": sig.get("evidence"),
            "type": sig.get("type"),
            "participants": sig.get("participants", []),
            "domain_descriptors": sig.get("domain_descriptors", []),
        })

    return {
        "observation_text": obs.comment,
        "signals": signals_view,
        "tagged_students": tagged_view,
        "ambiguous_named": ambiguous_payload,
    }


def _tagged_view(obs: ObservationInput, roster: RosterIndex) -> list[dict[str, Any]]:
    view: list[dict[str, Any]] = []
    for sid in obs.student_ids:
        s = roster.get(sid)
        if s is None:
            view.append({
                "student_id": sid,
                "first_name": None,
                "last_name": None,
                "crew_name": None,
            })
            continue
        view.append({
            "student_id": s.student_id,
            "first_name": s.first_name,
            "last_name": s.last_name,
            "crew_name": s.crew_name,
        })
    return view


def _uniform_assignments(
    signals: list[dict[str, Any]], student_ids: list[str]
) -> list[SignalAssignment]:
    return [
        SignalAssignment(
            signal_index=i,
            source="group_uniform",
            assignments=[
                SignalRoleAssignment(student_id=sid, role="group_member")
                for sid in student_ids
            ],
        )
        for i in range(len(signals))
    ]


def _single_student_assignments(
    signals: list[dict[str, Any]], student_id: str
) -> list[SignalAssignment]:
    return [
        SignalAssignment(
            signal_index=i,
            source="tagged",
            assignments=[SignalRoleAssignment(student_id=student_id, role="actor")],
        )
        for i in range(len(signals))
    ]


def _build_per_record_meta(
    assignments: list[SignalAssignment],
    student_ids: list[str],
) -> dict[tuple[str, ParticipantRole], StudentAttribution]:
    """For each (student, role) that appears in any signal assignment, compute
    the StudentAttribution metadata for the record we'll emit."""
    n = len(student_ids)
    result: dict[tuple[str, ParticipantRole], StudentAttribution] = {}
    for a in assignments:
        # `tagged` is the single-student path; other sources reflect group context.
        group_context = a.source != "tagged"
        group_size = 1 if a.source == "tagged" else n
        confidence = a.confidence if a.source == "named_match" else None
        for r in a.assignments:
            key = (r.student_id, r.role)
            if key in result:
                continue
            result[key] = StudentAttribution(
                source=a.source,
                role=r.role,
                group_context=group_context,
                group_size=group_size,
                confidence=confidence,
            )
    return result


def attribute_observation(
    obs: ObservationInput,
    l1: LayerOneRecord,
    roster: RosterIndex,
    *,
    llm_client: OpenAI | None,
    attribution_prompt: str,
    model: str,
) -> ObservationAttribution:
    """Main entry: decide per-signal student+role attributions for one obs."""
    n = len(obs.student_ids)
    tagged_crew_ids = roster.crew_ids_for(obs.student_ids)

    resolved_names, ambiguous_names = _resolve_named_students(
        l1.named_students, roster, tagged_crew_ids
    )

    tagged_set = set(obs.student_ids)
    deterministic_secondary: list[SecondaryParticipant] = []
    for r in resolved_names:
        sid = r.student_id
        # `_resolve_named_students` only keeps entries with a resolved
        # student_id, which rules out the "ambiguous"/"unresolved" match_kinds.
        if sid is None or sid in tagged_set:
            continue
        deterministic_secondary.append(
            SecondaryParticipant(
                student_id=sid,
                name_in_text=r.name_in_text,
                match=cast(SecondaryMatchKind, r.match_kind),
            )
        )

    # Branch 1: single-student, no ambiguity → pure deterministic.
    if n == 1 and not ambiguous_names:
        assignments = _single_student_assignments(l1.signals, obs.student_ids[0])
        meta = _build_per_record_meta(assignments, obs.student_ids)
        return ObservationAttribution(
            signal_assignments=assignments,
            secondary_participants=deterministic_secondary,
            per_record_meta=meta,
            used_llm=False,
        )

    # Branch 2: 6+ tagged → uniform, skip LLM.
    if n >= GROUP_UNIFORM_THRESHOLD:
        assignments = _uniform_assignments(l1.signals, obs.student_ids)
        meta = _build_per_record_meta(assignments, obs.student_ids)
        return ObservationAttribution(
            signal_assignments=assignments,
            secondary_participants=deterministic_secondary,
            per_record_meta=meta,
            used_llm=False,
        )

    # Branch 3: no tagged students — nothing to attribute.
    if n == 0:
        return ObservationAttribution(
            signal_assignments=[],
            secondary_participants=deterministic_secondary,
            per_record_meta={},
            used_llm=False,
        )

    # Branch 4: 1-student ambiguous OR 2-5 group → LLM.
    tagged_view = _tagged_view(obs, roster)
    payload = _build_attribution_prompt_payload(
        obs, l1, tagged_view, ambiguous_names, roster
    )

    if llm_client is None:
        # Dry-run fallback.
        if n == 1:
            assignments = _single_student_assignments(l1.signals, obs.student_ids[0])
        else:
            assignments = _uniform_assignments(l1.signals, obs.student_ids)
        meta = _build_per_record_meta(assignments, obs.student_ids)
        return ObservationAttribution(
            signal_assignments=assignments,
            secondary_participants=deterministic_secondary,
            per_record_meta=meta,
            used_llm=False,
        )

    raw = call_json(
        llm_client,
        attribution_prompt,
        json.dumps(payload, ensure_ascii=False),
        model=model,
    )
    parsed = AttributionLLMResponse.model_validate(raw)

    # Convert to our internal assignments. Clamp student_ids to the tagged set.
    assignments_by_index: dict[int, SignalAssignment] = {}
    for e in parsed.signal_attributions:
        if not 0 <= e.signal_index < len(l1.signals):
            continue
        valid_roles: list[SignalRoleAssignment] = []
        for a in e.assignments:
            if a.student_id in tagged_set:
                valid_roles.append(SignalRoleAssignment(
                    student_id=a.student_id, role=a.role,
                ))
        if not valid_roles:
            continue
        # `tagged` is reserved for single-student observations; in a group
        # context it's retyped to `group_uniform` for consistency.
        src: AttributionSource = (
            "group_uniform" if e.source == "tagged" and n > 1 else e.source
        )
        assignments_by_index[e.signal_index] = SignalAssignment(
            signal_index=e.signal_index,
            source=src,
            assignments=valid_roles,
            confidence=e.confidence,
            reasoning=e.reasoning,
        )

    # Fill missing signals with safe defaults.
    assignments = []
    for i in range(len(l1.signals)):
        if i in assignments_by_index:
            assignments.append(assignments_by_index[i])
        elif n == 1:
            assignments.append(SignalAssignment(
                signal_index=i, source="tagged",
                assignments=[SignalRoleAssignment(
                    student_id=obs.student_ids[0], role="actor",
                )],
            ))
        else:
            assignments.append(SignalAssignment(
                signal_index=i, source="group_uniform",
                assignments=[
                    SignalRoleAssignment(student_id=sid, role="group_member")
                    for sid in obs.student_ids
                ],
            ))

    meta = _build_per_record_meta(assignments, obs.student_ids)

    # Secondary participants: deterministic + LLM-resolved (dedupe by name).
    seen_names = {s.name_in_text for s in deterministic_secondary}
    secondaries: list[SecondaryParticipant] = list(deterministic_secondary)
    for se in parsed.secondary_participants:
        if se.name_in_text in seen_names:
            continue
        if se.student_id not in roster:
            continue
        secondaries.append(
            SecondaryParticipant(
                student_id=se.student_id,
                name_in_text=se.name_in_text,
                match="llm_resolved",
            )
        )

    return ObservationAttribution(
        signal_assignments=assignments,
        secondary_participants=secondaries,
        per_record_meta=meta,
        used_llm=True,
    )
