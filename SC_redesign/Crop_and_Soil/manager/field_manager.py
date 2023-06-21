from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time
from RUFAS.util import Utility
from SC_redesign.Crop_and_Soil.crop_and_soil_constants import HECTARES_TO_SQUARE_MILLIMETERS, \
    CUBIC_MILLIMETERS_TO_CUBIC_METERS, MEGAGRAMS_TO_KILOGRAMS
from SC_redesign.Crop_and_Soil.soil.soil import Soil
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from SC_redesign.Crop_and_Soil.manager.fertilizer_schedule import FertilizerSchedule
from SC_redesign.Crop_and_Soil.manager.manure_schedule import ManureSchedule
from SC_redesign.Crop_and_Soil.manager.tillage_schedule import TillageSchedule
from typing import Dict, List, Tuple


class FieldManager:
    def __init__(self, fields_config: List[Dict[str, str]]):
        self.fields: List[Field] = []
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

        soil_config = Utility.read_json_file(input_directory / 'soil' / field_config['soil'])
        crops_config = Utility.read_json_file(input_directory / 'crop' / field_config['crop'])
        management_config = \
            Utility.read_json_file(input_directory / 'field_management' / field_config['field_management'])

        available_fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule = \
            FieldManager._setup_management(field_name, management_config)

        return Field()

    @staticmethod
    def _setup_soil(soil_config: Dict[str]) -> Soil:
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

        config_dictionary = {}

        config_dictionary["second_moisture_condition_parameter"] = soil_config.get("CN2")
        config_dictionary["average_subbasin_slope"] = soil_config.get("field_slope")
        config_dictionary["slope_length"] = soil_config.get("slope_length")
        config_dictionary["manning"] = soil_config.get("manning")
        config_dictionary["albedo"] = soil_config.get("soil_albedo")
        config_dictionary["cover_type"] = soil_config.get("soil_cover_type")

        soil_layers_config = list(config_dictionary.get("soil_layers"))
        pass

    @staticmethod
    def _setup_soil_layer(top_depth: float, sand: float, silt: float, initial_residue: float,
                          layer_config: Dict) -> LayerData:
        """
        Initializes a LayerData instance to be added to a SoilData object.

        Parameters
        ----------
        top_depth : float
            Depth of top of the soil layer beneath the surface (mm)
        sand : float
            Sand content expressed as percent of soil in this layer (unitless)
        silt : float
            Silt content expressed as percent of soil in this layer (unitless)
        initial_residue : float
            Amount of residue on the soil surface when this soil layer is initialized (kg / ha)
        layer_config

        Returns
        -------
        LayerData
            LayerData instance configured with provided data.

        """
        config_dictionary = {}

        config_dictionary["top_depth"] = top_depth
        config_dictionary["bottom_depth"] = layer_config["bottom_depth"]
        config_dictionary["wilting_point_water_concentration"] = layer_config.get("wilting_point")
        config_dictionary["field_capacity_water_concentration"] = layer_config.get("field_capacity")
        config_dictionary["saturation_point_water_concentration"] = layer_config.get("saturation")
        config_dictionary["saturated_hydraulic_conductivity"] = layer_config.get("K_sat")
        config_dictionary["percent_clay_content"] = layer_config.get("clay")
        config_dictionary["temperature"] = layer_config.get("initial_temperature")
        config_dictionary["bulk_density"] = layer_config["bulk_density"]
        config_dictionary["percent_organic_carbon_content"] = layer_config["org_C_percent"]
        config_dictionary["initial_soil_nitrate_concentration"] = layer_config["NO3"]

    @staticmethod
    def convert_depth_to_kilograms(depth: float, area: float, density: float) -> float:
        """
        Converts a quantity expressed as a depth to kilograms.

        Parameters
        ----------
        depth : float
            Depth of the quantity being converted (mm)
        area : float
            Area over which the quantity is distributed (ha)
        density : float
            The mass per volume of the stuff over which the quantity is distributed (Megagrams / cubic meter)

        Returns
        -------
        float
            The quantity passed converted to kilograms.

        """
        area_in_mm = area * HECTARES_TO_SQUARE_MILLIMETERS
        quantity_in_cubic_mm = depth * area_in_mm
        quantity_in_cubic_meters = quantity_in_cubic_mm * CUBIC_MILLIMETERS_TO_CUBIC_METERS
        quantity_in_megagrams = quantity_in_cubic_meters * density
        quantity_in_kilograms = quantity_in_megagrams * MEGAGRAMS_TO_KILOGRAMS
        return quantity_in_kilograms

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

        tillage_config = manure_config.get("tillage")
        tillage_schedule_name = field_name + "_tillage_schedule"
        tillage_schedule = TillageSchedule(name=tillage_schedule_name,
                                           years=tillage_config.get("year"),
                                           days=tillage_config.get("day"),
                                           tillage_depths=tillage_config.get("depth"),
                                           incorporation_fractions=tillage_config.get("percent_incorporated"),
                                           mixing_fractions=tillage_config.get("percent_mixed"),
                                           pattern_repeat=tillage_config.get("repeat"))

        return fertilizer_mixes, fertilizer_schedule, manure_schedule, tillage_schedule
