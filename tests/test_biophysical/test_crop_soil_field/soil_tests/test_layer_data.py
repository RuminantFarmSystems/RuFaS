from math import exp, log
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.soil.layer_data import LayerData


@pytest.fixture
def layer(mocker: MockerFixture) -> LayerData:
    mocker.patch.object(LayerData, "__init__", return_value=None)
    return LayerData()


@pytest.mark.parametrize(
    "water_content,field_capacity_content,wilting_point_content,saturation_content,expected",
    [(0.3, 0.6, 0.8, 0.3, 2.5), (0.6, 0.5, 0.8, 0.3, 1.5)],
)
def test_water_factor(
    water_content: float,
    field_capacity_content: float,
    wilting_point_content: float,
    saturation_content: float,
    expected: float,
) -> None:
    """Tests that water factor was calculated correctly"""
    with (
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.field_capacity_content",
            new_callable=PropertyMock,
            return_value=field_capacity_content,
        ),
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.wilting_point_content",
            new_callable=PropertyMock,
            return_value=wilting_point_content,
        ),
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.saturation_content",
            new_callable=PropertyMock,
            return_value=saturation_content,
        ),
    ):
        layer = LayerData(top_depth=15, bottom_depth=32, field_size=35)
        layer.water_content = water_content
        actual = layer.water_factor
        assert expected == approx(actual)


@pytest.mark.parametrize("water,saturation,expected", [(30.0, 60.0, 0.5), (0.0, 20.0, 0.0), (45.0, 45.0, 1.0)])
def test_water_filled_pore_space(
    layer: LayerData, mocker: MockerFixture, water: float, saturation: float, expected: float
) -> None:
    """Tests that the water-filled pore space is calculated correctly for a soil layer."""
    layer.water_content = water
    mocker.patch.object(LayerData, "saturation_content", new_callable=PropertyMock, return_value=saturation)

    actual = layer.water_filled_pore_space

    assert actual == expected


@pytest.mark.parametrize(
    "top,bottom",
    [
        (0, 39),
        (18, 918.10329843),
        (182.9345038, 1509.92854),
    ],
)
def test_layer_thickness(top: float, bottom: float) -> None:
    """Test that the layer_thickness() in LayerData works as expected"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, field_size=1.75)
    expect = bottom - top
    assert layer.layer_thickness == expect


@pytest.mark.parametrize(
    "top,bottom",
    [
        (-43, 89),  # Invalid top depth
        (0, -24),  # Invalid bottom depth
        (-13, -23),  # Invalid top and bottom depths
        (76, 43),  # Bottom depth is above top depth
    ],
)
def test_layer_thickness_error(top: float, bottom: float) -> None:
    """Test that layer_thickness() in LayerData throws errors when given invalid data"""
    with pytest.raises(ValueError) as e:
        LayerData(top_depth=top, bottom_depth=bottom, field_size=1.75)
    assert (
        str(e.value) == f"Expected positive values for top and bottom depths of soil layer where top < bottom, "
        f"received top: '{top}', bottom: '{bottom}'."
    )


@pytest.mark.parametrize(
    "top,bottom,concentration",
    [
        (40, 106.39, 0.36),
        (23.9, 90.19, 0.41),
        (50, 178, 0.11),
    ],
)
def test_post_init(top: float, bottom: float, concentration: float) -> None:
    """Test that __post_init__() runs and correctly initializes attributes in LayerData"""
    with (
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.calculate_phosphorus_sorption_parameter",
            new_callable=MagicMock,
            return_value=0.5,
        ) as calc_psp,
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.determine_soil_nutrient_area_density",
            new_callable=MagicMock,
            return_value=22,
        ) as determine_nutrient_density,
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData._initialize_nitrogen_pools",
            new_callable=MagicMock,
        ) as init_nitrogen_pools,
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData._initialize_carbon_pools",
            new_callable=MagicMock,
        ) as init_carbon_pools,
    ):
        # Initialize object
        layer = LayerData(
            top_depth=top,
            bottom_depth=bottom,
            soil_water_concentration=concentration,
            field_size=1.66,
        )

        # Calculate expected value
        expected_water_content = layer.layer_thickness * concentration

        # Check everything
        assert layer.water_content == expected_water_content
        calc_psp.assert_called_once_with(layer.clay_fraction, 25, layer.organic_carbon_fraction)
        assert determine_nutrient_density.call_count == 3
        assert layer.mean_phosphorus_sorption_parameter == 0.5
        assert layer.labile_inorganic_phosphorus_content == 22
        assert layer.active_inorganic_phosphorus_content == 22
        assert layer.stable_inorganic_phosphorus_content == 22
        init_nitrogen_pools.assert_called_once()
        init_carbon_pools.assert_called_once()


@pytest.mark.parametrize(
    "field_size,top_depth,expected_active,expected_passive,expected_slow,"
    "expected_structural_litter,expected_metabolic_litter,residue",
    [
        (1.4, 0, 4950.0, 0.0, 242550.0, 2.5, 2.5, 5.0),
        (3.556, 0, 4950.0, 0.0, 242550.0, 5.0, 5.0, 10.0),
        (0.88, 0, 4950.0, 0.0, 242550.0, 9.75, 9.75, 19.5),
        (1.4, 120, 4158.0, 91476.0, 112266.0, 0.0, 0.0, 5.0),
        (3.556, 120, 4158.0, 91476.0, 112266.0, 0.0, 0.0, 10.0),
        (0.88, 120, 4158.0, 91476.0, 112266.0, 0.0, 0.0, 19.5),
    ],
)
def test_initialize_carbon_pools(
    field_size: float,
    top_depth: int,
    expected_active: float,
    expected_passive: float,
    expected_slow: float,
    expected_structural_litter: float,
    expected_metabolic_litter: float,
    residue: float,
) -> None:
    """Tests that carbon pools in a soil layer are properly initialized."""
    actual = LayerData(
        field_size=field_size,
        residue=residue,
        top_depth=top_depth,
        bottom_depth=750.0,
        bulk_density=1.5,
        organic_carbon_fraction=0.022,
    )
    assert actual.active_carbon_amount == pytest.approx(expected_active)
    assert actual.passive_carbon_amount == pytest.approx(expected_passive)
    assert actual.slow_carbon_amount == pytest.approx(expected_slow)
    assert actual.structural_litter_amount == pytest.approx(expected_structural_litter)
    assert actual.metabolic_litter_amount == pytest.approx(expected_metabolic_litter)
    assert actual.total_soil_carbon_amount == pytest.approx(expected_active + expected_passive + expected_slow)


@pytest.mark.parametrize(
    "top,bottom",
    [
        (13, 40),
        (188, 560.9328),
        (101.450, 1039.1948),
    ],
)
def test_depth_of_layer_center(top: float, bottom: float) -> None:
    """Test that depth_of_layer_center() in LayerData correctly determine the center depth"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, field_size=1.35)
    observe = layer.depth_of_layer_center
    expect = bottom - ((bottom - top) / 2)
    assert observe == expect


