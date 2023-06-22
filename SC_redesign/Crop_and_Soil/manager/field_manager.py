from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time
from RUFAS.util import Utility
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.manager.fertilizer_schedule import FertilizerSchedule
from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule
from SC_redesign.Crop_and_Soil.manager.tillage_schedule import TillageSchedule
from typing import Dict, List, Tuple


class FieldManager:
    def __init__(self, fields_config: List[Dict[str, str]]):
        self.fields: List[Field] = []
        for field in fields_config:
            field_name, field_config = field.items()
            self.fields.append(self._setup_field(field_name, field_config))
        self.om = OutputGatherer(fields=self.fields)

    def daily_update_routine(self, current_weather: CurrentWeather, time: Time):
        for field in self.fields:
            field.manage_field(time, current_weather)
        self.om.send_daily_variables()

    def annual_update_routine(self):
        for field in self.fields:
            field.perform_annual_reset()
        self.om.send_annual_variables()

    @staticmethod
    def _setup_field(field_name: str, field_config: Dict[str, str]) -> Field:
        """

        Parameters
        ----------
        field_name : str
            The name of the field being initialized.
        field_config : Dict[str, str]
            Contains the paths to input data files for soil profile, crop management, and farm management.

        Returns
        -------
        Field
            A `Field` instance configured with the specified input data

        """
        input_directory = Utility.get_base_dir() / 'input'

        management_config = \
            Utility.read_json_file(input_directory / 'field_management' / field_config['field_management'])

        available_fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule = \
            FieldManager._setup_management(field_name, management_config)
        fertilizer_events = fertilizer_schedule.generate_fertilizer_events()
        manure_events = manure_schedule.generate_manure_events()
        tillage_events = tillage_schedule.generate_tillage_events()

        return Field(tillage_events=tillage_events, fertilizer_events=fertilizer_events,
                     fertilizer_mixes=available_fertilizer_mixes, manure_events=manure_events)

    @staticmethod
    def _setup_management(field_name: str,
                          management_config: Dict) -> Tuple[Dict, FertilizerSchedule, ManureSchedule, TillageSchedule]:
        """
        Creates all the Schedule instances needed to manage the farm.

        Parameters
        ----------
        field_name : str
            The name of the field managed with this fertilizer schedule.
        management_config : Dict
            Contains the specifications for how this field will be managed.

        Returns
        -------
        Tuple
            Dictionary containing the available fertilizer mixes for this field, a FertilizerSchedule instance, a
            ManureSchedule instance, and a TillageSchedule instance.

        """
        fertilizer_config = management_config.get("fertilizer")
        fertilizer_mixes = fertilizer_config.get("mixes")
        fertilizer_schedule_name = field_name + "_fertilizer_schedule"
        fertilizer_schedule = FertilizerSchedule(name=fertilizer_schedule_name,
                                                 mix_names=fertilizer_config.get("mix"),
                                                 years=fertilizer_config.get("year"), days=fertilizer_config.get("day"),
                                                 nitrogen_masses=fertilizer_config.get("N_mass"),
                                                 phosphorus_masses=fertilizer_config.get("P_mass"),
                                                 application_depths=fertilizer_config.get("depth"),
                                                 surface_remainder_fractions=fertilizer_config.get("surface_percent"),
                                                 pattern_repeat=fertilizer_config.get("repeat"))

        manure_config = management_config.get("manure")
        manure_schedule_name = field_name + "_manure_schedule"
        manure_schedule = ManureSchedule(name=manure_schedule_name,
                                         years=manure_config.get("year"),
                                         days=manure_config.get("day"),
                                         nitrogen_masses=manure_config.get("N_mass"),
                                         phosphorus_masses=manure_config.get("P_mass"),
                                         field_coverages=manure_config.get("cover_percent"),
                                         application_depths=manure_config.get("depth"),
                                         surface_remainder_fractions=manure_config.get("surface_percent"),
                                         pattern_repeat=manure_config.get("repeat"))

        tillage_config = management_config.get("tillage")
        tillage_schedule_name = field_name + "_tillage_schedule"
        tillage_schedule = TillageSchedule(name=tillage_schedule_name,
                                           years=tillage_config.get("year"),
                                           days=tillage_config.get("day"),
                                           tillage_depths=tillage_config.get("depth"),
                                           incorporation_fractions=tillage_config.get("percent_incorporated"),
                                           mixing_fractions=tillage_config.get("percent_mixed"),
                                           pattern_repeat=tillage_config.get("repeat"))

        return fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule
