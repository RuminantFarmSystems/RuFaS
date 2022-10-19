from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.manure.constants.constants import ManureManagementConstants


@dataclass
class ManureHandlerDailyOutput:
    """Daily output of a manure handler.

    Attributes:
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        urea: Urea concentration in manure, g/L.
        TAN: Total ammonia nitrogen concentration, g/L.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure, kg.
        VSd: Amount of degradable volatile solids, kg.
        VSnd: Amount of non-degradable volatile solids, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        manure_volume: Amount of raw manure, m^3.
        cleaning_water_volume: Volume of cleaning water used in main barn, m^3.
        total_bedding_volume: Total amount of bedding needed for all the animals in pen, m^3.
        total_water_volume_in_milking_center: Total volume of water used for
            lactating cows in the milking center, m^3.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.

    """
    simulation_day: int = -1
    pen_id: int = -1
    urea: float = 0.0
    TAN: float = 0.0
    N: float = 0.0
    TS: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = field(init=False)
    P: float = 0.0
    K: float = 0.0

    manure_volume: float = 0.0
    cleaning_water_volume: float = 0.0
    total_bedding_volume: float = 0.0
    total_water_volume_in_milking_center: float = 0.0
    total_daily_manure_volume: float = field(init=False)

    def __post_init__(self) -> None:
        """Calculate total volatile solids and total daily manure volume after initialization."""

        self.VS_total = self.VSd + self.VSnd
        self.cleaning_water_volume *= ManureManagementConstants.LITERS_TO_CUBIC_METERS
        self.total_water_volume_in_milking_center *= ManureManagementConstants.LITERS_TO_CUBIC_METERS

        self.total_daily_manure_volume = sum([
            self.manure_volume,
            self.cleaning_water_volume,
            self.total_bedding_volume,
            self.total_water_volume_in_milking_center,
        ])
