import pytest

from RUFAS.routines.field.crop.nitrogen_incorporation import NitrogenIncorporation
from RUFAS.routines.field.crop.phosphorus_incorporation import PhosphorusIncorporation
from RUFAS.routines.field.crop.crop_data import CropData
from unittest.mock import MagicMock, patch, PropertyMock

from RUFAS.routines.field.soil.soil_data import SoilData


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


@pytest.mark.parametrize("uptakes,phosphates", [
    ([1], [1]),  # start
    ([1], [0]),  # no nitrates
    ([0], [1]),  # no uptakes
    ([0.5], [1]),  # uptakes < nitrates
    ([1.2], [1]),  # uptakes > nitrates
    ([37.9, 40.2, 18.3], [100.5, 83.3, 30.7]),  # arbitrary - abundant nitrates
    ([87.36, 86.40, 30.33], [82.4, 83.0, 29.9]),  # nitrates limited
    ([57.33, 32.20, 0], [40.2, 99.0, 30.7]),  # no uptake from last layer
])
def test_cd_phosphorus_from_soil_layers(uptakes, phosphates):
    """check that layer_nitrates were correctly updated by extract_phosphorus_from_soil_layers"""
    nitrates_copy = phosphates.copy()
    data = CropData(actual_phosphorus_uptakes=uptakes)
    incorp = PhosphorusIncorporation(data)
    incorp.extract_phosphorus_from_soil_layers(phosphates)
    remaining = []

    for i in range(len(uptakes)):
        remaining.append(max(nitrates_copy[i] - uptakes[i], 0))
    assert phosphates == remaining


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


@pytest.mark.parametrize("layers", (0, 3))
def test_extend_phosphate_uptakes_to_full_profile(layers: int) -> None:
    """Checks that the helper method extend_phosphate_uptakes_to_full_profile() does correctly updates the list to the
    right length"""
    data = CropData(actual_phosphorus_uptakes=[1.0, 2.0, 3.0], inaccessible_soil_layers=layers)
    incorp = PhosphorusIncorporation(data)
    pre_actual_phosphorus = data.actual_phosphorus_uptakes
    incorp.extend_phosphate_uptakes_to_full_profile()

    if layers > 0:
        pre_actual_phosphorus += [0] * layers
        assert data.actual_phosphorus_uptakes == pre_actual_phosphorus
    else:
        assert data.actual_phosphorus_uptakes == pre_actual_phosphorus


@pytest.mark.parametrize("depths,phosphates", [
    ([.5, 1, 10, 20], [0.5, 0.8, 5, 10])
])
def test_uptake_phosphorus(phosphates, depths):
    """check that uptake_phosphorus() correctly called functions and variables were updated as expected"""
    # initialize crop and run method
    data = CropData(potential_phosphorus_uptake=17.5, root_depth=35.0, phosphorus_distro_param=0.32)
    incorp = PhosphorusIncorporation(data)

    # Mock functions
    incorp.find_deepest_accessible_soil_layer = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[1, 2, 3])
    NitrogenIncorporation.determine_layer_nutrient_uptake_potential = MagicMock(return_value=[3.25, 6.33, 7.10])
    NitrogenIncorporation.determine_layer_nutrient_demands = MagicMock(return_value=[12, 15, 17])
    NitrogenIncorporation.determine_layer_nutrient_uptake = MagicMock(return_value=[8.9, 9.9, 13.12])
    NitrogenIncorporation.determine_layer_extracted_resource = MagicMock(return_value=[5.0, 4.0, 2.0])
    incorp.extend_phosphate_uptakes_to_full_profile = MagicMock()
    incorp.extract_phosphorus_from_soil_layers = MagicMock()
    incorp.tally_total_phosphorus_uptake = MagicMock()

    # run function
    incorp.uptake_phosphorus(phosphates, depths)

    # check assertions
    incorp.find_deepest_accessible_soil_layer.assert_called_once_with(depths)

    NitrogenIncorporation.determine_layer_nutrient_uptake_potential.assert_called_once_with([1, 2, 3],
                                                                                            17.5, 35.0, 0.32)
    assert data.layer_phosphorus_potentials == [3.25, 6.33, 7.10]

    NitrogenIncorporation.determine_layer_nutrient_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert data.unmet_phosphorus_demands == [12, 15, 17]

    NitrogenIncorporation.determine_layer_nutrient_uptake.assert_called_once_with([12, 15, 17], [3.25, 6.33, 7.10],
                                                                                  [1, 2, 3])
    assert data.phosphorus_requests == [8.9, 9.9, 13.12]

    NitrogenIncorporation.determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert data.actual_phosphorus_uptakes == [5.0, 4.0, 2.0]

    incorp.extend_phosphate_uptakes_to_full_profile.assert_called_once()
    incorp.extract_phosphorus_from_soil_layers.assert_called_once()
    incorp.tally_total_phosphorus_uptake.assert_called_once()


