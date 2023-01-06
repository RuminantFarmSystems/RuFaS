from SC_redesign.Crop_and_Soil.crop.root_development import *
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
    """check that root fraction is properly calculated by determine_root_fraction()"""
    assert RootDevelopment.determine_root_fraction(heatfrac) == expect


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
    """check that root depths are properly calculated by determine_root_depths()"""
    if heatfrac > 0.4:
        expect = maxd
    else:
        expect = 2.5 * heatfrac * maxd
    assert RootDevelopment.determine_root_depth(maxd, heatfrac) == expect


# ---- Test Class Functions ----
def init_rootdev(**kwargs):
    """helper function to initialize RootDevelopment object, with specified attributes"""
    rd = RootDevelopment()
    for key, val in kwargs.items():
        setattr(rd, key, val)
    return rd

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
    rd = init_rootdev(heat_fraction=heatfrac, max_root_depth=maxd, is_perennial=False)
    rd.develop_roots()
    assert rd.root_fraction == RootDevelopment.determine_root_fraction(heatfrac)
    assert rd.root_depth == RootDevelopment.determine_root_depth(maxd, heatfrac)
