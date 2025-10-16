import pytest

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.nitrogen_uptake import NitrogenUptake
from RUFAS.biophysical.field.crop.nutrient_uptake import NutrientUptake
from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.mark.parametrize(
    "pots,avails",
    [
        ([0.5, 0.25, 0.05], [0.3, 0.2, 0.01]),
        ([0.5, 0.25, 0.05], [0.6, 0.3, 0.06]),  # abundant nitrates
        ([0.5, 0.25, 0.05], [0, 0, 0]),  # no nitrates
        ([0.5, 0.25, 0.05, 0.01], [0.3, 0.2, 0.01, 0.01]),  # 4 layers
        ([0.5, 0.25, 0.05], [0.5, 0.25, 0.05]),  # exactly met demands
        ([112.3, 50.44, 17, 12.99], [50.33, 15.10, 8.05, 6.66]),  # arbitrary
    ],
)
def test_determine_layer_nutrient_demands(pots: list[float], avails: list[float]) -> None:
    """Test that nutrient demand is correctly calculated for each layer by determine_layer_nitrogen_demand()."""
    observe = NutrientUptake.determine_layer_nutrient_demands(pots, avails)
    no3_sum = 0
    up_sum = 0
    demand_list = []
    for pot_up, no3 in zip(pots, avails):
        demand = up_sum - no3_sum
        demand = max(demand, 0)
        demand_list.append(demand)
        up_sum += pot_up
        no3_sum += no3
    assert demand_list == pytest.approx(observe, rel=0.00001)


@pytest.mark.parametrize(
    "uptakes",
    [
        [1],  # one layer
        [1, 1, 1, 1],  # four layers
        [81.2, 0],  # arbitrary with zero
        [15.3, 18.2, 4, 20.33],
    ],
)
def test_tally_total_nutrient_uptake(uptakes: list[float], mock_crop_data: CropData) -> None:
    """Check that total nutrient is correctly calculated by tally_total_nutrient_uptake()."""
    incorp = NitrogenUptake(mock_crop_data)
    result = incorp.tally_total_nutrient_uptake(uptakes)
    assert result == sum(uptakes)
