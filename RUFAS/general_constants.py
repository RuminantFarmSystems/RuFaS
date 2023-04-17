class GeneralConstants:
    """Contains general constants used in the manure treatment module.

    Attributes:
        GRAMS_TO_KG: The conversion factor from grams to kilograms.
        LITERS_TO_CUBIC_METERS: The conversion factor from liters to cubic meters.
        KG_TO_CUBIC_METERS: The conversion factor from kilograms to cubic meters.

        DAYS_PER_YEAR: The number of days in a year.
        SECONDS_PER_DAY: The number of seconds in a day.

        WATER_DENSITY_KG_PER_LITER: The density of water in kilograms per liter.
        WATER_DENSITY_KG_PER_M3: The density of water in kilograms per cubic meter.

        PROTEIN_TO_NITROGEN: The nitrogen content of proteins is assumed to be 16%.   

    """
    # Mass-related
    GRAMS_TO_KG = 0.001
    KG_TO_GRAMS = 1000

    # Volume-related
    LITERS_TO_CUBIC_METERS = 0.001
    CUBIC_METERS_TO_LITERS = 1000
    KG_TO_CUBIC_METERS = 0.001

    # Time-related
    DAYS_PER_YEAR = 365
    SECONDS_PER_DAY = 86400

    # Density-related
    WATER_DENSITY_KG_PER_LITER = 0.997
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * LITERS_TO_CUBIC_METERS

    # Biochemistry-related
    PROTEIN_TO_NITROGEN = 0.16
