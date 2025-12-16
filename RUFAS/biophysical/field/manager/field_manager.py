from typing import Any
from datetime import date

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.events import FertilizerEvent, ManureEvent, TillageEvent, PlantingEvent, HarvestEvent
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_to_crop_soil_connection import (
    ManureEventNutrientRequest,
    ManureEventNutrientRequestResults,
)

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop_data_factory import CropDataFactory
from RUFAS.biophysical.field.field.field import Field
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.manager.crop_schedule import CropSchedule
from RUFAS.biophysical.field.manager.fertilizer_schedule import FertilizerSchedule
from RUFAS.biophysical.field.manager.field_data_reporter import FieldDataReporter
from RUFAS.biophysical.field.manager.manure_schedule import ManureSchedule
from RUFAS.biophysical.field.manager.tillage_schedule import TillageSchedule
from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.biophysical.field.soil.soil_data import SoilData
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather


class FieldManager:
    """
    Manages the initialization and simulation of field instances within the simulation environment. This class is
    responsible for creating `Field` instances based on input data, managing these fields across the simulation
    lifecycle, and interfacing with the `SimulationEngine` to execute daily and annual routines.


    Attributes
    ----------
    fields : list[Field]
        A list of `Field` instances that have been initialized and are managed by this `FieldManager`.
    output_gatherer : FieldDataReporter
        An instance of `FieldDataReporter` responsible for gathering and reporting data from the managed fields.
    om : OutputManager
        Instance of the OutputManager.

    """

    def __init__(self) -> None:
        info_map = {"class": self.__class__.__name__, "function": "__init__"}
        self.im = InputManager()
        self.om = OutputManager()
        self.fields: list[Field] = []
        fields = self.im.get_data_keys_by_properties("field_properties")
        if not fields:
            self.om.add_warning("No field input files.", "No fields will be simulated.", info_map)

        CropDataFactory.setup_crop_configurations()
        available_crop_configs = CropDataFactory.get_available_crop_configurations()

        for field in fields:
            new_field = self._setup_field(field, available_crop_configs)
            self.fields.append(new_field)
        self.output_gatherer = FieldDataReporter(fields=self.fields)

    def daily_update_routine(
        self, weather: Weather, time: RufasTime, manure_applications: list[ManureEventNutrientRequestResults]
    ) -> list[HarvestedCrop]:
        """
        This method will run the daily routine in the field, which will be calling the manage field method on each
        field.

        Parameters
        ----------
        weather: Weather
            A weather object that contains infos to be transformed to current weather
        time: RufasTime
            RufasTime object containing the current year and day of the simulation.
        manure_applications: list[ManureEventNutrientRequestResults]
            A list containing the ManureEvents and corresponding NutrientRequestResults for each field in
            the simulation.

        Returns
        -------
        list[HarvestedCrop]
            Crops that were harvested on the current day.

        Notes
        -----
        Because different fields can have different latitudes, the day length has to be recalculated for each field.

        """
        harvested_crops: list[HarvestedCrop] = []
        for field in self.fields:
            current_conditions = weather.get_current_day_conditions(time, field.field_data.absolute_latitude)
            info_map = {
                "class": self.__class__.__name__,
                "function": self.daily_update_routine.__name__,
                "suffix": f"field='{field.field_data.name}'",
                "units": MeasurementUnits.HOURS,
            }
            self.om.add_variable("daylength", current_conditions.daylength, info_map)
            manure_applications_for_field = [
                application for application in manure_applications if application.field_name == field.field_data.name
            ]
            newly_harvested_crops = field.manage_field(
                time, current_conditions=current_conditions, manure_applications=manure_applications_for_field
            )
            harvested_crops.extend(newly_harvested_crops)
        self.output_gatherer.send_daily_variables(time)

        return harvested_crops

    def annual_update_routine(self) -> None:
        """
        This method will run the annual routine in the field, which will be calling the perform_annual_reset() method
        on each field.
        """
        self.output_gatherer.send_annual_variables()
        for field in self.fields:
            field.perform_annual_reset()

    def get_next_harvest_dates(self, crops_to_look_for: list[str]) -> dict[str, date]:
        """
        Gets the date of the next harvest that is scheduled for each of the specified RuFaS crop configurations.

        Parameters
        ----------
        harvests_to_query : list[str]
            List of crop harvests to find next harvest dates for.

        Returns
        -------
        dict[str, date]
            Mapping from crop to the date of that feeds next harvest.

        """
        next_harvest_dates: dict[str, date] = {}
        all_harvests_sorted = sorted(
            [harvest_event for field in self.fields for harvest_event in field.harvest_events],
            key=lambda harvest_event: harvest_event.date_occurs,
        )
        for crop in crops_to_look_for:
            harvests = [harvest.date_occurs for harvest in all_harvests_sorted if harvest.crop_reference == crop]
            if len(harvests) > 0:
                next_harvest_dates[crop] = harvests[0]

        return next_harvest_dates

    @staticmethod
    def _setup_field(field_name: str, available_crop_configs: list[str]) -> Field:
        """

        Parameters
        ----------
        field_name : str
            The name of the blob in the metadata that contains the configuration for the field to be initialized.
        available_crop_configs : list[str]
            A list of the names of the available crop configurations.

        Returns
        -------
        Field
            A `Field` instance configured with the specified input data

        """
        im = InputManager()
        field_configuration_data: dict[str, Any] = im.get_data(field_name)

        field_data = FieldManager._setup_field_data(field_name, field_configuration_data)

        soil_profile = FieldManager._setup_soil(
            soil_configuration=field_configuration_data["soil_specification"],
            field_size=field_configuration_data["field_size"],
        )

        available_fertilizer_mixes, fertilizer_events = FieldManager._setup_fertilizer_events(
            field_configuration_data["fertilizer_management_specification"]
        )

        manure_events = FieldManager._setup_manure_events(field_configuration_data["manure_management_specification"])

        tillage_events = FieldManager._setup_tillage_events(
            field_configuration_data["tillage_management_specification"]
        )

        all_planting_events, all_harvest_events = FieldManager._setup_crop_events(
            field_configuration_data["crop_specification"], available_crop_configs
        )

        return Field(
            field_data=field_data,
            soil=soil_profile,
            plantings=all_planting_events,
            harvestings=all_harvest_events,
            tillage_events=tillage_events,
            fertilizer_events=fertilizer_events,
            fertilizer_mixes=available_fertilizer_mixes,
            manure_events=manure_events,
        )

    @staticmethod
    def _setup_field_data(field_name: str, field_configuration_data: dict[str, Any]) -> FieldData:
        """
        This method sets up the field data parameters using the given field name and
        field configuration data.

        Parameters
        ----------
        field_name: str
            The name of the field.
        field_configuration_data: dict[str, Any]
            Configuration details such as field size, latitude, longitude, and other simulation
            parameters.

        Returns
        -------
        FieldData
            An instance of the FieldData class populated with the values from the field_configuration_data.

        """
        return FieldData(
            name=field_name,
            field_size=field_configuration_data["field_size"],
            absolute_latitude=field_configuration_data["absolute_latitude"],
            longitude=field_configuration_data["longitude"],
            minimum_daylength=field_configuration_data["minimum_daylength"],
            seasonal_high_water_table=field_configuration_data["seasonal_high_water_table"],
            watering_amount_in_liters=field_configuration_data["watering_amount_in_liters"],
            watering_interval=field_configuration_data["watering_interval"],
            simulate_water_stress=field_configuration_data["simulate_water_stress"],
            simulate_temp_stress=field_configuration_data["simulate_temp_stress"],
            simulate_nitrogen_stress=field_configuration_data["simulate_nitrogen_stress"],
            simulate_phosphorus_stress=field_configuration_data["simulate_phosphorus_stress"],
        )

    @staticmethod
    def _setup_crop_events(
        crop_rotation_configuration: str, available_crop_configs: list[str]
    ) -> tuple[list[PlantingEvent], list[HarvestEvent]]:
        """
        Generates all planting and harvest events based on a given crop rotation configuration.

        Parameters
        ----------
        crop_rotation_configuration : str
            Configuration for crop rotation detailing the schedule and crops to be planted.
        available_crop_configs : list[str]
            A list of the names of the available crop configurations.

        Returns
        -------
        tuple[list[PlantingEvent], list[HarvestEvent]]
            A tuple containing two lists:
            - List of all planting events required by the crop rotation schedule.
            - List of all harvest events corresponding to the planting events.

        """
        crop_schedules = FieldManager._setup_crop_schedules(crop_rotation_configuration, available_crop_configs)
        all_planting_events: list[PlantingEvent] = []
        all_harvest_events: list[HarvestEvent] = []
        for schedule in crop_schedules:
            all_planting_events += schedule.generate_planting_events()
            all_harvest_events += schedule.generate_harvest_events()
        return all_planting_events, all_harvest_events

    @staticmethod
    def _setup_fertilizer_events(
        fertilizer_schedule: str,
    ) -> tuple[dict[str, dict[str, float]], list[FertilizerEvent]]:
        """
        Sets up a list of fertilizer events from fertilizer schedule and the list of available fertilizer mixes.

        Parameters
        ----------
        fertilizer_schedule : str
            Name of the metadata blob that contains the fertilizer schedule.

        Returns
        -------
        tuple[dict[str, dict[str, float], FertilizerSchedule]
            Dictionary containing the specifications of the available fertilizer mixes, and a FertilizerSchedule.

        """
        im = InputManager()
        fertilizer_data: dict[str, Any] = im.get_data(fertilizer_schedule)
        if fertilizer_data is None:
            om = OutputManager()
            info_map = {
                "class": FieldManager.__class__.__name__,
                "function": FieldManager._setup_fertilizer_events.__name__,
            }
            om.add_error("No fertilizer data", "Field data provided with empty fertilizer data.", info_map)
            raise ValueError("No fertilizer data")
        available_fertilizer_mixes: dict[str, dict[str, float]] = {}
        fertilizer_mix_data: list[dict[str, Any]] = fertilizer_data["available_fertilizer_mixes"]
        for mix in fertilizer_mix_data:
            mix_name: str = mix["name"]
            available_fertilizer_mixes[mix_name] = {
                "N": mix["N"],
                "P": mix["P"],
                "K": mix["K"],
                "ammonium_fraction": mix["ammonium_fraction"],
            }

        fertilizer_application_schedule = FertilizerSchedule(
            name="fertilizer_schedule",
            mix_names=fertilizer_data["mix_names"],
            years=fertilizer_data["years"],
            days=fertilizer_data["days"],
            nitrogen_masses=fertilizer_data["nitrogen_masses"],
            phosphorus_masses=fertilizer_data["phosphorus_masses"],
            potassium_masses=fertilizer_data["potassium_masses"],
            application_depths=fertilizer_data["application_depths"],
            surface_remainder_fractions=fertilizer_data["surface_remainder_fractions"],
            pattern_skip=fertilizer_data["pattern_skip"],
            pattern_repeat=fertilizer_data["pattern_repeat"],
        )
        fertilizer_application_events = fertilizer_application_schedule.generate_fertilizer_events()

        return available_fertilizer_mixes, fertilizer_application_events

    @staticmethod
    def _setup_manure_events(manure_schedule: str) -> list[ManureEvent]:
        """
        Sets up a list of manure events from ManureSchedule.

        Parameters
        ----------
        manure_schedule : str
            Name of the metadata blob that contains the manure schedule information.

        Returns
        -------
        list[ManureEvent]
            A list of generated manure events.

        """
        im = InputManager()
        manure_schedule_data: dict[str, Any] = im.get_data(manure_schedule)
        if manure_schedule_data is None:
            om = OutputManager()
            info_map = {
                "class": FieldManager.__class__.__name__,
                "function": FieldManager._setup_manure_events.__name__,
            }
            om.add_error("No manure data", "Field data provided with empty manure data.", info_map)
            raise ValueError("No manure data")
        manure_type_strings: list[str] = manure_schedule_data["manure_types"]
        manure_supplement_methods_strings: list[str] = manure_schedule_data["supplement_manure_nutrient_deficiencies"]
        manure_supplement_methods: list[ManureSupplementMethod] = [
            ManureSupplementMethod(manure_supplement_methods_string)
            for manure_supplement_methods_string in manure_supplement_methods_strings
        ]
        manure_types: list[ManureType] = [ManureType(manure_type_string) for manure_type_string in manure_type_strings]
        manure_schedule_instance = ManureSchedule(
            name="manure_schedule",
            years=manure_schedule_data["years"],
            days=manure_schedule_data["days"],
            nitrogen_masses=manure_schedule_data["nitrogen_masses"],
            phosphorus_masses=manure_schedule_data["phosphorus_masses"],
            manure_types=manure_types,
            manure_supplement_methods=manure_supplement_methods,
            field_coverages=manure_schedule_data["coverage_fractions"],
            application_depths=manure_schedule_data["application_depths"],
            surface_remainder_fractions=manure_schedule_data["surface_remainder_fractions"],
            pattern_skip=manure_schedule_data["pattern_skip"],
            pattern_repeat=manure_schedule_data["pattern_repeat"],
        )
        manure_events = manure_schedule_instance.generate_manure_events()
        return manure_events

    @staticmethod
    def _setup_tillage_events(tillage_schedule: str) -> list[TillageEvent]:
        """
        Sets up a list of TillageEvent from TillageSchedule.

        Parameters
        ----------
        tillage_schedule : str
            Name of the metadata blob that contains the tillage schedule information.

        Returns
        -------
        list[TillageEvent]
            A list of generated tillage events.

        """
        im = InputManager()
        tillage_schedule_data: dict[str, Any] = im.get_data(tillage_schedule)
        if tillage_schedule_data is None:
            om = OutputManager()
            info_map = {
                "class": FieldManager.__class__.__name__,
                "function": FieldManager._setup_tillage_events.__name__,
            }
            om.add_error("No tillage data", "Field data provided with empty tillage data.", info_map)
            raise ValueError("No tillage data")
        tillage_schedule_instance = TillageSchedule(
            name="tillage_schedule",
            years=tillage_schedule_data["years"],
            days=tillage_schedule_data["days"],
            incorporation_fractions=tillage_schedule_data["incorporation_fractions"],
            mixing_fractions=tillage_schedule_data["mixing_fractions"],
            tillage_depths=tillage_schedule_data["tillage_depths"],
            implements=tillage_schedule_data["implements"],
            pattern_skip=tillage_schedule_data["pattern_skip"],
            pattern_repeat=tillage_schedule_data["pattern_repeat"],
        )
        tillage_events = tillage_schedule_instance.generate_tillage_events()
        return tillage_events

    @staticmethod
    def _setup_crop_schedules(crop_rotation: str, available_crop_configurations: list[str]) -> list[CropSchedule]:
        """
        Creates CropSchedules as dictated by the input specifications.

        Parameters
        ----------
        crop_rotation : str
            Name of the metadata blob that contains the crop rotation information.
        available_crop_configurations : list[str]
            A list of the names of the available crop configurations.

        Returns
        -------
        list[CropSchedule]
            List of all crop schedules that have been created from the input specifications.

        Raises
        ------
        ValueError
            If the crop species in the crop rotation is not in the available crop configurations.

        """
        im = InputManager()
        schedules = []
        crop_rotation_data: list[dict[str, Any]] = im.get_data(f"{crop_rotation}.crop_schedules")
        if crop_rotation_data is None:
            om = OutputManager()
            info_map = {
                "class": FieldManager.__class__.__name__,
                "function": FieldManager._setup_crop_schedules.__name__,
            }
            om.add_error("No crop rotation data", "Field data provided with empty crop rotation data.", info_map)
            raise ValueError("No crop rotation data")

        for index, rotation in enumerate(crop_rotation_data):
            crop_species = rotation["crop_species"]
            if crop_species not in available_crop_configurations:
                om = OutputManager()
                info_map = {
                    "class": FieldManager.__class__.__name__,
                    "function": FieldManager._setup_crop_schedules.__name__,
                    "crop_species": crop_species,
                    "crop_rotation": crop_rotation,
                    "crop_configurations": available_crop_configurations,
                }
                err_name = "Invalid crop species."
                err_msg = f"{crop_species=} in {crop_rotation=} not in {available_crop_configurations=}."
                om.add_error(err_name, err_msg, info_map)
                raise ValueError(f"{err_name} {err_msg}")

            if rotation["harvest_type"] == "scheduled":
                heat_scheduled_harvest = False
            else:
                heat_scheduled_harvest = True
            new_schedule = CropSchedule(
                name=f"crop_schedule_{index}",
                crop_reference=rotation["crop_species"],
                planting_years=rotation["planting_years"],
                planting_days=rotation["planting_days"],
                harvest_years=rotation["harvest_years"],
                harvest_days=rotation["harvest_days"],
                harvest_operations=rotation["harvest_operations"],
                use_heat_scheduling=heat_scheduled_harvest,
                pattern_repeat=rotation["pattern_repeat"],
                planting_skip=rotation["planting_skip"],
                harvesting_skip=rotation["harvesting_skip"],
            )
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
        im = InputManager()
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
            "albedo",
            "humus_mineralization_rate_factor",
            "denitrification_rate_coefficient",
            "denitrification_threshold_water_content",
            "residue_fresh_organic_mineralization_rate",
        ]

        for value in expected_values:
            config_dictionary[value] = soil_configuration_data.get(value)

        config_dictionary["manning"] = soil_configuration_data.get("manning_roughness_coefficient")

        soil_data = SoilData(field_size=field_size, **config_dictionary)
        return Soil(soil_data=soil_data)

    @staticmethod
    def _setup_soil_layer(
        field_size: float, top_depth: float, initial_residue: float, layer_config: dict[str, Any]
    ) -> LayerData:
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
            "pH",
            "bulk_density",
            "organic_carbon_fraction",
            "clay_fraction",
            "silt_fraction",
            "sand_fraction",
            "rock_fraction",
            "initial_labile_inorganic_phosphorus_concentration",
            "initial_soil_nitrate_concentration",
            "initial_soil_ammonium_concentration",
            "ammonium_volatilization_cation_exchange_factor",
        ]

        for value in expected_values:
            config_dictionary[value] = layer_config.get(value)

        config_dictionary["temperature"] = layer_config.get("initial_temperature")

        config_dictionary["field_size"] = field_size
        config_dictionary["top_depth"] = top_depth
        config_dictionary["residue"] = initial_residue

        layer = LayerData(**config_dictionary)
        return layer

    def check_manure_schedules(self, field: Field, time: RufasTime) -> list[ManureEventNutrientRequest]:
        """
        Checks list of ManureEvents, sends all that occur today to another method to be executed.

        Parameters
        ----------
        time : RufasTime
            RufasTime object containing the current year and day of the simulation.

        """
        manure_requests = field.check_manure_application_schedule(time)
        return manure_requests
