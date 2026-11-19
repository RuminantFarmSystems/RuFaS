"""Unit tests for BeefStockerRequirementsCalculator.

Verifies:
- StockerRequirementsInputs type-guard (non-stocker animal_type raises ValueError)
- Weight/sex input validation (NaN, zero, non-finite raise ValueError)
- NotImplementedError guards on BeefNRCRequirementsCalculator and
  BeefCowCalfRequirementsCalculator when passed stocker animal types
- Structural checks: pregnancy/lactation/activity energy == 0
- DMI clamp at BEEF_DMI_MIN_NE_CONCENTRATION

NRC 2016 benchmark scenarios (SK-MAINT-1…SK-MP-1) live in test_beef_stocker_benchmarks.py.
"""

from __future__ import annotations

import math

import pytest

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.beef_cow_calf_requirements_calculator import (
    BeefCowCalfRequirementsCalculator,
    CowCalfRequirementsInputs,
)
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import (
    BeefNRCRequirementsCalculator,
)
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import (
    BeefStockerRequirementsCalculator,
    StockerRequirementsInputs,
)

# ---------------------------------------------------------------------------
# NRC 2016 benchmark scenario — 280 kg Angus steer (source: NRC 2016 Ch.10-12)
# ---------------------------------------------------------------------------

_BENCHMARK_BW = 280.0  # kg live weight
_BENCHMARK_MBW = 520.0  # kg, beef_mature_cow_weight_kg (NOT stocker exit weight)
_BENCHMARK_ADG = 0.80  # kg/d
_BENCHMARK_NE_DIET = 1.0  # Mcal/kg DM forage (Eq.10-5 input)
_BENCHMARK_TEMP = 20.0  # °C thermoneutral — a2 cold-stress term = 0


def _make_benchmark_inputs(**overrides: object) -> StockerRequirementsInputs:
    """Build a StockerRequirementsInputs with benchmark values and optional overrides."""
    defaults: dict[str, object] = {
        "animal_type": AnimalType.BEEF_STOCKER_STEER,
        "sex": Sex.STEER,
        "body_weight": _BENCHMARK_BW,
        "mature_body_weight": _BENCHMARK_MBW,
        "breed": "Angus",
        "target_adg": _BENCHMARK_ADG,
        "temperature_c": _BENCHMARK_TEMP,
        "ne_diet_concentration": _BENCHMARK_NE_DIET,
        "mud_condition": AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
    }
    defaults.update(overrides)
    return StockerRequirementsInputs(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Type guard — non-stocker animal_type must raise ValueError
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_calculate_requirements_raises_for_feedlot_steer() -> None:
    """FEEDLOT_STEER passed to stocker calculator must raise ValueError."""
    inputs = _make_benchmark_inputs(animal_type=AnimalType.FEEDLOT_STEER)
    with pytest.raises(ValueError, match="stocker"):
        BeefStockerRequirementsCalculator.calculate_requirements(inputs)


@pytest.mark.unit
def test_calculate_requirements_raises_for_cow_calf_type() -> None:
    """BEEF_COW passed to stocker calculator must raise ValueError."""
    inputs = _make_benchmark_inputs(animal_type=AnimalType.BEEF_COW)
    with pytest.raises(ValueError, match="stocker"):
        BeefStockerRequirementsCalculator.calculate_requirements(inputs)


# ---------------------------------------------------------------------------
# Weight validation — body_weight and mature_body_weight must be finite and > 0
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("bad_bw", [0.0, -1.0, float("nan"), float("inf")])
def test_calculate_requirements_invalid_body_weight(bad_bw: float) -> None:
    """body_weight must be positive and finite; zero/negative/NaN/inf raise ValueError."""
    inputs = _make_benchmark_inputs(body_weight=bad_bw)
    with pytest.raises(ValueError, match="body_weight"):
        BeefStockerRequirementsCalculator.calculate_requirements(inputs)


@pytest.mark.unit
@pytest.mark.parametrize("bad_mbw", [0.0, -1.0, float("nan"), float("inf")])
def test_calculate_requirements_invalid_mature_body_weight(bad_mbw: float) -> None:
    """mature_body_weight must be positive and finite; invalid values raise ValueError."""
    inputs = _make_benchmark_inputs(mature_body_weight=bad_mbw)
    with pytest.raises(ValueError, match="mature_body_weight"):
        BeefStockerRequirementsCalculator.calculate_requirements(inputs)


# ---------------------------------------------------------------------------
# Sex validation — must be a member of SEX_NEm_MULTIPLIER
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_calculate_requirements_valid_sex_female() -> None:
    """Sex.FEMALE (heifer) must be accepted without raising."""
    inputs = _make_benchmark_inputs(animal_type=AnimalType.BEEF_STOCKER_HEIFER, sex=Sex.FEMALE)
    result = BeefStockerRequirementsCalculator.calculate_requirements(inputs)
    assert math.isfinite(result.maintenance_energy)
    assert result.maintenance_energy > 0.0


@pytest.mark.unit
def test_calculate_requirements_stocker_heifer_lower_eqsbw() -> None:
    """BEEF_STOCKER_HEIFER with Sex.FEMALE should produce finite positive requirements."""
    inputs = _make_benchmark_inputs(
        animal_type=AnimalType.BEEF_STOCKER_HEIFER,
        sex=Sex.FEMALE,
        body_weight=260.0,
    )
    result = BeefStockerRequirementsCalculator.calculate_requirements(inputs)
    assert result.growth_energy >= 0.0
    assert result.metabolizable_protein > 0.0


# ---------------------------------------------------------------------------
# Structural checks — pregnancy/lactation fields must be zero for stocker
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_pregnancy_energy_is_zero() -> None:
    """Stocker animals never gestate; pregnancy_energy must be 0.0."""
    result = BeefStockerRequirementsCalculator.calculate_requirements(_make_benchmark_inputs())
    assert result.pregnancy_energy == pytest.approx(0.0)


@pytest.mark.unit
def test_lactation_energy_is_zero() -> None:
    """Stocker animals never lactate; lactation_energy must be 0.0."""
    result = BeefStockerRequirementsCalculator.calculate_requirements(_make_benchmark_inputs())
    assert result.lactation_energy == pytest.approx(0.0)


@pytest.mark.unit
def test_activity_energy_is_zero() -> None:
    """Activity energy is not modelled for stocker; activity_energy must be 0.0."""
    result = BeefStockerRequirementsCalculator.calculate_requirements(_make_benchmark_inputs())
    assert result.activity_energy == pytest.approx(0.0)


@pytest.mark.unit
def test_dmi_clamp_below_min_ne_concentration_returns_same_as_at_clamp() -> None:
    """ne_diet_concentration below BEEF_DMI_MIN_NE_CONCENTRATION is clamped; must not raise.

    Both at-clamp and below-clamp calls must produce the same DMI because
    the floor ensures identical effective ne_c in Eq.10-5.
    """
    at_clamp = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_benchmark_inputs(ne_diet_concentration=AnimalModuleConstants.BEEF_DMI_MIN_NE_CONCENTRATION)
    )
    below_clamp = BeefStockerRequirementsCalculator.calculate_requirements(
        _make_benchmark_inputs(ne_diet_concentration=0.1)
    )
    assert below_clamp.dry_matter == pytest.approx(at_clamp.dry_matter)


