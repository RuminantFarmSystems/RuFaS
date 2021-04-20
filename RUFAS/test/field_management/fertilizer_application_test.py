"""
RUFAS: Ruminant Farm Systems Model
File name: fertilizer_application_test.py
Description: tests the function of a fertilizer application from field_management.py
Author(s): William Donovan, william.m.donovan@gmail.com
"""

import unittest
from RUFAS.test.field_management.field_management_test_base import FieldManagementTest
from RUFAS.routines.field.field_management import fertilizer_application


class FertilizerApplicationTest(FieldManagementTest, unittest.TestCase):
    """
    Description:
        subclass of FieldManagementTest and TestCase used to test a fertilizer
        application. Inherits information and setup for the environment from
        FieldManagementTest. Inherits unittest functionality from TestCase
    """

    def setUp(self):
        """
        Description:
            references FieldManagementTest setUp. test_fert_app is the specific
            fertilizer application being tested.
        """
        super().setUp()
        self.test_fert_app = fertilizer_application.formulate_fert_app(self.FM_soil, self.scheduled_management_obj,
                                                                       self.scheduled_management_obj.managed_applications[
                                                                           'fertilizer'].applications[(2010, 10)].data)

    def test_formulation(self):
        """
        Description:
            tests fertilizer application is formulated correctly in accordance
            with fertilizer composition and user input.
        """
        assert self.scheduled_management_obj.fert_applied == 2000
        assert self.test_fert_app['N_mass'] == 100
        assert self.test_fert_app['P_mass'] == 200
        assert self.test_fert_app['K_mass'] == 300

    def test_fert_P(self):
        """
        Description:
            tests that fertilizer Phosphorus is correctly applied to the soil
        """
        fertilizer_application.fertilizer_P(self.FM_soil, self.scheduled_management_obj, self.test_fert_app)
        assert self.FM_soil.fert_P_released == 0.25 * 200 * 0.95
        assert round(self.FM_soil.soil_layers[0].labile_P, 3) == 200 * 0.05

    def test_fert_N(self):
        """
        Description:
            tests that fertilizer Nitrogen is correctly applied to the soil
        """
        fertilizer_application.fertilizer_N(self.FM_soil, self.scheduled_management_obj, self.test_fert_app)
        assert self.FM_soil.soil_layers[0].NH4 == 100

    def test_fert_K(self):
        """
        Description:
            tests that fertilizer Potassium is correctly applied to the soil
        """
        fertilizer_application.fertilizer_K(self.FM_soil, self.scheduled_management_obj, self.test_fert_app)
        assert self.FM_soil.soil_layers[0].K == 300


if __name__ == '__main__':
    unittest.main()
