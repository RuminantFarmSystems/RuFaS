import pytest
# from unittest.mock import MagicMock
from SC_redesign.Crop_and_Soil.soil.carbon_cycling.carbon_cycle import CarbonCycle
# from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
# from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS,\
    CUBIC_MILLIMETERS_TO_CUBIC_METERS


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
