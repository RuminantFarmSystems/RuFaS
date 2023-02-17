import pytest
from typing import Dict
from math import inf
from dataclasses import asdict

from SC_redesign.Crop_and_Soil.soil.soil_config_factory import SoilConfigurations, SoilConfigFactory
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


# --- Tests to validate Soil Config Factory module ---
@pytest.mark.parametrize("config,expected", [
    ("generic", SoilConfigurations.GENERIC),
])
def test_soil_config_enum(config: str, expected: SoilConfigurations) -> None:
    """Tests that SoilConfigurations properly enumerates accepted configuration names"""
    soil_config = SoilConfigurations(config)
    assert soil_config == expected


@pytest.mark.parametrize("invalid_config", [
    "prairie seafloor",
    "indoor floor",
])
def test_invalid_soil_config_enum(invalid_config: str) -> None:
    """Tests that SoilConfigurations raises an error correctly when an invalid configuration name is passed"""
    with pytest.raises(ValueError) as e:
        SoilConfigurations(invalid_config)
    assert str(e.value) == f"'{invalid_config}' is not a valid SoilConfigurations"


def test_config_factory_defaults():
    """Tests that SoilData objects created by the SoilConfigFactory method create_soil_data() have all the correct
        defaults"""
    generic = SoilConfigFactory.create_soil_data()
    assert generic.name == "generic soil configuration"
    assert generic.soil_layers == [LayerData(top_depth=0, bottom_depth=50, nitrate=0.5),
                                   LayerData(top_depth=50, bottom_depth=80, nitrate=1),
                                   LayerData(top_depth=80, bottom_depth=200, nitrate=5)]
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
                                                  saturation_point_water_concentration=inf)
    assert generic.time_step == 24
    assert generic.previous_temperature_effect == 0.8
    assert generic.slope_length == 3
    assert generic.manning == 0.4
    assert generic.peak_runoff_rate is None
    assert generic.snow_cover_water_content == 0
    assert generic.eroded_sediment == 0

    # TODO: would this maybe be a cleaner, easier way to test the validity of the SoilData object that gets returned?
    assert generic == SoilData()


@pytest.mark.parametrize("config,args_dict", [
    ("generic", {"name": "altered generic soil", "second_moisture_condition_parameter": "87",
                 "average_subbasin_slope": "0.12", "albedo": "0.11"})
])
def test_soil_factory_alterations(config: str, args_dict: Dict) -> None:
    """Test that SoilConfigFactory can properly create default SoilData objects with altered attributes"""
    # Create soil object
    altered_soil = SoilConfigFactory.create_soil_data(SoilConfigurations(config), **args_dict)
    # Check altered characteristics
    for key, val in args_dict.items():
        assert getattr(altered_soil, key) == val
    # Check that all unaltered attributes have been initialized to their defaults
    unaltered_attributes = asdict(altered_soil).keys() - args_dict.keys()
    default_soil = SoilConfigFactory.create_soil_data(SoilConfigurations(config))
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
        SoilConfigFactory.create_soil_data(SoilConfigurations(config), **args_dict)
    assert "is not a valid attribute" in str(e.value)


# --- Tests to verify correct behavior of SoilData module
def test_manual_soil_data_configuration() -> None:
    """Test that creating a custom SoilData object actually has all the correct values in its fields"""
    # Create custom soil configuration
    mollisols = SoilData(name="mollisols", soil_layers=[LayerData(top_depth=0, bottom_depth=80, nitrate=1.8),
                                                        LayerData(top_depth=80, bottom_depth=150, nitrate=2.6),
                                                        LayerData(top_depth=150, bottom_depth=300, nitrate=5)])
    # Check that attributes were properly set
    assert mollisols.name == "mollisols"
    assert mollisols.soil_layers[0] == LayerData(top_depth=0, bottom_depth=80, nitrate=1.8)
    assert mollisols.soil_layers[1] == LayerData(top_depth=80, bottom_depth=150, nitrate=2.6)
    assert mollisols.soil_layers[2] == LayerData(top_depth=150, bottom_depth=300, nitrate=5)
    # Vadose zone layer gets initialized based on the bottom soil layer, so check that too
    assert mollisols.vadose_zone_layer == LayerData(top_depth=300, bottom_depth=10000000, soil_water_concentration=0,
                                                    saturation_point_water_concentration=inf)
