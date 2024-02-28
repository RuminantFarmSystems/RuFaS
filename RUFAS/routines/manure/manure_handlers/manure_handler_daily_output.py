from RUFAS.routines.manure.constants_and_units.datatype_with_unit import FloatWithUnit, IntWithUnit, FieldWithUnit
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)
from dataclasses import dataclass
from dataclasses import field

from RUFAS.general_constants import GeneralConstants


@dataclass
class ManureHandlerDailyOutput(LiquidManurePortionProtocol):
    """
    Daily output of a manure handler.

    Attribute
    ---------
    pen_id: int
        ID of the pen that this output is associated with.
    simulation_day: int
        Number of days into the simulation.
    manure_urea: float
        Urea concentration in manure, g/L.
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen, kg.
    liquid_manure_nitrogen: float
        Amount of nitrogen in manure, kg.
    liquid_manure_total_solids: float
        Total amount of solids from the manure, kg.
    manure_degradable_volatile_solids: float
        Amount of degradable volatile solids, kg.
    manure_non_degradable_volatile_solids: float
        Amount of non-degradable volatile solids, kg.
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids, kg.
    liquid_manure_phosphorus: float
        Amount of phosphorus excreted in manure, kg.
    liquid_manure_potassium: float
        Amount of potassium in manure, kg.
    housing_methane: float
        Methane emissions from ..., kg.  # TODO: Fill in.
    housing_carbon_dioxide: float
        Carbon dioxide emissions from ..., kg.  # TODO: Fill in.
    housing_ammonia: float
        Ammonia emissions from ..., kg.  # TODO: Fill in.
    manure_volume: float
        Amount of raw manure, m^3.
    cleaning_water_volume: float
        Volume of cleaning water used in main barn, m^3.
    total_bedding_volume: float
        Total amount of bedding needed for all the animals in pen, m^3.
    total_water_volume_in_milking_parlor: float
        Total volume of water used for lactating cows in the milking center, m^3.
    total_daily_manure_volume: float
        Total amount of manure, bedding, and water combined, m^3.
    liquid_manure_daily_volume: float
        Same as total_daily_manure_volume. Used for satisfying the LiquidManurePortionProtocol.
    tempC: float
        Temperature of the current day, C.
    num_animals: int
        Number of animals in the pen each day.
    """

    pen_id: IntWithUnit = IntWithUnit(-1, unit="unitless")

    simulation_day: IntWithUnit = IntWithUnit(-1, unit="simulation days")

    manure_urea: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    manure_degradable_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    manure_non_degradable_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_total_volatile_solids: FloatWithUnit = FieldWithUnit(init=False, unit="kg")

    liquid_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    housing_methane: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    housing_carbon_dioxide: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    housing_ammonia: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    manure_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    cleaning_water_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    total_bedding_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    total_bedding_mass: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    total_water_volume_in_milking_parlor: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")

    total_daily_manure_volume: FloatWithUnit = field(init=False)
    total_daily_manure_volume.unit = "m^3"

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: FloatWithUnit = field(init=False)
    liquid_manure_daily_volume.unit = "m^3"

    tempC: FloatWithUnit = 0.0
    tempC.unit = "°C"

    num_animals: IntWithUnit = -1
    num_animals.unit = "uniteless"

    def __post_init__(self) -> None:
        """Calculates total volatile solids and total daily manure volume after initialization."""

        self.liquid_manure_total_volatile_solids = (
            self.manure_degradable_volatile_solids + self.manure_non_degradable_volatile_solids
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
