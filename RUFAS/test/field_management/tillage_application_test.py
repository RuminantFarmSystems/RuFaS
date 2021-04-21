"""
RUFAS: Ruminant Farm Systems Model
File name: tillage_application_test.py
Description: tests the function of a tillage application from field_management.py
Author(s): William Donovan, william.m.donovan@gmail.com
"""
import unittest
from .field_management_test_base import FieldManagementTest, FMSoil
from RUFAS.routines.field.field_management import tillage_application


class TillageApplicationTest(FieldManagementTest, unittest.TestCase):
    """
    Description:
        subclass of FieldManagementTest and TestCase used to test a tillage
        application. Inherits information and setup for the environment from
        FieldManagementTest. Inherits unittest functionality from TestCase
    """
    def setUp(self) -> None:
        """
        Description:
            references FieldManagementTest setUp. nutrient_soil emulates a
            profile with fresh nutrient application to allows for
            incorporation testing
        """
        super().setUp()
        self.nutrient_soil = FMSoil(fert_P_available=20, fert_P_released=20, WIP=20, SIP=20)

    def test_tillage(self):
        """
        Description:
            tests whether nutrients on the top of the profile are correctly
            introduced into lower layers by a tillage application.
        """
        tillage_application.update_all(self.nutrient_soil, self.scheduled_management_obj.managed_applications[
            'tillage'].applications[(2010, 300)].data)
        assert self.nutrient_soil.WIP == (20 - 20 * 0.3)
        assert self.nutrient_soil.SIP == (20 - 20 * 0.3)
        assert self.nutrient_soil.soil_layers[0].labile_P == 18
        assert self.nutrient_soil.soil_layers[0].active_P == 6


if __name__ == '__main__':
    unittest.main()
