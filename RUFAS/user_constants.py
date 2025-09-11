from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits


class UserConstants:
    """
    Contains user-overridable constants for RUFAS.

    Attributes
    ----------
    WATER_DENSITY_KG_PER_LITER : float
        Density of water (kg/L).
    WATER_DENSITY_KG_PER_M3 : float
        Density of water (kg/m^3).
    PROTEIN_TO_NITROGEN : float
        Conversion factor from protein to nitrogen (unitless).
    NITROGEN_TO_PROTEIN : float
        Conversion factor from nitrogen to protein (unitless).
    MILK_FAT_WEIGHT : float
        Average weight of milk fat (unitless).
    FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL : float
        Fraction of humic nitrogen in an active pool (unitless).
        Defined in SWAT Theoretical documentation, page 186 in paragraph beneath eqn. 3:1.1.4.
    METHANE_FACTOR : float
        Conversion factor for methane from :math:`m^3` to kg at 20 °C (kg/m³).
    GENERAL_LOWER_BOUND_TEMPERATURE : float
        General temperature lower bound (°C).
    GENERAL_UPPER_BOUND_TEMPERATURE : float
        General temperature upper bound (°C).
    CONSTANTS_TO_UNITS : dict[str, MeasurementUnits]
        A dictionary mapping constant names to their respective measurement units.

    """

    # Density-related
    WATER_DENSITY_KG_PER_LITER = 0.997
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * GeneralConstants.LITERS_TO_CUBIC_METERS

    # Biochemistry-related
    PROTEIN_TO_NITROGEN = 0.16
    NITROGEN_TO_PROTEIN = 6.25
    MILK_FAT_WEIGHT = 12.2
    FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL = 0.02

    METHANE_FACTOR: float = 0.67

    GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0
    GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0

    # Energy use related
    SPECIFIC_FUEL_CONSUMPTION: float = 0.2234

    CONSTANTS_TO_UNITS = {
        "WATER_DENSITY_KG_PER_LITER": MeasurementUnits.KILOGRAMS_PER_LITER,
        "WATER_DENSITY_KG_PER_M3": MeasurementUnits.KILOGRAMS_PER_CUBIC_METER,
        "PROTEIN_TO_NITROGEN": MeasurementUnits.UNITLESS,
        "NITROGEN_TO_PROTEIN": MeasurementUnits.UNITLESS,
        "MILK_FAT_WEIGHT": MeasurementUnits.UNITLESS,
        "FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL": MeasurementUnits.UNITLESS,
        "METHANE_FACTOR": MeasurementUnits.KILOGRAMS_PER_CUBIC_METER,
        "GENERAL_LOWER_BOUND_TEMPERATURE": MeasurementUnits.DEGREES_CELSIUS,
        "GENERAL_UPPER_BOUND_TEMPERATURE": MeasurementUnits.DEGREES_CELSIUS,
        "SPECIFIC_FUEL_CONSUMPTION": MeasurementUnits.LITERS_PER_KILOWATTS_PER_HOUR,
    }
