import pytest
import math

from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.carbon_cycling.pool_gas_partition import PoolGasPartition
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


@pytest.mark.parametrize("soil_structural_slow_carbon_usage", [
    70,  # lower values
    150,  # higher values
    88.8,  # arbitrary
])
def test_soil_structural_slow_carbon_remaining(soil_structural_slow_carbon_usage):
    structural_slow_carbon_loss_rate = 0.3
    expect = soil_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)
    assert expect == PoolGasPartition._soil_structural_slow_carbon_remaining(soil_structural_slow_carbon_usage)


@pytest.mark.parametrize("soil_structural_slow_carbon_usage", [
    70,  # lower values
    150,  # higher values
    88.8,  # arbitrary
])
def test_soil_structural_slow_carbon_loss(soil_structural_slow_carbon_usage):
    structural_slow_carbon_loss_rate = 0.3
    expect = soil_structural_slow_carbon_usage * structural_slow_carbon_loss_rate
    assert expect == PoolGasPartition._soil_structural_slow_carbon_loss(soil_structural_slow_carbon_usage)


@pytest.mark.parametrize("soil_structural_active_carbon_usage", [
    24,  # lower values
    77,  # higher values
    92.4,  # arbitrary
])
def test_soil_structural_active_carbon_remaining(soil_structural_active_carbon_usage):
    structural_active_carbon_loss_rate = 0.45
    expect = soil_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)
    assert expect == PoolGasPartition._soil_structural_active_carbon_remaining(soil_structural_active_carbon_usage)


@pytest.mark.parametrize("soil_structural_active_carbon_usage", [
    24,  # lower values
    77,  # higher values
    92.4,  # arbitrary
])
def test_soil_structural_active_carbon_loss(soil_structural_active_carbon_usage):
    structural_active_carbon_loss_rate = 0.45
    expect = soil_structural_active_carbon_usage * structural_active_carbon_loss_rate
    assert expect == PoolGasPartition._soil_structural_active_carbon_loss(soil_structural_active_carbon_usage)


@pytest.mark.parametrize("soil_metabolic_active_carbon_usage", [
    1,  # lower values
    30,  # higher values
    20.23,  # arbitrary
])
def test_soil_metabolic_active_carbon_remaining(soil_metabolic_active_carbon_usage):
    metabolic_active_carbon_loss_rate = 0.55
    expect = soil_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)
    assert expect == PoolGasPartition._soil_metabolic_active_carbon_remaining(soil_metabolic_active_carbon_usage)


@pytest.mark.parametrize("soil_metabolic_active_carbon_usage", [
    1,  # lower values
    30,  # higher values
    20.23,  # arbitrary
])
def test_soil_metabolic_active_carbon_loss(soil_metabolic_active_carbon_usage):
    metabolic_active_carbon_loss_rate = 0.55
    expect = soil_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate
    assert expect == PoolGasPartition._soil_metabolic_active_carbon_loss(soil_metabolic_active_carbon_usage)


@pytest.mark.parametrize("plant_structural_slow_carbon_usage", [
    7,  # lower values
    40,  # higher values
    83.1,  # arbitrary
])
def test_plant_structural_slow_carbon_remaining(plant_structural_slow_carbon_usage):
    structural_slow_carbon_loss_rate = 0.3
    expect = plant_structural_slow_carbon_usage * (1 - structural_slow_carbon_loss_rate)
    assert expect == PoolGasPartition._plant_structural_slow_carbon_remaining(plant_structural_slow_carbon_usage)


@pytest.mark.parametrize("plant_structural_slow_carbon_usage", [
    7,  # lower values
    40,  # higher values
    83.1,  # arbitrary
])
def test_plant_structural_slow_carbon_loss(plant_structural_slow_carbon_usage):
    structural_slow_carbon_loss_rate = 0.3
    expect = plant_structural_slow_carbon_usage * structural_slow_carbon_loss_rate
    assert expect == PoolGasPartition._plant_structural_slow_carbon_loss(plant_structural_slow_carbon_usage)