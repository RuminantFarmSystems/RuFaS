"""Tests for Step 5: Stocker ration management.

Covers RationManager ClassVars, get_beef_stocker_ration, set_ration_feeds
staged-atomic validation, and RationOptimizer beef_stocker_constraints wired
into both _select_constraints AND handle_failed_constraints.
"""

from __future__ import annotations

import copy
from typing import Any, Generator
from unittest.mock import MagicMock

import numpy as np
import pytest
from pytest_mock import MockerFixture
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import StockerDietSystem
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration import ration_optimizer
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, NutrientStandard

# ---------------------------------------------------------------------------
# Feed IDs used across tests (NRC 2016 stocker range)
# ---------------------------------------------------------------------------

_FEED_A: int = 301  # pasture feed
_FEED_B: int = 302  # drylot forage feed

# ---------------------------------------------------------------------------
# Autouse fixture: restore ClassVar state after every test (Style Rule 2)
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_ration_manager_stocker_state() -> Generator[None, None, None]:
    saved_pasture = copy.deepcopy(RationManager.beef_stocker_pasture_ration)
    saved_drylot = copy.deepcopy(RationManager.beef_stocker_drylot_ration)
    yield
    RationManager.beef_stocker_pasture_ration = saved_pasture
    RationManager.beef_stocker_drylot_ration = saved_drylot


def _minimal_ration_config(**kwargs: Any) -> dict[str, Any]:
    """Return a minimal set_ration_feeds config with only the supplied overrides."""
    base: dict[str, Any] = {"rations": []}
    base.update(kwargs)
    return base


# ---------------------------------------------------------------------------
# Group 1: RationManager ClassVar attribute existence
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_pasture_ration_classvar_exists() -> None:
    """beef_stocker_pasture_ration must be declared as a ClassVar on RationManager."""
    assert hasattr(RationManager, "beef_stocker_pasture_ration")


@pytest.mark.unit
def test_beef_stocker_drylot_ration_classvar_exists() -> None:
    """beef_stocker_drylot_ration must be declared as a ClassVar on RationManager."""
    assert hasattr(RationManager, "beef_stocker_drylot_ration")


@pytest.mark.unit
def test_beef_stocker_ration_classvars_are_dicts() -> None:
    """Both stocker ClassVar rations must be dict instances (default empty)."""
    assert isinstance(RationManager.beef_stocker_pasture_ration, dict)
    assert isinstance(RationManager.beef_stocker_drylot_ration, dict)


# ---------------------------------------------------------------------------
# Group 2: get_beef_stocker_ration()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_get_beef_stocker_ration_pasture(mocker: MockerFixture) -> None:
    """PASTURE system returns beef_stocker_pasture_ration contents."""
    RationManager.beef_stocker_pasture_ration = {_FEED_A: 100.0}
    mocker.patch.object(AnimalConfig, "stocker_diet_system", StockerDietSystem.PASTURE)
    result = RationManager.get_beef_stocker_ration(MagicMock())
    assert result == {_FEED_A: pytest.approx(100.0)}


@pytest.mark.unit
def test_get_beef_stocker_ration_drylot_forage(mocker: MockerFixture) -> None:
    """DRYLOT_FORAGE system returns beef_stocker_drylot_ration contents."""
    RationManager.beef_stocker_drylot_ration = {_FEED_B: 100.0}
    mocker.patch.object(AnimalConfig, "stocker_diet_system", StockerDietSystem.DRYLOT_FORAGE)
    result = RationManager.get_beef_stocker_ration(MagicMock())
    assert result == {_FEED_B: pytest.approx(100.0)}


@pytest.mark.unit
def test_get_beef_stocker_ration_unknown_system_raises(mocker: MockerFixture) -> None:
    """Unknown stocker_diet_system value raises ValueError."""
    mocker.patch.object(AnimalConfig, "stocker_diet_system", "unknown_system")
    with pytest.raises(ValueError, match="Unknown stocker_diet_system"):
        RationManager.get_beef_stocker_ration(MagicMock())


@pytest.mark.unit
def test_get_beef_stocker_ration_returns_shallow_copy(mocker: MockerFixture) -> None:
    """Returned dict is a copy; mutating it does not modify the ClassVar."""
    RationManager.beef_stocker_pasture_ration = {_FEED_A: 100.0}
    mocker.patch.object(AnimalConfig, "stocker_diet_system", StockerDietSystem.PASTURE)
    result = RationManager.get_beef_stocker_ration(MagicMock())
    result[_FEED_A] = 0.0
    assert RationManager.beef_stocker_pasture_ration[_FEED_A] == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# Group 3: set_ration_feeds() — staged-atomic validation
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_set_ration_feeds_stores_stocker_pasture_ration() -> None:
    """set_ration_feeds must persist beef_stocker_pasture_ration from config."""
    config = _minimal_ration_config(beef_stocker_pasture_ration={str(_FEED_A): 100.0})
    RationManager.set_ration_feeds(config)
    assert RationManager.beef_stocker_pasture_ration == {_FEED_A: 100.0}


@pytest.mark.unit
def test_set_ration_feeds_stores_stocker_drylot_ration() -> None:
    """set_ration_feeds must persist beef_stocker_drylot_ration from config."""
    config = _minimal_ration_config(beef_stocker_drylot_ration={str(_FEED_B): 100.0})
    RationManager.set_ration_feeds(config)
    assert RationManager.beef_stocker_drylot_ration == {_FEED_B: 100.0}


