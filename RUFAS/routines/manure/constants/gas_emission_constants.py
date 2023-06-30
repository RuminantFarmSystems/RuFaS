class GasEmissionConstants:
    """Constants used in gas emission calculations."""

    b1 = 1.0
    """Rate correcting factor (unitless)."""

    b2 = 0.01
    """Rate correcting factor (unitless)."""

    lnA = 43.33
    """Natural log of Arrhenius constant (unitless)."""

    E = 112700.0
    """
    Activation energy (joules per mole, J/mol). The activation energy is the 
    minimum energy that must be available to molecules for a reaction to occur.
    """

    R = 8.314
    """
    The ideal gas constant (J/mol :math:`\cdot` K).
    """

    Bo = 0.24
    """Achievable emission of methane (:math:`CH_4`) during anaerobic digestion (kg :math:`CH_4`/kg VS)."""

    METHANE_CONVERSION_FACTOR = 0.79
    """Methane conversion factor (unitless)."""

    FRACTION_OF_HANDLED_MANURE = 0.9
    """Fraction of manure handled by the manure management system (unitless)."""

    METHANE_FACTOR = 0.67
    """Unit conversion factor for methane from :math:`m^3` to kg (unitless)."""

    METHANE_ENERGY_DENSITY = 55.0
    """
    Methane energy density (megajoules per kg, MJ/kg). This is the amount of energy stored per unit 
    mass of methane.
    """

    METHANE_DENSITY = 0.657
    """Methane density (kg/:math:`m^3`)."""

    METHANE_POTENTIAL_Go = 240.0
    """Methane potential (mL/g). Default is set to 240.0."""

    POTENTIAL_METHANE_YIELD_OF_MANURE = 0.48
    """
    Potential methane yield of manure, (kg :math:`CH_4`/kg VS). This represents the potential 
    amount of methane that can be produced per kilogram of volatile solids (VS) in manure. 
    Default is set to 0.48.
    """

    DEFAULT_SLURRY_STORAGE_TEMPERATURE = 15.0
    """Default slurry storage temperature (:math:`^{\circ}C`). Default is set to 15.0."""

    DEFAULT_VOLATILE_SOLIDS_FRACTION = 0.68
    """
    Default volatile solids fraction, (unitless, [0, 1]). This is the fraction of 
    total solids that are volatile Default is set to 0.68.
    """

    CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH = 3.1
    """
    Chen-Hashimoto kinetic constant (unitless). This constant is used in the 
    Chen-Hashimoto equation to model the kinetic behaviour of the anaerobic digestion process.
    """

    SPECIFIC_GROWTH_RATE = 0.637
    """
    Specific growth rate (:math:`\mu`m). This represents the rate at which the microbial population 
    in the anaerobic digestion process increases.
    """

    DEFAULT_HOUSING_SPECIFIC_CONSTANT = 260.0  # s/m
    """
    Default housing specific constant (s/m). This constant may be used in calculations 
    related to the housing conditions for animals. Default is set to 260.0 s/m.
    """

    DEFAULT_PH_FOR_HOUSING_AMMONIA = 7.7
    """Default pH for housing ammonia (unitless). Default is set to 7.7."""

    DEFAULT_PH_FOR_STORAGE_AMMONIA = 7.5
    """Default pH for storage ammonia (unitless). Default is set to 7.5."""
