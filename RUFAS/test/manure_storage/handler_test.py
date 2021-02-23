"""
RUFAS: Ruminant Farm Systems Model
File name: handler_test.py
Description: tests the function of a manure handler
Author(s): William Donovan, william.m.donovan@gmail.com
"""
import unittest
from .manure_storage_test_base import ManureStorageTest
from RUFAS.routines.manure_storage import manure_handling


class HandlerTest(ManureStorageTest, unittest.TestCase):
    """
    Description:
        subclass of ManureStorageTest and TestCase used to test a manure
        handler. Inherits information and setup for the environment from
        ManureStorageTest. Inherits unittest functionality from TestCase
    """
    def setUp(self):
        """
        Description:
            references ManureStorageTest setUp
        """
        super().setUp()

    def tearDown(self):
        """
        Description:
            references ManureStorageTest tearDown
        """
        super().tearDown()

    def test_handler_1(self):
        """
        Description:
            tests whether the handler correctly collects, processes, and
            passes manure to the associated separator
        """
        pen = self.manure_storage.pens[0]
        separator = self.manure_storage.separators[pen.separator]
        pen.update_pen(self.animal_management)

        assert pen.raw_manure == 70.82359257209554

        manure_handling.update_all(pen, self.manure_storage)
        assert separator.flush_water_volume == 20076.723592572096
        assert separator.TS == pen.TS_loss


if __name__ == '__main__':
    unittest.main()
