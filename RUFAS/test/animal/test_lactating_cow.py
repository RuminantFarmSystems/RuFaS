################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: t_ration.py
Description:
Author(s): Militsa Sotirova
"""
################################################################################

import unittest
from RUFAS.routines import Feed
from RUFAS.routines.animal import ration
from RUFAS.test.animal import animal_inputs_outputs

class LactatingCowTest(unittest.TestCase):
    
    def set_up_feeds(self):
        feed_info = {
        "feed_library": "Inputs/testing_ration_feedlib.csv",
        
        "available_feeds":
            [
                "Corn_grain",
                "Legume_hay",
                "Cotton_seed",
                "Roasted_soybean",
                "Rye_hay"
            ]
        }
        self.feeds = [Feed(feed_info)]
   
    def setUp(self):
        self.inputs_ouputs = animal_inputs_outputs.AnimalInputsOutputs()
        self.set_up_feeds()

    def test_ration_1(self):
        inputs = self.inputs_ouputs.lactating_cow_input_1
        expected_rqmts = self.inputs_ouputs.lactating_cow_expected_rqmts_1
        expected_ration = self.inputs_ouputs.lactating_cow_expected_ration_1
        feed = self.feeds[0]
        
        rqmts = ration.calculate_rqmts(inputs['BW'], inputs['BCS'], 
                                       inputs['CBW'], inputs['CI'], 
                                       inputs['concentrate'], inputs['CP_Milk'],
                                       inputs['DOP'],inputs['DHD'],
                                       inputs['DVD'], inputs['DIM'], 
                                       inputs['fat_milk'], 
                                       inputs['lactose_milk'], 
                                       inputs['milk'], inputs['parity'], 
                                       inputs['type'], feed.nutrient_rqmts)
    
        formulated_ration = ration.optimize(feed, rqmts)
        
        self.assertEqual(rqmts, expected_rqmts)
        self.assertEqual(formulated_ration, expected_ration)

if __name__ == '__main__':
    unittest.main()