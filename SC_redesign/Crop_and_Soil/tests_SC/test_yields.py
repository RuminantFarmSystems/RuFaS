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
def init_yields(**kwargs):
    """helper function to initialize Yields object, with specified attributes"""
    yld = Yields()
    for key, val in kwargs.items():
        setattr(yld, key, val)
    return yld


@pytest.mark.parametrize("frac,expect", [
    (0, False),
    (0.5, False),
    (1, True),
    (1.5, True)
])
def test_is_mature_property(frac, expect):
    """check that the is_mature property is properly assigning maturity by heat fraction"""
    ylds = init_yields(heat_fraction=frac)
    assert ylds.is_mature == expect

@pytest.mark.parametrize("usr_index, expect", [
    (1.0, True),
    (None, False)
])
def test_given_harvest_index_property(usr_index, expect):
    """test the class knows if harvest index override is specified"""
    ylds = init_yields(user_harvest_index=usr_index)
    assert ylds.given_harvest_index == expect


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
    ylds = init_yields(user_harvest_index=usr_index, heat_fraction=heat_frac, harvest_efficiency=harv_eff,
                       optimal_harvest_index=2.63, min_harvest_index=0.186, water_deficiency=0.337,
                       above_ground_biomass=138.4, dry_down_percent=0.22, biomass=278.41,
                       optimal_nitrogen_fraction=0.33, optimal_phosphorus_fraction=0.077,
                       yield_nitrogen_fraction=0.281, yield_phosphorus_fraction=0.106)
    ylds.obtain_yields()

    # expect
    if usr_index is None:
        harv_indx = Yields.determine_potential_harvest_index(heat_frac, 2.63)
        harv_indx = Yields.adjust_harvest_index(harv_indx, 0.186, 0.337)
    else:
        assert ylds.harvest_index == usr_index
        harv_indx = usr_index

    assert ylds.harvest_index == harv_indx

    if heat_frac >= 1.0:
        assert ylds.is_mature == True
        shoot_mass = Yields.adjust_biomass_for_dry_down(138.4, 0.22)
    else:
        assert ylds.is_mature == False
        shoot_mass = 138.4
    assert ylds.above_ground_biomass == shoot_mass

    if harv_indx > 1.0:
        yld_mass = Yields.determine_yield_from_total_biomass(278.41, harv_indx)
        assert ylds.crop_yield == yld_mass
    else:
        yld_mass = Yields.determine_yield_from_shoot_biomass(shoot_mass, harv_indx)
        assert ylds.crop_yield == yld_mass

    collected = Yields.determine_extracted_yield(yld_mass, harv_eff)
    assert ylds.yield_collected == collected

    if usr_index is None:
        nitro = 0.281 * collected
        phos = 0.106 * collected
    else:
        nitro = 0.33 * collected
        phos = 0.077 * collected
    assert ylds.collected_nitrogen == nitro
    assert ylds.collected_phosphorus == phos
    assert ylds.residue_created == Yields.determine_unextracted_yield(yld_mass, harv_eff)

# @pytest.mark.parametrize("idx,min_index,deficiency", [
#     (0, 0.5, 0.5),  # 0 = harvest index < min
#     (0.2, 0.5, 0.5),  # harvest index < min
#     (-1, 0.5, 0.5),  # harvest index < 0
# ])
# def test_warn_calc_actual_harvest_index(idx, min_index, deficiency):
#     """ensure that warnings are raised appropriately by calc_actual_harvest_index()"""
#     with pytest.warns() as record:
#         Yields.calc_actual_harvest_index(idx, min_index, deficiency)
#     assert len(record) > 0

# def test_error_calc_actual_harvest_index(idx, min_index, deficiency):
#     with pytest.w

