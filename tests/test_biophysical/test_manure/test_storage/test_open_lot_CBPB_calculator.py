import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.open_lot_cbpb_calculator import OpenLotCbpbCalculator


def test_calculate_methane_conversion_factor() -> None:
    """Tests calculate_methane_conversion_factor()."""
    assert OpenLotCbpbCalculator.calculate_methane_conversion_factor(1.0) == -0.1875


def test_calculate_ifsm_methane_emission(mocker: MockerFixture) -> None:
    """Tests calculate_ifsm_methane_emission()."""
    mock_conversion_factor = mocker.patch.object(OpenLotCbpbCalculator,
        "calculate_methane_conversion_factor",
        return_value=1.0,
    )
    manure_volatile_solids = 1000.0
    expected = (manure_volatile_solids * 0.24 * 0.67 * 1.0) / 100

    actual = OpenLotCbpbCalculator.calculate_ifsm_methane_emission(manure_volatile_solids, 1.0)

    mock_conversion_factor.assert_called_once_with(1.0)
    assert actual == pytest.approx(expected)