@pytest.mark.parametrize("phosphates,depths,gate", [
    ([.5, .3, .2], [1, 2, 5], True),
    ([.5, .3, .2], [1, 2, 5], False)
])
def test_incorporate_phosphorus(phosphates: list[float], depths: list[float], gate: bool) -> None:
    """Check that incorporate_phosphorus() correctly called functions and variables were updated as expected."""
    # initialize object
    data = CropData(half_mature_heat_fraction=.54, mature_heat_fraction=0.99, emergence_phosphorus_fraction=0.71,
                    half_mature_phosphorus_fraction=0.68, near_mature_phosphorus_fraction=0.62,
                    mature_phosphorus_fraction=0.60, biomass=122.8, previous_phosphorus=0, biomass_growth_max=999)
    soil = SoilData(field_size=1.55)
    del soil.soil_layers[3]
    top_depths = [0] + depths[:2]
    soil.set_vectorized_layer_attribute("top_depth", top_depths)
    soil.set_vectorized_layer_attribute("bottom_depth", depths)
    soil.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", phosphates)
    incorp = PhosphorusIncorporation(data)

    # mock intermediate functions
    incorp.shift_phosphorus_time = MagicMock(return_value=None)
    NitrogenIncorporation.determine_nutrient_shape_parameters = MagicMock(return_value=[1.2, 0.8])
    NitrogenIncorporation.determine_optimal_nutrient_fraction = MagicMock(return_value=0.75)
    if gate:
        NitrogenIncorporation.determine_optimal_nutrient = MagicMock(return_value=-268)
    else:
        NitrogenIncorporation.determine_optimal_nutrient = MagicMock(return_value=268)
    NitrogenIncorporation.determine_potential_nutrient_uptake = MagicMock(return_value=123.1)
    incorp.uptake_phosphorus = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[5, 10, 15.3])
    NitrogenIncorporation.determine_stored_nutrient = MagicMock(return_value=99.3)

    # run method
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=0.38):
        incorp.incorporate_phosphorus(soil)

    # assertions
    incorp.shift_phosphorus_time.assert_called_once()
    NitrogenIncorporation.determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
    assert data.phosphorus_shapes == [1.2, 0.8]

    NitrogenIncorporation.determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
    assert data.optimal_phosphorus_fraction == 0.75

    if gate:
        NitrogenIncorporation.determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
        assert data.optimal_phosphorus == -268

        NitrogenIncorporation.determine_potential_nutrient_uptake.assert_not_called()
        assert data.potential_phosphorus_uptake == 0
    else:
        assert data.optimal_phosphorus == 268
        NitrogenIncorporation.determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
        assert data.potential_phosphorus_uptake == 123.1

    incorp.uptake_phosphorus.assert_called_once_with(phosphates, depths)
    NitrogenIncorporation.determine_stored_nutrient.assert_called_once()  # should be called_once_with() w/ attr mocked
    assert data.phosphorus == 99.3
