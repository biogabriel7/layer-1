"""Tests for contextualize() — exercises LLM response handling with a stub."""

from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from core.schema.layer1_5 import HistorySummary
from layer_1_5.pipeline.contextualization import contextualize


def _history(is_first: bool) -> HistorySummary:
    return HistorySummary(
        prior_observation_count=0 if is_first else 3,
        prior_signal_count=0 if is_first else 6,
        prior_individual_signal_count=0 if is_first else 4,
        prior_group_signal_count=0 if is_first else 2,
        prior_concern_flag_count=0,
        is_first_observation=is_first,
    )


_SIGNAL = {
    "evidence": "raised her hand",
    "type": "behavioral_evidence",
    "confidence": "high",
    "valence": "positive",
    "target": None,
    "agency": None,
    "temporality_cue": None,
    "domain_descriptors": ["task"],
    "participants": [],
    "reasoning": "r",
}


def test_first_observation_forces_novelty_null() -> None:
    """Even if the LLM returns a novelty, contextualize() nulls it when
    is_first_observation=True."""
    fake_response: dict[str, Any] = {
        "contextualized_signals": [
            {"signal_index": 0, "novelty": "new", "salience": "routine", "reasoning": "r"}
        ],
        "narrative": "First observation.",
    }
    with patch("layer_1_5.pipeline.contextualization.call_json", return_value=fake_response):
        signals, narrative = contextualize(
            llm_client=None,  # type: ignore[arg-type]
            system_prompt="",
            model="m",
            attributed_signals=[_SIGNAL],
            signal_indices=[0],
            signal_roles=["actor"],
            history=_history(is_first=True),
            student_crew_name="Y1",
        )
    assert signals[0].novelty is None
    assert signals[0].role == "actor"
    assert narrative == "First observation."


def test_malformed_response_raises() -> None:
    """Missing required fields must raise — Pydantic guards the LLM boundary."""
    fake_response: dict[str, Any] = {
        "contextualized_signals": [{"signal_index": 0}],  # missing salience/reasoning
        "narrative": "n",
    }
    with patch("layer_1_5.pipeline.contextualization.call_json", return_value=fake_response):
        with pytest.raises(ValidationError):
            contextualize(
                llm_client=None,  # type: ignore[arg-type]
                system_prompt="", model="m",
                attributed_signals=[_SIGNAL],
                signal_indices=[0],
                signal_roles=["actor"],
                history=_history(False),
                student_crew_name="Y1",
            )


def test_missing_profile_impact_is_accepted() -> None:
    """ContextualizationLLMResponse no longer requires profile_impact — the
    pipeline computes it from salience rollup."""
    fake_response: dict[str, Any] = {
        "contextualized_signals": [
            {"signal_index": 0, "novelty": "new", "salience": "notable", "reasoning": "r"}
        ],
        "narrative": "n",
    }
    with patch("layer_1_5.pipeline.contextualization.call_json", return_value=fake_response):
        signals, narrative = contextualize(
            llm_client=None,  # type: ignore[arg-type]
            system_prompt="", model="m",
            attributed_signals=[_SIGNAL],
            signal_indices=[0],
            signal_roles=["actor"],
            history=_history(False),
            student_crew_name="Y1",
        )
    assert signals[0].salience == "notable"


def test_missing_signal_filled_with_routine() -> None:
    fake_response: dict[str, Any] = {
        "contextualized_signals": [],
        "narrative": "n",
    }
    with patch("layer_1_5.pipeline.contextualization.call_json", return_value=fake_response):
        signals, _ = contextualize(
            llm_client=None,  # type: ignore[arg-type]
            system_prompt="", model="m",
            attributed_signals=[_SIGNAL],
            signal_indices=[0],
            signal_roles=["actor"],
            history=_history(False),
            student_crew_name="Y1",
        )
    assert len(signals) == 1
    assert signals[0].salience == "routine"
    assert signals[0].novelty is None
    assert signals[0].role == "actor"


def test_rejects_out_of_range_signal_index() -> None:
    fake_response: dict[str, Any] = {
        "contextualized_signals": [
            {"signal_index": 0, "novelty": "new", "salience": "notable", "reasoning": "r"},
            {"signal_index": 99, "novelty": "new", "salience": "notable", "reasoning": "r"},
        ],
        "narrative": "n",
    }
    with patch("layer_1_5.pipeline.contextualization.call_json", return_value=fake_response):
        signals, _ = contextualize(
            llm_client=None,  # type: ignore[arg-type]
            system_prompt="", model="m",
            attributed_signals=[_SIGNAL],
            signal_indices=[0],
            signal_roles=["actor"],
            history=_history(False),
            student_crew_name="Y1",
        )
    assert [s.signal_index for s in signals] == [0]
