"""
RUFAS: Ruminant Farm Systems Model
File name: test_manure_animal_merge.py
Description: Implements test cases
Author(s): Sadman Chowdhury, skc86@cornell.edu
"""

import pytest

from RUFAS.routines.animal import animal_management
from RUFAS.routines.manure_management import manure_management

animal_manure_output_1 = {
  "U": 1,
  "TAN_s": 0,
  "MN": 0,
  "Mkg": 0,
  "TSd": 0,
  "VSd": 0,
  "VSnd": 0,
  "WIP_frac": 0,
  "WOP_frac": 0,
  "p_excrt_manure": 0,
  "p_frac": 0,
  "K_manure": 0,
  "CH4_manure": 0
}

animal_manure_input_1 : animal_management.AnimalManagement = {
  "all_pens" : [
      {
          "manure" : {"U": 0,
          "TAN_s": 0,
          "MN": 0,
          "Mkg": 0,
          "TSd": 0,
          "VSd": 0,
          "VSnd": 0,
          "WIP_frac": 0,
          "WOP_frac": 0,
          "p_excrt_manure": 0,
          "p_frac": 0,
          "K_manure": 0,
          "CH4_manure": 0
          }

      },
      {
          "manure" : {"U": 1,
          "TAN_s": 0,
          "MN": 0,
          "Mkg": 0,
          "TSd": 0,
          "VSd": 0,
          "VSnd": 0,
          "WIP_frac": 0,
          "WOP_frac": 0,
          "p_excrt_manure": 0,
          "p_frac": 0,
          "K_manure": 0,
          "CH4_manure": 0
        }

      }
    ]
        }

animal_manure_input_2 = [0, 1]

#assert(manure_management.compile_manure_for_all_pens(animal_manure_input_1) == animal_manure_output_1

def test_compile_manure_for_all_pens():
	"""Unit test for function compile_manure_for_all_pens in file routines\manure_management\manure_management.py"""
	assert(manure_management.compile_manure_for_all_pens(animal_manure_input_1) == animal_manure_output_1)

def test_combine_manure_for_different_pens():
  assert(manure_management.combine_manure_for_different_pens(animal_manure_input_2, animal_manure_input_1) == animal_manure_output_1)