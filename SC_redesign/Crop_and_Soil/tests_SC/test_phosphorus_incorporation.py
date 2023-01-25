import pytest

from SC_redesign.Crop_and_Soil.crop.phosphorus_incorporation import PhosphorusIncorporation
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData


@pytest.mark.parametrize("old,new", [
    (None, 1),  # no start
    (0, 1),  # start = 0
    (1, 2),  # start = 0
    (2, 1),  # start > new
    (133.26, 149.4)  # arbitrary
])
def test_shift_phosphorus_time(old, new):
    data = CropData(previous_phosphorus=old, phosphorus=new)
    incorp = PhosphorusIncorporation(data)
    incorp.shift_phosphorus_time()
    assert data.previous_phosphorus == new
    pass


def test_find_deepest_accessible_soil_layer():
    pass


def test_access_layers():
    pass


def test_extract_phosphorus_from_soil_layers():
    pass


def test_tally_total_phosphorus_uptake():
    pass


def test_uptake_phosphorus():
    pass


def test_incorporate_phosphorus():
    pass
