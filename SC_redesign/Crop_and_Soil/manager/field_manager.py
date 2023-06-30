from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.util import Utility
from RUFAS.classes import Time, Weather, is_leap_year
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.manager.fertilizer_schedule import FertilizerSchedule
from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule
from SC_redesign.Crop_and_Soil.manager.tillage_schedule import TillageSchedule
from typing import Dict, List, Tuple

"""
This module is responsible for initializing the `Field` instances that will be simulated and providing an interface to
the `SimulationEngine` for executing daily and annual routines in the field module.
"""


class FieldManager:
    def __init__(self, fields_config: List[Dict[str, str]]):
        self.fields: List[Field] = []
        for field in fields_config:
            field_name, field_config = field.items()
            self.fields.append(self._setup_field(field_name, field_config))
        self.output_gatherer = OutputGatherer(fields=self.fields)

    def daily_update_routine(self, weather: Weather, time: Time) -> None:
        """
        This method will run the daily routine in the field, which will be calling the manage field method on each
        field.

        Parameters
        ----------
        weather: Weather
            A weather object that contains infos to be transformed to current weather
        time: Time
            Object containing the current year and day of the simulation.

        Notes
        -----
        Because different fields can have different latitudes, the day length has to be recalculated for each field.

        """
        for field in self.fields:
            month = FieldManager._date_conversion_month(time)
            current_weather = CurrentWeather.check_current_weather(weather=weather, month=month)
            field.manage_field(time, current_weather=current_weather)
        self.output_gatherer.send_daily_variables()

    def annual_update_routine(self) -> None:
        """
        This method will run the annual routine in the field, which will be calling the perform_annual_reset() method
        on each field.
        """
        for field in self.fields:
            field.perform_annual_reset()
        self.output_gatherer.send_annual_variables()

    @staticmethod
    def _date_conversion_month(time: Time) -> int:
        """
        Converts the day number into the corresponding month of the year.

        Parameters
        ----------
        time: Time
            Object containing the current year and day of the simulation.

        Returns
        -------
        int
            The corresponding month of the year.

        """
        days = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_days = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
        prev_month = 0
        if is_leap_year(time.calendar_year):
            for day in leap_days:
                if prev_month < time.day <= day:
                    return leap_days.index(day) + 1
                else:
                    prev_month = day
        else:
            for day in days:
                if prev_month < time.day <= day:
                    return days.index(day) + 1
                else:
                    prev_month = day

    @staticmethod
    def _date_conversion_day(time: Time) -> int:
        """
        Converts the day number into the corresponding day of the month.
        Parameters
        ----------
        time:
            Object containing the current year and day of the simulation.

        Returns
        -------
        int
        Corresponding day of the month.

        """
        days = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_days = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

        if is_leap_year(time.calendar_year):
            return time.day - leap_days[FieldManager._date_conversion_month(time) - 2]
        else:
            return time.day - days[FieldManager._date_conversion_month(time) - 2]

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
        fertilizer_config = management_config["fertilizer"]
        fertilizer_mixes = fertilizer_config["mixes"]
        fertilizer_schedule_name = field_name + "_fertilizer_schedule"
        fertilizer_schedule = FertilizerSchedule(name=fertilizer_schedule_name,
                                                 mix_names=fertilizer_config["mix"],
                                                 years=fertilizer_config["year"], days=fertilizer_config["day"],
                                                 nitrogen_masses=fertilizer_config["N_mass"],
                                                 phosphorus_masses=fertilizer_config["P_mass"],
                                                 application_depths=fertilizer_config["depth"],
                                                 surface_remainder_fractions=fertilizer_config["surface_percent"],
                                                 pattern_repeat=fertilizer_config["repeat"])

        manure_config = management_config["manure"]
        manure_schedule_name = field_name + "_manure_schedule"
        manure_schedule = ManureSchedule(name=manure_schedule_name,
                                         years=manure_config["year"],
                                         days=manure_config["day"],
                                         nitrogen_masses=manure_config["N_mass"],
                                         phosphorus_masses=manure_config["P_mass"],
                                         field_coverages=manure_config["cover_percent"],
                                         application_depths=manure_config["depth"],
                                         surface_remainder_fractions=manure_config["surface_percent"],
                                         pattern_repeat=manure_config["repeat"])

        tillage_config = management_config["tillage"]
        tillage_schedule_name = field_name + "_tillage_schedule"
        tillage_schedule = TillageSchedule(name=tillage_schedule_name,
                                           years=tillage_config["year"],
                                           days=tillage_config["day"],
                                           tillage_depths=tillage_config["depth"],
                                           incorporation_fractions=tillage_config["percent_incorporated"],
                                           mixing_fractions=tillage_config["percent_mixed"],
                                           pattern_repeat=tillage_config["repeat"])

        return fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule
