from core.schema.layer1_5 import ContextualizedSignal
from layer_1_5.pipeline.impact import rollup_profile_impact


def _s(idx: int, salience: str) -> ContextualizedSignal:
    return ContextualizedSignal(
        signal_index=idx, novelty=None, salience=salience, reasoning="t"
    )


def test_any_significant_rolls_up_to_high() -> None:
    assert rollup_profile_impact([_s(0, "routine"), _s(1, "significant")]) == "high"


def test_notable_without_significant_is_moderate() -> None:
    assert rollup_profile_impact([_s(0, "routine"), _s(1, "notable")]) == "moderate"


def test_all_routine_is_minimal() -> None:
    assert rollup_profile_impact([_s(0, "routine"), _s(1, "routine")]) == "minimal"


def test_empty_is_minimal() -> None:
    assert rollup_profile_impact([]) == "minimal"
