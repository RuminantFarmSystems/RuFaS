class GasEmissionConstants:
    """Constants for gas emission calculations."""

    b1 = 1.0  # rate correcting factor, dimensionless
    b2 = 0.01  # rate correcting factor, dimensionless
    lnA = 43.33  # log of Arrhenius parameter, g CH4/kg VS-h
    E = 112700  # apparent activation energy, J/mol
    R = 8.314  # gas constant, J/K-mol

    r_storage_for_manure_with_crust = 75.0
    r_storage_for_manure_without_crust = 19.0
    r_storage_for_solid_manure = 10.0

    DEFAULT_HOUSING_SPECIFIC_CONSTANT = 260.0  # s/m
    METHANE_ENERGY_DENSITY = 55  # MJ/kg
    METHANE_DENSITY = 0.657  # kg/m^3

    Bo = 0.24
    MCF = 0.79
    MS = 0.9
    METHANE_FACTOR = 0.67  # todo: use a better name

    DEFAULT_VOLATILE_SOLIDS_FRACTION = 0.68

    METHANE_POTENTIAL_Go = 240.0  # mL/g VS
    CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH = 3.1
    SPECIFIC_GROWTH_RATE = 0.637  # micrometers
    POTENTIAL_METHANE_YIELD_OF_MANURE = 0.48  # kg CH4/kg VS
