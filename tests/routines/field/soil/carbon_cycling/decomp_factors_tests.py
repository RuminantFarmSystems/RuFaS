"""
RUFAS: Ruminant Farm Systems Model
File name: decomp_factors_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import pytest
import json
import logging
import numpy as np
import sys 
import os 

sys.path.insert(0, os.path.dirname(os.path.realpath(__name__)))

from RUFAS.routines.field.soil.carbon_cycling import decomp_factors
from RUFAS.routines.field.soil import Soil
from config.defintions import ROOT_DIR
from RUFAS.classes import Weather
from RUFAS.classes import Config
from RUFAS.classes import Time

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

LOGGER.info("Read json file: ARL_soil_tillage.json")
soil_file = open(ROOT_DIR + "/input/soil/ARL_soil_tillage.json")
path_to_weather_file = ROOT_DIR + "/input/weather/ARL_weather.csv"

LOGGER.info("Convert from json file format to Python dictionary")
soil_data = json.load(soil_file)


def test_temp_factor():
	LOGGER.info("Testing function: temp_factor")
	test_soil = Soil(soil_data)
	test_config_data = {
		"start_date": "1990:1",
		"end_date": "2019:365",
		"csv_dir": "output/CSVs/",
		"graphic_dir": "output/graphics/",
		"set_seed": False,
		"seed": 0
	}
	test_config = Config(test_config_data, path_to_weather_file)
	test_weather = Weather(path_to_weather_file, test_config)
	test_time = Time(test_config)
	decomp_factors.temp_factor(test_soil, test_weather, test_time)

	LOGGER.info("Checking soil T_d")
	np.testing.assert_almost_equal(0.06893050947285823, test_soil.T_d)


def test_moisture_factor():
	LOGGER.info("Testing function: moisture_factor")
	test_soil = Soil(soil_data)
	decomp_factors.moisture_factor(test_soil)

	LOGGER.info("Checking changes to soil layers")
	LOGGER.info("Checking Layer 0")
	layer0 = test_soil.soil_layers[0]
	np.testing.assert_almost_equal(1.0187946798566629e-05, layer0.M_d)

	LOGGER.info("Checking Layer 1")
	layer1 = test_soil.soil_layers[1]
	np.testing.assert_almost_equal(1.0187946798566629e-05, layer1.M_d)

	LOGGER.info("Checking Layer 2")
	layer2 = test_soil.soil_layers[2]
	np.testing.assert_almost_equal(1.0187946798566629e-05, layer2.M_d)

	LOGGER.info("Checking Layer 3")
	layer3 = test_soil.soil_layers[3]
	np.testing.assert_almost_equal(1.0187946798566629e-05, layer3.M_d)

if __name__ == "__main__":
  test_temp_factor()