# from math import exp
#
#
# def mock_crop(HU = 0.1, PHU = 8.8, LAI = 2.3, yield_actual = 3.0, P = 0.5, N = 0.7, bmass = 3.2 \
#     ,fr_PHU = .13, HI_opt = 2.1, HI_max = 5.5, HI_min = 1.7, gamma_wu = 2.1 \
#     ,bio_AG = 5.0, dry_down_per = .75, HI_actual = 10.3, yld_max = 4.7, harv_eff = .8 \
#     ,fr_N = .15, fr_P = .31):
#     """
#     Description:
#         Creates a mock object of the BaseCrop class to be used for unittesting the functions
#         in the yields.py file.
#
#     Args:
#         (float) HU: crop attribute accumulated_HU
#         (float) PHU: crop attribute PHU
#         (float) LAI: crop attribute LAI_actual
#         (float) yld: crop attribute yield_actual
#         (float) P: crop attribute bio_P
#         (float) N: crop attribute bio_N
#         (float) bmass: crop attribute biomass_actual
#
#     Return:
#         returns the BaseCrop mock object set with the proper attribute values
#     """
#
#     mcrop = MagicMock(base_crop.BaseCrop)
#     mcrop.accumulated_HU = HU
#     mcrop.PHU = PHU
#     mcrop.LAI_actual = LAI
#     mcrop.yield_actual = yield_actual
#     mcrop.bio_P = P
#     mcrop.bio_N = N
#     mcrop.biomass_actual = bmass
#     mcrop.fr_PHU = fr_PHU
#     mcrop.HI_opt = HI_opt
#     mcrop.HI_max = HI_max
#     mcrop.HI_min = HI_min
#     mcrop.gamma_wu = gamma_wu
#     mcrop.bio_AG = bio_AG
#     mcrop.biomass_dry_down_percent = dry_down_per
#     mcrop.HI_actual = HI_actual
#     mcrop.yield_max = yld_max
#     mcrop.harvest_eff = harv_eff
#     mcrop.fr_N = fr_N
#     mcrop.fr_P = fr_P
#
#     return mcrop
#
#
# #the following tests are for the calc_HI_max() function
# #since there is only 1 attribute changed this test consitutes entirety of testing for the function
# def test_calc_HI_max_correctly_sets_HI_max():
#     crop = mock_crop()
#     calc_HI_max(crop)
#
#     assert pytest.approx(crop.HI_max) == 2.1 * ((100*.13)/(100*.13 + exp(11.1 - (10 * .13))))
#
#
# #the following tests are the for the calc_HI_act() function
# def test_calc_HI_act_correctly_sets_HI_actual():
#     crop = mock_crop()
#     calc_HI_act(crop)
#
#     term1 = 5.5 - 1.7
#     exp_part = exp(6.13 - (0.883 * 2.1))
#     term2 = 2.1 / (2.1 + exp_part)
#
#     assert pytest.approx(crop.HI_actual) == term1 * term2 + 1.7
#
# #the following tests are for the calc_dry_down() function
# def test_calc_dry_down_correctly_sets_bio_AG():
#     crop = mock_crop()
#     calc_dry_down(crop)
#
#     assert pytest.approx(crop.bio_AG) == 5.0 - (5.0 * .75)
#
# #the following tests are for the calc_yield_max() function
# def test_calc_yield_max_correctly_sets_yield_max():
#     crop = mock_crop()
#     calc_yield_max(crop)
#
#     assert pytest.approx(crop.yield_max) == 5.0 * 10.3
#
# #the following tests are for the calc_yield_act() function
# def test_calc_yield_act_correctly_sets_yield_act():
#     crop = mock_crop()
#     calc_yield_act(crop)
#
#     assert pytest.approx(crop.yield_actual) == 4.7 * .8
#
# #the following tests are for the calc_nutrient_removal() function
# def test_calc_nutrient_removal_correctly_sets_N_yield():
#     crop = mock_crop()
#     calc_nutrient_removal(crop)
#
#     assert pytest.approx(crop.N_yield) == .15 * 3.0
#
# def test_calc_nutrient_removal_correctly_sets_P_yield():
#     crop = mock_crop()
#     calc_nutrient_removal(crop)
#
#     assert pytest.approx(crop.P_yield) == .31 * 3.0
#
# def test_calc_nutrient_removal_sets_all():
#     crop = mock_crop()
#     calc_nutrient_removal(crop)
#
#     test_list = [
#         pytest.approx(crop.N_yield) == .15 * 3.0,
#         pytest.approx(crop.P_yield) == .31 * 3.0,
#     ]
#
#     assert all(test_list)
#
#
# #The following tests are for the cut() function in yields.py
# def test_cut_correctly_sets_accumulated_HU():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.accumulated_HU) == 0.1 * (1 - .33)
#
# def test_cut_correctly_sets_fr_PHU():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.fr_PHU) == (0.1 * (1 - .33)) / 8.8
#
# def test_cut_correctly_sets_LAI_actual():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.LAI_actual) == 2.3 * (1 - .33)
#
# def test_cut_correctly_sets_fr_LAI_max_to_zero():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.fr_LAI_max) == 0.0
#
# def test_cut_correctly_sets_biomass_actual():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.biomass_actual) == 3.2 - 3.0
#
# def test_cut_correctly_sets_bio_P():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33)
#
# def test_cut_correctly_sets_bio_N():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33)
#
# def test_cut_correctly_sets_ET_annual_to_zero():
#     crop = mock_crop()
#     cut(crop,0.33)
#
#     assert pytest.approx(crop.ET_annual) == 0
#
# def test_cut_correctly_sets_all():
#     crop = mock_crop()
#     cut(crop,0.33)
#     test_list = [
#         pytest.approx(crop.accumulated_HU) == 0.1 * (1 - .33),
#         pytest.approx(crop.fr_PHU) == (0.1 * (1 - .33)) / 8.8,
#         pytest.approx(crop.LAI_actual) == 2.3 * (1 - .33),
#         pytest.approx(crop.fr_LAI_max) == 0.0,
#         pytest.approx(crop.biomass_actual) == 3.2 - 3.0,
#         pytest.approx(crop.bio_P) == 0.5 * (1 - 0.33),
#         pytest.approx(crop.bio_N) == 0.7 * (1 - 0.33),
#         pytest.approx(crop.ET_annual) == 0
#     ]
#
#     assert all(test_list)
#
#
#
#
#
