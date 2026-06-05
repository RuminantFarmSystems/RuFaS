from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.field.soil.carbon_cycling.carbon_cycle import CarbonCycling
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


@pytest.mark.parametrize(
    "layer_thickness, field_size, expected_soil_volume",
    [(66, 44, 29040.0), (0.5, 1.8, 9.0), (2, 9, 180.0)],  # higher value  # arbitrary values  # lower value
)
def test_determine_soil_volume(layer_thickness: float, field_size: float, expected_soil_volume: float) -> None:
    """Checks that soil volume was calculated correctly"""
    assert expected_soil_volume == CarbonCycling._determine_soil_volume(layer_thickness, field_size)


@pytest.mark.parametrize(
    "bulk_density, soil_volume, ",
    [(65, 42), (0.6, 1.3), (1, 9)],  # higher value  # arbitrary values  # lower value
)
def test_determine_soil_mass(bulk_density: float, soil_volume: float) -> None:
    """Checks that soil mass was calculated correctly"""
    expected = bulk_density * soil_volume
    assert expected == CarbonCycling._determine_soil_mass(bulk_density, soil_volume)


@pytest.mark.parametrize(
    "active_carbon_amount, soil_mass, field_size",
    [
        (66, 100, 50),  # higher value
        (0.5, 1.8, 20.5),  # arbitrary values
        (2, 9, 3),  # lower value
    ],
)
def test_determine_soil_active_carbon_fraction(
    active_carbon_amount: float, soil_mass: float, field_size: float
) -> None:
    """Checks that the fraction of active carbon in the soil was calculated correctly"""
    expected = active_carbon_amount * field_size / soil_mass
    assert expected == CarbonCycling._determine_soil_active_carbon_fraction(active_carbon_amount, soil_mass, field_size)


@pytest.mark.parametrize(
    "slow_carbon_amount, soil_mass, field_size",
    [
        (66, 100, 50),  # higher value
        (0.5, 1.8, 20.5),  # arbitrary values
        (2, 9, 3),  # lower value
    ],
)
def test_determine_soil_slow_carbon_fraction(slow_carbon_amount: float, soil_mass: float, field_size: float) -> None:
    """Checks that the fraction of slow carbon in the soil was calculated correctly"""
    expected = slow_carbon_amount * field_size / soil_mass
    assert expected == CarbonCycling._determine_soil_slow_carbon_fraction(slow_carbon_amount, soil_mass, field_size)


@pytest.mark.parametrize(
    "passive_carbon_amount, soil_mass, field_size",
    [
        (66, 100, 50),  # higher value
        (0.5, 1.8, 25.5),  # arbitrary values
        (2, 9, 1),  # lower value
        (None, 100, 2.1),
    ],
)
def test_determine_soil_passive_carbon_fraction(
    passive_carbon_amount: float, soil_mass: float, field_size: float
) -> None:
    """Checks that the fraction of passive carbon in the soil was calculated correctly"""
    expected = passive_carbon_amount * field_size / soil_mass if passive_carbon_amount else 0
    assert expected == CarbonCycling._determine_soil_passive_carbon_fraction(
        passive_carbon_amount, soil_mass, field_size
    )


@pytest.mark.parametrize(
    "soil_active_carbon_fraction, soil_slow_carbon_fraction, soil_passive_carbon_fraction",
    [(0.01, 0.02, 0.03), (0.5, 0.3, 0.16)],  # lower value  # arbitrary values
)
def test_determine_soil_overall_carbon_fraction(
    soil_active_carbon_fraction: float,
    soil_slow_carbon_fraction: float,
    soil_passive_carbon_fraction: float,
) -> None:
    """Checks that the total fraction of carbon in the soil was calculated correctly"""
    expected = soil_active_carbon_fraction + soil_passive_carbon_fraction + soil_slow_carbon_fraction
    assert expected == CarbonCycling._determine_soil_overall_carbon_fraction(
        soil_active_carbon_fraction,
        soil_slow_carbon_fraction,
        soil_passive_carbon_fraction,
    )


@pytest.mark.parametrize(
    "active_carbon_amount, slow_carbon_amount, passive_carbon_amount",
    [
        (1, 2, 3),  # lower value
        (0.5, 0.3, 0.16),  # arbitrary values
        (40, 55, 79),  # higher value
    ],
)
def test_determine_total_soil_carbon_amount(
    active_carbon_amount: float, slow_carbon_amount: float, passive_carbon_amount: float
) -> None:
    """Checks that the total amount of soil carbon was calculated correctly"""
    expected = active_carbon_amount + slow_carbon_amount + passive_carbon_amount
    assert expected == CarbonCycling._determine_total_soil_carbon_amount(
        active_carbon_amount, slow_carbon_amount, passive_carbon_amount
    )


