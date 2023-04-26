import pytest
from typing import Dict, List
from math import inf, log
from dataclasses import asdict
from unittest.mock import patch, PropertyMock, MagicMock

from SC_redesign.Crop_and_Soil.soil.soil_config_factory import SoilConfiguration, SoilConfigFactory
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.evapotranspiration import Evapotranspiration
from SC_redesign.Crop_and_Soil.soil.infiltration import Infiltration
from SC_redesign.Crop_and_Soil.soil.soil_erosion import SoilErosion
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import MEGAGRAMS_TO_KILOGRAMS, HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_CUBIC_METERS, KILOGRAMS_TO_MILLIGRAMS, MILLIGRAMS_TO_KILOGRAMS


# --- Tests to validate Soil Config Factory module ---
@pytest.mark.parametrize("config,expected", [
    ("generic", SoilConfiguration.GENERIC),
])
def test_soil_config_enum(config: str, expected: SoilConfiguration) -> None:
    """Tests that SoilConfiguration properly enumerates accepted configuration names"""
    soil_config = SoilConfiguration(config)
    assert soil_config == expected


@pytest.mark.parametrize("invalid_config", [
    "prairie seafloor",
    "indoor floor",
])
def test_invalid_soil_config_enum(invalid_config: str) -> None:
    """Tests that SoilConfiguration raises an error correctly when an invalid configuration name is passed"""
    with pytest.raises(ValueError) as e:
        SoilConfiguration(invalid_config)
    assert str(e.value) == f"'{invalid_config}' is not a valid SoilConfiguration"


def test_config_factory_defaults():
    """Tests that SoilData objects created by the SoilConfigFactory method create_soil_data() have all the correct
        defaults"""
    generic = SoilConfigFactory.create_soil_data(1)
    assert generic.name == "generic soil configuration"
    assert generic.soil_layers == [LayerData(top_depth=0, bottom_depth=20, nitrate=0.5, field_size=1),
                                   LayerData(top_depth=20, bottom_depth=50, nitrate=0.5, field_size=1),
                                   LayerData(top_depth=50, bottom_depth=80, nitrate=1, field_size=1),
                                   LayerData(top_depth=80, bottom_depth=200, nitrate=5, field_size=1)]
    assert generic.potential_evapotranspiration is None
    assert generic.potential_evapotranspiration_adjusted is None
    assert generic.transpiration == 30
    assert generic.soil_evaporation_adjusted is None
    assert generic.maximum_soil_evaporation is None
    assert generic.second_moisture_condition_parameter == 85
    assert generic.previous_retention_parameter is None
    assert generic.average_subbasin_slope == 0.05
    assert generic.moisture_condition_parameter is None
    assert generic.accumulated_runoff is None
    assert generic.vadose_zone_layer == LayerData(top_depth=200, bottom_depth=10000000, soil_water_concentration=0,
                                                  saturation_point_water_concentration=inf, field_size=1.0,
                                                  initial_labile_inorganic_phosphorus_concentration=0)
    assert generic.time_step == 24
    assert generic.previous_temperature_effect == 0.8
    assert generic.slope_length == 3
    assert generic.manning == 0.4
    assert generic.peak_runoff_rate is None
    assert generic.snow_cover_water_content == 0
    assert generic.eroded_sediment == 0

    # Note: this kind of test (overall equality between objects) should be done IN ADDITION TO all the individual tests
    #       above
    assert generic == SoilData(field_size=1)


@pytest.mark.parametrize("config,args_dict", [
    ("generic", {"name": "altered generic soil", "second_moisture_condition_parameter": "87",
                 "average_subbasin_slope": "0.12", "albedo": "0.11"})
])
def test_soil_factory_alterations(config: str, args_dict: Dict) -> None:
    """Test that SoilConfigFactory can properly create default SoilData objects with altered attributes"""
    # Create soil object
    altered_soil = SoilConfigFactory.create_soil_data(1.2, SoilConfiguration(config), **args_dict)
    # Check altered characteristics
    for key, val in args_dict.items():
        assert getattr(altered_soil, key) == val
    # Check that all unaltered attributes have been initialized to their defaults
    unaltered_attributes = asdict(altered_soil).keys() - args_dict.keys()
    default_soil = SoilConfigFactory.create_soil_data(1.2, SoilConfiguration(config))
    for key in unaltered_attributes:
        assert getattr(altered_soil, key) == getattr(default_soil, key)


