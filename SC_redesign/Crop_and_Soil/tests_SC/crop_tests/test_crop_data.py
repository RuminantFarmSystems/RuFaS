import pytest
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


@pytest.mark.parametrize("usr_index, expect", [
    (1.0, True),
    (None, False)
])
def test_given_harvest_index_property(usr_index, expect):
    """test the class knows if harvest index override is specified"""
    data = CropData(user_harvest_index=usr_index)
    assert data.do_harvest_index_override == expect
