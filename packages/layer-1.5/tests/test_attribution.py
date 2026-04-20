from layer_1_5.pipeline.attribution import attribute_observation
from layer_1_5.pipeline.models import LayerOneRecord, ObservationInput, RosterStudent
from layer_1_5.pipeline.roster import RosterIndex


def _roster_student(sid: str, first: str, last: str, crew: str) -> RosterStudent:
    return RosterStudent(
        student_id=sid, first_name=first, last_name=last,
        full_name=f"{first} {last}", crew_id=crew, crew_name=crew, status="ACTIVE",
    )


def _obs(sids: list[str]) -> ObservationInput:
    return ObservationInput(
        observation_id="o1", client_id="c", created_at="2026-04-20T00:00:00Z",
        comment="the students worked together", student_ids=sids, student_count=len(sids),
    )


def _record(signal_count: int = 2, named: list[str] | None = None) -> LayerOneRecord:
    sigs = [
        {
            "type": "behavioral_evidence", "evidence": f"ev{i}", "valence": "positive",
            "domain_descriptors": ["peer"], "participants": [],
        }
        for i in range(signal_count)
    ]
    return LayerOneRecord(observation_id="o1", signals=sigs, named_students=named or [], raw={})


def test_one_tagged_student_no_named_skips_llm() -> None:
    roster = RosterIndex({"s1": _roster_student("s1", "Ana", "P", "y1")})
    obs = _obs(["s1"])
    l1 = _record()
    result = attribute_observation(
        obs, l1, roster,
        llm_client=None, attribution_prompt="", model="anthropic/claude-sonnet-4-6",
    )
    assert result.used_llm is False
    assert all(a.source == "tagged" for a in result.signal_assignments)
    # Every signal gets one assignment: that student, role=actor.
    for a in result.signal_assignments:
        assert len(a.assignments) == 1
        assert a.assignments[0].student_id == "s1"
        assert a.assignments[0].role == "actor"
    assert ("s1", "actor") in result.per_record_meta
    assert result.per_record_meta[("s1", "actor")].source == "tagged"


def test_6_plus_group_uses_uniform_no_llm() -> None:
    roster = RosterIndex({
        f"s{i}": _roster_student(f"s{i}", f"F{i}", "L", "y1") for i in range(7)
    })
    obs = _obs([f"s{i}" for i in range(7)])
    l1 = _record(signal_count=3)
    result = attribute_observation(
        obs, l1, roster,
        llm_client=None, attribution_prompt="", model="anthropic/claude-sonnet-4-6",
    )
    assert result.used_llm is False
    # Every signal is group_uniform, every student appears as group_member.
    for a in result.signal_assignments:
        assert a.source == "group_uniform"
        assert {r.role for r in a.assignments} == {"group_member"}
        assert len(a.assignments) == 7
    # per_record_meta has one entry per student, all role=group_member.
    assert len(result.per_record_meta) == 7
    for (_sid, role), m in result.per_record_meta.items():
        assert role == "group_member"
        assert m.source == "group_uniform"
        assert m.group_context is True


def test_2_to_5_group_without_llm_falls_back_to_uniform() -> None:
    roster = RosterIndex({
        "s1": _roster_student("s1", "Ana", "P", "y1"),
        "s2": _roster_student("s2", "Bo", "Q", "y1"),
    })
    obs = _obs(["s1", "s2"])
    l1 = _record()
    result = attribute_observation(
        obs, l1, roster,
        llm_client=None, attribution_prompt="", model="anthropic/claude-sonnet-4-6",
    )
    assert result.used_llm is False
    for a in result.signal_assignments:
        assert a.source == "group_uniform"
        assert {r.role for r in a.assignments} == {"group_member"}


def test_secondary_participants_surfaced_for_non_tagged_named() -> None:
    roster = RosterIndex({
        "s1": _roster_student("s1", "Ana", "P", "y1"),
        "s2": _roster_student("s2", "Romeo", "Martínez", "y1"),
    })
    obs = _obs(["s1"])
    l1 = _record(named=["Romeo"])
    result = attribute_observation(
        obs, l1, roster,
        llm_client=None, attribution_prompt="", model="anthropic/claude-sonnet-4-6",
    )
    assert any(
        s.student_id == "s2" and s.name_in_text == "Romeo"
        for s in result.secondary_participants
    )
