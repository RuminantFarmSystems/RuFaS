"""
RUFAS: Ruminant Farm Systems Model
File name: field_management_initialization_test.py
Description: tests the instantiation of the field management class structure
    based on user input
Author(s): William Donovan, william.m.donovan@gmail.com
"""

import unittest
from RUFAS.test.field_management.field_management_test_base import FieldManagementTest, FMSoil


class FieldManagementInitializationTest(FieldManagementTest, unittest.TestCase):
    """
    Description:
        subclass of FieldManagementTest and TestCase used to test initialization
        of field_management. Inherits information and setup for the environment
        from FieldManagementTest. Inherits unittest functionality from TestCase
    """

    def set_up_soil(self):
        """
        Description:
            artificially creates a saturated and a dry soil profile in order
            to test the function check_conditions()
        """
        self.saturated_soil = FMSoil(soil_water=30, fc_water=20)
        self.dry_soil = FMSoil(soil_water=20, fc_water=30)

    def setUp(self) -> None:
        """
        Description:
            references FieldManagementTest setUp with additional soil setup for
            testing check_conditions()
        """
        super().setUp()
        self.set_up_soil()

    def test_scheduled_init(self):
        """
        Description:
            tests that the scheduled management object created in
            FieldManagementTest matches with user description
        """
        assert self.scheduled_management_obj.managed_applications.keys() == {'manure', 'fertilizer', 'tillage'}
        manure = self.scheduled_management_obj.managed_applications['manure']
        fert = self.scheduled_management_obj.managed_applications['fertilizer']
        till = self.scheduled_management_obj.managed_applications['tillage']

        assert manure.applications.keys() == {(2010, 100), (2011, 100), (2012, 100)}
        assert fert.applications.keys() == {(2010, 10), (2010, 90), (2011, 90), (2012, 90)}
        assert till.applications.keys() == {(2010, 300), (2011, 300), (2012, 300)}

    def test_repeat_init(self):
        """
        Description:
            tests that the repeat management object created in
            FieldManagementTest matches with user description
        """
        assert self.repeat_management_obj.managed_applications.keys() == {'manure', 'fertilizer', 'tillage'}
        manure = self.repeat_management_obj.managed_applications['manure']
        fert = self.repeat_management_obj.managed_applications['fertilizer']
        till = self.repeat_management_obj.managed_applications['tillage']

        assert manure.applications.keys() == {(2010, -1), (2011, -1), (2012, -1)}
        assert fert.applications.keys() == {(2010, -1), (2011, -1), (2012, -1)}
        assert till.applications.keys() == {(2010, -1), (2011, -1), (2012, -1)}

    def test_mixed_init(self):
        """
        Description:
            tests that the mixed management object created in
            FieldManagementTest matches with user description
        """
        assert self.mixed_management_obj.managed_applications.keys() == {'manure', 'fertilizer', 'tillage'}
        manure = self.mixed_management_obj.managed_applications['manure']
        fert = self.mixed_management_obj.managed_applications['fertilizer']
        till = self.mixed_management_obj.managed_applications['tillage']

        assert manure.applications.keys() == {(2010, -1), (2011, 100), (2012, -1)}
        assert fert.applications.keys() == {(2010, -1), (2011, 90), (2012, -1)}
        assert till.applications.keys() == {(2010, -1), (2011, 300), (2012, -1)}

    def test_conditions(self):
        """
        Description:
            tests whether function check_conditions() returns appropriate
            boolean value given rain (day 24) and wet soil.
        """
        self.FM_time.day = 20
        self.FM_time.year = 1
        assert not self.scheduled_management_obj.check_conditions(self.saturated_soil, self.FM_weather, self.FM_time)
        assert self.scheduled_management_obj.check_conditions(self.dry_soil, self.FM_weather, self.FM_time)

        self.FM_time.day = 24
        self.FM_time.year = 1
        assert not self.scheduled_management_obj.check_conditions(self.dry_soil, self.FM_weather, self.FM_time)

    def test_schedule_app(self):
        """
        Description:
            tests function schedule_application() appropriately sets application
            date
        """
        # TODO: day and year have to match application if scheduled. Check mid year and end of year
        self.repeat_management_obj.managed_applications['manure'].schedule_application(self.FM_time)
        assert (self.FM_time.calendar_year, self.FM_time.day + 1) in \
               self.repeat_management_obj.managed_applications['manure'].applications.keys()

    def test_iterate_app(self):
        """
        Description:
            tests function iterate_application() appropriately moves application
            to the next day
        """
        # TODO: day and year have to match application if scheduled. Check mid year and end of year
        self.repeat_management_obj.managed_applications['manure'].iterate_application(self.FM_time)
        assert (self.FM_time.calendar_year, self.FM_time.day + 1) in \
               self.repeat_management_obj.managed_applications['manure'].applications.keys()


if __name__ == '__main__':
    unittest.main()
