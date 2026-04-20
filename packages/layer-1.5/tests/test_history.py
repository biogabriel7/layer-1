from layer_1_5.pipeline.history import build_history_snapshots
from layer_1_5.pipeline.models import LayerOneRecord, ObservationInput


def _obs(oid: str, created: str, student_ids: list[str]) -> ObservationInput:
    return ObservationInput(
        observation_id=oid, client_id="c", created_at=created,
        comment="", student_ids=student_ids, student_count=len(student_ids),
    )


def _rec(oid: str, signals: list[dict]) -> LayerOneRecord:
    return LayerOneRecord(observation_id=oid, signals=signals, named_students=[], raw={})


def _sig(stype: str, valence: str, domain: str | None = None,
         target: str | None = None, evidence: str = "ev") -> dict:
    sig: dict = {"type": stype, "evidence": evidence, "valence": valence}
    if domain:
        sig["domain_descriptors"] = [domain]
    if target:
        sig["target"] = target
    return sig


def test_first_observation_has_empty_snapshot() -> None:
    observations = {"o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"])}
    extractions = {"o1": _rec("o1", [_sig("behavioral_evidence", "positive", "task")])}
    snaps = build_history_snapshots(observations, extractions)
    h = snaps[("o1", "s1")]
    assert h.is_first_observation is True
    assert h.prior_observation_count == 0
    assert h.prior_signal_count == 0
    assert h.prior_individual_signal_count == 0
    assert h.prior_group_signal_count == 0


def test_temporal_ordering() -> None:
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"]),
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1"]),
    }
    extractions = {
        "o1": _rec("o1", [_sig("behavioral_evidence", "positive", "peer", evidence="ev1")]),
        "o2": _rec("o2", [_sig("concern_flag", "negative", "speech", evidence="ev2")]),
    }
    snaps = build_history_snapshots(observations, extractions)
    assert snaps[("o1", "s1")].prior_observation_count == 0
    h2 = snaps[("o2", "s1")]
    assert h2.is_first_observation is False
    assert h2.prior_observation_count == 1
    assert h2.prior_signal_count == 1


def test_individual_vs_group_split() -> None:
    """Individual observations (student_count=1) and group observations
    accumulate into separate counts."""
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"]),          # individual
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1", "s2"]),    # group
        "o3": _obs("o3", "2026-03-01T00:00:00Z", ["s1"]),          # individual
    }
    extractions = {
        "o1": _rec("o1", [_sig("behavioral_evidence", "positive", "task")]),
        "o2": _rec("o2", [_sig("behavioral_evidence", "positive", "peer")]),
        "o3": _rec("o3", [_sig("behavioral_evidence", "positive", "peer")]),
    }
    snaps = build_history_snapshots(observations, extractions)
    h3 = snaps[("o3", "s1")]
    assert h3.prior_signal_count == 2
    assert h3.prior_individual_signal_count == 1  # just o1
    assert h3.prior_group_signal_count == 1       # just o2


def test_domain_fallback_to_target() -> None:
    """When domain_descriptors is empty, the primary key falls back to target."""
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"]),
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1"]),
    }
    extractions = {
        "o1": _rec("o1", [_sig("behavioral_evidence", "positive", target="task")]),
        "o2": _rec("o2", []),
    }
    snaps = build_history_snapshots(observations, extractions)
    h = snaps[("o2", "s1")]
    # Domain frequency uses target when domain_descriptors is absent
    assert h.prior_domain_frequency.get("task") == 1


def test_recent_evidence_snippets_carry_facets() -> None:
    """Enriched snippets include type/domain/valence alongside evidence."""
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"]),
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1"]),
    }
    extractions = {
        "o1": _rec("o1", [_sig("behavioral_evidence", "positive", "peer", evidence="raised hand")]),
        "o2": _rec("o2", []),
    }
    snaps = build_history_snapshots(observations, extractions)
    h = snaps[("o2", "s1")]
    assert len(h.recent_evidence_snippets) == 1
    snip = h.recent_evidence_snippets[0]
    assert snip["evidence"] == "raised hand"
    assert snip["type"] == "behavioral_evidence"
    assert snip["primary_domain"] == "peer"
    assert snip["valence"] == "positive"
    assert snip["group_context"] is False


def test_concern_flag_count_accumulates() -> None:
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1"]),
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1"]),
        "o3": _obs("o3", "2026-03-01T00:00:00Z", ["s1"]),
    }
    extractions = {
        "o1": _rec("o1", [_sig("concern_flag", "negative", "speech", evidence="a")]),
        "o2": _rec("o2", [_sig("behavioral_evidence", "positive", "task", evidence="b")]),
        "o3": _rec("o3", [_sig("concern_flag", "negative", "peer", evidence="c")]),
    }
    snaps = build_history_snapshots(observations, extractions)
    assert snaps[("o3", "s1")].prior_concern_flag_count == 1


def test_group_signals_count_for_every_tagged_student() -> None:
    observations = {
        "o1": _obs("o1", "2026-01-01T00:00:00Z", ["s1", "s2"]),
        "o2": _obs("o2", "2026-02-01T00:00:00Z", ["s1"]),
    }
    extractions = {
        "o1": _rec("o1", [_sig("behavioral_evidence", "positive", "peer", evidence="shared")]),
        "o2": _rec("o2", []),
    }
    snaps = build_history_snapshots(observations, extractions)
    assert snaps[("o2", "s1")].prior_signal_count == 1
    assert snaps[("o2", "s1")].prior_group_signal_count == 1
    assert ("o2", "s2") not in snaps