@pytest.mark.parametrize("config,args_dict", [
    ("generic", {"is_mollisol": "False"}),  # Single invalid attribute
    ("generic", {"great_soil": "True", "is_tilled": "False"}),  # Multiple invalid attributes
    ("generic", {"name": "altered generic soil", "percent_asteroid_content": "0.21"}),  # Valid and invalid attributes
])
def test_soil_factory_alteration_error(config: str, args_dict: Dict) -> None:
    """Test that SoilConfigFactory throws correct error when there is an attempt to set a nonexistent attribute"""
    with pytest.raises(AttributeError) as e:
        SoilConfigFactory.create_soil_data(1.3, SoilConfiguration(config), **args_dict)
    assert "is not a valid attribute" in str(e.value)


# --- Tests to verify correct behavior of SoilData module
def test_get_vectorized_layer_attribute() -> None:
    """ensures that layer data can be vectorized."""
    soil_layers = [
        LayerData(top_depth=0, bottom_depth=20, soil_water_concentration=500, field_capacity_water_concentration=0.15,
                  saturation_point_water_concentration=0.2, field_size=1.55),
        LayerData(top_depth=20, bottom_depth=25, soil_water_concentration=1000, field_capacity_water_concentration=0.5,
                  saturation_point_water_concentration=0.8, field_size=1.55),
        LayerData(top_depth=25, bottom_depth=30, soil_water_concentration=30, field_capacity_water_concentration=0.10,
                  saturation_point_water_concentration=0.11, field_size=1.55),
        LayerData(top_depth=30, bottom_depth=100, soil_water_concentration=5000, field_capacity_water_concentration=0.5,
                  saturation_point_water_concentration=0.5, field_size=1.55),
    ]
    soil_data = SoilData(soil_layers=soil_layers, field_size=1.55)

    assert soil_data.get_vectorized_layer_attribute("top_depth") == [0, 20, 25, 30]
    assert soil_data.get_vectorized_layer_attribute("bottom_depth") == [20, 25, 30, 100]
    assert soil_data.get_vectorized_layer_attribute("soil_water_concentration") == [500, 1000, 30, 5000]
    assert soil_data.get_vectorized_layer_attribute("field_capacity_water_concentration") == [0.15, 0.5, 0.10, 0.5]
    assert soil_data.get_vectorized_layer_attribute("saturation_point_water_concentration") == [0.2, 0.8, 0.11, 0.5]
    with pytest.raises(Exception):
        soil_data.get_vectorized_layer_attribute("non_existant_variable")


def test_set_vectorized_layer_attribute() -> None:
    """ensures that layer attributes are properly set"""
    soil_data = SoilData(field_size=1.55)  # 4 layers by default
    water_concentration = [0.1, 0.2, 1, 0.8]
    soil_data.set_vectorized_layer_attribute("soil_water_concentration", water_concentration)
    assert soil_data.get_vectorized_layer_attribute("soil_water_concentration") == water_concentration


