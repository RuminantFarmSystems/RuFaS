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


@pytest.mark.parametrize("plant_structural_active_carbon_usage", [
    17,  # lower values
    90,  # higher values
    55.7,  # arbitrary
])
def test_plant_structural_active_carbon_remaining(plant_structural_active_carbon_usage):
    structural_active_carbon_loss_rate = 0.45
    expected = plant_structural_active_carbon_usage * (1 - structural_active_carbon_loss_rate)
    assert expected == PoolGasPartition._plant_structural_active_carbon_remaining(plant_structural_active_carbon_usage)


@pytest.mark.parametrize("plant_structural_active_carbon_usage", [
    17,  # lower values
    90,  # higher values
    55.7,  # arbitrary
])
def test_plant_structural_active_carbon_loss(plant_structural_active_carbon_usage):
    structural_active_carbon_loss_rate = 0.45
    expected = plant_structural_active_carbon_usage * structural_active_carbon_loss_rate
    assert expected == PoolGasPartition._plant_structural_active_carbon_loss(plant_structural_active_carbon_usage)


@pytest.mark.parametrize("plant_metabolic_active_carbon_usage", [
    3,  # lower values
    102,  # higher values
    51.8,  # arbitrary
])
def test_plant_metabolic_active_carbon_remaining(plant_metabolic_active_carbon_usage):
    metabolic_active_carbon_loss_rate = 0.55
    expected = plant_metabolic_active_carbon_usage * (1 - metabolic_active_carbon_loss_rate)
    assert expected == PoolGasPartition._plant_metabolic_active_carbon_remaining(plant_metabolic_active_carbon_usage)


@pytest.mark.parametrize("plant_metabolic_active_carbon_usage", [
    3,  # lower values
    102,  # higher values
    51.8,  # arbitrary
])
def test_plant_metabolic_active_carbon_loss(plant_metabolic_active_carbon_usage):
    metabolic_active_carbon_loss_rate = 0.55
    expected = plant_metabolic_active_carbon_usage * metabolic_active_carbon_loss_rate
    assert expected == PoolGasPartition._plant_metabolic_active_carbon_loss(plant_metabolic_active_carbon_usage)


@pytest.mark.parametrize("silt_clay_content", [
    5,  # lower values
    100,  # higher values
    35.8,  # arbitrary
])
def test_active_carbon_decomposition_rate(silt_clay_content):
    max_carbon_decomposition_rate = 0.14
    expected = max_carbon_decomposition_rate * (1 - 0.75 * silt_clay_content)
    assert expected == PoolGasPartition._active_carbon_decomposition_rate(silt_clay_content)


@pytest.mark.parametrize("moisture_effect, temperature_effect, active_carbon, active_carbon_decomposition_rate", [
    (3, 4, 5, 6),  # lower values
    (50, 89, 90, 0.7),  # higher value
    (1.8, 1.1, 1, 0.5),  # arbitrary values
])
def test__active_carbon_decomposition_amount(moisture_effect, temperature_effect,
                                             active_carbon, active_carbon_decomposition_rate):
    expected = active_carbon_decomposition_rate * moisture_effect * temperature_effect * active_carbon
    assert expected == PoolGasPartition._active_carbon_decomposition_amount(moisture_effect, temperature_effect,
                                                                            active_carbon,
                                                                            active_carbon_decomposition_rate)


@pytest.mark.parametrize("decomposition_moisture_effect, decomposition_temperature_effect,slow_carbon_amount", [
    (0.2, 1.3, 44),
    (0.5, 1.8, 23),
    (1.8, 1.1, 1),
    (1.1, 2.3, 50),
])
def test_slow_carbon_decomposition_amount(decomposition_moisture_effect, decomposition_temperature_effect,
                                          slow_carbon_amount):
    slow_carbon_decomposition_factor = 0.0038
    expected = decomposition_moisture_effect * decomposition_temperature_effect * slow_carbon_amount * \
               slow_carbon_decomposition_factor
    assert expected == PoolGasPartition._slow_carbon_decomposition_amount(decomposition_moisture_effect,
                                                                          decomposition_temperature_effect,
                                                                          slow_carbon_amount)


