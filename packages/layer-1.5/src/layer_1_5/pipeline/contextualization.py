"""Contextualization LLM caller — one call per (observation, student, role)."""

import json

from openai import OpenAI

from core.llm import call_json
from core.schema.layer1 import ParticipantRole
from core.schema.layer1_5 import (
    ContextualizationLLMResponse,
    ContextualizedSignal,
    HistorySummary,
)


def contextualize(
    *,
    llm_client: OpenAI,
    system_prompt: str,
    model: str,
    attributed_signals: list[dict[str, object]],
    signal_indices: list[int],
    signal_roles: list[ParticipantRole],
    history: HistorySummary,
    student_crew_name: str,
) -> tuple[list[ContextualizedSignal], str]:
    """Return (contextualized_signals, narrative)."""
    signals_view = []
    for idx, role, s in zip(
        signal_indices, signal_roles, attributed_signals, strict=True
    ):
        signals_view.append({
            "signal_index": idx,
            "role": role,
            "evidence": s.get("evidence"),
            "type": s.get("type"),
            "confidence": s.get("confidence"),
            "valence": s.get("valence"),
            "target": s.get("target"),
            "agency": s.get("agency"),
            "temporality_cue": s.get("temporality_cue"),
            "domain_descriptors": s.get("domain_descriptors", []),
            "participants": s.get("participants", []),
        })

    payload = {
        "signals": signals_view,
        "history_summary": history.model_dump(),
        "student_crew": student_crew_name,
    }

    raw = call_json(
        llm_client,
        system_prompt,
        json.dumps(payload, ensure_ascii=False),
        model=model,
    )
    parsed = ContextualizationLLMResponse.model_validate(raw)

    allowed_indices = set(signal_indices)
    role_by_index = dict(zip(signal_indices, signal_roles, strict=True))
    annotated: list[ContextualizedSignal] = []
    seen: set[int] = set()
    for c in parsed.contextualized_signals:
        if c.signal_index not in allowed_indices or c.signal_index in seen:
            continue
        seen.add(c.signal_index)
        novelty = None if history.is_first_observation else c.novelty
        annotated.append(
            ContextualizedSignal(
                signal_index=c.signal_index,
                role=role_by_index[c.signal_index],
                novelty=novelty,
                salience=c.salience,
                reasoning=c.reasoning,
            )
        )

    for idx in signal_indices:
        if idx in seen:
            continue
        annotated.append(
            ContextualizedSignal(
                signal_index=idx,
                role=role_by_index[idx],
                novelty=None,
                salience="routine",
                reasoning="LLM omitted this signal; defaulted to routine.",
            )
        )
    annotated.sort(key=lambda c: c.signal_index)

    return annotated, parsed.narrative
