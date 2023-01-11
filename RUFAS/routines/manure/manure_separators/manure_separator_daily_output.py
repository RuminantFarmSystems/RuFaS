from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol

om = OutputManager()


@dataclass
class ManureSeparatorDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure separator.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        final_solids_wet_mass: Total mass of the solids on wet-weight basis, kg.
        final_solids_wet_mass_volume: Total volume of the solids on wet-weight basis, m^3.

        solid_manure_total_solids: Total amount of solids in the separated solids, kg.
        solid_manure_total_volatile_solids: Total amount of volatile solids in the separated solids, kg.
        solid_manure_nitrogen: Amount of nitrogen in the separated solids, kg.
        solid_manure_phosphorus: Total amount of phosphorus in the separated solids, kg.
        solid_manure_potassium: Total amount of potassium in the separated solids, kg.

        liquid_manure_total_solids: Total amount of solids in the manure volume, kg.
        liquid_manure_total_volatile_solids: Total amount of volatile solids in the manure volume, kg.
        liquid_manure_nitrogen: Amount of nitrogen in the manure volume, kg.
        liquid_manure_total_ammoniacal_nitrogen: Total ammoniacal nitrogen in the manure volume, kg.
        liquid_manure_phosphorus: Total amount of phosphorus in the manure volume, kg.
        liquid_manure_potassium: Total amount of potassium in the manure volume, kg.

        final_daily_volume: Total manure volume after separation, m^3.
        liquid_manure_daily_volume: Same as final_daily_volume.
        Used for satisfying the LiquidManurePortionProtocol.

    """

    pen_id: int = -1
    simulation_day: int = -1
    total_daily_manure_volume: float = 0.0
    final_solids_wet_mass: float = 0.0
    final_solids_wet_mass_volume: float = field(init=False)

    solid_manure_total_solids: float = 0.0
    solid_manure_total_volatile_solids: float = 0.0
    solid_manure_nitrogen: float = 0.0
    solid_manure_phosphorus: float = 0.0
    solid_manure_potassium: float = 0.0

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_phosphorus: float = 0.0
    liquid_manure_potassium: float = 0.0

    final_daily_volume: float = field(init=False)
    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)

    def __post_init__(self):
        """Calculates the final daily volume and the final solids wet mass volume."""
        info_map = {
            'class': self.__class__.__name__,
            'function': self.__post_init__.__name__,
        }

        self.final_solids_wet_mass_volume = self.final_solids_wet_mass / \
            ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
        self.final_daily_volume = self.total_daily_manure_volume - \
            self.final_solids_wet_mass_volume
        self.liquid_manure_daily_volume = self.final_daily_volume

        om.add_variable("final_solids_wet_mass_volume",
                        self.final_solids_wet_mass_volume, info_map)
        om.add_variable("final_daily_volume",
                        self.final_daily_volume, info_map)
        om.add_variable("liquid_manure_daily_volume",
                        self.liquid_manure_daily_volume, info_map)
