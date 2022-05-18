"""
RUFAS: Ruminant Farm Systems Model
File name: carbon_cycle_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import logging
from unittest.mock import MagicMock

import numpy as np

from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import carbon_cycle

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def test_soil_carbon_aggregation():
    LOGGER.info("Testing function: soil_carbon_aggregation")
    test_soil = MagicMock(Soil)
    test_soil_layer = MagicMock(Soil.SoilLayer)
    layer_attributes = {
        "bottom_depth": 279.4,
        "bulk_density": 1.34,
        "C_active": 1250000,
        "C_slow": 1250000,
        "C_passive": 1250000,
        "AG_struct_to_C_active_loss": 0,
        "AG_met_to_C_active_loss": 0,
        "AG_struct_to_C_slow_loss": 0,
        "BG_met_to_C_active_loss": 0,
        "BG_struct_to_C_active_loss": 0,
        "BG_struct_to_C_slow_loss": 0,
        "C_CO2_loss_decomp": 0,
        "C_active_loss": 0,
        "C_slow_loss": 0,
        "C_passive_loss": 0
    }
    test_soil_layer.configure_mock(**layer_attributes)
    soil_attributes = {
        "soil_layers": [test_soil_layer],
        "curr_layer_depth": 0,
        "area": 1.0
    }
    test_soil.configure_mock(**soil_attributes)
    carbon_cycle.soil_carbon_aggregation(test_soil)

    LOGGER.info("Checking number of layers")
    assert len(test_soil.soil_layers) == 1

    LOGGER.info("Checking changes to soil layers")
    LOGGER.info("Checking Layer 0")
    layer0 = test_soil.soil_layers[0]
    np.testing.assert_almost_equal(1.0016132650989862, layer0.C_percent)
    np.testing.assert_almost_equal(1.0016132650989862, layer0.org_C)
    np.testing.assert_almost_equal(3750000, layer0.C)
    np.testing.assert_almost_equal(3750, layer0.C_mg)
    np.testing.assert_almost_equal(375000.0, layer0.C_g)
    np.testing.assert_almost_equal(0.0, layer0.C_CO2_loss_decomp)
    np.testing.assert_almost_equal(0.0, layer0.C_CO2_loss)

    assert test_soil.curr_layer_depth == 0


if __name__ == "__main__":
    test_soil_carbon_aggregation()
