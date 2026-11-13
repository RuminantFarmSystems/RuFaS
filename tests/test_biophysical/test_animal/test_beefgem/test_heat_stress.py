"""Phase D-1 checkpoint — THI-based heat stress on beef DMI and maintenance energy.

Covers the THI formula bracket form, the piecewise-linear interpolator, the
tuple-length invariant, and the application of both modifiers in the feedlot
and stocker calculators.
"""

from __future__ import annotations

import copy
from typing import Any, Iterator

import pytest

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import (
    BeefStockerRequirementsCalculator,
    StockerRequirementsInputs,
)
from RUFAS.data_validator import DataValidator

DMI_MULTIPLIERS = AnimalModuleConstants.BEEF_HEAT_STRESS_DMI_MULTIPLIERS
NEM_MULTIPLIERS = AnimalModuleConstants.BEEF_HEAT_STRESS_NEM_MULTIPLIERS
BREAKPOINTS = AnimalModuleConstants.BEEF_THI_BREAKPOINTS


@pytest.fixture(autouse=True)
def restore_humidity_config() -> Iterator[None]:
    """Keep relative_humidity_pct from leaking between tests."""
    saved = AnimalConfig.relative_humidity_pct
    yield
    AnimalConfig.relative_humidity_pct = saved


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


# ───────────────────────────── THI formula ──────────────────────────────


@pytest.mark.unit
@pytest.mark.nrc2016
def test_thi_at_thirty_c_eighty_pct_humidity() -> None:
    """THI at 30 C / 80% RH is 82.92 — guards the (1.8 x T - 26) bracket.

    The wrong form (t_f - 26) understates THI by about 3.5 units here and
    would silently suppress heat stress across the whole range.
    """
    thi = BeefNRCRequirementsCalculator.calculate_thi(30.0, 80.0)
    assert thi == pytest.approx(82.92, abs=0.01)


@pytest.mark.unit
def test_thi_second_bracket_is_not_fahrenheit() -> None:
    """The two bracket forms differ by 32 x the humidity coefficient."""
    temperature_c, humidity = 30.0, 80.0
    t_f = 1.8 * temperature_c + 32
    wrong = t_f - (0.55 - 0.0055 * humidity) * (t_f - 26)
    correct = BeefNRCRequirementsCalculator.calculate_thi(temperature_c, humidity)
    assert correct > wrong
    assert correct - wrong == pytest.approx(32 * (0.55 - 0.0055 * humidity), abs=1e-9)


@pytest.mark.unit
def test_thi_rises_with_humidity_at_fixed_temperature() -> None:
    """Higher humidity yields a higher index at the same temperature."""
    low = BeefNRCRequirementsCalculator.calculate_thi(30.0, 20.0)
    high = BeefNRCRequirementsCalculator.calculate_thi(30.0, 90.0)
    assert high > low


@pytest.mark.unit
def test_thi_rises_with_temperature_at_fixed_humidity() -> None:
    """Higher temperature yields a higher index at the same humidity."""
    cool = BeefNRCRequirementsCalculator.calculate_thi(15.0, 60.0)
    hot = BeefNRCRequirementsCalculator.calculate_thi(35.0, 60.0)
    assert hot > cool


# ────────────────────────── constants and invariant ──────────────────────


@pytest.mark.unit
def test_all_three_heat_stress_tuples_are_the_same_length() -> None:
    """Anchors and multipliers pair one-to-one."""
    assert len(DMI_MULTIPLIERS) == len(BREAKPOINTS)
    assert len(NEM_MULTIPLIERS) == len(BREAKPOINTS)


@pytest.mark.unit
def test_breakpoints_are_the_decided_anchors() -> None:
    """72 is the onset, 80 the moderate class, 90 the severe."""
    assert BREAKPOINTS == (72.0, 80.0, 90.0)
    assert DMI_MULTIPLIERS == (1.00, 0.88, 0.75)
    assert NEM_MULTIPLIERS == (1.00, 1.12, 1.20)


@pytest.mark.unit
def test_mismatched_multiplier_length_raises_value_error() -> None:
    """Adding an anchor without its multiplier must fail loudly, not silently."""
    with pytest.raises(ValueError, match="pair one-to-one"):
        BeefNRCRequirementsCalculator._interpolate_heat_stress(80.0, (1.0, 0.9))


