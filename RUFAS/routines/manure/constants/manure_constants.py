class ManureConstants:
    """Constants for manure management.

    Attributes:
        MANURE_DENSITY: The density of manure, kg/m^3.
        UREA_MOLAR_MASS: The molar mass of urea, g/mol.
        UREA_DENSITY: The density of urea, g/cm^3.
        TAN_MOLAR_MASS: The molar mass of total_ammoniacal_nitrogen, g/mol.
        URINE_TAN_FACTOR: The factor to convert manure nitrogen to urine total_ammoniacal_nitrogen, dimensionless.
        MANURE_SOLIDS_BEDDING_DENSITY: The density of manure solids bedding, kg/m^3.

    """
    MANURE_DENSITY = 990.0  # kg/m^3
    UREA_MOLAR_MASS = 60.06  # g/mol
    UREA_DENSITY = 1.32  # g/cm^3 = g/mL = kg/L
    TAN_MOLAR_MASS = 17.0306  # g/mol
    URINE_TAN_FACTOR = 0.45  # dimensionless
    MANURE_SOLIDS_BEDDING_DENSITY = 400.0  # kg/m^3
