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
    (0, 1),  # evapotrans = 0
    (1, 0),  # max_evapotrans = 0
    (1, 0.29),  # fractional max
    (0.38, 0.29),  # both fractional
    (135.77, 2001.5),  # arbitrary evapotrans < max
    (821.0, 533.53)  # arbitrary evapotrans > max

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


def init_wd(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    wd = WaterDynamics()
    for key, val in kwargs.items():
        setattr(wd, key, val)
    return wd


# ---- member function tests ----
@pytest.mark.parametrize("evap", [0, 1, .5, 0.25, 0.75, 1000, 1563.29])
def test_update_evaporation(evap):
    """check that evaporation is properly copied from soil"""
    soil = init_soil(evaporation=evap)
    wd = init_wd()
    wd.update_evaporation(soil)


@pytest.mark.parametrize("trans", [0, 1, .5, 0.25, 0.75, 1000, 1563.29])
def test_update_transpiration(trans):
    """check that transpiration is properly copied from soil"""
    soil = init_soil(transpiration=trans)
    wd = init_wd()
    wd.update_transpiration(soil)


@pytest.mark.parametrize("evap,trans", [
    (1, 1),  # all 1
    (0, 1),  # no evap
    (1, 0),  # no trans
    (0, 0),  # all 0
    (0.48, 0.33),  # arbitrary values
])
def test_update_evapotranspiration(evap, trans):
    """check that evapotranspiration is properly updated"""
    wd = init_wd(evaporation=evap, transpiration=trans)
    wd.update_evapotranspiration()
    assert wd.evapotranspiration == calc_evapotranspiration(evap, trans)


@pytest.mark.parametrize("et,max_et", [
    (1, 1),  # all 1
    (0, 0),  # all 0
    (0, 1),  # evapotrans = 0
    (1, 0),  # max_evapotrans = 0
    (1, 0.29),  # fractional max
    (0.38, 0.29),  # both fractional
    (135.77, 2001.5),  # arbitrary evapotrans < max
    (821.0, 533.53)  # arbitrary evapotrans > max

])
def test_update_water_deficiency(et, max_et):
    """check that water deficiency is properly updated"""
    wd = init_wd(evapotranspiration=et, evapotranspiration_max=max_et)
    wd.assess_water_deficiency()
    assert wd.water_deficiency == calc_water_deficiency(et, max_et)


@pytest.mark.parametrize("evap,trans,et_max", [
    (50, 50, 100),  # max = evap + trans
    (45, 50, 100),  # evap < trans
    (50, 33, 100),  # evap > trans
    (50, 50, 80),  # max < evap + trans
    (0.45, 0.50, 0.10),  # fractional
    (132.58, 72.01, 635.2),  # arbitrary
])
def test_cycle_water(evap, trans, et_max):
    """integration test to check that water cycling routines are properly carried out"""
    soil = init_soil(evaporation=evap, transpiration=trans, evapotranspiration=evap+trans,
                     evapotranspiration_max=et_max)
    wd = init_wd()
    wd.cycle_water(soil)
    expected = [wd.evaporation, wd.transpiration, wd.evapotranspiration, wd.evapotranspiration_max, wd.water_deficiency]
    observed = [evap, trans, evap+trans, et_max, calc_water_deficiency(evap+trans, et_max)]
    assert expected == observed
