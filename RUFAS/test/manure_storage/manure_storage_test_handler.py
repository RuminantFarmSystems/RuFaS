"""
RUFAS: Ruminant Farm Systems Model
File name: manure_storage_test_handler.py
Description: driver for the manure storage unit test module
Author(s): William Donovan, william.m.donovan@gmail.com
"""

from unittest import main
from RUFAS.test.manure_storage import handler_test, manure_storage_initialization_test, separator_test, storage_test


def run_tests():
    """
    Calls the unit test functions for the manure storage routine.
    """
    print('Running manure_storage tests...')
    main(module=handler_test, exit=False)
    main(module=manure_storage_initialization_test, exit=False)
    main(module=separator_test, exit=False)
    main(module=storage_test, exit=False)
    print()
