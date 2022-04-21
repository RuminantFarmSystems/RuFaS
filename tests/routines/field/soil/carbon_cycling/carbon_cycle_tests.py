"""
RUFAS: Ruminant Farm Systems Model
File name: carbon_cycle_tests.py
Description: Implements test cases
Author(s): Jessica Tweneboah, jnt42@cornell.edu
"""

import json
import logging
import numpy as np
import sys
import os 
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, os.path.dirname(os.path.realpath(__name__)))

from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import carbon_cycle
from config.defintions import ROOT_DIR

LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

LOGGER.info("Read json file: ARL_soil_tillage.json")
soil_file = open(ROOT_DIR + "/input/soil/ARL_soil_tillage.json")
LOGGER.info("Convert from json file format to Python dictionary")
soil_data = json.load(soil_file)


def test_soil_carbon_aggregation():
	LOGGER.info("Testing function: soil_carbon_aggregation")
	test_soil = Soil(soil_data)
	carbon_cycle.soil_carbon_aggregation(test_soil)

	LOGGER.info("Checking number of layers")
	assert len(test_soil.soil_layers) == 4

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

	LOGGER.info("Checking Layer 1")
	layer1 = test_soil.soil_layers[1]
	np.testing.assert_almost_equal(0.3465675945436397, layer1.C_percent)
	np.testing.assert_almost_equal(0.3465675945436397, layer1.org_C)
	np.testing.assert_almost_equal(3750000, layer1.C)
	np.testing.assert_almost_equal(3750, layer1.C_mg)
	np.testing.assert_almost_equal(375000.0, layer1.C_g)
	np.testing.assert_almost_equal(0.0, layer1.C_CO2_loss_decomp)
	np.testing.assert_almost_equal(0.0, layer1.C_CO2_loss)

	LOGGER.info("Checking Layer 2")
	layer2 = test_soil.soil_layers[2]
	np.testing.assert_almost_equal(1.845472440944882, layer2.C_percent)
	np.testing.assert_almost_equal(1.845472440944882, layer2.org_C)
	np.testing.assert_almost_equal(3750000, layer2.C)
	np.testing.assert_almost_equal(3750, layer2.C_mg)
	np.testing.assert_almost_equal(375000.0, layer2.C_g)
	np.testing.assert_almost_equal(0.0, layer2.C_CO2_loss_decomp)
	np.testing.assert_almost_equal(0.0, layer2.C_CO2_loss)

	LOGGER.info("Checking Layer 3")
	layer3 = test_soil.soil_layers[3]
	np.testing.assert_almost_equal(0.2982581722739203, layer3.C_percent)
	np.testing.assert_almost_equal(0.2982581722739203, layer3.org_C)
	np.testing.assert_almost_equal(3750000, layer3.C)
	np.testing.assert_almost_equal(3750, layer3.C_mg)
	np.testing.assert_almost_equal(375000.0, layer3.C_g)
	np.testing.assert_almost_equal(0.0, layer3.C_CO2_loss_decomp)
	np.testing.assert_almost_equal(0.0, layer3.C_CO2_loss)

	assert test_soil.curr_layer_depth == 0

if __name__ == "__main__":
   test_soil_carbon_aggregation()
