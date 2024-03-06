from typing import Optional, Dict

from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)
from dataclasses import dataclass

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

    pen_id: int = -1
    pen_id_unit: str = "unitless"

    simulation_day: int = -1
    simulation_day_unit: str = "simulation days"

    manure_urea: float = 0.0
    manure_urea_unit: str = "g/L"

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: str = "kg"

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: str = "kg"

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: str = "kg"

    manure_degradable_volatile_solids: float = 0.0
    manure_degradable_volatile_solids_unit: str = "kg"

    manure_non_degradable_volatile_solids: float = 0.0
    manure_non_degradable_volatile_solids_unit: str = "kg"

    liquid_manure_total_volatile_solids: Optional[float] = None
    liquid_manure_total_volatile_solids_unit: str = "kg"

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: str = "kg"

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: str = "kg"

    housing_methane: float = 0.0
    housing_methane_unit: str = "kg"

    housing_carbon_dioxide: float = 0.0
    housing_carbon_dioxide_unit: str = "kg"

    housing_ammonia: float = 0.0
    housing_ammonia_unit: str = "kg"

    manure_volume: float = 0.0
    manure_volume_unit: str = "m^3"

    cleaning_water_volume: float = 0.0
    cleaning_water_volume_unit: str = "m^3"

    total_bedding_volume: float = 0.0
    total_bedding_volume_unit: str = "m^3"

    total_bedding_mass: float = 0.0
    total_bedding_mass_unit: str = "kg"

    total_water_volume_in_milking_parlor: float = 0.0
    total_water_volume_in_milking_parlor_unit: str = "m^3"

    total_daily_manure_volume: Optional[float] = None
    total_daily_manure_volume_unit: str = "m^3"

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: Optional[float] = None
    liquid_manure_daily_volume_unit: str = "m^3"

    tempC: float = 0.0
    tempC_unit: str = "°C"

    num_animals: int = -1
    num_animals_unit: str = "unitless"

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

    @property
    def units_dict(self) -> Dict[str, str]:
        return {
            k: v
            for unit in ({k: v} for (k, v) in self.__dict__.items() if k.endswith("_unit"))
            for (k, v) in unit.items()
        }