# ---------------------------------------------------------------------------
# NotImplementedError guards on existing beef calculators
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_beef_nrc_calc_raises_not_implemented_for_stocker_steer() -> None:
    """BeefNRCRequirementsCalculator must raise NotImplementedError for BEEF_STOCKER_STEER."""
    with pytest.raises(NotImplementedError, match="BeefStockerRequirementsCalculator"):
        BeefNRCRequirementsCalculator.calculate_requirements(
            body_weight=280.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_STOCKER_STEER,
            breed="Angus",
            sex=Sex.STEER,
            days_on_feed=0,
            target_adg=0.80,
            implant_adg_factor=1.0,
            housing="Open_Lot",
            mud_condition=AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
            temperature_c=20.0,
            ne_diet_concentration=1.0,
            process_based_phosphorus_requirement=0.0,
        )


@pytest.mark.unit
def test_beef_nrc_calc_raises_not_implemented_for_stocker_heifer() -> None:
    """BeefNRCRequirementsCalculator must raise NotImplementedError for BEEF_STOCKER_HEIFER."""
    with pytest.raises(NotImplementedError, match="BeefStockerRequirementsCalculator"):
        BeefNRCRequirementsCalculator.calculate_requirements(
            body_weight=260.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_STOCKER_HEIFER,
            breed="Angus",
            sex=Sex.FEMALE,
            days_on_feed=0,
            target_adg=0.80,
            implant_adg_factor=1.0,
            housing="Open_Lot",
            mud_condition=AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
            temperature_c=20.0,
            ne_diet_concentration=1.0,
            process_based_phosphorus_requirement=0.0,
        )


@pytest.mark.unit
def test_beef_cow_calf_calc_raises_not_implemented_for_stocker_steer() -> None:
    """BeefCowCalfRequirementsCalculator must raise NotImplementedError for BEEF_STOCKER_STEER."""
    inputs = CowCalfRequirementsInputs(
        body_weight=280.0,
        mature_body_weight=520.0,
        animal_type=AnimalType.BEEF_STOCKER_STEER,
        breed="Angus",
        sex=Sex.STEER,
        body_condition_score=5.0,
        days_pregnant=None,
        days_in_milk=None,
        parity=0,
        target_adg=0.80,
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=1.0,
        process_based_phosphorus_requirement=0.0,
    )
    with pytest.raises(NotImplementedError, match="BeefStockerRequirementsCalculator"):
        BeefCowCalfRequirementsCalculator.calculate_requirements(inputs)


@pytest.mark.unit
def test_beef_cow_calf_calc_raises_not_implemented_for_stocker_heifer() -> None:
    """BeefCowCalfRequirementsCalculator must raise NotImplementedError for BEEF_STOCKER_HEIFER."""
    inputs = CowCalfRequirementsInputs(
        body_weight=260.0,
        mature_body_weight=520.0,
        animal_type=AnimalType.BEEF_STOCKER_HEIFER,
        breed="Angus",
        sex=Sex.FEMALE,
        body_condition_score=5.0,
        days_pregnant=None,
        days_in_milk=None,
        parity=0,
        target_adg=0.80,
        mud_condition="none",
        temperature_c=20.0,
        ne_diet_concentration=1.0,
        process_based_phosphorus_requirement=0.0,
    )
    with pytest.raises(NotImplementedError, match="BeefStockerRequirementsCalculator"):
        BeefCowCalfRequirementsCalculator.calculate_requirements(inputs)
