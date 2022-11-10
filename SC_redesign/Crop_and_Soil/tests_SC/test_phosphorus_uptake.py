import pytest

from SC_redesign.Crop_and_Soil.crop.phosphorus_uptake import *

# ---- initialization functions (reusable) ----
def init_pu(**kwargs):
    """helper function to create PhosphorusUptake instance, with specified attributes"""
    pu = PhosphorusUptake()
    for key, val in kwargs.items():
        setattr(pu, key, val)
    return pu


@pytest.mark.parametrize(("optimal_P","actual_P","mature_frac","potential_inc"),[
    (0,0,0,0),
    (1,1,1,1)
])
def test_calc_potential_phosphorus_uptake(optimal_P, actual_P, mature_frac, potential_inc):

    if optimal_P >= actual_P:
        part1 = optimal_P - actual_P
        part2 = 4 * mature_frac * potential_inc
        expected = 1.5 * min(part1, part2)
    else:
        expected = 0

    assert calc_potential_phosphorus_uptake(optimal_P, actual_P, mature_frac, potential_inc) == expected






