import pytest
from math import log, exp

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.fertilizer import Fertilizer


# --- Static method tests ---
@pytest.mark.parametrize("cover_factor,days", [
    (0.5333, 20),
    (0.6667, 60),
    (0.8, 4),
])
def test_determine_fraction_phosphorus_remaining(cover_factor, days):
    """Tests _determine_fraction_phosphorus_remaining() in Fertilizer module"""
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
    """Tests _determine_phosphorus_distribution_factor() in Fertilizer module"""
    observe = Fertilizer._determine_phosphorus_distribution_factor(rainfall, runoff)
    expect = 0.034 * exp(3.4 * (runoff / rainfall))
    assert observe == expect


@pytest.mark.parametrize("phosphorus,frac_released,distribution_factor,total_rainfall", [
    (10000000, 1, 0.28347283947, 12300),
    (1295043, 0.4, 0.238947265, 12320),
    (100421, 0.075, 0.3485781, 9183),
])
def test_determine_dissolved_phosphorus_concentration(phosphorus, frac_released, distribution_factor, total_rainfall):
    """Tests _determine_dissolved_phosphorus_concentration() in Fertilizer module"""
    observe = Fertilizer._determine_dissolved_phosphorus_concentration(phosphorus, frac_released, distribution_factor,
                                                                       total_rainfall)
    expect = phosphorus * frac_released * distribution_factor / total_rainfall
    assert observe == expect
