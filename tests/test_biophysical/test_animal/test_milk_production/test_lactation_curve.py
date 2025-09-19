from datetime import date
from typing import Any

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility


@pytest.fixture
def animal_inputs() -> dict[str, Any]:
    return {
        "herd_information": {
            "cow_num": 100,
            "parity_fractions": {"1": 34.6, "2": 27.2, "3": 37.7, "4": 0.1, "5": 0.1},
            "milking_cow_fraction": 0.8356,
            "annual_milk_yield": 10_000_000,
        },
        "animal_config": {"management_decisions": {"cow_times_milked_per_day": 2.7}},
    }


@pytest.fixture
def lactation_inputs() -> dict[str, Any]:
    return {
        "adjustments": {
            "parity": {
                "1": {"l": -4.18, "m": -0.37, "n": -9.31},
                "2": {"l": 2.16, "m": -1.20, "n": 2.66},
                "3": {"l": 2.02, "m": 1.57, "n": 6.65},
            },
            "year": {
                "2006": {"l": -0.37, "m": 0.72, "n": 0.83},
                "2007": {"l": -0.59, "m": 1.00, "n": 1.23},
                "2008": {"l": -0.31, "m": 0.47, "n": 0.98},
                "2009": {"l": -0.24, "m": 0.24, "n": 0.60},
                "2010": {"l": -0.11, "m": -0.14, "n": 0.31},
                "2011": {"l": 0.10, "m": -0.58, "n": -0.56},
                "2012": {"l": 0.33, "m": -0.71, "n": -0.83},
                "2013": {"l": 0.27, "m": -0.51, "n": -0.73},
                "2014": {"l": 0.12, "m": 0.069, "n": -0.37},
                "2015": {"l": 0.28, "m": -0.12, "n": -0.68},
                "2016": {"l": 0.52, "m": -0.44, "n": -0.78},
            },
            "month": {
                "1": {"l": -0.46, "m": 1.81, "n": 3.13},
                "2": {"l": 0.18, "m": 0.76, "n": 2.43},
                "3": {"l": 1.05, "m": -0.77, "n": 1.04},
                "4": {"l": 1.58, "m": -2.03, "n": -0.56},
                "5": {"l": 1.49, "m": -2.47, "n": -1.95},
                "6": {"l": 0.74, "m": -2.01, "n": -2.75},
                "7": {"l": -0.41, "m": -0.81, "n": -2.68},
                "8": {"l": -0.96, "m": 0.11, "n": -2.06},
                "9": {"l": -1.08, "m": 0.78, "n": -1.08},
                "10": {"l": -0.85, "m": 1.20, "n": 0.27},
                "11": {"l": -0.63, "m": 1.45, "n": 1.51},
                "12": {"l": -0.65, "m": 1.98, "n": 2.70},
            },
            "region": {
                "Appalachian": {"l": -0.22, "m": -0.042, "n": -0.89},
                "Corn Belt": {"l": 0.55, "m": -0.58, "n": -1.12},
                "Delta": {"l": -2.56, "m": 0.59, "n": 1.47},
                "Lake": {"l": 0.61, "m": -0.40, "n": -0.64},
                "Mountain": {"l": -0.96, "m": 3.13, "n": 1.50},
                "Northeast": {"l": 1.04, "m": -1.99, "n": -1.13},
                "Northern Plains": {"l": -0.26, "m": 0.19, "n": -0.79},
                "New York": {"l": 0.67, "m": -1.21, "n": -0.45},
                "Pennsylvania": {"l": 1.15, "m": -0.96, "n": 0.06},
                "Southeast": {"l": -2.00, "m": 2.59, "n": 2.60},
                "Southern Plains": {"l": -0.51, "m": -1.02, "n": -0.93},
                "West Coast": {"l": 1.09, "m": 0.53, "n": 0.52},
                "Wisconsin": {"l": 1.4, "m": -0.83, "n": -0.2},
                "None": {"l": 0.0, "m": 0.0, "n": 0.0},
            },
            "milking_frequency": {
                "twice_daily": {"l": -0.74, "m": 0.090, "n": 0.15},
                "thrice_daily": {"l": 0.74, "m": -0.090, "n": -0.15},
            },
        },
        "state_to_region_mapping": {
            "1": "Southeast",
            "2": "None",
            "3": "None",
            "4": "Mountain",
            "5": "Delta",
            "6": "West Coast",
            "7": "None",
            "8": "Mountain",
            "9": "Northeast",
            "10": "Northeast",
            "11": "None",
            "12": "Southeast",
            "13": "Southeast",
            "14": "None",
            "15": "None",
            "16": "Mountain",
            "17": "Corn Belt",
            "18": "Corn Belt",
            "19": "Corn Belt",
            "20": "Northern Plains",
            "21": "Appalachian",
            "22": "Delta",
            "23": "Northeast",
            "24": "Northeast",
            "25": "Northeast",
            "26": "Lake",
            "27": "Lake",
            "28": "Delta",
            "29": "Corn Belt",
            "30": "Mountain",
            "31": "Northern Plains",
            "32": "Mountain",
            "33": "Northeast",
            "34": "Northeast",
            "35": "Mountain",
            "36": "New York",
            "37": "Appalachian",
            "38": "Northern Plains",
            "39": "Corn Belt",
            "40": "Southern Plains",
            "41": "West Coast",
            "42": "Pennsylvania",
            "43": "None",
            "44": "Northeast",
            "45": "Southeast",
            "46": "Northern Plains",
            "47": "Appalachian",
            "48": "Southern Plains",
            "49": "Mountain",
            "50": "Northeast",
            "51": "Appalachian",
            "52": "None",
            "53": "West Coast",
            "54": "Appalachian",
            "55": "Wisconsin",
            "56": "Mountain",
        },
        "parity_milk_yield_adjustments": {
            "parity_2_305_day_milk_yield_adjustment": 1632,
            "parity_3_305_day_milk_yield_adjustment": 2196,
        },
        "parameter_mean_values": {"parameter_l_mean": 19.9, "parameter_m_mean": 0.247, "parameter_n_mean": 0.003376},
        "parameter_standard_deviations": {
            "1": {"parameter_l_std_dev": 0.28, "parameter_m_std_dev": 0.0046, "parameter_n_std_dev": 3.77e-5},
            "2": {"parameter_l_std_dev": 0.54, "parameter_m_std_dev": 0.0064, "parameter_n_std_dev": 5.82e-5},
            "3": {"parameter_l_std_dev": 0.51, "parameter_m_std_dev": 0.0060, "parameter_n_std_dev": 5.54e-5},
        },
    }


