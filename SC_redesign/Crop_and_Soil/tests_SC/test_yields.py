import pytest
from SC_redesign.Crop_and_Soil.crop.yields import *


# ---- Test Static Functions ----
@pytest.mark.parametrize("heatfrac,optimal_index", [
    (0, 1),
    (1, 1),
    (0.5, 1),
    (1.2, 1),
    (0.5, 0),
    (0.5, 100),
    (0.326, 12.2)  # arbitrary
])
def test_determine_potential_harvest_index(heatfrac, optimal_index):
    """ensure that the potential harvest index is properly calculated"""
    top = 100 * heatfrac
    bottom = (100 * heatfrac) + exp(11.1 - (10 * heatfrac))
    expect = optimal_index * (top / bottom)
    assert Yields.determine_potential_harvest_index(heatfrac, optimal_index) == expect


@pytest.mark.parametrize("idx,min_index,deficiency", [
    (1, .5, .5),  # start case
    (0, 0, 0),  # all zeros
    (0, 0.5, 0.5),  # zero harvest index
    (0, 0.5, 0.2),
    (-1, 0.5, 0.5),  # index < 0
    (1, 0, 0.5),  # zero min
    (1, 0.5, 1),  # high deficiency
    (1, 0.5, 0),  # no deficiency
    (1.35, 0.83, 0.29)  # arbitrary
])
def test_adjust_harvest_index(idx, min_index, deficiency):
    """ensure that actual harvest index is properly calculated by calc_actual_harvest_index()"""
    if min_index < 0:
        adj_min = 0
    else:
        adj_min = min_index

    if idx < adj_min:
        adj_idx = adj_min
    else:
        adj_idx = idx

    diff = adj_idx - adj_min
    bottom = deficiency + exp(6.13 - 0.883 * deficiency)
    expect = diff * deficiency / bottom + adj_min
    if expect < 0:
        expect = 0
    assert Yields.adjust_harvest_index(idx, min_index, deficiency) == expect


@pytest.mark.parametrize("start,percent,expect", [
    (1, 0, 1),  # no dry down
    (1, .2, .8),  # 20% loss
    (215.3, 0.347, (1 - 0.347) * 215.3)  # arbitrary
])
def test_adjust_biomass_for_dry_down(start, percent, expect):
    """ensure that dry-down is properly calculated by adjust_biomass_for_drydown()"""
    assert Yields.adjust_biomass_for_dry_down(start, percent) == pytest.approx(expect)


@pytest.mark.parametrize("ag_biomass,harv_ind", [
    (1, 1),  # both ones
    (1, 0),  # 0 harvest index
    (0, 1),  # no biomass
    (26, 0.8),  # arbitrary biomass > index
    (0.33, 0.8)  # arbitrary biomass < index
])
def test_determine_yield_from_shoot_biomass(ag_biomass, harv_ind):
    """ensure that yield is correctly calculated by determine_yield_from_shoot_biomass()"""
    expect = ag_biomass * harv_ind
    assert Yields.determine_yield_from_shoot_biomass(ag_biomass, harv_ind) == expect


@pytest.mark.parametrize("bmass,harv_ind", [
    (1, 1.2),
    (0, 1.2),  # no biomass
    (1, 2.5),  # increased biomass
    (136.5, 1.22)  # arbitrary
])
def test_determine_yield_from_total_biomass(bmass, harv_ind):
    """ensure that yield is correctly calculated by determine_yield_from_total_biomass()"""
    frac = 1 / (1 + harv_ind)
    assert Yields.determine_yield_from_total_biomass(bmass, harv_ind) == bmass * (1 - frac)


@pytest.mark.parametrize("crop_yield,harvest_efficiency", [
    (1, 1),
    (8, 0.9),
    (13, 0.896),
    (22, 0.5663)
])
def test_determine_extracted_yield(crop_yield, harvest_efficiency):
    """ensure that extracted yield is correctly calculated with determine_extracted_yield()"""
    expect = crop_yield * harvest_efficiency
    assert Yields.determine_extracted_yield(crop_yield, harvest_efficiency) == expect


@pytest.mark.parametrize("crop_yield,harvest_efficiency", [
    (12, -1),
    (13, 1.001)
])
def test_error_determine_extracted_yield(crop_yield, harvest_efficiency):
    """ensure that determine_exctracted_yield() throws errors when harvest_efficiency is out of bounds"""
    with pytest.raises(ValueError):
        Yields.determine_extracted_yield(crop_yield, harvest_efficiency)


