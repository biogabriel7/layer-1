from layer_1_5.pipeline.models import RosterStudent
from layer_1_5.pipeline.roster import RosterIndex


def _roster(*rows: tuple[str, str, str, str]) -> dict[str, RosterStudent]:
    """Build a roster from (student_id, first, last, crew_id) tuples."""
    return {
        sid: RosterStudent(
            student_id=sid,
            first_name=first,
            last_name=last,
            full_name=f"{first} {last}",
            crew_id=crew,
            crew_name=crew,
            status="ACTIVE",
        )
        for sid, first, last, crew in rows
    }


def test_full_name_match_wins() -> None:
    idx = RosterIndex(_roster(
        ("a", "Romeo", "Martínez", "y7"),
        ("b", "Romeo", "Peña", "y5"),
    ))
    r = idx.resolve("Romeo Martínez")
    assert r.student_id == "a"
    assert r.match_kind == "full_name"


def test_crew_scoped_first_name_disambiguates() -> None:
    idx = RosterIndex(_roster(
        ("a", "Romeo", "Martínez", "y7"),
        ("b", "Romeo", "Peña", "y5"),
    ))
    # Observation tagged a classmate in y5 → prefer Romeo Peña.
    r = idx.resolve("Romeo", crew_ids={"y5"})
    assert r.student_id == "b"
    assert r.match_kind == "first_name_unique_in_crew"


def test_ambiguous_when_both_in_same_crew() -> None:
    idx = RosterIndex(_roster(
        ("a", "Romeo", "Martínez", "y7"),
        ("b", "Romeo", "Peña", "y7"),
    ))
    r = idx.resolve("Romeo", crew_ids={"y7"})
    assert r.student_id is None
    assert r.match_kind == "ambiguous"
    assert set(r.candidates) == {"a", "b"}


def test_unique_first_name_client_wide_fallback() -> None:
    idx = RosterIndex(_roster(
        ("a", "Sofia", "López", "y3"),
    ))
    r = idx.resolve("Sofia")  # no crew hint
    assert r.student_id == "a"
    assert r.match_kind == "first_name_unique_client"


def test_unresolved() -> None:
    idx = RosterIndex(_roster(("a", "Ana", "P", "y1")))
    r = idx.resolve("Zzz")
    assert r.student_id is None
    assert r.match_kind == "unresolved"


def test_accent_and_case_normalization() -> None:
    idx = RosterIndex(_roster(("a", "Mía", "Ruiz", "y1")))
    r = idx.resolve("MÍA")
    assert r.student_id == "a"
