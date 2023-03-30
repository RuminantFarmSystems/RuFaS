class GasEmissionConstants:
    """Constants for gas emission calculations.

    Attributes:
        b1: rate correcting factor, dimensionless.
        b2: rate correcting factor, dimensionless.
        lnA: natural log of Arrhenius constant, g CH4/kg VS-h.
        E: activation energy, J/mol.
        R: gas constant, J/mol-K.

        Bo: achievable emission of CH4 during anaerobic digestion, g CH4/kg VS.
        MCF: TODO
        MS: TODO
        METHANE_FACTOR: TODO.
        METHANE_ENERGY_DENSITY: methane energy density, MJ/kg.
        METHANE_DENSITY: methane density, kg/m^3.
        METHANE_POTENTIAL_Go: methane potential, mL/g VS.
        POTENTIAL_METHANE_YIELD_OF_MANURE: potential methane yield of manure, g CH4/kg VS.

        DEFAULT_VOLATILE_SOLIDS_FRACTION: default volatile solids fraction, dimensionless.
        CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH: Chen-Hashimoto kinetic constant, dimensionless.
        SPECIFIC_GROWTH_RATE: specific growth rate, micrometers.

        DEFAULT_HOUSING_SPECIFIC_CONSTANT: default housing specific constant, s/m.

    """
    b1 = 1.0  # rate correcting factor, dimensionless.
    b2 = 0.01  # rate correcting factor, dimensionless.
    lnA = 43.33  # natural log of Arrhenius constant, g CH4/kg VS-h.
    E = 112700  # activation energy, J/mol.
    R = 8.314  # gas constant, J/mol-K.

    # Methane related constants
    Bo = 0.24  # achievable emission of CH4 during anaerobic digestion, g CH4/kg VS
    MCF = 0.79
    MS = 1.0
    METHANE_FACTOR = 0.67  # TODO: use a better name

    METHANE_ENERGY_DENSITY = 55  # MJ/kg
    METHANE_DENSITY = 0.657  # kg/m^3
    METHANE_POTENTIAL_Go = 240.0  # mL/g VS
    POTENTIAL_METHANE_YIELD_OF_MANURE = 0.48  # g CH4/kg VS
    DEFAULT_SLURRY_STORAGE_TEMPERATURE = 15.0  # deg C

    DEFAULT_VOLATILE_SOLIDS_FRACTION = 0.68  # dimensionless
    CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH = 3.1  # dimensionless
    SPECIFIC_GROWTH_RATE = 0.637  # micrometers

    DEFAULT_HOUSING_SPECIFIC_CONSTANT = 260.0  # s/m
