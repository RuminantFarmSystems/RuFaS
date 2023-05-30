from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol
from dataclasses import dataclass
from dataclasses import field

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager

om = OutputManager()


@dataclass
class ManureHandlerDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure handler."""

    pen_id: int = -1
    """ID of the pen that this output is associated with."""

    simulation_day: int = -1
    """Number of days into the simulation."""

    manure_urea: float = 0.0
    """Urea concentration in manure, g/L."""

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    """Total ammoniacal nitrogen, kg."""

    liquid_manure_nitrogen: float = 0.0
    """Amount of nitrogen in manure, kg."""

    liquid_manure_total_solids: float = 0.0
    """Total amount of solids from the manure, kg."""

    manure_degradable_volatile_solids: float = 0.0
    """Amount of degradable volatile solids, kg."""

    manure_non_degradable_volatile_solids: float = 0.0
    """Amount of non-degradable volatile solids, kg."""

    liquid_manure_total_volatile_solids: float = field(init=False)
    """Total amount of volatile solids, kg."""

    liquid_manure_phosphorus: float = 0.0
    """Amount of phosphorus excreted in manure, kg."""

    liquid_manure_potassium: float = 0.0
    """Amount of potassium in manure, kg."""

    housing_methane: float = 0.0
    """Housing methane emissions, kg."""

    housing_carbon_dioxide: float = 0.0
    """Housing carbon dioxide emissions, kg."""

    housing_ammonia: float = 0.0
    """Housing ammonia emissions, kg."""

    manure_volume: float = 0.0
    """Amount of raw manure, :math:`m^3`."""

    cleaning_water_volume: float = 0.0
    """Volume of cleaning water used in main barn, :math:`m^3`."""

    total_bedding_volume: float = 0.0
    """Total amount of bedding needed for all the animals in pen, :math:`m^3`."""

    total_water_volume_in_milking_parlor: float = 0.0
    """Total volume of water used for lactating cows in the milking center, :math:`m^3`."""

    total_daily_manure_volume: float = field(init=False)
    """Total amount of manure, bedding, and water combined, :math:`m^3`."""

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)
    """Same as total_daily_manure_volume. Used for satisfying the LiquidManurePortionProtocol."""

    tempC: float = 0.0
    """Temperature of the current day, :math:`^{\circ}C`."""

    def __post_init__(self) -> None:
        """Calculates total volatile solids and total daily manure volume after initialization."""
        info_map = {"class": self.__class__.__name__,
                    "function": self.__post_init__.__name__,
                    }

        self.liquid_manure_total_volatile_solids = (self.manure_degradable_volatile_solids +
                                                    self.manure_non_degradable_volatile_solids)
        self.cleaning_water_volume *= GeneralConstants.LITERS_TO_CUBIC_METERS
        self.total_water_volume_in_milking_parlor *= GeneralConstants.LITERS_TO_CUBIC_METERS

        self.total_daily_manure_volume = sum([
            self.manure_volume,
            self.cleaning_water_volume,
            self.total_bedding_volume,
            self.total_water_volume_in_milking_parlor,
        ])
        self.liquid_manure_daily_volume = self.total_daily_manure_volume

        om.add_variable("liquid_manure_total_volatile_solids",
                        self.liquid_manure_total_volatile_solids, info_map)
        om.add_variable("cleaning_water_volume",
                        self.cleaning_water_volume, info_map)
        om.add_variable("total_water_volume_in_milking_parlor",
                        self.total_water_volume_in_milking_parlor, info_map)
        om.add_variable("total_daily_manure_volume",
                        self.total_daily_manure_volume, info_map)
        om.add_variable("liquid_manure_daily_volume",
                        self.liquid_manure_daily_volume, info_map)
