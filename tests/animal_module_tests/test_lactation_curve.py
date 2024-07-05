import pytest
import numpy as np
from typing import Any, Dict
from unittest.mock import patch
from mock import MagicMock
from pytest_mock import MockerFixture
from scipy.integrate import quad
from RUFAS.routines.animal.life_cycle.lactation_curve import LactationCurve
from RUFAS.input_manager import InputManager


@pytest.fixture
def lactation_curve_fixture(mocker: MockerFixture) -> LactationCurve:
    mocker.patch("RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.__init__", return_value=None)
    lact = LactationCurve()
    lact.adjustment_dict = {
        "parity": [
            {"parity": "1", "adjustments": [-4.18, -0.37, -9.31]},
            {"parity": "2", "adjustments": [2.16, -1.20, 2.66]},
            {"parity": "3", "adjustments": [2.02, 1.57, 6.65]},
        ],
        "year": [
            {"year": "2006", "adjustments": [-0.37, 0.72, 0.83]},
            {"year": "2007", "adjustments": [-0.59, 1.00, 1.23]},
            {"year": "2008", "adjustments": [-0.31, 0.47, 0.98]},
            {"year": "2009", "adjustments": [-0.24, 0.24, 0.60]},
            {"year": "2010", "adjustments": [-0.11, -0.14, 0.31]},
            {"year": "2011", "adjustments": [0.10, -0.58, -0.56]},
            {"year": "2012", "adjustments": [0.33, -0.71, -0.83]},
            {"year": "2013", "adjustments": [0.27, -0.51, -0.73]},
            {"year": "2014", "adjustments": [0.12, 0.069, -0.37]},
            {"year": "2015", "adjustments": [0.28, -0.12, -0.68]},
            {"year": "2016", "adjustments": [0.52, -0.44, -0.78]},
        ],
        "month": [
            {"month": "January", "adjustments": [-0.46, 1.81, 3.13]},
            {"month": "February", "adjustments": [0.18, 0.76, 2.43]},
            {"month": "March", "adjustments": [1.05, -0.77, 1.04]},
            {"month": "April", "adjustments": [1.58, -2.03, -0.56]},
            {"month": "May", "adjustments": [1.49, -2.47, -1.95]},
            {"month": "June", "adjustments": [0.74, -2.01, -2.75]},
            {"month": "July", "adjustments": [-0.41, -0.81, -2.68]},
            {"month": "August", "adjustments": [-0.96, 0.11, -2.06]},
            {"month": "September", "adjustments": [-1.08, 0.78, -1.08]},
            {"month": "October", "adjustments": [-0.85, 1.20, 0.27]},
            {"month": "November", "adjustments": [-0.63, 1.45, 1.51]},
            {"month": "December", "adjustments": [-0.65, 1.98, 2.70]},
        ],
        "region": [
            {"region": "Appalachian", "adjustments": [-0.22, -0.042, -0.89]},
            {"region": "Corn Belt", "adjustments": [0.55, -0.58, -1.12]},
            {"region": "Delta", "adjustments": [-2.56, 0.59, 1.47]},
            {"region": "Lake", "adjustments": [0.61, -0.40, -0.64]},
            {"region": "Mountain", "adjustments": [-0.96, 3.13, 1.50]},
            {"region": "Northeast", "adjustments": [1.04, -1.99, -1.13]},
            {"region": "Northern Plains", "adjustments": [-0.26, 0.19, -0.79]},
            {"region": "New York", "adjustments": [0.67, -1.21, -0.45]},
            {"region": "Pennsylvania", "adjustments": [1.15, -0.96, 0.06]},
            {"region": "Southeast", "adjustments": [-2.00, 2.59, 2.60]},
            {"region": "Southern Plains", "adjustments": [-0.51, -1.02, -0.93]},
            {"region": "West Coast", "adjustments": [1.09, 0.53, 0.52]},
            {"region": "Wisconsin", "adjustments": [1.4, -0.83, -0.2]},
        ],
        "milking_frequency": [
            {"milking_frequency": "2x/d", "adjustments": [-0.74, 0.090, 0.15]},
            {"milking_frequency": "3x/d", "adjustments": [0.74, -0.090, -0.15]},
        ],
    }
    """lact.region_dict = 
    lact.year = 
    lact.region 
    lact.annual_MY_lbs
    lact.parity_percentages
    lact.num_milking_cows
    lact.milking_freq
    lact.parity2_MilkYield305_adj
    lact.parity3_MilkYield305_adj
    lact.adjustment_dict"""
    return lact


