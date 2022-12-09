import pytest
from SC_redesign.Crop_and_Soil.crop.leaf_area_index import *

@pytest.mark.parametrize("heatfrac,s1,s2", [
    (0.5, 1, 1),  # starting point
    (0.0, 1, 1),  # no heatfrac
    (1.0, 1, 1),  # full heatfrac
    (0.5, 0.33, 1),  # reduced s1
    (0.5, 1, 0.33),  # reduced s2
    (0.5, 0.33, 0.33),  # reduced s1 and s2
    (0.239, 1.2, -2.33),  # arbitrary
    (-1, 1, 1)
])
def test_determine_optimal_leaf_area_fraction(heatfrac, s1, s2):
    """ensure that optimal leaf area fraction is properly calculated by calc_optimal_leaf_area_fraction()"""
    x = heatfrac + exp(s1 - s2*heatfrac)
    if heatfrac/x < 0:
        expect = 0
    else:
        expect = heatfrac/x
    assert LeafAreaIndex.determine_optimal_leaf_area_fraction(heatfrac, s1, s2) == expect

@pytest.mark.parametrize("heatfrac,areafrac", [
    (0.5, 0.5),  # heatfrac = areafrac
    (0.3, 0.5),  # heatfrac < areafrac
    (0.4, 0.2),  # heatfrac > areafrac
    (1, 0.5),  # heatfrac = 1
    (1.3, 0.5),  # heatfrac > 1
    (0.5, 1-1e-9),  # areafrac approx 1
    (0.5, 1e-9),  # areafrac approx 0
    (1e-9, 0.5),  # heatfrac approx 0
    (-2, -1),  # both negative
    (-1, -2),  # both negative
    (0.439, 0.611),  # arbitrary
])
def test_calc_shape_log(heatfrac, areafrac):
    """ensure that log terms are calculated correctly"""
    observe = calc_shape_log(heatfrac, areafrac)
    x = (heatfrac/areafrac) - heatfrac
    assert log(x) == observe


@pytest.mark.parametrize("heatfrac,areafrac", [
    (0, 1),  # heatfrac = 0 -- math domain
    (0, 0.5),  # heatfrac = 0 -- math domain
    (1, 0),  # areafrac = 0 -- division by zero
    (0.5, 0),  # areafrac = 0 -- division by zero
    (0.5, 1),  # areafrac = 1 -- math domain
    (-1, 0.5),  # negative heatfrac -- math domain
    (0.5, -1),  # negative areafrac -- math domain
])
def test_error_calc_shape_log(heatfrac, areafrac):
    """ensure that the errors are thrown for inappropriate input to calc_shape_log()"""
    with pytest.raises(Exception):
        calc_shape_log(heatfrac, areafrac)


@pytest.mark.parametrize("heatfrac1,heatfrac2,areafrac1,areafrac2", [
    (0.3, 0.6, 0.2, 0.4),  # start
    (0.6, 0.3, 0.2, 0.4),  # heatfrac1 > heatfrac2
    (0.3, 0.6, 0.4, 0.2),  # areafrac1 > areafrac2
    (0.3, 0.6, 0.2, 0.2),  # areafrac1 = areafrac2
    (1, 0.6, 0.2, 0.4),  # heatfrac1 = 1
    (0.3, 1, 0.2, 0.4),  # heatfrac2 = 1
    (1.3, 0.6, 0.2, 0.4),  # heatfrac1 > 1
    (1, 1-1e-9, 0.2, 0.4),  # heatfrac1 approx heatfrac2
    (0.135, 0.842, 0.09, 0.321),  # arbitrary
])
def test_calc_shape_parameters(heatfrac1, heatfrac2, areafrac1, areafrac2):
    x = calc_shape_log(heatfrac1, areafrac1)
    y = calc_shape_log(heatfrac2, areafrac2)
    s2 = (x - y) / (heatfrac2 - heatfrac1)
    s1 = x + s2*heatfrac1
    assert calc_shape_parameters(heatfrac1, heatfrac2, areafrac1, areafrac2) == [s1, s2]

