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
