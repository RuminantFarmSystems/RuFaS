"""Tests for Step 6 — beef ration registration, seasonal selection, optimizer constraints (PR-C).

RED tests must FAIL before Step 6 is implemented and PASS (GREEN) after.
"""

from __future__ import annotations

import copy
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard

# ── helpers ──────────────────────────────────────────────────────────────────


VALID_RATION_CONFIG: dict[str, object] = {
    "rations": [],
    "beef_lactating_pasture_ration": {"301": 60.0, "302": 40.0},
    "beef_dry_gestating_ration": {"303": 100.0},
    "beef_creep_feed_ration": {"304": 100.0},
    "beef_replacement_heifer_ration": {"305": 100.0},
}

SENTINEL_LACTATING: dict[int, float] = {999: 50.0, 998: 50.0}
SENTINEL_DRY: dict[int, float] = {997: 100.0}
SENTINEL_CREEP: dict[int, float] = {996: 100.0}
SENTINEL_HEIFER: dict[int, float] = {995: 100.0}


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _restore_animal_config_creep() -> Generator[None, None, None]:
    """Save and restore AnimalConfig.beef_creep_feeding_enabled after each test.

    Returns
    -------
    Generator[None, None, None]
        Yields once; restores the original boolean value on teardown.
    """
    saved = AnimalConfig.beef_creep_feeding_enabled
    yield
    AnimalConfig.beef_creep_feeding_enabled = saved


@pytest.fixture(autouse=True)
def _restore_ration_manager_beef_state() -> Generator[None, None, None]:
    """Save and restore RationManager beef ration class attributes around each test.

    Prevents ration state leaking between tests.

    Yields
    ------
    None
        Yields control to the test body; restores state on teardown.
    """
    saved_lactating = copy.deepcopy(getattr(RationManager, "beef_lactating_pasture_ration", {}))
    saved_dry = copy.deepcopy(getattr(RationManager, "beef_dry_gestating_ration", {}))
    saved_creep = copy.deepcopy(getattr(RationManager, "beef_creep_feed_ration", {}))
    saved_heifer = copy.deepcopy(getattr(RationManager, "beef_replacement_heifer_ration", {}))
    yield
    RationManager.beef_lactating_pasture_ration = saved_lactating
    RationManager.beef_dry_gestating_ration = saved_dry
    RationManager.beef_creep_feed_ration = saved_creep
    RationManager.beef_replacement_heifer_ration = saved_heifer


def _make_minimal_ration_optimizer() -> RationOptimizer:
    """Build a RationOptimizer with stub constraints set.

    Returns
    -------
    RationOptimizer
        A RationOptimizer instance with NRC-standard constraints initialised via a mock ration config.
    """
    optimizer = RationOptimizer()
    mock_ration_config = MagicMock()
    mock_ration_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(mock_ration_config)
    return optimizer


# ── Task 6.1: Register four beef rations ──────────────────────────────────────


def test_set_ration_feeds_registers_beef_rations() -> None:
    """Happy path: all four beef rations are stored on the class after set_ration_feeds.

    Verifies Task 6.1: lactating-pasture, dry-gestating, creep-feed, and replacement-heifer
    rations are committed to RationManager ClassVars when all four are valid.
    """
    RationManager.set_ration_feeds(VALID_RATION_CONFIG)
    assert RationManager.beef_lactating_pasture_ration == {301: 60.0, 302: 40.0}
    assert RationManager.beef_dry_gestating_ration == {303: 100.0}
    assert RationManager.beef_creep_feed_ration == {304: 100.0}
    assert RationManager.beef_replacement_heifer_ration == {305: 100.0}


@pytest.mark.parametrize(
    "ration_key",
    [
        "beef_lactating_pasture_ration",
        "beef_dry_gestating_ration",
        "beef_creep_feed_ration",
        "beef_replacement_heifer_ration",
    ],
)
def test_set_ration_feeds_rejects_negative_percentage(ration_key: str) -> None:
    """set_ration_feeds raises ValueError when any beef ration percentage is negative.

    Parametrized over all four beef ration keys to confirm the guard applies uniformly.
    """
    config: dict[str, object] = {
        "rations": [],
        "beef_lactating_pasture_ration": {"301": 100.0},
        "beef_dry_gestating_ration": {"302": 100.0},
        "beef_creep_feed_ration": {"303": 100.0},
        "beef_replacement_heifer_ration": {"304": 100.0},
    }
    config[ration_key] = {"301": -5.0, "302": 105.0}

    with pytest.raises(ValueError, match="non-negative"):
        RationManager.set_ration_feeds(config)


