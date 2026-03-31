import pytest

from RUFAS.units import MeasurementUnits


def test_units_member_values() -> None:
    """
    Test accuracy of the values for each of the MeasurementUnits members
    """

    assert MeasurementUnits.ANIMALS.value == "animals"
    assert MeasurementUnits.ARTIFICIAL_INSEMINATIONS.value == "AI"
    assert MeasurementUnits.BYTES.value == "bytes"
    assert MeasurementUnits.CALENDAR_YEAR.value == "calendar year"
    assert MeasurementUnits.CENTIMETERS.value == "cm"
    assert MeasurementUnits.CENTIMETERS_PER_MILLIMETER.value == "cm/mm"
    assert MeasurementUnits.CONCEPTIONS.value == "conception"
    assert MeasurementUnits.CONCEPTIONS_PER_SERVICE.value == "conceptions per service"
    assert MeasurementUnits.COWS.value == "cows"
    assert MeasurementUnits.CUBIC_METERS.value == "m^3"
    assert MeasurementUnits.CUBIC_METERS_PER_DAY.value == "m^3/day"
    assert MeasurementUnits.CUBIC_METERS_PER_KILOGRAM.value == "m^3/kg"
    assert MeasurementUnits.CUBIC_METERS_PER_LITER.value == "m^3/L"
    assert MeasurementUnits.CUBIC_METERS_PER_CUBIC_MILLIMETER.value == "m^3/mm^3"
    assert MeasurementUnits.CUBIC_MILLIMETERS_PER_CUBIC_METER.value == "mm^3/m^3"
    assert MeasurementUnits.DAYS.value == "day"
    assert MeasurementUnits.DAYS_PER_LEAP_YEAR.value == "day/leap year"
    assert MeasurementUnits.DAYS_PER_YEAR.value == "day/year"
    assert MeasurementUnits.DEGREES_CELSIUS.value == "°C"
    assert MeasurementUnits.DRY_KILOGRAMS.value == "dry kg"
    assert MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE.value == "dry kg/ha"
    assert MeasurementUnits.FRACTION.value == "fraction"
    assert MeasurementUnits.GRAMS.value == "g"
    assert MeasurementUnits.GRAMS_PER_DAY.value == "g/day"
    assert MeasurementUnits.GRAMS_PER_KILOGRAM.value == "g/kg"
    assert MeasurementUnits.GRAMS_PER_LITER.value == "g/L"
    assert MeasurementUnits.HECTARE.value == "ha"
    assert MeasurementUnits.HECTARES_PER_SQUARE_CENTIMETER.value == "ha/cm^2"
    assert MeasurementUnits.HECTARES_PER_SQUARE_METER.value == "ha/m^2"
    assert MeasurementUnits.HECTARES_PER_SQUARE_KILOMETER.value == "ha/km^2"
    assert MeasurementUnits.HECTARES_PER_SQUARE_MILLIMETER.value == "ha/mm^2"
    assert MeasurementUnits.HOURS.value == "hour"
    assert MeasurementUnits.JULIAN_DAY.value == "julian day"
    assert MeasurementUnits.INJECTIONS.value == "injection"
    assert MeasurementUnits.KILOMETERS_PER_METER.value == "km/m"
    assert MeasurementUnits.KILOGRAMS.value == "kg"
    assert MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER.value == "kg CO2 / kg DM"
    assert MeasurementUnits.KILOGRAMS_PER_ANIMAL.value == "kg/animal"
    assert MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ.value == "kg CO2-eq"
    assert MeasurementUnits.KILOGRAMS_PER_CUBIC_METER.value == "kg/m^3"
    assert MeasurementUnits.KILOGRAMS_PER_DAY.value == "kg/day"
    assert MeasurementUnits.KILOGRAMS_PER_GRAM.value == "kg/g"
    assert MeasurementUnits.KILOGRAMS_PER_HECTARE.value == "kg/ha"
    assert MeasurementUnits.KILOGRAMS_PER_LITER.value == "kg/L"
    assert MeasurementUnits.KILOGRAMS_PER_MEGAGRAM.value == "kg/Mg"
    assert MeasurementUnits.KILOGRAMS_PER_MILLIGRAM.value == "kg/mg"
    assert MeasurementUnits.KILOMETERS.value == "km"
    assert MeasurementUnits.LITERS.value == "L"
    assert MeasurementUnits.LITERS_PER_CUBIC_METER.value == "L/m^3"
    assert MeasurementUnits.MEGACALORIES.value == "Mcal"
    assert MeasurementUnits.MEGACALORIES_PER_KILOGRAM.value == "Mcal/kg"
    assert MeasurementUnits.MEGAGRAMS_PER_KILOGRAM.value == "Mg/kg"
    assert MeasurementUnits.MEGAJOULES.value == "MJ"
    assert MeasurementUnits.MEGAJOULES_PER_CUBIC_METER.value == "MJ/m^3"
    assert MeasurementUnits.MEGAJOULES_PER_SQUARE_METER.value == "MJ/m^2"
    assert MeasurementUnits.METERS.value == "m"
    assert MeasurementUnits.METERS_PER_KILOMETER.value == "m/km"
    assert MeasurementUnits.METERS_PER_MILLIMETER.value == "m/mm"
    assert MeasurementUnits.METRIC_TONS.value == "metric ton"
    assert MeasurementUnits.MILLIMETERS.value == "mm"
    assert MeasurementUnits.MILLIMETERS_PER_CENTIMETER.value == "mm/cm"
    assert MeasurementUnits.MILLIMETERS_PER_HECTARE.value == "mm/ha"
    assert MeasurementUnits.ORDINAL_DAY.value == "ordinal day"
    assert MeasurementUnits.PERCENT.value == "percent"
    assert MeasurementUnits.PERCENT_OF_DRY_MATTER.value == "percent of DM"
    assert MeasurementUnits.PREGNANCY_CHECKS.value == "preg check"
    assert MeasurementUnits.RADIANS_PER_HOUR.value == "rad/h"
    assert MeasurementUnits.SECONDS.value == "s"
    assert MeasurementUnits.SECONDS_PER_DAY.value == "s/day"
    assert MeasurementUnits.HOURS_PER_DAY.value == "h/day"
    assert MeasurementUnits.SIMULATION_DAY.value == "simulation day"
    assert MeasurementUnits.SIMULATION_YEAR.value == "simulation year"
    assert MeasurementUnits.SQUARE_CENTIMETERS_PER_HECTARE.value == "cm^2/ha"
    assert MeasurementUnits.SQUARE_METERS_PER_HECTARE.value == "m^2/ha"
    assert MeasurementUnits.SQUARE_KILOMETERS_PER_HECTARE.value == "km^2/ha"
    assert MeasurementUnits.SQUARE_MILLIMETERS_PER_HECTARE.value == "mm^2/ha"
    assert MeasurementUnits.UNITLESS.value == "unitless"
    assert MeasurementUnits.WET_KILOGRAMS_PER_HECTARE.value == "wet kg/ha"


