"""
RUFAS: Ruminant Farm Systems Model
File name: residue_partitioning_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import logging

import numpy as np

from RUFAS.classes import Time
from RUFAS.classes import Weather
from RUFAS.routines.field.crop.crop_types.corn import Corn
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import residue_partitioning, decomp_factors

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

from unittest.mock import MagicMock


def test_residue_partitioning():
    LOGGER.info("Testing function: residue_partitioning")
    test_soil = MagicMock(Soil)
    test_soil_layer = MagicMock(Soil.SoilLayer)
    test_time = MagicMock(Time)
    test_weather = MagicMock(Weather)
    test_crop_type = MagicMock(Corn)

    layer_attributes = {
        "water_fac": 0.0,
        "AG_met": 1250000,
        "BG_met": 1250000,
        "tillage_percent": 0.0,
        "AG_struct": 1250000,
        "BG_struct": 1250000,
        "thickness": 0.0,
        "C_active": 1250000,
        "C_slow": 1250000,
        "C_passive": 1250000,
        "M_d": 0,
        "AG_struct_to_C_active_loss": 0
    }
    soil_attributes = {
        "soil_layers": [test_soil_layer],
        "AG_lignin_res_percent": 17,
        "residue_harvest": 0.0,
        "BG_lignin_res_percent": 17,
        "profile_depth": 279.4
    }
    weather_attributes = {
        "T_avg": [[0]],
        "rainfall": [[0]]
    }
    time_attributes = {
        "year": 1,
        "day": 1
    }
    corn_attributes = {
        "bio_BG": 0,
        "fr_N": 0
    }
    test_soil.configure_mock(**soil_attributes)
    test_soil_layer.configure_mock(**layer_attributes)
    test_weather.configure_mock(**weather_attributes)
    test_time.configure_mock(**time_attributes)
    test_crop_type.configure_mock(**corn_attributes)

    decomp_factors.temp_factor(test_soil, test_weather, test_time)
    residue_partitioning.residue_partitioning(soil=test_soil, crop_type=test_crop_type, weather=test_weather,
                                              time=test_time)

    LOGGER.info("Checking changes to soil")
    np.testing.assert_almost_equal(17.0, test_soil.AG_lignin_res_percent)
    np.testing.assert_almost_equal(0.425, test_soil.AG_L_to_N)

    LOGGER.info("Checking ADJ_crop_type_bio_BG for soil layers")
    np.testing.assert_almost_equal(0.0, test_soil.soil_layers[0].ADJ_crop_type_bio_BG)


if __name__ == "__main__":
    test_residue_partitioning()
