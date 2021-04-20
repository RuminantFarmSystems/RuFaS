################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: heifer_test.py
Description: This file contains the manure excretion subroutine unit tests for heifers.
Author(s): Joseph Merhi, jm2257@cornell.edu
"""
################################################################################

import unittest
from RUFAS.routines import Feed
from RUFAS.routines.animal.manure import growing_heifer_manure_excretion as manure_excretion
from RUFAS.test.manure_excretion import inputs_outputs


class HeiferTest(unittest.TestCase):

    def set_up_feeds(self):
        """
        Sets up the list of various feeds that will be used for the unit tests.
        """
        feed_info_0 = {
            "feed_database": "C:\\Users\\josep\\PycharmProjects\\MASM\\input\\databases\\feeds.sqlite",
            "feeds_table": "user_feeds",
            "feed_quality_table": "feed_quality",
            "nutrient_table": "nutrients",

            "purchased_feeds": [2, 26, 36, 86, 118, 136, 139],
            "purchased_feeds_costs": {"2": 0.17, "26": 0.1, "36": 0, "86": 0,
                                      "118": 0.39, "136": 0.53, "139": 0.25},
            "growing_feeds": [87],

            "storage_options": {
                "storage_1": {
                    "storage_type": "bag",
                    "moisture": "direct_cut",
                    "additive": "preservative",
                    "packing_density": 14,
                    "inoculation": "heterofermentative",
                    "bunk_type": "open_floor",
                    "ventilation": True,
                    "removal_rate": 6,
                    "initial_dry_matter": 0
                },
                "storage_2": {
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
        self.inputs_outputs = inputs_outputs.AnimalInputOutputs()
        self.set_up_feeds()

    def test_manure_1(self):
        inputs = self.inputs_outputs.heifer_input_1
        input_ration = self.inputs_outputs.ration_formulation0
        expected_manure = self.inputs_outputs.expected_heifer_manure_1
        feed = self.feeds[0]

        excrt, manure = \
            manure_excretion.manure_calculations(input_ration, feed,
                                                 inputs['BW'], inputs['p_feces_excrt'], inputs['p_urine'])
        self.assertEqual(manure, expected_manure)


if __name__ == '__main__':
    unittest.main()