# ─────────────────────────── the multiplier table ────────────────────────


@pytest.mark.unit
@pytest.mark.parametrize(
    "thi, expected_dmi, expected_nem",
    [
        (71.9, 1.000, 1.000),
        (72.0, 1.000, 1.000),
        (76.0, 0.940, 1.060),
        (80.0, 0.880, 1.120),
        (85.0, 0.815, 1.160),
        (90.0, 0.750, 1.200),
        (95.0, 0.750, 1.200),
    ],
)
def test_heat_stress_multiplier_table(thi: float, expected_dmi: float, expected_nem: float) -> None:
    """The seven-row specification table from the plan."""
    assert BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, DMI_MULTIPLIERS) == pytest.approx(
        expected_dmi, abs=1e-6
    )
    assert BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, NEM_MULTIPLIERS) == pytest.approx(
        expected_nem, abs=1e-6
    )


@pytest.mark.unit
def test_heat_stress_continuous_at_onset() -> None:
    """No step at THI 72 — the response rises from 1.0 continuously."""
    just_below = BeefNRCRequirementsCalculator._interpolate_heat_stress(71.999, DMI_MULTIPLIERS)
    just_above = BeefNRCRequirementsCalculator._interpolate_heat_stress(72.001, DMI_MULTIPLIERS)
    assert just_above == pytest.approx(just_below, abs=1e-4)


@pytest.mark.unit
def test_nem_also_continuous_at_onset() -> None:
    """The maintenance multiplier has no step at the onset either."""
    just_below = BeefNRCRequirementsCalculator._interpolate_heat_stress(71.999, NEM_MULTIPLIERS)
    just_above = BeefNRCRequirementsCalculator._interpolate_heat_stress(72.001, NEM_MULTIPLIERS)
    assert just_above == pytest.approx(just_below, abs=1e-4)


@pytest.mark.unit
def test_source_mild_dmi_value_falls_inside_the_mild_band() -> None:
    """0.95 is reached at THI 75.33, inside 72-80 — not pinned at the onset."""
    assert BeefNRCRequirementsCalculator._interpolate_heat_stress(75.33, DMI_MULTIPLIERS) == pytest.approx(
        0.95, abs=1e-3
    )


@pytest.mark.unit
def test_source_mild_nem_value_falls_inside_the_mild_band() -> None:
    """1.07 is reached at THI 76.67, inside 72-80 — not pinned at the onset."""
    assert BeefNRCRequirementsCalculator._interpolate_heat_stress(76.67, NEM_MULTIPLIERS) == pytest.approx(
        1.07, abs=1e-3
    )


@pytest.mark.unit
def test_dmi_multiplier_never_increases_with_thi() -> None:
    """Monotone non-increasing across the whole range."""
    values = [BeefNRCRequirementsCalculator._interpolate_heat_stress(t / 10, DMI_MULTIPLIERS) for t in range(600, 1001)]
    assert all(later <= earlier + 1e-12 for earlier, later in zip(values, values[1:]))


@pytest.mark.unit
def test_nem_multiplier_never_decreases_with_thi() -> None:
    """Monotone non-decreasing across the whole range."""
    values = [BeefNRCRequirementsCalculator._interpolate_heat_stress(t / 10, NEM_MULTIPLIERS) for t in range(600, 1001)]
    assert all(later >= earlier - 1e-12 for earlier, later in zip(values, values[1:]))


@pytest.mark.unit
def test_multipliers_stay_positive_so_dmi_cannot_go_negative() -> None:
    """Every multiplier is bounded by the tuple, so no floor is needed."""
    for tenths in range(0, 1500):
        assert BeefNRCRequirementsCalculator._interpolate_heat_stress(tenths / 10, DMI_MULTIPLIERS) > 0.0


# ──────────────────────── config field and validation ────────────────────


@pytest.mark.unit
def test_relative_humidity_defaults_to_none() -> None:
    """Heat stress is opt-in — the default disables it entirely."""
    assert AnimalConfig.relative_humidity_pct is None


@pytest.mark.unit
@pytest.mark.parametrize("humidity", [0.0, 50.0, 100.0])
def test_valid_humidity_accepted(humidity: float) -> None:
    """The inclusive 0-100 range is accepted."""
    DataValidator._validate_relative_humidity({"relative_humidity_pct": humidity})


