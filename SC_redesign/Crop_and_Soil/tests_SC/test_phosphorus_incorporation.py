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
    """check that soil layers are accessed correctly with access_layers()"""
    data = CropData(accessible_soil_layers=deepest)
    incorp = PhosphorusIncorporation(data)
    assert incorp.access_layers(layers) == layers[slice(deepest)]


@pytest.mark.parametrize("uptakes,nitrates", [
    ([1], [1]),  # start
    ([1], [0]),  # no nitrates
    ([0], [1]),  # no uptakes
    ([0.5], [1]),  # uptakes < nitrates
    ([1.2], [1]),  # uptakes > nitrates
    ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
    ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
    ([57.33, 32.20, 0], [40.2, 99.0, 30.7]),  # no uptake from last layer
])
def test_cd_phosphorus_from_soil_layers(uptakes, nitrates):
    """check that layer_nitrates were correctly updated by extract_phosphorus_from_soil_layers"""
    nitrates_copy = nitrates.copy()
    data = CropData(actual_phosphorus_uptakes=uptakes)
    incorp = PhosphorusIncorporation(data)
    incorp.extract_phosphorus_from_soil_layers(nitrates)
    remaining = []

    for i in range(len(uptakes)):
        remaining.append(max(nitrates_copy [i] - uptakes[i], 0))
    assert nitrates == remaining


@pytest.mark.parametrize("uptakes", [
    [1],  # one layer
    [1, 1, 1, 1],  # four layers
    [81.2, 0],  # arbitrary with zero
    [15.3, 18.2, 4, 20.33]
])
def test_tally_total_phosphorus_uptake(uptakes):
    """check that total phosphorus was correctly summed by tally_total_phosphorus_uptake"""
    data = CropData(actual_phosphorus_uptakes=uptakes)
    incorp = PhosphorusIncorporation(data)
    incorp.tally_total_phosphorus_uptake()
    assert data.total_phosphorus_uptake == sum(uptakes)


def test_uptake_phosphorus():

    pass


def test_incorporate_phosphorus():
    pass
