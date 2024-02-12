import pytest
from RUFAS.routines.EEE.tractor import TractorSpecs, TractorSize


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
def test_herd_size_to_tractor_size(herd_size, expected_size):
    specs = TractorSpecs(None, herd_size)
    assert specs.tractor_size == expected_size


@pytest.mark.parametrize("tractor_size", list(TractorSize))
def test_tractor_size_initialization(tractor_size):
    specs = TractorSpecs(tractor_size, None)
    assert specs.tractor_size == tractor_size


def test_raises_value_error_for_missing_parameters():
    with pytest.raises(ValueError):
        TractorSpecs(None, None)


@pytest.mark.parametrize("herd_size", [-1, -100])
def test_herd_size_negative_value_error(herd_size):
    with pytest.raises(ValueError):
        TractorSpecs(None, herd_size)


@pytest.mark.parametrize(
    "tractor_size, expected_pto_kW",
    [
        (TractorSize.SMALL, 55.93),
        (TractorSize.MEDIUM, 208.42),
        (TractorSize.LARGE, 328.11),
    ],
)
def test_pto_kW(tractor_size, expected_pto_kW):
    specs = TractorSpecs(tractor_size, None)
    assert specs.PTO_kW == expected_pto_kW


@pytest.mark.parametrize(
    "tractor_size, expected_power_available_kW",
    [
        (TractorSize.SMALL, 55.93 / 1.4),
        (TractorSize.MEDIUM, 208.42 / 1.4),
        (TractorSize.LARGE, 328.11 / 1.4),
    ],
)
def test_power_available_kW(tractor_size, expected_power_available_kW):
    specs = TractorSpecs(tractor_size, None)
    assert specs.power_available_kW == expected_power_available_kW


@pytest.mark.parametrize(
    "tractor_size, expected_mass_kg",
    [
        (TractorSize.SMALL, 8400.0),
        (TractorSize.MEDIUM, 12700.0),
        (TractorSize.LARGE, 20856.0),
    ],
)
def test_mass_kg(tractor_size, expected_mass_kg):
    specs = TractorSpecs(tractor_size, None)
    assert specs.mass_kg == expected_mass_kg


def test_speed_km_hr():
    specs = TractorSpecs(TractorSize.SMALL, None)  # Any tractor size would do
    assert specs.speed_km_hr == 10.0
