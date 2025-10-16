from math import exp, log
from unittest.mock import MagicMock, patch

import pytest

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization import PhosphorusMineralization
from RUFAS.biophysical.field.soil.soil_data import SoilData


# --- Static method tests ---
@pytest.mark.parametrize(
    "old_parameter,current_parameter,expected",
    [
        (0.05, 0.05, 0.05),
        (0.7, 0.7, 0.7),
        (0.05, 0.7, 0.05178082),
        (0.7, 0.05, 0.69821917),
        (0.1344, 0.3345, 0.13494821),
        (0.687, 0.512, 0.686520547),
    ],
)
def test_recompute_mean_phosphorus_sorption_parameter(
    old_parameter: float, current_parameter: float, expected: float
) -> None:
    """Tests that the mean phosphorus sorption parameter is re-averaged correctly."""
    observed = PhosphorusMineralization._recompute_mean_phosphorus_sorption_parameter(old_parameter, current_parameter)
    assert pytest.approx(observed) == expected


@pytest.mark.parametrize(
    "labile,active,sorption_parameter",
    [
        (34.32, 43.52, 0.445),
        (345.149, 284.194, 0.556),
        (130.59, 113.492, 0.223),
        (0.0, 355.93, 0.4902),
        (349.593, 0.0, 0.3354),
        (0.0, 0.0, 0.6698),
    ],
)
def test_determine_phosphorus_imbalance(labile: float, active: float, sorption_parameter: float) -> None:
    """Tests that the balance or imbalance between the active and labile pools is correctly calculated."""
    observed = PhosphorusMineralization._determine_phosphorus_imbalance(labile, active, sorption_parameter)
    expected = labile - active * (sorption_parameter / (1 - sorption_parameter))
    assert observed == expected


@pytest.mark.parametrize(
    "active_counter,sorption_parameter,balance",
    [(1, 0.3345, 1.34), (3, 0.5531, 0.9953), (5, 0.05, 2.345)],
)
def test_calculate_phosphorus_desorption(active_counter: int, sorption_parameter: float, balance: float) -> None:
    """Tests that the amount of phosphorus to be transferred from the active to labile pools is correctly calculated."""
    with patch(
        "RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization.PhosphorusMineralization"
        "._determine_desorption_base",
        new_callable=MagicMock,
        return_value=0.5,
    ) as mocked_determine_base:
        observed = PhosphorusMineralization._calculate_phosphorus_desorption(
            active_counter, sorption_parameter, balance
        )
        expected_sorption_factor = 0.5 * active_counter**-0.32
        expected_amount = expected_sorption_factor * balance * -1.0

        mocked_determine_base.assert_called_once_with(sorption_parameter)
        assert observed == expected_amount


@pytest.mark.parametrize("sorption_parameter", [0.124, 0.05, 0.7, 0.3345, 0.66752])
def test_determine_desorption_base(sorption_parameter: float) -> None:
    """Tests that the base variable is calculated correctly."""
    observed = PhosphorusMineralization._determine_desorption_base(sorption_parameter)
    expected = -1.0 * sorption_parameter + 0.8
    assert observed == expected


@pytest.mark.parametrize(
    "labile_counter,sorption_parameter,balance",
    [(1, 0.05, -1.34), (2, 0.4434, -0.887), (4, 0.6778, -0.33)],
)
def test_calculate_phosphorus_sorption(labile_counter: int, sorption_parameter: float, balance: float) -> None:
    """Tests that the correct amount of phosphorus to remove from the labile inorganic pool is calculated."""
    with patch(
        "RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization.PhosphorusMineralization"
        "._determine_sorption_scalar",
        new_callable=MagicMock,
        return_value=0.4,
    ) as mocked_sorption:
        with patch(
            "RUFAS.biophysical.field.soil.phosphorus_cycling.phosphorus_mineralization"
            ".PhosphorusMineralization._determine_sorption_exponent",
            new_callable=MagicMock,
            return_value=-0.91,
        ) as mocked_exponent:
            observed = PhosphorusMineralization._calculate_phosphorus_sorption(
                labile_counter, sorption_parameter, balance
            )
            expected_sorption_factor = 0.4 * labile_counter**-0.91
            expected_amount = expected_sorption_factor * balance

            mocked_sorption.assert_called_once_with(sorption_parameter)
            mocked_exponent.assert_called_once_with(0.4)
            assert observed == expected_amount


@pytest.mark.parametrize("sorption_parameter", [0.124, 0.05, 0.7, 0.3345, 0.66752])
def test_determine_sorption_scalar(sorption_parameter: float) -> None:
    """Tests that the scalar used in the sorption rate factor is calculated correctly."""
    observed = PhosphorusMineralization._determine_sorption_scalar(sorption_parameter)
    expected = 0.918 * exp(sorption_parameter * -4.603)
    assert observed == expected


@pytest.mark.parametrize("scalar", [0.518, 0.729, 0.0366, 0.1968, 0.0425])
def test_determine_sorption_exponent(scalar: float) -> None:
    """Tests that the exponential term used to determine the sorption rate factor is calculated correctly."""
    observed = PhosphorusMineralization._determine_sorption_exponent(scalar)
    expected = -0.238 * log(scalar) - 1.126
    assert observed == expected