def test_manual_soil_data_configuration() -> None:
    """Test that creating a custom SoilData object actually has all the correct values in its fields"""
    mollisols = SoilData(name="mollisols", field_size=1.8,
                         soil_layers=[LayerData(top_depth=0, bottom_depth=80, nitrate=1.8, field_size=1.8),
                                      LayerData(top_depth=80, bottom_depth=150, nitrate=2.6, field_size=1.8),
                                      LayerData(top_depth=150, bottom_depth=300, nitrate=5, field_size=1.8)])

    assert mollisols.name == "mollisols"
    assert mollisols.soil_layers[0] == LayerData(top_depth=0, bottom_depth=20, nitrate=1.8, field_size=1.8)
    assert mollisols.soil_layers[1] == LayerData(top_depth=20, bottom_depth=80, nitrate=1.8, field_size=1.8)
    assert mollisols.soil_layers[2] == LayerData(top_depth=80, bottom_depth=150, nitrate=2.6, field_size=1.8)
    assert mollisols.soil_layers[3] == LayerData(top_depth=150, bottom_depth=300, nitrate=5, field_size=1.8)
    assert mollisols.vadose_zone_layer == LayerData(top_depth=300, bottom_depth=10000000,
                                                    soil_water_concentration=0, field_size=1.8,
                                                    saturation_point_water_concentration=inf,
                                                    initial_labile_inorganic_phosphorus_concentration=0)


def test_error_manual_soil_data_configuration() -> None:
    """Test that an error is correctly raised when an invalid input is used to create SoilData object."""
    with pytest.raises(TypeError) as e:
        SoilData(field_size=1.8, soil_layers=[LayerData(top_depth=0, bottom_depth=19, nitrate=1.8),
                                              LayerData(top_depth=19, bottom_depth=150, nitrate=2.6),
                                              LayerData(top_depth=150, bottom_depth=300, nitrate=5)])
    assert str(e.value) == "'field_size' attribute is NoneType, must be given value when LayerData is initialized."
    with pytest.raises(ValueError) as e:
        SoilData(field_size=1.8, soil_layers=[LayerData(top_depth=0, bottom_depth=19, nitrate=1.8, field_size=1.8),
                                              LayerData(top_depth=19, bottom_depth=150, nitrate=2.6, field_size=1.8),
                                              LayerData(top_depth=150, bottom_depth=300, nitrate=5, field_size=-1.8)])
    assert str(e.value) == "Expected field_size to be greater than 0, received '-1.8'."
    with pytest.raises(ValueError) as e:
        SoilData(field_size=1.8, soil_layers=[LayerData(top_depth=0, bottom_depth=19, nitrate=1.8, field_size=1.8),
                                              LayerData(top_depth=19, bottom_depth=150, nitrate=2.6, field_size=1.8),
                                              LayerData(top_depth=150, bottom_depth=300, nitrate=5, field_size=1.8)])
    assert str(e.value) == "Expected bottom depth of top soil layer must be 20 mm or greater, received '19'."


