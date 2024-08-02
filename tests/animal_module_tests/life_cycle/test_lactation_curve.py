import pytest
from pytest_mock import MockerFixture
from RUFAS.routines.animal.life_cycle.lactation_curve import LactationCurve
from typing import Any


@pytest.fixture
def lactation_curve(mocker: MockerFixture) -> LactationCurve:
    mocker.patch.object(LactationCurve, "__init__", return_value=None)
    return LactationCurve()


@pytest.fixture
def animal_inputs() -> dict[str, Any]:
    return {
        "herd_information": {
            "cow_num": 100,
            "parity_percentages": {"1": 38.6, "2": 28.1, "3": 33.3},
            "annual_milk_yield": 10_000_000,
        },
        "management_decisions": {"cow_times_milked_per_day": 2.7},
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
            "parameter_l_std_dev": 0.28,
            "parameter_m_std_dev": 0.0046,
            "parameter_n_std_dev": 3.77e-5,
        },
        "milking_cow_percentage": 0.8356,
    }


def test_init() -> None:
    """Test init routine of the LactationCurve module."""
    pass


def test_get_year_adjustments() -> None:
    """Test that year adjustments are retrieved appropriately."""
    pass


def test_get_region_adjustments() -> None:
    """Test that the region adjustments are retrieved appropriately."""
    pass


def test_get_milking_frequency_adjustments() -> None:
    """Test that the milking frequency adjustments are retrieved appropriately."""
    pass


def test_calculate_adjusted_wood_parameters() -> None:
    """Test that the Wood's parameters are adjusted correctly."""
    pass


def test_get_milk_yield_values_wood_curve() -> None:
    """Test that milk yield on a given day is estimated correctly."""
    pass


def test_calc_305_day_milk_yield() -> None:
    """Test that 305 day milk yields are estimated correctly."""
    pass


def test_get_wood_parameters() -> None:
    """Test that Wood's parameters are retrieved correctly from LactationCurve."""
    pass


def test_adjust_lactation_curve_to_milk_yield() -> None:
    """Test that Wood's parameters are correctly adjusted based on a farm's total milk yield."""
    pass


def test_estimate_305_day_milk_yield_by_parity() -> None:
    """Test that the 305 day milk yields are correctly predicted for each parity based on a farm's total milk yield."""
    pass


@pytest.mark.parametrize(
    "l_param,milk_yield,expected",
    [
        (19.2, 11331.4772561, 19.20),
        (20.1, 11868.5420636, 20.11),
        (16.4, 12393.8032489, 21.0),
        (19.5, 10033.0788205, 17.0),
        (23.0, 5901.8110709, 13.0),
        (12.0, 14754.5276773, 21.99),
    ]
)
def test_fit_wood_l_param_to_milk_yield(
    lactation_curve: LactationCurve, l_param: float, milk_yield: float, expected: float
) -> None:
    """Test that Wood's l parameter is correctly fitted to a 305 day milk yield."""
    actual = lactation_curve._fit_wood_l_param_to_milk_yield(l_param, 0.247, 0.003376, milk_yield)

    assert pytest.approx(actual) == expected
