from SC_redesign.Crop_and_Soil.field.field import Field
from SC_redesign.Crop_and_Soil.field.field_data import FieldData
from RUFAS.util import Utility
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.manager.crop_schedule import CropSchedule
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.manager.fertilizer_schedule import FertilizerSchedule
from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule
from SC_redesign.Crop_and_Soil.manager.tillage_schedule import TillageSchedule
from SC_redesign.Crop_and_Soil.manager.schedule import Schedule
from typing import Dict, List, Tuple, Any

"""
This module is responsible for initializing the `Field` instances that will be simulated and providing an interface to
the `SimulationEngine` for executing daily and annual routines in the field module.
"""


class FieldManager:
    def __init__(self, fields_config: Dict[str, Dict[str, str]]):
        self.fields: List[Field] = []
        for field_name, field_config in fields_config.items():
            self.fields.append(self._setup_field(field_name, field_config))
        self.output_gatherer = OutputGatherer(fields=self.fields)

    def daily_update_routine(self, weather, time) -> None:
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
            current_weather = FieldManager._create_current_weather(weather=weather, time=time, month=month)
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
    def _date_conversion_month(time) -> int:
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
        if Schedule.is_leap_year(time.calendar_year):
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
    def _date_conversion_day(time) -> int:
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

        if Schedule.is_leap_year(time.calendar_year):
            return time.day - leap_days[FieldManager._date_conversion_month(time) - 2]
        else:
            return time.day - days[FieldManager._date_conversion_month(time) - 2]

    @staticmethod
    def _create_current_weather(weather, time, month: int) -> CurrentWeather:
        """
        Creates a CurrentWeather object containing all the weather conditions of the current day.

        Parameters
        ----------
        weather : Weather
            Object containing all the environmental conditions of the simulation.
        time : Time
            Object containing the current time and day of the simulation.
        month : int
            Number representing the current month of the simulation.

        Returns
        -------
        CurrentWeather
            Object containing the weather conditions of the current day.

        """
        daylength = CurrentWeather.determine_daylength(month)
        return CurrentWeather(incoming_light=weather.radiation[time.year - 1][time.day - 1],
                              min_air_temperature=weather.T_min[time.year - 1][time.day - 1],
                              mean_air_temperature=weather.T_avg[time.year - 1][time.day - 1],
                              max_air_temperature=weather.T_max[time.year - 1][time.day - 1],
                              annual_mean_air_temperature=weather.T_avg_annual[time.year - 1],
                              rainfall=weather.rainfall[time.year - 1][time.day - 1],
                              irrigation=weather.irrigation[time.year - 1][time.day - 1],
                              daylength=daylength)

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
        soil_config = Utility.read_json_file(input_directory / 'soil' / field_config['soil'])

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

        soil_profile = FieldManager._setup_soil(soil_config)

        field_data = FieldData(name=field_name, field_size=soil_config["field_size"],
                               current_residue=soil_config["initial_residue"],
                               absolute_latitude=abs(crops_config["latitude"]))

        return Field(field_data=field_data, soil=soil_profile, plantings=all_planting_events,
                     harvestings=all_harvest_events, tillage_events=tillage_events, fertilizer_events=fertilizer_events,
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

    @staticmethod
    def _setup_soil(soil_config: Dict[str, Any]) -> Soil:
        """
        Sets up a Soil instance that will be used by the Field class.

        Parameters
        ----------
        soil_config : Dict[str]
            Contains all the data necessary to set up a SoilData object.

        Returns
        -------
        Soil
            Soil instance that contains a SoilData instance configured to the provided specifications.

        """
        field_size = soil_config["field_size"]
        sand_content = soil_config["sand"]
        silt_content = soil_config["silt"]
        residue = soil_config["initial_residue"]
        nitrogen_mineralization_rate = soil_config["fresh_N_mineral_rate"]

        soil_layers_config = list(soil_config.get("soil_layers").values())
        soil_layers_config.sort(key=lambda x: x.get("bottom_depth"))
        soil_layers = []
        for index, layer_config in enumerate(soil_layers_config):
            if index == 0:
                new_layer = FieldManager._setup_soil_layer(field_size, 0.0, sand_content, silt_content, residue,
                                                           nitrogen_mineralization_rate, layer_config)
            else:
                new_layer = FieldManager._setup_soil_layer(field_size, soil_layers[-1].bottom_depth, sand_content,
                                                           silt_content, residue, nitrogen_mineralization_rate,
                                                           layer_config)
            soil_layers.append(new_layer)

        config_dictionary = {}

        config_dictionary["second_moisture_condition_parameter"] = soil_config.get("CN2")
        config_dictionary["average_subbasin_slope"] = soil_config.get("field_slope")
        config_dictionary["slope_length"] = soil_config.get("slope_length")
        config_dictionary["manning"] = soil_config.get("manning")
        config_dictionary["albedo"] = soil_config.get("soil_albedo")
        config_dictionary["cover_type"] = soil_config.get("soil_cover_type")
        config_dictionary["soil_layers"] = soil_layers

        soil_data = SoilData(field_size=field_size, **config_dictionary)
        return Soil(soil_data=soil_data)

    @staticmethod
    def _setup_soil_layer(field_size: float, top_depth: float, sand: float, silt: float, initial_residue: float,
                          fresh_nitrogen_mineralization_rate: float, layer_config: Dict) -> LayerData:
        """
        Initializes a LayerData instance to be added to a SoilData object.

        Parameters
        ----------
        field_size : float
            Size of the field that contains the soil layer being created (ha)
        top_depth : float
            Depth of top of the soil layer beneath the surface (mm)
        sand : float
            Sand content expressed as percent of soil in this layer (unitless)
        silt : float
            Silt content expressed as percent of soil in this layer (unitless)
        initial_residue : float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha)
        fresh_nitrogen_mineralization_rate : float
            Rate at which fresh organic nitrogen mineralizes (unitless)
        layer_config : Dict
            Contains all the specifications for a layer of soil.

        Returns
        -------
        LayerData
            LayerData instance configured with provided data.

        Notes
        -----
        Whoever wrote the JSON's for soil profile inputs wrote "N03" (the digit zero) instead of "NO3" (the letter 'O'),
        and that is why it is written with a zero and not the letter here.

        """
        config_dictionary = {}

        config_dictionary["bottom_depth"] = layer_config["bottom_depth"]
        config_dictionary["wilting_point_water_concentration"] = layer_config.get("wilting_point")
        config_dictionary["field_capacity_water_concentration"] = layer_config.get("field_capacity")
        config_dictionary["saturation_point_water_concentration"] = layer_config.get("saturation")
        config_dictionary["saturated_hydraulic_conductivity"] = layer_config.get("K_sat")
        config_dictionary["percent_clay_content"] = layer_config.get("clay")
        config_dictionary["temperature"] = layer_config.get("initial_temperature")
        config_dictionary["bulk_density"] = layer_config["bulk_density"]
        config_dictionary["percent_organic_carbon_content"] = layer_config.get("org_C_percent")
        config_dictionary["initial_soil_ammonium_concentration"] = layer_config.get("NH4")
        config_dictionary["initial_soil_nitrate_concentration"] = layer_config.get("N03")
        config_dictionary["initial_labile_inorganic_phosphorus_concentration"] = layer_config.get("labile_P")
        config_dictionary["humus_mineralization_rate_factor"] = layer_config.get("active_mineral_rate")
        config_dictionary["ammonium_volatilization_cation_exchange_factor"] = \
            layer_config.get("volatile_exchange_factor")
        config_dictionary["denitrification_rate_coefficient"] = layer_config.get("denitrification_rate")
        config_dictionary["soil_water_concentration"] = layer_config.get("soil_water_percent")

        config_dictionary["field_size"] = field_size
        config_dictionary["top_depth"] = top_depth
        config_dictionary["percent_sand_content"] = sand
        config_dictionary["percent_silt_content"] = silt
        config_dictionary["residue"] = initial_residue
        config_dictionary["residue_fresh_organic_mineralization_rate"] = fresh_nitrogen_mineralization_rate

        layer = LayerData(**config_dictionary)
        return layer
