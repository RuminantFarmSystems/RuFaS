"""
RUFAS: Ruminant Farm Systems Model
File name: pool_gas_partitioning_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import pytest
import json
import logging
import numpy as np

from RUFAS.routines.field.crop.crop_types.corn import Corn
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import residue_partitioning, decomp_factors, pool_gas_partitioning
from config.defintions import ROOT_DIR
from RUFAS.classes import Weather
from RUFAS.classes import Config
from RUFAS.classes import Time

LOGGER = logging.getLogger(__name__)

LOGGER.info("Read json file: ARL_soil_tillage.json")
soil_file = open(ROOT_DIR + "/input/soil/ARL_soil_tillage.json")
LOGGER.info("Read json file: ARL_rotation.json")
crop_file = open(ROOT_DIR + "/input/crop/ARL_rotation.json")
path_to_weather_file = ROOT_DIR + "/input/weather/ARL_weather.csv"

LOGGER.info("Convert from json file format to Python dictionary")
soil_data = json.load(soil_file)
crop_data = json.load(crop_file)

def test_update_all():
    LOGGER.info("Testing function: update_all")
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

    decomp_factors.update_all(test_soil, test_weather, test_time)
    residue_partitioning.update_all(soil=test_soil, crop_type=test_crop_type, weather=test_weather,
                                              time=test_time)
    pool_gas_partitioning.update_all(test_soil)

    LOGGER.info("Checking changes to soil layers")
    LOGGER.info("Checking Layer 0")
    layer0 = test_soil.soil_layers[0]
    np.testing.assert_almost_equal(0.01931215999095825, layer0.AG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.015800858174420382, layer0.AG_met_to_C_active_act)
    np.testing.assert_almost_equal(4.836322822029068e-05, layer0.AG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(5.911061226924417e-05, layer0.AG_struct_to_C_active_act)
    np.testing.assert_almost_equal(3.224215214686045e-05, layer0.AG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(7.523168834267439e-05, layer0.AG_struct_to_C_slow_act)
    np.testing.assert_almost_equal(0.02414019998869781, layer0.BG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.019751072718025477, layer0.BG_met_to_C_active_act)
    np.testing.assert_almost_equal(0.005293287488430829, layer0.BG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.006469573596971014, layer0.BG_struct_to_C_active_act)
    np.testing.assert_almost_equal(0.0035288583256205524, layer0.BG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.008234002759781289, layer0.BG_struct_to_C_slow_act)

    LOGGER.info("Checking Layer 1")
    layer1 = test_soil.soil_layers[1]
    np.testing.assert_almost_equal(0.01931215999095825, layer1.AG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.015800858174420382, layer1.AG_met_to_C_active_act)
    np.testing.assert_almost_equal(4.836322822029068e-05, layer1.AG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(5.911061226924417e-05, layer1.AG_struct_to_C_active_act)
    np.testing.assert_almost_equal(3.224215214686045e-05, layer1.AG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(7.523168834267439e-05, layer1.AG_struct_to_C_slow_act)
    np.testing.assert_almost_equal(0.02414019998869781, layer1.BG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.019751072718025477, layer1.BG_met_to_C_active_act)
    np.testing.assert_almost_equal(0.005293287488430829, layer1.BG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.006469573596971014, layer1.BG_struct_to_C_active_act)
    np.testing.assert_almost_equal(0.0035288583256205524, layer1.BG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.008234002759781289, layer1.BG_struct_to_C_slow_act)

    LOGGER.info("Checking Layer 2")
    layer2 = test_soil.soil_layers[2]
    np.testing.assert_almost_equal(0.01931215999095825, layer2.AG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.015800858174420382, layer2.AG_met_to_C_active_act)
    np.testing.assert_almost_equal(4.836322822029068e-05, layer2.AG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(5.911061226924417e-05, layer2.AG_struct_to_C_active_act)
    np.testing.assert_almost_equal(3.224215214686045e-05, layer2.AG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(7.523168834267439e-05, layer2.AG_struct_to_C_slow_act)
    np.testing.assert_almost_equal(0.02414019998869781, layer2.BG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.019751072718025477, layer2.BG_met_to_C_active_act)
    np.testing.assert_almost_equal(0.005293287488430829, layer2.BG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.006469573596971014, layer2.BG_struct_to_C_active_act)
    np.testing.assert_almost_equal(0.0035288583256205524, layer2.BG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.008234002759781289, layer2.BG_struct_to_C_slow_act)

    LOGGER.info("Checking Layer 3")
    layer3 = test_soil.soil_layers[3]
    np.testing.assert_almost_equal(0.01931215999095825, layer3.AG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.015800858174420382, layer3.AG_met_to_C_active_act)
    np.testing.assert_almost_equal(4.836322822029068e-05, layer3.AG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(5.911061226924417e-05, layer3.AG_struct_to_C_active_act)
    np.testing.assert_almost_equal(3.224215214686045e-05, layer3.AG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(7.523168834267439e-05, layer3.AG_struct_to_C_slow_act)
    np.testing.assert_almost_equal(0.02414019998869781, layer3.BG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.019751072718025477, layer3.BG_met_to_C_active_act)
    np.testing.assert_almost_equal(0.005293287488430829, layer3.BG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.006469573596971014, layer3.BG_struct_to_C_active_act)
    np.testing.assert_almost_equal(0.0035288583256205524, layer3.BG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.008234002759781289, layer3.BG_struct_to_C_slow_act)
