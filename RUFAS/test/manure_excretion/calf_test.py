################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: calf_test.py
Description: This file contains the manure excretion subroutine unit tests for calves.
Author(s): Joseph Merhi, jm2257@cornell.edu
"""
################################################################################

import unittest
from RUFAS.routines.animal.manure import calf_manure_excretion as manure_excretion
from RUFAS.test.manure_excretion import inputs_outputs


class CalfTest(unittest.TestCase):
    def setUp(self):
        """
        Sets up the inputs and expected outputs for the unit tests.
        """
        self.inputs_outputs = inputs_outputs.AnimalInputOutputs()

    def test_manure_1(self):
        inputs = self.inputs_outputs.calf_input_1
        expected_manure = self.inputs_outputs.expected_calf_manure_1

        excrt, manure = \
            manure_excretion.manure_calculations(inputs['BW'], inputs['p_feces_excrt'], inputs['p_urine'])
        self.assertEqual(manure, expected_manure)


if __name__ == '__main__':
    unittest.main()
