class GasEmissionConstants:
    """Constants for gas emission calculations."""

    b1 = 1.0
    """Rate correcting factor, dimensionless."""

    b2 = 0.01
    """Rate correcting factor, dimensionless."""

    lnA = 43.33
    """Natural log of Arrhenius constant, g CH4/kg VS-h."""

    E = 112700.0
    """Activation energy, J/mol."""

    R = 8.314
    """Gas constant, J/mol-K."""

    Bo = 0.24
    """Achievable emission of CH4 during anaerobic digestion, g CH4/kg VS."""

    MCF = 0.79
    """Methane conversion factor, dimensionless."""

    MS = 1.0
    """TODO"""

    METHANE_FACTOR = 0.67
    """TODO"""

    METHANE_ENERGY_DENSITY = 55.0
    """Methane energy density, MJ/kg."""

    METHANE_DENSITY = 0.657
    """Methane density, kg/m^3."""

    METHANE_POTENTIAL_Go = 240.0
    """Methane potential, mL/g VS."""

    POTENTIAL_METHANE_YIELD_OF_MANURE = 0.48
    """Potential methane yield of manure, g CH4/kg VS."""

    DEFAULT_SLURRY_STORAGE_TEMPERATURE = 15.0
    """Default slurry storage temperature, :math:`^{\circ}C`."""

    DEFAULT_VOLATILE_SOLIDS_FRACTION = 0.68
    """Default volatile solids fraction, dimensionless."""

    CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH = 3.1
    """Chen-Hashimoto kinetic constant, dimensionless."""

    SPECIFIC_GROWTH_RATE = 0.637
    """Specific growth rate, micrometers."""

    DEFAULT_HOUSING_SPECIFIC_CONSTANT_FOR_HOUSING = 260.0  # s/m
    """Default housing specific constant, s/m."""

    DEFAULT_PH_FOR_HOUSING_AMMONIA = 7.7
    """Default pH for housing ammonia, dimensionless."""

    DEFAULT_PH_FOR_STORAGE_AMMONIA = 7.5
    """Default pH for storage ammonia, dimensionless."""

    DEFAULT_STORAGE_AREA = 1.0
    """Default storage area, :math:`m^2`."""

    MAX_COMPOST_AMMONIUM_CONCENTRATION_FRACTION = 2.67 * (10 ** -4)
    """Maximum compost ammonium concentration fraction, dimensionless."""

    NITRIFICATION_CONVERSION_FACTOR = 15.7
    """Nitrification conversion factor, :math:`(kg N_2O/ha-day)/(g N/m^2-day)`."""
