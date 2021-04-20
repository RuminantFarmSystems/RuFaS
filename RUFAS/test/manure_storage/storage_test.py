"""
RUFAS: Ruminant Farm Systems Model
File name: storage_test.py
Description: tests the function of a manure storage receptacle
Author(s): William Donovan, william.m.donovan@gmail.com
"""
import unittest
from .manure_storage_test_base import ManureStorageTest
from RUFAS.routines.manure_storage import manure_handling, manure_separator, manure_emissions


class StorageTest(ManureStorageTest, unittest.TestCase):
    """
    Description:
        subclass of ManureStorageTest and TestCase used to test a storage
        receptacle. Inherits information and setup for the environment from
        ManureStorageTest. Inherits unittest functionality from TestCase
    """
    def setUp(self):
        """
        Description:
            references ManureStorageTest setUp. Establishes pen-separator-
            storage relationship. Sends manure through the handler and separator
            into the storage receptacle.
        """
        super().setUp()
        pen = self.manure_storage.pens[0]
        separator = self.manure_storage.separators[pen.separator]
        self.storage = self.manure_storage.storage[separator.storage_system]
        manure_handling.update_all(pen, self.manure_storage)
        manure_separator.update_all(separator, self.manure_storage)

    def test_storage_1(self):
        """
        Description:
            tests that manure is appropriately stored in the receptacle and
            that methane emission is calculated correctly.
        """
        manure_emissions.update_all(self.storage, self.manure_storage)
        assert self.manure_storage.CH4_emissions == 0.268420815405238


if __name__ == '__main__':
    unittest.main()
