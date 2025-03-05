import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.digester.anaerobic_digester import AnaerobicDigester


@pytest.mark.parametrize(
    "set_point, effluent_temp, influent_heat, heat_capacity, expected",
    [(20.0, 15.0, 1.8, 1.9, 9.25), (17.0, 22.0, 1.2, 1.8, -7.5)]
)
def test_calculate_specific_input_energy(mocker: MockerFixture, set_point: float, effluent_temp: float, influent_heat: float, heat_capacity: float, expected: float) -> None:
    """Test that the specific input energy of an Anaerobic Digester is calculated correctly."""
    mocker.patch.object(AnaerobicDigester, "_bind_influent_temperature", return_value=effluent_temp)
    mocker.patch.object(AnaerobicDigester, "_calculate_manure_heat_capacity", side_effect=[influent_heat, heat_capacity])

    actual = AnaerobicDigester._calculate_specific_input_energy(17.0, 0.93, set_point)

    assert actual == expected


@pytest.mark.parametrize("temp, expected", [(30.0, 30.0), (10.0, 10.0), (0.0, 4.0)])
def test_bind_influent_temperature(temp: float, expected: float) -> None:
    """Test that the influent temperature is bounded correctly."""
    actual = AnaerobicDigester._bind_influent_temperature(temp)

    assert actual == expected


@pytest.mark.parametrize("temp, moisture_frac, expected", [(20.0, 0.5, 1.84922), (5.0, 0.9, 1.98669)])
def test_calculate_manure_heat_capacity(temp: float, moisture_frac: float, expected: float) -> None:
    """Test that the heat capacity of manure is calculated correctly."""
    actual = AnaerobicDigester._calculate_manure_heat_capacity(temp, moisture_frac)

    assert actual == expected


@pytest.mark.parametrize("total_vol_sols, expected", [(100.0, 24.0), (0.0, 0.0)])
def test_calculate_CSTR_methane_volume(total_vol_sols: float, expected: float) -> None:
    """Test that the generated methane volume is calculated correctly."""
    actual = AnaerobicDigester._calculate_CSTR_methane_volume(total_vol_sols)

    assert actual == expected


@pytest.mark.parametrize(
    "methane, leakage, expected", [(0.0, 0.0, 0.0), (0.0, 0.2, 0.0), (100.0, 0.0, 0.0), (100.0, 0.25, 25.0)]
)
def test_calculate_methane_leakage(methane: float, leakage: float, expected: float) -> None:
    """Test that methane leakage is calculated correctly."""
    actual = AnaerobicDigester._calculate_methane_leakage(methane, leakage)

    assert actual == expected


@pytest.mark.parametrize("methane, expected", [(100.0, 5500.0), (0.0, 0.0)])
def test_calculate_methane_energy_content(methane: float, expected: float) -> None:
    """Test that the energy content of methane is calculated correctly."""
    actual = AnaerobicDigester._calculate_methane_energy_content(methane)

    assert actual == expected
