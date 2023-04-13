import pytest

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus


# --- Static method tests ---
@pytest.mark.parametrize("percent_clay", [
    99.1,
    55.42,
    9.13,
    0.0,
])
def test_determine_isotherm_slope(percent_clay: float) -> None:
    """Tests that the slope of the phosphorus sorption isotherm is calculated correctly."""
    observed = SolublePhosphorus._determine_isotherm_slope(percent_clay)
    expected = (173.51 * (percent_clay / 100)) + 8.48
    assert observed == expected


@pytest.mark.parametrize("slope", [
    8.48,
    158.28,
    34.183,
    94.13,
])
def test_determine_isotherm_intercept(slope: float) -> None:
    """Tests that the intercept of the phosphorus sorption isotherm is calculated correctly."""
    observed = SolublePhosphorus._determine_isotherm_intercept(slope)
    expected = (4.726 * slope) - 8.97
    assert observed == expected
