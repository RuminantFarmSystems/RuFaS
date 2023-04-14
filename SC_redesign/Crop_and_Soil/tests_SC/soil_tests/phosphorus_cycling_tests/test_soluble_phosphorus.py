import pytest
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MEGAGRAMS_TO_KILOGRAMS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_LITERS
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


# --- Test helper methods ---
@pytest.mark.parametrize("runoff,field_size", [
    (1.3, 1.39),
    (2.56, 3.45),
    (0.35, 1.89),
])
def test_remove_runoff_phosphorus_from_top_soil(runoff: float, field_size: float) -> None:
    """Tests that the correct amount of phosphorus lost is calculated and removed."""
    data = SoilData()
    incorp = SolublePhosphorus(data)
    incorp.data.soil_layers[0].labile_phosphorus_content = 20

    incorp._determine_soil_phosphorus_concentration = MagicMock(return_value=100)

    incorp._remove_runoff_phosphorus_from_top_soil(runoff, field_size)
    expected_runoff_liters_per_ha = runoff * field_size * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_LITERS \
        / field_size
    expected_unadjusted_phosphorus_removed = 100 * 0.005 * expected_runoff_liters_per_ha * (1 / 1000_000)
    expected_actual_phosphorus_removed = min(20, expected_unadjusted_phosphorus_removed)
    expected_labile_phosphorus_left = 20 - expected_actual_phosphorus_removed
    expected_phosphorus_removed_in_kg = expected_actual_phosphorus_removed * field_size

    incorp._determine_soil_phosphorus_concentration.assert_called_once_with(20, incorp.data.soil_layers[0].bulk_density,
                                                                            incorp.data.soil_layers[0].layer_thickness)
    assert incorp.data.soil_layers[0].labile_phosphorus_content == expected_labile_phosphorus_left
    assert incorp.data.annual_soil_phosphorus_runoff == expected_phosphorus_removed_in_kg
