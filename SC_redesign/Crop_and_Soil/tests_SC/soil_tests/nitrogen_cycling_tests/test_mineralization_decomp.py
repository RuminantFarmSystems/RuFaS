import pytest
from math import exp

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
    if organic + inorganic == 0:
        expected = carbon / 0.000001
    else:
        expected = carbon / (organic + inorganic)
    assert observed == expected


@pytest.mark.parametrize("ratio,constant", [
    (1.334, 25),
    (0.4465, 25),
    (0.234, 200),
    (0, 200)
])
def test_calculate_nutrient_term_for_residue_composition_factor(ratio: float, constant: float) -> float:
    """Tests that the nitrogen and phosphorus ratio terms are calculated correctly for use in calculating the nutrient
        cycling residue composition factor."""
    observed = MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(ratio, constant)
    expected = exp(-0.693 * ((ratio - constant) / constant))
    assert observed == expected