# TODO: implement test cases for test_error_calc_shape_parameters()
@pytest.mark.parametrize("heatfrac1,heatfrac2,areafrac1,areafrac2", [
    # shape log errors
    (0, 0.3, 0.2, 0.4),  # heatfrac1 = 0 -- math domain
    (0.5, 0, 0.2, 0.4),  # heatfrac2 = 0 -- math domain
    (0.5, 0.3, 0, 0.4),  # areafrac1 = 0 -- division by zero
    (0.5, 0.3, 0.2, 0),  # areafrac2 = 0 -- division by zero
    (0.5, 0.3, 1, 0.4),  # areafrac1 = 0 -- math domain
    (0.5, 0.3, 0.2, 1),  # areafrac2 = 0 -- math domain
    (-1, 0.3, 0.2, 0.4),  # heatfrac1 < 0 -- math domain
    (0.5, -1, 0.2, 0.4),  # heatfrac2 < 0 -- math domain
    (0.5, 0.3, -1, 0.4),  # areafrac1 < 0 -- math domain
    (0.5, 0.3, 0.2, -1),  # areafrac2 < 0 -- math domain
    (0.3, 0.3, 0.2, 0.4),  # heatfrac1 = heatfrac2 -- division by zero
])
def test_error_calc_shape_parameters(heatfrac1, heatfrac2, areafrac1, areafrac2):
    """check that invalid input to test_error_calc_shape_parameters throws errors"""
    with pytest.raises(ValueError):
        calc_shape_parameters(heatfrac1, heatfrac2, areafrac1, areafrac2)

@pytest.mark.parametrize("frac,prev_frac,max_lai,prev_lai", [
    (1, 1/3, 3, 1),  # start (prevfrac = prev_lai/max_lai)
    (1, 1/3, 3, 2.5),  # increased prev_lai, same prev_frac
    (0.5, 1/3, 3, 1),  # reduced frac
    (0, 1/3, 3, 1),  # frac = 0
    (1, 1/3, 3, 3),  # prev_lai = lai
    (1, 1, 3, 3),  # prev_lai = lai, pref_frac = current frac
    (1.2, 0.657, 3, 2.5),  # arbitrary
])
def test_calc_max_leaf_area_change(frac, prev_frac, max_lai, prev_lai):
    scaled_diff = (frac - prev_frac) * max_lai
    expo = 1 - exp(5 * prev_lai - max_lai)
    assert calc_max_leaf_area_change(frac, prev_frac, max_lai, prev_lai) == scaled_diff * expo

# ---- Initializer functions
def init_lai(**kwargs):
    """helper function to create GrowthConstraint instance, with specified attributes"""
    lai = LeafAreaIndex()
    for key, val in kwargs.items():
        setattr(lai, key, val)
    return lai

# ---- Member functions

# @pytest.mark.parametrize("heatfrac", [-1, 0, 0.11, 0.25, 0.5, 0.8, 1])
# def test_determine_optimal_leaf_area_fraction(heatfrac):
#     """ensure that the optimal leaf area fraction is properly set by determine_optimal_leaf_area_fraction"""
#     lai = init_lai(heat_fraction=heatfrac, first_heat_fraction_point=0.15, second_heat_fraction_point=0.50,
#                    first_leaf_fraction_point=0.01, second_leaf_fraction_point=0.95)
#     lai.determine_optimal_leaf_area_fraction()
#     assert [lai._lai_shapes[0], lai._lai_shapes[1]] == calc_shape_parameters(0.15, 0.50, 0.01, 0.95)
#     assert lai.optimal_leaf_area_fraction == calc_optimal_leaf_area_fraction(heatfrac, lai._lai_shapes[0],
#                                                                              lai._lai_shapes[1])

