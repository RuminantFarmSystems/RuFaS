from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.routines.field.crop.phosphorus_incorporation import PhosphorusIncorporation
from RUFAS.routines.field.soil.soil_data import SoilData


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
def test_shift_phosphorus_time(old: float | None, new: float) -> None:
    """ensure shift_phosphorus_time correctly copies current phosphorus value to previous_phosphorus"""
    data = CropData(phosphorus=new)
    incorp = PhosphorusIncorporation(data, previous_phosphorus=old)
    incorp.shift_phosphorus_time()
    assert incorp.previous_phosphorus == new


@pytest.mark.parametrize("depths,phosphates", [([0.5, 1, 10, 20], [0.5, 0.8, 5, 10])])
def test_uptake_phosphorus(phosphates, depths):
    """check that uptake_phosphorus() correctly called functions and variables were updated as expected"""
    # initialize crop and run method
    data = CropData(root_depth=35.0)
    incorp = PhosphorusIncorporation(data, potential_phosphorus_uptake=17.5, phosphorus_distro_param=0.32)

    # Mock functions
    incorp.find_deepest_accessible_soil_layer = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[1, 2, 3])
    NutrientUptake.determine_layer_nutrient_uptake_potential = MagicMock(return_value=[3.25, 6.33, 7.10])
    NutrientUptake.determine_layer_nutrient_demands = MagicMock(return_value=[12, 15, 17])
    NutrientUptake.determine_layer_nutrient_uptake = MagicMock(return_value=[8.9, 9.9, 13.12])
    NutrientUptake.determine_layer_extracted_resource = MagicMock(return_value=[5.0, 4.0, 2.0])
    NutrientUptake.extend_nutrient_uptakes_to_full_profile = MagicMock()
    NutrientUptake.extract_nutrient_from_soil_layers = MagicMock()
    NutrientUptake.tally_total_nutrient_uptake = MagicMock()

    # run function
    incorp.uptake_phosphorus(phosphates, depths)

    # check assertions
    incorp.find_deepest_accessible_soil_layer.assert_called_once_with(depths)

    NutrientUptake.determine_layer_nutrient_uptake_potential.assert_called_once_with([1, 2, 3], 17.5, 35.0, 0.32)
    assert incorp.layer_phosphorus_potentials == [3.25, 6.33, 7.10]

    NutrientUptake.determine_layer_nutrient_demands.assert_called_once_with([3.25, 6.33, 7.10], [1, 2, 3])
    assert incorp.unmet_phosphorus_demands == [12, 15, 17]

    NutrientUptake.determine_layer_nutrient_uptake.assert_called_once_with(
        [12, 15, 17], [3.25, 6.33, 7.10], [1, 2, 3]
    )
    assert incorp.phosphorus_requests == [8.9, 9.9, 13.12]

    NutrientUptake.determine_layer_extracted_resource.assert_called_once_with([8.9, 9.9, 13.12], [1, 2, 3])
    assert incorp.actual_phosphorus_uptakes == [5.0, 4.0, 2.0]

    NutrientUptake.extend_nutrient_uptakes_to_full_profile.assert_called_once()
    NutrientUptake.extract_nutrient_from_soil_layers.assert_called_once()
    NutrientUptake.tally_total_nutrient_uptake.assert_called_once()


@pytest.mark.parametrize(
    "phosphates,depths,gate",
    [([0.5, 0.3, 0.2], [1, 2, 5], True), ([0.5, 0.3, 0.2], [1, 2, 5], False)],
)
def test_incorporate_phosphorus(phosphates: list[float], depths: list[float], gate: bool) -> None:
    """Check that incorporate_phosphorus() correctly called functions and variables were updated as expected."""
    # initialize object
    data = CropData(
        half_mature_heat_fraction=0.54,
        mature_heat_fraction=0.99,
        biomass=122.8,
        biomass_growth_max=999,
        emergence_phosphorus_fraction=0.71,
        half_mature_phosphorus_fraction=0.68,
        mature_phosphorus_fraction=0.60,
    )
    soil = SoilData(field_size=1.55)
    del soil.soil_layers[3]
    top_depths = [0] + depths[:2]
    soil.set_vectorized_layer_attribute("top_depth", top_depths)
    soil.set_vectorized_layer_attribute("bottom_depth", depths)
    soil.set_vectorized_layer_attribute("labile_inorganic_phosphorus_content", phosphates)
    incorp = PhosphorusIncorporation(
        data,
        previous_phosphorus=0,
    )

    # mock intermediate functions
    incorp.shift_phosphorus_time = MagicMock(return_value=None)
    NutrientUptake.determine_nutrient_shape_parameters = MagicMock(return_value=[1.2, 0.8])
    NutrientUptake.determine_optimal_nutrient_fraction = MagicMock(return_value=0.75)
    if gate:
        NutrientUptake.determine_optimal_nutrient = MagicMock(return_value=-268)
    else:
        NutrientUptake.determine_optimal_nutrient = MagicMock(return_value=268)
    NutrientUptake.determine_potential_nutrient_uptake = MagicMock(return_value=123.1)
    incorp.uptake_phosphorus = MagicMock(return_value=None)
    incorp.access_layers = MagicMock(return_value=[5, 10, 15.3])
    NutrientUptake.determine_stored_nutrient = MagicMock(return_value=99.3)

    # run method
    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=0.38):
        incorp.incorporate_phosphorus(soil)

    # assertions
    incorp.shift_phosphorus_time.assert_called_once()
    NutrientUptake.determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
    assert incorp.phosphorus_shapes == [1.2, 0.8]

    NutrientUptake.determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
    assert data.optimal_phosphorus_fraction == 0.75

    if gate:
        NutrientUptake.determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
        assert data.optimal_phosphorus == -268

        NutrientUptake.determine_potential_nutrient_uptake.assert_not_called()
        assert incorp.potential_phosphorus_uptake == 0
    else:
        assert data.optimal_phosphorus == 268
        NutrientUptake.determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
        assert incorp.potential_phosphorus_uptake == 123.1

    incorp.uptake_phosphorus.assert_called_once_with(phosphates, depths)
    NutrientUptake.determine_stored_nutrient.assert_called_once()  # should be called_once_with() w/ attr mocked
    assert data.phosphorus == 99.3
