import pytest

from SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation import NitrogenIncorporation
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
    """ensure shift_phosphorus_time correctly copies current phosphorus value to previous_phosphorus"""
    data = CropData(previous_phosphorus=old, phosphorus=new)
    incorp = PhosphorusIncorporation(data)
    incorp.shift_phosphorus_time()
    assert data.previous_phosphorus == new


@pytest.mark.parametrize("root_depth,depths,expect", [
    (1.5, [0, 1, 2, 3], [4, 1]),
    (2.6, [0, 1, 2, 3], [4, 0]),
    (0.3, [0, 0.5, 1, 2, 3], [5, 3]),
    (28.4, [18.2, 21.6, 100.4], [3, 0])
])
def test_phosphorus_determine_deepest_accessible_soil_layer(root_depth, depths, expect):
    """ensure that layers are partitioned correctly by determine_deepest_accessible_soil_layer"""
    data = CropData(root_depth=root_depth)
    incorp = PhosphorusIncorporation(data)
    incorp.find_deepest_accessible_soil_layer(depths)
    assert data.total_soil_layers == expect[0]
    assert data.accessible_soil_layers == NitrogenIncorporation.determine_deepest_accessible_layer(root_depth, depths)
    assert data.inaccessible_soil_layers == expect[1]


@pytest.mark.parametrize("deepest,layers", [
    (1, [1, 2, 3, 4]),  # one layer
    (2, [1, 2, 3, 4]),  # two layers
    (3, [1, 2, 3, 4]),  # three layers
    (4, [1, 2, 3, 4]),  # four layers
    (2, [22.5, 80.6, 100.0, 199.9]),  # arbitrary list
])
def test_access_layers(deepest, layers):
    data = CropData(accessible_soil_layers=deepest)
    incorp = PhosphorusIncorporation(data)
    assert incorp.access_layers(layers) == layers[slice(deepest)]


def test_extract_phosphorus_from_soil_layers():
    pass


def test_tally_total_phosphorus_uptake():
    pass


def test_uptake_phosphorus():
    pass


def test_incorporate_phosphorus():
    pass
