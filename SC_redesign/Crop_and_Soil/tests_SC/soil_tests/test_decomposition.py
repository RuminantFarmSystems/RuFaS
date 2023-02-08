import pytest
import math

from pytest_mock import MockerFixture
from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.carbon_cycling.decomposition import Decomposition
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


@pytest.mark.parametrize("temp_average", [
    70,  # lower values
    150,  # higher values
    88.8,  # arbitrary
])
def test_calc_temp_factor(temp_average):
    """ensure that temperature factor was calculated according to the formula in "pseudocode_soil" S.6.A"""
    decomposition_inflection_x = 15.400
    decomposition_inflection_y = 11.750
    max_min_distance = 29.700
    inflection_slope = 0.03
    normalizer = 20.80546
    data = SoilData()
    decomp = Decomposition(data)
    decomp._calc_temp_factor(temp_average)
    expect = max(0.0,
                 (decomposition_inflection_y + (max_min_distance / math.pi) * math.atan(math.pi * inflection_slope * (
                         temp_average - decomposition_inflection_x))) / normalizer)
    assert decomp._calc_temp_factor(temp_average) == expect

@pytest.mark.parametrize("layers", [
    [LayerData(top_depth=0, bottom_depth=4, soil_water_concentration=1.8, field_capacity_water_concentration=1.6,
               wilting_point_water_concentration=0.9),
     LayerData(top_depth=4, bottom_depth=12, soil_water_concentration=0.9, field_capacity_water_concentration=1.2,
               wilting_point_water_concentration=0.8),
     LayerData(top_depth=12, bottom_depth=20, soil_water_concentration=0.8, field_capacity_water_concentration=0.8,
               wilting_point_water_concentration=0.3)],
    [LayerData(top_depth=0, bottom_depth=3, soil_water_concentration=2.8, field_capacity_water_concentration=2.3,
               wilting_point_water_concentration=1.8),
     LayerData(top_depth=3, bottom_depth=15, soil_water_concentration=1.9, field_capacity_water_concentration=1.8,
               wilting_point_water_concentration=0.8),
     LayerData(top_depth=15, bottom_depth=22, soil_water_concentration=0.8, field_capacity_water_concentration=1,
               wilting_point_water_concentration=0.2)],
    [LayerData(top_depth=0, bottom_depth=8, soil_water_concentration=2.3, field_capacity_water_concentration=2.9,
               wilting_point_water_concentration=1.8),
     LayerData(top_depth=8, bottom_depth=20, soil_water_concentration=1.4, field_capacity_water_concentration=1.8,
               wilting_point_water_concentration=0.8),
     LayerData(top_depth=20, bottom_depth=22, soil_water_concentration=0.8, field_capacity_water_concentration=1,
               wilting_point_water_concentration=0.6)],
])
def test_calc_temp_factor(layers):
    data = SoilData(soil_layers=layers)
    decomp = Decomposition(data)

    dimensionless_empirical_factor_a = 0.55
    dimensionless_empirical_factor_b = 1.7
    dimensionless_empirical_factor_c = -0.007
    dimensionless_empirical_factor_e1 = 6.648115
    dimensionless_empirical_factor_e2 = 3.22

    for layer in layers:
        # S.6.A.5
        base_1 = (layer.water_factor - dimensionless_empirical_factor_b) / (dimensionless_empirical_factor_a -
                                                                            dimensionless_empirical_factor_b)
        base_2 = (layer.water_factor - dimensionless_empirical_factor_c) / (dimensionless_empirical_factor_a -
                                                                            dimensionless_empirical_factor_c)
        hold = (base_1 ** dimensionless_empirical_factor_e1) * (base_2 ** dimensionless_empirical_factor_e2)
    expect = hold
    assert decomp._calc_moisture_factor(layers) == hold

@pytest.mark.parametrize("temp_average", [
    70,  # lower values
    150,  # higher values
    88.8,  # arbitrary
])
def test_decompose(temp_average):
    data = SoilData()
    decomp = Decomposition(data)
    decomp._calc_moisture_factor = MagicMock(return_value=1.89)
    decomp._calc_temp_factor = MagicMock(return_value=3.99)

    decomp.decompose(temp_average)

    decomp._calc_moisture_factor.assert_called_once()
    decomp._calc_temp_factor.assert_called_once()

    assert data.decomposition_temperature_effect == 3.99
    assert data.decomposition_moisture_effect == 1.89