# lact = LactationCurve()

"""'mock_input_manager = InputManager()
patch_im_getdata = mocker.patch.object(
    mock_input_manager,
    "get_data",
    return_value={
            "calves": [],
            "heiferIs": [],
            "heiferIIs": [],
            "heiferIIIs": [],
            "cows": [],
            "replacement": [],
    },
)"""


def test_get_y_values_wood_curve(lactation_curve_fixture: LactationCurve):
    """Unit test for function get_y_values_wood_curve in file routines/animal/life_cycle/lactation_curve.py"""

    # Arrange
    expected_y_value = 2 * np.power(1, 3) * np.exp(-1 * 4 * 1)

    # Act
    actual_y_value = lactation_curve_fixture.get_y_values_wood_curve(1, 2, 3, 4)

    # Assert
    assert actual_y_value == expected_y_value


def test_calc_integral_wood_curve(lactation_curve_fixture: LactationCurve):
    """Unit test for function calc_integral_wood_curve in file routines/animal/life_cycle/lactation_curve.py"""

    # Arrange
    expected_calc_integral, _ = quad(lactation_curve_fixture.get_y_values_wood_curve, 1, 305, args=(1, 2, 3))

    # Act
    actual_calc_integral = lactation_curve_fixture.calc_integral_wood_curve(1, 2, 3)
    # Assert
    assert actual_calc_integral == expected_calc_integral


def test_get_wood_parameters_305dNone(mocker: MockerFixture, lactation_curve_fixture: LactationCurve):
    """Unit test for function get_wood_parameters in file routines/animal/life_cycle/lactation_curve.py when MY_305 is None"""

    # Arrange
    # mock t and animalBase.get_t_values()
    # mock adjustment_dict and im.get_data
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.calc_integral_wood_curve",
        return_value=305.00,
    )
    # mock_lact_curve = LactationCurve()
    # param_a_mock = MagicMock()
    # param_b_mock = MagicMock()
    # param_c_mock = MagicMock()
    mock_lactation_group = MagicMock()
    mock_year = MagicMock()
    mock_month = MagicMock()
    mock_region = MagicMock()
    mock_milking_freq = MagicMock()
    mock_MY_305d = 305.00
    # mock_lact_curve.calc_integral_wood_curve = MagicMock(return_value=305.00)

    # Act
    # actual_param_a, actual_param_b, actual_param_c,
    _, _, _, actual_305d = lactation_curve_fixture.get_wood_parameters(
        mock_lactation_group, mock_year, mock_month, mock_region, mock_milking_freq, None
    )

    # Assert
    # assert actual_param_a == param_a_mock
    # assert actual_param_b == param_b_mock
    # assert actual_param_c == param_c_mock
    # mock_lact_curve.calc_integral_wood_curve.assert_called_once()
    assert actual_305d == mock_MY_305d


def test_get_wood_parameters_305d(mocker: MockerFixture, lactation_curve_fixture: LactationCurve):
    """Unit test for function get_wood_parameters in file routines/animal/life_cycle/lactation_curve.py when MY_305 is not None"""

    # Arrange
    # mock t and animalBase.get_t_values()
    # mock adjustment_dict and im.get_data
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.calc_integral_wood_curve",
        return_value=305.00,
    )
    # lact_curve_mock = LactationCurve()
    # param_a_mock = MagicMock()
    # param_b_mock = MagicMock()
    # param_c_mock = MagicMock()
    lactation_group_mock = MagicMock()
    year_mock = MagicMock()
    month_mock = MagicMock()
    region_mock = MagicMock()
    milking_freq_mock = MagicMock()
    MY_305d_mock = 305.00

    # Act
    # actual_param_a, actual_param_b, actual_param_c,
    _, _, _, actual_305d = lactation_curve_fixture.get_wood_parameters(
        lactation_group_mock, year_mock, month_mock, region_mock, milking_freq_mock, "50000"
    )

    # Assert
    assert actual_305d == MY_305d_mock


