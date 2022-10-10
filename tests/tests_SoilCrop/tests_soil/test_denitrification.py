"""
RUFAS: Ruminant Farm Systems Model
File name: test_denitrification.py
Description: Implements test cases for denitrification.py
Author(s): Brandon DeBoer, brdeboer@wisc.edu
"""

from RUFAS.routines.field.soil.nitrogen_cycling.denitrification import *
from RUFAS.routines.field.soil.soil import *
from tests.tests_SoilCrop.mock_classes import *

import pytest

from math import exp


@pytest.mark.parametrize("C,rate,water,fc,NO3,temp",[
    (1, 3, 4, 7, 3, 5), #arbitrary starting integer values
    (0, 0, 0, 0, 0, 0), #all zeroes
    (1, 1, 1, 1, 1, 1), #all ones
    (2.5, 1, 3.4, 1.1, 4, 2), # SW > fc
    (2, 3.3, 1, 4, 6.4, 3) #fc > SW
])
def test_denitrification(C , rate, water , fc , NO3 , temp):
    """
    Description:
        Unit test function that tests the denitrification() function in RUFAS/routines/field/soil/nitrogen_cycling/denitrification.py.
        Makes use of pytest parameterization in order to field multiple test scenarios in a single function. Tests that
         the Soil.SoilLayer attributes denitrification and NO3 are calculated and set properly.
    """
    soil_layer = mock_soil_layer(org_C = C,de_N_rate = rate,soil_water = water,fc_water=fc,NO3 = NO3,temp_fac = temp)
    soil = mock_soil(soil_layers = [soil_layer])
    
    # calculate expected results based on soil pseudocode S.D.4 
    DenitrN = 0
    if water > fc:
        DenitrN = NO3 * (1 - exp(-(rate) * temp * C))
    NO3_res = NO3 - DenitrN

    # DN = 0
    # if water > fc:
    #     exp_part = exp(-(rate) * temp * C)
    #     DN = NO3 * (1 - exp_part)

    # DN = min(NO3,DN)
    # NO3_res = NO3 - DN


    # collect function results
    denitrification(soil)
    denitrification_N = soil_layer.denitrification
    no3 = soil_layer.NO3

    assert pytest.approx([denitrification_N,no3]) == [DenitrN,NO3_res]
