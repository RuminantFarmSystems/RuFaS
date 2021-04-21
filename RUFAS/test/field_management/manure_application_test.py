"""
RUFAS: Ruminant Farm Systems Model
File name: manure_application_test.py
Description: tests the function of a manure application from field_management.py
Author(s): William Donovan, william.m.donovan@gmail.com
"""
import unittest
from .field_management_test_base import FieldManagementTest
from RUFAS.routines.field.field_management.manure_application import *


class ManureApplicationTest(FieldManagementTest, unittest.TestCase):
    """
    Description:
        subclass of FieldManagementTest and TestCase used to test a manure
        application. Inherits information and setup for the environment from
        FieldManagementTest. Inherits unittest functionality from TestCase
    """
    def set_up_manure_app(self, N_mass=100, P_mass=100):
        """
        Description:
            Allows changes to be made to the essential data of a manure app
        Args:
            N_mass: default 100kg, requested mass of Nitrogen in application
            P_mass: default 100kg, requested mass of Phosphorus in application
        """
        self.requested_manure_app = {
            'N_mass': N_mass,
            'P_mass': P_mass,
            'cover_percent': 0.95,
            'surface_percent': 1.0,
            'depth': 0.0
        }

    def setUp(self):
        """
        Description:
            references FieldManagementTest setUp. manure_application is the
            specific manure application being tested.
        """
        super().setUp()
        self.set_up_manure_app()
        self.manure_application = formulate_manure_application(self.FM_manure_storage, self.requested_manure_app)

    def test_formulation(self):
        """
        Description:
            tests manure application is formulated correctly in accordance
            with composition of available manure and user input.
        """
        assert self.manure_application == {
            'N_mass': 100,
            'P_mass': 100,
            'cover_percent': 0.95,
            'surface_percent': 1.0,
            'depth': 0.0,
            'mass': 2000,
            'DM': 1300,
            'WIP': 0.0,
            'WOP': 0.0
        }

    def test_manure_N(self):
        """
        Description:
            tests that manure Nitrogen is correctly applied to the soil
        """
        added_manure_N(self.FM_soil, self.scheduled_management_obj, self.manure_application)
        assert self.FM_soil.soil_layers[0].active_N == 87.5
        assert self.FM_soil.soil_layers[0].stable_N == 12.5

    def test_manure_P(self):
        """
        Description:
            tests that manure Phosphorus is correctly applied to the soil
        """
        added_manure_P(self.FM_soil, self.scheduled_management_obj, self.manure_application)
        assert self.FM_soil.soil_layers[0].labile_P == 52.22601923076923
        assert self.FM_soil.soil_layers[0].active_P == 18.32491902834008


if __name__ == '__main__':
    unittest.main()