def test_get_wood_param_adjust_params(mocker: MockerFixture, lactation_curve_fixture: LactationCurve):
    """Unit test for adjustments to parameters l,m,n in function get_wood_parameters in file routines/animal/life_cycle/lactation_curve.py"""

    # Arrange
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.calc_integral_wood_curve",
        return_value=305.00,
    )
    lactation_group = "1"

    # Act
    actual_param_a, actual_param_b, actual_param_c, _ = lactation_curve_fixture.get_wood_parameters(
        lactation_group, year=None, month=None, region=None, milking_frequency=None, MY_305d=None
    )

    # Assert
    assert actual_param_a == 19.9 - 4.18
    assert actual_param_b == 24.7 * 1e-2 - 0.37 * 1e-2
    assert actual_param_c == 33.76 * 1e-4 - 9.31 * 1e-4


def test_calc_parities_annual_MY(mocker: MockerFixture, lactation_curve_fixture: LactationCurve):
    """Unit test for function calc_parities in file routines/animal/life_cycle/lactation_curve.py when annual milk yield is not None"""

    # Arrange
    lactation_curve_fixture.annual_MY_lbs = mocker.MagicMock()
    lactation_curve_fixture.parity_percentages = mocker.MagicMock()
    lactation_curve_fixture.num_milking_cows = mocker.MagicMock()
    lactation_curve_fixture.parity2_MilkYield305_adj = mocker.MagicMock()
    lactation_curve_fixture.parity3_MilkYield305_adj = mocker.MagicMock()

    # Act
    actual_parity1_305, actual_parity2_305, actual_parity3_305 = lactation_curve_fixture.calc_parities()

    # Assert
    assert actual_parity1_305 != None
    assert actual_parity2_305 != None
    assert actual_parity3_305 != None


def test_calc_parities_annual_MY_None(lactation_curve_fixture: LactationCurve):
    """Unit test for function calc_parities in file routines/animal/life_cycle/lactation_curve.py when annual milk yield is None"""

    # Arrange
    lactation_curve_fixture.annual_MY_lbs = None

    # Act
    actual_parity1_305, actual_parity2_305, actual_parity3_305 = lactation_curve_fixture.calc_parities()

    # Assert
    assert actual_parity1_305 == None
    assert actual_parity2_305 == None
    assert actual_parity3_305 == None


def test_set_lactation_curve_parameters(mocker: MockerFixture, lactation_curve_fixture: LactationCurve):
    # Arrange
    lactation_curve_fixture.year = mocker.MagicMock
    lactation_curve_fixture.region = mocker.MagicMock
    lactation_curve_fixture.milking_freq = mocker.MagicMock
    lactation_curve_fixture.annual_MY_lbs = mocker.MagicMock
    patch_for_get_wood_parameters = mocker.patch(
        "RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.get_wood_parameters", return_value=[1, 2, 3]
    )
    patch_for_calc_parities = mocker.patch(
        "RUFAS.routines.animal.life_cycle.lactation_curve.LactationCurve.calc_parities", return_value=[1, 2, 3]
    )

    # Act
    lactation_curve_fixture.set_lactation_curve_parameters()

    # Assert
    patch_for_get_wood_parameters.assert_called_with(
        lactation_group="3",
        year=lactation_curve_fixture.year,
        region=lactation_curve_fixture.region,
        milking_frequency=lactation_curve_fixture.milking_freq,
        MY_305d=3,
    )
    patch_for_calc_parities.assert_called_once()
