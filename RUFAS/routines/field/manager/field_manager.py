from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.field.field.field import Field
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.routines.field.manager.crop_schedule import CropSchedule
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType
from RUFAS.weather import Weather
from RUFAS.time import Time
from RUFAS.routines.field.manager.field_data_reporter import FieldDataReporter
from RUFAS.routines.field.manager.fertilizer_schedule import FertilizerSchedule
from RUFAS.routines.field.manager.manure_schedule import ManureSchedule
from RUFAS.routines.field.manager.tillage_schedule import TillageSchedule
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from typing import Dict, List, Tuple

"""
This module is responsible for initializing the `Field` instances that will be simulated and providing an interface to
the `SimulationEngine` for executing daily and annual routines in the field module.
"""

im = InputManager()
om = OutputManager()


class FieldManager:
    def __init__(self, manure_manager: ManureManager, feed_manager: FeedManager):
        info_map = {
            "class": self.__class__.__name__,
            "function": self.__init__.__name__
        }

        self.fields: List[Field] = []
        fields = im.get_data_keys_by_properties("field_properties")
        if not fields:
            om.add_warning(
                "No field input files.",
                "No fields will be simulated.",
                info_map
            )

        for field in fields:
            new_field = self._setup_field(field, manure_manager, feed_manager)
            self.fields.append(new_field)
        self.output_gatherer = FieldDataReporter(fields=self.fields)

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
        current_conditions = weather.get_current_day_conditions(time)
        for field in self.fields:
            field.manage_field(time, current_conditions=current_conditions)
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
    def _setup_field(field_name: str, manure_manager: ManureManager, feed_manager: FeedManager) -> Field:
        """

        Parameters
        ----------
        field_name : str
            The name of the blob in the metadata that contains the configuration for the field to be initialized.
        manure_manager : ManureManager
            Instance of the ManureManager class.
        feed_manager : FeedManager
            Instance of the FeedManager class which receives and manages harvested crops.

        Returns
        -------
        Field
            A `Field` instance configured with the specified input data

        """
        field_configuration_data = im.get_data(field_name)
        field_size = field_configuration_data.get("field_size")
        absolute_latitude = field_configuration_data.get("absolute_latitude")
        longitude = field_configuration_data.get("longitude")
        minimum_daylength = field_configuration_data.get("minimum_daylength")
        seasonal_high_water_table = field_configuration_data.get("seasonal_high_water_table")
        watering_amount_in_liters = field_configuration_data.get("watering_amount_in_liters")
        watering_interval = field_configuration_data.get("watering_interval")
        supplement_manure = field_configuration_data.get("supplement_manure_nutrient_deficiencies")

        fertilizer_configuration = field_configuration_data.get("fertilizer_management_specification")
        available_fertilizer_mixes, fertilizer_schedule = FieldManager._setup_fertilizer_schedule(
            fertilizer_configuration)
        fertilizer_events = fertilizer_schedule.generate_fertilizer_events()

        manure_configuration = field_configuration_data.get("manure_management_specification")
        manure_application_schedule = FieldManager._setup_manure_schedule(manure_configuration)
        manure_events = manure_application_schedule.generate_manure_events()

        tillage_configuration = field_configuration_data.get("tillage_management_specification")
        tillage_schedule = FieldManager._setup_tillage_schedule(tillage_configuration)
        tillage_events = tillage_schedule.generate_tillage_events()

        crop_rotation_configuration = field_configuration_data.get("crop_specification")
        crop_schedules = FieldManager._setup_crop_schedules(crop_rotation_configuration)
        all_planting_events = []
        all_harvest_events = []
        for schedule in crop_schedules:
            all_planting_events += schedule.generate_planting_events()
            all_harvest_events += schedule.generate_harvest_events()

        soil_configuration = field_configuration_data.get("soil_specification")
        soil_profile = FieldManager._setup_soil(soil_configuration, field_size)

        field_data = FieldData(name=field_name, field_size=field_size, absolute_latitude=absolute_latitude,
                               longitude=longitude, minimum_daylength=minimum_daylength,
                               seasonal_high_water_table=seasonal_high_water_table,
                               watering_amount_in_liters=watering_amount_in_liters, watering_interval=watering_interval,
                               supplement_manure_nutrient_deficiencies=supplement_manure)

        return Field(field_data=field_data, soil=soil_profile, plantings=all_planting_events,
                     harvestings=all_harvest_events, tillage_events=tillage_events, fertilizer_events=fertilizer_events,
                     fertilizer_mixes=available_fertilizer_mixes, manure_events=manure_events,
                     manure_manager=manure_manager, feed_manager=feed_manager)

    @staticmethod
    def _setup_fertilizer_schedule(fertilizer_schedule: str) -> Tuple[Dict, FertilizerSchedule]:
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

    @staticmethod
    def _setup_manure_schedule(manure_schedule: str) -> ManureSchedule:
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
        manure_type_strings = manure_schedule_data.get("manure_types")
        manure_types = [ManureType(manure_type_string) for manure_type_string in manure_type_strings]
        manure_schedule_instance = ManureSchedule(
            name="manure_schedule",
            years=manure_schedule_data.get("years"),
            days=manure_schedule_data.get("days"),
            nitrogen_masses=manure_schedule_data.get("nitrogen_masses"),
            phosphorus_masses=manure_schedule_data.get("phosphorus_masses"),
            manure_types=manure_types,
            field_coverages=manure_schedule_data.get("coverage_fractions"),
            application_depths=manure_schedule_data.get("application_depths"),
            surface_remainder_fractions=manure_schedule_data.get("surface_remainder_fractions"),
            pattern_skip=manure_schedule_data.get("pattern_skip"),
            pattern_repeat=manure_schedule_data.get("pattern_repeat"),
        )
        return manure_schedule_instance

    @staticmethod
    def _setup_tillage_schedule(tillage_schedule: str) -> TillageSchedule:
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

    @staticmethod
    def _setup_crop_schedules(crop_rotation: str) -> List[CropSchedule]:
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
                                        planting_skip=rotation.get("planting_skip"),
                                        harvesting_skip=rotation.get("harvesting_skip"))
            schedules.append(new_schedule)
        return schedules

    @staticmethod
    def _setup_soil(soil_configuration: str, field_size: float) -> Soil:
        """
        Sets up a Soil instance that will be used by the Field class.

        Parameters
        ----------
        soil_configuration : str
            Name of the metadata blob that contains the soil.
        field_size : float
            Size of the field that contains this soil profile (ha).

        Returns
        -------
        Soil
            Soil instance that contains a SoilData instance configured to the provided specifications.

        Raises
        ------
        ValueError
            If no specification is provided for soil layers.

        """
        soil_configuration_data = im.get_data(soil_configuration)
        residue = soil_configuration_data["initial_residue"]
        soil_layers_config = soil_configuration_data.get("soil_layers")
        if soil_layers_config is None:
            raise ValueError("Configuration for soil layers must be provided.")
        soil_layers_config.sort(key=lambda x: x.get("bottom_depth"))
        soil_layers = []
        top_depth = 0.0
        for index, layer_config in enumerate(soil_layers_config):
            new_layer = FieldManager._setup_soil_layer(field_size, top_depth, residue, layer_config)
            soil_layers.append(new_layer)
            top_depth = new_layer.bottom_depth

        config_dictionary = {"soil_layers": soil_layers}

        expected_values = [
            "second_moisture_condition_parameter",
            "average_subbasin_slope",
            "slope_length",
            "albedo"
        ]

        for value in expected_values:
            config_dictionary[value] = soil_configuration_data.get(value)

        config_dictionary["manning"] = soil_configuration_data.get("manning_roughness_coefficient")

        soil_data = SoilData(field_size=field_size, **config_dictionary)
        return Soil(soil_data=soil_data)

    @staticmethod
    def _setup_soil_layer(field_size: float, top_depth: float, initial_residue: float, layer_config: Dict) -> LayerData:
        """
        Initializes a LayerData instance to be added to a SoilData object.

        Parameters
        ----------
        field_size : float
            Size of the field that contains the soil layer being created (ha)
        top_depth : float
            Depth of top of the soil layer beneath the surface (mm)
        initial_residue : float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha)
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

        expected_values = [
            "soil_water_concentration",
            "wilting_point_water_concentration",
            "field_capacity_water_concentration",
            "saturation_point_water_concentration",
            "saturated_hydraulic_conductivity",
            "bulk_density",
            "percent_organic_carbon_content",
            "percent_clay_content",
            "percent_silt_content",
            "percent_sand_content",
            "percent_rock_content",
            "initial_labile_inorganic_phosphorus_concentration",
            "initial_soil_nitrate_concentration",
            "initial_soil_ammonium_concentration",
            "humus_mineralization_rate_factor",
            "ammonium_volatilization_cation_exchange_factor",
            "denitrification_rate_coefficient",
            "denitrification_threshold_water_content",
            "residue_fresh_organic_mineralization_rate"
        ]

        for value in expected_values:
            config_dictionary[value] = layer_config.get(value)

        config_dictionary["temperature"] = layer_config.get("initial_temperature")

        config_dictionary["field_size"] = field_size
        config_dictionary["top_depth"] = top_depth
        config_dictionary["residue"] = initial_residue

        layer = LayerData(**config_dictionary)
        return layer
