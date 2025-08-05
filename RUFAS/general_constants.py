from RUFAS.units import MeasurementUnits


class GeneralConstants:
    """Contains general constants used in RuFaS.

    Attributes
    ----------
    BYTES_PER_GB : int
        Number of bytes in a gigabyte (bytes).
    MM_TO_M : float
        Conversion factor from millimeters to meters (m/mm).
    CM_TO_MM : float
        Conversion factor from centimeters to millimeters (mm/cm).
    MM_TO_CM : float
        Conversion factor from millimeters to centimeters (cm/mm).
    M_TO_KM : float
        Conversion factor from meters to kilometers (km/m).
    KM_TO_M : float
        Conversion factor from kilometers to meters (m/km).
    GRAMS_TO_KG : float
        Conversion factor from grams to kilograms (kg/g).
    KG_TO_GRAMS : float
        Conversion factor from kilograms to grams (g/kg).
    KG_TO_MILLIGRAMS : float
        Conversion factor from kilograms to milligrams (mg/kg).
    MILLIGRAMS_TO_KG : float
        Conversion factor from milligrams to kilograms (kg/mg).
    MEGAGRAMS_TO_KILOGRAMS : float
        Conversion factor from megagrams to kilograms (kg/Mg).
    KILOGRAMS_TO_MEGAGRAMS : float
        Conversion factor from kilograms to megagrams (Mg/kg).
    LITERS_TO_CUBIC_METERS : float
        Conversion factor from liters to cubic meters (m³/L).
    CUBIC_METERS_TO_LITERS : float
        Conversion factor from cubic meters to liters (L/m³).
    KG_TO_CUBIC_METERS : float
        Conversion factor from kilograms to cubic meters (m³/kg).
    LITERS_TO_CUBIC_MILLIMETERS : float
        Conversion factor from liters to cubic millimeters (mm³/L).
    CUBIC_MILLIMETERS_TO_LITERS : float
        Conversion factor from cubic millimeters to liters (L/mm³).
    CUBIC_METERS_TO_CUBIC_MILLIMETERS : float
        Conversion factor from cubic meters to cubic millimeters (mm³/m³).
    CUBIC_MILLIMETERS_TO_CUBIC_METERS : float
        Conversion factor from cubic millimeters to cubic meters (m³/mm³).
    YEAR_LENGTH : int
        Number of days in a year (days/year).
    LEAP_YEAR_LENGTH : int
        Number of days in a leap year (days/year).
    SECONDS_PER_DAY : int
        Number of seconds in a day (s/day).
    HOURS_PER_DAY : int
        Number of hours in a day (hr/day).
    KCAL_TO_MJ : float
        Conversion factor from kilocalories to megajoules (MJ/kcal).
    MJ_CH4_TO_G_CH4 : float
        Conversion factor from megajoules of methane to grams of methane (g CH₄/MJ CH₄).
    EARTH_ANGULAR_VELOCITY : float
        Earth's angular velocity (rad/s).
    CELSIUS_TO_KELVIN : float
        Conversion factor from Celsius to Kelvin (K/°C).
    PERCENTAGE_TO_FRACTION : float
        Conversion factor from percentage to fractional values (unitless).
    FRACTION_TO_PERCENTAGE : float
        Conversion factor from fractional values to percentage (unitless).
    HECTARES_TO_SQUARE_CENTIMETERS : float
        Conversion factor from hectares to square centimeters (cm²/ha).
    SQUARE_CENTIMETERS_TO_HECTARES : float
        Conversion factor from square centimeters to hectares (ha/cm²).
    HECTARES_TO_SQUARE_MILLIMETERS : float
        Conversion factor from hectares to square millimeters (mm²/ha).
    SQUARE_MILLIMETERS_TO_HECTARES : float
        Conversion factor from square millimeters to hectares (ha/mm²).
    SQUARE_KILOMETERS_TO_HECTARES : float
        Conversion factor from square kilometers to hectares (ha/km²).
    HECTARES_TO_SQUARE_KILOMETERS : float
        Conversion factor from hectares to square kilometers (km²/ha).
    HECTARES_PER_SQUARE_METER : float
        Conversion factor from hectares to square meters (ha/m²).
    SQUARE_METERS_TO_HECTARES : float
        Conversion factor from square meters to hectares (m²/ha).
    AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN : float
        Mole fraction of oxygen in ambient air (unitless).
    GAS_CONSTANT : float
        The ideal gas constant (J/(K·mol)).
    IDEAL_GAS_LAW_R : float
        Value of R in the ideal gas law (L·atm/(mol·K)).
    CONSTANTS_TO_UNITS : dict
        A dictionary mapping constant names to their associated units.

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

    # Biochemistry-related
    KCAL_TO_MJ = 4.184
    MJ_CH4_TO_G_CH4 = 0.05565

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

    # Manure related
    AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21

    GAS_CONSTANT: float = 8.314
    IDEAL_GAS_LAW_R: float = 0.0821

    CONSTANTS_TO_UNITS = {
        "BYTES_PER_GB": MeasurementUnits.BYTES,
        "MM_TO_M": MeasurementUnits.METERS_PER_MILLIMETER,
        "CM_TO_MM": MeasurementUnits.MILLIMETERS_PER_CENTIMETER,
        "MM_TO_CM": MeasurementUnits.CENTIMETERS_PER_MILLIMETER,
        "M_TO_KM": MeasurementUnits.KILOMETERS_PER_METER,
        "KM_TO_M": MeasurementUnits.METERS_PER_KILOMETER,
        "GRAMS_TO_KG": MeasurementUnits.KILOGRAMS_PER_GRAM,
        "KG_TO_GRAMS": MeasurementUnits.GRAMS_PER_KILOGRAM,
        "KG_TO_MILLIGRAMS": MeasurementUnits.MILLIGRAMS_PER_KILOGRAM,
        "MILLIGRAMS_TO_KG": MeasurementUnits.KILOGRAMS_PER_MILLIGRAM,
        "MEGAGRAMS_TO_KILOGRAMS": MeasurementUnits.KILOGRAMS_PER_MEGAGRAM,
        "KILOGRAMS_TO_MEGAGRAMS": MeasurementUnits.MEGAGRAMS_PER_KILOGRAM,
        "LITERS_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_LITER,
        "CUBIC_METERS_TO_LITERS": MeasurementUnits.LITERS_PER_CUBIC_METER,
        "KG_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_KILOGRAM,
        "LITERS_TO_CUBIC_MILLIMETERS": MeasurementUnits.CUBIC_MILLIMETERS_PER_LITER,
        "CUBIC_MILLIMETERS_TO_LITERS": MeasurementUnits.LITERS_PER_CUBIC_MILLIMETER,
        "CUBIC_METERS_TO_CUBIC_MILLIMETERS": MeasurementUnits.CUBIC_MILLIMETERS_PER_CUBIC_METER,
        "CUBIC_MILLIMETERS_TO_CUBIC_METERS": MeasurementUnits.CUBIC_METERS_PER_CUBIC_MILLIMETER,
        "YEAR_LENGTH": MeasurementUnits.DAYS_PER_YEAR,
        "LEAP_YEAR_LENGTH": MeasurementUnits.DAYS_PER_LEAP_YEAR,
        "SECONDS_PER_DAY": MeasurementUnits.SECONDS_PER_DAY,
        "HOURS_PER_DAY": MeasurementUnits.HOURS_PER_DAY,
        "KCAL_TO_MJ": MeasurementUnits.MCAL_PER_MJ,
        "MJ_CH4_TO_G_CH4": MeasurementUnits.MJ_CH4_PER_G_CH4,
        "EARTH_ANGULAR_VELOCITY": MeasurementUnits.RADIANS_PER_HOUR,
        "CELSIUS_TO_KELVIN": MeasurementUnits.DEGREES_CELSIUS,
        "PERCENTAGE_TO_FRACTION": MeasurementUnits.UNITLESS,
        "FRACTION_TO_PERCENTAGE": MeasurementUnits.UNITLESS,
        "HECTARES_TO_SQUARE_CENTIMETERS": MeasurementUnits.SQUARE_CENTIMETERS_PER_HECTARE,
        "SQUARE_CENTIMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_CENTIMETER,
        "HECTARES_TO_SQUARE_MILLIMETERS": MeasurementUnits.SQUARE_MILLIMETERS_PER_HECTARE,
        "SQUARE_MILLIMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_MILLIMETER,
        "SQUARE_KILOMETERS_TO_HECTARES": MeasurementUnits.HECTARES_PER_SQUARE_KILOMETER,
        "HECTARES_TO_SQUARE_KILOMETERS": MeasurementUnits.SQUARE_KILOMETERS_PER_HECTARE,
        "HECTARES_PER_SQUARE_METER": MeasurementUnits.HECTARES_PER_SQUARE_METER,
        "SQUARE_METERS_TO_HECTARES": MeasurementUnits.SQUARE_METERS_PER_HECTARE,
        "AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN": MeasurementUnits.UNITLESS,
        "GAS_CONSTANT": MeasurementUnits.J_PER_K_PER_MOL,
        "IDEAL_GAS_LAW_R": MeasurementUnits.L_ATM_PER_MOL_K,
    }
