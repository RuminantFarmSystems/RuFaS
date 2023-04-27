import pytest

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.humus_mineralization import HumusMineralization
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL


# --- Static method tests ---
@pytest.mark.parametrize("active,stable", [
    (12, 5),
    (1.8, 15),
    (4, 4),
    (0, 6),
    (7, 0),
    (0, 0)
])
def test_determine_intra_organic_mineralization(active: float, stable: float) -> None:
    """Tests that the amount of nitrogen determined to be transferred from the active organic to stable organic pool are
        calculated correctly."""
    observed = HumusMineralization._determine_intra_organic_mineralization(active, stable)
    expect = (10 ** (-5)) * active * ((1 / FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL) - 1) - stable
    if expect > 0:
        expect = min(active, expect)
    elif expect < 0:
        expect = max(-1 * stable, expect)
    assert observed == expect