@pytest.mark.parametrize(
    "plant_metabolic_active_carbon_loss, plant_structural_active_carbon_loss, " "plant_structural_slow_carbon_loss",
    [
        (1, 2, 3),  # lower value
        (0.5, 0.3, 0.16),  # arbitrary values
        (40, 55, 79),  # higher value
    ],
)
def test_determine_total_plant_carbon_CO2_loss(
    plant_metabolic_active_carbon_loss: float,
    plant_structural_active_carbon_loss: float,
    plant_structural_slow_carbon_loss: float,
) -> None:
    """Checks that the total amount of plant carbon lost as CO2 was calculated correctly"""
    expected = (
        plant_metabolic_active_carbon_loss + plant_structural_active_carbon_loss + plant_structural_slow_carbon_loss
    )
    assert expected == CarbonCycling._determine_total_plant_carbon_CO2_loss(
        plant_metabolic_active_carbon_loss,
        plant_structural_active_carbon_loss,
        plant_structural_slow_carbon_loss,
    )


@pytest.mark.parametrize(
    "soil_metabolic_active_carbon_loss, soil_structural_active_carbon_loss, " "soil_structural_slow_carbon_loss",
    [
        (1, 2, 3),  # lower value
        (0.5, 0.3, 0.16),  # arbitrary values
        (40, 55, 79),  # higher value
    ],
)
def test_determine_total_soil_carbon_CO2_loss(
    soil_metabolic_active_carbon_loss: float,
    soil_structural_active_carbon_loss: float,
    soil_structural_slow_carbon_loss: float,
) -> None:
    """Checks that the total amount of soil carbon lost as CO2 was calculated correctly"""
    expected = soil_metabolic_active_carbon_loss + soil_structural_active_carbon_loss + soil_structural_slow_carbon_loss
    assert expected == CarbonCycling._determine_total_soil_carbon_CO2_loss(
        soil_metabolic_active_carbon_loss,
        soil_structural_active_carbon_loss,
        soil_structural_slow_carbon_loss,
    )


@pytest.mark.parametrize(
    "active_carbon_to_slow_loss, slow_carbon_co2_lost_amount, " "passive_carbon_co2_lost_amount",
    [
        (1, 2, 3),  # lower value
        (0.5, 0.3, 0.16),  # arbitrary values
        (40, 55, 79),  # higher value
    ],
)
def test_determine_total_decomposition_carbon_CO2_lost(
    active_carbon_to_slow_loss: float,
    slow_carbon_co2_lost_amount: float,
    passive_carbon_co2_lost_amount: float,
) -> None:
    """Checks that the total amount of carbon lost as CO2 during decomposition was calculated correctly"""
    expected = active_carbon_to_slow_loss + slow_carbon_co2_lost_amount + passive_carbon_co2_lost_amount
    assert expected == CarbonCycling._determine_total_decomposition_carbon_CO2_lost(
        active_carbon_to_slow_loss,
        slow_carbon_co2_lost_amount,
        passive_carbon_co2_lost_amount,
    )


@pytest.mark.parametrize(
    "total_plant_carbon_CO2_loss, total_soil_carbon_CO2_loss, " "total_decomposition_carbon_CO2_lost",
    [
        (1, 2, 3),  # lower value
        (0.5, 0.3, 0.16),  # arbitrary values
        (40, 55, 79),  # higher value
    ],
)
def test_determine_total_carbon_CO2_lost(
    total_plant_carbon_CO2_loss: float,
    total_soil_carbon_CO2_loss: float,
    total_decomposition_carbon_CO2_lost: float,
) -> None:
    """Checks that the total amount of carbon lost as CO2 was calculated correctly"""
    expected = total_decomposition_carbon_CO2_lost + total_plant_carbon_CO2_loss + total_soil_carbon_CO2_loss
    assert expected == CarbonCycling._determine_total_carbon_CO2_lost(
        total_plant_carbon_CO2_loss,
        total_soil_carbon_CO2_loss,
        total_decomposition_carbon_CO2_lost,
    )


