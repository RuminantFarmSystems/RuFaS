import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.non_water_uptake import NonWaterUptake
from tests.soil_crop_tests.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.mark.parametrize("depths,nutrients", [([0.5, 1, 10, 20], [0.5, 0.8, 5, 10])])
def test_uptake_nutrient(
    depths: list[float], nutrients: list[float], mocker: MockerFixture, mock_crop_data: CropData
) -> None:
    mock_crop_data.root_depth = 35
    incorp = NonWaterUptake(mock_crop_data, potential_nutrient_uptake=17.5, nutrient_distro_param=0.32)

    mock_find_deepest_accessible_soil_layer = mocker.patch.object(
        incorp, "find_deepest_accessible_soil_layer", return_value=None
    )
    mocker.patch.object(incorp, "access_layers", return_value=[1, 2, 3])
    mock_determine_layer_nutrient_uptake_potential = mocker.patch.object(
        incorp, "determine_layer_nutrient_uptake_potential", return_value=[3.25, 6.33, 7.10]
    )
    mock_determine_layer_nutrient_demands = mocker.patch.object(
        incorp, "determine_layer_nutrient_demands", return_value=[12, 15, 17]
    )
    mock_determine_layer_nutrient_uptake = mocker.patch.object(
        incorp, "determine_layer_nutrient_uptake", return_value=[8.9, 9.9, 13.12]
    )
    mock_determine_layer_extracted_resource = mocker.patch.object(
        incorp, "determine_layer_extracted_resource", return_value=[5.0, 4.0, 2.0]
    )
    mock_extend_nutrient_uptakes_to_full_profile = mocker.patch.object(
        incorp, "extend_nutrient_uptakes_to_full_profile"
    )
    mock_extract_nutrient_from_soil_layers = mocker.patch.object(incorp, "extract_nutrient_from_soil_layers")
    mock_tally_total_nutrient_uptake = mocker.patch.object(incorp, "tally_total_nutrient_uptake")

    incorp.uptake_nutrient(nutrients, depths)

    mock_find_deepest_accessible_soil_layer.assert_called_once_with(depths)
    mock_determine_layer_nutrient_uptake_potential.assert_called_once_with([1, 2, 3], 17.5, 35.0, 0.32)
    assert incorp.layer_nutrient_potentials == [3.25, 6.33, 7.10]
    mock_determine_layer_nutrient_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.unmet_nutrient_demands == [12, 15, 17]
    mock_determine_layer_nutrient_uptake.assert_called_once_with([12, 15, 17], [3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.nutrient_requests == [8.9, 9.9, 13.12]
    mock_determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert incorp.actual_nutrient_uptakes == [5.0, 4.0, 2.0]
    mock_extend_nutrient_uptakes_to_full_profile.assert_called_once()
    mock_extract_nutrient_from_soil_layers.assert_called_once()
    mock_tally_total_nutrient_uptake.assert_called_once()


@pytest.mark.parametrize(
    "old,new",
    [
        (None, 1),  # no start
        (0, 1),  # start = 0
        (1, 2),  # start = 0
        (2, 1),  # start > new
        (133.26, 149.4),  # arbitrary
    ],
)
def test_shift_nutrient_time(old: float | None, new: float, mock_crop_data: CropData) -> None:
    """Ensure shift_nutrient_time correctly copies current nutrient value to previous_nutrient."""
    incorp = NonWaterUptake(mock_crop_data, previous_nutrient=old)
    incorp.shift_nutrient_time(new)
    assert incorp.previous_nutrient == new
