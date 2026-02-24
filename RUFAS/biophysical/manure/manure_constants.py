from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


class ManureConstants:
    """
    A class to store constants for manure management.
    """

    # General manure constants
    LIQUID_MANURE_DENSITY = 1000
    """The density of liquid manure (kg/:math:`m^3`)."""

    SLURRY_MANURE_DENSITY = 990
    """The density of slurry manure (kg/:math:`m^3`)."""

    SOLID_MANURE_DENSITY = 700
    """The density of solid manure (kg/:math:`m^3`)."""

    # Handler-related constants
    HOUSING_SPECIFIC_CONSTANT = 260.0
    """
    Default housing specific constant (s/m) used in the calculation of ammonia emissions from manure deposited in
     freestall or tiestall barns. Default is set to 260.0 s/m.
    """

    DEFAULT_PH_FOR_HOUSING_AMMONIA: float = 7.7
    """
    Default pH for manure on tiestall or freestall barn floors (unitless).
    """

    MILKING_FRESH_WATER_USE_RATE: float = 30.0
    """
    The milking fresh water use rate for each animal (L/animal/day).
    """

    # Anaerobic digestion-related constants
    METHANE_MOLAR_MASS = 16.04
    """Molar mass of methane (g)."""

    CARBON_DIOXIDE_MOLAR_MASS = 44.01
    """Molar mass of carbon dioxide (g)."""

    CARBON_DIOXIDE_TO_METHANE_RATIO: float = 4 / 6
    """Volumetric ratio of carbon dioxide to methane generated during anaerobic digestion
     (m^3 carbon dioxide / m^3 methane)."""

    TAN_INCREASE_FACTOR = 1.60
    """Factor by which total ammoniacal nitrogen content is increased by the anaerobic digestion process (unitless)."""

    # Liquid manure storage-related constants
    VS_TO_METHANE_LOSS_RATIO: float = 6.665
    """
    Factor to determine kg of VS degraded per kg CH4 emitted from stored manure (kg VS / kg CH4).
    """

    METHANE_DESTRUCTION_EFFICIENCY = 81
    """
    The percentage of methane destroyed in systems using a cap and flare (percent).
    """

    STORAGE_RESISTANCE = 4.1
    """
    Resistance value utilized in calculation of ammonia emission from manure stored in slurry storage outdoor,
    slurry storage underfloor, or anaerobic lagoon (s/m).
    """

    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING: dict[StorageCover, float] = {
        StorageCover.COVER: 0.005,
        StorageCover.CRUST: 0.005,
        StorageCover.NO_COVER: 0.0,
        StorageCover.COVER_AND_FLARE: 0.005,
    }
    """
    Mapping of storage cover types to the nitrous oxide emissions factor associated with that cover type (kg nitrous
    oxide N / kg manure N).
    """

    DEFAULT_STORED_MANURE_PH: float = 7.5
    """Default pH of manure in slurry storage or anaerobic lagoon (unitless)."""

    ACTIVATION_ENERGY: float = 81_000.0
    """
    Apparent activation energy of methanogenesis in dairy manure (joules per mole, J/mol). The activation energy is the
     minimum energy that must be available to microbes for methanogenesis to occur.
    """

    NATURAL_LOG_ARRHENIUS_CONSTANT: float = 30.7
    """Natural log of the Arrhenius parameter used in determination of methane emissions from stored slurry or liquid
     manure (g methane / kg manure Volatile Solids / hour)."""

    # Solid manure storage-related constants
    DEFAULT_LAG_TIME = 2
    """Default lag time used in the calculation of the carbon decomposition rate (days). Default is set to 2."""

    LEACHING_COEFFICIENT: float = 0.035
    """Leaching coefficient used in the calculation of leaching N loss in a bedded pack and open lot
    (unitless)."""

    DEFAULT_LAYER_TEMPERATURE: float = 30
    """The default layer temperature for open lot and bedded pack."""

    NITROUS_OXIDE_COEFFICIENT_WITH_TILLED_BEDDING: float = 0.07
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a bedded pack
    when the bedding is tilled (unitless).
    """

    NITROUS_OXIDE_COEFFICIENT_WITH_UNTILLED_BEDDING: float = 0.01
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in a bedded pack
    when the bedding is not tilled (unitless).
    """

    AMMONIA_EMISSION_COEFFICIENT_WITH_TILLED_BEDDING: float = 0.5
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a bedded pack
    when the bedding is tilled (unitless).
    """

    AMMONIA_EMISSION_COEFFICIENT_WITH_UNTILLED_BEDDING: float = 0.25
    """
    Ammonia emission coefficient used for calculating nitrogen loss in a bedded pack
    when the bedding is not tilled (unitless).
    """

    MCF_COMPOSTING_STATIC_PILE: float = 0.005
    """The MCF for static pile composting."""

    MCF_LOWER_BOUND_TEMPERATURE: float = 15.0
    """The lower bound temperature for determining MCF for windrow composting."""

    MCF_UPPER_BOUND_TEMPERATURE: float = 25.0
    """The upper bound temperature for determining MCF for windrow composting."""

    MCF_COMPOSTING_WINDROW_LOW: float = 0.005
    """The MCF for windrow composting when the air temperature is below the lower bound temperature."""

    MCF_COMPOSTING_WINDROW_MEDIUM: float = 0.01
    """The MCF for windrow composting when the air temperature is between the lower and upper bound temperature."""

    MCF_COMPOSTING_WINDROW_HIGH: float = 0.015
    """The MCF for windrow composting when the air temperature is above the upper bound temperature."""

    AMMONIA_EMISSION_COEFFICIENT_IN_OPEN_LOTS: float = 0.36
    """
    Ammonia emission coefficient used for calculating nitrogen loss in an open lot (unitless).
    """

    NITROUS_OXIDE_COEFFICIENT_IN_OPEN_LOTS: float = 0.02
    """
    Nitrous oxide coefficient used for calculating nitrogen loss in an open lot (unitless).
    """

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD: float = 0.5
    """Default carbon content (percent by mass) of manure degradable volatile solids (unitless, [0, 1])."""

    DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND: float = 0.35
    """Default carbon content (percent by mass) of manure non-degradable volatile solids (unitless, [0, 1])."""

    DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION: float = 0.65
    """The default effect of moisture on microbial decomposition."""

    DEFAULT_DAYS_SINCE_LAST_MIXING: int = 1
    """Default days since the previous mixing event (days). Default is set to 1. For Composting, this refers to compost
    turning. For Open Lot, this refers to lot harrowing. For Bedded Pack, this refers to pack tillage."""

    DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 1.0
    """
    Rate correcting factor for degradable volatile solids, used in calculation of slurry storage methane emission
    (unitless).
    """

    NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 0.01
    """
    Rate correcting factor for non-degradable volatile solids, used in calculation of slurry storage methane emission
    (unitless).
    """

    EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE: float = 2.37e-3
    """The rate of effectiveness of microbial decomposition."""

    FIRST_ORDER_DECAYING_COEFFICIENT: float = 0.1
    """The first order decaying coefficient."""

    DECOMPOSITION_TEMPERATURE: float = 60.0
    """The temperature of the inner decomposing material layer at which microbial growth and decomposition is
    maximized (C)."""

    OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
    """The half saturation constant of Oxygen gas (O2)"""

    MCF_CONSTANT_A: float = 0.0625
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the open lot
    Methane Conversion Factor (MCF) calculation. The coefficient scales the ambient barn temperature.
    """

    MCF_CONSTANT_B: float = 0.25
    """
    Parameter estimate (unitless) of a regression using IPCC data (2006) used in the open lot
    Methane Conversion Factor (MCF) calculation. The coefficient is a constant offset.
    """

    DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
    """The default mole fraction of oxygen in the air within the decomposing material layer."""

    ANAEROBIC_LAGOON_MANURE_RETENTION: float = 0.1
    """The manure retention proportion in the anaerobic lagoon (fraction)."""

    MANURE_DAMPING_FACTOR: float = 0.65
    """Unitless factor representing the reduction of the amplitude of manure temperature in the sin/cosin equation
     compared to air temperature amplitude (unitless)."""

    MANURE_TEMPERATURE_LAG: int = 30
    """
    Number of days that elapse between peak air temperature and manure temperature. Note that this constant is
    subtracted in the equation for calculation daily air temperature; a positive value for this constant indicates
    manure temperature peaks later than air temperature, whereas a negative value indicates manure temperature peaks
    earlier than air temperature (days).
    """

    ANAEROBIC_LAGOON_MINIMUM_TEMPERATURE: float = 1.0
    """The minimum temperature of manure stored in an anaerobic lagoon (°C)."""

    SLURRY_OUTDOOR_MINIMUM_TEMPERATURE: float = -20.0
    """The minimum temperature of manure stored in slurry storage outdoors (°C)."""
