################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: test_lactating_cow.py
Description: This file contains the test class for lactating cows, and its main
    function runs the tests.
Author(s): Militsa Sotirova
"""
################################################################################

import unittest
from RUFAS.routines import Feed
from RUFAS.routines.animal.ration import lactating_cow_ration as ration
from RUFAS.routines.animal.manure import lactating_cow_manure_excretion as manure_excretion
from RUFAS.routines.animal.pen import phosphorus_in_ration, calc_DMI
from RUFAS.test.animal import animal_inputs_outputs


class LactatingCowTest(unittest.TestCase):

    def set_up_feeds(self):
        """
        Sets up the list of various feeds that will be used for the unit tests.
        """
        feed_info_0 = {
            "feed_database": "Inputs/feeds.sqlite",
            "table_name": "feed_library",

            "managed_feeds":
                [
                    "Corn_grain",
                    "Legume_hay",
                    "Cotton_seed",
                    "Roasted_soybean",
                    "Rye_hay"
                ],

            "storage_options":
                {
                    "storage_1":
                        {
                            "storage_type": "bag",
                            "moisture": "direct_cut",
                            "additive": "preservative",
                            "packing_density": 14,
                            "inoculation": "heterofermentative",
                            "bunk_type": "open_floor",
                            "ventilation": True,
                            "removal_rate": 6,

                            "initial_dry_matter": 0
                        }
                }
        }
        self.feeds = [Feed(feed_info_0)]

    def setUp(self):
        """
        Sets up the inputs and expected outputs for the unit tests.
        """
        self.inputs_outputs = animal_inputs_outputs.AnimalInputsOutputs()
        self.set_up_feeds()

    def test_ration_1(self):
        inputs = self.inputs_outputs.lactating_cow_input_1
        expected_rqmts = self.inputs_outputs.lactating_cow_expected_rqmts_1
        expected_ration = self.inputs_outputs.lactating_cow_expected_ration_1
        feed = self.feeds[0]

        rqmts, _, _ = ration.calculate_rqmts(inputs['BW'], inputs['BCS'],
                                             inputs['CBW'],
                                             inputs['concentrate'],
                                             inputs['CP_Milk'],
                                             inputs['DOP'], inputs['DHD'],
                                             inputs['DVD'], inputs['DIM'],
                                             inputs['fat_milk'],
                                             inputs['lactose_milk'],
                                             inputs['milk'], inputs['parity'],
                                             inputs['type'],
                                             feed.nutrient_rqmts)

        self.assertEqual(rqmts, expected_rqmts)

        formulated_ration = ration.optimize(feed, rqmts)

        self.assertEqual(formulated_ration, expected_ration)

    def test_manure_1(self):
        inputs = self.inputs_outputs.lactating_cow_input_1
        input_ration = self.inputs_outputs.lactating_cow_input_ration_1
        expected_manure = self.inputs_outputs.lactating_cow_expected_manure_1
        feed = self.feeds[0]
        DMI = calc_DMI(input_ration, feed)
        p_intake, p_conc = phosphorus_in_ration(DMI, input_ration, feed)

        # hard coded value because actual calculations require other variables
        # that aren't able to be inputs (e.g. dP_reserves)
        p_urine = 1
        p_feces_excrt = 1

        excrt, manure = \
            manure_excretion.manure_calculations(input_ration, feed,
                                                 inputs['BW'], inputs['DIM'],
                                                 inputs['mPrt'], inputs['milk'],
                                                 p_feces_excrt, p_urine)

        self.assertEqual(manure, expected_manure)


if __name__ == '__main__':
    unittest.main()
