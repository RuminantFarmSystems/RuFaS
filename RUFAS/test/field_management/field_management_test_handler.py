"""
RUFAS: Ruminant Farm Systems Model
File name: field_management_test_handler.py
Description: driver for the field management unit test module
Author(s): William Donovan, william.m.donovan@gmail.com
"""
from unittest import main
from RUFAS.test.field_management import fertilizer_application_test, field_management_initialization_test, \
    manure_application_test, tillage_application_test


def run_tests():
    """
    Description:
        Calls the unit test functions for the field_management routine.
    """
    print('Running field_management tests...')
    main(module=fertilizer_application_test, exit=False, buffer=False)
    main(module=field_management_initialization_test, exit=False, buffer=False)
    main(module=manure_application_test, exit=False, buffer=False)
    main(module=tillage_application_test, exit=False, buffer=False)
    print()
