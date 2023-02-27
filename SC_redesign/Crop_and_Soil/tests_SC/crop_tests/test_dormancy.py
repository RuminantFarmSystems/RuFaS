import pytest
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy


# --- Static function tests ---
@pytest.mark.parametrize("min_daylength,dormancy_threshold", [
    (16, 17),
    (0, 0),
    (14, 17),
    (16.218347349, 16.329438502)
])
def test_find_threshold_daylength(min_daylength: float, dormancy_threshold: float) -> float:
    """Tests that _find_threshold_daylength() in Dormancy module works correctly"""
    observe = Dormancy._find_threshold_daylength(min_daylength, dormancy_threshold)
    expect = min_daylength + dormancy_threshold
    assert observe == expect


@pytest.mark.parametrize("latitude", [
    40,
    28,
    8,
    17.9238487592,
    56.2948349202,
])
def test_find_dormancy_threshold(latitude: float) -> float:
    """Tests that _find_dormancy_threshold() in Dormancy module works correctly"""
    observe = Dormancy._find_dormancy_threshold(latitude)
    if latitude > 40:
        expect = 1
    elif 20 <= latitude <= 40:
        expect = (latitude - 20) / 20
    else:
        expect = 0
    assert observe == expect
