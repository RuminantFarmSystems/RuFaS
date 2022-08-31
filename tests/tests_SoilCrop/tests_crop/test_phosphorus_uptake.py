"""
RUFAS: Ruminant Farm Systems Model
File name: test_phosphorus_uptake.py
Description: Implements tests for phosphorus_uptake.py
Author(s): Clay Morrow, morrowcj@outlook.com
"""

from tests.tests_SoilCrop.mock_classes import mock_crop
from RUFAS.routines.field.crop import phosphorus_uptake
from math import log

# TODO: I don't like this type of test. It is basically testing that the function is the function.
def test_calc_log_term_of_shape_coefficient():
    """test of the calc_log_term_of_shape_coefficient function"""
    mc = mock_crop(fr_p3=0.25, fr_p1=0.8)
    bottom = 1 - (0.55 - 0.25) / (0.8 - 0.25)
    inside = (0.1 / bottom) - 0.1
    assert phosphorus_uptake.calc_log_term_of_shape_coefficient(crop_type=mc, fr_PHU_frac=0.1, fr_px=0.55)\
           == log(inside)


def test_calc_p2():
    """test for the calc_p2() function"""
    assert False


def test_calc_p1():
    """test for the calc_p1() function"""
    assert False


def test_calc_fr_P():
    """test for the calc_fr_P() function"""
    assert False


def test_calc_bio_P_opt():
    """test for the calc_bio_P_opt() function"""
    assert False


def test_calc_P_up():
    """test for the calc_P_up() function"""
    assert False


def test_calc_act_P_up_each_layer():
    """test for the calc_act_P_up_each_layer() function"""
    assert False


def test_calc_P_up_each_layer():
    """test for the calc_P_up_each_layer() function"""
    assert False

def test_calc_P_up_z():
    """test for the calc_P_up_z() function"""
    assert False


def test_calc_bio_P():
    """test for the calc_bio_P() function"""
    assert False


def test_P_uptake():
    """test for the P_uptake() function"""
    assert False

def test_update_all():
    """test for the update_all() function"""
    assert False