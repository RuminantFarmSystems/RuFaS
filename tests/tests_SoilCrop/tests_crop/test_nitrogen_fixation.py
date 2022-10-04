<<<<<<< HEAD
"""
RUFAS: Ruminant Farm Systems Model
File name: test_nitrogen_fixation.py
Description: Implements test cases
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from webbrowser import get
from RUFAS.routines.field.crop.nitrogen_fixation import *
from RUFAS.routines.field.crop.crop_types.base_crop import BaseCrop
from RUFAS.routines.field.soil.soil import Soil

from unittest.mock import MagicMock
import pytest

def mock_crop(pot_N_up_each_layer = [21.1],fr_PHU = 0.5, z_root = 640.3, fix_nitrogen = True):
    mcrop = MagicMock(BaseCrop)

    mcrop.pot_N_up_each_layer = pot_N_up_each_layer
    mcrop.fr_PHU = fr_PHU
    mcrop.z_root = z_root
    mcrop.fix_nitrogen = fix_nitrogen

    return mcrop

def mock_soil_layer(NO3 = 12.7,soil_water = 3.1,fc_water = 2.7,bottom_depth = 893.8):
    mlayer = MagicMock(Soil.SoilLayer)

    mlayer.NO3 = NO3
    mlayer.soil_water = soil_water
    mlayer.fc_water = fc_water 
    mlayer.bottom_depth = bottom_depth
    
    
    return mlayer

def mock_soil(soil_layers = [mock_soil_layer()]):
    msoil = MagicMock(Soil)

    msoil.soil_layers = soil_layers
    
    return msoil


#calc_N_demand()
def test_calc_N_demand_correctly_calculates_nitrogen_demand():
    crop = mock_crop()
    soil = mock_soil()

    assert pytest.approx(calc_N_demand(crop,soil.soil_layers)) == max(21.1-12.7, 0)

#calc_f_sw()
def test_calc_f_sw_correctly_calculates_soil_water_factor_non_zero_FC():
    soil = mock_soil()

    assert pytest.approx(calc_f_sw(soil.soil_layers)) == 3.1 / (0.85 * 2.7)

def test_calc_f_sw_correctly_calculates_soil_water_factor_zero_FC():
    soil = mock_soil(soil_layers = [mock_soil_layer(fc_water=0)])

    assert pytest.approx(calc_f_sw(soil.soil_layers)) == 0

#calc_f_NO3()
def test_calc_f_NO3_correctly_calculates_growth_factor_small_sum():
    soil = mock_soil(soil_layers = [mock_soil_layer(NO3 = 100)])

    assert pytest.approx(calc_f_NO3(soil.soil_layers)) == 1

def test_calc_f_NO3_correctly_calculates_growth_factor_med_sum():
    soil = mock_soil(soil_layers = [mock_soil_layer(NO3 = 300)])

    assert pytest.approx(calc_f_NO3(soil.soil_layers)) == 1.5 - 0.0005 * 300

def test_calc_f_NO3_correctly_calculates_growth_factor_large_sum():
    soil = mock_soil(soil_layers = [mock_soil_layer(NO3 = 371.4)])

    assert pytest.approx(calc_f_NO3(soil.soil_layers)) == 0


#calc_f_gr()
def test_calc_f_gr_1():
    crop = mock_crop(fr_PHU = 0.15)

    assert pytest.approx(calc_f_gr(crop)) == 0

def test_calc_f_gr_2():
    crop = mock_crop(fr_PHU = 0.3)

    assert pytest.approx(calc_f_gr(crop)) == 6.67 * 0.3 - 1

def test_calc_f_gr_3():
    crop = mock_crop(fr_PHU = 0.55)

    assert pytest.approx(calc_f_gr(crop)) == 1

def test_calc_f_gr_4():
    crop = mock_crop(fr_PHU = 0.75)

    assert pytest.approx(calc_f_gr(crop)) == 3.75 - 5 * 0.75

def test_calc_f_gr_5():
    crop = mock_crop(fr_PHU = 0.9)

    assert pytest.approx(calc_f_gr(crop)) == 0



#get_root_accessible_layers()
def test_get_root_accessible_layers_correctly_returns_layers_non_zero_z_root():
    crop = mock_crop()
    soil = mock_soil()

    assert pytest.approx(get_root_accessible_layers(soil,crop)) == soil.soil_layers

def test_get_root_accessible_layers_correctly_returns_layers_zero_z_root():
    crop = mock_crop(z_root = 0.0)
    soil = mock_soil()

    assert pytest.approx(get_root_accessible_layers(soil,crop)) == []


#calc_N_fixation()...assumes dependencies work properly
def test_calc_N_fixation_correctly_calculates_fix_nitrogen_fixing_crop():
    crop = mock_crop()
    soil = mock_soil()

    accessible_layers = get_root_accessible_layers(soil, crop)
    f_gr = calc_f_gr(crop)
    f_NO3 = calc_f_NO3(accessible_layers)
    f_sw = calc_f_sw(accessible_layers)
    N_demand = calc_N_demand(crop, accessible_layers) 

    assert pytest.approx(calc_N_fixation(soil,crop)) == min(N_demand * f_gr * min(f_sw,f_NO3,1),N_demand)

def test_calc_N_fixation_correctly_calculates_fix_non_nitrogen_fixing_crop():
    crop = mock_crop(fix_nitrogen = False)
    soil = mock_soil()

    assert pytest.approx(calc_N_fixation(soil,crop)) == 0






    
=======
import pytest
from RUFAS.routines.field.crop.nitrogen_fixation import *


@pytest.mark.parametrize("depth,bounds,expect", [
    (0.2, [0.25, 0.5, 0.75, 1.0], 0),  # first layer
    (0.3, [0.25, 0.5, 0.75, 1.0], 1),  # second layer
    (0.6, [0.25, 0.5, 0.75, 1.0], 2),  # third layer
    (0.8, [0.25, 0.5, 0.75, 1.0], 3),  # fourth layer
    (2, [0.25, 0.5, 0.75, 1.0], 3),  # deeper than deepest layer
    (0, [0.25, 0.5, 0.75, 1.0], None),  # no roots
    (-0.5, [0.25, 0.5, 0.75, 1.0], None),  # negative roots (invalid)
])
def test_get_root_accessible_layer(depth, bounds, expect):
    assert get_deepest_root_accessible_layer(root_depth=depth, layer_bounds=bounds) == expect


@pytest.mark.parametrize("hf,exp", [
    (0, 0),  # first piece
    (0.15, 0),  # first boundary
    (0.2, (6.67 * 0.2) - 1),  # second piece
    (0.3, (6.67 * 0.3) - 1),  # second boundary
    (0.4, 1),  # third part
    (0.55, 1),  # third boundary
    (0.7, 3.75 - (5 * 0.7)),  # forth part
    (0.75, 3.75 - (5 * 0.75)),  # forth boundary
    (1, 0),  # beyond forth boundary
    (-1, 0),  # less than 0
])
def test_calc_growth_stage_factor(hf, exp):
    assert calc_growth_stage_factor(heatfrac=hf) == exp


@pytest.mark.parametrize("nitrates,expect", [
    (0, 1),  # zero
    (50.5, 1),  # first piece
    (100, 1),  # first boundary
    (150.5, 1.5 - (0.0005 * 150.5)),  # second piece
    (300, 1.5 - (0.0005 * 300)),  # second boundary
    (350, 0),  # third piece
    (-100, 1),  # negative
])
def test_calc_nitrate_factor(nitrates, expect):
    assert calc_nitrate_factor(accessible_nitrates=nitrates) == expect


@pytest.mark.parametrize("acc,cap", [
    (0.8, 1),  # 80% capacity
    (0.2, 1),  # 20% capacity
    (80, 100),  # whole numbers
    (100, 100),  # 100% capacity
    (120, 100),  # > 100% capacity
    (0, 100),  # no water
    (137.59, 157.33)  # arbitrary
])
def test_calc_soil_water_factor(acc, cap):
    obs = calc_soil_water_factor(accessible_water=acc, at_capacity_water=cap)
    assert obs == acc / (0.85 * cap)


@pytest.mark.parametrize("d,g,w,n", [
    (1, 1, 1, 1),  # all 1
    (0, 1, 1, 1),  # zero growth factor
    (1, 0, 1, 1),  # zero water factor
    (1, 1, 0, 1),  # zero nitrate factor
    (1, 1, 1, 0),  # zero water factor
    (0, 0, 0, 0),  # all zero
    (38.9, 0.5, 0.6, 0.7),  # arbitrary
    (38.9, 0.5, 0.6, 0.55),  # n < w
    (38.9, 0.5, 1.5, 1.1),  # n > 1, w > 1
])
def test_calc_fixed_nitrogen(d, g, w, n):
    expect = d * g * min(w, n, 1)
    if expect < d:
        expect = d
    assert calc_fixed_nitrogen(d, g, w, n) == expect
>>>>>>> master_validation_morrowcj