def test_annual_reset() -> None:
    """Test that annual_reset() actually resets the values it should"""
    # Initialize objects
    soil_data = SoilData(name="test", peak_runoff_rate=0.95, field_size=2.11,
                         annual_runoff_machine_manure_organic_phosphorus=10,
                         annual_runoff_machine_manure_inorganic_phosphorus=10,
                         annual_runoff_grazing_manure_organic_phosphorus=10,
                         annual_runoff_grazing_manure_inorganic_phosphorus=10)
    evapotranspirator = Evapotranspiration(soil_data)
    infiltrator = Infiltration(soil_data)
    eroder = SoilErosion(soil_data)
    fertilizer_phosphorus = Fertilizer(soil_data)

    # Run methods that add to annual totals
    evapotranspirator.evapotranspirate(500, 24, 18, 20, 1000, 200, 0.12, 1.01)
    infiltrator.infiltrate(20, 0.58392)
    eroder.erode(1, 0.2, 800)
    fertilizer_phosphorus.add_fertilizer_phosphorus(90)
    fertilizer_phosphorus.do_fertilizer_phosphorus_operations(13, 5, 1.8)

    # Patch profile soil water content and profile nitrates total so that they are different from their initial values
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.soil_data.SoilData",
                        profile_soil_water_content=PropertyMock(return_value=1.05),
                        profile_nitrates_total=PropertyMock(return_value=2.83)):
        # Check that annual totals actually need to be reset
        assert soil_data.initial_water_content != soil_data.profile_soil_water_content
        assert soil_data.initial_nitrates_total != soil_data.profile_nitrates_total
        assert soil_data.annual_potential_evapotranspiration_total != 0
        assert soil_data.annual_adjusted_potential_evapotranspiration_total != 0
        assert soil_data.annual_maximum_soil_evaporation_total != 0
        assert soil_data.annual_adjusted_soil_evaporation_total != 0
        assert soil_data.annual_runoff_total != 0
        assert soil_data.annual_eroded_sediment_total != 0
        assert soil_data.annual_surface_runoff_total != 0
        assert soil_data.annual_runoff_fertilizer_phosphorus != 0
        assert soil_data.annual_runoff_machine_manure_organic_phosphorus != 0
        assert soil_data.annual_runoff_machine_manure_inorganic_phosphorus != 0
        assert soil_data.annual_runoff_grazing_manure_organic_phosphorus != 0
        assert soil_data.annual_runoff_grazing_manure_inorganic_phosphorus != 0

        # Run method
        soil_data.do_annual_reset()

        # Check that annual totals were reset correctly
        assert soil_data.initial_water_content == soil_data.profile_soil_water_content
        assert soil_data.initial_nitrates_total == soil_data.profile_nitrates_total
        assert soil_data.annual_potential_evapotranspiration_total == 0
        assert soil_data.annual_adjusted_potential_evapotranspiration_total == 0
        assert soil_data.annual_maximum_soil_evaporation_total == 0
        assert soil_data.annual_adjusted_soil_evaporation_total == 0
        assert soil_data.annual_runoff_total == 0
        assert soil_data.annual_eroded_sediment_total == 0
        assert soil_data.annual_surface_runoff_total == 0
        assert soil_data.annual_runoff_fertilizer_phosphorus == 0
        assert soil_data.annual_runoff_machine_manure_organic_phosphorus == 0
        assert soil_data.annual_runoff_machine_manure_inorganic_phosphorus == 0
        assert soil_data.annual_runoff_grazing_manure_organic_phosphorus == 0
        assert soil_data.annual_runoff_grazing_manure_inorganic_phosphorus == 0


def test_profile_soil_water_content() -> None:
    """Test that SoilData correctly calculates amount of water in the entire soil profile"""
    # Set water content and wilting point content of every soil layer to certain amount
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData",
                        soil_water_concentration=PropertyMock(return_value=0.87),
                        layer_thickness=PropertyMock(return_value=1),
                        wilting_point_content=PropertyMock(return_value=0.32)):
        soil_data = SoilData(field_size=0.98)
        observe = soil_data.profile_soil_water_content
        expect = len(soil_data.soil_layers) * (0.87 - 0.32)
        assert observe == expect


def test_profile_saturation() -> None:
    """Test that SoilData correctly calculates the amount of water in soil profile when completely saturated"""
    with patch("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.saturation_content", new_callable=PropertyMock,
               return_value=0.98):
        soil_data = SoilData(field_size=1.83)
        observe = soil_data.profile_saturation
        expect = len(soil_data.soil_layers) * 0.98
        assert observe == expect


def test_profile_field_capacity() -> None:
    """Test that SoilData correctly calculates the amount of water in the soil profile when at field capacity"""
    with patch("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.field_capacity_content", new_callable=PropertyMock,
               return_value=0.67):
        soil_data = SoilData(field_size=1.223)
        observe = soil_data.profile_field_capacity
        expect = len(soil_data.soil_layers) * 0.67
        assert observe == expect


@pytest.mark.parametrize("profile_water,profile_field_capacity", [
    (3.4857, 4.3948569),
    (5.29485, 5.0918482),
    (3.495839, 3.948591),
])
def test_soil_water_factor(profile_water: float, profile_field_capacity: float) -> None:
    """Test that SoilData correctly calculates the soil water factor for a soil profile"""
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.soil_data.SoilData",
                        profile_soil_water_content=PropertyMock(return_value=profile_water),
                        profile_field_capacity=PropertyMock(return_value=profile_field_capacity)):
        soil_data = SoilData(field_size=1.88)
        observe = soil_data.soil_water_factor
        expect = profile_water / (0.85 * profile_field_capacity)
        assert observe == expect


