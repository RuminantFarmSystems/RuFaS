"""Tests for feedlot ration step-up protocol and optimizer constraints."""

import copy
from collections.abc import Generator
import pytest
from unittest.mock import MagicMock
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer


@pytest.fixture(autouse=True)
def _restore_ration_manager_state() -> Generator[None, None, None]:
    """Save and restore RationManager class-level feedlot state around each test.

    Prevents tests that mutate RationManager feedlot attributes from leaking
    state into subsequent tests or other test modules.

    Yields
    ------
    None
        Yields control to the test body; restores state on teardown.
    """
    saved_feeds = copy.deepcopy(getattr(RationManager, "ration_feeds", {}))
    saved_starter = copy.deepcopy(getattr(RationManager, "feedlot_starter_ration", {}))
    saved_transition = copy.deepcopy(getattr(RationManager, "feedlot_transition_ration", {}))
    saved_finisher = copy.deepcopy(getattr(RationManager, "feedlot_finisher_ration", {}))
    yield
    RationManager.ration_feeds = saved_feeds
    RationManager.feedlot_starter_ration = saved_starter
    RationManager.feedlot_transition_ration = saved_transition
    RationManager.feedlot_finisher_ration = saved_finisher


_FEEDLOT_RATION_CONFIG = {
    "rations": [],  # required so existing dairy list comprehensions don't KeyError
    "feedlot_feeds": [301, 302, 303],
    "feedlot_starter_ration": {"301": 50, "303": 50},
    "feedlot_transition_ration": {"301": 65, "302": 20, "303": 15},
    "feedlot_finisher_ration": {"301": 70, "302": 20, "303": 10},
}


@pytest.mark.unit
def test_set_ration_feeds_registers_feedlot_combination() -> None:
    """set_ration_feeds must populate ration_feeds[FEEDLOT_FINISHING]."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    assert AnimalCombination.FEEDLOT_FINISHING in RationManager.ration_feeds


@pytest.mark.unit
def test_set_ration_feeds_feedlot_feed_ids() -> None:
    """set_ration_feeds must store the feedlot feed IDs as RUFAS_IDs (ints)."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    assert RationManager.ration_feeds[AnimalCombination.FEEDLOT_FINISHING] == [301, 302, 303]


@pytest.mark.unit
@pytest.mark.parametrize("phase", ["starter", "transition", "finisher"])
def test_get_feedlot_phase_ration_returns_nonempty_dict(phase: str) -> None:
    """get_feedlot_phase_ration must return a non-empty dict for all three phases."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    mock_req = MagicMock(spec=NutritionRequirements)
    mock_req.dry_matter = 10.0

    result = RationManager.get_feedlot_phase_ration(phase, mock_req)
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.unit
def test_get_feedlot_phase_ration_scales_to_dmi() -> None:
    """Feed amounts must sum to dry_matter when phase ration percentages sum to 100."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    mock_req = MagicMock(spec=NutritionRequirements)
    mock_req.dry_matter = 8.0

    result = RationManager.get_feedlot_phase_ration("finisher", mock_req)
    total_kg = sum(result.values())
    assert total_kg == pytest.approx(8.0)


@pytest.mark.unit
def test_get_feedlot_phase_ration_unknown_phase_falls_back() -> None:
    """An unrecognised phase string must fall back to the finisher ration."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    mock_req = MagicMock(spec=NutritionRequirements)
    mock_req.dry_matter = 8.0

    finisher = RationManager.get_feedlot_phase_ration("finisher", mock_req)
    unknown = RationManager.get_feedlot_phase_ration("unknown_phase", mock_req)
    assert unknown == finisher


@pytest.mark.unit
def test_feedlot_optimizer_select_constraints_does_not_raise() -> None:
    """_select_constraints must return without raising for FEEDLOT_FINISHING."""
    optimizer = RationOptimizer()
    result = optimizer._select_constraints(AnimalCombination.FEEDLOT_FINISHING)
    assert result is not None


@pytest.mark.unit
@pytest.mark.parametrize("phase", ["starter", "transition", "finisher"])
def test_set_ration_feeds_raises_on_negative_percentage(phase: str) -> None:
    """set_ration_feeds must raise ValueError when any ration percentage is negative."""
    bad_config = {
        "rations": [],
        "feedlot_feeds": [301, 302],
        "feedlot_starter_ration": {"301": 50, "302": 50},
        "feedlot_transition_ration": {"301": 65, "302": 20, "303": 15},
        "feedlot_finisher_ration": {"301": 70, "302": 20, "303": 10},
    }
    bad_config[f"feedlot_{phase}_ration"] = {"301": 110, "302": -10}
    with pytest.raises(ValueError, match=f"Feedlot {phase} ration percentages must be non-negative"):
        RationManager.set_ration_feeds(bad_config)


@pytest.mark.unit
@pytest.mark.parametrize("phase", ["starter", "transition", "finisher"])
def test_set_ration_feeds_raises_on_bad_percentages(phase: str) -> None:
    """set_ration_feeds must raise ValueError when a ration's percentages do not sum to 100."""
    bad_config = {
        "rations": [],
        "feedlot_feeds": [301, 302],
        "feedlot_starter_ration": {"301": 50, "302": 50},
        "feedlot_transition_ration": {"301": 65, "302": 20, "303": 15},
        "feedlot_finisher_ration": {"301": 70, "302": 20, "303": 10},
    }
    bad_config[f"feedlot_{phase}_ration"] = {"301": 40, "302": 40}  # sums to 80, not 100
    with pytest.raises(ValueError, match=f"Feedlot {phase} ration percentages must sum to 100.0%"):
        RationManager.set_ration_feeds(bad_config)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("bad_config", "match"),
    [
        (
            {
                "rations": [],
                "feedlot_feeds": [301, 302],
                "feedlot_starter_ration": {"301": 40, "302": 40},  # sums to 80
                "feedlot_transition_ration": {"301": 65, "302": 20, "303": 15},
                "feedlot_finisher_ration": {"301": 70, "302": 20, "303": 10},
            },
            "must sum to 100.0%",
        ),
        (
            {
                "rations": [],
                "feedlot_feeds": [301, 302],
                "feedlot_starter_ration": {"301": 110, "302": -10},  # negative
                "feedlot_transition_ration": {"301": 65, "302": 20, "303": 15},
                "feedlot_finisher_ration": {"301": 70, "302": 20, "303": 10},
            },
            "must be non-negative",
        ),
    ],
)
def test_set_ration_feeds_does_not_mutate_cls_on_validation_failure(bad_config: dict[str, object], match: str) -> None:
    """cls.ration_feeds must remain unchanged when set_ration_feeds raises ValueError."""
    RationManager.set_ration_feeds(_FEEDLOT_RATION_CONFIG)
    assert RationManager.ration_feeds is not None
    feeds_before = dict(RationManager.ration_feeds)

    with pytest.raises(ValueError, match=match):
        RationManager.set_ration_feeds(bad_config)

    assert RationManager.ration_feeds == feeds_before
