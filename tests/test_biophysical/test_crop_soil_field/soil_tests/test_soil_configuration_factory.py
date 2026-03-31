from dataclasses import asdict
from math import inf
from typing import Dict

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_config_factory import SoilConfigFactory, SoilConfiguration
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "config,expected",
    [
        ("generic", SoilConfiguration.GENERIC),
    ],
)
def test_soil_config_enum(config: str, expected: SoilConfiguration) -> None:
    """Tests that SoilConfiguration properly enumerates accepted configuration names"""
    soil_config = SoilConfiguration(config)
    assert soil_config == expected


@pytest.mark.parametrize(
    "invalid_config",
    [
        "prairie seafloor",
        "indoor floor",
    ],
)
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
    assert generic.soil_layers == [
        LayerData(top_depth=0, bottom_depth=20, field_size=1),
        LayerData(top_depth=20, bottom_depth=50, field_size=1),
        LayerData(top_depth=50, bottom_depth=80, field_size=1),
        LayerData(top_depth=80, bottom_depth=200, field_size=1),
    ]
    assert generic.water_evaporated == 0
    assert generic.second_moisture_condition_parameter == 85
    assert generic.previous_retention_parameter is None
    assert generic.average_subbasin_slope == 0.05
    assert generic.moisture_condition_parameter is None
    assert generic.accumulated_runoff == 0.0
    expected_vadose_zone_layer = LayerData(
        top_depth=200,
        bottom_depth=10000000,
        soil_water_concentration=0,
        saturation_point_water_concentration=inf,
        field_size=1.0,
        initial_labile_inorganic_phosphorus_concentration=0,
        initial_soil_nitrate_concentration=0,
    )
    expected_vadose_zone_layer.active_organic_nitrogen_content = 0
    expected_vadose_zone_layer.stable_organic_nitrogen_content = 0
    assert generic.vadose_zone_layer == expected_vadose_zone_layer
    assert generic.time_step == 24
    assert generic.previous_temperature_effect == 0.8
    assert generic.slope_length == 3
    assert generic.manning == 0.4
    assert generic.snow_content == 0
    assert generic.eroded_sediment == 0

    # Note: this kind of test (overall equality between objects) should be done IN ADDITION TO all the individual tests
    #       above
    assert generic == SoilData(field_size=1)


@pytest.mark.parametrize(
    "config,args_dict",
    [
        (
            "generic",
            {
                "name": "altered generic soil",
                "second_moisture_condition_parameter": "87",
                "average_subbasin_slope": "0.12",
                "albedo": "0.11",
            },
        )
    ],
)
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


@pytest.mark.parametrize(
    "config,args_dict",
    [
        ("generic", {"is_mollisol": "False"}),  # Single invalid attribute
        (
            "generic",
            {"great_soil": "True", "is_tilled": "False"},
        ),  # Multiple invalid attributes
        (
            "generic",
            {"name": "altered generic soil", "percent_asteroid_content": "0.21"},
        ),  # Valid and invalid attributes
    ],
)
def test_soil_factory_alteration_error(config: str, args_dict: Dict) -> None:
    """Test that SoilConfigFactory throws correct error when there is an attempt to set a nonexistent attribute"""
    with pytest.raises(AttributeError) as e:
        SoilConfigFactory.create_soil_data(1.3, SoilConfiguration(config), **args_dict)
    assert "is not a valid attribute" in str(e.value)