@pytest.mark.parametrize("layers", [
    [LayerData(top_depth=0, bottom_depth=30, bulk_density=2.4, field_size=1.5),
     LayerData(top_depth=30, bottom_depth=76, bulk_density=2.9, field_size=1.5),
     LayerData(top_depth=76, bottom_depth=145, bulk_density=3.4, field_size=1.5)],
    [LayerData(top_depth=0, bottom_depth=140, bulk_density=5.683745, field_size=1.5),
     LayerData(top_depth=140, bottom_depth=369, bulk_density=8.9384785, field_size=1.5),
     LayerData(top_depth=369, bottom_depth=798, bulk_density=7.485968, field_size=1.5)],
    [LayerData(top_depth=0, bottom_depth=99, bulk_density=1.88973834, field_size=1.5),
     LayerData(top_depth=99, bottom_depth=213, bulk_density=2.119481, field_size=1.5),
     LayerData(top_depth=213, bottom_depth=359, bulk_density=2.556948, field_size=1.5)],
])
def test_profile_bulk_density(layers: List[LayerData]) -> None:
    """Test that SoilData correctly calculates average bulk density of soil profile, weighted by layer thickness"""
    soil_data = SoilData(field_size=1.5, soil_layers=layers)
    observe = soil_data.profile_bulk_density
    expect_top = 0
    expect_bottom = 0
    for layer in layers:
        expect_top += (layer.bulk_density * layer.layer_thickness)
        expect_bottom += layer.layer_thickness
    assert observe == (expect_top / expect_bottom)


@pytest.mark.parametrize("layers", [
    [LayerData(top_depth=0, bottom_depth=30, nitrate=3.8, field_size=0.95),
     LayerData(top_depth=30, bottom_depth=76, nitrate=2.9, field_size=0.95),
     LayerData(top_depth=76, bottom_depth=145, nitrate=1.99, field_size=0.95)],
    [LayerData(top_depth=0, bottom_depth=140, nitrate=10.9983, field_size=0.95),
     LayerData(top_depth=140, bottom_depth=369, nitrate=8.9384785, field_size=0.95),
     LayerData(top_depth=369, bottom_depth=798, nitrate=7.485968, field_size=0.95)],
    [LayerData(top_depth=0, bottom_depth=99, nitrate=5.3950, field_size=0.95),
     LayerData(top_depth=99, bottom_depth=213, nitrate=3.20583, field_size=0.95),
     LayerData(top_depth=213, bottom_depth=359, nitrate=2.556948, field_size=0.95)],
])
def test_profile_nitrates_total(layers: List[LayerData]) -> None:
    """Test that SoilData correctly sums nitrates contained in soil profile"""
    soil_data = SoilData(field_size=0.95, soil_layers=layers)
    observe = soil_data.profile_nitrates_total
    expect = 0
    for layer in layers:
        expect += layer.nitrate
    assert observe == expect


