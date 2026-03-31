from math import exp
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.phosphorus_cycling.soluble_phosphorus import SolublePhosphorus
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- Static method tests ---
@pytest.mark.parametrize(
    "runoff,field_size,phosphorus,density,thickness",
    [
        (1.3, 1.39, 13.4, 1.22, 20),
        (2.56, 3.45, 29.334, 2.11, 24),
        (0.35, 1.89, 0.556, 1.01, 31),
        (1.88, 0.97, 0.0, 0.95, 23),
    ],
)
def test_determine_phosphorus_runoff_from_top_soil(
    runoff: float,
    field_size: float,
    phosphorus: float,
    density: float,
    thickness: float,
) -> None:
    """Tests that the correct amount of phosphorus lost to runoff is calculated"""
    with patch(
        "RUFAS.biophysical.field.soil.layer_data.LayerData.determine_soil_nutrient_concentration",
        new_callable=MagicMock,
        return_value=100,
    ) as mocked_soil_nutrient_concentration:
        expected_runoff_liters_per_ha = (
            runoff
            * field_size
            * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
            * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
            / field_size
        )
        expected_unadjusted_phosphorus_removed = 100 * 0.005 * expected_runoff_liters_per_ha * (1 / 1000_000)
        expected_actual_phosphorus_removed = min(phosphorus, expected_unadjusted_phosphorus_removed)

        observed = SolublePhosphorus._determine_phosphorus_runoff_from_top_soil(
            runoff, field_size, phosphorus, density, thickness
        )

        mocked_soil_nutrient_concentration.assert_called_once_with(phosphorus, density, thickness, field_size)
        assert observed == expected_actual_phosphorus_removed


@pytest.mark.parametrize(
    "proportion_clay",
    [
        0.991,
        0.5542,
        0.0913,
        0.0,
    ],
)
def test_determine_isotherm_slope(proportion_clay: float) -> None:
    """Tests that the slope of the phosphorus sorption isotherm is calculated correctly."""
    observed = SolublePhosphorus._determine_isotherm_slope(proportion_clay)
    expected = (173.51 * proportion_clay) + 8.48
    assert observed == expected


@pytest.mark.parametrize(
    "slope",
    [
        8.48,
        158.28,
        34.183,
        94.13,
    ],
)
def test_determine_isotherm_intercept(slope: float) -> None:
    """Tests that the intercept of the phosphorus sorption isotherm is calculated correctly."""
    observed = SolublePhosphorus._determine_isotherm_intercept(slope)
    expected = (4.726 * slope) - 8.97
    assert observed == expected


@pytest.mark.parametrize(
    "phosphorus,slope,intercept,overflow",
    [
        (
            28,
            60.29,
            194,
            False,
        ),
        (12, 33.294, 145.56, False),
        (86, 46.792, 167.398, False),
        (2000000000000000000000000000000000000000000000000000000000, 0.00001, 1, True),
    ],
)
def test_determine_dissolved_reactive_phosphorus_leachate(
    phosphorus: float, slope: float, intercept: float, overflow: bool
) -> None:
    """Tests that the amount of phosphorus calculated to leach out of the layer is correct."""
    observed = SolublePhosphorus._determine_dissolved_reactive_phosphorus_leachate(phosphorus, slope, intercept)
    if overflow:
        assert observed == 20
    else:
        expected = min(20.0, exp(((phosphorus * 1.5) - intercept) / slope))
        assert observed == expected


@pytest.mark.parametrize("percolated_water,area", [(1.8, 3.4), (2.3, 1.22), (0.88, 0.97)])
def test_determine_percolated_water_volume(percolated_water: float, area: float) -> None:
    """Tests that a water amount is correctly converted to a volume."""
    observed = SolublePhosphorus._determine_percolated_water_volume(percolated_water, area)
    expected = (
        percolated_water
        * area
        * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        * GeneralConstants.CUBIC_MILLIMETERS_TO_LITERS
    )
    assert observed == expected


