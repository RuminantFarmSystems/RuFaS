"""Tests for the stocker limit-feeding diet system.

Verifies:
- LIMIT_FEED as a third StockerDietSystem member
- AnimalConfig.stocker_limit_feed_pct parsing and validation
- The DMI cap applied in BeefStockerRequirementsCalculator
- The limit-feed ration lookup in RationManager
- Constraint routing consistency between _select_constraints and
  handle_failed_constraints
- days_on_restricted_intake / is_on_restricted_intake lifecycle tracking
- Regression: PASTURE and DRYLOT_FORAGE behaviour is unchanged
"""

from __future__ import annotations

import copy
from typing import Any, Generator
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex, StockerDietSystem
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import (
    BeefStockerRequirementsCalculator,
    StockerRequirementsInputs,
)
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_validator import DataValidator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_LIMIT_FEED_PCT: float = 85.0
_BENCHMARK_BODY_WEIGHT: float = 280.0  # kg
_BENCHMARK_NE_CONCENTRATION: float = 1.0  # Mcal/kg DM
_BENCHMARK_MATURE_WEIGHT: float = 520.0  # kg

_LIMIT_FEED_RATION: dict[int, float] = {301: 60.0, 302: 40.0}


# ---------------------------------------------------------------------------
# Fixtures — restore mutated class state after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_stocker_config() -> Generator[None, None, None]:
    """Save and restore stocker ClassVars: scalars by assignment, dicts by deepcopy."""
    saved_diet_system = AnimalConfig.stocker_diet_system
    saved_limit_feed_pct = AnimalConfig.stocker_limit_feed_pct
    saved_limit_feed_ration = copy.deepcopy(RationManager.beef_stocker_limit_feed_ration)
    saved_pasture_ration = copy.deepcopy(RationManager.beef_stocker_pasture_ration)
    saved_drylot_ration = copy.deepcopy(RationManager.beef_stocker_drylot_ration)
    yield
    AnimalConfig.stocker_diet_system = saved_diet_system
    AnimalConfig.stocker_limit_feed_pct = saved_limit_feed_pct
    RationManager.beef_stocker_limit_feed_ration = saved_limit_feed_ration
    RationManager.beef_stocker_pasture_ration = saved_pasture_ration
    RationManager.beef_stocker_drylot_ration = saved_drylot_ration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stocker_inputs(**overrides: object) -> StockerRequirementsInputs:
    """Build StockerRequirementsInputs with benchmark values and optional overrides."""
    defaults: dict[str, object] = {
        "animal_type": AnimalType.BEEF_STOCKER_STEER,
        "sex": Sex.STEER,
        "body_weight": _BENCHMARK_BODY_WEIGHT,
        "mature_body_weight": _BENCHMARK_MATURE_WEIGHT,
        "breed": "Angus",
        "target_adg": 0.80,
        "temperature_c": 20.0,
        "ne_diet_concentration": _BENCHMARK_NE_CONCENTRATION,
        "mud_condition": AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
    }
    defaults.update(overrides)
    return StockerRequirementsInputs(**defaults)  # type: ignore[arg-type]


def _make_stocker_animal() -> Animal:
    """Construct a minimal BEEF_STOCKER_STEER partway through the stocker phase."""
    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    animal.sex = Sex.STEER
    animal.breed = Breed.AN
    animal.body_weight = _BENCHMARK_BODY_WEIGHT
    animal.mature_body_weight = _BENCHMARK_MATURE_WEIGHT
    animal.days_born = 300
    animal.days_in_stocker = 10
    animal.stocker_entry_weight = 240.0
    animal.stocker_cumulative_dmi = 0.0
    animal.days_on_restricted_intake = 0
    animal.is_on_restricted_intake = False
    animal.events = AnimalEvents()
    animal.growth = MagicMock()
    animal.nutrition_supply = NutritionSupply.make_empty_nutrition_supply()
    animal.previous_nutrition_supply = None
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal._future_cull_date = None
    animal._future_death_date = None
    return animal


def _mock_time(simulation_day: int = 300) -> MagicMock:
    """Return a minimal time mock with simulation_day set."""
    time: MagicMock = MagicMock()
    time.simulation_day = simulation_day
    return time


def _make_stocker_config(**overrides: object) -> dict[str, Any]:
    """Return a stocker config dict with optional overrides."""
    config: dict[str, Any] = {}
    config.update(overrides)
    return config


# ---------------------------------------------------------------------------
# B-1.1 — LIMIT_FEED enum member
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_limit_feed_member_exists() -> None:
    """StockerDietSystem.LIMIT_FEED must exist."""
    assert hasattr(StockerDietSystem, "LIMIT_FEED")


