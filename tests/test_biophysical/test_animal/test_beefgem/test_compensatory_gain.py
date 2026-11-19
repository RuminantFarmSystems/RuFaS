"""Phase D-2 checkpoint — compensatory gain after nutritional restriction.

Covers the trigger threshold, the multiplier ceiling, decay toward 1.0, the
opt-in gate, and application to target ADG in both beef calculators.
"""

from __future__ import annotations

from typing import Any, Iterator

import pytest

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import (
    BeefStockerRequirementsCalculator,
    StockerRequirementsInputs,
)

THRESHOLD = AnimalModuleConstants.CG_RESTRICTION_THRESHOLD_DAYS
MAX_MULTIPLIER = AnimalModuleConstants.CG_MAX_ADG_MULTIPLIER
DECAY = AnimalModuleConstants.CG_DECAY_RATE_PER_DAY


@pytest.fixture(autouse=True)
def restore_cg_config() -> Iterator[None]:
    """Keep the opt-in gate from leaking between tests."""
    saved = AnimalConfig.enable_compensatory_gain
    yield
    AnimalConfig.enable_compensatory_gain = saved


def _stocker_inputs(**overrides: Any) -> StockerRequirementsInputs:
    """Build a valid stocker input dataclass, overriding named fields."""
    defaults: dict[str, Any] = {
        "animal_type": AnimalType.BEEF_STOCKER_STEER,
        "sex": Sex.MALE,
        "body_weight": 300.0,
        "mature_body_weight": 520.0,
        "breed": "Angus",
        "target_adg": 0.8,
        "temperature_c": 20.0,
        "ne_diet_concentration": 1.2,
    }
    defaults.update(overrides)
    return StockerRequirementsInputs(**defaults)


def _feedlot_kwargs(**overrides: Any) -> dict[str, Any]:
    """Build a valid feedlot calculate_requirements kwargs dict."""
    defaults: dict[str, Any] = {
        "body_weight": 400.0,
        "mature_body_weight": 620.0,
        "animal_type": AnimalType.FEEDLOT_STEER,
        "breed": "Angus",
        "sex": Sex.MALE,
        "days_on_feed": 100,
        "target_adg": 1.5,
        "implant_adg_factor": 1.0,
        "housing": "Open_Lot",
        "mud_condition": "none",
        "temperature_c": 20.0,
        "ne_diet_concentration": 1.4,
        "process_based_phosphorus_requirement": 0.0,
    }
    defaults.update(overrides)
    return defaults


# ───────────────────────────── constants ────────────────────────────────


@pytest.mark.unit
def test_compensatory_gain_constants_have_the_settled_values() -> None:
    """The three CG constants are pinned."""
    assert THRESHOLD == 21
    assert MAX_MULTIPLIER == pytest.approx(1.25)
    assert DECAY == pytest.approx(0.02)


@pytest.mark.unit
def test_per_day_coefficient_is_exposed_as_a_constant() -> None:
    """The 0.005 per-day rate is a named constant, not an inline number."""
    assert AnimalModuleConstants.CG_ADG_MULTIPLIER_PER_RESTRICTED_DAY == pytest.approx(0.005)


# ──────────────────────── the factor calculation ─────────────────────────


@pytest.mark.unit
def test_exactly_threshold_days_gives_no_factor() -> None:
    """21 days is not 'more than 21' — the boundary yields 1.0, not a factor."""
    assert Animal.calculate_compensatory_gain_factor(THRESHOLD) == pytest.approx(1.0)


@pytest.mark.unit
def test_below_threshold_gives_no_factor() -> None:
    """A short restriction does not trigger compensatory gain."""
    assert Animal.calculate_compensatory_gain_factor(THRESHOLD - 1) == pytest.approx(1.0)


@pytest.mark.unit
def test_zero_days_restricted_gives_no_factor() -> None:
    """An animal that was never restricted gains nothing."""
    assert Animal.calculate_compensatory_gain_factor(0) == pytest.approx(1.0)


@pytest.mark.unit
def test_one_day_past_threshold_is_just_above_one() -> None:
    """The response starts continuously at the threshold, not with a jump."""
    assert Animal.calculate_compensatory_gain_factor(THRESHOLD + 1) == pytest.approx(1.005)


@pytest.mark.unit
def test_thirty_days_restricted_gives_factor_above_one() -> None:
    """30 days restricted yields 1.0 + 9 * 0.005 = 1.045."""
    factor = Animal.calculate_compensatory_gain_factor(30)
    assert factor > 1.0
    assert factor <= MAX_MULTIPLIER
    assert factor == pytest.approx(1.045)


@pytest.mark.unit
@pytest.mark.parametrize("days", [71, 100, 365, 10_000])
def test_ceiling_holds_regardless_of_restriction_length(days: int) -> None:
    """The multiplier is capped no matter how long the restriction ran."""
    assert Animal.calculate_compensatory_gain_factor(days) == pytest.approx(MAX_MULTIPLIER)


