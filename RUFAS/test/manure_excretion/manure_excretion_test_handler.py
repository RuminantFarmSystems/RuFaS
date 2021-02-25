################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: manure_excretion_test_handler.py
Description: This file contains the main driver of the manure excretion subroutine unit tests.
Author(s): Joseph Merhi, jm2257@cornell.edu
"""
################################################################################

from unittest import main
from RUFAS.test.manure_excretion import lactating_cow_test, dry_cow_test, heifer_test, calf_test


def run_tests():
    """
    Calls the unit test functions for the manure excretion subroutine.
    """
    print('Running manure excretion tests...')
    main(module=calf_test, exit=False)
    main(module=heifer_test, exit=False)
    main(module=dry_cow_test, exit=False)
    main(module=lactating_cow_test, exit=False)
    print()


run_tests()