# --- Tests to verify the correct behavior fo the LayerData module
@pytest.mark.parametrize("top,bottom", [
    (0, 39),
    (18, 918.10329843),
    (182.9345038, 1509.92854),
])
def test_layer_thickness(top: float, bottom: float) -> None:
    """Test that the layer_thickness() in LayerData works as expected"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, field_size=1.75)
    expect = bottom - top
    assert layer.layer_thickness == expect


@pytest.mark.parametrize("top,bottom", [
    (-43, 89),  # Invalid top depth
    (0, -24),  # Invalid bottom depth
    (-13, -23),  # Invalid top and bottom depths
    (76, 43),  # Bottom depth is above top depth
])
def test_layer_thickness_error(top: float, bottom: float) -> None:
    """Test that layer_thickness() in LayerData throws errors when given invalid data"""
    with pytest.raises(ValueError) as e:
        LayerData(top_depth=top, bottom_depth=bottom, field_size=1.75)
    assert str(e.value) == f"Expected positive values for top and bottom depths of soil layer where top < bottom, " \
                           f"received top: '{top}', bottom: '{bottom}'."


@pytest.mark.parametrize("top,bottom,concentration", [
    (40, 106.39, 0.36),
    (23.9, 90.19, 0.41),
    (50, 178, 0.11),
])
def test_post_init(top: float, bottom: float, concentration: float) -> None:
    """Test that __post_init__() runs and correctly initializes attributes in LayerData"""
    with patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.calculate_phosphorus_sorption_parameter',
               new_callable=MagicMock, return_value=0.5) as calc_psp:
        with patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.determine_soil_phosphorus_area_density',
                   new_callable=MagicMock, return_value=22) as determine_phosphorus_amount:
            # Initialize object
            layer = LayerData(top_depth=top, bottom_depth=bottom, soil_water_concentration=concentration,
                              field_size=1.66)

            # Calculate expected value
            expected_water_content = layer.layer_thickness * concentration

            # Check everything
            assert layer.water_content == expected_water_content
            calc_psp.assert_called_once_with(layer.percent_clay_content, 25, layer.percent_organic_carbon_content)
            assert determine_phosphorus_amount.call_count == 3
            assert layer.mean_phosphorus_sorption_parameter == 0.5
            assert layer.labile_inorganic_phosphorus_content == 22
            assert layer.active_inorganic_phosphorus_content == 22
            assert layer.stable_inorganic_phosphorus_content == 22


@pytest.mark.parametrize("top,bottom", [
    (13, 40),
    (188, 560.9328),
    (101.450, 1039.1948),
])
def test_depth_of_layer_center(top: float, bottom: float) -> None:
    """Test that depth_of_layer_center() in LayerData correctly determine the center depth"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, field_size=1.35)
    observe = layer.depth_of_layer_center
    expect = bottom - ((bottom - top) / 2)
    assert observe == expect


