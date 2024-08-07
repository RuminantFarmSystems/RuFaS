import pytest
from RUFAS.units import MeasurementUnits


def test_units_member_values() -> None:
    """
    Test accuracy of the values for each of the MeasurementUnits members
    """

    assert MeasurementUnits.ANIMALS.value == "animals"
    assert MeasurementUnits.ARTIFICIAL_INSEMINATIONS.value == "AIs"
    assert MeasurementUnits.CALENDAR_YEAR.value == "calendar year"
    assert MeasurementUnits.CONCEPTIONS.value == "conceptions"
    assert MeasurementUnits.CONCEPTIONS_PER_SERVICE.value == "conceptions per service"
    assert MeasurementUnits.CUBIC_METERS.value == "m^3"
    assert MeasurementUnits.CUBIC_METERS_PER_DAY.value == "m^3/day"
    assert MeasurementUnits.DAYS.value == "days"
    assert MeasurementUnits.DEGREES_CELSIUS.value == "°C"
    assert MeasurementUnits.DRY_KILOGRAMS.value == "dry kg"
    assert MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE.value == "dry kg/ha"
    assert MeasurementUnits.FRACTION.value == "fraction"
    assert MeasurementUnits.GRAMS.value == "g"
    assert MeasurementUnits.GRAMS_PER_DAY.value == "g/day"
    assert MeasurementUnits.GRAMS_PER_LITER.value == "g/L"
    assert MeasurementUnits.HECTARE.value == "ha"
    assert MeasurementUnits.HOURS.value == "hours"
    assert MeasurementUnits.INJECTIONS.value == "injections"
    assert MeasurementUnits.KILOGRAMS.value == "kg"
    assert MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER.value == "kg CO2 / kg DM"
    assert MeasurementUnits.KILOGRAMS_PER_ANIMAL.value == "kg/animal"
    assert MeasurementUnits.KILOGRAMS_PER_DAY.value == "kg/day"
    assert MeasurementUnits.KILOGRAMS_PER_HECTARE.value == "kg/ha"
    assert MeasurementUnits.MEGACALORIES.value == "Mcal"
    assert MeasurementUnits.MEGACALORIES_PER_KILOGRAM.value == "Mcal/kg"
    assert MeasurementUnits.MEGAJOULES.value == "MJ"
    assert MeasurementUnits.MEGAJOULES_PER_CUBIC_METER.value == "MJ/m^3"
    assert MeasurementUnits.MEGAJOULES_PER_SQUARE_METER.value == "MJ/m^2"
    assert MeasurementUnits.METERS.value == "m"
    assert MeasurementUnits.METRIC_TONS.value == "metric tons"
    assert MeasurementUnits.MILLIMETERS.value == "mm"
    assert MeasurementUnits.MILLIMETERS_PER_HECTARE.value == "mm/ha"
    assert MeasurementUnits.ORDINAL_DAY.value == "ordinal day"
    assert MeasurementUnits.PERCENT.value == "percent"
    assert MeasurementUnits.PERCENT_OF_DRY_MATTER.value == "percent of DM"
    assert MeasurementUnits.PREGNANCY_CHECKS.value == "preg checks"
    assert MeasurementUnits.SIMULATION_DAY.value == "simulation day"
    assert MeasurementUnits.SIMULATION_YEAR.value == "simulation year"
    assert MeasurementUnits.UNITLESS.value == "unitless"
    assert MeasurementUnits.WET_KILOGRAMS_PER_HECTARE.value == "wet kg/ha"


def test_units_str_method() -> None:
    """
    Test the __str__ method for each of the MeasurementUnits members.
    """

    assert str(MeasurementUnits.ANIMALS) == "animals"
    assert str(MeasurementUnits.ARTIFICIAL_INSEMINATIONS) == "AIs"
    assert str(MeasurementUnits.CALENDAR_YEAR) == "calendar year"
    assert str(MeasurementUnits.CONCEPTIONS) == "conceptions"
    assert str(MeasurementUnits.CONCEPTIONS_PER_SERVICE) == "conceptions per service"
    assert str(MeasurementUnits.CUBIC_METERS) == "m^3"
    assert str(MeasurementUnits.CUBIC_METERS_PER_DAY) == "m^3/day"
    assert str(MeasurementUnits.DAYS) == "days"
    assert str(MeasurementUnits.DEGREES_CELSIUS) == "°C"
    assert str(MeasurementUnits.DRY_KILOGRAMS) == "dry kg"
    assert str(MeasurementUnits.DRY_KILOGRAMS_PER_HECTARE) == "dry kg/ha"
    assert str(MeasurementUnits.FRACTION) == "fraction"
    assert str(MeasurementUnits.GRAMS) == "g"
    assert str(MeasurementUnits.GRAMS_PER_DAY) == "g/day"
    assert str(MeasurementUnits.GRAMS_PER_LITER) == "g/L"
    assert str(MeasurementUnits.HECTARE) == "ha"
    assert str(MeasurementUnits.HOURS) == "hours"
    assert str(MeasurementUnits.INJECTIONS) == "injections"
    assert str(MeasurementUnits.KILOGRAMS) == "kg"
    assert str(MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER) == "kg CO2 / kg DM"
    assert str(MeasurementUnits.KILOGRAMS_PER_ANIMAL) == "kg/animal"
    assert str(MeasurementUnits.KILOGRAMS_PER_DAY) == "kg/day"
    assert str(MeasurementUnits.KILOGRAMS_PER_HECTARE) == "kg/ha"
    assert str(MeasurementUnits.MEGACALORIES) == "Mcal"
    assert str(MeasurementUnits.MEGACALORIES_PER_KILOGRAM) == "Mcal/kg"
    assert str(MeasurementUnits.MEGAJOULES) == "MJ"
    assert str(MeasurementUnits.MEGAJOULES_PER_CUBIC_METER) == "MJ/m^3"
    assert str(MeasurementUnits.MEGAJOULES_PER_SQUARE_METER) == "MJ/m^2"
    assert str(MeasurementUnits.METERS) == "m"
    assert str(MeasurementUnits.METRIC_TONS) == "metric tons"
    assert str(MeasurementUnits.MILLIMETERS) == "mm"
    assert str(MeasurementUnits.MILLIMETERS_PER_HECTARE) == "mm/ha"
    assert str(MeasurementUnits.ORDINAL_DAY) == "ordinal day"
    assert str(MeasurementUnits.PERCENT) == "percent"
    assert str(MeasurementUnits.PERCENT_OF_DRY_MATTER) == "percent of DM"
    assert str(MeasurementUnits.PREGNANCY_CHECKS) == "preg checks"
    assert str(MeasurementUnits.SIMULATION_DAY) == "simulation day"
    assert str(MeasurementUnits.SIMULATION_YEAR) == "simulation year"
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
    ]
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
    ]
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
    ]
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
    ]
)
def test_simplify_units(numerator: dict[str, int], denominator: dict[str, int], expected_numerator: dict[str, int],
                        expected_denominator: dict[str, int]) -> None:
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
    ]
)
def test_units_to_string(numerator: dict[str, int], denominator: dict[str, int], expected: str) -> None:
    result = MeasurementUnits.units_to_string(numerator, denominator)
    assert result == expected, f"For numerator '{numerator}' and denominator '{denominator}', expected '{expected}' but"
    f" got '{result}'"
