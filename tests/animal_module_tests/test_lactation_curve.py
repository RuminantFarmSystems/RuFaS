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

    # Arrange
    expected_y_value = 2 * np.power(1, 3) * np.exp(-1 * 4 * 1)

    # Act
    actual_y_value = lact.get_y_values_wood_curve(1, 2, 3, 4)

    # Assert
    assert actual_y_value == expected_y_value


def test_calc_integral_wood_curve():
    """Unit test for function calc_integral_wood_curve in file routines/animal/life_cycle/lactation_curve.py"""

    # Arrange
    expected_calc_integral, _ = quad(lact.get_y_values_wood_curve, 1, 305, args=(1, 2, 3))

    # Act
    actual_calc_integral = lact.calc_integral_wood_curve(1, 2, 3)
    # Assert
    assert actual_calc_integral == expected_calc_integral


def test_get_wood_parameters_305dNone(mocker: MockerFixture):
    """Unit test for function test_get_wood_parameteres in file routines/animal/life_cycle/lactation_curve.py when MY_305 is None"""

    # Arrange
    # mock t and animalBase.get_t_values()
    # mock adjustment_dict and im.get_data
    mocker.patch(
        "RUFAS.routines.animal.ration.lactation_curve.LactationCurve.calc_integral_wood_curve",
        return_value=305.00,
    )
    mock_lact_curve = LactationCurve()
    #param_a_mock = MagicMock()
    #param_b_mock = MagicMock() 
    #param_c_mock = MagicMock()
    mock_lactation_group = MagicMock()
    mock_year= MagicMock() 
    mock_month = MagicMock() 
    mock_region = MagicMock() 
    mock_milking_freq = MagicMock() 
    mock_MY_305d = 305.00
    #mock_lact_curve.calc_integral_wood_curve = MagicMock(return_value=305.00)
    
    # Act
    #actual_param_a, actual_param_b, actual_param_c, 
    _, _, _, actual_305d = mock_lact_curve.get_wood_parameters(mock_lactation_group, mock_year, mock_month, mock_region, mock_milking_freq, None)

    # Assert
    #assert actual_param_a == param_a_mock 
    #assert actual_param_b == param_b_mock 
    #assert actual_param_c == param_c_mock 
    #mock_lact_curve.calc_integral_wood_curve.assert_called_once()
    assert actual_305d == mock_MY_305d

    
def test_get_wood_parameters_305d(mocker):
    """Unit test for function test_get_wood_parameteres in file routines/animal/life_cycle/lactation_curve.py when MY_305 is not None"""

    # Arrange
    # mock t and animalBase.get_t_values()
    # mock adjustment_dict and im.get_data
    mocker.patch(
        "RUFAS.routines.animal.ration.lactation_curve.LactationCurve.calc_integral_wood_curve",
        return_value=305.00,
    )
    lact_curve_mock = LactationCurve()
    #param_a_mock = MagicMock()
    #param_b_mock = MagicMock() 
    #param_c_mock = MagicMock()
    lactation_group_mock = MagicMock()
    year_mock = MagicMock() 
    month_mock = MagicMock() 
    region_mock = MagicMock() 
    milking_freq_mock = MagicMock() 
    MY_305d_mock = 305.00
    
    # Act
    #actual_param_a, actual_param_b, actual_param_c, 
    _, _, _, actual_305d = lact_curve_mock.get_wood_parameters(lactation_group_mock, year_mock, month_mock, region_mock, milking_freq_mock, "50000")

    # Assert
    #assert actual_param_a == param_a_mock 
    #assert actual_param_b == param_b_mock 
    #assert actual_param_c == param_c_mock 
    assert actual_305d == MY_305d_mock
    

  


# def test_set_lactation_curve_parameters(cow_fixture: AnimalBase):
#     """Unit test for function set_lactation_curve_parameters in file routines/animal/life_cycle/lactation_curve.py"""

#     # Act
#     cow_fixture.set_lactation_curve_parameters()
#     AnimalBase.set_lactation_curve_parameters()

#     # Assert
#     AnimalBase.lactation_parameters[0]
