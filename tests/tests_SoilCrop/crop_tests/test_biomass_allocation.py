import pytest

from SC_redesign.Crop_and_Soil.crop.biomass_allocation import BiomassAllocation
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from math import exp


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
    result = BiomassAllocation._intercept_radiation(rad, ext, lai)
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
    assert BiomassAllocation._determine_max_accumulation(rad, eff) == expected


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
    assert BiomassAllocation._determine_accumulated_biomass(factor, max_growth) == max_growth * factor


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
    assert BiomassAllocation._determine_above_ground_biomass(frac, bmass) == expect


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
    assert BiomassAllocation._determine_below_ground_biomass(frac, bmass) == bmass * frac


# ---- member function tests ----
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
    data = CropData(light_extinction=ext, leaf_area_index=1.87, light_use_efficiency=conv, growth_factor=gfact,
                    root_fraction=rfrac, biomass=89.0)
    bioal = BiomassAllocation(data)
    bioal.allocate_biomass(light)

    # photosynthesize
    energy = BiomassAllocation._intercept_radiation(light, ext, lai=1.87)
    max_growth = BiomassAllocation._determine_max_accumulation(energy, conv)
    growth = BiomassAllocation._determine_accumulated_biomass(gfact, max_growth)
    mass = 89.0 + growth
    # TODO: test photosynthesize() and partition_biomass() separately?
    # partition_biomass
    green = BiomassAllocation._determine_above_ground_biomass(rfrac, mass)
    root = BiomassAllocation._determine_below_ground_biomass(rfrac, mass)

    assert data.usable_light == energy
    assert data.biomass_growth_max == max_growth
    assert data.previous_biomass == 89.0
    assert data.biomass_growth == growth
    assert data.biomass == mass
    assert data.above_ground_biomass == green
    assert data.root_biomass == root
