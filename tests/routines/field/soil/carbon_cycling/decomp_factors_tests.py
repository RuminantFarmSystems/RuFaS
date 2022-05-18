"""
RUFAS: Ruminant Farm Systems Model
File name: decomp_factors_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import logging
from unittest.mock import MagicMock

import numpy as np

from RUFAS.classes import Time
from RUFAS.classes import Weather
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import decomp_factors

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def test_temp_factor():
    LOGGER.info("Testing function: temp_factor")
    test_soil = MagicMock(Soil)
    weather_attributes = {
        "T_avg": [[0]]
    }
    time_attributes = {
        "year": 1,
        "day": 1
    }
    test_weather = MagicMock(Weather)
    test_weather.configure_mock(**weather_attributes)
    test_time = MagicMock(Time)
    test_time.configure_mock(**time_attributes)
    decomp_factors.temp_factor(test_soil, test_weather, test_time)

    LOGGER.info("Checking soil T_d")
    np.testing.assert_almost_equal(0.12513139838984882, test_soil.T_d)


def test_moisture_factor():
    LOGGER.info("Testing function: moisture_factor")
    test_soil = MagicMock(Soil)
    test_soil_layer = MagicMock(Soil.SoilLayer)
    layer_attributes = {
        "water_fac": 0.0
    }
    test_soil_layer.configure_mock(**layer_attributes)
    soil_attributes = {
        "soil_layers": [test_soil_layer]
    }
    test_soil.configure_mock(**soil_attributes)
    decomp_factors.moisture_factor(test_soil)

    LOGGER.info("Checking changes to soil layers")
    LOGGER.info("Checking Layer 0")
    layer0 = test_soil.soil_layers[0]
    np.testing.assert_almost_equal(1.0187946798566629e-05, layer0.M_d)


if __name__ == "__main__":
    test_temp_factor()