@pytest.mark.unit
@pytest.mark.parametrize("humidity", [-0.1, 100.1, -20.0, 150.0])
def test_humidity_outside_range_raises_value_error(humidity: float) -> None:
    """Outside 0-100 is rejected."""
    with pytest.raises(ValueError, match="relative_humidity_pct"):
        DataValidator._validate_relative_humidity({"relative_humidity_pct": humidity})


@pytest.mark.unit
@pytest.mark.parametrize("humidity", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_humidity_raises_value_error(humidity: float) -> None:
    """NaN and both infinities are rejected."""
    with pytest.raises(ValueError, match="relative_humidity_pct"):
        DataValidator._validate_relative_humidity({"relative_humidity_pct": humidity})


@pytest.mark.unit
def test_absent_humidity_key_is_accepted() -> None:
    """A config block without the key keeps the None default."""
    DataValidator._validate_relative_humidity({})


@pytest.mark.unit
def test_explicit_none_humidity_is_accepted() -> None:
    """An explicit null disables heat stress rather than failing validation."""
    DataValidator._validate_relative_humidity({"relative_humidity_pct": None})


@pytest.mark.component
def test_config_parses_humidity_from_animal_config_block(mocker: Any) -> None:
    """The field is read from the top level, since heat stress is farm-wide."""
    mocker.patch.object(AnimalConfig, "relative_humidity_pct", None, create=True)
    AnimalConfig._initialize_relative_humidity({"relative_humidity_pct": 72.5})
    assert AnimalConfig.relative_humidity_pct == pytest.approx(72.5)


@pytest.mark.component
def test_config_keeps_none_when_key_absent(mocker: Any) -> None:
    """A missing key leaves heat stress disabled."""
    mocker.patch.object(AnimalConfig, "relative_humidity_pct", None, create=True)
    AnimalConfig._initialize_relative_humidity({})
    assert AnimalConfig.relative_humidity_pct is None


# ─────────────────────── application in the calculators ──────────────────


@pytest.mark.component
def test_stocker_humidity_none_applies_no_modification() -> None:
    """Backward compatibility: no humidity means identical results."""
    baseline = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=35.0, relative_humidity_pct=None)
    )
    reference = BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(temperature_c=35.0))
    assert baseline.dry_matter == pytest.approx(reference.dry_matter)
    assert baseline.maintenance_energy == pytest.approx(reference.maintenance_energy)


@pytest.mark.component
def test_stocker_heat_stress_reduces_dmi_and_raises_maintenance() -> None:
    """At 35 C / 90% RH the animal eats less and needs more maintenance energy."""
    neutral = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=35.0, relative_humidity_pct=None)
    )
    stressed = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=35.0, relative_humidity_pct=90.0)
    )
    assert stressed.dry_matter < neutral.dry_matter
    assert stressed.maintenance_energy > neutral.maintenance_energy


@pytest.mark.component
def test_stocker_below_onset_applies_no_modification() -> None:
    """A cool day sits below THI 72 and leaves both values untouched."""
    neutral = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=10.0, relative_humidity_pct=None)
    )
    mild = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=10.0, relative_humidity_pct=50.0)
    )
    assert mild.dry_matter == pytest.approx(neutral.dry_matter)
    assert mild.maintenance_energy == pytest.approx(neutral.maintenance_energy)


@pytest.mark.component
def test_stocker_modifier_matches_the_interpolated_multiplier() -> None:
    """The applied factor is exactly the interpolator's output, not an approximation."""
    temperature_c, humidity = 32.0, 85.0
    neutral = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=temperature_c, relative_humidity_pct=None)
    )
    stressed = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=temperature_c, relative_humidity_pct=humidity)
    )
    thi = BeefNRCRequirementsCalculator.calculate_thi(temperature_c, humidity)
    expected_dmi = BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, DMI_MULTIPLIERS)
    expected_nem = BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, NEM_MULTIPLIERS)
    assert stressed.dry_matter == pytest.approx(neutral.dry_matter * expected_dmi)
    assert stressed.maintenance_energy == pytest.approx(neutral.maintenance_energy * expected_nem)