def test_units_str_method() -> None:
    """
    Test the __str__ method for each of the MeasurementUnits members.
    """

    assert str(MeasurementUnits.ANIMALS) == "animals"
    assert str(MeasurementUnits.ARTIFICIAL_INSEMINATIONS) == "AI"
    assert str(MeasurementUnits.BYTES) == "bytes"
    assert str(MeasurementUnits.CALENDAR_YEAR) == "calendar year"
    assert str(MeasurementUnits.CENTIMETERS) == "cm"
    assert str(MeasurementUnits.CENTIMETERS_PER_MILLIMETER) == "cm/mm"
    assert str(MeasurementUnits.CONCEPTIONS) == "conception"
    assert str(MeasurementUnits.CONCEPTIONS_PER_SERVICE) == "conceptions per service"
    assert str(MeasurementUnits.COWS) == "cows"
    assert str(MeasurementUnits.CUBIC_METERS) == "m^3"
    assert str(MeasurementUnits.CUBIC_METERS_PER_DAY) == "m^3/day"
    assert str(MeasurementUnits.CUBIC_METERS_PER_KILOGRAM) == "m^3/kg"
    assert str(MeasurementUnits.CUBIC_METERS_PER_LITER) == "m^3/L"
    assert str(MeasurementUnits.CUBIC_METERS_PER_CUBIC_MILLIMETER) == "m^3/mm^3"
    assert str(MeasurementUnits.CUBIC_MILLIMETERS_PER_CUBIC_METER) == "mm^3/m^3"
    assert str(MeasurementUnits.DAYS) == "day"
    assert str(MeasurementUnits.DAYS_PER_LEAP_YEAR) == "day/leap year"
    assert str(MeasurementUnits.DAYS_PER_YEAR) == "day/year"
    assert str(MeasurementUnits.DEGREES_CELSIUS) == "°C"
    assert str(MeasurementUnits.DRY_KILOGRAMS) == "dry kg"
    assert str(MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE) == "dry kg/ha"
    assert str(MeasurementUnits.FRACTION) == "fraction"
    assert str(MeasurementUnits.GRAMS) == "g"
    assert str(MeasurementUnits.GRAMS_PER_DAY) == "g/day"
    assert str(MeasurementUnits.GRAMS_PER_KILOGRAM) == "g/kg"
    assert str(MeasurementUnits.GRAMS_PER_LITER) == "g/L"
    assert str(MeasurementUnits.HECTARE) == "ha"
    assert str(MeasurementUnits.HECTARES_PER_SQUARE_CENTIMETER) == "ha/cm^2"
    assert str(MeasurementUnits.HECTARES_PER_SQUARE_METER) == "ha/m^2"
    assert str(MeasurementUnits.HECTARES_PER_SQUARE_KILOMETER) == "ha/km^2"
    assert str(MeasurementUnits.HECTARES_PER_SQUARE_MILLIMETER) == "ha/mm^2"
    assert str(MeasurementUnits.HOURS) == "hour"
    assert str(MeasurementUnits.INJECTIONS) == "injection"
    assert str(MeasurementUnits.KILOMETERS_PER_METER) == "km/m"
    assert str(MeasurementUnits.KILOGRAMS) == "kg"
    assert str(MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER) == "kg CO2 / kg DM"
    assert str(MeasurementUnits.KILOGRAMS_PER_ANIMAL) == "kg/animal"
    assert str(MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ) == "kg CO2-eq"
    assert str(MeasurementUnits.KILOGRAMS_PER_CUBIC_METER) == "kg/m^3"
    assert str(MeasurementUnits.KILOGRAMS_PER_DAY) == "kg/day"
    assert str(MeasurementUnits.KILOGRAMS_PER_GRAM) == "kg/g"
    assert str(MeasurementUnits.KILOGRAMS_PER_HECTARE) == "kg/ha"
    assert str(MeasurementUnits.KILOGRAMS_PER_LITER) == "kg/L"
    assert str(MeasurementUnits.KILOGRAMS_PER_MEGAGRAM) == "kg/Mg"
    assert str(MeasurementUnits.KILOGRAMS_PER_MILLIGRAM) == "kg/mg"
    assert str(MeasurementUnits.KILOMETERS) == "km"
    assert str(MeasurementUnits.LITERS) == "L"
    assert str(MeasurementUnits.LITERS_PER_CUBIC_METER) == "L/m^3"
    assert str(MeasurementUnits.MEGACALORIES) == "Mcal"
    assert str(MeasurementUnits.MEGACALORIES_PER_KILOGRAM) == "Mcal/kg"
    assert str(MeasurementUnits.MEGAJOULES) == "MJ"
    assert str(MeasurementUnits.MEGAJOULES_PER_CUBIC_METER) == "MJ/m^3"
    assert str(MeasurementUnits.MEGAJOULES_PER_SQUARE_METER) == "MJ/m^2"
    assert str(MeasurementUnits.METERS) == "m"
    assert str(MeasurementUnits.METERS_PER_KILOMETER) == "m/km"
    assert str(MeasurementUnits.METERS_PER_MILLIMETER) == "m/mm"
    assert str(MeasurementUnits.METRIC_TONS) == "metric ton"
    assert str(MeasurementUnits.MILLIMETERS) == "mm"
    assert str(MeasurementUnits.MILLIMETERS_PER_CENTIMETER) == "mm/cm"
    assert str(MeasurementUnits.MILLIMETERS_PER_HECTARE) == "mm/ha"
    assert str(MeasurementUnits.ORDINAL_DAY) == "ordinal day"
    assert str(MeasurementUnits.PERCENT) == "percent"
    assert str(MeasurementUnits.PERCENT_OF_DRY_MATTER) == "percent of DM"
    assert str(MeasurementUnits.PREGNANCY_CHECKS) == "preg check"
    assert str(MeasurementUnits.RADIANS_PER_HOUR) == "rad/h"
    assert str(MeasurementUnits.SECONDS) == "s"
    assert str(MeasurementUnits.SECONDS_PER_DAY) == "s/day"
    assert str(MeasurementUnits.HOURS_PER_DAY) == "h/day"
    assert str(MeasurementUnits.SIMULATION_DAY) == "simulation day"
    assert str(MeasurementUnits.SIMULATION_YEAR) == "simulation year"
    assert str(MeasurementUnits.SQUARE_CENTIMETERS_PER_HECTARE) == "cm^2/ha"
    assert str(MeasurementUnits.SQUARE_METERS_PER_HECTARE) == "m^2/ha"
    assert str(MeasurementUnits.SQUARE_KILOMETERS_PER_HECTARE) == "km^2/ha"
    assert str(MeasurementUnits.SQUARE_MILLIMETERS_PER_HECTARE) == "mm^2/ha"
    assert str(MeasurementUnits.UNITLESS) == "unitless"
    assert str(MeasurementUnits.WET_KILOGRAMS_PER_HECTARE) == "wet kg/ha"