@pytest.mark.parametrize("invalid_pct", [float("nan"), float("inf")])
def test_set_ration_feeds_rejects_non_finite_values(invalid_pct: float) -> None:
    """set_ration_feeds raises ValueError when a ration percentage is non-finite.

    Parametrized over nan and +inf (the two non-finite values that bypass the
    non-negative guard).  -inf is caught earlier by the non-negative check and
    therefore raises a different error message.

    Parameters
    ----------
    invalid_pct : float
        A non-finite percentage value (nan or +inf).
    """
    config: dict[str, object] = {
        "rations": [],
        "beef_lactating_pasture_ration": {"301": invalid_pct, "302": 50.0},
        "beef_dry_gestating_ration": {"302": 100.0},
        "beef_creep_feed_ration": {"303": 100.0},
        "beef_replacement_heifer_ration": {"304": 100.0},
    }

    with pytest.raises(ValueError, match="non-finite"):
        RationManager.set_ration_feeds(config)


@pytest.mark.parametrize(
    "ration_key",
    [
        "beef_lactating_pasture_ration",
        "beef_dry_gestating_ration",
        "beef_creep_feed_ration",
        "beef_replacement_heifer_ration",
    ],
)
def test_set_ration_feeds_rejects_bad_sum(ration_key: str) -> None:
    """set_ration_feeds raises ValueError when a beef ration does not sum to 100%.

    Parametrized over all four beef ration keys so that each ration is tested as the
    lone offender while the other three remain valid.
    """
    config: dict[str, object] = {
        "rations": [],
        "beef_lactating_pasture_ration": {"301": 100.0},
        "beef_dry_gestating_ration": {"302": 100.0},
        "beef_creep_feed_ration": {"303": 100.0},
        "beef_replacement_heifer_ration": {"304": 100.0},
    }
    config[ration_key] = {"301": 60.0, "302": 20.0}  # sums to 80, not 100

    with pytest.raises(ValueError, match="100"):
        RationManager.set_ration_feeds(config)


def test_set_ration_feeds_allows_empty_creep_feed() -> None:
    """An empty creep feed ration ({}) is valid and skips validation.

    Creep feed is optional (farms without it pass an empty dict). The validation loop
    must treat an empty ration as a no-op rather than raising a sum-to-100 error.
    """
    config: dict[str, object] = {
        "rations": [],
        "beef_lactating_pasture_ration": {"301": 100.0},
        "beef_dry_gestating_ration": {"302": 100.0},
        "beef_creep_feed_ration": {},
        "beef_replacement_heifer_ration": {"304": 100.0},
    }
    RationManager.set_ration_feeds(config)
    assert RationManager.beef_creep_feed_ration == {}


def test_set_ration_feeds_is_atomic() -> None:
    """If any beef ration is invalid, no class attribute is modified (atomic commit).

    Verifies all four ClassVars remain unchanged when set_ration_feeds raises;
    partial updates would leave RationManager in an inconsistent state.
    """
    RationManager.beef_lactating_pasture_ration = SENTINEL_LACTATING
    RationManager.beef_dry_gestating_ration = SENTINEL_DRY
    RationManager.beef_creep_feed_ration = SENTINEL_CREEP
    RationManager.beef_replacement_heifer_ration = SENTINEL_HEIFER

    bad_config: dict[str, object] = {
        "rations": [],
        "beef_lactating_pasture_ration": {"301": 60.0, "302": 20.0},  # sums to 80
        "beef_dry_gestating_ration": {"302": 100.0},
        "beef_creep_feed_ration": {"303": 100.0},
        "beef_replacement_heifer_ration": {"304": 100.0},
    }

    with pytest.raises(ValueError, match="non-negative|sum to 100"):
        RationManager.set_ration_feeds(bad_config)
    assert RationManager.beef_lactating_pasture_ration is SENTINEL_LACTATING
    assert RationManager.beef_dry_gestating_ration is SENTINEL_DRY
    assert RationManager.beef_creep_feed_ration is SENTINEL_CREEP
    assert RationManager.beef_replacement_heifer_ration is SENTINEL_HEIFER


# ── Task 6.2: Seasonal ration selection ───────────────────────────────────────


