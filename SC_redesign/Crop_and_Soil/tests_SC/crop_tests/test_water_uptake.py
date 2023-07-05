from math import exp
from typing import List

import pytest
from unittest.mock import MagicMock, patch

from SC_redesign.Crop_and_Soil.crop.crop_data import CropData
from SC_redesign.Crop_and_Soil.crop.water_uptake import WaterUptake
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


# TODO: Since, these will be updated/replaced along with Issue #450, these tests are simple and won't test wrappers


@pytest.mark.parametrize("pot,avail,wilt", [
    (1, 2, 3)
])
def test_determine_actual_layer_uptake(pot, avail, wilt):
    """checks that layer uptake is correct"""
    if pot > avail - wilt:
        expect = avail - wilt
    else:
        expect = pot
    assert WaterUptake._determine_actual_layer_uptake(pot, avail, wilt) == expect


@pytest.mark.parametrize("pot,avail,cap", [
    (1, 2, 3),
    (1, 1, 8)
])
def test_correct_layer_for_efficiency(pot, avail, cap):
    """checks that layer efficiency is corrected properly"""
    if avail >= cap * 0.25:
        assert WaterUptake._correct_layer_for_efficiency(pot, avail, cap) == pot
    else:
        assert WaterUptake._correct_layer_for_efficiency(pot, avail, cap) == pot * exp(5 * ((avail / (0.25 * cap)) - 1))


def test_determine_max_water_uptake_to_depth():
    pass  # this is equivalent to the tests in test_nitrogen_incorporation and test_phosphorus_incorporation


@pytest.mark.parametrize("max_trans", [
    5
])
def test_uptake_water(max_trans):
    """ensure that uptake_water can run without error"""
    # This patch is a quick fix for the mock from NitrogenIncorporation spilling over into this one.
    with patch("SC_redesign.Crop_and_Soil.crop.nitrogen_incorporation.NitrogenIncorporation."
               "determine_layer_nutrient_demands", new_callable=MagicMock, return_value=[1, 2, 3, 4]):
        crop_data = CropData()
        crop_data.max_transpiration = max_trans
        soil_data = SoilData(field_size=1.5)
        wu = WaterUptake(crop_data)
        wu.uptake_water(soil_data)


@pytest.mark.parametrize("layers,uptakes", [
    ([LayerData(bottom_depth=20, top_depth=1, field_size=3), LayerData(bottom_depth=3, top_depth=1, field_size=3),
      LayerData(bottom_depth=2, top_depth=1, field_size=3)], [LayerData(bottom_depth=4, top_depth=1, field_size=3)])
])
def test_extract_water_from_soil(layers, uptakes) -> None:
    """This method only tests for edge cases, other parts of the method already have coverage"""
    crop_data = CropData(actual_water_uptakes=uptakes)
    soil_data = SoilData(soil_layers=layers, field_size=3)
    uptake = WaterUptake(crop_data=crop_data)
    try:
        uptake.extract_water_from_soil(soil_data)
    except Exception as e:
        assert len(soil_data.soil_layers) != len(uptake.crop_data.actual_water_uptakes)
        assert str(e) == "actual_water_uptakes should be the same length as the number of soil layers"


@pytest.mark.parametrize("potential_uptakes,water_availabilities,available_capacities,should_fail",
                         [([0.1, 0.2, 0.3], [9.24, 7.7, 1.31], [2.0, 3.5, 4.2], False),
                          ([0.1, 0.2], [9.24, 7.7, 1.31], [2.0, 3.5, 4.2], True),
                          ([0.1, 0.2, 0.4], [9.24, 7.7], [2.0, 3.5, 4.2], True),
                          ([0.1, 0.2, 0.4], [9.24, 7.7, 1.31], [2.0, 3.5], True)])
def test_reduce_efficiency_of_uptake(potential_uptakes: List[float], water_availabilities: List[float],
                                     available_capacities: List[float], should_fail: bool) -> None:
    if should_fail:
        try:
            WaterUptake._reduce_efficiency_of_uptake(potential_uptakes, water_availabilities, available_capacities)
        except Exception as e:
            assert str(e) == "potential_uptakes, water_availabilities, and available_capacities must be of equal length"
    else:
        zipped = zip(potential_uptakes, water_availabilities, available_capacities)
        expected = [WaterUptake._correct_layer_for_efficiency(pot, avail, cap) for pot, avail, cap in zipped]
        assert expected == WaterUptake._reduce_efficiency_of_uptake(potential_uptakes, water_availabilities,
                                                                    available_capacities)


@pytest.mark.parametrize("potential_uptakes,water_availabilities,unmet_demands,uptake_compensation,should_fail",
                         [([0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], 2.3, False),
                          ([0.1, 0.2], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], 2.5, True)])
def test_adjust_water_uptakes(potential_uptakes: List[float], water_availabilities: List[float],
                              unmet_demands: List[float], uptake_compensation: float, should_fail: bool) -> None:
    if should_fail:
        try:
            WaterUptake._adjust_water_uptakes(potential_uptakes, water_availabilities, unmet_demands,
                                              uptake_compensation)
        except Exception as e:
            assert str(e) == "potential_uptakes and unmet_demands must be the same length."
    else:
        expected = [uptake + (demand * uptake_compensation) for uptake, demand in zip(potential_uptakes, unmet_demands)]
        assert WaterUptake._adjust_water_uptakes(potential_uptakes, water_availabilities, unmet_demands,
                                                 uptake_compensation) == expected



