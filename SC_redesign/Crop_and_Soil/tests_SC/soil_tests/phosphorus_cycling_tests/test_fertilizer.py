import pytest
from math import log

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