@pytest.mark.parametrize("leaf_area,optimal_fraction", [
    (1, 1),
    (2, 1/3),
    (2.44, 0.359)
])
def test_shift_leaf_area_time(leaf_area, optimal_fraction):
    """ensure that the time window is properly shifted for LAI traits with shift_leaf_area_time()"""
    lai = init_lai(leaf_area_index=leaf_area, optimal_leaf_area_fraction=optimal_fraction)
    lai.shift_leaf_area_time()
    assert lai.previous_leaf_area_index == leaf_area
    assert lai.previous_optimal_leaf_area_fraction == optimal_fraction

@pytest.mark.parametrize("max_h,opt_lai_frac,expect", [
    (1, 1, 1),
    (20, 1, 20),
    (20, 0.5, 20*sqrt(0.5)),
    (20, 1.5, 20),
    (232.765, 0.83, 232.765*sqrt(0.83))
])
def test_determine_canopy_height(max_h, opt_lai_frac, expect):
    """ensure that canopy height is calculated as expected by determine_canopy_height()"""
    lai = init_lai(max_canopy_height=max_h, optimal_leaf_area_fraction=opt_lai_frac)
    lai.determine_canopy_height()
    assert lai.canopy_height == expect

@pytest.mark.parametrize("frac,lai,expect", [
    (None, None, (0, 0)),
    (None, 1.3, (0, 1.3)),
    (0.33, None, (0.33, 0)),
    (0.33, 1.3, (0.33, 1.3)),
])
def test_check_for_previous_leaf_area_values(frac, lai, expect):
    """ensure that previous LAI values are properly set with check_previous_leaf_area_values()"""
    obj = init_lai(previous_optimal_leaf_area_fraction=frac, previous_leaf_area_index=lai)
    obj.check_previous_leaf_area_values()
    assert (obj.previous_optimal_leaf_area_fraction, obj.previous_leaf_area_index) == expect

@pytest.mark.parametrize("frac,prev_frac,max_lai,prev_lai", [
    (0.5, 0.3, 3, 1),
    (0.5, 0.5, 3, 1),
    (0.5, 0.6, 3, 1),
    (0.5, 0, 3, 1),
    (0.5, 0, 3, 0),
    (0.79, 0.62, 2.8, 1.75)
])
def test_determine_max_leaf_area_change(frac, prev_frac, max_lai, prev_lai):
    lai = init_lai(optimal_leaf_area_fraction=frac, previous_optimal_leaf_area_fraction=prev_frac,
                   max_leaf_area_index=max_lai, previous_leaf_area_index=prev_lai)
    lai.determine_max_leaf_area_change()
    assert lai.max_leaf_area_change == calc_max_leaf_area_change(frac, prev_frac, max_lai, prev_lai)

@pytest.mark.parametrize("max_change,growth,expect", [
    (1, 1, 1),
    (100, 1, 100),
    (100, 1.3, 100),
    (100, 0.8, 100*sqrt(0.8)),
    (12.359, 0.633, 12.359*sqrt(0.633))
])
def test_determine_leaf_area_added(max_change, growth, expect):
    """ensure that added leaf area is calculated correctly by determine_leaf_area_added()"""
    lai = init_lai(max_leaf_area_change=max_change, growth_factor=growth)
    lai.determine_leaf_area_added()
    assert lai.leaf_area_added == expect

@pytest.mark.parametrize("previous,added,expect", [
    (0, 1, 1),  # start = 0
    (1, 1, 2),  # start = 1
    (0, -1, 0),  # loss < 0
    (10, -15, 0),  # lose more than possible
    (122.374, 15.99, 122.374 + 15.99)  # arbitrary
])
def test_add_leaf_area(previous, added, expect):
    """ensure that leaf area index is properly updated by add_leaf_area()"""
    lai = init_lai(previous_leaf_area_index=previous, leaf_area_added=added)
    lai.add_leaf_area()
    assert lai.leaf_area_index == expect