@pytest.mark.parametrize(
    "unit, expected",
    [
        ("m", {"m": 1}),
        ("m^2", {"m": 2}),
        ("kg", {"kg": 1}),
        ("s^-1", {"s": -1}),
        ("m^1*s^-2", {"m": 1, "s": -2}),
        ("N*m", {"N": 1, "m": 1}),
    ],
)
def test_parse_unit(unit: str, expected: dict[str, int]) -> None:
    result = MeasurementUnits._parse_unit(unit)
    assert result == expected, f"For unit '{unit}', expected {expected} but got {result}"


@pytest.mark.parametrize(
    "key, expected",
    [
        ("distance (m)", ({"m": 1}, {})),
        ("area (m^2)", ({"m": 2}, {})),
        ("density (kg/m^3)", ({"kg": 1}, {"m": 3})),
        ("rate (m/s)", ({"m": 1}, {"s": 1})),
        ("acceleration (m/s^2)", ({"m": 1}, {"s": 2})),
        ("pressure (N/m^2)", ({"N": 1}, {"m": 2})),
        ("energy (J/kg*K)", ({"J": 1}, {"kg": 1, "K": 1})),
        ("no units here", ({}, {})),
    ],
)
def test_extract_units(key: str, expected: tuple[dict[str, int], dict[str, int]]) -> None:
    result = MeasurementUnits.extract_units(key)
    assert result == expected, f"For key '{key}', expected {expected} but got {result}"


