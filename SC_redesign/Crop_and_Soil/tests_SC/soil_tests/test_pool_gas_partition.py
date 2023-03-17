import pytest

from unittest.mock import MagicMock

from SC_redesign.Crop_and_Soil.soil.carbon_cycling.pool_gas_partition import PoolGasPartition
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


@pytest.mark.parametrize("layers", [
    ([LayerData(top_depth=0, bottom_depth=4, soil_water_concentration=1.8, field_capacity_water_concentration=1.6,
                wilting_point_water_concentration=0.9),
      LayerData(top_depth=4, bottom_depth=12, soil_water_concentration=0.9, field_capacity_water_concentration=1.2,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=12, bottom_depth=20, soil_water_concentration=0.8, field_capacity_water_concentration=0.8,
                wilting_point_water_concentration=0.3)]),
    ([LayerData(top_depth=0, bottom_depth=3, soil_water_concentration=2.8, field_capacity_water_concentration=2.3,
                wilting_point_water_concentration=1.8),
      LayerData(top_depth=3, bottom_depth=15, soil_water_concentration=1.9, field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=15, bottom_depth=22, soil_water_concentration=0.8, field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.2)]),
    ([LayerData(top_depth=0, bottom_depth=8, soil_water_concentration=2.3, field_capacity_water_concentration=2.9,
                wilting_point_water_concentration=1.8),
      LayerData(top_depth=8, bottom_depth=20, soil_water_concentration=1.4,
                field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=20, bottom_depth=22, soil_water_concentration=0.8, field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.6)])
])
def test_partition(layers):
    data = SoilData(soil_layers=layers)
    partition = PoolGasPartition(data)

    # S.6.C.1 mocking
    PoolGasPartition._plant_metabolic_active_carbon_loss = MagicMock(return_value=1.89)
    PoolGasPartition._plant_metabolic_active_carbon_remaining = MagicMock(return_value=2.1)
    PoolGasPartition._plant_structural_active_carbon_loss = MagicMock(return_value=2.2)
    PoolGasPartition._plant_structural_active_carbon_remaining = MagicMock(return_value=2.3)
    PoolGasPartition._plant_structural_slow_carbon_loss = MagicMock(return_value=2.4)
    PoolGasPartition._plant_structural_slow_carbon_remaining = MagicMock(return_value=2.5)
    PoolGasPartition._soil_metabolic_active_carbon_loss = MagicMock(return_value=2.6)
    PoolGasPartition._soil_metabolic_active_carbon_remaining = MagicMock(return_value=2.7)
    PoolGasPartition._soil_structural_active_carbon_loss = MagicMock(return_value=2.8)
    PoolGasPartition._soil_structural_active_carbon_remaining = MagicMock(return_value=2.9)
    PoolGasPartition._soil_structural_slow_carbon_loss = MagicMock(return_value=3.1)
    PoolGasPartition._soil_structural_slow_carbon_remaining = MagicMock(return_value=3.2)

    # S.6.C.2 mocking
    PoolGasPartition._active_carbon_decomposition_rate = MagicMock(return_value=0.87)

    # S.6.C.3 mocking
    PoolGasPartition._active_carbon_decomposition_amount = MagicMock(return_value=3.4)

    # S.6.C.4 mocking
    PoolGasPartition._slow_carbon_decomposition_amount = MagicMock(return_value=3.5)

    # S.6.C.5 mocking
    PoolGasPartition._passive_carbon_decomposition_amount = MagicMock(return_value=3.6)

    # S.6.C.6 mocking
    PoolGasPartition._carbon_lost_adjusted_factor = MagicMock(return_value=3.7)

    # S.6.C.7 mocking
    PoolGasPartition._active_carbon_to_slow_amount = MagicMock(return_value=3.8)
    PoolGasPartition._active_carbon_to_slow_loss = MagicMock(return_value=3.9)

    # S.6.C.8 mocking
    PoolGasPartition._active_carbon_to_passive_amount = MagicMock(return_value=4.1)

    # S.6.C.9 mocking
    PoolGasPartition._slow_to_active_carbon_amount = MagicMock(return_value=4.2)
    PoolGasPartition._slow_carbon_co2_lost_amount = MagicMock(return_value=4.3)
    PoolGasPartition._slow_to_passive_carbon_amount = MagicMock(return_value=4.4)

    # S.6.C.10 mocking
    PoolGasPartition._passive_to_active_carbon_amount = MagicMock(return_value=4.5)
    PoolGasPartition._passive_carbon_co2_lost_amount = MagicMock(return_value=4.6)

    # S.6.C.11 mocking
    PoolGasPartition._plant_active_decompose_carbon = MagicMock(return_value=4.7)
    PoolGasPartition._soil_active_decompose_carbon = MagicMock(return_value=4.8)
    PoolGasPartition._soil_active_carbon_amount = MagicMock(return_value=4.9)

    # S.6.C.12 mocking
    PoolGasPartition._soil_slow_carbon_amount = MagicMock(return_value=5.1)

    # S.6.C.13 mocking
    PoolGasPartition._soil_passive_carbon_amount = MagicMock(return_value=5.2)

    partition.partition()

    # Checking if methods are called correct number of times
    assert PoolGasPartition._plant_metabolic_active_carbon_loss.call_count == 3
    assert PoolGasPartition._plant_metabolic_active_carbon_remaining.call_count == 3
    assert PoolGasPartition._plant_structural_active_carbon_loss.call_count == 3
    assert PoolGasPartition._plant_structural_active_carbon_remaining.call_count == 3
    assert PoolGasPartition._plant_structural_slow_carbon_loss.call_count == 3
    assert PoolGasPartition._plant_structural_slow_carbon_remaining.call_count == 3
    assert PoolGasPartition._soil_metabolic_active_carbon_loss.call_count == 3
    assert PoolGasPartition._soil_metabolic_active_carbon_remaining.call_count == 3
    assert PoolGasPartition._soil_structural_active_carbon_loss.call_count == 3
    assert PoolGasPartition._soil_structural_active_carbon_remaining.call_count == 3
    assert PoolGasPartition._soil_structural_slow_carbon_loss.call_count == 3
    assert PoolGasPartition._soil_structural_slow_carbon_remaining.call_count == 3

    assert PoolGasPartition._active_carbon_decomposition_rate.call_count == 1

    assert PoolGasPartition._active_carbon_decomposition_amount.call_count == 3

    assert PoolGasPartition._slow_carbon_decomposition_amount.call_count == 3

    assert PoolGasPartition._passive_carbon_decomposition_amount.call_count == 3

    assert PoolGasPartition._carbon_lost_adjusted_factor.call_count == 1

    assert PoolGasPartition._active_carbon_to_slow_amount.call_count == 3
    assert PoolGasPartition._active_carbon_to_slow_loss.call_count == 3

    assert PoolGasPartition._slow_to_active_carbon_amount.call_count == 3
    assert PoolGasPartition._slow_carbon_co2_lost_amount.call_count == 3
    assert PoolGasPartition._slow_to_passive_carbon_amount.call_count == 3

    assert PoolGasPartition._passive_to_active_carbon_amount.call_count == 3
    assert PoolGasPartition._passive_carbon_co2_lost_amount.call_count == 3

    assert PoolGasPartition._plant_active_decompose_carbon.call_count == 3
    assert PoolGasPartition._soil_active_decompose_carbon.call_count == 3
    assert PoolGasPartition._soil_active_carbon_amount.call_count == 3

    assert PoolGasPartition._soil_slow_carbon_amount.call_count == 3

    assert PoolGasPartition._soil_passive_carbon_amount.call_count == 3

    # Checking values were set correctly by the main routine
    assert partition.data.active_carbon_decomposition_rate == 0.87

    assert partition.data.carbon_lost_adjusted_factor == 3.7
    for layer in data.soil_layers:
        assert layer.plant_metabolic_active_carbon_loss == 1.89
        assert layer.plant_metabolic_active_carbon_remaining == 2.1
        assert layer.plant_structural_active_carbon_remaining == 2.3
        assert layer.plant_structural_slow_carbon_loss == 2.4
        assert layer.plant_structural_slow_carbon_remaining == 2.5
        assert layer.soil_metabolic_active_carbon_loss == 2.6
        assert layer.soil_metabolic_active_carbon_remaining == 2.7
        assert layer.soil_structural_active_carbon_loss == 2.8
        assert layer.soil_structural_active_carbon_remaining == 2.9
        assert layer.soil_structural_slow_carbon_loss == 3.1
        assert layer.soil_structural_slow_carbon_remaining == 3.2

        assert layer.active_carbon_decomposition_amount == 3.4

        assert layer.slow_carbon_decomposition_amount == 3.5

        assert layer.passive_carbon_decomposition_amount == 3.6

        assert layer.active_carbon_to_slow_amount == 3.8
        assert layer.active_carbon_to_slow_loss == 3.9

        assert layer.active_carbon_to_passive_amount == 4.1

        assert layer.slow_to_active_carbon_amount == 4.2
        assert layer.slow_carbon_co2_lost_amount == 4.3
        assert layer.slow_to_passive_carbon_amount == 4.4

        assert layer.passive_to_active_carbon_amount == 4.5
        assert layer.passive_carbon_co2_lost_amount == 4.6

        assert layer.plant_active_decompose_carbon == 4.7
        assert layer.soil_active_decompose_carbon == 4.8
        assert layer.active_carbon_amount == 4.9

        assert layer.slow_carbon_amount == 5.1

        assert layer.passive_carbon_amount == 5.2


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


@pytest.mark.parametrize("passive_carbon_amount, slow_to_passive_carbon_amount,active_carbon_to_passive_amount,"
                         "passive_carbon_decomposition_amount", [
                             (77, 54, 88, 97),  # higher value
                             (0.5, 1.8, 21.2, 1.2),  # arbitrary values
                             (2, 9, 1, 3)  # lower value
                         ])
def test_soil_passive_carbon_amount(passive_carbon_amount, slow_to_passive_carbon_amount,
                                    active_carbon_to_passive_amount,
                                    passive_carbon_decomposition_amount):
    expected = passive_carbon_amount + slow_to_passive_carbon_amount + active_carbon_to_passive_amount - \
               passive_carbon_decomposition_amount
    assert expected == PoolGasPartition._soil_passive_carbon_amount(passive_carbon_amount,
                                                                    slow_to_passive_carbon_amount,
                                                                    active_carbon_to_passive_amount,
                                                                    passive_carbon_decomposition_amount)
