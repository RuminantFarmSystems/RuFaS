class ManureConstants:
    """
    A class to store constants for manure management.

    Attributes
    ----------
    MANURE_DENSITY : float
        The density of manure (kg/:math:`m^3`).
    UREA_MOLAR_MASS : float
        The molar mass of urea (g/mol).
    UREA_DENSITY : float
        The density of urea (g/:math:`cm^3`).
    TAN_MOLAR_MASS : float
        The molar mass of TAN (g/mol).
    URINE_TAN_FACTOR : float
        The factor to convert urine nitrogen to urine total ammoniacal nitrogen (unitless).
    MANURE_SOLIDS_BEDDING_DENSITY : float
        The density of manure solids bedding (kg/:math:`m^3`).
    LIQUID_MANURE_DENSITY : float
        The density of liquid manure (kg/:math:`m^3`).
    SLURRY_MANURE_DENSITY : int
        The density of slurry manure (kg/:math:`m^3`).
    SOLID_MANURE_DENSITY : int
        The density of solid manure (kg/:math:`m^3`).
    """

    MANURE_DENSITY = 990.0
    UREA_MOLAR_MASS = 60.06
    UREA_DENSITY = 1.32
    TAN_MOLAR_MASS = 17.0306
    URINE_TAN_FACTOR = 0.45
    MANURE_SOLIDS_BEDDING_DENSITY = 400.0
    LIQUID_MANURE_DENSITY = 990.0
    SLURRY_MANURE_DENSITY = 1400
    SOLID_MANURE_DENSITY = 1250
    DEFAULT_CARBON_AVAILABLE_IN_MANURE = 0.5
    """
    Default proportion of carbon available in manure, (unitless, [0, 1]). Default is set to 0.5.
    """
    EFFECTIVE_MICROBIAL_DECOMP_RATE = 2.37e-3
    """The effectiveness of microbial decomposition rate (unitless)"""
    DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP = 0.65
    """The effect of moisture on microbial decomposition"""
