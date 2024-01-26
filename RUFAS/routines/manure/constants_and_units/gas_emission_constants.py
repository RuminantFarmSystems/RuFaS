from typing import Dict
from RUFAS.routines.manure.manure_treatments.composting_types import CompostingType


class GasEmissionConstants:
    """Constants used in gas emission calculations."""

    METHANE_EMISSION_COEFFICIENT: float = 24
    """Methane emission coefficient, used in calculation of slurry storage methane emission (unitless)."""

    DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 1.0
    """
    Rate correcting factor for degradable volatile solids, used in calculation of slurry storage
    methane emission (unitless).
    """

    NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 0.01
    """
    Rate correcting factor for non-degradable volatile solids, used in calculation of slurry storage
    methane emission (unitless)."""

    NATURAL_LOG_ARRHENIUS_CONSTANT: float = 43.33
    """Natural log of the Arrhenius constant (unitless)."""

    ACTIVATION_ENERGY: float = 112700.0
    """
    Activation energy (joules per mole, J/mol). The activation energy is the
    minimum energy that must be available to molecules for a reaction to occur.
    """

    GAS_CONSTANT: float = 8.314
    """The ideal gas constant (J/mol :math:`\\cdot` K)."""

    ACHIEVABLE_METHANE_EMISSION: float = 0.24
    """Achievable emission of methane (:math:`CH_4`) from dairy manure (kg :math:`CH_4`/kg VS)."""

    METHANE_CONVERSION_FACTOR: float = 0.79
    """Methane conversion factor (unitless)."""

    FRACTION_OF_HANDLED_MANURE: float = 0.9
    """Fraction of manure handled by the manure management system (unitless)."""

    METHANE_FACTOR: float = 0.67
    """Unit conversion factor for methane from :math:`m^3` to kg (unitless)."""

    METHANE_ENERGY_DENSITY: float = 55.0
    """
    Methane energy density (megajoules per kg, MJ/kg). This is the amount of energy stored per unit
    mass of methane.
    """

    METHANE_DENSITY: float = 0.657
    """Methane density (kg/:math:`m^3`)."""

    METHANE_POTENTIAL_Go: float = 240.0
    """Methane potential (mL/g). Default is set to 240.0."""

    MCF_CONSTANT_A: float = 7.11
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
    Methane Conversion Factor (MCF) calculation. This coefficient scales the exponential
    function of ambient barn temperature.
    """

    MCF_CONSTANT_B: float = 0.0884
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the
    Methane Conversion Factor (MCF) calculation. This exponent coefficient determines the rate
    at which MCF increases with ambient barn temperature.
    """

    MCF_LOWER_BOUND_TEMPERATURE: float = 15.0
    """
    The lower bound temperature for determining MCF for windrow composting.
    """

    MCF_UPPER_BOUND_TEMPERATURE: float = 25.0
    """
    The lower bound temperature for determining MCF for windrow composting.
    """

    MCF_COMPOSTING_STATIC_PILE: float = 0.005
    """
    The MCF for static pile composting.
    """

    MCF_COMPOSTING_WINDROW_LOW: float = 0.005
    """
    The MCF for windrow composting when the air temperature is below the lower bound temperature.
    """

    MCF_COMPOSTING_WINDROW_MEDIUM: float = 0.01
    """
    The MCF for windrow composting when the air temperature is between the lower and upper bound temperature.
    """

    MCF_COMPOSTING_WINDROW_HIGH: float = 0.015
    """
    The MCF for windrow composting when the air temperature is above the upper bound temperature.
    """

    POTENTIAL_METHANE_YIELD_OF_MANURE: float = 0.48
    """
    Potential methane yield of manure, (kg :math:`CH_4`/kg VS). This represents the potential
    amount of methane that can be produced per kilogram of volatile solids (VS) in manure.
    Default is set to 0.48.
    """

    DEFAULT_SLURRY_STORAGE_TEMPERATURE: float = 15.0
    """Default slurry storage temperature (:math:`^{\\circ}C`). Default is set to 15.0."""

    DEFAULT_VOLATILE_SOLIDS_FRACTION: float = 0.68
    """
    Default volatile solids fraction, (unitless, [0, 1]). This is the fraction of
    total solids that are volatile Default is set to 0.68.
    """

    CHEN_HASHIMOTO_KINETIC_CONSTANT_KCH: float = 3.1
    """
    Chen-Hashimoto kinetic constant (unitless). This constant is used in the
    Chen-Hashimoto equation to model the kinetic behaviour of the anaerobic digestion process.
    """

    SPECIFIC_GROWTH_RATE: float = 0.637
    """
    Specific growth rate (:math:`\\mu`m). This represents the rate at which the microbial population
    in the anaerobic digestion process increases.
    """

    DEFAULT_HOUSING_SPECIFIC_CONSTANT: float = 260.0  # s/m
    """
    Default housing specific constant (s/m). This constant may be used in calculations
    related to the housing conditions for animals. Default is set to 260.0 s/m.
    """

    DEFAULT_PH_FOR_HOUSING_AMMONIA: float = 7.7
    """Default pH for housing ammonia (unitless). Default is set to 7.7."""

    DEFAULT_PH_FOR_STORAGE_AMMONIA: float = 7.5
    """Default pH for storage ammonia (unitless). Default is set to 7.5."""

    OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
    """The half saturation constant of Oxygen gas (O2)"""

    DEFAULT_CARBON_AVAILABLE_IN_BEDDING: float = 0.35
    """
    Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35.
    """
    GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0
    """General temperature lower bound (:math:`^{\\circ}C`). Default is set to -40.0."""

    GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0
    """General temperature upper bound (:math:`^{\\circ}C`). Default is set to 60.0."""

    SOLID_AND_SEMI_SOLID_MANURE_HSC: float = 10.0
    """Housing specific constant for solid and semi-solid manure (s/m)."""

    SLURRY_MANURE_HSC: float = 19.0
    """Housing specific constant for slurry manure (s/m)."""

    LIQUID_MANURE_HSC: float = 4.1
    """Housing specific constant for liquid manure (s/m)."""

    SOLID_MANURE_THRESHOLD: float = 8.0
    """Dry matter threshold for classifying solid and semi-solid manure (unitless)."""

    SLURRY_MANURE_THRESHOLD: float = 5.0
    """Dry matter threshold for classifying slurry manure (unitless)."""

    DEFAULT_STORAGE_AREA_PER_ANIMAL: float = 1.0
    """Default storage area per animal (:math:`m^2`). Default is set to 1.0."""

    AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING: float = 0.5
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is tilled (unitless).
    """

    AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING: float = 0.25
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is not tilled (unitless).
    """

    LEACHING_COEFFICIENT: float = 0.035
    """Leaching coefficient used in the calculation of nitrogen loss in a compost bedded pack barn (unitless)."""

    NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING: float = 0.07
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is tilled (unitless).
    """

    NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING: float = 0.01
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a compost bedded pack barn
    when the bedding is not tilled (unitless).
    """

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING: float = 0.35
    """
    Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35.
    """

    NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS: float = 0.02
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in an open lot (unitless).
    """

    AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS: float = 0.36
    """
    Ammonia emission coefficient used for calculating nitrogen loss in an open lot (unitless).
    """

    DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE: float = 2.73e-3
    """
    The default effectiveness of microbial decomposition rate.
    """

    DEFAULT_COMPOSTING_DECOMPOSITION_TEMPERATURE: float = 60.0
    """
    The default decomposition temperature for composting.
    """

    DEFAULT_FIRST_ORDER_DECAYING_COEFFICIENT: float = 0.1
    """
    The default first order decaying coefficient.
    """

    DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
    """
    The default mole fraction of Oxygen.
    """

    DEFAULT_AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
    """
    The default ambient air mole fraction of Oxygen.
    """

    DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION: float = 0.65
    """
    The default effect of moisture on microbial decomposition.
    """

    FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.5,
        CompostingType.PASSIVE_WINDROW: 0.45,
        CompostingType.INTENSIVE_WINDROW: 0.5
    }

    FRACTION_NITROGEN_LOST_TO_LEACHING: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.06,
        CompostingType.PASSIVE_WINDROW: 0.04,
        CompostingType.INTENSIVE_WINDROW: 0.06
    }

    FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION: Dict[CompostingType, float] = {
        CompostingType.STATIC_PILE: 0.06,
        CompostingType.PASSIVE_WINDROW: 0.04,
        CompostingType.INTENSIVE_WINDROW: 0.06
    }
