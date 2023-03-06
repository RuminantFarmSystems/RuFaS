import pytest
from SC_redesign.Crop_and_Soil.crop.crop_management import *


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
    assert CropManagement._determine_potential_harvest_index(heatfrac, optimal_index) == expect


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
    assert CropManagement._adjust_harvest_index(idx, min_index, deficiency) == expect




@pytest.mark.parametrize("bmass,harv_ind", [
    (1, 1.2),
    (0, 1.2),  # no biomass
    (1, 2.5),  # increased biomass
    (136.5, 1.22)  # arbitrary
])
def test_determine_biomass_cut_from_whole_plant(bmass, harv_ind):
    """ensure that yield is correctly calculated by determine_yield_from_total_biomass()"""
    frac = 1 / (1 + harv_ind)
    assert CropManagement._determine_biomass_cut_from_whole_plant(bmass, harv_ind) == bmass * (1 - frac)


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
    assert data.do_harvest_index_override == expect

# def test_cut_crop():
#     assert False
#
# def test_determine_harvest_index():
#     assert False
#
# def test_dry_down():
#     assert False
#
# def test_kill():
#     assert False
#
# def test_manage_harvest():
#     assert False


# @pytest.mark.parametrize("usr_index,heat_frac,harv_eff", [
#     (None, 0, 1),
#     (None, 0.5, 1),
#     (None, 1, 1),
#     (None, 0.389, 1),
#     (None, 0.5, 0),
#     (None, 0.5, 0.5),
#     (None, 0.5, 0.833),
#
#     (0.9, 0, 1),
#     (0.5, 0, 1),
#     (1.3, 0, 1),
#
#     (0.9, 0.5, 1),
#     (0.9, 1, 1),
#     (0.9, 0.389, 1),
#     (0.9, 0.5, 0),
#     (0.9, 0.5, 0.5),
#     (0.9, 0.5, 0.833),
# ])
# def test_obtain_yields(usr_index, heat_frac, harv_eff):
#     """integration test for obtain_yields()"""
#     # Observe
#     # data = CropData(user_harvest_index=usr_index, heat_fraction=heat_frac, harvest_efficiency=harv_eff,
#     #                 optimal_harvest_index=2.63, min_harvest_index=0.186, water_deficiency=0.337,
#     #                 above_ground_biomass=138.4, dry_down_fraction=0.22, biomass=278.41,
#     #                 optimal_nitrogen_fraction=0.33, optimal_phosphorus_fraction=0.077,
#     #                 yield_nitrogen_fraction=0.281, yield_phosphorus_fraction=0.106)
#     # ylds = CropManagement(data)
#     # ylds.obtain_yields()
#     #
#     # # expect
#     # if usr_index is None:
#     #     harv_indx = CropManagement._determine_potential_harvest_index(heat_frac, 2.63)
#     #     harv_indx = CropManagement._adjust_harvest_index(harv_indx, 0.186, 0.337)
#     # else:
#     #     assert data.harvest_index == usr_index
#     #     harv_indx = usr_index
#     #
#     # assert data.harvest_index == harv_indx
#     #
#     # if heat_frac >= 1.0:
#     #     assert data.is_mature == True
#     #     shoot_mass = CropManagement._adjust_biomass_for_dry_down(138.4, 0.22)
#     # else:
#     #     assert data.is_mature == False
#     #     shoot_mass = 138.4
#     # assert data.above_ground_biomass == shoot_mass
#     #
#     # if harv_indx > 1.0:
#     #     yld_mass = CropManagement._determine_biomass_cut_from_whole_plant(278.41, harv_indx)
#     #     assert data.cut_biomass == yld_mass
#     # else:
#     #     yld_mass = CropManagement._determine_biomass_cut_from_shoot(shoot_mass, harv_indx)
#     #     assert data.cut_biomass == yld_mass
#     #
#     # collected = CropManagement._determine_extracted_yield(yld_mass, harv_eff)
#     # assert data.yield_collected == collected
#     #
#     # if usr_index is None:
#     #     nitro = 0.281 * collected
#     #     phos = 0.106 * collected
#     # else:
#     #     nitro = 0.33 * collected
#     #     phos = 0.077 * collected
#     # assert data.yield_nitrogen == nitro
#     # assert data.yield_phosphorus == phos
#     # assert data.yield_residue == CropManagement._determine_unextracted_yield(yld_mass, harv_eff)
#     assert False