@pytest.mark.unit
def test_limit_feed_value() -> None:
    """LIMIT_FEED value must be 'limit_feed'."""
    assert StockerDietSystem.LIMIT_FEED.value == "limit_feed"


@pytest.mark.unit
def test_stocker_diet_system_now_has_three_members() -> None:
    """StockerDietSystem must have exactly three members."""
    assert len(StockerDietSystem) == 3


@pytest.mark.unit
def test_stocker_diet_system_remains_plain_enum() -> None:
    """StockerDietSystem must stay a plain Enum, never a str,Enum."""
    assert not issubclass(StockerDietSystem, str)


@pytest.mark.unit
def test_limit_feed_roundtrip() -> None:
    """StockerDietSystem('limit_feed') round-trips to LIMIT_FEED."""
    assert StockerDietSystem("limit_feed") is StockerDietSystem.LIMIT_FEED


@pytest.mark.unit
def test_validator_accepts_limit_feed_diet_system() -> None:
    """The stocker config validator must accept the new diet system value."""
    DataValidator.validate_beef_stocker_config(_make_stocker_config(stocker_diet_system="limit_feed"))


# ---------------------------------------------------------------------------
# B-1.2 — stocker_limit_feed_pct config and validation
# ---------------------------------------------------------------------------


@pytest.mark.regression
def test_limit_feed_pct_defaults_to_85() -> None:
    """The default limit-feed percentage must be 85.0."""
    assert AnimalConfig.stocker_limit_feed_pct == pytest.approx(_DEFAULT_LIMIT_FEED_PCT)


@pytest.mark.unit
def test_limit_feed_pct_parsed_from_config() -> None:
    """A configured limit_feed_pct must land on the ClassVar."""
    AnimalConfig._initialize_beef_stocker_config(_make_stocker_config(limit_feed_pct=70.0))
    assert AnimalConfig.stocker_limit_feed_pct == pytest.approx(70.0)


@pytest.mark.unit
def test_limit_feed_pct_absent_keeps_default() -> None:
    """An absent limit_feed_pct must leave the default in place."""
    AnimalConfig.stocker_limit_feed_pct = _DEFAULT_LIMIT_FEED_PCT
    AnimalConfig._initialize_beef_stocker_config(_make_stocker_config())
    assert AnimalConfig.stocker_limit_feed_pct == pytest.approx(_DEFAULT_LIMIT_FEED_PCT)


@pytest.mark.unit
@pytest.mark.parametrize("bad_pct", [0.0, -1.0, 100.1, 150.0, float("nan"), float("inf")])
def test_invalid_limit_feed_pct_raises(bad_pct: float) -> None:
    """Zero, negative, above-100, NaN and inf percentages must all raise ValueError."""
    with pytest.raises(ValueError, match="limit_feed_pct"):
        DataValidator.validate_beef_stocker_config(_make_stocker_config(limit_feed_pct=bad_pct))


@pytest.mark.unit
@pytest.mark.parametrize("good_pct", [0.1, 50.0, 85.0, 100.0])
def test_valid_limit_feed_pct_accepted(good_pct: float) -> None:
    """Percentages in (0, 100] must validate."""
    DataValidator.validate_beef_stocker_config(_make_stocker_config(limit_feed_pct=good_pct))


# ---------------------------------------------------------------------------
# B-1.3 / B-1.6 — the DMI cap
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_limit_feed_reduces_dmi_by_configured_fraction() -> None:
    """LIMIT_FEED must scale ad libitum DMI by exactly limit_feed_pct / 100."""
    ad_libitum = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.PASTURE)
    ).dry_matter
    limited = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(
            diet_system=StockerDietSystem.LIMIT_FEED,
            limit_feed_pct=_DEFAULT_LIMIT_FEED_PCT,
        )
    ).dry_matter
    assert limited == pytest.approx(ad_libitum * 0.85)


@pytest.mark.unit
@pytest.mark.parametrize("pct", [50.0, 70.0, 85.0, 100.0])
def test_limit_feed_cap_scales_with_percentage(pct: float) -> None:
    """The cap must track the configured percentage across its valid range."""
    ad_libitum = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.PASTURE)
    ).dry_matter
    limited = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.LIMIT_FEED, limit_feed_pct=pct)
    ).dry_matter
    assert limited == pytest.approx(ad_libitum * (pct / 100.0))


@pytest.mark.unit
def test_limit_feed_at_100_pct_equals_ad_libitum() -> None:
    """A 100% cap must be a no-op."""
    ad_libitum = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.PASTURE)
    ).dry_matter
    limited = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.LIMIT_FEED, limit_feed_pct=100.0)
    ).dry_matter
    assert limited == pytest.approx(ad_libitum)


