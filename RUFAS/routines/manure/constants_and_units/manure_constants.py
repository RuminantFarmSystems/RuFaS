class ManureConstants:
    """
    A class to store constants for manure management.
    """

    MANURE_DENSITY = 990.0
    """The density of manure (kg/:math:`m^3`)."""

    UREA_MOLAR_MASS = 60.06
    """The molar mass of urea (g/mol)."""

    UREA_DENSITY = 1.32
    """The density of urea (g/:math:`cm^3`)."""

    TAN_MOLAR_MASS = 17.0306
    """The molar mass of TAN (g/mol)."""

    URINE_TAN_FACTOR = 0.45
    """The factor to convert urine nitrogen to urine total ammoniacal nitrogen (unitless)."""

    MANURE_SOLIDS_BEDDING_DENSITY = 400.0
    """The density of manure solids bedding (kg/:math:`m^3`)."""

    LIQUID_MANURE_DENSITY = 990.0
    """The density of liquid manure (kg/:math:`m^3`)."""

    SLURRY_MANURE_DENSITY = 1400
    """The density of slurry manure (kg/:math:`m^3`)."""

    SOLID_MANURE_DENSITY = 1250
    """The density of solid manure (kg/:math:`m^3`)."""

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE = 0.5
    """Default proportion of carbon available in manure, (unitless, [0, 1]). Default is set to 0.5."""

    EFFECTIVE_MICROBIAL_DECOMP_RATE = 2.37e-3
    """The effectiveness of microbial decomposition rate (unitless)."""

    DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP = 0.65
    """The effect of moisture on microbial decomposition."""

    DEFAULT_DAYS_SINCE_LAST_TILLAGE = 1
    """
    Default number of days since last tillage used in the calculation of the carbon decomposition rate
    (days). Default is set to 1.
    """

    DEFAULT_LAG_TIME = 2
    """Default lag time used in the calculation of the carbon decomposition rate (days). Default is set to 2."""

    COMPOST_BEDDING_ORGANIC_NITROGEN_FRACTION = 0.952
    """The fraction of organic nitrogen in compost bedding (unitless, [0, 1]). Default is set to 0.952."""

    COMPOST_BEDDING_INORGANIC_NITROGEN_AMMONIUM_FRACTION = 0.5
    """
    The fraction of inorganic nitrogen in compost bedding that is ammonium (unitless, [0, 1]).
    Default is set to 0.5.
    """

    COMPOSTING_N2O_INDIRECT_EMISSION_FACTOR = 0.01
    """
    The constant factor for indirect N2O emissions lost due to leaching and NH3.
    """