@pytest.mark.parametrize("current,cutoff,expect", [
    (0.5, 0.9, False),
    (0.9, 0.9, False),
    (0.95, 0.9, True),
    (1.3, 1, True)
])
def test_check_for_senescence(current, cutoff, expect):
    """check that senescence is properly triggered by check_for_senescence()"""
    lai = init_lai(heat_fraction=current, senescent_heat_fraction=cutoff)
    lai.check_for_senescence()
    assert lai.is_in_senescence == expect

@pytest.mark.parametrize("opt_lai_frac,heatfrac,cutoff", [
    (1, 1.2, 1-1e-9),  # cutoff approx 1
    (0.9, 0.87, 0.8),
    (0.5, 0.43, 0.44)
])
def test_senesce_leaf_area(opt_lai_frac, heatfrac, cutoff):
    """check that leaf area is correctly set with senesce_leaf_area()"""
    lai = init_lai(optimal_leaf_area_fraction=opt_lai_frac, heat_fraction=heatfrac, senescent_heat_fraction=cutoff)
    lai.senesce_leaf_area()
    assert lai.leaf_area_index == calc_senescent_leaf_area_index(heatfrac, cutoff, opt_lai_frac)

@pytest.mark.parametrize("opt_lai_frac,heatfrac,cutoff", [])
def test_calc_senescent_leaf_area_index(opt_lai_frac, heatfrac, cutoff):
    """check that LAI is calculated correctly during senescence with calc_senescent_leaf_area_index()"""
    if cutoff == 1:
        x = 1 - heatfrac
    else:
        x = (1 - heatfrac) / (1 - cutoff)
    y = x * opt_lai_frac
    if y > 0:
        expect = y
    else:
        expect = 0
    assert calc_senescent_leaf_area_index(heatfrac, cutoff, opt_lai_frac) == expect

# TODO: rewrite test to reflect update functions
@pytest.mark.parametrize("heatfrac", [0, 0.2, 0.5, 0.75, 0.9, 0.95, 1, 1.2, -1])
def test_grow_canopy(heatfrac):
    """integration test for leaf area processes via grow_canopy()"""
    # observe
    lai = init_lai(heat_fraction=heatfrac, leaf_area_index=0.7,
                   first_heat_fraction_point=0.2, second_heat_fraction_point=0.33, first_leaf_fraction_point=0.05,
                   second_leaf_fraction_point=0.95, max_canopy_height=2.5, growth_factor=0.95, max_leaf_area_index=3.0,
                   senescent_heat_fraction=0.9, previous_leaf_area_index=0.1, previous_optimal_leaf_area_fraction=0.01)
    lai.grow_canopy()
    # expect
    shapes = calc_shape_parameters(0.2, 0.33, 0.05, 0.95)
    assert lai._lai_shapes == shapes
    optimal_lai = calc_optimal_leaf_area_fraction(heatfrac, shapes[0], shapes[1])
    assert lai.optimal_leaf_area_fraction == optimal_lai
    assert lai.canopy_height == 2.5*sqrt(optimal_lai)
    if heatfrac <= 0.9:  # normal growth
        assert lai.is_in_senescence is False
        max_change = calc_max_leaf_area_change(optimal_lai, 0.01, 3.0, 0.1)
        assert lai.max_leaf_area_change == max_change
        added = max_change*sqrt(0.95)
        if max_change < added:  # when heatfrac = 0, no growth occurs
            added = max_change
        assert lai.leaf_area_added == added
        assert lai.leaf_area_index == 0.1 + added
        assert lai.previous_leaf_area_index == lai.leaf_area_index
        assert lai.previous_optimal_leaf_area_fraction == optimal_lai
    else:  # senescence
        assert lai.is_in_senescence is True
        assert lai.leaf_area_index == calc_senescent_leaf_area_index(heatfrac, 0.9, optimal_lai)