@pytest.mark.parametrize(
    "top,bottom,field_concentration",
    [
        (13, 40, 0.47),
        (188, 560.9328, 0.54472),
        (101.450, 1039.1948, 0.4990291094),
    ],
)
def test_field_capacity_content(top: float, bottom: float, field_concentration: float) -> None:
    """Test that field_capacity_content() in LayerData correctly calculates the field water content of the layer"""
    layer = LayerData(
        top_depth=top,
        bottom_depth=bottom,
        field_capacity_water_concentration=field_concentration,
        field_size=1.35,
    )
    observe = layer.field_capacity_content
    expect = field_concentration * layer.layer_thickness
    assert observe == expect


@pytest.mark.parametrize(
    "top,bottom,wilt_concentration",
    [
        (13, 40, 0.11),
        (188, 560.9328, 0.091019834),
        (101.450, 1039.1948, 0.179384383),
    ],
)
def test_wilting_point_content(top: float, bottom: float, wilt_concentration: float) -> None:
    """Test that wilting_point_content() in LayerData calculates the wilting point content correctly"""
    layer = LayerData(
        top_depth=top,
        bottom_depth=bottom,
        wilting_point_water_concentration=wilt_concentration,
        field_size=2.44,
    )
    observe = layer.wilting_point_content
    expect = wilt_concentration * layer.layer_thickness
    assert observe == expect


@pytest.mark.parametrize(
    "saturation_concentration,layer_thickness",
    [(0.55, 45), (1.011292, 76.2), (0.9847, 146.3)],
)
def test_saturation_content(saturation_concentration: float, layer_thickness: float) -> None:
    """Test that saturation_content() in LayerData calculates the saturation content of a soil layer correctly"""
    with patch(
        "RUFAS.biophysical.field.soil.layer_data.LayerData.layer_thickness",
        new_callable=PropertyMock,
        return_value=layer_thickness,
    ):
        layer = LayerData(
            top_depth=0,
            bottom_depth=30,
            saturation_point_water_concentration=saturation_concentration,
            field_size=1.61,
        )
        observe = layer.saturation_content
        expect = saturation_concentration * layer_thickness
        assert observe == expect