@pytest.mark.component
def test_feedlot_humidity_none_applies_no_modification() -> None:
    """Backward compatibility for the feedlot path."""
    baseline = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=35.0, relative_humidity_pct=None)
    )
    reference = BeefNRCRequirementsCalculator.calculate_requirements(**_feedlot_kwargs(temperature_c=35.0))
    assert baseline.dry_matter == pytest.approx(reference.dry_matter)
    assert baseline.maintenance_energy == pytest.approx(reference.maintenance_energy)


@pytest.mark.component
def test_feedlot_heat_stress_reduces_dmi_and_raises_maintenance() -> None:
    """The feedlot calculator responds the same way as the stocker."""
    neutral = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=35.0, relative_humidity_pct=None)
    )
    stressed = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=35.0, relative_humidity_pct=90.0)
    )
    assert stressed.dry_matter < neutral.dry_matter
    assert stressed.maintenance_energy > neutral.maintenance_energy


@pytest.mark.component
def test_feedlot_modifier_matches_the_interpolated_multiplier() -> None:
    """The feedlot factor is the interpolator's output exactly."""
    temperature_c, humidity = 32.0, 85.0
    neutral = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=temperature_c, relative_humidity_pct=None)
    )
    stressed = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=temperature_c, relative_humidity_pct=humidity)
    )
    thi = BeefNRCRequirementsCalculator.calculate_thi(temperature_c, humidity)
    expected_dmi = BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, DMI_MULTIPLIERS)
    expected_nem = BeefNRCRequirementsCalculator._interpolate_heat_stress(thi, NEM_MULTIPLIERS)
    assert stressed.dry_matter == pytest.approx(neutral.dry_matter * expected_dmi)
    assert stressed.maintenance_energy == pytest.approx(neutral.maintenance_energy * expected_nem)


@pytest.mark.component
def test_maintenance_energy_is_not_modified_twice_for_the_stocker() -> None:
    """The stocker borrows the feedlot's NEm helper.

    If the modifier were applied inside _calculate_maintenance_energy as well as
    in calculate_requirements, the feedlot path would square it. Comparing the
    two calculators' ratios at the same THI catches that.
    """
    temperature_c, humidity = 33.0, 88.0
    stocker_neutral = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=temperature_c, relative_humidity_pct=None)
    )
    stocker_stressed = BeefStockerRequirementsCalculator.calculate_requirements(
        _stocker_inputs(temperature_c=temperature_c, relative_humidity_pct=humidity)
    )
    feedlot_neutral = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=temperature_c, relative_humidity_pct=None)
    )
    feedlot_stressed = BeefNRCRequirementsCalculator.calculate_requirements(
        **_feedlot_kwargs(temperature_c=temperature_c, relative_humidity_pct=humidity)
    )
    stocker_ratio = stocker_stressed.maintenance_energy / stocker_neutral.maintenance_energy
    feedlot_ratio = feedlot_stressed.maintenance_energy / feedlot_neutral.maintenance_energy
    assert stocker_ratio == pytest.approx(feedlot_ratio)


@pytest.mark.component
def test_stocker_rejects_humidity_outside_range() -> None:
    """Calculator-level validation mirrors the config validation."""
    with pytest.raises(ValueError, match="relative_humidity_pct"):
        BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(relative_humidity_pct=150.0))


@pytest.mark.component
def test_stocker_rejects_non_finite_humidity() -> None:
    """NaN humidity would otherwise propagate into DMI silently."""
    with pytest.raises(ValueError, match="relative_humidity_pct"):
        BeefStockerRequirementsCalculator.calculate_requirements(_stocker_inputs(relative_humidity_pct=float("nan")))


@pytest.mark.regression
def test_dairy_path_is_untouched_by_heat_stress() -> None:
    """The multipliers live on the beef calculators only."""
    from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator

    assert not hasattr(NASEMRequirementsCalculator, "_interpolate_heat_stress")


@pytest.mark.regression
def test_constants_are_immutable_tuples() -> None:
    """Tuples, not lists — a shared mutable default would leak across runs."""
    assert isinstance(BREAKPOINTS, tuple)
    assert isinstance(DMI_MULTIPLIERS, tuple)
    assert isinstance(NEM_MULTIPLIERS, tuple)


@pytest.mark.regression
def test_deepcopy_of_multipliers_is_equal() -> None:
    """Guards against a future refactor to a mutable container."""
    assert copy.deepcopy(DMI_MULTIPLIERS) == DMI_MULTIPLIERS
