class ManureConstants:
    """
    A class to store constants for manure management.
    """

    ACHIEVABLE_METHANE_EMISSION = 0.24
    """Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids)."""

    MANURE_DENSITY = 990.0
    """The density of manure (kg/:math:`m^3`)."""

    MANURE_SOLIDS_BEDDING_DENSITY = 400.0
    """The density of manure solids bedding (kg/:math:`m^3`)."""

    LIQUID_MANURE_DENSITY = 1000
    """The density of liquid manure (kg/:math:`m^3`)."""

    SLURRY_MANURE_DENSITY = 990
    """The density of slurry manure (kg/:math:`m^3`)."""

    SOLID_MANURE_DENSITY = 700
    """The density of solid manure (kg/:math:`m^3`)."""

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

    METHANE_DESTRUCTION_EFFICIENCY = 81
    """
    The percentage of methane destroyed in systems using a cap and flare
    """

    AD_TAN_INCREASE_FACTOR = 1.60
    """
    The factor by which manure total ammoniacal nitrogen content is increased by the anaerobic digestion process
    (unitless).
    """
