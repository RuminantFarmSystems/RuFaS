import pytest
from unittest.mock import MagicMock
from math import log, exp

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer


# --- Static method tests ---
@pytest.mark.parametrize("cover_factor,days", [
    (0.5333, 20),
    (0.6667, 60),
    (0.8, 4),
])
def test_determine_fraction_phosphorus_remaining(cover_factor, days):
    """Tests that the fraction of phosphorus remaining in the available pool after absorption by soil is correctly
        calculated."""
    observe = Fertilizer._determine_fraction_phosphorus_remaining(cover_factor, days)
    expect = (-0.16 * log(days)) + cover_factor
    if expect < 0:
        expect = 0
    assert observe == expect


@pytest.mark.parametrize("rainfall,runoff", [
    (5.6, 1.2),
    (8.3, 8.3),
    (4.7, 0.8),
    (18.6, 3.4498274),
])
def test_determine_phosphorus_distribution_factor(rainfall, runoff):
    """Tests that the distribution factor for partitioning solubilized phosphorus between runoff and infiltration is
        determined correctly."""
    observe = Fertilizer._determine_phosphorus_distribution_factor(rainfall, runoff)
    expect = 0.034 * exp(3.4 * (runoff / rainfall))
    assert observe == expect


@pytest.mark.parametrize("phosphorus,frac_released,distribution_factor,total_rainfall", [
    (10000000, 1, 0.28347283947, 12300),
    (1295043, 0.4, 0.238947265, 12320),
    (100421, 0.075, 0.3485781, 9183),
])
def test_determine_dissolved_phosphorus_concentration(phosphorus, frac_released, distribution_factor, total_rainfall):
    """Tests that the concentration of dissolved phosphorus is runoff is correctly calculated."""
    observe = Fertilizer._determine_dissolved_phosphorus_concentration(phosphorus, frac_released, distribution_factor,
                                                                       total_rainfall)
    expect = phosphorus * frac_released * distribution_factor / total_rainfall
    assert observe == expect


# --- Helper function tests ---
@pytest.mark.parametrize("added_phosphorus,initial_labile_phosphorus,field_size", [
    (3, 6.8, 1.5),
    (0.87, 1.235, 1),
    (8.9284921, 5.18393, 2.393481),
    (0.34, 2.495821, 4.10184),
    (2.39854, 0, 3.29184)
])
def test_add_to_labile_phosphorus(added_phosphorus: float, initial_labile_phosphorus: float, field_size: float) -> None:
    """Tests that the labile phosphorus content of the top soil layer has phosphorus correctly added to it."""
    data = SoilData()
    data.soil_layers[0].labile_phosphorus_content = initial_labile_phosphorus
    fert = Fertilizer(data)

    fert._add_to_labile_phosphorus(added_phosphorus, field_size)
    observe = fert.data.soil_layers[0].labile_phosphorus_content

    expect = initial_labile_phosphorus * field_size
    expect += added_phosphorus
    expect /= field_size

    assert observe == expect


@pytest.mark.parametrize("initial_pool_amount,available_pool_amount,days_since_application,cover_type,field_size", [
    (100, 100, 1, "BARE", 1.56),
    (120, 96, 5, "GRASSED", 2.876),
    (96, 21, 40, "RESIDUE_COVER", 1.243),
    (100, 15, 35, "GRASSED", 2.3954),  # All phosphorus should be removed from pool
    (90, 0, 78, "RESIDUE_COVER", 0.897),  # No phosphorus left in available pool
])
def test_absorb_phosphorus_from_available_pool(initial_pool_amount: float, available_pool_amount: float,
                                               days_since_application: int, cover_type: str, field_size: float) -> None:
    """Tests that soil absorbs the correct amount of phosphorus from the available phosphorus pool"""
    data = SoilData(full_available_phosphorus_pool=initial_pool_amount, available_phosphorus_pool=available_pool_amount,
                    days_since_application=days_since_application, cover_type=cover_type)
    fert = Fertilizer(data)

    fert._add_to_labile_phosphorus = MagicMock()
    fert._determine_fraction_phosphorus_remaining = MagicMock(return_value=0.2)

    fraction_to_remain_in_pool = 0.2
    amount_to_remove = available_pool_amount - (initial_pool_amount * fraction_to_remain_in_pool)
    if amount_to_remove < 0:
        amount_to_remove = available_pool_amount
    expected_remaining_pool_amount = available_pool_amount - amount_to_remove

    fert._absorb_phosphorus_from_available_pool(field_size)

    fert._add_to_labile_phosphorus.assert_called_with(amount_to_remove, field_size)
    fert._determine_fraction_phosphorus_remaining.assert_called_with(fert.data.cover_factor,
                                                                     days_since_application)
    assert fert.data.available_phosphorus_pool == expected_remaining_pool_amount