@pytest.mark.parametrize(
    "stable,active",
    [
        (14.55, 2.334),
        (18.4948, 9.5495),
        (3.49587, 5.6938),
        (0.0, 0.0),
        (0.0, 4.596),
        (6.592, 0.0),
        (-3, 0.0),
    ],
)
def test_determine_stable_to_active_phosphorus_mineralization(stable: float, active: float) -> None:
    """Tests that the amount mineralized between the stable and active pools is calculated correctly."""
    observed = PhosphorusMineralization._determine_stable_to_active_phosphorus_mineralization(stable, active)
    expected = 0.0006 * (stable - 4 * active)
    expected = min(stable, expected)
    expected = max(-1.0 * active, expected)
    assert observed == expected


# --- Main routine test ---
@pytest.mark.parametrize("field_size", [1.55, 0.88, 2.33, 1.5])
def test_mineralize_phosphorus(field_size: float) -> None:
    """Tests that the main routine correctly calls all subroutines and updates values correctly.

    Notes
    -----
    `calculate_phosphorus_sorption_parameter()` has a call count of 7 because it is called once for when each layer in
    the soil profile in initialized, once for the vadose zone layer, and once for each iteration of the for loop in
    `mineralize_phosphorus()`

    """
    with (
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.determine_soil_nutrient_area_density",
            new_callable=MagicMock,
            return_value=20,
        ),
        patch(
            "RUFAS.biophysical.field.soil.layer_data.LayerData.labile_inorganic_phosphorus_content",
            new_callable=MagicMock,
            return_value=20,
        ),
    ):
        # Case 1: tests that desorption occurs correctly
        LayerData.determine_soil_nutrient_concentration = MagicMock()
        LayerData.calculate_phosphorus_sorption_parameter = MagicMock()
        layers1 = [
            LayerData(top_depth=0, bottom_depth=20, field_size=field_size),
            LayerData(top_depth=20, bottom_depth=65, field_size=field_size),
            LayerData(top_depth=65, bottom_depth=120, field_size=field_size),
        ]
        data1 = SoilData(soil_layers=layers1, field_size=field_size)
        incorp1 = PhosphorusMineralization(data1)

        incorp1._recompute_mean_phosphorus_sorption_parameter = MagicMock(return_value=0.35)
        incorp1._determine_phosphorus_imbalance = MagicMock(return_value=-0.5)
        incorp1._calculate_phosphorus_desorption = MagicMock(return_value=5)
        incorp1._calculate_phosphorus_sorption = MagicMock()
        incorp1._determine_stable_to_active_phosphorus_mineralization = MagicMock(return_value=6)

        incorp1.mineralize_phosphorus(field_size)

        assert LayerData.determine_soil_nutrient_concentration.call_count == 3
        assert LayerData.calculate_phosphorus_sorption_parameter.call_count == 7
        assert incorp1._recompute_mean_phosphorus_sorption_parameter.call_count == 3
        assert incorp1._determine_phosphorus_imbalance.call_count == 3
        assert incorp1._calculate_phosphorus_desorption.call_count == 3
        assert incorp1._calculate_phosphorus_sorption.call_count == 0
        assert incorp1._determine_stable_to_active_phosphorus_mineralization.call_count == 3
        for layer in incorp1.data.soil_layers:
            assert layer.mean_phosphorus_sorption_parameter == 0.35
            assert layer.active_inorganic_unbalanced_counter == 1
            assert layer.labile_inorganic_unbalanced_counter == 0
            assert layer.labile_inorganic_phosphorus_content == 25
            assert layer.active_inorganic_phosphorus_content == 21
            assert layer.stable_inorganic_phosphorus_content == 14

        # Case 2: tests that sorption occurs correctly
        LayerData.determine_soil_nutrient_concentration = MagicMock()
        LayerData.calculate_phosphorus_sorption_parameter = MagicMock()
        layers2 = [
            LayerData(top_depth=0, bottom_depth=20, field_size=field_size),
            LayerData(top_depth=20, bottom_depth=78, field_size=field_size),
            LayerData(top_depth=78, bottom_depth=200, field_size=field_size),
        ]
        data2 = SoilData(soil_layers=layers2, field_size=field_size)
        incorp2 = PhosphorusMineralization(data2)

        incorp2._recompute_mean_phosphorus_sorption_parameter = MagicMock(return_value=0.37)
        incorp2._determine_phosphorus_imbalance = MagicMock(return_value=0.5)
        incorp2._calculate_phosphorus_desorption = MagicMock()
        incorp2._calculate_phosphorus_sorption = MagicMock(return_value=4)
        incorp2._determine_stable_to_active_phosphorus_mineralization = MagicMock(return_value=2)

        incorp2.mineralize_phosphorus(field_size)

        assert LayerData.determine_soil_nutrient_concentration.call_count == 3
        assert LayerData.calculate_phosphorus_sorption_parameter.call_count == 7
        assert incorp2._recompute_mean_phosphorus_sorption_parameter.call_count == 3
        assert incorp2._determine_phosphorus_imbalance.call_count == 3
        assert incorp2._calculate_phosphorus_desorption.call_count == 0
        assert incorp2._calculate_phosphorus_sorption.call_count == 3
        assert incorp2._determine_stable_to_active_phosphorus_mineralization.call_count == 3
        for layer in incorp2.data.soil_layers:
            assert layer.mean_phosphorus_sorption_parameter == 0.37
            assert layer.active_inorganic_unbalanced_counter == 0
            assert layer.labile_inorganic_unbalanced_counter == 1
            assert layer.labile_inorganic_phosphorus_content == 16
            assert layer.active_inorganic_phosphorus_content == 26
            assert layer.stable_inorganic_phosphorus_content == 18

        # Case 3: tests that when there is no imbalance, no phosphorus is transferred between active and labile pools
        LayerData.determine_soil_nutrient_concentration = MagicMock()
        LayerData.calculate_phosphorus_sorption_parameter = MagicMock()
        layers3 = [
            LayerData(top_depth=0, bottom_depth=20, field_size=field_size),
            LayerData(top_depth=20, bottom_depth=56, field_size=field_size),
            LayerData(top_depth=56, bottom_depth=200, field_size=field_size),
        ]
        data3 = SoilData(soil_layers=layers3, field_size=field_size)
        incorp3 = PhosphorusMineralization(data3)

        incorp3._recompute_mean_phosphorus_sorption_parameter = MagicMock(return_value=0.44)
        incorp3._determine_phosphorus_imbalance = MagicMock(return_value=0.0)
        incorp3._calculate_phosphorus_desorption = MagicMock()
        incorp3._calculate_phosphorus_sorption = MagicMock()
        incorp3._determine_stable_to_active_phosphorus_mineralization = MagicMock(return_value=5)

        incorp3.mineralize_phosphorus(field_size)

        assert LayerData.determine_soil_nutrient_concentration.call_count == 3
        assert LayerData.calculate_phosphorus_sorption_parameter.call_count == 7
        assert incorp3._recompute_mean_phosphorus_sorption_parameter.call_count == 3
        assert incorp3._determine_phosphorus_imbalance.call_count == 3
        assert incorp3._calculate_phosphorus_desorption.call_count == 0
        assert incorp3._calculate_phosphorus_sorption.call_count == 0
        assert incorp3._determine_stable_to_active_phosphorus_mineralization.call_count == 3
        for layer in incorp3.data.soil_layers:
            assert layer.mean_phosphorus_sorption_parameter == 0.44
            assert layer.active_inorganic_unbalanced_counter == 0
            assert layer.labile_inorganic_unbalanced_counter == 0
            assert layer.labile_inorganic_phosphorus_content == 20
            assert layer.active_inorganic_phosphorus_content == 25
            assert layer.stable_inorganic_phosphorus_content == 15

        LayerData.determine_soil_nutrient_concentration = MagicMock()
        LayerData.calculate_phosphorus_sorption_parameter = MagicMock()
        layers1 = [
            LayerData(top_depth=0, bottom_depth=20, field_size=field_size),
            LayerData(top_depth=20, bottom_depth=65, field_size=field_size),
            LayerData(top_depth=65, bottom_depth=120, field_size=field_size),
        ]
        for layer in layers1:
            layer.previous_phosphorus_balance = 1
        data1 = SoilData(soil_layers=layers1, field_size=field_size)
        incorp1 = PhosphorusMineralization(data1)

        incorp1._recompute_mean_phosphorus_sorption_parameter = MagicMock(return_value=0.35)
        incorp1._determine_phosphorus_imbalance = MagicMock(return_value=1000)
        incorp1._calculate_phosphorus_desorption = MagicMock(return_value=5)
        incorp1._calculate_phosphorus_sorption = MagicMock(return_value=15)
        incorp1._determine_stable_to_active_phosphorus_mineralization = MagicMock(return_value=6)

        incorp1.mineralize_phosphorus(field_size)

        assert LayerData.determine_soil_nutrient_concentration.call_count == 3
        assert LayerData.calculate_phosphorus_sorption_parameter.call_count == 7
        assert incorp1._recompute_mean_phosphorus_sorption_parameter.call_count == 3
        assert incorp1._determine_phosphorus_imbalance.call_count == 3
        assert incorp1._calculate_phosphorus_desorption.call_count == 0
        assert incorp1._calculate_phosphorus_sorption.call_count == 3
        assert incorp1._determine_stable_to_active_phosphorus_mineralization.call_count == 3
        for layer in incorp1.data.soil_layers:
            assert layer.mean_phosphorus_sorption_parameter == 0.35
            assert layer.active_inorganic_unbalanced_counter == 0
            assert layer.labile_inorganic_unbalanced_counter == 1
            assert layer.labile_inorganic_phosphorus_content == 5
            assert layer.active_inorganic_phosphorus_content == 41
            assert layer.stable_inorganic_phosphorus_content == 14
