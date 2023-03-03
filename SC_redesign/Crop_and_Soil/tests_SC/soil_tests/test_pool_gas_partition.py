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
