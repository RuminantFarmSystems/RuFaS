from SC_redesign.Crop_and_Soil.crop.crop import Crop
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
import pytest
from unittest.mock import MagicMock


@pytest.mark.parametrize("in_growing_system", [
    True,
    False
])
def test_grow_crop(in_growing_system: bool) -> None:
    mocked_soil_data = MagicMock(SoilData)
    mocked_crop_data = MagicMock(CropData)
    CropData.in_growing_season = MagicMock(return_value=in_growing_system)
    crop = Crop(crop_data=mocked_crop_data)
    crop.heat_units.absorb_heat_units = MagicMock()
    crop.root_development.develop_roots = MagicMock()
    crop.nitrogen_incorporation.incorporate_nitrogen = MagicMock()
    crop.phosphorus_incorporation.incorporate_phosphorus = MagicMock()
    crop.growth_constraints.constrain_growth = MagicMock()
    crop.leaf_area_index.grow_canopy = MagicMock()
    crop.biomass_allocation.allocate_biomass = MagicMock()
    crop.grow_crop(mocked_soil_data, 2, 2, 2, 2)
    if not CropData.in_growing_season:
        assert crop.heat_units.absorb_heat_units.call_count == 0
        assert crop.root_development.develop_roots.call_count == 0
        assert crop.nitrogen_incorporation.incorporate_nitrogen.call_count == 0
        assert crop.phosphorus_incorporation.incorporate_phosphorus.call_count == 0
        assert crop.growth_constraints.constrain_growth.call_count == 0
        assert crop.leaf_area_index.grow_canopy.call_count == 0
        assert crop.biomass_allocation.allocate_biomass.call_count == 0
    else:
        assert crop.heat_units.absorb_heat_units.call_count == 1
        assert crop.root_development.develop_roots.call_count == 1
        assert crop.nitrogen_incorporation.incorporate_nitrogen.call_count == 1
        assert crop.phosphorus_incorporation.incorporate_phosphorus.call_count == 1
        assert crop.growth_constraints.constrain_growth.call_count == 1
        assert crop.leaf_area_index.grow_canopy.call_count == 1
        assert crop.biomass_allocation.allocate_biomass.call_count == 1

