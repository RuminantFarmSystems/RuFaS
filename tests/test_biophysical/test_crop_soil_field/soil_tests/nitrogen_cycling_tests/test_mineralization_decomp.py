from math import exp, inf
from unittest.mock import MagicMock, call

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.nitrogen_cycling.mineralization_decomp import MineralizationDecomposition
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- Static method tests ---
@pytest.mark.parametrize("carbon,organic,inorganic", [(55, 22, 44), (12, 23, 18), (180, 56, 120), (0, 0, 0)])
def test_calculate_residue_nutrient_ratio(carbon: float, organic: float, inorganic: float) -> None:
    """Tests that the correct carbon-residue ratio is calculated."""
    observed = MineralizationDecomposition._calculate_residue_nutrient_ratio(carbon, organic, inorganic)
    if organic + inorganic == 0.0:
        expected = inf
    else:
        expected = carbon / (organic + inorganic)
    assert observed == expected


@pytest.mark.parametrize("ratio,constant", [(1.334, 25), (0.4465, 25), (0.234, 200), (0, 200), (inf, 25)])
def test_calculate_nutrient_term_for_residue_composition_factor(ratio: float, constant: float) -> None:
    """Tests that the nitrogen and phosphorus ratio terms are calculated correctly for use in calculating the nutrient
    cycling residue composition factor."""
    observed = MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor(ratio, constant)
    expected = exp(-0.693 * ((ratio - constant) / constant))
    assert observed == expected


@pytest.mark.parametrize(
    "nitrogen_ratio,phosphorus_ratio,nutrient_term",
    [
        (1.92324, 1.84928, 1.9),
        (0.8859, 0.8879, 0.55),
        (1.2235, 1.1224, 0.999),
        (0.662, 0.88583, 1.0013),
    ],
)
def test_calculate_nutrient_cycling_residue_composition_factor(
    nitrogen_ratio: float, phosphorus_ratio: float, nutrient_term: float
) -> None:
    """Tests that the nutrient cycling residue composition factor is calculated correctly."""
    MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor = MagicMock(
        return_value=nutrient_term
    )
    observed = MineralizationDecomposition._calculate_nutrient_cycling_residue_composition_factor(
        nitrogen_ratio, phosphorus_ratio
    )
    expected = 1

    calls = [call(nitrogen_ratio, 25), call(phosphorus_ratio, 200)]
    MineralizationDecomposition._calculate_nutrient_term_for_residue_composition_factor.assert_has_calls(calls)
    assert observed == expected


@pytest.mark.parametrize(
    "mineralization_rate,composition_factor,temp_factor,water_factor",
    [
        (0.05, 0.8, 0.15, 0.8),
        (0.045, 0.7753, 0.66754, 0.05),
        (0.051134, 0.5562, 0.996, 0.66745),
    ],
)
def test_calculate_rate_constant(
    mineralization_rate: float,
    composition_factor: float,
    temp_factor: float,
    water_factor: float,
) -> None:
    """Tests that the decay rate constant is correctly calculated."""
    observed = MineralizationDecomposition._calculate_decay_rate_constant(
        mineralization_rate, composition_factor, temp_factor, water_factor
    )
    expected = mineralization_rate * composition_factor * (temp_factor * water_factor) ** 0.5
    assert observed == expected


# --- Test main routine ---
@pytest.mark.parametrize(
    "temp,fresh_nitrogen,decay_rate",
    [
        (20, 16, 0.44),
        (14, 6, 1.1),
        (0, 13, 0.77),
        (-3, 20, 1.3),
    ],
)
def test_mineralize_and_decompose_nitrogen(temp: float, fresh_nitrogen: float, decay_rate: float) -> None:
    """Tests that the main routine correctly calculates and updates all necessary values."""
    top_layer = LayerData(
        top_depth=0,
        bottom_depth=20,
        field_size=1.5,
        temperature=temp,
        fresh_organic_nitrogen_content=fresh_nitrogen,
        nitrate_content=60,
        fresh_organic_phosphorus_content=5,
        labile_inorganic_phosphorus_content=33,
    )
    data = SoilData(field_size=1.5, soil_layers=[top_layer])
    data.soil_layers[0].total_soil_carbon_amount = 30.0
    incorp = MineralizationDecomposition(data)

    incorp._calculate_residue_nutrient_ratio = MagicMock(return_value=0.66)
    incorp._calculate_nutrient_cycling_residue_composition_factor = MagicMock(return_value=0.88)
    incorp._calculate_decay_rate_constant = MagicMock(return_value=decay_rate)
    expected_fresh_nitrogen_removed = decay_rate * incorp.data.soil_layers[0].fresh_organic_nitrogen_content
    expected_fresh_nitrogen = (
        incorp.data.soil_layers[0].fresh_organic_nitrogen_content - expected_fresh_nitrogen_removed
    )
    expected_nitrate_content = incorp.data.soil_layers[0].nitrate_content + 0.8 * expected_fresh_nitrogen_removed
    expected_active_nitrogen = (
        incorp.data.soil_layers[0].active_organic_nitrogen_content + 0.2 * expected_fresh_nitrogen_removed
    )

    incorp.mineralize_and_decompose_nitrogen()

    if temp > 0:
        nutrient_ratio_calls = [
            call(
                incorp.data.soil_layers[0].carbon_residue_amount,
                incorp.data.soil_layers[0].fresh_organic_nitrogen_content,
                incorp.data.soil_layers[0].nitrate_content,
            ),
            call(
                incorp.data.soil_layers[0].carbon_residue_amount,
                incorp.data.soil_layers[0].fresh_organic_phosphorus_content,
                incorp.data.soil_layers[0].labile_inorganic_phosphorus_content,
            ),
        ]
        incorp._calculate_residue_nutrient_ratio.assert_has_calls(nutrient_ratio_calls)
        incorp._calculate_nutrient_cycling_residue_composition_factor.assert_called_once_with(0.66, 0.66)
        incorp._calculate_decay_rate_constant(
            incorp.data.residue_fresh_organic_mineralization_rate,
            0.88,
            incorp.data.soil_layers[0].nutrient_cycling_temp_factor,
            incorp.data.soil_layers[0].nutrient_cycling_water_factor,
        )
        assert incorp.data.soil_layers[0].fresh_organic_nitrogen_content == expected_fresh_nitrogen
        assert incorp.data.soil_layers[0].nitrate_content == expected_nitrate_content
        assert incorp.data.soil_layers[0].active_organic_nitrogen_content == expected_active_nitrogen
    else:
        incorp._calculate_residue_nutrient_ratio.assert_not_called()
        incorp._calculate_nutrient_cycling_residue_composition_factor.assert_not_called()
        incorp._calculate_decay_rate_constant.assert_not_called()
