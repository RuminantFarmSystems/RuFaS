from SC_redesign.Crop_and_Soil.crop.root_development import RootDevelopment
from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.crop_data import PlantCategory
import pytest


# ---- Test Static Functions ----
@pytest.mark.parametrize("heatfrac,expect", [
    (-1, 0.4),
    (0, 0.4),
    (0.5, 0.4 - (0.2 * 0.5)),
    (1, 0.4 - (0.2 * 1)),
    (1.2, 0.4 - (0.2 * 1.2)),
    (2, 0),
    (2.1, 0)
])
def test_determine_root_fraction(heatfrac, expect):
    """check that root fraction is properly calculated by
    determine_root_fraction()"""
    assert RootDevelopment._determine_root_fraction(heatfrac) == expect


@pytest.mark.parametrize("maxd,heatfrac", [
    (1, 0.5),
    (1, 0.3),
    (1, 0),
    (1, 1),
    (1, 1.2),
    (0, 0.5),
    (100, 0.5),
])
def test_determine_root_depth(maxd, heatfrac):
    """check that root depths are properly calculated by
    determine_root_depths()"""
    if heatfrac > 0.4:
        expect = maxd
    else:
        expect = 2.5 * heatfrac * maxd
    assert RootDevelopment._determine_root_depth(maxd, heatfrac) == expect


# ---- Test Class Methods ----

@pytest.mark.parametrize("maxd, heatfrac", [
    (1, 0.5),
    (1, 0.3),
    (1, 0),
    (1, 1),
    (1, 1.2),
    (0, 0.5),
    (100, 0.5),
])
def test_develop_roots(maxd, heatfrac):
    """integration test for main root development function develop_roots()"""

    # ---- perennial crop ----
    data_perennial = CropData(heat_fraction=heatfrac, max_root_depth=maxd, plant_category=PlantCategory("perennial"))
    rd = RootDevelopment(data_perennial)
    rd.develop_roots()
    assert data_perennial.root_fraction == RootDevelopment._determine_root_fraction(heatfrac)
    assert data_perennial.root_depth == maxd

    # ---- annual crop ----
    data_annual = CropData(heat_fraction=heatfrac, max_root_depth=maxd, plant_category=PlantCategory("warm_annual"))
    rd = RootDevelopment(data_annual)
    rd.develop_roots()
    assert data_annual.root_fraction == RootDevelopment._determine_root_fraction(heatfrac)
    assert data_annual.root_depth == RootDevelopment._determine_root_depth(maxd, heatfrac)
