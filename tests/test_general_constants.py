from pytest import approx

from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits


def test_general_constants() -> None:
    """Tests the general constants in GeneralConstants."""
    constants = GeneralConstants

    # Memory-related
    assert constants.BYTES_PER_GB == 1024**3

    # Length-related
    assert constants.MM_TO_M == approx(0.001)
    assert constants.CM_TO_MM == approx(10.0)
    assert constants.MM_TO_CM == approx(0.1)
    assert constants.M_TO_KM == approx(0.001)
    assert constants.KM_TO_M == approx(1000)

    # Mass-related
    assert constants.GRAMS_TO_KG == approx(0.001)
    assert constants.KG_TO_GRAMS == approx(1000)
    assert constants.KG_TO_MILLIGRAMS == approx(1_000_000)
    assert constants.MILLIGRAMS_TO_KG == approx(1 / 1_000_000)
    assert constants.MEGAGRAMS_TO_KILOGRAMS == approx(1000)
    assert constants.KILOGRAMS_TO_MEGAGRAMS == approx(1 / 1000)

    # Volume-related
    assert constants.LITERS_TO_CUBIC_METERS == approx(0.001)
    assert constants.CUBIC_METERS_TO_LITERS == approx(1000)
    assert constants.KG_TO_CUBIC_METERS == approx(0.001)
    assert constants.LITERS_TO_CUBIC_MILLIMETERS == approx(1_000_000)
    assert constants.CUBIC_MILLIMETERS_TO_LITERS == approx(1 / 1_000_000)
    assert constants.CUBIC_METERS_TO_CUBIC_MILLIMETERS == approx(1_000_000_000)
    assert constants.CUBIC_MILLIMETERS_TO_CUBIC_METERS == approx(1 / 1_000_000_000)

    # RufasTime-related
    assert constants.YEAR_LENGTH == 365
    assert constants.LEAP_YEAR_LENGTH == 366
    assert constants.SECONDS_PER_DAY == 86400
    assert constants.HOURS_PER_DAY == 24

    # Earth-related data
    assert constants.EARTH_ANGULAR_VELOCITY == approx(0.2618)

    # Temperature-related
    assert constants.CELSIUS_TO_KELVIN == approx(273.15)

    # Fractions and Percentages
    assert constants.PERCENTAGE_TO_FRACTION == approx(0.01)
    assert constants.FRACTION_TO_PERCENTAGE == approx(100.0)

    # Area-related
    assert constants.HECTARES_TO_SQUARE_CENTIMETERS == approx(100_000_000)
    assert constants.SQUARE_CENTIMETERS_TO_HECTARES == approx(1 / 100_000_000)
    assert constants.HECTARES_TO_SQUARE_MILLIMETERS == approx(10_000_000_000)
    assert constants.SQUARE_MILLIMETERS_TO_HECTARES == approx(1 / 10_000_000_000)
    assert constants.SQUARE_KILOMETERS_TO_HECTARES == approx(100)
    assert constants.HECTARES_TO_SQUARE_KILOMETERS == approx(1 / 100)
    assert constants.HECTARES_PER_SQUARE_METER == approx(10_000)
    assert constants.SQUARE_METERS_TO_HECTARES == approx(1 / 10_000)

    # Verify units are correctly assigned
    for constant, unit in constants.CONSTANTS_TO_UNITS.items():
        assert getattr(MeasurementUnits, unit.name) == unit