@pytest.mark.parametrize("top,bottom,field_concentration", [
    (13, 40, 0.47),
    (188, 560.9328, 0.54472),
    (101.450, 1039.1948, 0.4990291094),
])
def test_field_capacity_content(top: float, bottom: float, field_concentration: float) -> None:
    """Test that field_capacity_content() in LayerData correctly calculates the field water content of the layer"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, field_capacity_water_concentration=field_concentration,
                      field_size=1.35)
    observe = layer.field_capacity_content
    expect = field_concentration * layer.layer_thickness
    assert observe == expect


@pytest.mark.parametrize("top,bottom,wilt_concentration", [
    (13, 40, 0.11),
    (188, 560.9328, 0.091019834),
    (101.450, 1039.1948, 0.179384383),
])
def test_wilting_point_content(top: float, bottom: float, wilt_concentration: float) -> None:
    """Test that wilting_point_content() in LayerData calculates the wilting point content correctly"""
    layer = LayerData(top_depth=top, bottom_depth=bottom, wilting_point_water_concentration=wilt_concentration,
                      field_size=2.44)
    observe = layer.wilting_point_content
    expect = wilt_concentration * layer.layer_thickness
    assert observe == expect


@pytest.mark.parametrize("saturation_concentration,layer_thickness", [
    (0.55, 45),
    (1.011292, 76.2),
    (0.9847, 146.3)
])
def test_saturation_content(saturation_concentration: float, layer_thickness: float) -> None:
    """Test that saturation_content() in LayerData calculates the saturation content of a soil layer correctly"""
    with patch('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData.layer_thickness', new_callable=PropertyMock,
               return_value=layer_thickness):
        layer = LayerData(top_depth=0, bottom_depth=30, saturation_point_water_concentration=saturation_concentration,
                          field_size=1.61)
        observe = layer.saturation_content
        expect = saturation_concentration * layer_thickness
        assert observe == expect


@pytest.mark.parametrize("water_content,field_capacity_content", [
    (0.11, 0.08),
    (0.99, 0.56),
    (0.19, 0.36),
    (0.21, 0.21),
])
def test_excess_water_available(water_content: float, field_capacity_content: float) -> None:
    """Test that excess_water_available() in LayerData correctly calculates the amount of excess water available in a
        layer"""
    with patch.multiple('SC_redesign.Crop_and_Soil.soil.layer_data.LayerData',
                        soil_water_concentration=PropertyMock(return_value=water_content),
                        layer_thickness=PropertyMock(return_value=1),
                        field_capacity_content=PropertyMock(return_value=field_capacity_content)):
        layer = LayerData(top_depth=0, bottom_depth=30, field_size=1.22)
        observe = layer.excess_water_available
        if water_content >= field_capacity_content:
            expect = water_content - field_capacity_content
        else:
            expect = 0
        assert observe == expect


@pytest.mark.parametrize("water_content,saturation_content", [
    (0.45, 0.66),
    (0.99, 0.87),
    (0.19, 0.45697),
    (0.546, 0.546),
])
def test_acceptable_percolation_amount(water_content: float, saturation_content: float) -> None:
    """Test that acceptable_percolation_amount() in LayerData correctly calculates the maximum amount of water that can
        be percolated into it"""
    with patch.multiple("SC_redesign.Crop_and_Soil.soil.layer_data.LayerData",
                        soil_water_concentration=PropertyMock(return_value=water_content),
                        layer_thickness=PropertyMock(return_value=1),
                        saturation_content=PropertyMock(return_value=saturation_content)):
        layer = LayerData(top_depth=0, bottom_depth=30, field_size=1.11)
        observe = layer.acceptable_percolation_amount
        if saturation_content > water_content:
            expect = saturation_content - water_content
        else:
            expect = 0
        assert observe == expect


@pytest.mark.parametrize("percent_organic_carbon_proportion", [
    0.98,
    1.82,
    2.49585
])
def test_percent_organic_matter_proportion(percent_organic_carbon_proportion: float) -> None:
    """Test that percent_organic_matter_proportion() in LayerData correctly calculates the percent of organic matter
        content in a layer of soil"""
    layer = LayerData(top_depth=0, bottom_depth=30, percent_organic_carbon_content=percent_organic_carbon_proportion,
                      field_size=1.98)
    observe = layer.percent_organic_matter_proportion
    expect = 1.72 * percent_organic_carbon_proportion
    assert observe == expect


@pytest.mark.parametrize("added_phosphorus,initial_labile_phosphorus,field_size", [
    (100, 450, 1.5),
    (78, 335, 1),
    (150, 800, 2.393481),
    (200, 467, 4.10184),
    (138, 0, 3.29184),
])
def test_add_to_labile_phosphorus(added_phosphorus: float, initial_labile_phosphorus: float, field_size: float) -> None:
    """Tests that the labile phosphorus content of the top soil layer has phosphorus correctly added to it."""
    layer = LayerData(top_depth=0, bottom_depth=30, field_size=field_size)
    layer.labile_inorganic_phosphorus_content = initial_labile_phosphorus
    layer._add_phosphorus_to_pool = MagicMock(return_value=100)

    layer.add_to_labile_phosphorus(added_phosphorus, field_size)

    layer._add_phosphorus_to_pool.assert_called_once_with(initial_labile_phosphorus, added_phosphorus, field_size)
    assert layer.labile_inorganic_phosphorus_content == 100


@pytest.mark.parametrize("added_phosphorus,initial_active_phosphorus,field_size", [
    (210, 460, 1.8),
    (135, 540, 2.37),
    (95, 300, 1.88),
    (215, 0, 4.15),
])
def test_add_to_active_phosphorus(added_phosphorus: float, initial_active_phosphorus: float, field_size: float) -> None:
    """Tests that the stable phosphorus content of the top soil layer has phosphorus correctly added to it."""
    layer = LayerData(top_depth=0, bottom_depth=27, field_size=field_size)
    layer.active_inorganic_phosphorus_content = initial_active_phosphorus
    layer._add_phosphorus_to_pool = MagicMock(return_value=200)

    layer.add_to_active_phosphorus(added_phosphorus, field_size)

    layer._add_phosphorus_to_pool.assert_called_once_with(initial_active_phosphorus, added_phosphorus, field_size)
    assert layer.active_inorganic_phosphorus_content == 200


@pytest.mark.parametrize("pool,added_phosphorus,area", [
    (400, 35, 1.8),
    (166, 84, 3.8),
    (0, 221, 2.334),
])
def test_add_phosphorus_to_pool(pool: float, added_phosphorus: float, area: float) -> None:
    """Tests that this method correctly calculates the new value of the soil phosphorus pool being added to."""
    observe = LayerData._add_phosphorus_to_pool(pool, added_phosphorus, area)
    expect = pool + (added_phosphorus / area)
    assert observe == expect


@pytest.mark.parametrize("clay,phosphorus,carbon", [
    (23.1, 23, 14.22),
    (55.43, 12.11, 8.45),
    (3.24, 15.66, 34.85),
    (0.0, 0.0, 0.0),
])
def test_calculate_phosphorus_sorption_parameter(clay: float, phosphorus: float, carbon: float) -> None:
    """Tests the that the phosphorus sorption parameter is calculated properly based on the clay, labile inorganic
        phosphorus, and carbon contents of the soil."""
    observed = LayerData.calculate_phosphorus_sorption_parameter(clay, phosphorus, carbon)
    if clay <= 0.0:
        clay = 10 ** -8
    expected = -0.045 * log(clay) + 0.001 * phosphorus - 0.035 * carbon + 0.43
    expected = max(0.05, min(0.7, expected))
    assert observed == expected


@pytest.mark.parametrize("phosphorus,density,depth,area", [
    (25, 22.13, 20, 1.88),
    (13, 34.556, 9.12, 3.45),
    (1.2344, 19.84, 15, 2.3341),
])
def test_determine_soil_phosphorus_concentration(phosphorus: float, density: float, depth: float, area: float) -> None:
    """Tests that the soil phosphorus concentration is calculated correctly."""
    observed = LayerData.determine_soil_phosphorus_concentration(phosphorus, density, depth, area)
    total_soil_volume = depth * area * HECTARES_TO_SQUARE_MILLIMETERS * CUBIC_MILLIMETERS_TO_CUBIC_METERS
    total_soil_mass = density * MEGAGRAMS_TO_KILOGRAMS * total_soil_volume
    total_phosphorus_mass = phosphorus * area
    expected_concentration = (total_phosphorus_mass * KILOGRAMS_TO_MILLIGRAMS) / total_soil_mass
    assert pytest.approx(observed) == expected_concentration


@pytest.mark.parametrize("phosphorus,density,thickness,field_size", [
    (30.45, 1.9, 30, 1.88),
    (11.495, 0.66, 35.66, 2.13),
    (76.35, 1.1, 12, 0.95)
])
def test_determine_soil_phosphorus_area_density(phosphorus: float, density: float, thickness: float,
                                                field_size: float) -> None:
    """Tests that the conversion from mg / kg soil to kg / ha is performed correctly."""
    observed = LayerData.determine_soil_phosphorus_area_density(phosphorus, density, thickness, field_size)
    expected_soil_mass_kg = density * MEGAGRAMS_TO_KILOGRAMS * (thickness * field_size * HECTARES_TO_SQUARE_MILLIMETERS
                                                                * CUBIC_MILLIMETERS_TO_CUBIC_METERS)
    expected = phosphorus * MILLIGRAMS_TO_KILOGRAMS * expected_soil_mass_kg * (1 / field_size)
    assert pytest.approx(observed) == expected
