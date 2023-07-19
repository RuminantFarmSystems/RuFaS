import pytest
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData, PlantCategory


# --- Static function tests ---
@pytest.mark.parametrize("min_daylength,dormancy_threshold", [
    (16, 17),
    (0, 0),
    (14, 17),
    (16.218347349, 16.329438502)
])
def test_find_threshold_daylength(min_daylength: float, dormancy_threshold: float) -> None:
    """Tests that the dormancy threshold daylength is calculated correctly."""
    observe = Dormancy.find_threshold_daylength(min_daylength, dormancy_threshold)
    expect = min_daylength + dormancy_threshold
    assert observe == expect


@pytest.mark.parametrize("latitude", [
    40,
    28,
    8,
    17.9238487592,
    56.2948349202,
])
def test_find_dormancy_threshold(latitude: float) -> None:
    """Tests that the dormancy threshold is correctly calculated based on the latitude."""
    observe = Dormancy.find_dormancy_threshold(latitude)
    if latitude > 40:
        expect = 1
    elif 20 <= latitude <= 40:
        expect = (latitude - 20) / 20
    else:
        expect = 0
    assert observe == expect


# --- Integration tests ---
@pytest.mark.parametrize("biomass,residue,lai,min_lai,plant_type,loss_frac,is_dormant", [
    (800, 150, 0.87, 0.75, PlantCategory("perennial"), 0.1, False),               # Perennial with defaults
    (2000, 70, 0.91, 0.56, PlantCategory("tree"), 0.3, False),                    # Tree with tree defaults
    (1100, 210, 0.78, 0.3, PlantCategory("cool_annual"), 0.3, False),           # Cool annual
    (980, 145, 0.8891, None, PlantCategory("warm_annual_legume"), None, False),   # should not go into dormancy at all
    (1100, 210, 0.78, 0.3, PlantCategory("cool_annual"), 0.3, True),  # check is_dormant
])
def test_go_into_dormancy(biomass: float, residue: float, lai: float, min_lai: float, plant_type: PlantCategory,
                          loss_frac: float, is_dormant: bool) -> None:
    """Tests that crops are correctly set to be dormant, and when set to being dormant lose the correct
         amount of biomass and have their leaf area index reset to the correct value.
    """
    data = CropData(biomass=biomass, yield_residue=residue, leaf_area_index=lai, minimum_lai_during_dormancy=min_lai,
                    plant_category=plant_type, dormancy_loss_fraction=loss_frac, is_dormant=is_dormant)
    incorp = Dormancy(data)
    pre_biomass = incorp.data.biomass
    pre_yield_residue = incorp.data.yield_residue
    pre_leaf_area_index = incorp.data.leaf_area_index
    pre_dormant = incorp.data.is_dormant

    incorp.enter_dormancy()

    if incorp.data.plant_category == PlantCategory.WARM_ANNUAL_LEGUME or \
            incorp.data.plant_category == PlantCategory.WARM_ANNUAL:
        assert incorp.data.biomass == pre_biomass
        assert incorp.data.yield_residue == pre_yield_residue
        assert incorp.data.leaf_area_index == pre_leaf_area_index
    elif pre_dormant:
        assert incorp.data.biomass == pre_biomass
        assert incorp.data.yield_residue == pre_yield_residue
        assert incorp.data.leaf_area_index == pre_leaf_area_index
    else:
        assert incorp.data.is_dormant is True
        if incorp.data.plant_category == PlantCategory.PERENNIAL or \
                incorp.data.plant_category == PlantCategory.PERENNIAL_LEGUME or \
                incorp.data.plant_category == PlantCategory.TREE:
            assert incorp.data.biomass == (biomass * (1 - loss_frac))
            assert incorp.data.yield_residue == (residue + (biomass * loss_frac))
            assert incorp.data.leaf_area_index == min(lai, min_lai)
