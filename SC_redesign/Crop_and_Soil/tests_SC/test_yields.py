import pytest
from SC_redesign.Crop_and_Soil.crop.yields import *


@pytest.mark.parametrize("heatfrac,optimal_index", [
    (0, 1),
    (1, 1),
    (0.5, 1),
    (1.2, 1),
    (0.5, 0),
    (0.5, 100),
    (0.326, 12.2)  # arbitrary
])
def test_calc_potential_harvest_index(heatfrac, optimal_index):
    """ensure that the potential harvest index is properly calculated"""
    top = 100 * heatfrac
    bottom = (100 * heatfrac) + exp(11.1 - (10 * heatfrac))
    expect = optimal_index * (top/bottom)
    assert Yields.calc_potential_harvest_index(heatfrac, optimal_index) == expect

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
@pytest.mark.filterwarnings("ignore")  # ignore warnings for these tests
def test_calc_actual_harvest_index(idx, min_index, deficiency):
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
    assert Yields.calc_actual_harvest_index(min_index, idx, deficiency) == expect


def init_yields(**kwargs):
    """helper function to initialize Yields object, with specified attributes"""
    yld = Yields()
    for key, val in kwargs.items():
        setattr(yld, key, val)
    return yld

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
    """ensure that potential harvest index is properly updated by determine_potential_harvest_index()"""
    yld = init_yields(heat_fraction=heatfrac, optimal_harvest_index=optimal_index)
    yld.determine_potential_harvest_index()
    assert yld.potential_harvest_index == Yields.calc_potential_harvest_index(heatfrac, optimal_index)



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
