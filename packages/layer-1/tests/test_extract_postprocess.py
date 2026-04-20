from layer_1.cli.extract import postprocess


def _sig(confidence: str) -> dict:
    return {
        "type": "behavioral_evidence",
        "evidence": "x",
        "confidence": confidence,
    }


def test_meaningful_content_true_when_any_high() -> None:
    result = postprocess({"signals": [_sig("low"), _sig("high")], "named_students": []}, 1)
    assert result["meaningful_content"] is True


def test_meaningful_content_true_when_any_medium() -> None:
    result = postprocess({"signals": [_sig("low"), _sig("medium")], "named_students": []}, 1)
    assert result["meaningful_content"] is True


def test_meaningful_content_false_when_all_low() -> None:
    """'Did well today' canonical case: one low-confidence signal shouldn't
    flip the meaningful_content flag."""
    result = postprocess({"signals": [_sig("low")], "named_students": []}, 1)
    assert result["meaningful_content"] is False


def test_meaningful_content_false_when_zero_signals() -> None:
    result = postprocess({"signals": [], "named_students": []}, 1)
    assert result["meaningful_content"] is False


def test_observation_type_derived_from_student_count() -> None:
    assert postprocess({"signals": [], "named_students": []}, 1)["observation_type"] == "individual"
    assert postprocess({"signals": [], "named_students": []}, 3)["observation_type"] == "group"