@pytest.mark.parametrize("crop_yield,harvest_efficiency", [
    (1, 1),
    (8, 0.9),
    (13, 0.896),
    (22, 0.5663)
])
def test_determine_unextracted_yield(crop_yield, harvest_efficiency):
    """check that un-removed yield is properly calculated"""
    assert Yields.determine_unextracted_yield(crop_yield, harvest_efficiency) == crop_yield*(1-harvest_efficiency)


@pytest.mark.parametrize("crop_yield,harvest_efficiency", [
    (12, -1),
    (13, 1.001)
])
def test_error_determine_unextracted_yield(crop_yield, harvest_efficiency):
    """ensure that determine_exctracted_yield() throws errors when harvest_efficiency is out of bounds"""
    with pytest.raises(ValueError):
        Yields.determine_unextracted_yield(crop_yield, harvest_efficiency)


# ---- Test Member functions
@pytest.mark.parametrize("frac,expect", [
    (0, False),
    (0.5, False),
    (1, True),
    (1.5, True)
])
def test_is_mature_property(frac, expect):
    """check that the is_mature property is properly assigning maturity by heat fraction"""
    data = CropData(heat_fraction=frac)
    assert data.is_mature == expect

@pytest.mark.parametrize("usr_index, expect", [
    (1.0, True),
    (None, False)
])
def test_given_harvest_index_property(usr_index, expect):
    """test the class knows if harvest index override is specified"""
    data = CropData(user_harvest_index=usr_index)
    ylds = Yields(data)
    assert data.has_given_harvest_index == expect


@pytest.mark.parametrize("usr_index,heat_frac,harv_eff", [
    (None, 0, 1),
    (None, 0.5, 1),
    (None, 1, 1),
    (None, 0.389, 1),
    (None, 0.5, 0),
    (None, 0.5, 0.5),
    (None, 0.5, 0.833),

    (0.9, 0, 1),
    (0.5, 0, 1),
    (1.3, 0, 1),

    (0.9, 0.5, 1),
    (0.9, 1, 1),
    (0.9, 0.389, 1),
    (0.9, 0.5, 0),
    (0.9, 0.5, 0.5),
    (0.9, 0.5, 0.833),
])
def test_obtain_yields(usr_index, heat_frac, harv_eff):
    """integration test for obtain_yields()"""
    # Observe
    data = CropData(user_harvest_index=usr_index, heat_fraction=heat_frac, harvest_efficiency=harv_eff,
                    optimal_harvest_index=2.63, min_harvest_index=0.186, water_deficiency=0.337,
                    above_ground_biomass=138.4, dry_down_fraction=0.22, biomass=278.41,
                    optimal_nitrogen_fraction=0.33, optimal_phosphorus_fraction=0.077,
                    yield_nitrogen_fraction=0.281, yield_phosphorus_fraction=0.106)
    ylds = Yields(data)
    ylds.obtain_yields()

    # expect
    if usr_index is None:
        harv_indx = Yields.determine_potential_harvest_index(heat_frac, 2.63)
        harv_indx = Yields.adjust_harvest_index(harv_indx, 0.186, 0.337)
    else:
        assert data.harvest_index == usr_index
        harv_indx = usr_index

    assert data.harvest_index == harv_indx

    if heat_frac >= 1.0:
        assert data.is_mature == True
        shoot_mass = Yields.adjust_biomass_for_dry_down(138.4, 0.22)
    else:
        assert data.is_mature == False
        shoot_mass = 138.4
    assert data.above_ground_biomass == shoot_mass

    if harv_indx > 1.0:
        yld_mass = Yields.determine_yield_from_total_biomass(278.41, harv_indx)
        assert data.crop_yield == yld_mass
    else:
        yld_mass = Yields.determine_yield_from_shoot_biomass(shoot_mass, harv_indx)
        assert data.crop_yield == yld_mass

    collected = Yields.determine_extracted_yield(yld_mass, harv_eff)
    assert data.yield_collected == collected

    if usr_index is None:
        nitro = 0.281 * collected
        phos = 0.106 * collected
    else:
        nitro = 0.33 * collected
        phos = 0.077 * collected
    assert data.collected_nitrogen == nitro
    assert data.collected_phosphorus == phos
    assert data.yield_residue == Yields.determine_unextracted_yield(yld_mass, harv_eff)
