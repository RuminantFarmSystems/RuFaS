import pytest
from unittest.mock import MagicMock, patch
from math import exp, log

from SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization


# --- Static method tests ---
@pytest.mark.parametrize("old_parameter,current_parameter", [
    (0.05, 0.05),
    (0.7, 0.7),
    (0.05, 0.7),
    (0.7, 0.05),
    (0.1344, 0.3345),
    (0.687, 0.512)
])
def test_recompute_mean_phosphorus_sorption_parameter(old_parameter: float, current_parameter: float) -> None:
    """Tests that the mean phosphorus sorption parameter is re-averaged correctly."""
    observed = PhosphorusMineralization._recompute_mean_phosphorus_sorption_parameter(old_parameter, current_parameter)
    expected = (old_parameter * 29 + current_parameter) / 30
    expected = max(0.05, min(0.7, expected))
    assert observed == expected


@pytest.mark.parametrize("labile,active,sorption_parameter", [
    (34.32, 43.52, 0.445),
    (345.149, 284.194, 0.556),
    (130.59, 113.492, 0.223),
    (0.0, 355.93, 0.4902),
    (349.593, 0.0, 0.3354),
    (0.0, 0.0, 0.6698)
])
def test_determine_phosphorus_imbalance(labile: float, active: float, sorption_parameter: float) -> None:
    """Tests that the balance or imbalance between the active and labile pools is correctly calculated."""
    observed = PhosphorusMineralization._determine_phosphorus_imbalance(labile, active, sorption_parameter)
    expected = labile - active * (sorption_parameter / (1 - sorption_parameter))
    assert observed == expected


@pytest.mark.parametrize("active_counter,sorption_parameter,balance", [
    (1, 0.3345, 1.34),
    (3, 0.5531, 0.9953),
    (5, 0.05, 2.345)
])
def test_calculate_phosphorus_desorption(active_counter: int, sorption_parameter: float, balance: float) -> None:
    """Tests that the amount of phosphorus to be transferred from the active to labile pools is correctly calculated."""
    with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization.PhosphorusMineralization"
               "._determine_desorption_base", new_callable=MagicMock, return_value=0.5) as mocked_determine_base:
        observed = PhosphorusMineralization._calculate_phosphorus_desorption(active_counter, sorption_parameter,
                                                                             balance)
        expected_sorption_factor = 0.5 * active_counter ** -0.32
        expected_amount = expected_sorption_factor * balance * -1.0

        mocked_determine_base.assert_called_once_with(sorption_parameter)
        assert observed == expected_amount


@pytest.mark.parametrize("sorption_parameter", [
    0.124,
    0.05,
    0.7,
    0.3345,
    0.66752
])
def test_determine_desorption_base(sorption_parameter: float) -> None:
    """Tests that the base variable is calculated correctly."""
    observed = PhosphorusMineralization._determine_desorption_base(sorption_parameter)
    expected = -1.0 * sorption_parameter + 0.8
    assert observed == expected


@pytest.mark.parametrize("labile_counter,sorption_parameter,balance", [
    (1, 0.05, -1.34),
    (2, 0.4434, -0.887),
    (4, 0.6778, -0.33)
])
def test_calculate_phosphorus_sorption(labile_counter: int, sorption_parameter: float, balance: float) -> None:
    """Tests that the correct amount of phosphorus to remove from the labile inorganic pool is calculated."""
    with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization.PhosphorusMineralization"
               "._determine_sorption_scalar", new_callable=MagicMock, return_value=0.4) as mocked_sorption:
        with patch("SC_redesign.Crop_and_Soil.soil.phosphorus_cycling.phosphorus_mineralization"
                   ".PhosphorusMineralization._determine_sorption_exponent",
                   new_callable=MagicMock, return_value=-0.91) as mocked_exponent:
            observed = PhosphorusMineralization._calculate_phosphorus_sorption(labile_counter, sorption_parameter,
                                                                               balance)
            expected_sorption_factor = 0.4 * labile_counter ** -0.91
            expected_amount = expected_sorption_factor * balance

            mocked_sorption.assert_called_once_with(sorption_parameter)
            mocked_exponent.assert_called_once_with(0.4)
            assert observed == expected_amount


@pytest.mark.parametrize("sorption_parameter", [
    0.124,
    0.05,
    0.7,
    0.3345,
    0.66752
])
def test_determine_sorption_scalar(sorption_parameter: float) -> None:
    """Tests that the scalar used in the sorption rate factor is calculated correctly."""
    observed = PhosphorusMineralization._determine_sorption_scalar(sorption_parameter)
    expected = 0.918 * exp(sorption_parameter * -4.603)
    assert observed == expected


@pytest.mark.parametrize("scalar", [
    0.518,
    0.729,
    0.0366,
    0.1968,
    0.0425
])
def test_determine_sorption_exponent(scalar: float) -> None:
    """Tests that the exponential term used to determine the sorption rate factor is calculated correctly."""
    observed = PhosphorusMineralization._determine_sorption_exponent(scalar)
    expected = -0.238 * log(scalar) - 1.126
    assert observed == expected


@pytest.mark.parametrize("stable,active", [
    (14.55, 2.334),
    (18.4948, 9.5495),
    (3.49587, 5.6938),
    (0.0, 0.0),
    (0.0, 4.596),
    (6.592, 0.0)
])
def test_determine_stable_to_active_phosphorus_mineralization(stable: float, active: float) -> None:
    """Tests that the amount mineralized between the stable and active pools is calculated correctly."""
    observed = PhosphorusMineralization._determine_stable_to_active_phosphorus_mineralization(stable, active)
    expected = 0.0006 * (stable - 4 * active)
    expected = min(stable, expected)
    expected = max(-1.0 * active, expected)
    assert observed == expected


# --- Main routine test ---
# @pytest.mark.parametrize("field_size, balance", [
#     ()
# ])
# def test_mineralize_phosphorus(field_size: float, balance: float) -> None:
#     """Tests that the main routine correctly calls all subroutines and updates values correctly."""
#     layers = [LayerData(top_depth=0, bottom_depth=20, labile_inorganic_phosphorus_content=)]
#     data = SoilData()