@pytest.fixture
def mock_animal_lactating_cow() -> MagicMock:
    """Mock Animal: BEEF_COW with calf at side (lactating).

    Returns
    -------
    MagicMock
        Animal mock with ``animal_type=BEEF_COW`` and a non-None ``calf_at_side``.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_COW
    animal.calf_at_side = MagicMock()
    return animal


@pytest.fixture
def mock_animal_dry_cow() -> MagicMock:
    """Mock Animal: BEEF_COW without calf at side (dry/gestating).

    Returns
    -------
    MagicMock
        Animal mock with ``animal_type=BEEF_COW`` and ``calf_at_side=None``.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_COW
    animal.calf_at_side = None
    return animal


@pytest.fixture
def mock_animal_replacement_heifer() -> MagicMock:
    """Mock Animal: BEEF_HEIFER_REPLACEMENT.

    Returns
    -------
    MagicMock
        Animal mock with ``animal_type=BEEF_HEIFER_REPLACEMENT`` and ``calf_at_side=None``.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    animal.calf_at_side = None
    return animal


@pytest.fixture
def mock_animal_bull() -> MagicMock:
    """Mock Animal: BEEF_BULL.

    Returns
    -------
    MagicMock
        Animal mock with ``animal_type=BEEF_BULL`` and ``calf_at_side=None``.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_BULL
    animal.calf_at_side = None
    return animal


@pytest.fixture
def mock_animal_calf() -> MagicMock:
    """Mock Animal: BEEF_CALF (nursing).

    Returns
    -------
    MagicMock
        Animal mock with ``animal_type=BEEF_CALF`` and ``calf_at_side=None``.
    """
    animal = MagicMock()
    animal.animal_type = AnimalType.BEEF_CALF
    animal.calf_at_side = None
    return animal


def test_get_beef_seasonal_ration_lactating_cow(mock_animal_lactating_cow: MagicMock) -> None:
    """A BEEF_COW with calf_at_side returns the beef_lactating_pasture_ration.

    Verifies the lactating branch: a nursing cow needs pasture-quality feed to
    support milk production, distinct from the dry/gestating ration.
    """
    RationManager.beef_lactating_pasture_ration = SENTINEL_LACTATING
    RationManager.beef_dry_gestating_ration = SENTINEL_DRY

    result = RationManager.get_beef_seasonal_ration(mock_animal_lactating_cow)

    assert result == SENTINEL_LACTATING


def test_get_beef_seasonal_ration_dry_cow(mock_animal_dry_cow: MagicMock) -> None:
    """A BEEF_COW without calf_at_side returns the beef_dry_gestating_ration.

    Verifies the dry/gestating branch: once weaned, the cow transitions to a
    maintenance ration rather than the lactation-support ration.
    """
    RationManager.beef_lactating_pasture_ration = SENTINEL_LACTATING
    RationManager.beef_dry_gestating_ration = SENTINEL_DRY

    result = RationManager.get_beef_seasonal_ration(mock_animal_dry_cow)

    assert result == SENTINEL_DRY


def test_get_beef_seasonal_ration_replacement_heifer(mock_animal_replacement_heifer: MagicMock) -> None:
    """A BEEF_HEIFER_REPLACEMENT returns the beef_replacement_heifer_ration.

    Replacement heifers are on a growing plane and need a distinct ration from
    mature cows; verifies the heifer branch routes to the correct ClassVar.
    """
    RationManager.beef_replacement_heifer_ration = SENTINEL_HEIFER

    result = RationManager.get_beef_seasonal_ration(mock_animal_replacement_heifer)

    assert result == SENTINEL_HEIFER


def test_get_beef_seasonal_ration_bull(mock_animal_bull: MagicMock) -> None:
    """A BEEF_BULL returns the beef_dry_gestating_ration (same as non-lactating cows).

    Bulls share the maintenance ration with dry cows; this verifies the shared
    branch rather than accidentally falling through to an unsupported-type error.
    """
    RationManager.beef_dry_gestating_ration = SENTINEL_DRY

    result = RationManager.get_beef_seasonal_ration(mock_animal_bull)

    assert result == SENTINEL_DRY


def test_get_beef_creep_feed_supplement_disabled(mock_animal_calf: MagicMock) -> None:
    """Returns {} when beef_creep_feeding_enabled is False even for a BEEF_CALF.

    Creep feeding is opt-in; confirms that setting the flag False skips the ration
    even when a valid creep feed dict is loaded on the class.
    """
    AnimalConfig.beef_creep_feeding_enabled = False
    RationManager.beef_creep_feed_ration = SENTINEL_CREEP

    result = RationManager.get_beef_creep_feed_supplement(mock_animal_calf)

    assert result == {}


