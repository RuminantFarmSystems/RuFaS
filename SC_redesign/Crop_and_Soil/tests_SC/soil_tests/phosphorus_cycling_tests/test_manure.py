import pytest
from math import exp, sqrt

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.manure import Manure


# --- Static Method tests ---
@pytest.mark.parametrize("avg_air_temp", [
    10,
    33,
    0,
    -14,
    18.34580983290,
])
def test_determine_temperature_factor(avg_air_temp: float) -> None:
    """Tests that the temperature factor is correctly calculated and bounded."""
    observe = Manure._determine_temperature_factor(avg_air_temp)
    expect = min(1, max(0, (2 * 32 ** 2 * avg_air_temp ** 2 - avg_air_temp ** 4) / 32 ** 4))
    assert observe == expect


@pytest.mark.parametrize("temp_factor", [
    0.0,
    1.0,
    0.4,
    0.8884959312,
])
def test_determine_dry_matter_decomposition_rate(temp_factor: float) -> None:
    """Tests that the dry matter decomposition rate is calculated correctly for a given day."""
    observe = Manure.determine_dry_matter_decomposition_rate(temp_factor)
    expect = 0.003 * temp_factor ** 0.5
    assert observe == expect


@pytest.mark.parametrize("moisture,temp_factor,area,is_dung", [
    [0.4, 0.3, 1, False],
    [0.8, 0.1, 3.18, True],
    [0.2, 0.187, 2.854, False],
    [0.552, 0.87, 0.875, True],
])
def test_determine_dry_manure_matter_assimilation(moisture: float, temp_factor: float, area: float,
                                                  is_dung: bool) -> None:
    """Tests that the correct amount of manure dry matter is assimilated into the soil on a given day is calculated
        correctly.
    """
    observe = Manure.determine_dry_manure_matter_assimilation(moisture, temp_factor, area, is_dung)
    if is_dung:
        expect = (30 * exp(3.5 * sqrt(moisture)) * (temp_factor ** 0.1) * area)
    else:
        expect = (30 * exp(2.5 * moisture)) * temp_factor * area
    assert observe == expect
