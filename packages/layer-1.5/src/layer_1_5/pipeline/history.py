"""Pass 1: build per-student, time-ordered history snapshots.

The snapshot for an observation at time `t` for student S only includes signals
from S's prior observations with `created_at < t`. This prevents future data
from leaking into the present contextualization.

We attribute signals naively to every tagged student at history-build time
(before attribution resolves). Downstream, the LLM judging novelty/salience
sees a `role` on the *current* signal and weights accordingly.

History is split by observation size:
- `prior_individual_signal_count`: signals from this student's single-student
  observations.
- `prior_group_signal_count`: signals from group observations (>1 tagged).

Individual signals are stronger evidence about the student; group signals are
contextual. The contextualization LLM uses this split when judging novelty.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from core.schema.layer1_5 import HistorySummary
from layer_1_5.pipeline.models import LayerOneRecord, ObservationInput

_RECENT_SNIPPET_COUNT = 5


def _primary_key(signal: dict[str, Any]) -> str:
    """Novelty-key primary component: first domain_descriptor, then target, then '<none>'."""
    domains = signal.get("domain_descriptors") or []
    if isinstance(domains, list) and domains:
        d0 = str(domains[0])
        if d0:
            return d0
    target = signal.get("target")
    if isinstance(target, str) and target:
        return target
    return "<none>"


@dataclass
class _StudentTimeline:
    """Mutable running counters + rolling recent evidence for one student."""

    observation_count: int = 0
    signal_count: int = 0
    individual_signal_count: int = 0
    group_signal_count: int = 0
    concern_flag_count: int = 0
    by_type: Counter[str] = field(default_factory=Counter)
    by_domain: Counter[str] = field(default_factory=Counter)
    by_valence: Counter[str] = field(default_factory=Counter)
    recent: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> HistorySummary:
        return HistorySummary(
            prior_observation_count=self.observation_count,
            prior_signal_count=self.signal_count,
            prior_individual_signal_count=self.individual_signal_count,
            prior_group_signal_count=self.group_signal_count,
            prior_concern_flag_count=self.concern_flag_count,
            is_first_observation=self.observation_count == 0,
            prior_signals_by_type=dict(self.by_type),
            prior_domain_frequency=dict(self.by_domain),
            prior_valence_distribution=dict(self.by_valence),
            recent_evidence_snippets=list(self.recent),
        )

    def absorb(
        self,
        signals: list[dict[str, Any]],
        created_at: str,
        *,
        is_group: bool,
    ) -> None:
        self.observation_count += 1
        for s in signals:
            self.signal_count += 1
            if is_group:
                self.group_signal_count += 1
            else:
                self.individual_signal_count += 1
            stype = str(s.get("type", ""))
            if stype:
                self.by_type[stype] += 1
            if stype == "concern_flag":
                self.concern_flag_count += 1
            key = _primary_key(s)
            if key and key != "<none>":
                self.by_domain[key] += 1
            valence = s.get("valence")
            if isinstance(valence, str) and valence:
                self.by_valence[valence] += 1
            evidence = str(s.get("evidence", ""))
            if evidence:
                self.recent.append({
                    "evidence": evidence[:200],
                    "created_at": created_at,
                    "type": stype or None,
                    "primary_domain": key if key != "<none>" else None,
                    "valence": valence if isinstance(valence, str) else None,
                    "group_context": is_group,
                })
        if len(self.recent) > _RECENT_SNIPPET_COUNT:
            self.recent[:] = self.recent[-_RECENT_SNIPPET_COUNT:]


def build_history_snapshots(
    observations: dict[str, ObservationInput],
    extractions: dict[str, LayerOneRecord],
) -> dict[tuple[str, str], HistorySummary]:
    """For every (observation_id, student_id) pair with a tag, produce the
    history summary BEFORE that observation.

    Returns a map keyed by (observation_id, student_id).
    """
    ordered = sorted(
        observations.values(), key=lambda o: (o.created_at, o.observation_id)
    )

    timelines: dict[str, _StudentTimeline] = {}
    snapshots: dict[tuple[str, str], HistorySummary] = {}

    for obs in ordered:
        l1 = extractions.get(obs.observation_id)
        signals = l1.signals if l1 is not None else []
        is_group = len(obs.student_ids) > 1

        for sid in obs.student_ids:
            tl = timelines.setdefault(sid, _StudentTimeline())
            snapshots[(obs.observation_id, sid)] = tl.snapshot()

        for sid in obs.student_ids:
            timelines[sid].absorb(signals, obs.created_at, is_group=is_group)

    return snapshots