@pytest.mark.parametrize(
    "water_content,field_capacity_content",
    [
        (0.11, 0.08),
        (0.99, 0.56),
        (0.19, 0.36),
        (0.21, 0.21),
    ],
)
def test_excess_water_available(water_content: float, field_capacity_content: float) -> None:
    """Test that excess_water_available() in LayerData correctly calculates the amount of excess water available in a
    layer"""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.layer_data.LayerData",
        soil_water_concentration=PropertyMock(return_value=water_content),
        layer_thickness=PropertyMock(return_value=1),
        field_capacity_content=PropertyMock(return_value=field_capacity_content),
    ):
        layer = LayerData(top_depth=0, bottom_depth=30, field_size=1.22)
        observe = layer.excess_water_available
        if water_content >= field_capacity_content:
            expect = water_content - field_capacity_content
        else:
            expect = 0
        assert observe == expect


@pytest.mark.parametrize(
    "water_content,saturation_content",
    [
        (0.45, 0.66),
        (0.99, 0.87),
        (0.19, 0.45697),
        (0.546, 0.546),
    ],
)
def test_acceptable_percolation_amount(water_content: float, saturation_content: float) -> None:
    """Test that acceptable_percolation_amount() in LayerData correctly calculates the maximum amount of water that can
    be percolated into it"""
    with patch.multiple(
        "RUFAS.biophysical.field.soil.layer_data.LayerData",
        soil_water_concentration=PropertyMock(return_value=water_content),
        layer_thickness=PropertyMock(return_value=1),
        saturation_content=PropertyMock(return_value=saturation_content),
    ):
        layer = LayerData(top_depth=0, bottom_depth=30, field_size=1.11)
        observe = layer.acceptable_percolation_amount
        if saturation_content > water_content:
            expect = saturation_content - water_content
        else:
            expect = 0
        assert observe == expect


@pytest.mark.parametrize(
    "added_phosphorus,initial_labile_phosphorus,field_size",
    [
        (100, 450, 1.5),
        (78, 335, 1),
        (150, 800, 2.393481),
        (200, 467, 4.10184),
        (138, 0, 3.29184),
    ],
)
def test_add_to_labile_phosphorus(added_phosphorus: float, initial_labile_phosphorus: float, field_size: float) -> None:
    """Tests that the labile phosphorus content of the top soil layer has phosphorus correctly added to it."""
    layer = LayerData(top_depth=0, bottom_depth=30, field_size=field_size)
    layer.labile_inorganic_phosphorus_content = initial_labile_phosphorus
    layer._add_phosphorus_to_pool = MagicMock(return_value=100)

    layer.add_to_labile_phosphorus(added_phosphorus, field_size)

    layer._add_phosphorus_to_pool.assert_called_once_with(initial_labile_phosphorus, added_phosphorus, field_size)
    assert layer.labile_inorganic_phosphorus_content == 100


@pytest.mark.parametrize(
    "added_phosphorus,initial_active_phosphorus,field_size",
    [
        (210, 460, 1.8),
        (135, 540, 2.37),
        (95, 300, 1.88),
        (215, 0, 4.15),
    ],
)
def test_add_to_active_phosphorus(added_phosphorus: float, initial_active_phosphorus: float, field_size: float) -> None:
    """Tests that the stable phosphorus content of the top soil layer has phosphorus correctly added to it."""
    layer = LayerData(top_depth=0, bottom_depth=27, field_size=field_size)
    layer.active_inorganic_phosphorus_content = initial_active_phosphorus
    layer._add_phosphorus_to_pool = MagicMock(return_value=200)

    layer.add_to_active_phosphorus(added_phosphorus, field_size)

    layer._add_phosphorus_to_pool.assert_called_once_with(initial_active_phosphorus, added_phosphorus, field_size)
    assert layer.active_inorganic_phosphorus_content == 200


@pytest.mark.parametrize(
    "pool,added_phosphorus,area",
    [
        (400, 35, 1.8),
        (166, 84, 3.8),
        (0, 221, 2.334),
    ],
)
def test_add_phosphorus_to_pool(pool: float, added_phosphorus: float, area: float) -> None:
    """Tests that this method correctly calculates the new value of the soil phosphorus pool being added to."""
    observe = LayerData._add_phosphorus_to_pool(pool, added_phosphorus, area)
    expect = pool + (added_phosphorus / area)
    assert observe == expect