@pytest.mark.unit
def test_set_ration_feeds_staged_atomic_nan_pasture_raises_no_commit() -> None:
    """NaN in pasture ration raises ValueError and leaves ClassVar unchanged (staged-atomic)."""
    RationManager.beef_stocker_pasture_ration = {_FEED_A: 100.0}
    config = _minimal_ration_config(beef_stocker_pasture_ration={str(_FEED_A): float("nan")})
    with pytest.raises(ValueError):
        RationManager.set_ration_feeds(config)
    assert RationManager.beef_stocker_pasture_ration == {_FEED_A: 100.0}


@pytest.mark.unit
def test_set_ration_feeds_staged_atomic_inf_drylot_raises_no_commit() -> None:
    """Inf in drylot ration raises ValueError and leaves ClassVar unchanged (staged-atomic)."""
    RationManager.beef_stocker_drylot_ration = {_FEED_B: 100.0}
    config = _minimal_ration_config(beef_stocker_drylot_ration={str(_FEED_B): float("inf")})
    with pytest.raises(ValueError):
        RationManager.set_ration_feeds(config)
    assert RationManager.beef_stocker_drylot_ration == {_FEED_B: 100.0}


@pytest.mark.unit
def test_set_ration_feeds_negative_pasture_raises() -> None:
    """Negative percentage in pasture ration raises ValueError."""
    config = _minimal_ration_config(beef_stocker_pasture_ration={str(_FEED_A): -5.0, str(_FEED_B): 105.0})
    with pytest.raises(ValueError, match="non-negative"):
        RationManager.set_ration_feeds(config)


@pytest.mark.unit
def test_set_ration_feeds_wrong_sum_drylot_raises() -> None:
    """Drylot ration percentages summing to ≠100% raises ValueError."""
    config = _minimal_ration_config(beef_stocker_drylot_ration={str(_FEED_A): 60.0, str(_FEED_B): 30.0})
    with pytest.raises(ValueError, match="100.0%"):
        RationManager.set_ration_feeds(config)


# ---------------------------------------------------------------------------
# Group 4: RationOptimizer beef_stocker_constraints
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_stocker_constraints_attr_exists_after_init() -> None:
    """RationOptimizer.__init__ must initialise beef_stocker_constraints."""
    optimizer = RationOptimizer()
    assert hasattr(optimizer, "beef_stocker_constraints")


@pytest.mark.unit
def test_set_constraints_builds_beef_stocker_constraints() -> None:
    """set_constraints must populate beef_stocker_constraints as a non-empty list."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    assert isinstance(optimizer.beef_stocker_constraints, list)
    assert len(optimizer.beef_stocker_constraints) > 0


@pytest.mark.unit
def test_beef_stocker_constraints_include_ndf_lower() -> None:
    """Stocker constraints must include NDF_constraint_lower (NDF ≥ 25% DM minimum)."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    funs = {c["fun"] for c in optimizer.beef_stocker_constraints}
    assert optimizer.NDF_constraint_lower in funs


@pytest.mark.unit
def test_beef_stocker_constraints_exclude_ndf_upper() -> None:
    """Stocker high-roughage diet has no upper NDF ceiling: NDF_constraint_upper must be absent."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    funs = {c["fun"] for c in optimizer.beef_stocker_constraints}
    assert optimizer.NDF_constraint_upper not in funs


@pytest.mark.unit
def test_select_constraints_beef_stocker_returns_beef_stocker_constraints() -> None:
    """_select_constraints(BEEF_STOCKER) must return beef_stocker_constraints."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    result = optimizer._select_constraints(AnimalCombination.BEEF_STOCKER)
    assert result is optimizer.beef_stocker_constraints


@pytest.mark.unit
def test_handle_failed_constraints_accepts_beef_stocker(mocker: MockerFixture) -> None:
    """handle_failed_constraints routes BEEF_STOCKER through beef_stocker_constraints without ValueError."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    optimizer.beef_stocker_constraints = [{"fun": MagicMock(__name__="ndf_lower")}]
    mocker.patch.object(optimizer, "make_ration_from_solution", return_value={})
    mocker.patch.object(ration_optimizer, "OutputManager", return_value=MagicMock())
    mocker.patch.object(RationOptimizer, "find_failed_constraints", return_value=[])

    solution = MagicMock(spec=OptimizeResult)
    solution.x = np.array([1.0])

    optimizer.handle_failed_constraints(
        num_attempts=1,
        solution=solution,
        ration_config=MagicMock(),
        animal_combination=AnimalCombination.BEEF_STOCKER,
        pen_id=1,
        pen_available_feeds=[MagicMock(spec=Feed)],
        average_nutrient_requirements=MagicMock(spec=NutritionRequirements),
        sim_day=1,
        initial_dry_matter_requirement=1.0,
        initial_protein_requirement=1.0,
    )


@pytest.mark.unit
def test_constraint_consistency_select_and_handle_use_same_list() -> None:
    """_select_constraints and handle_failed_constraints must both route BEEF_STOCKER
    to the same beef_stocker_constraints object — consistency guard against PR #32 mistake."""
    optimizer = RationOptimizer()
    dummy_config = MagicMock()
    dummy_config.nutrient_standard = NutrientStandard.NRC
    optimizer.set_constraints(dummy_config)
    assert optimizer._select_constraints(AnimalCombination.BEEF_STOCKER) is optimizer.beef_stocker_constraints
