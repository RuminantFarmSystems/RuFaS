from typing import NamedTuple


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

    MANURE_SOLIDS_BEDDING_DENSITY = 400.0
    """The density of manure solids bedding (kg/:math:`m^3`)."""

    LIQUID_MANURE_DENSITY = 1000
    """The density of liquid manure (kg/:math:`m^3`)."""

    SLURRY_MANURE_DENSITY = 990
    """The density of slurry manure (kg/:math:`m^3`)."""

    SOLID_MANURE_DENSITY = 700
    """The density of solid manure (kg/:math:`m^3`)."""

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE = 0.5
    """Default proportion of carbon available in manure, (unitless, [0, 1]). Default is set to 0.5."""

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING = 0.35
    """Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35."""

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

    METHANE_TO_VOLATILE_SOLIDS_FACTOR = 3
    """
    The conversion from methane emission to volatile solids (NEED UNITS!). Set to 3.
    """

    LIQUID_MANURE_SOLIDS_FRACTION = 0.05
    """
    The fraction of total solids in Liquid manure. Temporary placeholder until upstream solids tracking is fixed.
    """

    BarnArea = NamedTuple("BarnArea", [("has_cows", float), ("no_cows", float)])
    freestall = BarnArea(has_cows=3.5, no_cows=2.5)
    tiestall = BarnArea(has_cows=1.2, no_cows=1.0)
    bedded_pack = BarnArea(has_cows=5.0, no_cows=3.0)
    open_lot = BarnArea(has_cows=5.0, no_cows=3.0)

    barn_area_by_pen_type = {
        "freestall": freestall,
        "tiestall": tiestall,
        "compost bedded pack barn": bedded_pack,
        "open lot": open_lot,
    }