@pytest.mark.unit
def test_ceiling_is_reached_exactly_at_seventy_one_days() -> None:
    """1.0 + (71 - 21) * 0.005 = 1.25, the first day the cap binds."""
    assert Animal.calculate_compensatory_gain_factor(71) == pytest.approx(MAX_MULTIPLIER)


@pytest.mark.unit
def test_factor_is_monotone_non_decreasing_in_restricted_days() -> None:
    """More restriction never yields less compensatory gain."""
    values = [Animal.calculate_compensatory_gain_factor(d) for d in range(0, 120)]
    assert all(later >= earlier for earlier, later in zip(values, values[1:]))


@pytest.mark.unit
def test_negative_days_raises_value_error() -> None:
    """A negative counter is a programming error, not a zero factor."""
    with pytest.raises(ValueError, match="days_on_restricted_intake"):
        Animal.calculate_compensatory_gain_factor(-1)


# ────────────────────────────── the decay ────────────────────────────────


@pytest.mark.unit
def test_decay_moves_the_factor_toward_one() -> None:
    """One day of decay removes exactly CG_DECAY_RATE_PER_DAY."""
    assert Animal.decay_compensatory_gain_factor(1.25) == pytest.approx(1.23)


@pytest.mark.unit
def test_decay_never_falls_below_one() -> None:
    """The factor floors at 1.0 rather than becoming a penalty."""
    assert Animal.decay_compensatory_gain_factor(1.005) == pytest.approx(1.0)


@pytest.mark.unit
def test_decay_of_an_unmodified_factor_is_a_no_op() -> None:
    """An animal with no compensatory gain stays at 1.0."""
    assert Animal.decay_compensatory_gain_factor(1.0) == pytest.approx(1.0)


@pytest.mark.unit
def test_repeated_decay_converges_to_one_and_stays() -> None:
    """Decaying for longer than the advantage lasts leaves it at exactly 1.0."""
    factor = MAX_MULTIPLIER
    for _ in range(100):
        factor = Animal.decay_compensatory_gain_factor(factor)
    assert factor == pytest.approx(1.0)


@pytest.mark.unit
def test_decay_is_monotone_non_increasing() -> None:
    """Each step moves toward 1.0, never away from it."""
    factor = MAX_MULTIPLIER
    for _ in range(40):
        decayed = Animal.decay_compensatory_gain_factor(factor)
        assert decayed <= factor
        assert decayed >= 1.0
        factor = decayed


@pytest.mark.unit
def test_full_advantage_decays_within_expected_days() -> None:
    """A 0.25 advantage at 0.02/day is gone after 13 days."""
    factor = MAX_MULTIPLIER
    days = 0
    while factor > 1.0:
        factor = Animal.decay_compensatory_gain_factor(factor)
        days += 1
    assert days == 13


# ────────────────────────────── the opt-in gate ──────────────────────────


@pytest.mark.unit
def test_gate_defaults_to_disabled() -> None:
    """Compensatory gain is opt-in — nothing changes by default."""
    assert AnimalConfig.enable_compensatory_gain is False


@pytest.mark.component
@pytest.mark.regression
@pytest.mark.parametrize("days", [0, 21, 30, 100])
def test_disabled_gate_leaves_the_factor_at_one(days: int) -> None:
    """With the gate off the factor is 1.0 regardless of restriction history."""
    AnimalConfig.enable_compensatory_gain = False
    assert Animal.resolve_compensatory_gain_factor(days) == pytest.approx(1.0)


@pytest.mark.component
def test_enabled_gate_applies_the_factor() -> None:
    """With the gate on a long restriction produces an uplift."""
    AnimalConfig.enable_compensatory_gain = True
    assert Animal.resolve_compensatory_gain_factor(30) == pytest.approx(1.045)


# ─────────────────────── application in the calculators ──────────────────


@pytest.mark.unit
def test_stocker_inputs_default_the_factor_to_one() -> None:
    """An unset factor means no compensatory gain."""
    assert _stocker_inputs().compensatory_gain_factor == pytest.approx(1.0)


@pytest.mark.component
def test_stocker_neg_is_higher_with_a_factor_above_one() -> None:
    """Compensatory gain raises the growth energy requirement."""
    plain = BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs())
    boosted = BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(compensatory_gain_factor=1.2))
    assert boosted.growth_energy > plain.growth_energy


@pytest.mark.component
def test_feedlot_neg_is_higher_with_a_factor_above_one() -> None:
    """The feedlot calculator responds the same way."""
    plain = BeefNRCRequirementsCalculator.calculate_requirements(**_feedlot_kwargs())
    boosted = BeefNRCRequirementsCalculator.calculate_requirements(**_feedlot_kwargs(compensatory_gain_factor=1.2))
    assert boosted.growth_energy > plain.growth_energy


