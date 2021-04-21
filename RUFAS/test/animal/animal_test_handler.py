################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: animal_test_handler.py
Description: This file contains the function which runs the unit tests for 
    the animal routines of RUFAS.
Author(s): Militsa Sotirova
"""
################################################################################
from unittest import main
from RUFAS.test.animal import test_lactating_cow


def run_tests():
    """
    Calls the unit test functions for the animal routine.
    """
    print('Running animal tests...')
    main(module=test_lactating_cow, exit=False, buffer=False)
    print()
