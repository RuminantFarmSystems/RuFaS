from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.manure.constants.general_constants import GeneralConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


@dataclass
class ManureHandlerDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure handler.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        urea: Urea concentration in manure, g/L.
        TAN: Total ammoniacal nitrogen, kg.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure, kg.
        VSd: Amount of degradable volatile solids, kg.
        VSnd: Amount of non-degradable volatile solids, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        CH4_housing: Methane emissions from ..., kg.  # TODO: Fill in.
        CO2_housing: Carbon dioxide emissions from ..., kg.  # TODO: Fill in.
        NH3_housing: Ammonia emissions from ..., kg.  # TODO: Fill in.
        manure_volume: Amount of raw manure, m^3.
        cleaning_water_volume: Volume of cleaning water used in main barn, m^3.
        total_bedding_volume: Total amount of bedding needed for all the animals in pen, m^3.
        total_water_volume_in_milking_parlor: Total volume of water used for
            lactating cows in the milking center, m^3.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        daily_volume: Same as total_daily_manure_volume. Used for satisfying the LiquidManurePortionProtocol.

    """
    pen_id: int = -1
    simulation_day: int = -1
    urea: float = 0.0
    TAN: float = 0.0
    N: float = 0.0
    TS: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = field(init=False)
    P: float = 0.0
    K: float = 0.0

    CH4_housing: float = 0.0
    CO2_housing: float = 0.0
    NH3_housing: float = 0.0

    manure_volume: float = 0.0
    cleaning_water_volume: float = 0.0
    total_bedding_volume: float = 0.0
    total_water_volume_in_milking_parlor: float = 0.0
    total_daily_manure_volume: float = field(init=False)
    daily_volume: float = field(init=False)  # To satisfy the LiquidManurePortionProtocol

    tempC: float = 0.0

    def __post_init__(self) -> None:
        """Calculate total volatile solids and total daily manure volume after initialization."""

        self.VS_total = self.VSd + self.VSnd
        self.cleaning_water_volume *= GeneralConstants.LITERS_TO_CUBIC_METERS
        self.total_water_volume_in_milking_parlor *= GeneralConstants.LITERS_TO_CUBIC_METERS

        self.total_daily_manure_volume = sum([
            self.manure_volume,
            self.cleaning_water_volume,
            self.total_bedding_volume,
            self.total_water_volume_in_milking_parlor,
        ])
        self.daily_volume = self.total_daily_manure_volume