@pytest.mark.parametrize("annual_milk_yield,expect_fitting", [(10_000_000, True), (None, False)])
def test_set_lactation_curve(
    mocker: MockerFixture,
    animal_inputs: dict[str, Any],
    lactation_inputs: dict[str, Any],
    annual_milk_yield: float,
    expect_fitting: bool,
) -> None:
    """Test init routine of the LactationCurve module."""
    mock_time = mocker.MagicMock()
    animal_inputs["herd_information"]["annual_milk_yield"] = annual_milk_yield
    im = InputManager()
    get_data = mocker.patch.object(im, "get_data", side_effect=[lactation_inputs, 55025, animal_inputs])
    om = OutputManager()
    add_log = mocker.patch.object(om, "add_log")
    add_var = mocker.patch.object(om, "add_variable")
    year_adjustments = mocker.patch.object(LactationCurve, "_get_year_adjustments", return_value=[0.0, 0.0, 0.0])
    region_adjustments = mocker.patch.object(LactationCurve, "_get_region_adjustments", return_value=[0.0, 0.0, 0.0])
    milking_freq = mocker.patch.object(
        LactationCurve, "_get_milking_frequency_adjustments", return_value=[0.0, 0.0, 0.0]
    )
    adjust_wood_params = mocker.patch.object(
        LactationCurve,
        "_calculate_adjusted_wood_parameters",
        side_effect=[
            {"l": 17.0, "m": 0.240, "n": 0.003376},
            {"l": 21.0, "m": 0.247, "n": 0.003376},
            {"l": 20.0, "m": 0.245, "n": 0.003376},
        ],
    )
    adjust_lactation_curve = mocker.patch.object(LactationCurve, "_adjust_lactation_curve_to_milk_yield")

    LactationCurve.set_lactation_parameters(mock_time)

    assert get_data.call_count == 3
    year_adjustments.assert_called_once()
    region_adjustments.assert_called_once()
    milking_freq.assert_called_once()
    assert adjust_wood_params.call_count == 3
    assert LactationCurve._parity_to_parameter_mapping == {
        1: {"l": 17.0, "m": 0.240, "n": 0.003376},
        2: {"l": 21.0, "m": 0.247, "n": 0.003376},
        3: {"l": 20.0, "m": 0.245, "n": 0.003376},
    }
    assert LactationCurve._parity_to_std_dev_mapping == {
        1: {"parameter_l_std_dev": 0.28, "parameter_m_std_dev": 0.0046, "parameter_n_std_dev": 3.77e-5},
        2: {"parameter_l_std_dev": 0.54, "parameter_m_std_dev": 0.0064, "parameter_n_std_dev": 5.82e-5},
        3: {"parameter_l_std_dev": 0.51, "parameter_m_std_dev": 0.0060, "parameter_n_std_dev": 5.54e-5},
    }
    add_log.assert_called_once()
    if expect_fitting:
        adjust_lactation_curve.assert_called_once()
    else:
        adjust_lactation_curve.assert_not_called()
    assert add_var.call_count == 9


