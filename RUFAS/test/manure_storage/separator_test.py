"""
RUFAS: Ruminant Farm Systems Model
File name: separator_test.py
Description: tests the function of a manure separator
Author(s): William Donovan, william.m.donovan@gmail.com
"""
import unittest
from .manure_storage_test_base import ManureStorageTest
from RUFAS.routines.manure_storage import manure_handling, manure_separator


class SeparatorTest(ManureStorageTest, unittest.TestCase):
    """
    Description:
        subclass of ManureStorageTest and TestCase used to test a manure
        separator. Inherits information and setup for the environment from
        ManureStorageTest. Inherits unittest functionality from TestCase
    """
    def setUp(self):
        """
        Description:
            references ManureStorageTest setUp. Establishes pen and separator
            relationship then passes manure through the handler to the separator
        """
        super().setUp()
        pen = self.manure_storage.pens[0]
        self.separator = self.manure_storage.separators[pen.separator]
        pen.update_pen(self.animal_management)
        manure_handling.update_all(pen, self.manure_storage)

    def tearDown(self):
        """
        Description:
            references ManureStorageTest tearDown
        """
        super().tearDown()

    def test_separator_1(self):
        """
        Description:
            tests whether the separator correctly processes, and
            passes manure to the associated storage receptacle
        """
        manure_separator.update_all(self.separator, self.manure_storage)
        assert self.separator.TS_liquid == 281.07413029600934
        assert self.separator.TS_DM_effluent == 24.09206831108652
        assert self.separator.TS == 96.36827324434607

        assert self.manure_storage.storage[self.separator.storage_system].TS == 96.36827324434607


if __name__ == '__main__':
    unittest.main()
