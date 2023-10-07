class GasEmissionConstants:
    """Constants used in gas emission calculations."""

    METHANE_EMISSION_COEFFICIENT = 24
    """Methane emission coefficient, used in calculation of slurry storage methane emission (unitless)."""

    DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR = 1.0
    """
    Rate correcting factor for degradable volatile solids, used in calculation of slurry storage
    methane emission (unitless).
    """

    NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR = 0.01
    """
    Rate correcting factor for non-degradable volatile solids, used in calculation of slurry storage
    methane emission (unitless)."""

    NATURAL_LOG_ARRHENIUS_CONSTANT = 43.33
    """Natural log of the Arrhenius constant (unitless)."""

    ACTIVATION_ENERGY = 112700.0
    """
    Activation energy (joules per mole, J/mol). The activation energy is the
    minimum energy that must be available to molecules for a reaction to occur.
    """

    GAS_CONSTANT = 8.314
    """The ideal gas constant (J/mol :math:`\\cdot` K)."""

    ACHIEVABLE_METHANE_EMISSION = 0.24
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

    MCF_CONSTANT_A = 7.11
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
    Methane Conversion Factor (MCF) calculation. This coefficient scales the exponential
    function of ambient barn temperature.
    """

    MCF_CONSTANT_B = 0.0884
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
    Methane Conversion Factor (MCF) calculation. This exponent coefficient determines the rate
    at which MCF increases with ambient barn temperature.
    """

    POTENTIAL_METHANE_YIELD_OF_MANURE = 0.48
    """
    Potential methane yield of manure, (kg :math:`CH_4`/kg VS). This represents the potential
    amount of methane that can be produced per kilogram of volatile solids (VS) in manure.
    Default is set to 0.48.
    """

    DEFAULT_SLURRY_STORAGE_TEMPERATURE = 15.0
    """Default slurry storage temperature (:math:`^{\\circ}C`). Default is set to 15.0."""

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
    Specific growth rate (:math:`\\mu`m). This represents the rate at which the microbial population
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

    OXYGEN_HALF_SATURATION_CONSTANT = 0.02
    """The half saturation constant of Oxygen gas (O2)"""

    DEFAULT_CARBON_AVAILABLE_IN_BEDDING = 0.35
    """
    Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35.
    """
    GENERAL_LOWER_BOUND_TEMPERATURE = -40.0
    """General temperature lower bound (:math:`^{\\circ}C`). Default is set to -40.0."""

    GENERAL_UPPER_BOUND_TEMPERATURE = 60.0
    """General temperature upper bound (:math:`^{\\circ}C`). Default is set to 60.0."""

    SOLID_AND_SEMI_SOLID_MANURE_HSC = 10.0
    """Housing specific constant for solid and semi-solid manure (s/m)."""

    SLURRY_MANURE_HSC = 19.0
    """Housing specific constant for slurry manure (s/m)."""

    LIQUID_MANURE_HSC = 4.1
    """Housing specific constant for liquid manure (s/m)."""

    SOLID_MANURE_THRESHOLD = 8.0
    """Dry matter threshold for classifying solid and semi-solid manure (unitless)."""

    SLURRY_MANURE_THRESHOLD = 5.0
    """Dry matter threshold for classifying slurry manure (unitless)."""

    DEFAULT_STORAGE_AREA_PER_ANIMAL = 1.0
    """Default storage area per animal (:math:`m^2`). Default is set to 1.0."""

    AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING = 0.5
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is tilled (unitless).
    """

    AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING = 0.25
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is not tilled (unitless).
    """

    LEACHING_COEFFICIENT = 0.035
    """Leaching coefficient used in the calculation of nitrogen loss in a compost bedded pack barn (unitless)."""

    NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING = 0.07
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is tilled (unitless).
    """

    NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING = 0.01
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is not tilled (unitless).
    """

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING = 0.35
    """
    Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35.
    """
