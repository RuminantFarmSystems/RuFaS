import math
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator


def test_calculate_nitrogen_loss_to_leaching() -> None:
    """Test nitrogen loss to leaching calculation with a simple input."""
    nitrous_oxide_fraction = 0.04
    received_nitrogen = 20.0

    expected = 0.04 * 20.0
    result = SolidsStorageCalculator.calculate_nitrogen_loss_to_leaching(nitrous_oxide_fraction, received_nitrogen)

    assert result == pytest.approx(expected)


def test_calculate_dry_matter_loss() -> None:
    """Test dry matter loss calculation."""
    methane_emissions = 0.12
    carbon_decomposition = 0.24

    expected = 2 * carbon_decomposition + methane_emissions
    result = SolidsStorageCalculator.calculate_dry_matter_loss(methane_emissions, carbon_decomposition)

    assert result == pytest.approx(expected)


def test_calculate_carbon_decomposition(mocker: MockerFixture) -> None:
    """Test carbon decomposition calculation with mocked coefficient + rate."""
    manure_temp = 30.0
    total_solids = 10.0
    ndvs = 5.0

    mocker.patch.object(SolidsStorageCalculator, "calculate_carbon_decomposition_rate", return_value=0.1)
    mocker.patch.object(SolidsStorageCalculator, "calculate_anaerobic_coefficient", return_value=0.2)

    expected = (
        (
            total_solids * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
            + ndvs * ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
        )
        * 0.1
        * ManureConstants.DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION
        * 0.2
    )

    result = SolidsStorageCalculator.calculate_carbon_decomposition(manure_temp, ndvs, total_solids)
    assert result == pytest.approx(expected)


def test_calculate_carbon_decomposition_rate(mocker: MockerFixture) -> None:
    """Test carbon decomposition rate with mocked decomposition values."""
    manure_temp = 30.0
    r_max = 0.2
    r_slow = 0.05

    mocker.patch.object(SolidsStorageCalculator, "calculate_max_microbial_decomposition_rate", return_value=r_max)
    mocker.patch.object(SolidsStorageCalculator, "calculate_slow_fraction_decomposition_rate", return_value=r_slow)

    exponent = ManureConstants.FIRST_ORDER_DECAYING_COEFFICIENT * (
        ManureConstants.DEFAULT_DAYS_SINCE_LAST_MIXING - ManureConstants.DEFAULT_LAG_TIME
    )
    expected = (r_max - r_slow) * (math.e**exponent) + r_slow

    result = SolidsStorageCalculator.calculate_carbon_decomposition_rate(manure_temp)
    assert result == pytest.approx(expected)


def test_calculate_max_microbial_decomposition_rate() -> None:
    """Test that the max microbial decomposition rate is computed correctly."""
    expected = float(
        ManureConstants.EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        * (
            1.066 ** (ManureConstants.DECOMPOSITION_TEMPERATURE - 10)
            - 1.21 ** (ManureConstants.DECOMPOSITION_TEMPERATURE - 50)
        )
    )

    result = SolidsStorageCalculator.calculate_max_microbial_decomposition_rate()
    assert result == pytest.approx(expected)


def test_calculate_slow_fraction_decomposition_rate() -> None:
    """Test slow fraction decomposition rate calculation at a specific temperature."""
    manure_temperature = 35.0

    expected = float(
        ManureConstants.EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        * (1.066 ** (manure_temperature - 10) - 1.21 ** (manure_temperature - 50))
    )

    result = SolidsStorageCalculator.calculate_slow_fraction_decomposition_rate(manure_temperature)
    assert result == pytest.approx(expected)


def test_calculate_anaerobic_coefficient() -> None:
    """Test anaerobic coefficient calculation against expected value."""
    expected = (0.15 / (0.02 + 0.15)) * ((0.02 + 0.21) / 0.21)

    result = SolidsStorageCalculator.calculate_anaerobic_coefficient()
    assert result == pytest.approx(expected)


def test_calculate_methane_conversion_factor() -> None:
    """Tests calculate_methane_conversion_factor()."""
    assert SolidsStorageCalculator.calculate_methane_conversion_factor(25) == 1.3125


def test_calculate_ifsm_methane_emission(mocker: MockerFixture) -> None:
    """Tests calculate_ifsm_methane_emission()."""
    mock_conversion_factor = mocker.patch.object(
        SolidsStorageCalculator,
        "calculate_methane_conversion_factor",
        return_value=1.0,
    )
    manure_volatile_solids = 1000.0
    expected = (manure_volatile_solids * 0.24 * 0.67 * 1.0) / 100

    actual = SolidsStorageCalculator.calculate_ifsm_methane_emission(manure_volatile_solids, 1.0, 0.24)

    mock_conversion_factor.assert_called_once_with(1.0)
    assert actual == pytest.approx(expected)


def test_calculate_ifsm_methane_emission_error() -> None:
    """Tests invalid case for calculate_ifsm_methane_emission()."""
    with pytest.raises(ValueError, match="Manure volatile solids mass must be positive. Received -5."):
        SolidsStorageCalculator.calculate_ifsm_methane_emission(-5, 30, 0.24)


def test_calculate_degradable_volatile_solids_fraction() -> None:
    """Tests calculate_degradable_volatile_solids_fraction()."""
    assert SolidsStorageCalculator.calculate_degradable_volatile_solids_fraction(1, 2) == 0.5


def test_calculate_degradable_volatile_solids_fraction_no_total_volatile_solids() -> None:
    """Tests calculate_degradable_volatile_solids_fraction()."""
    assert SolidsStorageCalculator.calculate_degradable_volatile_solids_fraction(1, 0) == 0.0
