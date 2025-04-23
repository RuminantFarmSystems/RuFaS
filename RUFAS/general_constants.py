from RUFAS.units import MeasurementUnits


class GeneralConstants:
    """Contains general constants used in RuFaS.

    Attributes:
        MM_TO_M: The conversion factor from millimeters to meters.
        CM_TO_MM: The conversion factor from centimeters to millimeters.
        MM_TO_CM: The conversion factor from millimeters to centimeters.

        GRAMS_TO_KG: The conversion factor from grams to kilograms.
        LITERS_TO_CUBIC_METERS: The conversion factor from liters to cubic meters.
        KG_TO_CUBIC_METERS: The conversion factor from kilograms to cubic meters.

        DAYS_PER_YEAR: The number of days in a year.
        SECONDS_PER_DAY: The number of seconds in a day.
        HOURS_PER_DAY: The number of hours in a day.

        WATER_DENSITY_KG_PER_LITER: The density of water in kilograms per liter.
        WATER_DENSITY_KG_PER_M3: The density of water in kilograms per cubic meter.

        PROTEIN_TO_NITROGEN: The nitrogen content of proteins is assumed to be 16%.
        MILK_FAT_WEIGHT: The weight of milk fat.

        EARTH_ANGULAR_VELOCITY: Earth's angular velocity.

        CELSIUS_TO_KELVIN: The constant for converting temperatures from Celsius to Kelvin.

        PERCENTAGE_TO_FRACTION: The conversion factor from a percentage to a fraction.
        FRACTION_TO_PERCENTAGE: The conversion factor from a fraction to a percentage.

    """

    # Memory related
    BYTES_PER_GB = 1024**3

    # Length-related
    MM_TO_M = 0.001
    CM_TO_MM = 10.0
    MM_TO_CM = 0.1
    M_TO_KM = 0.001
    KM_TO_M = 1000

    # Mass-related
    GRAMS_TO_KG = 0.001
    KG_TO_GRAMS = 1000
    KG_TO_MILLIGRAMS = 1_000_000
    MILLIGRAMS_TO_KG = 1 / KG_TO_MILLIGRAMS
    MEGAGRAMS_TO_KILOGRAMS = 1_000
    KILOGRAMS_TO_MEGAGRAMS = 1 / MEGAGRAMS_TO_KILOGRAMS

    # Volume-related
    LITERS_TO_CUBIC_METERS = 0.001
    CUBIC_METERS_TO_LITERS = 1000
    KG_TO_CUBIC_METERS = 0.001
    LITERS_TO_CUBIC_MILLIMETERS = 1_000_000
    CUBIC_MILLIMETERS_TO_LITERS = 1 / LITERS_TO_CUBIC_MILLIMETERS
    CUBIC_METERS_TO_CUBIC_MILLIMETERS = 1_000_000_000
    CUBIC_MILLIMETERS_TO_CUBIC_METERS = 1 / CUBIC_METERS_TO_CUBIC_MILLIMETERS

    # RufasTime-related
    YEAR_LENGTH = 365
    LEAP_YEAR_LENGTH = 366
    SECONDS_PER_DAY = 86400
    HOURS_PER_DAY = 24

    # Density-related
    WATER_DENSITY_KG_PER_LITER = 0.997
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * LITERS_TO_CUBIC_METERS

    # Biochemistry-related
    PROTEIN_TO_NITROGEN = 0.16
    NITROGEN_TO_PROTEIN = 6.25
    MILK_FAT_WEIGHT = 12.2
    FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL = 0.02
    """Defined in SWAT Theoretical documentation, page 186 in paragraph beneath eqn. 3:1.1.4."""

    # Earth related data
    EARTH_ANGULAR_VELOCITY = 0.2618

    # Temperature-related
    CELSIUS_TO_KELVIN = 273.15

    # Fractions and Percentages
    PERCENTAGE_TO_FRACTION = 0.01
    FRACTION_TO_PERCENTAGE = 100.0

    # Area related
    HECTARES_TO_SQUARE_CENTIMETERS = 100_000_000
    SQUARE_CENTIMETERS_TO_HECTARES = 1 / HECTARES_TO_SQUARE_CENTIMETERS
    HECTARES_TO_SQUARE_MILLIMETERS = 10_000_000_000
    SQUARE_MILLIMETERS_TO_HECTARES = 1 / HECTARES_TO_SQUARE_MILLIMETERS
    SQUARE_KILOMETERS_TO_HECTARES = 100
    HECTARES_TO_SQUARE_KILOMETERS = 1 / SQUARE_KILOMETERS_TO_HECTARES
    HECTARES_PER_SQUARE_METER = 10_000
    SQUARE_METERS_TO_HECTARES = 1 / HECTARES_PER_SQUARE_METER

    DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
    """The default mole fraction of oxygen in the air within the decomposing material layer."""

    AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
    """The mole fraction of oxygen in ambient air."""

    METHANE_FACTOR: float = 0.67
    """Unit conversion factor for methane from :math:`m^3` to kg at 20 degrees C (kg/m3)."""

    GAS_CONSTANT: float = 8.314
    """The ideal gas constant (J/mol * K)."""

    """General temperature lower bound (degrees C)."""
    GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0

    """General temperature upper bound (degrees C)."""
    GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0

    CONSTANTS_TO_UNITS = {
        "BYTES_PER_GB": MeasurementUnits.BYTES,
        "MM_TO_M": MeasurementUnits.METERS_PER_MILLIMETER,
        "CM_TO_MM": MeasurementUnits.MILLIMETERS_PER_CENTIMETER,
        "MM_TO_CM": MeasurementUnits.CENTIMETERS_PER_MILLIMETER,
        "M_TO_KM": MeasurementUnits.KILOMETERS_PER_METER,
        "KM_TO_M": MeasurementUnits.METERS_PER_KILOMETER,
        "GRAMS_TO_KG": MeasurementUnits.KILOGRAMS_PER_GRAM,
        "KG_TO_GRAMS": MeasurementUnits.GRAMS_PER_KILOGRAM,
        "MEGAGRAMS_TO_KILOGRAMS": MeasurementUnits.KILOGRAMS_PER_MEGAGRAM,
        "KILOGRAMS_TO_MEGAGRAMS": MeasurementUnits.MEGAGRAMS_PER_KILOGRAM,
        "MILLIGRAMS_TO_KG": MeasurementUnits.KILOGRAMS_PER_MILLIGRAM,
        "LITERS_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_LITER,
        "CUBIC_METERS_TO_LITERS": MeasurementUnits.LITERS_PER_CUBIC_METER,
        "CUBIC_METERS_TO_CUBIC_MILLIMETERS": MeasurementUnits.CUBIC_MILLIMETERS_PER_CUBIC_METER,
        "CUBIC_MILLIMETERS_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_CUBIC_MILLIMETER,
        "KG_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_KILOGRAM,
        "YEAR_LENGTH": MeasurementUnits.DAYS_PER_YEAR,
        "LEAP_YEAR_LENGTH": MeasurementUnits.DAYS_PER_LEAP_YEAR,
        "SECONDS_PER_DAY": MeasurementUnits.SECONDS_PER_DAY,
        "HOURS_PER_DAY": MeasurementUnits.HOURS_PER_DAY,
        "WATER_DENSITY_KG_PER_LITER": MeasurementUnits.KILOGRAMS_PER_LITER,
        "WATER_DENSITY_KG_PER_M3": MeasurementUnits.KILOGRAMS_PER_CUBIC_METER,
        "PROTEIN_TO_NITROGEN": MeasurementUnits.UNITLESS,
        "NITROGEN_TO_PROTEIN": MeasurementUnits.UNITLESS,
        "MILK_FAT_WEIGHT": MeasurementUnits.UNITLESS,
        "EARTH_ANGULAR_VELOCITY": MeasurementUnits.RADIANS_PER_HOUR,
        "CELSIUS_TO_KELVIN": MeasurementUnits.DEGREES_CELSIUS,
        "PERCENTAGE_TO_FRACTION": MeasurementUnits.UNITLESS,
        "FRACTION_TO_PERCENTAGE": MeasurementUnits.UNITLESS,
        "HECTARES_TO_SQUARE_CENTIMETERS": MeasurementUnits.SQUARE_CENTIMETERS_PER_HECTARE,
        "HECTARES_TO_SQUARE_MILLIMETERS": MeasurementUnits.SQUARE_MILLIMETERS_PER_HECTARE,
        "SQUARE_MILLIMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_MILLIMETER,
        "SQUARE_CENTIMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_CENTIMETER,
        "SQUARE_KILOMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_KILOMETER,
        "HECTARES_TO_SQUARE_KILOMETERS": MeasurementUnits.SQUARE_KILOMETERS_PER_HECTARE,
        "FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL": MeasurementUnits.UNITLESS,
        "HECTARES_PER_SQUARE_METER": MeasurementUnits.HECTARES_PER_SQUARE_METER,
        "SQUARE_METERS_TO_HECTARES": MeasurementUnits.SQUARE_METERS_PER_HECTARE,
    }
