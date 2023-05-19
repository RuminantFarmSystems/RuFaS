import pytest
from unittest.mock import patch, PropertyMock
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


@pytest.mark.parametrize("frac,expect", [
    (0, False),
    (0.5, False),
    (1, True),
    (1.5, True)
])
def test_is_mature_property(frac, expect):
    """check that the is_mature property is properly assigning maturity by heat fraction"""
    data = CropData(heat_fraction=frac)
    assert data.is_mature == expect


@pytest.mark.parametrize("mature,dormant,alive,expected", [
    (False, False, False, False),
    (True, False, False, False),
    (True, True, False, False),
    (True, True, True, False),
    (True, False, True, False),
    (False, False, True, True)
])
def test_is_growing_property(mature: bool, dormant: bool, alive: bool, expected: bool) -> None:
    """Tests that crop's growth status is correctly determined."""
    with patch("SC_redesign.Crop_and_Soil.crop.crop_data.CropData.is_mature", new_callable=PropertyMock,
               return_value=mature):
        data = CropData(is_dormant=dormant, is_alive=alive)
        assert data.is_growing == expected


@pytest.mark.parametrize("usr_index, expect", [
    (1.0, True),
    (None, False)
])
def test_given_harvest_index_property(usr_index, expect):
    """test the class knows if harvest index override is specified"""
    data = CropData(user_harvest_index=usr_index)
    assert data.do_harvest_index_override == expect


@pytest.mark.parametrize("max_capacity,lai,max_lai", [
    (1.445, 0.55, 1.88),
    (2.88, 3.445, 4.5),
    (0.0, 1.8, 2.1),
    (2.3, 0.0, 2.9),
    (4.33, 3.7, 3.7)
])
def test_water_canopy_storage_capacity(max_capacity: float, lai: float, max_lai: float) -> None:
    """Tests that the current storage capacity of the canopy is correctly calculated."""
    data = CropData(max_canopy_water_capacity=max_capacity, leaf_area_index=lai, max_leaf_area_index=max_lai)
    actual = data.water_canopy_storage_capacity
    expected = max_capacity * lai / max_lai
    assert pytest.approx(actual) == expected
