import pytest
from unittest.mock import patch
from RUFAS.routines.EEE.tractor import Tractor
from RUFAS.routines.EEE.enums import TractorSize, FieldOperationEvent


@pytest.mark.parametrize(
    "herd_size, expected_size",
    [
        (100, TractorSize.SMALL),
        (500, TractorSize.MEDIUM),
        (1500, TractorSize.MEDIUM),
        (2000, TractorSize.LARGE),
        (3000, TractorSize.LARGE),
    ],
)
@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_herd_size_to_tractor_size(_, herd_size, expected_size):
    specs = Tractor(FieldOperationEvent.TILLING, herd_size=herd_size)
    assert specs.tractor_size == expected_size


@pytest.mark.parametrize("tractor_size", list(TractorSize))
@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_tractor_size_initialization(_, tractor_size):
    specs = Tractor(None, tractor_size=tractor_size)
    assert specs.tractor_size == tractor_size


def test_raises_value_error_for_missing_parameters():
    with pytest.raises(ValueError):
        Tractor(None, None)


@pytest.mark.parametrize("herd_size", [-1, -100])
def test_herd_size_negative_value_error(herd_size):
    with pytest.raises(ValueError):
        Tractor(None, herd_size)


@pytest.mark.parametrize(
    "tractor_size, expected_pto_kW",
    [
        (TractorSize.SMALL, 55.93),
        (TractorSize.MEDIUM, 208.42),
        (TractorSize.LARGE, 328.11),
    ],
)
@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_pto_kW(mock_get_data, tractor_size, expected_pto_kW):
    mock_get_data.return_value = [
        {"ID": 589, "Value": 55.93},
        {"ID": 592, "Value": 208.42},
        {"ID": 595, "Value": 328.11},
    ]
    specs = Tractor(None, tractor_size=tractor_size)
    assert specs.PTO_kW == expected_pto_kW


@pytest.mark.parametrize(
    "tractor_size, expected_power_available_kW",
    [
        (TractorSize.SMALL, 55.93 / 1.4),
        (TractorSize.MEDIUM, 208.42 / 1.4),
        (TractorSize.LARGE, 328.11 / 1.4),
    ],
)
@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_power_available_kW(mock_get_data, tractor_size, expected_power_available_kW):
    mock_get_data.return_value = [
        {"ID": 589, "Value": 55.93},
        {"ID": 592, "Value": 208.42},
        {"ID": 595, "Value": 328.11},
    ]
    specs = Tractor(None, tractor_size=tractor_size)
    assert specs.power_available_kW == expected_power_available_kW


@pytest.mark.parametrize(
    "tractor_size, expected_mass_kg",
    [
        (TractorSize.SMALL, 8400.0),
        (TractorSize.MEDIUM, 12700.0),
        (TractorSize.LARGE, 20856.0),
    ],
)
@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_mass_kg(mock_get_data, tractor_size, expected_mass_kg):
    mock_get_data.return_value = [
        {"ID": 591, "Value": 8400.0},
        {"ID": 594, "Value": 12700.0},
        {"ID": 597, "Value": 20856.0},
    ]
    specs = Tractor(None, tractor_size=tractor_size)
    assert specs.mass_kg == expected_mass_kg


@patch("RUFAS.routines.EEE.tractor.InputManager.get_data")
def test_speed_km_hr(mock_get_data):
    mock_get_data.return_value = [{"ID": 598, "Value": 10.0}]
    specs = Tractor(None, tractor_size=TractorSize.SMALL)  # Any tractor size would do
    assert specs.speed_km_hr == 10.0