@pytest.mark.parametrize(
    "phosphorus,density,thickness,clay_content,percolated_water,area",
    [
        (12.3, 1.4, 35, 18.44, 3.4, 1.88),
        (16.7, 1.23, 28.7, 17.4, 2.1, 0.88),
        (0.0, 1.023, 12, 9.33, 1.21, 3.45),
        (2.33, 0.33, 40.32, 0.0, 4.11, 2.34),
        (8.44, 2.13, 60.7, 24.33, 0.0, 1.23),
        (0.0, 1.23, 28.7, 0.0, 0.0, 0.88),
    ],
)
def test_determine_phosphorus_percolated_from_layer(
    phosphorus: float,
    density: float,
    thickness: float,
    clay_content: float,
    percolated_water: float,
    area: float,
) -> None:
    """Tests that the correct amount of phosphorus removed from a layer of soil is calculated."""
    LayerData.determine_soil_nutrient_concentration = MagicMock(return_value=3.8)
    SolublePhosphorus._determine_isotherm_slope = MagicMock(return_value=35)
    SolublePhosphorus._determine_isotherm_intercept = MagicMock(return_value=155)
    SolublePhosphorus._determine_dissolved_reactive_phosphorus_leachate = MagicMock(return_value=2_000_000)
    SolublePhosphorus._determine_percolated_water_volume = MagicMock(return_value=1.0)
    drp_leachate_in_kg_per_ha = 2_000_000 * GeneralConstants.MILLIGRAMS_TO_KG / area
    bounded_drp_leachate_in_kg_per_ha = min(phosphorus, drp_leachate_in_kg_per_ha)

    observed = SolublePhosphorus._determine_phosphorus_percolated_from_layer(
        phosphorus, density, thickness, clay_content, percolated_water, area
    )

    LayerData.determine_soil_nutrient_concentration.assert_called_once_with(phosphorus, density, thickness, area)
    SolublePhosphorus._determine_isotherm_slope.assert_called_once_with(clay_content)
    SolublePhosphorus._determine_isotherm_intercept.assert_called_once_with(35)
    SolublePhosphorus._determine_dissolved_reactive_phosphorus_leachate.assert_called_once_with(3.8, 35, 155)
    SolublePhosphorus._determine_percolated_water_volume.assert_called_once_with(percolated_water, area)
    assert observed == bounded_drp_leachate_in_kg_per_ha


# --- Test helper methods ---
@pytest.mark.parametrize("runoff,field_size", [(1.3, 2.34), (0.0, 1.2), (2.66, 1.9)])
def test_daily_update_routine(runoff: float, field_size: float) -> None:
    """Tests that the daily update routine for percolating phosphorus down through layers works correctly."""
    layers = [
        LayerData(
            top_depth=0,
            bottom_depth=20,
            initial_soil_nitrate_concentration=0.5,
            field_size=1.1,
        ),
        LayerData(
            top_depth=20,
            bottom_depth=50,
            initial_soil_nitrate_concentration=0.5,
            field_size=1.1,
        ),
        LayerData(
            top_depth=50,
            bottom_depth=80,
            initial_soil_nitrate_concentration=1,
            field_size=1.1,
        ),
        LayerData(
            top_depth=80,
            bottom_depth=200,
            initial_soil_nitrate_concentration=5,
            field_size=1.1,
        ),
    ]
    layers[0].labile_inorganic_phosphorus_content = 3.4
    layers[1].labile_inorganic_phosphorus_content = 3.18
    layers[2].labile_inorganic_phosphorus_content = 2.8
    layers[3].labile_inorganic_phosphorus_content = 2.9

    data = SoilData(field_size=1.1, soil_layers=layers)
    incorp = SolublePhosphorus(data)

    incorp._determine_phosphorus_runoff_from_top_soil = MagicMock(return_value=0.9)
    incorp._determine_phosphorus_percolated_from_layer = MagicMock(return_value=1.2)

    incorp.daily_update_routine(runoff, field_size)

    if runoff > 0:
        incorp._determine_phosphorus_runoff_from_top_soil.assert_called_once_with(runoff, field_size, 3.4, 1.4, 20)
        assert incorp.data.soil_layers[0].labile_inorganic_phosphorus_content == (3.4 - 0.9 - 1.2)
        assert incorp.data.annual_soil_phosphorus_runoff == 0.9
        assert incorp.data.soil_phosphorus_runoff == 0.9
    else:
        incorp._determine_phosphorus_runoff_from_top_soil.assert_not_called()
        assert incorp.data.soil_layers[0].labile_inorganic_phosphorus_content == 3.4 - 1.2
        assert incorp.data.soil_phosphorus_runoff == 0.0
    assert incorp._determine_phosphorus_percolated_from_layer.call_count == len(layers)
    assert pytest.approx(incorp.data.soil_layers[1].labile_inorganic_phosphorus_content) == 3.18
    assert pytest.approx(incorp.data.soil_layers[2].labile_inorganic_phosphorus_content) == 2.8
    assert pytest.approx(incorp.data.soil_layers[3].labile_inorganic_phosphorus_content) == 2.9
    assert incorp.data.vadose_zone_layer.labile_inorganic_phosphorus_content == 1.2
    for layer in incorp.data.soil_layers:
        assert layer.percolated_phosphorus == 1.2