@pytest.mark.regression
@pytest.mark.parametrize(
    "diet_system",
    [StockerDietSystem.PASTURE, StockerDietSystem.DRYLOT_FORAGE],
)
def test_non_limit_feed_diets_are_unchanged(diet_system: StockerDietSystem) -> None:
    """PASTURE and DRYLOT_FORAGE must produce unreduced DMI."""
    default_dmi = BeefStockerRequirementsCalculator._calculate_dmi(_BENCHMARK_BODY_WEIGHT, _BENCHMARK_NE_CONCENTRATION)
    result = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=diet_system, limit_feed_pct=_DEFAULT_LIMIT_FEED_PCT)
    )
    assert result.dry_matter == pytest.approx(default_dmi)


@pytest.mark.regression
def test_inputs_default_to_pasture() -> None:
    """The inputs dataclass must default to PASTURE so existing call sites are unaffected."""
    assert _make_stocker_inputs().diet_system is StockerDietSystem.PASTURE


@pytest.mark.unit
def test_limit_feed_does_not_change_energy_or_protein() -> None:
    """The cap touches DMI only; energy and protein requirements are unchanged."""
    ad_libitum = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.PASTURE)
    )
    limited = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.LIMIT_FEED)
    )
    assert limited.maintenance_energy == pytest.approx(ad_libitum.maintenance_energy)
    assert limited.growth_energy == pytest.approx(ad_libitum.growth_energy)
    assert limited.metabolizable_protein == pytest.approx(ad_libitum.metabolizable_protein)


# ---------------------------------------------------------------------------
# B-1.4 — the limit-feed ration
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_limit_feed_ration_classvar_exists() -> None:
    """RationManager must expose beef_stocker_limit_feed_ration."""
    assert hasattr(RationManager, "beef_stocker_limit_feed_ration")


@pytest.mark.unit
def test_get_ration_returns_limit_feed_ration_under_limit_feed() -> None:
    """Under LIMIT_FEED the getter must return the limit-feed ration."""
    RationManager.beef_stocker_limit_feed_ration = dict(_LIMIT_FEED_RATION)
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    assert RationManager.get_beef_stocker_ration(_make_stocker_animal()) == _LIMIT_FEED_RATION


@pytest.mark.unit
def test_get_ration_returns_a_copy_not_the_classvar() -> None:
    """The getter must return a copy so callers cannot mutate class state."""
    RationManager.beef_stocker_limit_feed_ration = dict(_LIMIT_FEED_RATION)
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    returned = RationManager.get_beef_stocker_ration(_make_stocker_animal())
    assert returned is not RationManager.beef_stocker_limit_feed_ration


@pytest.mark.regression
def test_get_ration_pasture_unchanged() -> None:
    """PASTURE must still return the pasture ration."""
    RationManager.beef_stocker_pasture_ration = {301: 100.0}
    AnimalConfig.stocker_diet_system = StockerDietSystem.PASTURE
    assert RationManager.get_beef_stocker_ration(_make_stocker_animal()) == {301: 100.0}


@pytest.mark.regression
def test_get_ration_drylot_unchanged() -> None:
    """DRYLOT_FORAGE must still return the drylot ration."""
    RationManager.beef_stocker_drylot_ration = {302: 100.0}
    AnimalConfig.stocker_diet_system = StockerDietSystem.DRYLOT_FORAGE
    assert RationManager.get_beef_stocker_ration(_make_stocker_animal()) == {302: 100.0}


# ---------------------------------------------------------------------------
# B-1.5 — constraint routing consistency
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_select_constraints_routes_stocker_without_error() -> None:
    """BEEF_STOCKER must resolve to a constraint set rather than raising."""
    optimizer = RationOptimizer()
    assert optimizer._select_constraints(AnimalCombination.BEEF_STOCKER) is not None


@pytest.mark.unit
def test_handle_failed_constraints_uses_the_same_constraint_set(mocker: MockerFixture) -> None:
    """handle_failed_constraints must source its constraints from _select_constraints.

    The two cannot diverge while this delegation holds. PR #32 review found a
    parallel list; this guards against one being reintroduced.
    """
    optimizer = RationOptimizer()
    spy = mocker.patch.object(optimizer, "_select_constraints", return_value=[])
    mocker.patch.object(RationOptimizer, "find_failed_constraints", return_value=[])
    mocker.patch.object(optimizer, "make_ration_from_solution", return_value={})

    optimizer.handle_failed_constraints(
        num_attempts=1,
        solution=MagicMock(),
        ration_config=MagicMock(),
        animal_combination=AnimalCombination.BEEF_STOCKER,
        pen_id=1,
        pen_available_feeds={},
        average_nutrient_requirements=MagicMock(),
        initial_dry_matter_requirement=1.0,
        initial_protein_requirement=1.0,
        sim_day=1,
    )

    spy.assert_called_once_with(AnimalCombination.BEEF_STOCKER)