@pytest.mark.parametrize("decomposition_moisture_effect, decomposition_temperature_effect,passive_carbon_amount", [
    (0.2, 1.3, 44),
    (0.5, 1.8, 23),
    (1.8, 1.1, 1),
    (1.1, 2.3, 50),
])
def test_passive_carbon_decomposition_amount(decomposition_moisture_effect, decomposition_temperature_effect,
                                             passive_carbon_amount):
    passive_carbon_decomposition_factor = 0.00013
    expected = decomposition_moisture_effect * decomposition_temperature_effect * passive_carbon_amount * \
               passive_carbon_decomposition_factor
    assert expected == PoolGasPartition._passive_carbon_decomposition_amount(decomposition_moisture_effect,
                                                                             decomposition_temperature_effect,
                                                                             passive_carbon_amount)


@pytest.mark.parametrize("silt_clay_content", [
    0.2,  # lower value
    100,  # higher value
    1.8,  # arbitrary values
])
def test_carbon_lost_adjusted_factor(silt_clay_content):
    expected = 0.85 - 0.68 * silt_clay_content
    assert expected == PoolGasPartition._carbon_lost_adjusted_factor(silt_clay_content)


@pytest.mark.parametrize("active_carbon_decomposition_amount, carbon_lost_adjusted_factor", [
    (66, 44),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_active_carbon_to_slow_amount(active_carbon_decomposition_amount, carbon_lost_adjusted_factor):
    expected = active_carbon_decomposition_amount * (1 - carbon_lost_adjusted_factor - 0.004)
    assert expected == PoolGasPartition._active_carbon_to_slow_amount(active_carbon_decomposition_amount,
                                                                      carbon_lost_adjusted_factor)


@pytest.mark.parametrize("active_carbon_decomposition_amount, carbon_lost_adjusted_factor", [
    (66, 44),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_active_carbon_to_slow_loss(active_carbon_decomposition_amount, carbon_lost_adjusted_factor):
    expected = active_carbon_decomposition_amount * carbon_lost_adjusted_factor
    assert expected == PoolGasPartition._active_carbon_to_slow_loss(active_carbon_decomposition_amount,
                                                                    carbon_lost_adjusted_factor)


@pytest.mark.parametrize("active_carbon_decomposition_amount", [
    14,  # lower value
    102,  # higher value
    1.8,  # arbitrary values
])
def test_active_carbon_to_passive_amount(active_carbon_decomposition_amount):
    expected = active_carbon_decomposition_amount * 0.004
    assert expected == PoolGasPartition._active_carbon_to_passive_amount(active_carbon_decomposition_amount)


@pytest.mark.parametrize("slow_carbon_decomposition_amount", [
    15,  # lower value
    99,  # higher value
    9.24,  # arbitrary values
])
def test_slow_to_active_carbon_amount(slow_carbon_decomposition_amount):
    slow_carbon_passive_decompose_rate = 0.03
    slow_carbon_co2_lost_rate = 0.55
    expected = slow_carbon_decomposition_amount * (1 - slow_carbon_co2_lost_rate - slow_carbon_passive_decompose_rate)
    assert expected == PoolGasPartition._slow_to_active_carbon_amount(slow_carbon_decomposition_amount)


@pytest.mark.parametrize("slow_carbon_decomposition_amount", [
    15,  # lower value
    99,  # higher value
    9.24,  # arbitrary values
])
def test_slow_carbon_co2_lost_amount(slow_carbon_decomposition_amount):
    slow_carbon_co2_lost_rate = 0.55
    expected = slow_carbon_decomposition_amount * slow_carbon_co2_lost_rate
    assert expected == PoolGasPartition._slow_carbon_co2_lost_amount(slow_carbon_decomposition_amount)


@pytest.mark.parametrize("slow_carbon_decomposition_amount", [
    15,  # lower value
    99,  # higher value
    9.24,  # arbitrary values
])
def test_slow_to_passive_carbon_amount(slow_carbon_decomposition_amount):
    slow_carbon_passive_decompose_rate = 0.03
    expected = slow_carbon_decomposition_amount * slow_carbon_passive_decompose_rate
    assert expected == PoolGasPartition._slow_to_passive_carbon_amount(slow_carbon_decomposition_amount)


@pytest.mark.parametrize("passive_carbon_decomposition_amount", [
    16,  # lower value
    77,  # higher value
    7.7,  # arbitrary values
])
def test_passive_to_active_carbon_amount(passive_carbon_decomposition_amount):
    passive_carbon_co2_lost_rate = 0.55
    expected = passive_carbon_decomposition_amount * (1 - passive_carbon_co2_lost_rate)
    assert expected == PoolGasPartition._passive_to_active_carbon_amount(passive_carbon_decomposition_amount)


@pytest.mark.parametrize("passive_carbon_decomposition_amount", [
    16,  # lower value
    77,  # higher value
    7.7,  # arbitrary values
])
def test_passive_carbon_co2_lost_amount(passive_carbon_decomposition_amount):
    passive_carbon_co2_lost_rate = 0.55
    expected = passive_carbon_decomposition_amount * passive_carbon_co2_lost_rate
    assert expected == PoolGasPartition._passive_carbon_co2_lost_amount(passive_carbon_decomposition_amount)


@pytest.mark.parametrize("plant_metabolic_active_carbon_remaining, plant_structural_active_carbon_remaining", [
    (77, 54),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_plant_active_decompose_carbon(plant_metabolic_active_carbon_remaining,
                                       plant_structural_active_carbon_remaining):
    expected = plant_metabolic_active_carbon_remaining + plant_structural_active_carbon_remaining
    assert expected == PoolGasPartition._plant_active_decompose_carbon(plant_metabolic_active_carbon_remaining,
                                                                       plant_structural_active_carbon_remaining)


@pytest.mark.parametrize("soil_metabolic_active_carbon_remaining,soil_structural_active_carbon_remaining", [
    (77, 54),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_soil_active_decompose_carbon(soil_metabolic_active_carbon_remaining, soil_structural_active_carbon_remaining):
    expected = soil_metabolic_active_carbon_remaining + soil_structural_active_carbon_remaining
    assert expected == PoolGasPartition._soil_active_decompose_carbon(soil_metabolic_active_carbon_remaining,
                                                                      soil_structural_active_carbon_remaining)


@pytest.mark.parametrize("active_carbon_amount, plant_active_decompose_carbon, soil_active_decompose_carbon, "
                         "passive_to_active_carbon_amount, slow_to_active_carbon_amount,"
                         "active_carbon_decomposition_amount", [
                             (77, 54, 88, 97, 103, 94),  # higher value
                             (0.5, 1.8, 21.2, 1.2, 99.45, 100.01),  # arbitrary values
                             (2, 9, 1, 3, 5, 3)  # lower value
                         ])
def test_soil_active_carbon_amount(active_carbon_amount, plant_active_decompose_carbon,
                                   soil_active_decompose_carbon, passive_to_active_carbon_amount,
                                   slow_to_active_carbon_amount,
                                   active_carbon_decomposition_amount):
    expected = active_carbon_amount + plant_active_decompose_carbon + soil_active_decompose_carbon \
               + slow_to_active_carbon_amount + passive_to_active_carbon_amount - active_carbon_decomposition_amount
    assert expected == PoolGasPartition._soil_active_carbon_amount(active_carbon_amount, plant_active_decompose_carbon,
                                                                   soil_active_decompose_carbon,
                                                                   passive_to_active_carbon_amount,
                                                                   slow_to_active_carbon_amount,
                                                                   active_carbon_decomposition_amount)


@pytest.mark.parametrize("slow_carbon_amount, plant_structural_slow_carbon_remaining,"
                         "soil_structural_slow_carbon_remaining, active_carbon_to_slow_amount,"
                         "slow_carbon_decomposition_amount", [
                             (77, 54, 88, 97, 103),  # higher value
                             (0.5, 1.8, 21.2, 1.2, 99.45),  # arbitrary values
                             (2, 9, 1, 3, 5)  # lower value
                         ])
def test_soil_slow_carbon_amount(slow_carbon_amount, plant_structural_slow_carbon_remaining,
                                 soil_structural_slow_carbon_remaining, active_carbon_to_slow_amount,
                                 slow_carbon_decomposition_amount):
    expected = slow_carbon_amount + plant_structural_slow_carbon_remaining + soil_structural_slow_carbon_remaining + \
               active_carbon_to_slow_amount - slow_carbon_decomposition_amount
    assert expected == PoolGasPartition._soil_slow_carbon_amount(slow_carbon_amount,
                                                                 plant_structural_slow_carbon_remaining,
                                                                 soil_structural_slow_carbon_remaining,
                                                                 active_carbon_to_slow_amount,
                                                                 slow_carbon_decomposition_amount)
