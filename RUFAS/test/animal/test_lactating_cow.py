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
from RUFAS.routines.animal.ration import lactating_cow_ration as ration
from RUFAS.routines.animal.manure import lactating_cow_manure_excretion as manure_excretion
from RUFAS.test.animal import animal_inputs_outputs

class LactatingCowTest(unittest.TestCase):
    
    def set_up_feeds(self):
        feed_info_0 = {
        "feed_library": "Inputs/manure_feed_test.csv",
        
        "available_feeds":
            [
                "Corn_grain",
                "Legume_hay",
                "Cotton_seed",
                "Roasted_soybean",
                "Rye_hay"
            ]
        }
        self.feeds = [Feed(feed_info_0)]
   
    def setUp(self):
        self.inputs_ouputs = animal_inputs_outputs.AnimalInputsOutputs()
        self.set_up_feeds()

    def test_ration_1(self):
        inputs = self.inputs_ouputs.lactating_cow_input_1
        expected_rqmts = self.inputs_ouputs.lactating_cow_expected_rqmts_1
        expected_ration = self.inputs_ouputs.lactating_cow_expected_ration_1
        feed = self.feeds[0]
        
        rqmts, _, _ = ration.calculate_rqmts(inputs['BW'], inputs['BCS'], 
                                       inputs['CBW'], inputs['CI'], 
                                       inputs['concentrate'], inputs['CP_Milk'],
                                       inputs['DOP'],inputs['DHD'],
                                       inputs['DVD'], inputs['DIM'], 
                                       inputs['fat_milk'], 
                                       inputs['lactose_milk'], 
                                       inputs['milk'], inputs['parity'], 
                                       inputs['type'], feed.nutrient_rqmts)

        self.assertEqual(rqmts, expected_rqmts)
        
        formulated_ration = ration.optimize(feed, rqmts)
        
        self.assertEqual(formulated_ration, expected_ration)
        
    def test_manure_1(self):
        inputs = self.inputs_ouputs.lactating_cow_input_1
        input_ration = self.inputs_ouputs.lactating_cow_input_ration_1
        expected_manure = self.inputs_ouputs.lactating_cow_expected_manure_1
        feed = self.feeds[0]
        
        manure = manure_excretion.manure_calculations(input_ration, feed,
                                        inputs['BW'], inputs['DIM'], 
                                        inputs['mPrt'])
            
        self.assertEqual(manure, expected_manure)

if __name__ == '__main__':
    unittest.main()