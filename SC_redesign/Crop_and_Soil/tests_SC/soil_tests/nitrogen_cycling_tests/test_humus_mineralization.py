import pytest
from unittest.mock import MagicMock, PropertyMock, patch

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.humus_mineralization import HumusMineralization
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL


# --- Static method tests ---
@pytest.mark.parametrize("active,stable", [
    (12, 5),
    (1.8, 15),
    (4, 4),
    (0, 6),
    (7, 0),
    (0, 0)
])
def test_determine_intra_organic_mineralization(active: float, stable: float) -> None:
    """Tests that the amount of nitrogen determined to be transferred from the active organic to stable organic pool are
        calculated correctly."""
    observed = HumusMineralization._determine_intra_organic_mineralization(active, stable)
    expect = (10 ** (-5)) * active * ((1 / FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL) - 1) - stable
    if expect > 0:
        expect = min(active, expect)
    elif expect < 0:
        expect = max(-1 * stable, expect)
    assert observed == expect


@pytest.mark.parametrize("active,temp_factor,water_factor,mineralization_rate", [
    (13, 0.1, 0.05, 0.0003),
    (10.91, 0.334, 0.112, 0.0003),
    (23.445, 0.7754, 0.4461, 0.00028),
])
def test_determine_organic_to_nitrate_mineralization(active: float, temp_factor: float, water_factor: float,
                                                     mineralization_rate: float) -> float:
    """Tests that the correct amount of active organic nitrogen mineralized is calculated."""
    observed = HumusMineralization._determine_organic_to_nitrate_mineralization(active, temp_factor, water_factor,
                                                                                mineralization_rate)
    expected = mineralization_rate * (temp_factor * water_factor) ** 0.5 * active
    assert observed == expected


# --- Main routine test ---
@pytest.mark.parametrize("active_to_stable,active_to_nitrate", [
    (3, 2),
    (0, 0),
    (2, 6),
    (-4, 4)
])
def test_mineralize_organic_nitrogen(active_to_stable: float, active_to_nitrate: float) -> None:
    """Tests that the main routine of HumusMineralization correctly transfers nitrogen between the right pools."""
    layer = LayerData(top_depth=0, bottom_depth=20, field_size=1.5)
    soil = SoilData(soil_layers=[layer], field_size=1.5)
    incorp = HumusMineralization(soil)
    incorp.data.soil_layers[0].active_organic_nitrogen_content = 15
    incorp.data.soil_layers[0].stable_organic_nitrogen_content = 12
    incorp.data.soil_layers[0].nitrate_content = 25
    incorp.data.soil_layers[0].humus_mineralization_rate_factor = 0.00035

    incorp._determine_intra_organic_mineralization = MagicMock(return_value=active_to_stable)
    incorp._determine_organic_to_nitrate_mineralization = MagicMock(return_value=active_to_nitrate)
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData",
                        nutrient_cycling_temp_factor=PropertyMock(return_value=0.5),
                        nutrient_cycling_water_factor=PropertyMock(return_value=0.4)):
        incorp.mineralize_organic_nitrogen()

        incorp._determine_intra_organic_mineralization.assert_called_once_with(15, 12)
        incorp._determine_organic_to_nitrate_mineralization.assert_called_once_with(15 - active_to_stable, 0.5, 0.4,
                                                                                    0.00035)
        assert incorp.data.soil_layers[0].active_organic_nitrogen_content == 15 - active_to_stable - active_to_nitrate
        assert incorp.data.soil_layers[0].stable_organic_nitrogen_content == 12 + active_to_stable
        assert incorp.data.soil_layers[0].nitrate_content == 25 + active_to_nitrate
