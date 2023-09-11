from RUFAS.input_manager import InputManager
from RUFAS.routines.field.field.field import Field
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.util import Utility
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.routines.field.manager.crop_schedule import CropSchedule
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.field.manager.current_weather import CurrentWeather
from RUFAS.routines.field.manager.output_gatherer import OutputGatherer
from RUFAS.routines.field.manager.fertilizer_schedule import FertilizerSchedule
from RUFAS.routines.field.manager.manure_schedule import ManureSchedule
from RUFAS.routines.field.manager.tillage_schedule import TillageSchedule
from RUFAS.routines.field.manager.schedule import Schedule
from typing import Dict, List, Tuple, Any

"""
This module is responsible for initializing the `Field` instances that will be simulated and providing an interface to
the `SimulationEngine` for executing daily and annual routines in the field module.
"""

im = InputManager()


class FieldManager:
    def __init__(self, manure_manager: ManureManager):
        self.fields: List[Field] = []
        # for field_name, field_config in fields_config.items():
        #     self.fields.append(self._setup_field(field_name, field_config, manure_manager))
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
        self.output_gatherer.send_annual_variables()
        for field in self.fields:
            field.perform_annual_reset()

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

    def _get_field_blob_names(self) -> List[str]:
        """
        Gets the names of each blob in the metadata that conforms to the field properties.

        Returns
        -------
        List[str]
            List of blob names that contain field configurations.

        """
        field_blob_names = []

        try:
            blobs = im.get_metadata("files")
        except KeyError:
            raise KeyError("Could not find 'files' section of metadata.")

        for blob_name, blob_values in blobs.items():
            try:
                property = blob_values["properties"]
            except KeyError:
                raise KeyError(f"{blob_name} in metadata did not contain 'properties' value.")

            if property == "field_properties":
                field_blob_names.append(blob_name)

        return field_blob_names

    def _setup_field(self, field_name: str, manure_manager: ManureManager) -> Field:
        """

        Parameters
        ----------
        field_name : str
            The name of the blob in the metadata that contains the configuration for the field to be initialized.
        manure_manager: ManureManager
            Instance of the ManureManager class.

        Returns
        -------
        Field
            A `Field` instance configured with the specified input data

        """
        field_data_address = f"{field_name}."
        field_size = im.get_data(field_data_address + "field_size")
        absolute_latitude = im.get_data(field_data_address + "absolute_latitude")
        longitude = im.get_data(field_data_address + "longitude")
        minimum_daylength = im.get_data(field_data_address + "minimum_daylength")
        seasonal_high_water_table = im.get_data(field_data_address + "seasonal_high_water_table")
        watering_amount_in_liters = im.get_data(field_data_address + "watering_amount_in_liters")
        watering_interval = im.get_data(field_data_address + "watering_interval")

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

        field_data = FieldData(name=field_name, field_size=field_size, absolute_latitude=absolute_latitude,
                               longitude=longitude, minimum_daylength=minimum_daylength,
                               seasonal_high_water_table=seasonal_high_water_table,
                               watering_amount_in_liters=watering_amount_in_liters, watering_interval=watering_interval)

        return Field(field_data=field_data, soil=soil_profile, plantings=all_planting_events,
                     harvestings=all_harvest_events, tillage_events=tillage_events, fertilizer_events=fertilizer_events,
                     fertilizer_mixes=available_fertilizer_mixes, manure_events=manure_events,
                     manure_manager=manure_manager)

    def _setup_fertilizer_schedule(self, fertilizer_schedule: str) -> Tuple[Dict, FertilizerSchedule]:
        """
        Sets up the fertilizer schedule and the list of available fertilizer mixes.

        Parameters
        ----------
        fertilizer_schedule : str
            Name of the metadata blob that contains the fertilizer schedule.

        Returns
        -------
        Tuple[Dict, FertilizerSchedule]
            Dictionary containing the specifications of the available fertilizer mixes, and a FertilizerSchedule.

        """
        fertilizer_data = im.get_data(fertilizer_schedule)
        available_fertilizer_mixes = {}
        fertilizer_mix_data = fertilizer_data.get("available_fertilizer_mixes")
        for mix in fertilizer_mix_data:
            available_fertilizer_mixes[mix.get("name")] = {
                "N": mix.get("N"),
                "P": mix.get("P"),
                "K": mix.get("K")
            }

        fertilizer_application_schedule = FertilizerSchedule(
            name="fertilizer_schedule",
            mix_names=fertilizer_data.get("mix_names"),
            years=fertilizer_data.get("years"),
            days=fertilizer_data.get("days"),
            nitrogen_masses=fertilizer_data.get("nitrogen_masses"),
            phosphorus_masses=fertilizer_data.get("phosphorus_masses"),
            application_depths=fertilizer_data.get("application_depths"),
            surface_remainder_fractions=fertilizer_data.get("surface_remainder_fractions"),
            pattern_skip=fertilizer_data.get("pattern_skip"),
            pattern_repeat=fertilizer_data.get("pattern_repeat")
        )

        return available_fertilizer_mixes, fertilizer_application_schedule

    def _setup_manure_schedule(self, manure_schedule: str) -> ManureSchedule:
        """
        Sets up a ManureSchedule.

        Parameters
        ----------
        manure_schedule : str
            Name of the metadata blob that contains the manure schedule information.

        Returns
        -------
        ManureSchedule
            ManureSchedule instance created using data pulled from the Input Manager.

        """
        manure_schedule_data = im.get_data(manure_schedule)
        manure_schedule_instance = ManureSchedule(
            name="manure_schedule",
            years=manure_schedule_data.get("years"),
            days=manure_schedule_data.get("days"),
            nitrogen_masses=manure_schedule_data.get("nitrogen_masses"),
            phosphorus_masses=manure_schedule_data.get("phosphorus_masses"),
            field_coverages=manure_schedule_data.get("coverage_fractions"),
            application_depths=manure_schedule_data.get("application_depths"),
            surface_remainder_fractions=manure_schedule_data.get("surface_remainder_fractions"),
            pattern_skip=manure_schedule_data.get("pattern_skip"),
            pattern_repeat=manure_schedule_data.get("pattern_repeat"),
        )
        return manure_schedule_instance

    def _setup_tillage_schedule(self, tillage_schedule: str) -> TillageSchedule:
        """
        Sets up a TillageSchedule.

        Parameters
        ----------
        tillage_schedule : str
            Name of the metadata blob that contains the manure schedule information.

        Returns
        -------
        TillageSchedule
            TillageSchedule instance created using data pulled from the Input Manager.

        """
        tillage_schedule_data = im.get_data(tillage_schedule)
        tillage_schedule_instance = TillageSchedule(
            name="tillage_schedule",
            years=tillage_schedule_data.get("years"),
            days=tillage_schedule_data.get("days"),
            incorporation_fractions=tillage_schedule_data.get("incorporation_fractions"),
            mixing_fractions=tillage_schedule_data.get("mixing_fractions"),
            tillage_depths=tillage_schedule_data.get("tillage_depths"),
            pattern_skip=tillage_schedule_data.get("pattern_skip"),
            pattern_repeat=tillage_schedule_data.get("pattern_repeat")
        )
        return tillage_schedule_instance

    def _setup_crop_schedules(self, crop_rotation: str) -> List[CropSchedule]:
        """
        Creates CropSchedules as dictated by the input specifications.

        Parameters
        ----------
        crop_rotation : str
            Name of the metadata blob that contains the crop rotation information.

        Returns
        -------
        List[CropSchedule]
            List of all crop schedules that have been created from the input specifications.

        """
        schedules = []
        crop_rotation_data = im.get_data(f"{crop_rotation}.crop_schedules")

        for index, rotation in enumerate(crop_rotation_data):
            print(rotation)
            if rotation.get("harvest_type") == "scheduled":
                heat_scheduled_harvest = False
            else:
                heat_scheduled_harvest = True
            new_schedule = CropSchedule(name=f"crop_schedule_{index}",
                                        crop_reference=rotation.get("crop_species"),
                                        planting_years=rotation.get("planting_years"),
                                        planting_days=rotation.get("planting_days"),
                                        harvest_years=rotation.get("harvest_years"),
                                        harvest_days=rotation.get("harvest_days"),
                                        harvest_operations=rotation.get("harvest_operations"),
                                        use_heat_scheduling=heat_scheduled_harvest,
                                        pattern_repeat=rotation.get("pattern_repeat"),
                                        pattern_skip=rotation.get("pattern_skip"))
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
                top_depth = 0.0
            else:
                top_depth = soil_layers[-1].bottom_depth
            new_layer = FieldManager._setup_soil_layer(field_size, top_depth, sand_content,
                                                       silt_content, residue, nitrogen_mineralization_rate,
                                                       layer_config)
            soil_layers.append(new_layer)

        config_dictionary = {"second_moisture_condition_parameter": soil_config.get("CN2"),
                             "average_subbasin_slope": soil_config.get("field_slope"),
                             "slope_length": soil_config.get("slope_length"), "manning": soil_config.get("manning"),
                             "albedo": soil_config.get("soil_albedo"), "cover_type": soil_config.get("soil_cover_type"),
                             "soil_layers": soil_layers}

        soil_data = SoilData(field_size=field_size, **config_dictionary)
        return Soil(soil_data=soil_data)

    def _setup_soil_layer(self, field_size: float, top_depth: float, sand: float, silt: float, initial_residue: float,
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

        try:
            config_dictionary["bottom_depth"] = layer_config["bottom_depth"]
        except KeyError:
            raise ValueError("Bottom depth is required for each soil layer.")

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
