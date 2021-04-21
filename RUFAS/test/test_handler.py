
"""
RUFAS: Ruminant Farm Systems Model
File name: test_handler.py
Description: This file contains the function which runs the unit tests for
    the routines of RUFAS.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
            William Donovan, william.m.donovan@gmail.com
"""

from RUFAS.test.animal import animal_test_handler as animal
from RUFAS.test.field_management import field_management_test_handler as field_management
from RUFAS.test.manure_storage import manure_storage_test_handler as manure_storage


def run_tests():
    """
    Calls the unit test functions for each routine that has them.
    """

    animal.run_tests()
    field_management.run_tests()
    manure_storage.run_tests()
    print('Tests completed.\n')
