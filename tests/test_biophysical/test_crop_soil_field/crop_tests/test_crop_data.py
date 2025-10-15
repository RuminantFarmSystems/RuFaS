from unittest.mock import PropertyMock, patch

import pytest

from RUFAS.biophysical.field.crop.crop_data import CropData, PlantCategory

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.mark.parametrize("frac,expect", [(0, False), (0.5, False), (1, True), (1.5, True)])
def test_is_mature_property(mock_crop_data: CropData, frac: float, expect: bool) -> None:
    """Check that the is_mature property is properly assigning maturity by heat fraction."""
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=frac):
        assert mock_crop_data.is_mature == expect


@pytest.mark.parametrize(
    "mature,dormant,alive,growing,expected",
    [
        (False, False, False, False, False),
        (True, False, False, True, False),
        (True, True, False, False, False),
        (True, True, True, True, False),
        (True, False, True, False, False),
        (False, False, True, True, True),
    ],
)
def test_in_growing_season_property(
    mock_crop_data: CropData, mature: bool, dormant: bool, alive: bool, growing: bool, expected: bool
) -> None:
    """Tests that crop's growth status is correctly determined."""
    with patch(
        "RUFAS.biophysical.field.crop.crop_data.CropData.is_mature",
        new_callable=PropertyMock,
        return_value=mature,
    ):
        mock_crop_data.is_dormant = dormant
        mock_crop_data.is_alive = alive
        mock_crop_data.is_growing = growing

        assert mock_crop_data.in_growing_season == expected


@pytest.mark.parametrize("usr_index, expect", [(1.0, True), (None, False)])
def test_given_harvest_index_property(mock_crop_data: CropData, usr_index: float | None, expect: bool) -> None:
    """Test the class knows if harvest index override is specified."""
    mock_crop_data.user_harvest_index = usr_index

    assert mock_crop_data.do_harvest_index_override == expect


@pytest.mark.parametrize(
    "max_capacity,lai,max_lai",
    [
        (1.445, 0.55, 1.88),
        (2.88, 3.445, 4.5),
        (0.0, 1.8, 2.1),
        (2.3, 0.0, 2.9),
        (4.33, 3.7, 3.7),
    ],
)
def test_water_canopy_storage_capacity(
    mock_crop_data: CropData, max_capacity: float, lai: float, max_lai: float
) -> None:
    """Tests that the current storage capacity of the canopy is correctly calculated."""
    mock_crop_data.max_canopy_water_capacity = max_capacity
    mock_crop_data.leaf_area_index = lai
    mock_crop_data.max_leaf_area_index = max_lai

    actual = mock_crop_data.water_canopy_storage_capacity

    expected = max_capacity * lai / max_lai
    assert pytest.approx(actual) == expected


def test_tree_dormancy_loss(mock_crop_data: CropData) -> None:
    """A separate test to check the dormancy loss for future use of TREE."""
    mock_crop_data.plant_category = PlantCategory.TREE
    mock_crop_data.__post_init__()

    assert mock_crop_data.dormancy_loss_fraction == 0.3


@pytest.mark.parametrize(
    "plant_type",
    [
        PlantCategory.PERENNIAL,
        PlantCategory.PERENNIAL_LEGUME,
        PlantCategory.TREE,
        PlantCategory.WARM_ANNUAL,
        PlantCategory.WARM_ANNUAL_LEGUME,
        PlantCategory.COOL_ANNUAL,
        PlantCategory.COOL_ANNUAL_LEGUME,
    ],
)
def test_is_perennial(mock_crop_data: CropData, plant_type: PlantCategory) -> None:
    """Tests that is_perennial() correctly determines whether a plant is a perennial"""
    mock_crop_data.plant_category = plant_type
    mock_crop_data.is_perennial = False
    mock_crop_data.__post_init__()

    # Determine observed and expected results
    observe = mock_crop_data.is_perennial
    perennial_set = {
        PlantCategory.PERENNIAL,
        PlantCategory.PERENNIAL_LEGUME,
        PlantCategory.TREE,
    }
    expect = plant_type in perennial_set

    # Check results
    assert observe == expect


@pytest.mark.parametrize(
    "accumulated,potential,expected",
    [(100, 800, 0.125), (0, 1200, 0.0), (1000, 800, 1.25), (900, 900, 1.0)],
)
def test_heat_fraction(mock_crop_data: CropData, accumulated: float, potential: float, expected: float) -> None:
    """Tests that the heat fraction is correctly calculated based on the heat units."""
    mock_crop_data.accumulated_heat_units = accumulated
    mock_crop_data.potential_heat_units = potential

    assert mock_crop_data.heat_fraction == expected