# ---------------------------------------------------------------------------
# B-1.7 — restricted-intake lifecycle tracking
# ---------------------------------------------------------------------------


@pytest.mark.component
def test_restricted_intake_attributes_initialised_to_zero() -> None:
    """A freshly initialised stocker must start unrestricted."""
    animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    animal._initialize_stocker_animal({"body_weight": 240.0, "mature_body_weight": 520.0})
    assert animal.days_on_restricted_intake == 0
    assert animal.is_on_restricted_intake is False


@pytest.mark.component
def test_restricted_days_increment_under_limit_feed() -> None:
    """Each simulated day under LIMIT_FEED must increment the restricted-day count."""
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    animal = _make_stocker_animal()
    animal._stocker_daily_routines(_mock_time())
    assert animal.days_on_restricted_intake == 1
    assert animal.is_on_restricted_intake is True


@pytest.mark.component
def test_restricted_days_accumulate_over_several_days() -> None:
    """The count must accumulate across consecutive restricted days."""
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    animal = _make_stocker_animal()
    for _ in range(5):
        animal._stocker_daily_routines(_mock_time())
    assert animal.days_on_restricted_intake == 5


@pytest.mark.regression
@pytest.mark.parametrize(
    "diet_system",
    [StockerDietSystem.PASTURE, StockerDietSystem.DRYLOT_FORAGE],
)
def test_restricted_days_do_not_increment_on_unrestricted_diets(
    diet_system: StockerDietSystem,
) -> None:
    """PASTURE and DRYLOT_FORAGE must leave the restricted-intake counters untouched."""
    AnimalConfig.stocker_diet_system = diet_system
    animal = _make_stocker_animal()
    animal._stocker_daily_routines(_mock_time())
    assert animal.days_on_restricted_intake == 0
    assert animal.is_on_restricted_intake is False


@pytest.mark.unit
@pytest.mark.regression
def test_limit_feed_at_one_hundred_percent_is_not_restriction() -> None:
    """LIMIT_FEED at 100% caps at ad libitum, so no restriction occurred.

    is_on_restricted_intake must reflect an actual intake cap, not merely
    the diet-system enum. Without this guard a 100% limit-feed pen would
    accumulate restricted days and could later trigger compensatory gain
    for a restriction that never reduced intake.
    """
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    AnimalConfig.stocker_limit_feed_pct = 100.0
    animal = _make_stocker_animal()
    animal._stocker_daily_routines(_mock_time())
    assert animal.is_on_restricted_intake is False
    assert animal.days_on_restricted_intake == 0


@pytest.mark.unit
def test_limit_feed_below_one_hundred_percent_is_still_restriction() -> None:
    """A genuine cap below 100% must still count as restriction."""
    AnimalConfig.stocker_diet_system = StockerDietSystem.LIMIT_FEED
    AnimalConfig.stocker_limit_feed_pct = 99.9
    animal = _make_stocker_animal()
    animal._stocker_daily_routines(_mock_time())
    assert animal.is_on_restricted_intake is True
    assert animal.days_on_restricted_intake == 1


# ---------------------------------------------------------------------------
# Calculator-level validation of limit_feed_pct and diet_system
# ---------------------------------------------------------------------------


@pytest.mark.component
@pytest.mark.parametrize("bad_pct", [0.0, -5.0, 100.1, float("nan"), float("inf")])
def test_calculator_rejects_invalid_limit_feed_pct(bad_pct: float) -> None:
    """Calculator-level validation must mirror the config-level bound.

    limit_feed_pct is not checked by _validate_inputs today, so a caller
    that builds StockerRequirementsInputs directly -- every test in this
    suite does exactly that -- bypasses the (0, 100] and finite guard that
    AnimalConfig enforces at parse time.
    """
    with pytest.raises(ValueError, match="limit_feed_pct"):
        BeefStockerRequirementsCalculator.calculate_requirements(
            _make_stocker_inputs(diet_system=StockerDietSystem.LIMIT_FEED, limit_feed_pct=bad_pct)
        )


@pytest.mark.component
def test_calculator_accepts_limit_feed_pct_at_the_boundary() -> None:
    """100.0 is the inclusive upper bound and must be accepted."""
    result = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_stocker_inputs(diet_system=StockerDietSystem.LIMIT_FEED, limit_feed_pct=100.0)
    )
    assert result.dry_matter > 0.0


@pytest.mark.component
def test_calculator_rejects_a_diet_system_that_is_not_a_member() -> None:
    """diet_system must be a real StockerDietSystem member, not an arbitrary value."""
    with pytest.raises(ValueError, match="diet_system"):
        BeefStockerRequirementsCalculator.calculate_requirements(_make_stocker_inputs(diet_system="limit_feed"))
