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

        WATER_DENSITY_KG_PER_LITER: The density of water in kilograms per liter.
        WATER_DENSITY_KG_PER_M3: The density of water in kilograms per cubic meter.

        PROTEIN_TO_NITROGEN: The nitrogen content of proteins is assumed to be 16%.
        MILK_FAT_WEIGHT: The weight of milk fat.

        EARTH_ANGULAR_VELOCITY: Earth's angular velocity.

        PERCENTAGE_TO_FRACTION: The conversion factor from a percentage to a fraction.
        FRACTION_TO_PERCENTAGE: The conversion factor from a fraction to a percentage.

    """

    # Length-related
    MM_TO_M = 0.001
    CM_TO_MM = 10.0
    MM_TO_CM = 0.1
    M_TO_KM = 0.001
    KM_TO_M = 1000

    # Mass-related
    GRAMS_TO_KG = 0.001
    KG_TO_GRAMS = 1000

    # Volume-related
    LITERS_TO_CUBIC_METERS = 0.001
    CUBIC_METERS_TO_LITERS = 1000
    KG_TO_CUBIC_METERS = 0.001

    # Time-related
    YEAR_LENGTH = 365
    LEAP_YEAR_LENGTH = 366
    SECONDS_PER_DAY = 86400

    # Density-related
    WATER_DENSITY_KG_PER_LITER = 0.997
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * LITERS_TO_CUBIC_METERS

    # Biochemistry-related
    PROTEIN_TO_NITROGEN = 0.16
    NITROGEN_TO_PROTEIN = 6.25
    MILK_FAT_WEIGHT = 12.2

    # Earth related data
    EARTH_ANGULAR_VELOCITY = 0.2618

    # Fractions and Percentages
    PERCENTAGE_TO_FRACTION = 0.01
    FRACTION_TO_PERCENTAGE = 100.0

    CONSTANTS_TO_UNITS = {
        "MM_TO_M": MeasurementUnits.METERS_PER_MILLIMETER,
        "CM_TO_MM": MeasurementUnits.MILLIMETERS_PER_CENTIMETER,
        "MM_TO_CM": MeasurementUnits.CENTIMETERS_PER_MILLIMETER,
        "M_TO_KM": MeasurementUnits.KILOMETERS_PER_METER,
        "KM_TO_M": MeasurementUnits.METERS_PER_KILOMETER,
        "GRAMS_TO_KG": MeasurementUnits.KILOGRAMS_PER_GRAM,
        "KG_TO_GRAMS": MeasurementUnits.GRAMS_PER_KILOGRAM,
        "LITERS_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_LITER,
        "CUBIC_METERS_TO_LITERS": MeasurementUnits.LITERS_PER_CUBIC_METER,
        "KG_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_KILOGRAM,
        "YEAR_LENGTH": MeasurementUnits.DAYS_PER_YEAR,
        "LEAP_YEAR_LENGTH": MeasurementUnits.DAYS_PER_LEAP_YEAR,
        "SECONDS_PER_DAY": MeasurementUnits.SECONDS_PER_DAY,
        "WATER_DENSITY_KG_PER_LITER": MeasurementUnits.KILOGRAMS_PER_LITER,
        "WATER_DENSITY_KG_PER_M3": MeasurementUnits.KILOGRAMS_PER_CUBIC_METER,
        "PROTEIN_TO_NITROGEN": MeasurementUnits.UNITLESS,
        "NITROGEN_TO_PROTEIN": MeasurementUnits.UNITLESS,
        "MILK_FAT_WEIGHT": MeasurementUnits.UNITLESS,
        "EARTH_ANGULAR_VELOCITY": MeasurementUnits.RADIANS_PER_HOUR,
        "PERCENTAGE_TO_FRACTION": MeasurementUnits.UNITLESS,
        "FRACTION_TO_PERCENTAGE": MeasurementUnits.UNITLESS,
    }
