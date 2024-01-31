from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)
from dataclasses import dataclass
from dataclasses import field

from RUFAS.general_constants import GeneralConstants


@dataclass
class ManureHandlerDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure handler.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        manure_urea: Urea concentration in manure, g/L.
        liquid_manure_total_ammoniacal_nitrogen: Total ammoniacal nitrogen, kg.
        liquid_manure_nitrogen: Amount of nitrogen in manure, kg.
        liquid_manure_total_solids: Total amount of solids from the manure, kg.
        manure_degradable_volatile_solids: Amount of degradable volatile solids, kg.
        manure_non_degradable_volatile_solids: Amount of non-degradable volatile solids, kg.
        liquid_manure_total_volatile_solids: Total amount of volatile solids, kg.
        liquid_manure_phosphorus: Amount of phosphorus excreted in manure, kg.
        liquid_manure_potassium: Amount of potassium in manure, kg.
        housing_methane: Methane emissions from ..., kg.  # TODO: Fill in. - Issue #1119
        housing_carbon_dioxide: Carbon dioxide emissions from ..., kg.  # TODO: Fill in. - Issue #1119
        housing_ammonia: Ammonia emissions from ..., kg.  # TODO: Fill in. - Issue #1119
        manure_volume: Amount of raw manure, m^3.
        cleaning_water_volume: Volume of cleaning water used in main barn, m^3.
        total_bedding_volume: Total amount of bedding needed for all the animals in pen, m^3.
        total_water_volume_in_milking_parlor: Total volume of water used for
            lactating cows in the milking center, m^3.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        liquid_manure_daily_volume: Same as total_daily_manure_volume. Used for satisfying the
        LiquidManurePortionProtocol.
        tempC: Temperature of the current day, C.

    """

    pen_id: int = -1
    simulation_day: int = -1
    manure_urea: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_nitrogen: float = 0.0
    liquid_manure_total_solids: float = 0.0
    manure_degradable_volatile_solids: float = 0.0
    manure_non_degradable_volatile_solids: float = 0.0
    liquid_manure_total_volatile_solids: float = field(init=False)
    liquid_manure_phosphorus: float = 0.0
    liquid_manure_potassium: float = 0.0

    housing_methane: float = 0.0
    housing_carbon_dioxide: float = 0.0
    housing_ammonia: float = 0.0

    manure_volume: float = 0.0
    cleaning_water_volume: float = 0.0
    total_bedding_volume: float = 0.0
    total_bedding_mass: float = 0.0
    total_water_volume_in_milking_parlor: float = 0.0
    total_daily_manure_volume: float = field(init=False)
    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)

    tempC: float = 0.0

    def __post_init__(self) -> None:
        """Calculates total volatile solids and total daily manure volume after initialization."""

        self.liquid_manure_total_volatile_solids = (
            self.manure_degradable_volatile_solids
            + self.manure_non_degradable_volatile_solids
        )
        self.cleaning_water_volume *= GeneralConstants.LITERS_TO_CUBIC_METERS
        self.total_water_volume_in_milking_parlor *= (
            GeneralConstants.LITERS_TO_CUBIC_METERS
        )

        self.total_daily_manure_volume = sum(
            [
                self.manure_volume,
                self.cleaning_water_volume,
                self.total_bedding_volume,
                self.total_water_volume_in_milking_parlor,
            ]
        )
        self.liquid_manure_daily_volume = self.total_daily_manure_volume