@pytest.mark.parametrize(
    "year,bounded,expected",
    [
        (2004, False, {"l": -0.37, "m": 0.72, "n": 0.83}),
        (2006, True, {"l": -0.37, "m": 0.72, "n": 0.83}),
        (2008, True, {"l": -0.31, "m": 0.47, "n": 0.98}),
        (2011, True, {"l": 0.10, "m": -0.58, "n": -0.56}),
        (2016, True, {"l": 0.52, "m": -0.44, "n": -0.78}),
        (2020, False, {"l": 0.52, "m": -0.44, "n": -0.78}),
    ],
)
def test_get_year_adjustments(
    mocker: MockerFixture,
    lactation_inputs: dict[str, Any],
    expected: dict[str, float],
    year: int,
    bounded: bool,
) -> None:
    """Test that year adjustments are retrieved appropriately."""
    mock_time = mocker.MagicMock()
    mock_time.end_date = date(year, 6, 1)
    year_adjustments = lactation_inputs["adjustments"]["year"]
    LactationCurve._om = mocker.MagicMock()
    add_warning = mocker.patch.object(LactationCurve._om, "add_warning")

    actual = LactationCurve._get_year_adjustments(year_adjustments, mock_time)

    if not bounded:
        add_warning.assert_called_once()
    assert actual == expected


@pytest.mark.parametrize(
    "fips_code,expected",
    [
        (1000, {"l": -2.00, "m": 2.59, "n": 2.60}),
        (42000, {"l": 1.15, "m": -0.96, "n": 0.06}),
        (12000, {"l": -2.00, "m": 2.59, "n": 2.60}),
        (52000, {"l": 0.0, "m": 0.0, "n": 0.0}),
        (26000, {"l": 0.61, "m": -0.40, "n": -0.64}),
        (35000, {"l": -0.96, "m": 3.13, "n": 1.50}),
    ],
)
def test_get_region_adjustments(lactation_inputs: dict[str, Any], fips_code: int, expected: dict[str, float]) -> None:
    """Test that the region adjustments are retrieved appropriately."""
    all_region_adjustments = lactation_inputs["adjustments"]["region"]
    region_mapping = lactation_inputs["state_to_region_mapping"]

    actual = LactationCurve._get_region_adjustments(all_region_adjustments, region_mapping, fips_code)

    assert actual == expected


@pytest.mark.parametrize(
    "milking_frequency,expected",
    [
        (2.5, {"l": 0.74, "m": -0.090, "n": -0.15}),
        (1.8, {"l": -0.74, "m": 0.090, "n": 0.15}),
        (3.6, {"l": 0.74, "m": -0.090, "n": -0.15}),
        (2.8, {"l": 0.74, "m": -0.090, "n": -0.15}),
        (2.1, {"l": -0.74, "m": 0.090, "n": 0.15}),
    ],
)
def test_get_milking_frequency_adjustments(
    lactation_inputs: dict[str, Any], milking_frequency: float, expected: dict[str, float]
) -> None:
    """Test that the milking frequency adjustments are retrieved appropriately."""
    milking_frequency_adjustments = lactation_inputs["adjustments"]["milking_frequency"]

    actual = LactationCurve._get_milking_frequency_adjustments(milking_frequency_adjustments, milking_frequency)

    assert actual == expected


