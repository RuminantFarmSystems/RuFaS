import math

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.open_lot_cbpb_calculator import OpenLotCbpbCalculator


def test_calculate_methane_conversion_factor() -> None:
    """Tests calculate_methane_conversion_factor()."""
    assert OpenLotCbpbCalculator.calculate_methane_conversion_factor(1.0) == -0.1875


def test_calculate_ifsm_methane_emission(mocker: MockerFixture) -> None:
    """Tests calculate_ifsm_methane_emission()."""
    mock_conversion_factor = mocker.patch.object(
        OpenLotCbpbCalculator,
        "calculate_methane_conversion_factor",
        return_value=1.0,
    )
    manure_volatile_solids = 1000.0
    expected = (manure_volatile_solids * 0.24 * 0.67 * 1.0) / 100

    actual = OpenLotCbpbCalculator.calculate_ifsm_methane_emission(manure_volatile_solids, 1.0)

    mock_conversion_factor.assert_called_once_with(1.0)
    assert actual == pytest.approx(expected)


def test_calculate_total_carbon_decomposition(mocker: MockerFixture) -> None:
    """Tests calculate_total_carbon_decomposition()."""
    mock_anaerobic_effect = mocker.patch.object(OpenLotCbpbCalculator, "calculate_anaerobic_effect", return_value=1)
    mock_carbon_decomp_rate = mocker.patch.object(
        OpenLotCbpbCalculator, "calculate_carbon_decomposition_rate", return_value=0.7
    )

    result = OpenLotCbpbCalculator.calculate_total_carbon_decomposition(12, 20, 3, 4)

    assert result == 5.915
    mock_anaerobic_effect.assert_called_once()
    mock_carbon_decomp_rate.assert_called_once()


def test_calculate_carbon_decomposition_rate(mocker: MockerFixture) -> None:
    """Tests calculate_carbon_decomposition_rate()."""
    mock_microbial_rate = mocker.patch.object(
        OpenLotCbpbCalculator, "calculate_microbial_decomp_rate", side_effect=[0.4, 0.1]
    )

    result = OpenLotCbpbCalculator.calculate_carbon_decomposition_rate(16)

    assert 0.1216559 == pytest.approx(result)
    assert mock_microbial_rate.call_count == 2


@pytest.mark.parametrize(
    "oxygen_mole_fraction, oxygen_ambient_air_mole_fraction, should_throw",
    [
        (-1.0, 0.21, True),
        (2.0, 0.21, True),
        (0.15, -1.0, True),
        (0.15, 2.0, True),
        (0.15, 0.21, False),
    ],
)
def test_calculate_anaerobic_effect(
    oxygen_mole_fraction: float,
    oxygen_ambient_air_mole_fraction: float,
    should_throw: bool,
) -> None:
    """Tests _aneerobic_coefficient() in calculator.py."""
    if should_throw:
        with pytest.raises(ValueError):
            OpenLotCbpbCalculator.calculate_anaerobic_effect(
                oxygen_mole_fraction=oxygen_mole_fraction,
                oxygen_ambient_air_mole_fraction=oxygen_ambient_air_mole_fraction,
            )
    else:
        expected = (oxygen_mole_fraction / (0.02 + oxygen_mole_fraction)) * (
            (0.02 + oxygen_ambient_air_mole_fraction) / oxygen_ambient_air_mole_fraction
        )
        assert OpenLotCbpbCalculator.calculate_anaerobic_effect(
            oxygen_mole_fraction=oxygen_mole_fraction,
            oxygen_ambient_air_mole_fraction=oxygen_ambient_air_mole_fraction,
        ) == pytest.approx(expected)


@pytest.mark.parametrize("temperature", [-10.0, 0.0, 10.0])
def test_calculate_microbial_decomp_rate(temperature: float) -> None:
    """Tests _microbial_decomp_rate() in calculator.py."""
    assert OpenLotCbpbCalculator.calculate_microbial_decomp_rate(temperature) == pytest.approx(
        2.37e-3 * (math.pow(1.066, (temperature - 10)) - math.pow(1.21, (temperature - 50)))
    )