@pytest.mark.component
def test_factor_of_one_changes_nothing_in_either_calculator() -> None:
    """Backward compatibility: the default factor is a no-op."""
    stocker_default = BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs())
    stocker_explicit = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(compensatory_gain_factor=1.0)
    )
    assert stocker_default.growth_energy == pytest.approx(stocker_explicit.growth_energy)

    feedlot_default = BeefNRCRequirementsCalculator.calculate_requirements(**_feedlot_kwargs())
    feedlot_explicit = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(compensatory_gain_factor=1.0)
    )
    assert feedlot_default.growth_energy == pytest.approx(feedlot_explicit.growth_energy)


@pytest.mark.component
def test_calculator_caps_an_out_of_range_factor() -> None:
    """A factor above the ceiling is clamped, not trusted."""
    capped = BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(compensatory_gain_factor=5.0))
    at_ceiling = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(compensatory_gain_factor=MAX_MULTIPLIER)
    )
    assert capped.growth_energy == pytest.approx(at_ceiling.growth_energy)


@pytest.mark.component
def test_feedlot_caps_an_out_of_range_factor() -> None:
    """The feedlot ceiling binds alongside the implant factor."""
    capped = BeefNRCRequirementsCalculator.calculate_requirements(**_feedlot_kwargs(compensatory_gain_factor=5.0))
    at_ceiling = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(compensatory_gain_factor=MAX_MULTIPLIER)
    )
    assert capped.growth_energy == pytest.approx(at_ceiling.growth_energy)


@pytest.mark.component
def test_stocker_rejects_a_non_finite_factor() -> None:
    """NaN would otherwise propagate silently into growth energy."""
    with pytest.raises(ValueError, match="compensatory_gain_factor"):
        BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(compensatory_gain_factor=float("nan")))


@pytest.mark.component
def test_stocker_rejects_a_factor_below_one() -> None:
    """Compensatory gain is an uplift; a penalty is a caller error."""
    with pytest.raises(ValueError, match="compensatory_gain_factor"):
        BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(compensatory_gain_factor=0.8))


# ────────────────────────── animal instance state ────────────────────────


@pytest.mark.unit
def test_stocker_animal_initialises_the_factor_to_one() -> None:
    """Every stocker animal starts with no compensatory gain."""
    animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_STOCKER_STEER
    Animal._initialize_stocker_animal(animal, {"body_weight": 250.0, "mature_body_weight": 520.0})
    assert animal.compensatory_gain_factor == pytest.approx(1.0)
    assert animal.days_on_restricted_intake == 0


@pytest.mark.unit
def test_feedlot_animal_initialises_the_factor_to_one() -> None:
    """A feedlot animal created directly carries no compensatory gain."""
    animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.FEEDLOT_STEER
    animal.days_born = 0
    animal.step_up_phase = ""
    animal.events = AnimalEvents()
    Animal._initialize_feedlot_animal(animal, {"body_weight": 320.0, "mature_body_weight": 620.0})
    assert animal.compensatory_gain_factor == pytest.approx(1.0)


@pytest.mark.regression
def test_dairy_calculators_have_no_compensatory_gain() -> None:
    """The feature lives on the beef path only."""
    from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator

    assert not hasattr(NASEMRequirementsCalculator, "calculate_compensatory_gain_factor")


# ──────────────────── the ceiling caps uplift, not total ADG ─────────────


@pytest.mark.unit
@pytest.mark.regression
def test_ceiling_does_not_clip_the_implant_factor() -> None:
    """With no compensatory gain, an implant factor above the cap is untouched.

    The ceiling bounds the compensatory uplift, not total ADG. Capping the
    product would change feedlot growth for anyone running an implant factor
    above 1.25 even with the feature switched off.
    """
    base = 1.5 * 1.3
    assert BeefNRCRequirementsCalculator._apply_compensatory_gain(base, 1.0) == pytest.approx(1.950)


@pytest.mark.unit
def test_ceiling_still_binds_on_genuine_uplift() -> None:
    """A factor at the cap yields exactly base x 1.25."""
    assert BeefNRCRequirementsCalculator._apply_compensatory_gain(1.5, 1.25) == pytest.approx(1.875)


@pytest.mark.unit
def test_ceiling_clamps_a_factor_beyond_the_cap() -> None:
    """An out-of-range factor is clamped to the cap, not trusted."""
    assert BeefNRCRequirementsCalculator._apply_compensatory_gain(1.5, 5.0) == pytest.approx(1.875)


@pytest.mark.unit
@pytest.mark.regression
def test_growth_and_calculator_paths_agree_under_compensatory_gain() -> None:
    """Body-weight growth and the nutrition calculator must use one ADG.

    Two expressions that have to agree is the defect; both paths call the same
    helper. At implant 1.3 with a factor at the cap they previously diverged by
    0.5625 kg/d, so the animal gained weight the calculator never budgeted for.
    """
    target, implant, factor = 1.5, 1.3, 1.25
    base = target * implant
    shared = BeefNRCRequirementsCalculator._apply_compensatory_gain(base, factor)

    growth_path = Animal.effective_feedlot_adg(target, implant, factor)
    assert growth_path == pytest.approx(shared)
    assert growth_path == pytest.approx(2.4375)