@pytest.mark.parametrize(
    "l_param,m_param,n_param,adjustments,expected",
    [
        (19.2, 0.247, 0.003376, [{"l": 0, "m": 0, "n": 0}], {"l": 19.2, "m": 0.247, "n": 0.003376}),
        (19.2, 0.247, 0.003376, [{"l": 1, "m": 1, "n": 1}], {"l": 20.2, "m": 0.257, "n": 0.003476}),
        (19.2, 0.247, 0.003376, [{"l": -1, "m": -1, "n": -1}], {"l": 18.2, "m": 0.237, "n": 0.003276}),
        (
            19.2,
            0.247,
            0.003376,
            [{"l": 1, "m": 1, "n": 1}, {"l": 1, "m": 1, "n": 1}],
            {"l": 21.2, "m": 0.267, "n": 0.003576},
        ),
        (
            19.2,
            0.247,
            0.003376,
            [{"l": 1, "m": 1, "n": 1}, {"l": 1, "m": 1, "n": 1}, {"l": 1, "m": 1, "n": 1}, {"l": -1, "m": -1, "n": -1}],
            {"l": 21.2, "m": 0.267, "n": 0.003576},
        ),
        (19.2, 24.7, 3.376, [{"l": -19.2, "m": -2470, "n": -33760}], {"l": 0.0, "m": 0.0, "n": 0.0}),
    ],
)
def test_calculate_adjusted_wood_parameters(
    l_param: float,
    m_param: float,
    n_param: float,
    adjustments: list[dict[str, float]],
    expected: dict[str, float],
) -> None:
    """Test that the Wood's parameters are adjusted correctly."""
    actual = LactationCurve._calculate_adjusted_wood_parameters(l_param, m_param, n_param, adjustments)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "parity,l_expect,m_expect,n_expect,l_std_dev_expected,m_std_dev_expected,n_std_dev_expected",
    [
        (1, 18.1, 0.228, 0.003321, 0.28, 0.0046, 3.77e-5),
        (2, 22.1, 0.247, 0.003376, 0.54, 0.0064, 5.82e-5),
        (3, 22.0, 0.231, 0.003351, 0.51, 0.0060, 5.54e-5),
    ],
)
def test_get_wood_parameters(
    mocker: MockerFixture,
    parity: int,
    l_expect: float,
    m_expect: float,
    n_expect: float,
    l_std_dev_expected: float,
    m_std_dev_expected: float,
    n_std_dev_expected: float,
) -> None:
    """Test that Wood's parameters are retrieved correctly from LactationCurve."""
    gen_rand = mocker.patch.object(Utility, "generate_random_number", side_effect=[20.22, 0.311, 0.003122])
    LactationCurve._parity_to_parameter_mapping = {
        1: {"l": 18.1, "m": 0.228, "n": 0.003321},
        2: {"l": 22.1, "m": 0.247, "n": 0.003376},
        3: {"l": 22.0, "m": 0.231, "n": 0.003351},
    }
    parity_1_std_dev = {"parameter_l_std_dev": 0.28, "parameter_m_std_dev": 0.0046, "parameter_n_std_dev": 3.77e-5}
    parity_2_std_dev = {"parameter_l_std_dev": 0.54, "parameter_m_std_dev": 0.0064, "parameter_n_std_dev": 5.82e-5}
    parity_3_std_dev = {"parameter_l_std_dev": 0.51, "parameter_m_std_dev": 0.0060, "parameter_n_std_dev": 5.54e-5}
    LactationCurve._parity_to_std_dev_mapping = {1: parity_1_std_dev, 2: parity_2_std_dev, 3: parity_3_std_dev}

    actual = LactationCurve.get_wood_parameters(parity)

    assert actual["l"] == 20.22
    assert actual["m"] == 0.311
    assert actual["n"] == 0.003122
    gen_rand.assert_has_calls(
        [
            mocker.call(l_expect, l_std_dev_expected),
            mocker.call(m_expect, m_std_dev_expected),
            mocker.call(n_expect, n_std_dev_expected),
        ]
    )