@pytest.mark.parametrize(
    "units1, units2, expected",
    [
        ({"m": 1}, {"m": 1}, {"m": 2}),
        ({"m": 2}, {"m": -1}, {"m": 1}),
        ({"m": 1, "s": -1}, {"s": 1}, {"m": 1}),
        ({"kg": 1}, {"m": 2, "s": -2}, {"kg": 1, "m": 2, "s": -2}),
        ({"m": 1, "s": -2}, {"m": -1, "s": 2}, {}),
        ({"m": 2}, {"m": -2}, {}),
        ({"N": 1}, {"N": -1, "kg": 1}, {"kg": 1}),
        ({}, {"m": 1}, {"m": 1}),
        ({"m": 1}, {}, {"m": 1}),
        ({"m": 1}, {"unitless": 1}, {"m": 1}),
        ({"m": 1}, {"1": 1}, {"m": 1}),
    ],
)
def test_adjust_unit_exponents(units1: dict[str, int], units2: dict[str, int], expected: dict[str, int]) -> None:
    result = MeasurementUnits.adjust_unit_exponents(units1, units2)
    assert result == expected, f"For units1 '{units1}' and units2 '{units2}', expected {expected} but got {result}"


@pytest.mark.parametrize(
    "numerator, denominator, expected_numerator, expected_denominator",
    [
        ({"m": 1}, {"m": 1}, {}, {}),
        ({"m": 2}, {"m": 1}, {"m": 1}, {}),
        ({"m": 1, "s": -1}, {"s": -1}, {"m": 1}, {}),
        ({"kg": 1}, {"m": 2, "s": -2}, {"kg": 1}, {"m": 2, "s": -2}),
        ({"m": 2}, {"m": 2}, {}, {}),
        ({"N": 1}, {"N": 1, "kg": 1}, {}, {"kg": 1}),
        ({}, {"m": 1}, {}, {"m": 1}),
        ({"m": 1}, {}, {"m": 1}, {}),
        ({"m": 1, "kg": 2}, {"kg": 2, "s": -1}, {"m": 1}, {"s": -1}),
    ],
)
def test_simplify_units(
    numerator: dict[str, int],
    denominator: dict[str, int],
    expected_numerator: dict[str, int],
    expected_denominator: dict[str, int],
) -> None:
    result_numerator, result_denominator = MeasurementUnits.simplify_units(numerator, denominator)
    assert result_numerator == expected_numerator, f"For numerator '{numerator}' and denominator '{denominator}',"
    f" expected numerator {expected_numerator} but got {result_numerator}"
    assert result_denominator == expected_denominator, f"For numerator '{numerator}' and denominator '{denominator}',"
    f" expected denominator {expected_denominator} but got {result_denominator}"


@pytest.mark.parametrize(
    "numerator, denominator, expected",
    [
        ({"m": 1}, {}, "m"),
        ({"m": 2}, {}, "m^2"),
        ({"m": 1}, {"s": 1}, "m/s"),
        ({"m": 1, "s": -1}, {}, "m*s^-1"),
        ({"kg": 1}, {"m": 2, "s": -2}, "kg/m^2*s^-2"),
        ({"m": 1, "s": -2}, {"m": -1, "s": 2}, "m*s^-2/m^-1*s^2"),
        ({}, {"m": 1}, "1/m"),
        ({"m": 1}, {}, "m"),
        ({}, {}, "unitless"),
        ({"unitless": 1}, {}, "unitless"),
        ({}, {"unitless": 1}, "unitless"),
    ],
)
def test_units_to_string(numerator: dict[str, int], denominator: dict[str, int], expected: str) -> None:
    result = MeasurementUnits.units_to_string(numerator, denominator)
    assert result == expected, f"For numerator '{numerator}' and denominator '{denominator}', expected '{expected}' but"
    f" got '{result}'"
