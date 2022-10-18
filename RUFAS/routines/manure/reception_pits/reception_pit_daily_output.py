from __future__ import annotations

from dataclasses import dataclass

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput


@dataclass
class ReceptionPitDailyOutput:
    """Daily output of a reception pit.

    Attributes
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        urea: Urea concentration in manure, g/L.
        TAN_s: Total ammonia nitrogen concentration, g/L.
        N_manure: Amount of nitrogen in manure, kg.
        TSd: Total amount of solids, kg.
        VSd: Amount of degradable volatile solids, kg.
        VSnd: Amount of non-degradable volatile solids, kg.
        VS_total: Total amount of volatile solids, kg.
        p_excrt_manure: Amount of phosphorus excreted in manure, kg.
        K_manure: Amount of potassium in manure, kg.
        raw_manure: Amount of raw manure, kg.
        cleaning_water: Volume of cleaning water used in main barn, L.
        total_bedding_mass: Total amount of bedding needed for all the animals in pen, kg.
        total_water_volume_in_milking_center: Total volume of water used for
            lactating cows in the milking center, L.
        total_daily_mass: Total amount of manure, bedding, and water combined, kg.

    """
    simulation_day: int = -1
    pen_id: int = -1
    urea: float = 0.0
    TAN_s: float = 0.0
    N_manure: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    total_bedding_mass: float = 0.0
    total_water_volume_in_milking_center: float = 0.0
    total_daily_mass: float = 0.0

    @staticmethod
    def get_instance(manure_handler_daily_output: ManureHandlerDailyOutput) -> ReceptionPitDailyOutput:
        """Create a ReceptionPitDailyOutput instance from a ManureHandlerDailyOutput instance.

        Notes:
            The daily output of a reception pit has less data than that of a manure handler.

        Args:
            manure_handler_daily_output: ManureHandlerDailyOutput instance.

        Returns:
            ReceptionPitDailyOutput instance.

        """

        reception_pit_daily_output = ReceptionPitDailyOutput()
        for var in vars(reception_pit_daily_output):
            if hasattr(manure_handler_daily_output, var):
                setattr(reception_pit_daily_output, var, getattr(manure_handler_daily_output, var))
        return reception_pit_daily_output
