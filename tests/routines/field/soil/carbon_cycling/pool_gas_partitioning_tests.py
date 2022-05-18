"""
RUFAS: Ruminant Farm Systems Model
File name: pool_gas_partitioning_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import logging

import numpy as np

from RUFAS.classes import Time
from RUFAS.classes import Weather
from RUFAS.routines.field.crop.crop_types.corn import Corn
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import residue_partitioning, decomp_factors, pool_gas_partitioning

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

from unittest.mock import MagicMock


def test_update_all():
    LOGGER.info("Testing function: update_all")
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
        "C_passive": 1250000
    }
    soil_attributes = {
        "soil_layers": [test_soil_layer],
        "AG_lignin_res_percent": 17,
        "residue_harvest": 0.0,
        "BG_lignin_res_percent": 17,
        "profile_depth": 279.4,
        "silt_to_clay_percent": 0.5
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

    decomp_factors.update_all(test_soil, test_weather, test_time)
    residue_partitioning.update_all(soil=test_soil, crop_type=test_crop_type, weather=test_weather,
                                    time=test_time)
    pool_gas_partitioning.update_all(test_soil)

    LOGGER.info("Checking changes to soil layers")
    LOGGER.info("Checking Layer 0")
    layer0 = test_soil.soil_layers[0]
    np.testing.assert_almost_equal(0.03505788081471571, layer0.AG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.028683720666585574, layer0.AG_met_to_C_active_act)
    np.testing.assert_almost_equal(8.77950623625564e-05, layer0.AG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.00010730507622090227, layer0.AG_struct_to_C_active_act)
    np.testing.assert_almost_equal(5.85300415750376e-05, layer0.AG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.00013657009700842107, layer0.AG_struct_to_C_slow_act)
    np.testing.assert_almost_equal(0.043822351018394635, layer0.BG_met_to_C_active_loss)
    np.testing.assert_almost_equal(0.035854650833231964, layer0.BG_met_to_C_active_act)
    np.testing.assert_almost_equal(0.009609046423306167, layer0.BG_struct_to_C_active_loss)
    np.testing.assert_almost_equal(0.011744390072929762, layer0.BG_struct_to_C_active_act)
    np.testing.assert_almost_equal(0.006406030948870778, layer0.BG_struct_to_C_slow_loss)
    np.testing.assert_almost_equal(0.014947405547365148, layer0.BG_struct_to_C_slow_act)


if __name__ == "__main__":
    test_update_all()
