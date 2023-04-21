import pytest
from unittest.mock import MagicMock
from SC_redesign.Crop_and_Soil.soil.carbon_cycling.carbon_cycle import CarbonCycle
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS,\
    CUBIC_MILLIMETERS_TO_CUBIC_METERS
# from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
# from SC_redesign.Crop_and_Soil.soil.carbon_cycling.decomposition import Decomposition
# from SC_redesign.Crop_and_Soil.soil.carbon_cycling.pool_gas_partition import PoolGasPartition
# from SC_redesign.Crop_and_Soil.soil.carbon_cycling.residue_partition import ResiduePartition


@pytest.mark.parametrize("layer_thickness, field_size", [
    (66, 44),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_determine_soil_volume(layer_thickness: float, field_size: float) -> None:
    """Checks that soil volume was calculated correctly"""
    expected = (layer_thickness * field_size * HECTARES_TO_SQUARE_MILLIMETERS) * CUBIC_MILLIMETERS_TO_CUBIC_METERS
    assert expected == CarbonCycle._determine_soil_volume(layer_thickness, field_size)


@pytest.mark.parametrize("bulk_density, soil_volume", [
    (65, 42),  # higher value
    (0.6, 1.3),  # arbitrary values
    (1, 9)  # lower value
])
def test_determine_soil_mass(bulk_density: float, soil_volume: float) -> None:
    """Checks that soil mass was calculated correctly"""
    expected = bulk_density * soil_volume
    assert expected == CarbonCycle._determine_soil_mass(bulk_density, soil_volume)


@pytest.mark.parametrize("active_carbon_amount, soil_mass", [
    (66, 100),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_determine_soil_active_carbon_fraction(active_carbon_amount: float, soil_mass: float) -> None:
    """Checks that the fraction of active carbon in the soil was calculated correctly"""
    expected = active_carbon_amount/soil_mass
    assert expected == CarbonCycle._determine_soil_active_carbon_fraction(active_carbon_amount, soil_mass)


@pytest.mark.parametrize("slow_carbon_amount, soil_mass", [
    (66, 100),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_determine_soil_slow_carbon_fraction(slow_carbon_amount: float, soil_mass: float) -> None:
    """Checks that the fraction of slow carbon in the soil was calculated correctly"""
    expected = slow_carbon_amount/soil_mass
    assert expected == CarbonCycle._determine_soil_slow_carbon_fraction(slow_carbon_amount, soil_mass)


@pytest.mark.parametrize("passive_carbon_amount, soil_mass", [
    (66, 100),  # higher value
    (0.5, 1.8),  # arbitrary values
    (2, 9)  # lower value
])
def test_determine_soil_passive_carbon_fraction(passive_carbon_amount: float, soil_mass: float) -> None:
    """Checks that the fraction of passive carbon in the soil was calculated correctly"""
    expected = passive_carbon_amount/soil_mass
    assert expected == CarbonCycle._determine_soil_passive_carbon_fraction(passive_carbon_amount, soil_mass)


@pytest.mark.parametrize("soil_active_carbon_fraction, soil_slow_carbon_fraction, soil_passive_carbon_fraction", [
    (0.01, 0.02, 0.03),  # lower value
    (0.5, 0.3, 0.16)  # arbitrary values
])
def test_determine_soil_overall_carbon_fraction(soil_active_carbon_fraction: float,
                                                soil_slow_carbon_fraction: float,
                                                soil_passive_carbon_fraction: float) -> None:
    """Checks that the total fraction of carbon in the soil was calculated correctly"""
    expected = soil_active_carbon_fraction + soil_passive_carbon_fraction + soil_slow_carbon_fraction
    assert expected == CarbonCycle._determine_soil_overall_carbon_fraction(soil_active_carbon_fraction,
                                                                           soil_slow_carbon_fraction,
                                                                           soil_passive_carbon_fraction)


@pytest.mark.parametrize("active_carbon_amount, slow_carbon_amount, passive_carbon_amount", [
    (1, 2, 3),  # lower value
    (0.5, 0.3, 0.16),  # arbitrary values
    (40, 55, 79)  # higher value
])
def test_determine_total_soil_carbon_amount(active_carbon_amount: float,
                                            slow_carbon_amount: float,
                                            passive_carbon_amount: float) -> None:
    """Checks that the total amount of soil carbon was calculated correctly"""
    expected = active_carbon_amount + slow_carbon_amount + passive_carbon_amount
    assert expected == CarbonCycle._determine_total_soil_carbon_amount(active_carbon_amount,
                                                                       slow_carbon_amount,
                                                                       passive_carbon_amount)


@pytest.mark.parametrize("plant_metabolic_active_carbon_loss, plant_structural_active_carbon_loss, "
                         "plant_structural_slow_carbon_loss", [
                            (1, 2, 3),  # lower value
                            (0.5, 0.3, 0.16),  # arbitrary values
                            (40, 55, 79)  # higher value
                         ])
def test_determine_total_plant_carbon_CO2_loss(plant_metabolic_active_carbon_loss: float,
                                               plant_structural_active_carbon_loss: float,
                                               plant_structural_slow_carbon_loss: float) -> None:
    """Checks that the total amount of plant carbon lost as CO2 was calculated correctly"""
    expected = plant_metabolic_active_carbon_loss + plant_structural_active_carbon_loss + \
        plant_structural_slow_carbon_loss
    assert expected == CarbonCycle._determine_total_plant_carbon_CO2_loss(plant_metabolic_active_carbon_loss,
                                                                          plant_structural_active_carbon_loss,
                                                                          plant_structural_slow_carbon_loss)


@pytest.mark.parametrize("soil_metabolic_active_carbon_loss, soil_structural_active_carbon_loss, "
                         "soil_structural_slow_carbon_loss", [
                            (1, 2, 3),  # lower value
                            (0.5, 0.3, 0.16),  # arbitrary values
                            (40, 55, 79)  # higher value
                         ])
def test_determine_total_soil_carbon_CO2_loss(soil_metabolic_active_carbon_loss: float,
                                              soil_structural_active_carbon_loss: float,
                                              soil_structural_slow_carbon_loss: float) -> None:
    """Checks that the total amount of soil carbon lost as CO2 was calculated correctly"""
    expected = soil_metabolic_active_carbon_loss + soil_structural_active_carbon_loss + \
        soil_structural_slow_carbon_loss
    assert expected == CarbonCycle._determine_total_soil_carbon_CO2_loss(soil_metabolic_active_carbon_loss,
                                                                         soil_structural_active_carbon_loss,
                                                                         soil_structural_slow_carbon_loss)


@pytest.mark.parametrize("active_carbon_to_slow_loss, slow_carbon_co2_lost_amount, "
                         "passive_carbon_co2_lost_amount", [
                            (1, 2, 3),  # lower value
                            (0.5, 0.3, 0.16),  # arbitrary values
                            (40, 55, 79)  # higher value
                         ])
def test_determine_total_decomposition_carbon_CO2_lost(active_carbon_to_slow_loss: float,
                                                       slow_carbon_co2_lost_amount: float,
                                                       passive_carbon_co2_lost_amount: float) -> None:
    """Checks that the total amount of carbon lost as CO2 during decomposition was calculated correctly"""
    expected = active_carbon_to_slow_loss + slow_carbon_co2_lost_amount + passive_carbon_co2_lost_amount
    assert expected == CarbonCycle._determine_total_decomposition_carbon_CO2_lost(active_carbon_to_slow_loss,
                                                                                  slow_carbon_co2_lost_amount,
                                                                                  passive_carbon_co2_lost_amount)


@pytest.mark.parametrize("total_plant_carbon_CO2_loss, total_soil_carbon_CO2_loss, "
                         "total_decomposition_carbon_CO2_lost", [
                            (1, 2, 3),  # lower value
                            (0.5, 0.3, 0.16),  # arbitrary values
                            (40, 55, 79)  # higher value
                         ])
def test_determine_total_carbon_CO2_lost(total_plant_carbon_CO2_loss: float,
                                         total_soil_carbon_CO2_loss: float,
                                         total_decomposition_carbon_CO2_lost: float) -> None:
    """Checks that the total amount of carbon lost as CO2 was calculated correctly"""
    expected = total_decomposition_carbon_CO2_lost + total_plant_carbon_CO2_loss + total_soil_carbon_CO2_loss
    assert expected == CarbonCycle._determine_total_carbon_CO2_lost(total_plant_carbon_CO2_loss,
                                                                    total_soil_carbon_CO2_loss,
                                                                    total_decomposition_carbon_CO2_lost)


@pytest.mark.parametrize("layers", [
    ([LayerData(top_depth=0, bottom_depth=40, soil_water_concentration=1.8, field_capacity_water_concentration=1.6,
                wilting_point_water_concentration=0.9),
      LayerData(top_depth=40, bottom_depth=120, soil_water_concentration=0.9, field_capacity_water_concentration=1.2,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=120, bottom_depth=200, soil_water_concentration=0.8, field_capacity_water_concentration=0.8,
                wilting_point_water_concentration=0.3)]),
    ([LayerData(top_depth=0, bottom_depth=30, soil_water_concentration=2.8, field_capacity_water_concentration=2.3,
                wilting_point_water_concentration=1.8),
      LayerData(top_depth=30, bottom_depth=150, soil_water_concentration=1.9, field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=150, bottom_depth=220, soil_water_concentration=0.8, field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.2)]),
    ([LayerData(top_depth=0, bottom_depth=80, soil_water_concentration=2.3, field_capacity_water_concentration=2.9,
                wilting_point_water_concentration=1.8),
      LayerData(top_depth=80, bottom_depth=200, soil_water_concentration=1.4,
                field_capacity_water_concentration=1.8,
                wilting_point_water_concentration=0.8),
      LayerData(top_depth=200, bottom_depth=220, soil_water_concentration=0.8, field_capacity_water_concentration=1,
                wilting_point_water_concentration=0.6)])
])
def test_soil_carbon_aggregation(layers) -> None:
    """test that attributes are aggregated correctly"""
    data = SoilData(soil_layers=layers)
    cycle = CarbonCycle(data)
    CarbonCycle._determine_soil_volume = MagicMock(return_value=1)
    CarbonCycle._determine_soil_mass = MagicMock(return_value=2)
    CarbonCycle._determine_soil_active_carbon_fraction = MagicMock(return_value=3)
    CarbonCycle._determine_soil_slow_carbon_fraction = MagicMock(return_value=4)
    CarbonCycle._determine_soil_passive_carbon_fraction = MagicMock(return_value=5)
    CarbonCycle._determine_soil_overall_carbon_fraction = MagicMock(return_value=6)
    CarbonCycle._determine_total_soil_carbon_amount = MagicMock(return_value=7)
    CarbonCycle._determine_total_plant_carbon_CO2_loss = MagicMock(return_value=8)
    CarbonCycle._determine_total_soil_carbon_CO2_loss = MagicMock(return_value=9)
    CarbonCycle._determine_total_decomposition_carbon_CO2_lost = MagicMock(return_value=10)
    CarbonCycle._determine_total_carbon_CO2_lost = MagicMock(return_value=11)

    cycle._soil_carbon_aggregation(10)

    assert CarbonCycle._determine_soil_volume.call_count == len(layers)
    assert CarbonCycle._determine_soil_mass.call_count == len(layers)
    assert CarbonCycle._determine_soil_active_carbon_fraction.call_count == len(layers)
    assert CarbonCycle._determine_soil_slow_carbon_fraction.call_count == len(layers)
    assert CarbonCycle._determine_soil_passive_carbon_fraction.call_count == len(layers)
    assert CarbonCycle._determine_soil_overall_carbon_fraction.call_count == len(layers)
    assert CarbonCycle._determine_total_soil_carbon_amount.call_count == len(layers)
    assert CarbonCycle._determine_total_plant_carbon_CO2_loss.call_count == len(layers)
    assert CarbonCycle._determine_total_soil_carbon_CO2_loss.call_count == len(layers)
    assert CarbonCycle._determine_total_decomposition_carbon_CO2_lost.call_count == len(layers)
    assert CarbonCycle._determine_total_carbon_CO2_lost.call_count == len(layers)

    for layer in layers:
        assert layer.soil_overall_carbon_fraction == 6
        assert layer.total_soil_carbon_amount == 7
        assert layer.total_decomposition_carbon_CO2_lost == 10
        assert layer.total_carbon_CO2_lost == 11

#
# @pytest.mark.parametrize("rainfall, crop, temp_average, field_size", [
#     (1, CropData(yield_residue=300), 3, 4)
# ])
# def test_carbon_cycle(rainfall: float, crop: CropData, temp_average: float, field_size: float) -> None:
#     """tests that routines are called"""
#     data = SoilData()
#     cycle = CarbonCycle(data)
#     Decomposition.decompose = MagicMock()
#     PoolGasPartition.partition_pool_gas = MagicMock()
#     ResiduePartition.partition_residue = MagicMock()
#     cycle._soil_carbon_aggregation = MagicMock()
#
#     cycle.cycle_carbon(rainfall, crop, temp_average, field_size)
#
#     assert Decomposition.decompose.call_count == 1
#     assert PoolGasPartition.partition_pool_gas.call_count == 1
#     assert ResiduePartition.partition_residue.call_count == 1
