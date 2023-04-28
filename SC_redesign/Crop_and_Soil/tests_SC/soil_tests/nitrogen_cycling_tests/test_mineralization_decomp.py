import pytest
from math import exp
from unittest.mock import MagicMock, call

from SC_redesign.Crop_and_Soil.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition

# --- Static method tests ---
@pytest.mark.parametrize("carbon,organic,inorganic", [
    (55, 22, 44),
    (12, 23, 18),
    (180, 56, 120),
    (0, 0, 0)
])
def test_calculate_residue_nutrient_ratio(carbon: float, organic: float, inorganic: float) -> None:
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
def test_calculate_nutrient_term_for_residue_composition_factor(ratio: float, constant: float) -> None:
    """Tests that the nitrogen and phosphorus ratio terms are calculated correctly for use in calculating the nutrient
        cycling residue composition factor."""
    observed = MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(ratio, constant)
    expected = exp(-0.693 * ((ratio - constant) / constant))
    assert observed == expected


@pytest.mark.parametrize("nitrogen_ratio,phosphorus_ratio,nutrient_term", [
    (1.92324, 1.84928, 1.9),
    (0.8859, 0.8879, 0.55),
    (1.2235, 1.1224, 0.999),
    (0.662, 0.88583, 1.0013)
])
def test_calculate_nutrient_cycling_residue_composition_factor(nitrogen_ratio: float, phosphorus_ratio: float,
                                                               nutrient_term: float) -> None:
    """Tests that the nutrient cycling residue composition factor is calculated correctly."""
    MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor = \
        MagicMock(return_value=nutrient_term)
    observed = MineralizationDecomposition._calculate_nutrient_cycling_residue_composition_factor(nitrogen_ratio,
                                                                                                  phosphorus_ratio)
    expected = min(1.0, nutrient_term)

    calls = [call(nitrogen_ratio, 25), call(phosphorus_ratio, 200)]
    MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor.assert_has_calls(calls)
    assert observed == expected
