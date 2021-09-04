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
# from RUFAS.routines.animal.manure import lactating_cow_manure_excretion as manure_excretion
from RUFAS.test.animal import animal_inputs_outputs


class LactatingCowTest(unittest.TestCase):

    def set_up_feeds(self):
        """
        Sets up the list of various feeds that will be used for the unit tests.
        """
        feed_info_0 = {
            "feed_database": "input/databases/feeds.sqlite",
            "table_name": "feed_library",
            "feeds_table": "user_feeds",
            "feed_quality_table": "feed_quality",
            "nutrient_table": "nutrients",
            "purchased_feeds": [2, 26, 36, 86, 118, 136, 139],
            "purchased_feeds_costs": {"2": 0.17, "26": 0.1, "36": 0, "86": 0,
                                      "118": 0.39, "136": 0.53, "139": 0.25},
            "farm_grown_feeds": [],


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
        self.inputs_outputs = animal_inputs_outputs.AnimalInputOutputs()
        self.set_up_feeds()

    # TODO: this test is no longer functional. See manure excretion submodule
    # def test_manure_1(self):
    #     inputs = self.inputs_outputs.lactating_cow_input_1
    #     input_ration = self.inputs_outputs.lactating_cow_input_ration_1
    #     expected_manure = self.inputs_outputs.lactating_cow_expected_manure_1
    #     feed = self.feeds[0]
    #     # hardcoded for now
    #     DMI = 25
    #     p_intake, p_conc = 4, 0.3
    #
    #     # hard coded value because actual calculations require other variables
    #     # that aren't able to be inputs (e.g. dP_reserves)
    #     p_urine = 1
    #     p_feces_excrt = 1
    #
    #     excrt, manure = \
    #         manure_excretion.manure_calculations(input_ration, feed,
    #                                              inputs['BW'], inputs['DIM'],
    #                                              inputs['mPrt'], inputs['milk'],
    #                                              p_feces_excrt, p_urine)
    #
    #     self.assertEqual(manure, expected_manure)


if __name__ == '__main__':
    unittest.main()