@pytest.mark.parametrize("field_size,recalcitrant_amount,rainfall_events", [
    (1, 20, 2),
    (2.34, 17.837, 2),
    (1.87, 10.39548, 3),
    (1.09, 3.294, 5)
])
def test_absorb_phosphorus_from_recalcitrant_pool(field_size: float, recalcitrant_amount: float,
                                                  rainfall_events: int) -> None:
    """Tests that correct amount of phosphorus is removed from the recalcitrant pool and is added to the top soil
        layer's labile phosphorus content"""
    data = SoilData(recalcitrant_phosphorus_pool=recalcitrant_amount,
                    rain_events_after_fertilizer_application=rainfall_events)
    fert = Fertilizer(data)

    fert._add_to_labile_phosphorus = MagicMock()

    expected_amount_to_remove = recalcitrant_amount * fert.data.solubilizing_factor
    expected_remaining_amount = recalcitrant_amount - expected_amount_to_remove

    fert._absorb_phosphorus_from_recalcitrant_pool(field_size)
    observe = fert.data.recalcitrant_phosphorus_pool

    fert._add_to_labile_phosphorus.assert_called_with(expected_amount_to_remove, field_size)
    assert observe == expected_remaining_amount


@pytest.mark.parametrize("pool_amount,days_since_application,rainfall_events,rainfall,runoff,field_size", [
    (30, 0, 1, 30, 2, 3),
    (15.434, 1, 1, 14, 1.9899, 2.9384),
    (0.98321, 15, 1, 7, 0.35, 1.342),
    (10, 13, 2, 9, 0.818, 0.95),
    (17, 21, 3, 11, 1.3, 3.45)
])
def test_leach_phosphorus(pool_amount: float, days_since_application: float,
                          rainfall_events: int, rainfall: float, runoff: float, field_size: float) -> None:
    """Tests that the correct amounts of phosphorus to be removed by runoff and soil absorption are calculated."""
    data = SoilData(days_since_application=days_since_application,
                    rain_events_after_fertilizer_application=rainfall_events)
    if rainfall_events == 1:
        data.available_phosphorus_pool = pool_amount
    else:
        data.recalcitrant_phosphorus_pool = pool_amount
    fert = Fertilizer(data)

    fert._determine_phosphorus_distribution_factor = MagicMock(return_value=0.05)
    fert._determine_dissolved_phosphorus_concentration = MagicMock(return_value=0.05)

    pool_amount_mg = pool_amount * 1000000
    solubilized_amount = pool_amount * fert.data.solubilizing_factor
    concentration = 0.05    # Matches what is mocked for _determine_dissolved_phosphorus_concentration()
    rainfall_liters = rainfall * field_size * 10000
    runoff_liters = runoff * field_size * 10000
    dissolved_phosphorus_runoff_mg = runoff_liters * concentration
    dissolved_phosphorus_runoff_kg = dissolved_phosphorus_runoff_mg / 1000000
    adsorbed_phosphorus_kg = max(0, solubilized_amount - dissolved_phosphorus_runoff_kg)
    expected = {"runoff_phosphorus": dissolved_phosphorus_runoff_kg, "absorbed_phosphorus": adsorbed_phosphorus_kg}

    observed = fert._determine_leached_phosphorus(rainfall, runoff, field_size, pool_amount)

    fert._determine_phosphorus_distribution_factor.assert_called_with(rainfall, runoff)
    fert._determine_dissolved_phosphorus_concentration(pool_amount_mg, fert.data.solubilizing_factor, 0.05,
                                                       rainfall_liters)
    assert observed == pytest.approx(expected)
