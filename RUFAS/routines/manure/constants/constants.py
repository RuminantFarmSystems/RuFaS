class ManureManagementConstants:
    """This class stores constants related to unit conversion and manure calculations.

    All the constant names are capitalized. To make code look more natural, the
    general way of using these constants is through multiplication.

    """

    # Unit conversion constants
    LITERS_TO_CUBIC_METERS = 0.001
    KG_TO_CUBIC_METERS = 0.001
    CUBIC_METERS_TO_LITERS = 1000.0
    GRAMS_TO_KG = 0.001
    INCHES_TO_METERS = 0.0254  # inch/m
    FEET_TO_METERS = 0.3048  # ft/m

    # Specific constants
    UREA_MOLAR_MASS = 60.06  # g/mol
    UREA_DENSITY = 1.32  # g/cm^3 = g/mL = kg/L
    TAN_MOLAR_MASS = 17.0306  # g/mol
    METHANE_ENERGY_DENSITY = 55  # MJ / kg
    METHANE_DENSITY = 0.657  # kg/m^3

    WATER_DENSITY_KG_PER_LITER = 0.997  # kg/liter
    WATER_DENSITY_KG_PER_M3 = WATER_DENSITY_KG_PER_LITER * LITERS_TO_CUBIC_METERS
    DAYS_PER_YEAR = 365  # days per year



