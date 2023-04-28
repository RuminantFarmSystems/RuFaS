import pytest

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition

# --- Static method tests ---
@pytest.mark.parametrize("carbon,organic,inorganic", [
    (55, 22, 44),
    (12, 23, 18),
    (180, 56, 120),
    (0, 0, 0)
])
def test_calculate_residue_nutrient_ratio(carbon: float, organic: float, inorganic: float) -> float:
    """Tests that the correct carbon-residue ratio is calculated."""
    observed = MineralizationDecomposition._calculate_residue_nutrient_ratio(carbon, organic, inorganic)
    expected = carbon / (organic + inorganic)
    assert observed == expected
