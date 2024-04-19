import pytest
import numpy as np
from typing import Any, Dict
from unittest.mock import patch
from mock import MagicMock
from pytest_mock import MockerFixture
from scipy.integrate import quad
from RUFAS.routines.animal.life_cycle.lactation_curve import LactationCurve

lact = LactationCurve()


def test_get_y_values_wood_curve(): 
  """Unit test for function get_y_values_wood_curve in file routines/animal/life_cycle/lactation_curve.py"""

  #Arrange
  expected_y_value = 2 * np.power(1, 3) * np.exp (-1 * 4 * 1)

  #Act 
  actual_y_value = lact.get_y_values_wood_curve(1, 2, 3, 4)

  #Assert
  assert actual_y_value == expected_y_value


def test_calc_integral_wood_curve(): 
  """Unit test for function calc_integral_wood_curve in file routines/animal/life_cycle/lactation_curve.py"""

  #Arrange 
  expected_calc_integral, _ = quad(lact.get_y_values_wood_curve, 1, 305, args=(1, 2, 3))

  #Act 
  actual_calc_integral = lact.calc_integral_wood_curve(1, 2, 3)
  #Assert
  assert actual_calc_integral == expected_calc_integral 


def test_get_wood_parameters_305d(mocker:MockerFixture): 
  """Unit test for function test_get_wood_parameteres in file routines/animal/life_cycle/lactation_curve.py when MY_305 is None"""

  #Arrange 
  #mock t and animalBase.get_t_values()
  #mock adjustment_dict and im.get_data
  mocker.patch("RUFAS.routines.animal.ration.animal_requirements.AnimalRequirements.set_requirements",return_value=None,)
    

  #Act 
  actual_wood_parameters = AnimalBase.get_wood_parameters("1", "2016", "July", "New York", "2x/d")

  #Assert 


def test_set_lactation_curve_parameters(cow_fixture: AnimalBase): 
  """Unit test for function set_lactation_curve_parameters in file routines/animal/life_cycle/lactation_curve.py"""
    
  # Act
  cow_fixture.set_lactation_curve_parameters() 
  AnimalBase.set_lactation_curve_parameters()
    
  #Assert 
  AnimalBase.lactation_parameters[0] 