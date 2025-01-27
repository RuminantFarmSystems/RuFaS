from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pytest_mock import MockerFixture

from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.nutrient_uptake import NutrientUptake
from RUFAS.routines.field.crop.phosphorus_uptake import PhosphorusUptake
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
    incorp = PhosphorusUptake(data, previous_nutrient=old)
    incorp.shift_phosphorus_time()
    assert incorp.previous_nutrient == new


@pytest.mark.parametrize(
    "phosphates,depths,gate",
    [([0.5, 0.3, 0.2], [1, 2, 5], True), ([0.5, 0.3, 0.2], [1, 2, 5], False)],
)
def test_incorporate_phosphorus(
    phosphates: list[float], depths: list[float], gate: bool, mocker: MockerFixture
) -> None:
    """Check that incorporate_phosphorus() correctly called functions and variables were updated as expected."""
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
    incorp = PhosphorusUptake(
        data,
        previous_nutrient=0,
    )

    incorp.shift_phosphorus_time = MagicMock(return_value=None)
    mock_determine_nutrient_shape_parameters = mocker.patch.object(
        NutrientUptake, "determine_nutrient_shape_parameters", return_value=[1.2, 0.8]
    )
    mock_determine_optimal_nutrient_fraction = mocker.patch.object(
        NutrientUptake, "determine_optimal_nutrient_fraction", return_value=0.75
    )
    if gate:
        mock_determine_optimal_nutrient = mocker.patch.object(
            NutrientUptake, "determine_optimal_nutrient", return_value=-268
        )
    else:
        mock_determine_optimal_nutrient = mocker.patch.object(
            NutrientUptake, "determine_optimal_nutrient", return_value=268
        )
    mock_determine_potential_nutrient_uptake = mocker.patch.object(
        NutrientUptake, "determine_potential_nutrient_uptake", return_value=123.1
    )
    mock_uptake_phosphorus = mocker.patch.object(incorp, "uptake_nutrient", return_value=None)
    mocker.patch.object(incorp, "access_layers", return_value=[5, 10, 15.3])
    mock_determine_stored_nutrient = mocker.patch.object(NutrientUptake, "determine_stored_nutrient", return_value=99.3)

    with patch.object(CropData, "heat_fraction", new_callable=PropertyMock, return_value=0.38):
        incorp.incorporate_phosphorus(soil)

    incorp.shift_phosphorus_time.assert_called_once()
    mock_determine_nutrient_shape_parameters.assert_called_once_with(0.54, 0.99, 0.71, 0.68, 0.60)
    assert incorp.nutrient_shapes == [1.2, 0.8]

    mock_determine_optimal_nutrient_fraction.assert_called_once_with(0.38, 0.71, 0.60, 1.2, 0.8)
    assert data.optimal_phosphorus_fraction == 0.75

    if gate:
        mock_determine_optimal_nutrient.assert_called_once_with(0.75, 122.8)
        assert data.optimal_phosphorus == -268

        mock_determine_potential_nutrient_uptake.assert_not_called()
        assert incorp.potential_nutrient_uptake == 0
    else:
        assert data.optimal_phosphorus == 268
        mock_determine_potential_nutrient_uptake.assert_called_once_with(268, 0, 0.60, 999)
        assert incorp.potential_nutrient_uptake == 123.1

    mock_uptake_phosphorus.assert_called_once_with(phosphates, depths)
    mock_determine_stored_nutrient.assert_called_once()
    assert data.phosphorus == 99.3
