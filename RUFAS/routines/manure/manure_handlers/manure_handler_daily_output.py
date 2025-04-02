from dataclasses import dataclass, field

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol
from RUFAS.units import MeasurementUnits


@dataclass
class ManureHandlerDailyOutput(LiquidManurePortionProtocol):
    """
    Daily output of a manure handler.

    Attribute
    ---------
    pen_id: int
        ID of the pen that this output is associated with.
    pen_id_unit: MeasurementUnits.UNITLESS
        Unit for pen_id
    simulation_day: int
        Number of days into the simulation.
    simulation_day_unit: MeasurementUnits.SIMULATION_DAY
        Unit for simulation_day
    manure_urea: float
        Urea concentration in manure, g/L.
    manure_urea_unit: MeasurementUnits.GRAMS_PER_LITER
        Unit for manure_urea
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen, kg.
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_total_ammoniacal_nitrogen
    liquid_manure_nitrogen: float
        Amount of nitrogen in manure, kg.
    liquid_manure_nitrogen_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_nitrogen
    liquid_manure_total_solids: float
        Total amount of solids from the manure, kg.
    liquid_manure_total_solids_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_total_solids
    liquid_manure_total_degradable_volatile_solids: float
        Amount of degradable volatile solids, kg.
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_total_degradable_volatile_solids
    liquid_manure_total_non_degradable_volatile_solids: float
        Amount of non-degradable volatile solids, kg.
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_total_non_degradable_volatile_solids
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids, kg.
    liquid_manure_total_volatile_solids_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_total_volatile_solids
    liquid_manure_phosphorus: float
        Amount of phosphorus excreted in manure, kg.
    liquid_manure_phosphorus_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_phosphorus
    liquid_manure_potassium: float
        Amount of potassium in manure, kg.
    liquid_manure_potassium_unit: MeasurementUnits.KILOGRAMS
        Unit for liquid_manure_potassium
    housing_methane: float
        Methane emissions from ..., kg.  # TODO: Fill in.
    housing_methane_unit: MeasurementUnits.KILOGRAMS
        Unit for housing_methane
    housing_carbon_dioxide: float
        Carbon dioxide emissions from ..., kg.  # TODO: Fill in.
    housing_carbon_dioxide_unit: MeasurementUnits.KILOGRAMS
        Unit for housing_carbon_dioxide
    housing_ammonia: float
        Ammonia emissions from ..., kg.  # TODO: Fill in.
    housing_ammonia_unit: MeasurementUnits.KILOGRAMS
        Unit for housing_ammonia
    manure_volume: float
        Amount of raw manure, m^3.
    manure_volume_unit: MeasurementUnits.KILOGRAMS
        Unit for manure_volume
    cleaning_water_volume: float
        Volume of cleaning water used in main barn, m^3.
    cleaning_water_volume_unit: MeasurementUnits.CUBIC_METERS
        Unit for cleaning_water_volume
    total_bedding_volume: float
        Total amount of bedding needed for all the animals in pen, m^3.
    total_bedding_volume_unit: MeasurementUnits.CUBIC_METERS
        Unit for total_bedding_volume
    total_bedding_mass : float, default 0.0
        Total amount of bedding needed for all the animals in pen, kg.
    total_bedding_mass_unit : MeasurementUnits, default MeasurementUnits.KILOGRAMS
        Unit for total_bedding_mass.
    organic_bedding_added_to_manure : float, default 0.0
        Amount of organic bedding material removed from the pen and added to the non-degradable volatile solids pool in
        the manure, kg.
    organic_bedding_added_to_manure_unit : MeasurementUnits, default MeasurementUnits.KILOGRAMS
        Unit for organic_bedding_added_to_manure.
    total_water_volume_in_milking_parlor: float
        Total volume of water used for lactating cows in the milking center, m^3.
    total_water_volume_in_milking_parlor_unit: MeasurementUnits.CUBIC_METERS
        Unit for total_water_volume_in_milking_parlor
    total_daily_manure_volume: float
        Total amount of manure, bedding, and water combined, m^3.
    total_daily_manure_volume_unit: MeasurementUnits.CUBIC_METERS
        Unit for total_daily_manure_volume
    liquid_manure_daily_volume: float
        Same as total_daily_manure_volume. Used for satisfying the LiquidManurePortionProtocol.
    liquid_manure_daily_volume_unit: MeasurementUnits.CUBIC_METERS
        Unit for liquid_manure_daily_volume
    air_temp: float
        Temperature of the current day, C.
    air_temp_unit: MeasurementUnits.DEGREES_CELSIUS
        Unit for air_temp.
    barn_temp: float
        Temperature in the barn, C.
    barn_temp_unit: MeasurementUnits.DEGREES_CELSIUS
        Unit for barn_temp.
    num_animals: int
        Number of animals in the pen each day.
    num_animals_unit: MeasurementUnits.UNITLESS
        Unit for num_animals
    """

    pen_id: int = -1
    pen_id_unit: MeasurementUnits = MeasurementUnits.UNITLESS

    simulation_day: int = -1
    simulation_day_unit: MeasurementUnits = MeasurementUnits.SIMULATION_DAY

    manure_urea: float = 0.0
    manure_urea_unit: MeasurementUnits = MeasurementUnits.GRAMS_PER_LITER

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_degradable_volatile_solids: float = 0.0
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_non_degradable_volatile_solids: float = 0.0
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_volatile_solids: float = field(init=False)
    liquid_manure_total_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    housing_methane: float = 0.0
    housing_methane_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    housing_carbon_dioxide: float = 0.0
    housing_carbon_dioxide_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    housing_ammonia: float = 0.0
    housing_ammonia_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    manure_volume: float = 0.0
    manure_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    cleaning_water_volume: float = 0.0
    cleaning_water_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    total_bedding_volume: float = 0.0
    total_bedding_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    total_bedding_mass: float = 0.0
    total_bedding_mass_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    organic_bedding_added_to_manure: float = 0.0
    organic_bedding_added_to_manure_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    total_water_volume_in_milking_parlor: float = 0.0
    total_water_volume_in_milking_parlor_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    total_daily_manure_volume: float = field(init=False)
    total_daily_manure_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)
    liquid_manure_daily_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    air_temperature: float | None = 0.0
    air_temperature_unit: MeasurementUnits = MeasurementUnits.DEGREES_CELSIUS

    barn_temperature: float = 0.0
    barn_temperature_unit: MeasurementUnits = MeasurementUnits.DEGREES_CELSIUS

    num_animals: int = -1
    num_animals_unit: MeasurementUnits = MeasurementUnits.UNITLESS

    def __post_init__(self) -> None:
        """Calculates total volatile solids and total daily manure volume after initialization."""

        self.liquid_manure_total_volatile_solids = (
            self.liquid_manure_total_degradable_volatile_solids
            + self.liquid_manure_total_non_degradable_volatile_solids
        )
        self.cleaning_water_volume *= GeneralConstants.LITERS_TO_CUBIC_METERS
        self.total_water_volume_in_milking_parlor *= GeneralConstants.LITERS_TO_CUBIC_METERS

        self.total_daily_manure_volume = sum(
            [
                self.manure_volume,
                self.cleaning_water_volume,
                self.total_bedding_volume,
                self.total_water_volume_in_milking_parlor,
            ]
        )
        self.liquid_manure_daily_volume = self.total_daily_manure_volume
