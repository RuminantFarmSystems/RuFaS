from RUFAS.biophysical.manure.storage.composting_type import CompostingType
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


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

    METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO: float = 9.25
    """
    The mass conversion factor from methane to methane and carbon dioxide emitted from stored manure, based on a molar
    ratio of 1:3 (methane : carbon dioxide).
    """

    STORAGE_RESISTANCE = 4.1
    """
    Resistance value utilized in calculation of ammonia emission from manure stored in slurry storage outdoor,
    slurry storage underfloor, or anaerobic lagoon (s/m).
    """

    DEFAULT_PH_FOR_AMMONIA: float = 7.5
    """Default pH for ammonia (unitless)."""

    LEACHING_COEFFICIENT: float = 0.035
    """Leaching coefficient used in the calculation of leaching N loss in a compost bedded pack and open lot
    (unitless)."""

    DEFAULT_LAYER_TEMPERATURE: float = 30
    """The default layer temperature for open lot and compost bedded pack barn."""

    HOUSING_HSC = 260.0
    """
    Default housing specific constant (s/m). This constant may be used in calculations
    related to the housing conditions for animals. Default is set to 260.0 s/m.
    """

    DEFAULT_PH_FOR_HOUSING_AMMONIA: float = 7.7
    """Default pH for housing ammonia (unitless). Default is set to 7.7."""

    MILKING_FRESH_WATER_USE_RATE: float = 30.0
    """
    The milking fresh water use rate for each animal (L/animal/day).
    """


    CARBON_DIOXIDE_DENSITY: float = 1.716
    """
    Unit conversion factor for carbon dioxide generated from anaerobic digestion at 1 atm of pressure and 37.5C (kg / m^3).
    """

    CARBON_DIOXIDE_TO_METHANE_RATIO: float = 4 / 6
    """
    Volumetric ratio of carbon dioxide to methane generated during anaerobic digestion (m^3 carbon dioxide / m^3 methane).
    """

    METHANE_DENSITY: float = 0.629
    """
    Unit conversion factor for methane generated from an anaerobic digester at 1 atm of pressure and 37.5 C (kg / m^3).
    """

    METHANE_ENERGY_DENSITY: float = 55.0
    """Methane energy density (MJ / kg)."""

    MINIMUM_INFLUENT_TEMPERATURE = 4.0
    """The lower temperature bound for manure flowing into an anaerobic digester (degrees C)."""

    TAN_INCREASE_FACTOR = 1.60
    """Factor by which total ammoniacal nitrogen content is increased by the anaerobic digestion process (unitless)."""

    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING: dict[StorageCover, float] = {
        StorageCover.COVER: 0.005,
        StorageCover.CRUST: 0.005,
        StorageCover.NO_COVER: 0.0,
        StorageCover.COVER_AND_FLARE: 0.005,
    }
    """
    Mapping of storage cover types to the nitrous oxide emissions factor associated with that cover type (kg nitrous oxide N
    / kg manure N).
    """

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
    turning. For Open Lot, this refers to lot harrowing. For Compost Bedded Pack barn, this refers to pack tillage."""

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
