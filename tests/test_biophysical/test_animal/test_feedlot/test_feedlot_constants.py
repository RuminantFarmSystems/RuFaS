"""Tests for feedlot constants in AnimalModuleConstants and event strings."""

import pytest
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal import animal_constants


@pytest.mark.unit
def test_feedlot_min_dmi_ratio_exists() -> None:
    """FEEDLOT_MIN_DMI_RATIO must be 0.015."""
    assert AnimalModuleConstants.FEEDLOT_MIN_DMI_RATIO == pytest.approx(0.015)


@pytest.mark.unit
def test_step_up_starter_end_day_exists() -> None:
    """STEP_UP_STARTER_END_DAY must be 7."""
    assert AnimalModuleConstants.STEP_UP_STARTER_END_DAY == 7


@pytest.mark.unit
def test_step_up_transition_end_day_exists() -> None:
    """STEP_UP_TRANSITION_END_DAY must be 21."""
    assert AnimalModuleConstants.STEP_UP_TRANSITION_END_DAY == 21


@pytest.mark.unit
def test_receiving_period_days_exists() -> None:
    """RECEIVING_PERIOD_DAYS must be 21."""
    assert AnimalModuleConstants.RECEIVING_PERIOD_DAYS == 21


@pytest.mark.unit
def test_receiving_dmi_fraction_exists() -> None:
    """RECEIVING_DMI_FRACTION must be 0.60."""
    assert AnimalModuleConstants.RECEIVING_DMI_FRACTION == pytest.approx(0.60)


@pytest.mark.unit
@pytest.mark.parametrize(
    "breed,expected_mult",
    [
        # NRC 2016 Table 19-1 exact BE factors
        ("Angus", 1.0),
        ("Hereford", 1.0),
        ("Charolais", 1.0),
        ("Limousin", 1.0),
        ("Brahman", 0.9),
        ("Crossbred", 1.0),
        ("Simmental", 1.2),
        ("Holstein", 1.2),
        ("Jersey", 1.2),
    ],
)
def test_breed_nem_multiplier(breed: str, expected_mult: float) -> None:
    """BREED_NEm_MULTIPLIER must contain correct NRC 2016 Table 19-1 BE values."""
    assert breed in AnimalModuleConstants.BREED_NEm_MULTIPLIER
    assert AnimalModuleConstants.BREED_NEm_MULTIPLIER[breed] == pytest.approx(expected_mult)


@pytest.mark.unit
@pytest.mark.parametrize(
    "sex,expected_mult",
    [
        (Sex.STEER, 1.00),
        (Sex.FEMALE, 1.00),
        (Sex.MALE, 1.15),
    ],
)
def test_sex_nem_multiplier(sex: Sex, expected_mult: float) -> None:
    """SEX_NEm_MULTIPLIER must contain correct NRC 2016 Table 19-1 values."""
    assert sex in AnimalModuleConstants.SEX_NEm_MULTIPLIER
    assert AnimalModuleConstants.SEX_NEm_MULTIPLIER[sex] == pytest.approx(expected_mult)


@pytest.mark.unit
@pytest.mark.parametrize(
    "attr,expected",
    [
        ("MUD_NEm_MULTIPLIER_NONE", 1.00),
        ("MUD_NEm_MULTIPLIER_MILD", 1.08),
        ("MUD_NEm_MULTIPLIER_SEVERE", 1.30),
        ("DEFAULT_IMPLANT_ADG_FACTOR", 1.0),
    ],
)
def test_feedlot_numeric_constants(attr: str, expected: float) -> None:
    """Feedlot numeric constants must exist with correct values."""
    assert hasattr(AnimalModuleConstants, attr)
    assert getattr(AnimalModuleConstants, attr) == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.parametrize(
    "attr,expected_str",
    [
        ("FEEDLOT_ARRIVAL", "feedlot arrival"),
        ("RECEIVING_STRESS_END", "receiving stress period ended"),
        ("SLAUGHTER_WEIGHT_REACHED", "slaughter weight reached"),
        ("MAX_DAYS_ON_FEED_REACHED", "max days on feed reached"),
        ("STEP_UP_STARTER", "diet phase: starter"),
        ("STEP_UP_TRANSITION", "diet phase: transition"),
        ("STEP_UP_FINISHER", "diet phase: finisher"),
    ],
)
def test_feedlot_event_constants(attr: str, expected_str: str) -> None:
    """Feedlot event string constants must exist with correct values."""
    assert hasattr(animal_constants, attr)
    assert getattr(animal_constants, attr) == expected_str
