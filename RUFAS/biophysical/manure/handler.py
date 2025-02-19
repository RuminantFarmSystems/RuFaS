from abc import ABC

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time


class Handler(Processor, ABC):
    def __init__(self, is_housing_emissions_calculator: bool):
        super().__init__(is_housing_emissions_calculator)
        self.manure_water = 0
        self.manure_total_ammoniacal_nitrogen = 0
        self.manure_nitrogen = 0
        self.manure_phosphorus = 0
        self.manure_potassium = 0
        self.manure_ash = 0
        self.manure_non_degradable_volatile_solids = 0
        self.manure_degradable_volatile_solids = 0
        self.manure_total_solids = 0
        self.manure_total_volatile_solids = 0
        self.manure_mass = 0
        self.manure_volume = 0
        self.pen_manure_data = None

    def receive_manure(self, manure: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
            The manure to be processed.

        Raises
        ------
        ValueError
            If the ManureStream is incompatible with the processor receiving it.

        """
        if manure.pen_manure_data is None:
            om = OutputManager()
            info_map = {"class": Handler.__class__.__name__, "function": Handler.receive_manure.__name__}
            om.add_error(
                "None type PenManureData", "The received ManureStream has a None type PenManureData.", info_map
            )
            raise TypeError("TypeError: Handler received 'NoneType' object for PenManureData in ManureStream")

        self.manure_water = manure.water
        self.manure_total_ammoniacal_nitrogen = manure.ammoniacal_nitrogen
        self.manure_nitrogen = manure.nitrogen
        self.manure_phosphorus = manure.phosphorus
        self.manure_potassium = manure.potassium
        self.manure_ash = manure.ash
        self.manure_non_degradable_volatile_solids = manure.non_degradable_volatile_solids
        self.manure_degradable_volatile_solids = manure.degradable_volatile_solids
        self.manure_total_solids = manure.total_solids
        self.manure_total_volatile_solids = manure.total_volatile_solids
        self.manure_mass = manure.mass
        self.manure_volume = manure.volume
        self.pen_manure_data = manure.pen_manure_data

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : Time
            Time instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information. If the processor is a separator, the classifications are "solid" and "liquid". Otherwise
            the only classification is "manure".

        """
        pass