def test_adjust_lactation_curve_to_milk_yield(
    mocker: MockerFixture, animal_inputs: dict[str, Any], lactation_inputs: dict[str, Any]
) -> None:
    """Test that Wood's parameters are correctly adjusted based on a farm's total milk yield."""
    LactationCurve._parity_to_parameter_mapping = {
        1: {"l": 17.0, "m": 0.247, "n": 0.003376},
        2: {"l": 17.0, "m": 0.247, "n": 0.003376},
        3: {"l": 17.0, "m": 0.247, "n": 0.003376},
    }
    estimate_305d_yield = mocker.patch.object(
        LactationCurve,
        "_estimate_305_day_milk_yield_by_parity",
        return_value={"parity_1": 10_000.0, "parity_2": 11_000.0, "parity_3": 10_500.0},
    )
    fit_l_param = mocker.patch.object(LactationCurve, "_fit_wood_l_param_to_milk_yield", side_effect=[19.2, 20.0, 19.5])

    LactationCurve._adjust_lactation_curve_to_milk_yield(animal_inputs, lactation_inputs)

    estimate_305d_yield.assert_called_once()
    assert fit_l_param.call_count == 3
    assert LactationCurve._parity_to_parameter_mapping[1]["l"] == 19.2
    assert LactationCurve._parity_to_parameter_mapping[2]["l"] == 20.0
    assert LactationCurve._parity_to_parameter_mapping[3]["l"] == 19.5


@pytest.mark.parametrize(
    "annual_yield,milking_cows,p1_frac,p2_frac,p3_frac,p2_adjust,p3_adjust,expected_p1,expected_p2,expected_p3,error,"
    "warning",
    [
        (1_196_721.31, 100, 0.3, 0.4, 0.3, 1.18, 1.25, 8718.395, 10287.707, 10897.994, False, False),
        (15_000_000.0, 1500, 0.28, 0.36, 0.36, 1.18, 1.25, 7236.027, 8538.512, 9045.034, False, False),
        (15_000_000.0, 1500, 0.28, 0.36, 0.355, 1.18, 1.25, 7275.403, 8584.975, 9094.254, False, True),
        (15_000_000.0, 1500, 0.2, 0.3, 0.3, 1.18, 1.25, 7369.856, 8696.430, 9212.320, True, False),
    ],
)
def test_estimate_305_day_milk_yield_by_parity(
    mocker: MockerFixture,
    annual_yield: float,
    milking_cows: int,
    p1_frac: float,
    p2_frac: float,
    p3_frac: float,
    p2_adjust: float,
    p3_adjust: float,
    expected_p1: float,
    expected_p2: float,
    expected_p3: float,
    error: bool,
    warning: bool,
) -> None:
    """Test that the 305 day milk yields are correctly predicted for each parity based on a farm's total milk yield."""
    om = OutputManager()
    add_error = mocker.patch.object(om, "add_error")
    add_warning = mocker.patch.object(om, "add_warning")
    LactationCurve._om = om

    actual = LactationCurve._estimate_305_day_milk_yield_by_parity(
        annual_yield, milking_cows, p1_frac, p2_frac, p3_frac, p2_adjust, p3_adjust
    )

    assert actual.keys() == {"parity_1", "parity_2", "parity_3"}
    assert pytest.approx(actual["parity_1"]) == expected_p1
    assert pytest.approx(actual["parity_2"]) == expected_p2
    assert pytest.approx(actual["parity_3"]) == expected_p3
    if error:
        add_error.assert_called_once()
    else:
        add_error.assert_not_called()
    if warning:
        add_warning.assert_called_once()
    else:
        add_warning.assert_not_called()


@pytest.mark.parametrize(
    "l_param,milk_yield,expected",
    [
        (19.2, 11331.4772561, 19.20),
        (20.1, 11868.5420636, 20.11),
        (16.4, 12393.8032489, 21.0),
        (19.5, 10033.0788205, 17.0),
        (23.0, 900.0, 3.0),
        (8.0, 18000.0, 28.00),
    ],
)
def test_fit_wood_l_param_to_milk_yield(l_param: float, milk_yield: float, expected: float) -> None:
    """Test that Wood's l parameter is correctly fitted to a 305 day milk yield."""
    actual = LactationCurve._fit_wood_l_param_to_milk_yield(l_param, 0.247, 0.003376, milk_yield)

    assert pytest.approx(actual) == expected
