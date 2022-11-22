import pytest

from SC_redesign.Crop_and_Soil.crop.biomass_allocation import *


# ---- helper function tests ----
@pytest.mark.parametrize("rad,ext,lai", [
    (1, 1, 1),
    (0, 0, 0),
    (1, 0, 1),
    (.2, -.38, 0.75),
    (.2, .38, 0.75)
])
def test_calc_intercepted_radiation(rad, ext, lai):
    """ensure that intercepted radiation is correctly calculated by calc_intercepted_radiation()"""
    h_photo = 0.5 * rad * (1 - exp(-ext * lai))
    result = calc_intercepted_radiation(rad, ext, lai)
    assert result == h_photo


@pytest.mark.parametrize("rad,eff,expected", [
    (0, 0, 0),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 0),
    (1, 1, 1),
    (1000, 0.33, 330),  # arbitrary
    (1961.67, 0.217, 1961.67 * 0.217),
    (18.5, 22.19, 18.5 * 22.19)  # rad < eff
])
def test_calc_max_accumulation(rad, eff, expected):
    """test that maximum biomass accumulation is properly calculated with calc_max_accumulation()"""
    assert calc_max_accumulation(rad, eff) == expected


@pytest.mark.parametrize("factor,max_growth", [
    (1, 0),
    (0, 1),
    (1, 1),
    (0.8, 103.84),
    (1.2, 103.84),
    (1.2, 873.2)
])
def test_calc_biomass_accumulation(factor, max_growth):
    """ensure that biomass growth is correctly calculated by calc_biomass_accumulation()"""
    assert calc_biomass_accumulation(factor, max_growth) == max_growth * factor


@pytest.mark.parametrize("frac,bmass", [
    (1, 0),
    (0, 1),
    (0, 0),
    (1, 1),
    (1.00, 836.2),  # arbitrary: frac = 1
    (0.46, 836.2),  # arbitrary: frac < 1
    (1.27, 836.2),  # arbitrary: frac > 1
    (-1, 836.2),  # arbitrary: frac < 0
    (0.59, 529.33),  # arbitrary 2
])
def test_calc_above_ground_biomass(frac, bmass):
    """ensure that above ground biomass is correctly calculated"""
    expect = bmass * (1 - frac)
    assert calc_above_ground_biomass(frac, bmass) == expect


@pytest.mark.parametrize("frac,bmass", [
    (1, 0),
    (0, 1),
    (0, 0),
    (1, 1),
    (1.00, 836.2),  # arbitrary: frac = 1
    (0.46, 836.2),  # arbitrary: frac < 1
    (1.27, 836.2),  # arbitrary: frac > 1
    (-1, 836.2),  # arbitrary: frac < 0
    (0.59, 529.33),  # arbitrary 2
])
def test_calc_below_ground_biomass(frac, bmass):
    """ensure that below ground biomass is correctly calculated"""
    assert calc_below_ground_biomass(frac, bmass) == bmass * frac


# ---- initialization functions (reusable) ----
def init_bioal(**kwargs):
    """helper function to create BiomassAllocation instance, with specified attributes"""
    bioal = BiomassAllocation()
    for key, val in kwargs.items():
        setattr(bioal, key, val)
    return bioal


# ---- member function tests ----
@pytest.mark.parametrize("rad,ext,lai", [
    (1, 1, 1),
    (0, 0, 0),
    (1, 0, 1),
    (.6, -.42, 0.35),
    (.26, .28, 0.44)
])
def test_intercept_radiation(rad, ext, lai):
    """check that usable_light is properly updated"""
    bioal = init_bioal(light_extinction=ext, leaf_area_index=lai)
    bioal.intercept_radiation(rad)
    assert bioal.usable_light == calc_intercepted_radiation(rad, ext, lai)


@pytest.mark.parametrize("rad, eff", [
    (0, 1),
    (1, 0),
    (1, 1),
    (1350.86, 15.21),  # arbitrary rad >> eff
    (20.7, 15.3),  # rad near eff
    (12.86, 20.37)  # rad < eff
])
def test_determine_max_growth(rad, eff):
    """ensure that max_evapotranspiration growth is properly updated"""
    bioal = init_bioal(light_conversion=eff, usable_light=rad)
    bioal.determine_max_growth()
    assert bioal.biomass_growth_max == calc_max_accumulation(rad, eff)


@pytest.mark.parametrize("start,factor,gmax", [
    (10, 1, 1000),
    (.8, 1, 1000),
    (10, .8, 1000),
    (8, .75, 1000),
    (8, .75, 833.9),
    (8, 1.2, 833.9)
])
def test_accumulate_biomass(start, factor, gmax):
    """check that biomass attributes are correctly updated by accumulate_biomass()"""
    bioal = init_bioal(biomass=start, growth_factor=factor, biomass_growth_max=gmax)
    bioal.accumulate_biomass()
    expect_growth = calc_biomass_accumulation(factor, gmax)
    expect_end = start + expect_growth

    assert bioal.previous_biomass == start
    assert bioal.biomass == expect_end
    assert bioal.biomass_growth == expect_growth


@pytest.mark.parametrize("light,ext,conv,gfact,rfrac", [
    (1000, 0.7, 20, 1, 1/3),  # start
    (1000, 0.7, 20, 1, 0.66),  # increased root proportion
    (1000, 0.7, 20, 0.83, 0.33),  # restricted growth
    (1000, 0.7, 16.3, 1, 0.33),  # reduced energy conversion
    (1000, 0.8, 20, 1, 0.33),  # greater light extinction
    (824.6, 0.7, 20, 1, 0.33),  # lower incoming light
    (2372.55, 0.29, 15.17, 0.663, 0.205),  # arbitrary
])
def test_allocate_biomass(light, ext, conv, gfact, rfrac):
    """integration check to check that biomass gets allocated correctly"""
    bioal = init_bioal(light_extinction=ext, leaf_area_index=1.87, light_conversion=conv, growth_factor=gfact,
                       root_fraction=rfrac, biomass=89.0)
    bioal.allocate_biomass(light)

    # photosynthesize
    energy = calc_intercepted_radiation(light, ext, lai=1.87)
    max_growth = calc_max_accumulation(energy, conv)
    growth = calc_biomass_accumulation(gfact, max_growth)
    mass = 89.0 + growth
    # partition_biomass
    green = calc_above_ground_biomass(rfrac, mass)
    root = calc_below_ground_biomass(rfrac, mass)

    assert bioal.usable_light == energy
    assert bioal.biomass_growth_max == max_growth
    assert bioal.previous_biomass == 89.0
    assert bioal.biomass_growth == growth
    assert bioal.biomass == mass
    assert bioal.green_biomass == green
    assert bioal.root_biomass == root
