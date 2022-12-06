from SC_redesign.Crop_and_Soil.crop.root_development import *
import pytest

# ---- Helper function tests ----
def test_calc_root_fraction():
    """check that root fraction is properly calculated by calc_root_fraction()"""
    assert False


def test_calc_root_depth():
    """check that root depths are properly calculated by calc_root_depths()"""
    assert False

# ---- Initializer functions ----
def init_rootdev(**kwargs):
    """helper function to initialize RootDevelopment object, with specified attributes"""
    rootdev = RootDevelopment()
    for key, val in kwargs.items():
        setattr(rootdev, key, val)
    return rootdev

# ---- Member function tests ----
def test_determine_root_fraction():
    """check that root fractions are correctly set by determine_root_fraction()"""
    assert False


def test_determine_root_depth():
    """check that root depths are appropriately set by determine_root_depth()"""
    assert False


def test_develop_roots():
    """integration test for main root development function develop_roots()"""
    assert False


# @pytest.mark.parametrize("fr_PHU,z_root,z_root_max",[
#     (0.45, 800, 1000), #arbitrary starting case
#     (0, 0, 0), #all zeroes
#     (1, 1, 1), #all ones
#     (2.5,750, 980) #creates scenario where fr_root < 0
# ])
# def test_calc_daily_root_biomass(fr_PHU, z_root, z_root_max):
#     """
#     Description:
#         Unit test for calc_daily_root_biomass in routines/field/crop/root_development.py.
#         Uses pytest parametrization to test several scenarios of possible values.
#     """
#     crop = mock_crop(fr_PHU = fr_PHU, z_root = z_root, z_root_max = z_root_max)
#
#     #calculate expected results based on crop pseudocode C.3.A.1
#     fr_root = 0.40 - 0.20 * fr_PHU
#     if fr_root < 0:
#         fr_root = 0
#     #if fr_root is >= 0 its value does not need to be changed from
#     #original calculation
#
#     calc_daily_root_biomass(crop)
#
#     assert pytest.approx(crop.fr_root) == fr_root
#
#
# @pytest.mark.parametrize("z_root_max,fr_PHU,z_root",[
#     (1000, 0.45, 800), #arbitrary starting case
#     (0, 0, 0), #all zeroes
#     (1, 1, 1), #all ones
#     (1000, .5, 1000), #z_root_max = z_root
#     (910, .31, 680), #fr_PHU < 0.4
#     (925, .60, 490) #fr_PHU > 0.4
# ])
# def test_calc_z_root(z_root_max,fr_PHU,z_root):
#     """
#     Description:
#         Unit test for calc_z_root in routines/field/crop/root_development.py.
#         Uses pytest parametrization to test several scenarios of possible values.
#     """
#     crop = mock_crop(z_root_max = z_root_max,fr_PHU = fr_PHU,z_root = z_root)
#
#     #calculate expected results based on crop pseudocode C.3.A.2/3
#     if z_root != z_root_max:
#         if fr_PHU > 0.4:
#             z_root = z_root_max
#         else:
#             z_root = 2.5 * fr_PHU * z_root_max
#
#     calc_z_root(crop)
#
#     assert pytest.approx(crop.z_root) == z_root
