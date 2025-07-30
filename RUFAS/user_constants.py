from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits


class UserConstants:
    # Density-related
    WATER_DENSITY_KG_PER_LITER = 0.997
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * GeneralConstants.LITERS_TO_CUBIC_METERS

    # Biochemistry-related
    PROTEIN_TO_NITROGEN = 0.16
    NITROGEN_TO_PROTEIN = 6.25
    MILK_FAT_WEIGHT = 12.2
    FRACTION_OF_HUMIC_NITROGEN_IN_ACTIVE_POOL = 0.02
    """Defined in SWAT Theoretical documentation, page 186 in paragraph beneath eqn. 3:1.1.4."""

    METHANE_FACTOR: float = 0.67
    """Unit conversion factor for methane from :math:`m^3` to kg at 20 degrees C (kg/m3)."""

    GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0
    """General temperature lower bound (degrees C)."""

    GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0
    """General temperature upper bound (degrees C)."""

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
    }
