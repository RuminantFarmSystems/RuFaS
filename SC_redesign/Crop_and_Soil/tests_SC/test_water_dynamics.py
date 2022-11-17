import pytest
from SC_redesign.Crop_and_Soil.crop.water_dynamics import *


# ---- helper functions tests ----
@pytest.mark.parametrize("evap,trans", [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 0),
    (-1, 0),
    (0, -1),
    (-1, -1),
    (0.32, 1.357)
])
def test_calc_evapotranspiration(evap, trans):
    """ensure that evapotranspiration is correclty calculated"""
    assert calc_evapotranspiration(evap, trans) == evap + trans


@pytest.mark.parametrize("et,max_et", [
    (1, 1),  # all 1
    (0, 0),  # all 0
    (0, 1),  # evapotranspiration = 0
    (1, 0),  # max_evapotrans = 0
    (1, 0.29),  # fractional max_evapotranspiration
    (0.38, 0.29),  # both fractional
    (135.77, 2001.5),  # arbitrary evapotranspiration < max_evapotranspiration
    (821.0, 533.53)  # arbitrary evapotranspiration > max_evapotranspiration

])
def test_calc_water_deficiency(et, max_et):
    """ensure that water deficiency is properly calculated"""
    if max_et == 0:
        expect = 0
    else:
        expect = 100 * (et / max_et)
    assert calc_water_deficiency(et, max_et) == expect


# ---- initialization functions (reusable) ----
def init_soil(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    soil = Soil()
    for key, val in kwargs.items():
        setattr(soil, key, val)
    return soil


def init_water_dyn(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    water_dyn = WaterDynamics()
    for key, val in kwargs.items():
        setattr(water_dyn, key, val)
    return water_dyn


# ---- member function tests ----
@pytest.mark.parametrize("evap", [0, 1, .5, 0.25, 0.75, 1000, 1563.29])
def test_set_evaporation(evap):
    """check that evaporation is properly set"""
    water_dyn = init_water_dyn()
    water_dyn.set_evaporation(evap)
    assert water_dyn.evaporation == evap


@pytest.mark.parametrize("trans", [0, 1, .5, 0.25, 0.75, 1000, 1563.29])
def test_set_transpiration(trans):
    """check that transpiration is properly set"""
    water_dyn = init_water_dyn()
    water_dyn.set_transpiration(trans)
    assert water_dyn.transpiration == trans


@pytest.mark.parametrize("max", [0, 1, .5, 0.25, 0.75, 1000, 1563.29])
def test_set_max_evapotranspiration(max):
    """check that max_evapotranspiration evapotranspiration is correctly set"""
    water_dyn = init_water_dyn()
    water_dyn.set_max_evapotranspiration(max)
    assert water_dyn.evapotranspiration_max == max

@pytest.mark.parametrize("evap,trans", [
    (1, 1),  # all 1
    (0, 1),  # no evap
    (1, 0),  # no trans
    (0, 0),  # all 0
    (0.48, 0.33),  # arbitrary values
])
def test_update_evapotranspiration(evap, trans):
    """check that evapotranspiration is properly updated"""
    water_dyn = init_water_dyn(evaporation=evap, transpiration=trans)
    water_dyn.update_evapotranspiration()
    assert water_dyn.evapotranspiration == calc_evapotranspiration(evap, trans)


@pytest.mark.parametrize("et,max_et", [
    (1, 1),  # all 1
    (0, 0),  # all 0
    (0, 1),  # evapotranspiration = 0
    (1, 0),  # max_evapotrans = 0
    (1, 0.29),  # fractional max_evapotranspiration
    (0.38, 0.29),  # both fractional
    (135.77, 2001.5),  # arbitrary evapotranspiration < max_evapotranspiration
    (821.0, 533.53)  # arbitrary evapotranspiration > max_evapotranspiration

])
def test_assess_water_deficiency(et, max_et):
    """check that water deficiency is properly updated"""
    water_dyn = init_water_dyn(evapotranspiration=et, evapotranspiration_max=max_et)
    water_dyn.assess_water_deficiency()
    assert water_dyn.water_deficiency == calc_water_deficiency(et, max_et)


@pytest.mark.parametrize("evap,trans,et_max", [
    (50, 50, 100),  # max_evapotranspiration = evap + trans
    (45, 50, 100),  # evap < trans
    (50, 33, 100),  # evap > trans
    (50, 50, 80),  # max_evapotranspiration < evap + trans
    (0.45, 0.50, 0.10),  # fractional
    (132.58, 72.01, 635.2),  # arbitrary
])
def test_cycle_water(evap, trans, et_max):
    """integration test to check that water cycling routines are properly carried out"""
    water_dyn = init_water_dyn()
    water_dyn.cycle_water(evap, trans, et_max)
    expected = [water_dyn.evaporation, water_dyn.transpiration, water_dyn.evapotranspiration,
                water_dyn.evapotranspiration_max, water_dyn.water_deficiency]
    observed = [evap, trans, evap+trans, et_max, calc_water_deficiency(evap+trans, et_max)]
    assert expected == observed