@pytest.mark.parametrize(
    "layers",
    [
        (
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=40,
                    soil_water_concentration=1.8,
                    field_capacity_water_concentration=1.6,
                    wilting_point_water_concentration=0.9,
                    field_size=5,
                ),
                LayerData(
                    top_depth=40,
                    bottom_depth=120,
                    soil_water_concentration=0.9,
                    field_capacity_water_concentration=1.2,
                    wilting_point_water_concentration=0.8,
                    field_size=5,
                ),
                LayerData(
                    top_depth=120,
                    bottom_depth=200,
                    soil_water_concentration=0.8,
                    field_capacity_water_concentration=0.8,
                    wilting_point_water_concentration=0.3,
                    field_size=5,
                ),
            ]
        ),
        (
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=30,
                    soil_water_concentration=2.8,
                    field_capacity_water_concentration=2.3,
                    wilting_point_water_concentration=1.8,
                    field_size=5,
                ),
                LayerData(
                    top_depth=30,
                    bottom_depth=150,
                    soil_water_concentration=1.9,
                    field_capacity_water_concentration=1.8,
                    wilting_point_water_concentration=0.8,
                    field_size=5,
                ),
                LayerData(
                    top_depth=150,
                    bottom_depth=220,
                    soil_water_concentration=0.8,
                    field_capacity_water_concentration=1,
                    wilting_point_water_concentration=0.2,
                    field_size=5,
                ),
            ]
        ),
        (
            [
                LayerData(
                    top_depth=0,
                    bottom_depth=80,
                    soil_water_concentration=2.3,
                    field_capacity_water_concentration=2.9,
                    wilting_point_water_concentration=1.8,
                    field_size=5,
                ),
                LayerData(
                    top_depth=80,
                    bottom_depth=200,
                    soil_water_concentration=1.4,
                    field_capacity_water_concentration=1.8,
                    wilting_point_water_concentration=0.8,
                    field_size=5,
                ),
                LayerData(
                    top_depth=200,
                    bottom_depth=220,
                    soil_water_concentration=0.8,
                    field_capacity_water_concentration=1,
                    wilting_point_water_concentration=0.6,
                    field_size=5,
                ),
            ]
        ),
    ],
)
def test_soil_carbon_aggregation(layers) -> None:
    """test that attributes are aggregated correctly"""
    data = SoilData(soil_layers=layers, field_size=5)
    cycle = CarbonCycling(data)
    CarbonCycling._determine_soil_volume = MagicMock(return_value=1)
    CarbonCycling._determine_soil_mass = MagicMock(return_value=2)
    CarbonCycling._determine_soil_active_carbon_fraction = MagicMock(return_value=3)
    CarbonCycling._determine_soil_slow_carbon_fraction = MagicMock(return_value=4)
    CarbonCycling._determine_soil_passive_carbon_fraction = MagicMock(return_value=5)
    CarbonCycling._determine_soil_overall_carbon_fraction = MagicMock(return_value=6)
    CarbonCycling._determine_total_soil_carbon_amount = MagicMock(return_value=7)
    CarbonCycling._determine_total_plant_carbon_CO2_loss = MagicMock(return_value=8)
    CarbonCycling._determine_total_soil_carbon_CO2_loss = MagicMock(return_value=9)
    CarbonCycling._determine_total_decomposition_carbon_CO2_lost = MagicMock(return_value=10)
    CarbonCycling._determine_total_carbon_CO2_lost = MagicMock(return_value=11)

    cycle._soil_carbon_aggregation(10)

    assert CarbonCycling._determine_soil_volume.call_count == len(layers)
    assert CarbonCycling._determine_soil_mass.call_count == len(layers)
    assert CarbonCycling._determine_soil_active_carbon_fraction.call_count == len(layers)
    assert CarbonCycling._determine_soil_slow_carbon_fraction.call_count == len(layers)
    assert CarbonCycling._determine_soil_passive_carbon_fraction.call_count == len(layers)
    assert CarbonCycling._determine_soil_overall_carbon_fraction.call_count == len(layers)
    assert CarbonCycling._determine_total_soil_carbon_amount.call_count == len(layers)
    assert CarbonCycling._determine_total_plant_carbon_CO2_loss.call_count == len(layers)
    assert CarbonCycling._determine_total_soil_carbon_CO2_loss.call_count == len(layers)
    assert CarbonCycling._determine_total_decomposition_carbon_CO2_lost.call_count == len(layers)
    assert CarbonCycling._determine_total_carbon_CO2_lost.call_count == len(layers)

    for layer in layers:
        assert layer.soil_overall_carbon_fraction == 6
        assert layer.total_soil_carbon_amount == 7
        assert layer.annual_decomposition_carbon_CO2_lost == 10
        assert layer.annual_carbon_CO2_lost == 11


@pytest.mark.parametrize("rainfall, temp_average, field_size", [(1, 3, 4)])
def test_carbon_cycle(rainfall: float, temp_average: float, field_size: float) -> None:
    """tests that routines are called"""
    data = SoilData(field_size=5)
    cycle = CarbonCycling(data)
    cycle.decomposition.decompose = MagicMock()
    cycle.pool_gas_partition.partition_pool_gas = MagicMock()
    cycle.residue_partition.partition_residue = MagicMock()
    cycle._soil_carbon_aggregation = MagicMock()
    cycle.cycle_carbon(rainfall, temp_average, field_size)

    assert cycle.decomposition.decompose.call_count == 1
    assert cycle.pool_gas_partition.partition_pool_gas.call_count == 1
    assert cycle.residue_partition.partition_residue.call_count == 1
    assert cycle._soil_carbon_aggregation.call_count == 1