def test_get_beef_creep_feed_supplement_enabled(mock_animal_calf: MagicMock) -> None:
    """Returns beef_creep_feed_ration when beef_creep_feeding_enabled is True for a BEEF_CALF.

    Verifies the enabled path returns a copy equal to the ClassVar dict so
    callers cannot mutate shared state.
    """
    AnimalConfig.beef_creep_feeding_enabled = True
    RationManager.beef_creep_feed_ration = SENTINEL_CREEP

    result = RationManager.get_beef_creep_feed_supplement(mock_animal_calf)

    assert result == SENTINEL_CREEP


def test_get_beef_creep_feed_supplement_non_calf_returns_empty(mock_animal_lactating_cow: MagicMock) -> None:
    """Returns {} for non-BEEF_CALF animals regardless of creep feeding config.

    Creep feed is only for nursing calves. Cows, bulls, and heifers must never
    receive creep feed supplement via this path.
    """
    AnimalConfig.beef_creep_feeding_enabled = True
    RationManager.beef_creep_feed_ration = SENTINEL_CREEP

    result = RationManager.get_beef_creep_feed_supplement(mock_animal_lactating_cow)

    assert result == {}


# ── Task 6.3: RationOptimizer beef constraint branches ────────────────────────


@pytest.fixture
def optimizer() -> RationOptimizer:
    """Provide a RationOptimizer with constraints initialized for NRC standard.

    Returns
    -------
    RationOptimizer
        A RationOptimizer built by ``_make_minimal_ration_optimizer`` with NRC constraints set.
    """
    return _make_minimal_ration_optimizer()


def test_select_constraints_beef_cow_calf_pair(optimizer: RationOptimizer) -> None:
    """_select_constraints returns beef_cow_constraints for BEEF_COW_CALF_PAIR.

    Verifies Task 6.3: the optimizer dispatches the cow-calf-specific constraint set
    rather than falling back to the default dairy constraints.
    """
    result = optimizer._select_constraints(AnimalCombination.BEEF_COW_CALF_PAIR)
    assert result is optimizer.beef_cow_constraints


def test_select_constraints_beef_replacement(optimizer: RationOptimizer) -> None:
    """_select_constraints returns beef_replacement_constraints for BEEF_REPLACEMENT.

    Verifies Task 6.3: growing replacement heifers use a separate constraint set
    calibrated for weight gain rather than mature maintenance.
    """
    result = optimizer._select_constraints(AnimalCombination.BEEF_REPLACEMENT)
    assert result is optimizer.beef_replacement_constraints


@pytest.mark.parametrize(
    "combination",
    [
        AnimalCombination.BEEF_COW_CALF_PAIR,
        AnimalCombination.BEEF_GESTATING,
        AnimalCombination.BEEF_BULL_BATTERY,
        AnimalCombination.BEEF_REPLACEMENT,
    ],
)
def test_handle_failed_constraints_agrees_with_select_constraints(
    optimizer: RationOptimizer,
    combination: AnimalCombination,
    mocker: MockerFixture,
) -> None:
    """handle_failed_constraints uses the same constraint set as _select_constraints for beef combinations.

    Verifies consistency between the two dispatch paths: a failed-constraint retry
    must evaluate against the same constraint object that was used for the initial solve.
    """
    expected_constraints = optimizer._select_constraints(combination)

    mock_find = mocker.patch.object(RationOptimizer, "find_failed_constraints", return_value=[])
    mock_solution = MagicMock()
    mock_ration_config = MagicMock()
    mock_available_feeds: list[object] = []
    mock_requirements = MagicMock()

    optimizer.handle_failed_constraints(
        num_attempts=1,
        solution=mock_solution,
        ration_config=mock_ration_config,
        animal_combination=combination,
        pen_id=1,
        pen_available_feeds=mock_available_feeds,
        average_nutrient_requirements=mock_requirements,
        initial_dry_matter_requirement=10.0,
        initial_protein_requirement=1.0,
        sim_day=1,
    )

    mock_find.assert_called_once()
    _, constraints_used, _ = mock_find.call_args.args
    assert constraints_used == list(expected_constraints)
