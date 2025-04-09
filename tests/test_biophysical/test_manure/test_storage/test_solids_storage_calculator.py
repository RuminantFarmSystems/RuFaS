import math
import pytest
from pytest_mock import MockerFixture
from RUFAS.biophysical.manure.storage.solids_storage_calculator import (
    AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN,
    COMPOSTING_DECOMPOSITION_TEMPERATURE,
    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD,
    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND,
    DEFAULT_DAYS_SINCE_LAST_TURNING,
    DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION,
    DEFAULT_LAG_TIME,
    DEFAULT_MOLE_FRACTION_OF_OXYGEN,
    EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE,
    FIRST_ORDER_DECAYING_COEFFICIENT,
    OXYGEN_HALF_SATURATION_CONSTANT,
    SolidsStorageCalculator,
)


def test_calculate_nitrogen_loss_to_leaching() -> None:
    """Test nitrogen loss to leaching calculation with a simple input."""
    nitrous_oxide_fraction = 0.04
    received_nitrogen = 20.0

    expected = 0.04 * 20.0
    result = SolidsStorageCalculator._calculate_nitrogen_loss_to_leaching(nitrous_oxide_fraction, received_nitrogen)

    assert result == pytest.approx(expected)


def test_calculate_dry_matter_loss() -> None:
    """Test dry matter loss calculation."""
    methane_emissions = 0.12
    carbon_decomposition = 0.24

    expected = 2 * carbon_decomposition + methane_emissions
    result = SolidsStorageCalculator._calculate_dry_matter_loss(methane_emissions, carbon_decomposition)

    assert result == pytest.approx(expected)


def test_calculate_carbon_decomposition(mocker: MockerFixture) -> None:
    """Test carbon decomposition calculation with mocked coefficient + rate."""
    manure_temp = 30.0
    total_solids = 10.0
    ndvs = 5.0

    mocker.patch.object(SolidsStorageCalculator, "_calculate_carbon_decomposition_rate", return_value=0.1)
    mocker.patch.object(SolidsStorageCalculator, "_calculate_anaerobic_coefficient", return_value=0.2)

    expected = (
        (total_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD + ndvs * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND)
        * 0.1
        * DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION
        * 0.2
    )

    result = SolidsStorageCalculator._calculate_carbon_decomposition(manure_temp, ndvs, total_solids)
    assert result == pytest.approx(expected)


def test_calculate_carbon_decomposition_rate(mocker: MockerFixture) -> None:
    """Test carbon decomposition rate with mocked decomposition values."""
    manure_temp = 30.0
    r_max = 0.2
    r_slow = 0.05

    mocker.patch.object(SolidsStorageCalculator, "_calculate_max_microbial_decomposition_rate", return_value=r_max)
    mocker.patch.object(SolidsStorageCalculator, "_calculate_slow_fraction_decomposition_rate", return_value=r_slow)

    exponent = FIRST_ORDER_DECAYING_COEFFICIENT * (DEFAULT_DAYS_SINCE_LAST_TURNING - DEFAULT_LAG_TIME)
    expected = (r_max - r_slow) * (math.e**exponent) + r_slow

    result = SolidsStorageCalculator._calculate_carbon_decomposition_rate(manure_temp)
    assert result == pytest.approx(expected)


def test_calculate_max_microbial_decomposition_rate() -> None:
    """Test that the max microbial decomposition rate is computed correctly."""
    expected = float(
        EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        * (1.066 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 10) - 1.21 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 50))
    )

    result = SolidsStorageCalculator._calculate_max_microbial_decomposition_rate()
    assert result == pytest.approx(expected)


def test_calculate_slow_fraction_decomposition_rate() -> None:
    """Test slow fraction decomposition rate calculation at a specific temperature."""
    manure_temperature = 35.0

    expected = float(
        EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        * (1.066 ** (manure_temperature - 10) - 1.21 ** (manure_temperature - 50))
    )

    result = SolidsStorageCalculator._calculate_slow_fraction_decomposition_rate(manure_temperature)
    assert result == pytest.approx(expected)


def test_calculate_anaerobic_coefficient() -> None:
    """Test anaerobic coefficient calculation against expected value."""
    expected = (
        DEFAULT_MOLE_FRACTION_OF_OXYGEN / (OXYGEN_HALF_SATURATION_CONSTANT + DEFAULT_MOLE_FRACTION_OF_OXYGEN)
    ) * ((OXYGEN_HALF_SATURATION_CONSTANT + AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN) / AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN)

    result = SolidsStorageCalculator._calculate_anaerobic_coefficient()
    assert result == pytest.approx(expected)
