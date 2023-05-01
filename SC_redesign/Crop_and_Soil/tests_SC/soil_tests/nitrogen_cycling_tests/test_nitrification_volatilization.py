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