@pytest.mark.parametrize(
    "clay,phosphorus,carbon",
    [
        (23.1, 23, 14.22),
        (55.43, 12.11, 8.45),
        (3.24, 15.66, 34.85),
        (0.0, 0.0, 0.0),
    ],
)
def test_calculate_phosphorus_sorption_parameter(clay: float, phosphorus: float, carbon: float) -> None:
    """Tests the that the phosphorus sorption parameter is calculated properly based on the clay, labile inorganic
    phosphorus, and carbon contents of the soil."""
    observed = LayerData.calculate_phosphorus_sorption_parameter(clay, phosphorus, carbon)
    if clay <= 0.0:
        clay = 10**-8
    expected = -0.045 * log(clay) + 0.001 * phosphorus - 0.035 * carbon + 0.43
    expected = max(0.05, min(0.7, expected))
    assert observed == expected


@pytest.mark.parametrize(
    "nutrient,density,depth,area",
    [
        (25, 22.13, 20, 1.88),
        (13, 34.556, 9.12, 3.45),
        (1.2344, 19.84, 15, 2.3341),
    ],
)
def test_determine_soil_nutrient_concentration(nutrient: float, density: float, depth: float, area: float) -> None:
    """Tests that the soil nutrient concentration is calculated correctly."""
    observed = LayerData.determine_soil_nutrient_concentration(nutrient, density, depth, area)
    total_soil_volume = (
        depth
        * area
        * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS
    )
    total_soil_mass = density * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS * total_soil_volume
    total_nutrient_mass = nutrient * area
    expected_concentration = (total_nutrient_mass * GeneralConstants.KG_TO_MILLIGRAMS) / total_soil_mass
    assert pytest.approx(observed) == expected_concentration


@pytest.mark.parametrize(
    "phosphorus,density,thickness,field_size",
    [(30.45, 1.9, 30, 1.88), (11.495, 0.66, 35.66, 2.13), (76.35, 1.1, 12, 0.95)],
)
def test_determine_soil_nutrient_area_density(
    phosphorus: float, density: float, thickness: float, field_size: float
) -> None:
    """Tests that the conversion from mg / kg soil to kg / ha is performed correctly."""
    observed = LayerData.determine_soil_nutrient_area_density(phosphorus, density, thickness, field_size)
    expected_soil_mass_kg = (
        density
        * GeneralConstants.MEGAGRAMS_TO_KILOGRAMS
        * (
            thickness
            * field_size
            * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
            * GeneralConstants.CUBIC_MILLIMETERS_TO_CUBIC_METERS
        )
    )
    expected = phosphorus * GeneralConstants.MILLIGRAMS_TO_KG * expected_soil_mass_kg * (1 / field_size)
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize(
    "temp",
    [
        13,
        2.233,
        -3.445,
        24,
    ],
)
def test_nutrient_cycling_temp_factor(temp: float) -> None:
    """Tests the nutrient cycling temperature factor is correctly calculated as a property of LayerData."""
    layer = LayerData(top_depth=23, bottom_depth=67, field_size=1.5, temperature=temp)
    observed = layer.nutrient_cycling_temp_factor
    expected = 0.9 * (temp / (temp + exp(9.93 - 0.312 * temp))) + 0.1
    expected = max(0.1, expected)
    assert observed == expected


@pytest.mark.parametrize("water_content,field_capacity", [(13.44, 16.77), (14.332, 12.445), (0, 5.334)])
def test_nutrient_cycling_water_factor(water_content: float, field_capacity: float) -> float:
    """Tests that the nutrient cycling water factor is correctly calculated as a property of LayerData."""
    with patch(
        "RUFAS.biophysical.field.soil.layer_data.LayerData.field_capacity_content",
        new_callable=PropertyMock,
        return_value=field_capacity,
    ):
        layer = LayerData(top_depth=15, bottom_depth=40, field_size=1.8)
        layer.water_content = water_content
        observed = layer.nutrient_cycling_water_factor
        expected = max(0.05, water_content / field_capacity)
        assert observed == expected


@pytest.mark.parametrize("metabolic,structural,expected", [(2, 3, 5), (14.332, 12.445, 26.777), (0, 5.334, 5.334)])
def test_carbon_residue_amount(metabolic: float, structural: float, expected: float, mocker: MockerFixture) -> None:
    """Test that the carbon_residue_amount adds carbon residue correctly."""
    layer = LayerData(top_depth=15, bottom_depth=40, field_size=1.8)
    mocker.patch.object(layer, "metabolic_litter_amount", metabolic)
    mocker.patch.object(layer, "structural_litter_amount", structural)

    observed = layer.carbon_residue_amount
    assert observed == expected
