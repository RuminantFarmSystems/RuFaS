"""
RUFAS: Ruminant Farm Systems Model
File name: residue_partitioning_tests.py
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

from RUFAS.routines.field.crop.crop_types.corn import Corn
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import residue_partitioning, decomp_factors
from config.defintions import ROOT_DIR
from RUFAS.classes import Weather
from RUFAS.classes import Config
from RUFAS.classes import Time

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

LOGGER.info("Read json file: ARL_soil_tillage.json")
soil_file = open(ROOT_DIR + "/input/soil/ARL_soil_tillage.json")
LOGGER.info("Read json file: ARL_rotation.json")
crop_file = open(ROOT_DIR + "/input/crop/ARL_rotation.json")
path_to_weather_file = ROOT_DIR + "/input/weather/ARL_weather.csv"

LOGGER.info("Convert from json file format to Python dictionary")
soil_data = json.load(soil_file)
crop_data = json.load(crop_file)


def test_residue_partitioning():
    LOGGER.info("Testing function: residue_partitioning")
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
    corn89_data = crop_data["crops"]["corn_89"]
    test_crop_type = Corn("corn_89", corn89_data)

    decomp_factors.temp_factor(test_soil, test_weather, test_time)
    residue_partitioning.residue_partitioning(soil=test_soil, crop_type=test_crop_type, weather=test_weather, time=test_time)

    LOGGER.info("Checking changes to soil")
    np.testing.assert_almost_equal(17.0, test_soil.AG_lignin_res_percent)
    np.testing.assert_almost_equal(0.425, test_soil.AG_L_to_N)

    LOGGER.info("Checking ADJ_crop_type_bio_BG for soil layers")
    np.testing.assert_almost_equal(0.0, test_soil.soil_layers[0].ADJ_crop_type_bio_BG)
    np.testing.assert_almost_equal(0.0, test_soil.soil_layers[1].ADJ_crop_type_bio_BG)
    np.testing.assert_almost_equal(0.0, test_soil.soil_layers[2].ADJ_crop_type_bio_BG)
    np.testing.assert_almost_equal(0.0, test_soil.soil_layers[3].ADJ_crop_type_bio_BG)


if __name__ == "__main__":
   test_residue_partitioning()
