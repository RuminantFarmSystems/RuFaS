from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.util import Utility
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule
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
        crops_config = Utility.read_json_file(input_directory / 'crop' / field_config['crop'])

        available_fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule = \
            FieldManager._setup_management(field_name, management_config)
        fertilizer_events = fertilizer_schedule.generate_fertilizer_events()
        manure_events = manure_schedule.generate_manure_events()
        tillage_events = tillage_schedule.generate_tillage_events()

        crop_schedules = FieldManager._setup_crop_schedules(crops_config.get("crops"))
        all_planting_events = []
        all_harvest_events = []
        for schedule in crop_schedules:
            all_planting_events += schedule.generate_planting_events()
            all_harvest_events += schedule.generate_harvest_events()

        return Field(plantings=all_planting_events, harvestings=all_harvest_events, tillage_events=tillage_events,
                     fertilizer_events=fertilizer_events, fertilizer_mixes=available_fertilizer_mixes,
                     manure_events=manure_events)

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

    @staticmethod
    def _setup_crop_schedules(crop_config: Dict) -> List[CropSchedule]:
        """
        Creates CropSchedules as dictated by the input specifications.

        Parameters
        ----------
        crop_config : Dict
            Contains all specifications for when crops should be planted and harvested.

        Returns
        -------
        List[CropSchedule]
            List of all crop schedules that have been created from the input specifications.

        """
        schedules = []
        for schedule_name, specifications in crop_config.items():
            if specifications.get("harvest_type") == "scheduled":
                heat_scheduled_harvest = False
            else:
                heat_scheduled_harvest = True
            new_schedule = CropSchedule(name=schedule_name,
                                        crop_reference=specifications.get("crop_reference"),
                                        planting_years=specifications.get("plant_years"),
                                        planting_days=specifications.get("planting_day"),
                                        harvest_years=specifications.get("harvest_years"),
                                        harvest_days=specifications.get("harvest_day"),
                                        harvest_operations=specifications.get("harvest_operations"),
                                        use_heat_scheduling=heat_scheduled_harvest,
                                        pattern_repeat=specifications.get("repeat"))
            schedules.append(new_schedule)
        return schedules
