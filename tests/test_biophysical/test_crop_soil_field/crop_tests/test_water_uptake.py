from math import exp
from typing import List
from unittest.mock import MagicMock, call, patch

import pytest

from RUFAS.biophysical.field.crop.crop_data import CropData
from RUFAS.biophysical.field.crop.water_uptake import WaterUptake
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData

from tests.test_biophysical.test_crop_soil_field.sample_crop_configuration import SAMPLE_CROP_CONFIGURATION


@pytest.fixture
def mock_crop_data() -> CropData:
    return CropData(**SAMPLE_CROP_CONFIGURATION)


@pytest.mark.parametrize("pot,avail,wilt", [(1, 2, 3)])
def test_determine_actual_layer_uptake(pot: float, avail: float, wilt: float) -> None:
    """checks that layer uptake is correct"""
    if pot > avail - wilt:
        expect = avail - wilt
    else:
        expect = pot
    assert WaterUptake._determine_actual_layer_uptake(pot, avail, wilt) == expect


@pytest.mark.parametrize("pot,avail,cap", [(1, 2, 3), (1, 1, 8)])
def test_correct_layer_for_efficiency(pot: float, avail: float, cap: float) -> None:
    """checks that layer efficiency is corrected properly"""
    if avail >= cap * 0.25:
        assert WaterUptake._correct_layer_for_efficiency(pot, avail, cap) == pot
    else:
        assert WaterUptake._correct_layer_for_efficiency(pot, avail, cap) == pot * exp(5 * ((avail / (0.25 * cap)) - 1))


@pytest.mark.parametrize("max_trans", [5])
def test_uptake_water(mock_crop_data: CropData, max_trans: float) -> None:
    """ensure that uptake_water can run without error"""
    # This patch is a quick fix for the mock from NitrogenIncorporation spilling over into this one.
    with patch(
        "RUFAS.biophysical.field.crop.nitrogen_uptake.NitrogenUptake.determine_layer_nutrient_demands",
        new_callable=MagicMock,
        return_value=[1, 2, 3, 4],
    ):
        mock_crop_data.max_transpiration = max_trans
        soil_data = SoilData(field_size=1.5)
        wu = WaterUptake(mock_crop_data)
        wu.uptake(soil_data)


@pytest.mark.parametrize(
    "layers,uptakes,should_fail",
    [
        (
            [
                LayerData(bottom_depth=20, top_depth=1, field_size=3),
                LayerData(bottom_depth=3, top_depth=1, field_size=3),
                LayerData(bottom_depth=2, top_depth=1, field_size=3),
            ],
            [LayerData(bottom_depth=4, top_depth=1, field_size=3)],
            True,
        ),
        (
            [LayerData(bottom_depth=20, top_depth=1, field_size=3)],
            [LayerData(bottom_depth=4, top_depth=1, field_size=3)],
            False,
        ),
    ],
)
def test_extract_water_from_soil(
    mock_crop_data: CropData, layers: list[LayerData], uptakes: list[LayerData], should_fail: bool
) -> None:
    """This method only tests for edge cases, other parts of the method already have coverage"""
    soil_data = SoilData(soil_layers=layers, field_size=3)
    uptake = WaterUptake(crop_data=mock_crop_data, actual_water_uptakes=uptakes)
    if should_fail:
        with pytest.raises(Exception) as e:
            uptake.extract_water_from_soil(soil_data)
        assert str(e.value) == "actual_water_uptakes should be the same length as the number of soil layers"
    else:
        soil_data.get_vectorized_layer_attribute = MagicMock()
        soil_data.set_vectorized_layer_attribute = MagicMock()
        uptake.extract_water_from_soil(soil_data)
        assert soil_data.get_vectorized_layer_attribute.call_count == 1
        assert soil_data.set_vectorized_layer_attribute.call_count == 1


@pytest.mark.parametrize(
    "potential_uptakes,water_availabilities,available_capacities,should_fail",
    [
        ([0.1, 0.2, 0.3], [9.24, 7.7, 1.31], [2.0, 3.5, 4.2], False),
        ([0.1, 0.2], [9.24, 7.7, 1.31], [2.0, 3.5, 4.2], True),
        ([0.1, 0.2, 0.4], [9.24, 7.7], [2.0, 3.5, 4.2], True),
        ([0.1, 0.2, 0.4], [9.24, 7.7, 1.31], [2.0, 3.5], True),
    ],
)
def test_reduce_efficiency_of_uptake(
    potential_uptakes: List[float],
    water_availabilities: List[float],
    available_capacities: List[float],
    should_fail: bool,
) -> None:
    """Tests that the reduced efficiency of uptake is calculated correctly when there's no error in input"""
    if should_fail:
        with pytest.raises(Exception) as e:
            WaterUptake._reduce_efficiency_of_uptake(potential_uptakes, water_availabilities, available_capacities)
        assert (
            str(e.value) == "potential_uptakes, water_availabilities, and available_capacities must be of equal"
            " length"
        )
    else:
        WaterUptake._correct_layer_for_efficiency = MagicMock(return_value=0.5)
        result = WaterUptake._reduce_efficiency_of_uptake(potential_uptakes, water_availabilities, available_capacities)
        expected_calls = []
        for i in range(len(potential_uptakes)):
            expected_calls.append(
                call(
                    potential_uptakes[i],
                    water_availabilities[i],
                    available_capacities[i],
                )
            )
        WaterUptake._correct_layer_for_efficiency.assert_has_calls(expected_calls)
        expected = [0.5] * len(potential_uptakes)
        assert expected == result


@pytest.mark.parametrize(
    "potential_uptakes,unmet_demands,uptake_compensation,should_fail,expected",
    [
        ([0.1, 0.2, 0.3], [0.7, 0.8, 0.9], 2.3, False, [1.71, 2.04, 2.37]),
        ([0.1, 0.2], [0.7, 0.8, 0.9], 2.5, True, []),
    ],
)
def test_adjust_water_uptakes(
    potential_uptakes: List[float],
    unmet_demands: List[float],
    uptake_compensation: float,
    should_fail: bool,
    expected: List[float],
) -> None:
    """Tests that the adjusted water uptakes are calculated correctly when there's no error in input"""
    if should_fail:
        with pytest.raises(Exception) as e:
            WaterUptake._adjust_water_uptakes(potential_uptakes, unmet_demands, uptake_compensation)
        assert str(e.value) == "potential_uptakes and unmet_demands must be the same length."
    else:
        assert WaterUptake._adjust_water_uptakes(
            potential_uptakes, unmet_demands, uptake_compensation
        ) == pytest.approx(expected)


@pytest.mark.parametrize(
    "root_depth,max_transpiration,water_distro_parameter,upper_depths,lower_depths,should_fail," "expected",
    [
        (
            69.4,
            25.7,
            33.4,
            [23.5, 24.6],
            [24.5, 41.6],
            False,
            [0.00012028579, 0.0001854024],
        ),
        (69.4, 25.7, 33.4, [23.5], [24.5, 41.6], True, []),
    ],
)
def test_find_stratified_max_water_uptakes(
    root_depth: float,
    max_transpiration: float,
    water_distro_parameter: float,
    upper_depths: List[float],
    lower_depths: List[float],
    should_fail: bool,
    expected: List[float],
) -> None:
    """Tests that the stratified max water uptakes are calculated correctly when there's no error in input"""
    if should_fail:
        with pytest.raises(Exception) as e:
            WaterUptake._find_stratified_max_water_uptakes(
                root_depth,
                max_transpiration,
                water_distro_parameter,
                upper_depths,
                lower_depths,
            )
        assert str(e.value) == "upper_depths and lower_depths must be the same length"
    else:
        assert pytest.approx(expected) == WaterUptake._find_stratified_max_water_uptakes(
            root_depth,
            max_transpiration,
            water_distro_parameter,
            upper_depths,
            lower_depths,
        )


@pytest.mark.parametrize(
    "root_depth,depth,max_plant_transpiration,water_distribution_parameter",
    [(69.4, 25.7, 33.4, 69.4), (0, 25.7, 33.4, 42.3)],
)
def test_determine_max_water_uptake_to_depth(
    root_depth: float,
    depth: float,
    max_plant_transpiration: float,
    water_distribution_parameter: float,
) -> None:
    """Tests that the stratified max water uptake to depth are calculated correctly"""
    if root_depth == 0:
        expected = 0
    else:
        expected = (1 - exp(-water_distribution_parameter * (depth / root_depth))) * (
            max_plant_transpiration / (1 - exp(-water_distribution_parameter))
        )

    assert expected == WaterUptake._determine_max_water_uptake_to_depth(
        root_depth, depth, max_plant_transpiration, water_distribution_parameter
    )


@pytest.mark.parametrize(
    "potential_uptakes,water_availabilities,wilting_points,should_fail",
    [
        ([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], False),
        ([0.1, 0.2], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], True),
        ([0.1, 0.2, 0.3], [0.4, 0.5], [0.7, 0.8, 0.9], True),
        ([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8], True),
    ],
)
def test_take_up_water(
    potential_uptakes: List[float],
    water_availabilities: List[float],
    wilting_points: List[float],
    should_fail: bool,
) -> None:
    """Tests that the the correct output _take_up_water of were calculated when there's no error in input"""
    if should_fail:
        with pytest.raises(Exception) as e:
            WaterUptake._take_up_water(potential_uptakes, water_availabilities, wilting_points)
        assert str(e.value) == "potential_uptakes, water_availabilities, and wilting_points must be of equal length"
    else:
        WaterUptake._determine_actual_layer_uptake = MagicMock(return_value=0.5)
        result = WaterUptake._take_up_water(potential_uptakes, water_availabilities, wilting_points)
        expected_calls = []
        for i in range(len(potential_uptakes)):
            expected_calls.append(call(potential_uptakes[i], water_availabilities[i], wilting_points[i]))
        WaterUptake._determine_actual_layer_uptake.assert_has_calls(expected_calls)
        expected = [0.5] * len(potential_uptakes)
        assert expected == result
