import pytest

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.nitrification_volatilization import NitrificationVolatilization


# --- Static method tests ---
@pytest.mark.parametrize("temp", [
    20,
    31.493,
    14.334,
    5.0193
])
def test_calculate_nitrification_volatilization_temp_factor(temp: float) -> None:
    """Tests that the temperature factor used by the nitrification volatilization module is calculated correctly."""
    observed = NitrificationVolatilization._calculate_nitrification_volatilization_temp_factor(temp)
    expected = 0.41 * (temp - 5) / 10
    assert observed == expected


@pytest.mark.parametrize("water,wilting,field", [
    (3.55, 1.85, 6.559),
    (0.0, 1.22, 4.55712),
    (1.33, 2.22, 5.7781),
    (7.55, 2.314, 6.0133)
])
def test_calculate_nitrification_soil_water_factor(water: float, wilting: float, field: float) -> None:
    """Tests that the water factor for nitrification is calculated correctly."""
    observed = NitrificationVolatilization._calculate_nitrification_soil_water_factor(water, wilting, field)
    if water < 0.25 * field - 0.75 * wilting:
        expected = (water - wilting) / (0.25 * (field - wilting))
    else:
        expected = 1.0
    assert observed == expected
