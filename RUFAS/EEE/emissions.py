import re
from datetime import date, datetime
from typing import Any, Literal

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS: dict[str, dict[str, Any]] = {
    "harvest_yield": {
        "name": "Farmgrown Feeds Yields",
        "description": "Collects all crop harvests that occurred in the simulation.",
        "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
        "variables": [
            "dry_yield",
            "crop",
            "harvest_year",
            "harvest_day",
            "field_name",
            "harvest_type"
        ],
        "date_fields": ("harvest_year", "harvest_day"),
    },
    "nitrous_oxide_emissions": {
        "name": "Nitrous Oxide Emissions",
        "description": "Collects the nitrous oxide emissions of all soil layers across all fields in the simulation.",
        "filters": ["FieldDataReporter.send_soil_layer_daily_variables.nitrous_oxide_emissions"],
        "date_fields": "simulation_day",
    },
    "ammonia_emissions": {
        "name": "Ammonia Emissions",
        "description": "Collects the ammonia emissions of all soil layers across all fields in the simulation.",
        "filters": ["FieldDataReporter.send_soil_layer_daily_variables.ammonia_emissions"],
        "date_fields": "simulation_day",
    },
    "fertilizer_applications": {
        "name": "Fertilizer Applications",
        "description": "Collects all synthetic fertilizer applications that occurred in the simulation.",
        "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
        "variables": [
            "nitrogen",
            "phosphorus",
            "potassium",
            "year",
            "day"
        ],
        "date_fields": ("year", "day"),
    },
    "manure_applications": {
        "name": "Manure Applications",
        "description": "Collects all manure applications that occurred in the simulation.",
        "filters": ["Field._record_manure_application\\.manure_application\\.field='.*'"],
        "variables": [
            "nitrogen",
            "year",
            "day"
        ],
        "date_fields": ("year", "day"),
    },
    "farmgrown_feed_deductions": {
        "name": "Farmgrown Feed Deductions",
        "description": "Collects all farmgrown feeds fed to animals in the simulation.",
        "filters": ["FeedManager._deduct_feeds_from_inventory.farmgrown_feed_.*_fed"],
        "date_fields": "simulation_day",
    },
}


class EmissionsEstimator:
    """
    Estimates emissions associated with purchased feeds used for animals.

    Attributes
    ----------
    im : InputManager
        An instance of the InputManager class.
    om : OutputManager
        An instance of the OutputManager class.
    crop_species_to_purchased_feed_id : dict[str, list[str]]
        A dictionary mapping crop species to their corresponding RuFaS feed IDs.
    purchased_feed_emissions_by_location : dict[str, float]
        A dictionary mapping RuFaS feed IDs to their emissions factors (kg CO2e / kg dry matter) for the location of
        the simulation.
    land_use_change_emissions_by_location : dict[str, float]
        A dictionary mapping RuFaS feed IDs to their land use change emissions factors (kg CO2e / kg dry matter) for
        the location of the simulation.
    _missing_purchased_ids : set[str]
        A set of RuFaS feed IDs that were used in the simulation but do not have purchased feed emissions data.
    _missing_land_use_ids : set[str]
        A set of RuFaS feed IDs that were used in the simulation but do not have land use change emissions data.
    """

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        county_code = self.im.get_data("config.FIPS_county_code")

        purchased_feed_emissions_data = self.im.get_data("purchased_feeds_emissions")
        self.purchased_feed_emissions_by_location = self._get_feed_emissions_data(
            county_code, purchased_feed_emissions_data
        )

        land_use_change_emissions_data = self.im.get_data("purchased_feed_land_use_change_emissions")
        self.land_use_change_emissions_by_location = self._get_feed_emissions_data(
            county_code, land_use_change_emissions_data
        )
        self._missing_purchased_ids: set[str] = set()
        self._missing_land_use_ids: set[str] = set()

        feed_storage_configs = self.im.get_data("feed_storage_configurations")
        feed_storage_instances = self.im.get_data("feed_storage_instances")

        all_configs: list[dict[str, Any]] = [
            storage_config
            for storage_config_list in feed_storage_configs.values()
            for storage_config in storage_config_list
        ]
        instance_names: list[str] = [name for names in feed_storage_instances.values() for name in names]

        self.crop_species_to_purchased_feed_id: dict[str, list[str]] = {}
        for config in all_configs:
            if config["name"] not in instance_names:
                continue
            else:
                if "crop_species" in config and "rufas_ids" in config:
                    self.crop_species_to_purchased_feed_id[config["crop_species"]] = [
                        str(rufas_id) for rufas_id in config["rufas_ids"]
                    ]

    def check_available_purchased_feed_data(self, available_feed_ids: list[int]) -> None:
        """
        Checks that all purchased feed IDs used in the simulation have emissions data available for them.
        """
        available_feeds = {str(feed_id) for feed_id in available_feed_ids}
        missing_purchased = sorted(available_feeds - set(self.purchased_feed_emissions_by_location.keys()))
        missing_land_use = sorted(available_feeds - set(self.land_use_change_emissions_by_location.keys()))
        self._missing_purchased_ids.update(missing_purchased)
        self._missing_land_use_ids.update(missing_land_use)

        if missing_purchased:
            info_map = {"class": self.__class__.__name__, "function": self.check_available_purchased_feed_data.__name__}
            self.om.add_warning(
                "Missing Purchased Feed Emissions Data",
                "Missing emissions data for RuFaS feed IDs: "
                + ", ".join(missing_purchased)
                + ". These feeds will be omitted from purchased feed emissions estimations.",
                info_map,
            )
        if missing_land_use:
            info_map = {"class": self.__class__.__name__, "function": self.check_available_purchased_feed_data.__name__}
            self.om.add_warning(
                "Missing Land Use Change Purchased Feed Emissions Data",
                "Missing land use change emissions data for RuFaS feed IDs: "
                + ", ".join(missing_land_use)
                + ". These feeds will be omitted from land use change purchased feed emissions estimations.",
                info_map,
            )

    def calculate_emissions(
        self,
        purchased_feeds: dict[int, float],
    ) -> None:
        """Calculates the emissions from purchased feeds and land use changes. If there are feed IDs with missing
        emissions factor data, they will be omitted from the calculations and not reported."""
        purchased_feed_emissions: dict[str, float] = {}
        land_use_change_emissions: dict[str, float] = {}

        for feed_id, feed_amount in purchased_feeds.items():
            stringified_feed_id = str(feed_id)

            factor = self.purchased_feed_emissions_by_location.get(stringified_feed_id)
            if factor is not None:
                purchased_feed_emissions[stringified_feed_id] = feed_amount * factor

            luc_factor = self.land_use_change_emissions_by_location.get(stringified_feed_id)
            if luc_factor is not None:
                land_use_change_emissions[stringified_feed_id] = feed_amount * luc_factor

        info_map = {
            "class": self.__class__.__name__,
            "function": self.calculate_emissions.__name__,
            "units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER,
        }
        self.om.add_variable("purchased_feed_emissions", purchased_feed_emissions, info_map)
        self.om.add_variable("land_use_change_emissions", land_use_change_emissions, info_map)

    def _get_feed_emissions_data(
        self, county_code: int, feed_emissions_data: dict[str, list[float]]
    ) -> dict[str, float]:
        """Grabs the appropriate list of emissions for purchased feeds for the location of the simulation."""
        county_codes = feed_emissions_data["county_code"]
        try:
            emissions_index = county_codes.index(county_code)
        except ValueError as e:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._get_feed_emissions_data.__name__,
            }
            self.om.add_error(
                "Invalid country code access.",
                f"Emission data have county codes {county_codes}," f"Tried to get data with county code: {county_code}",
                info_map,
            )
            raise e

        feed_keys = [key for key in feed_emissions_data.keys() if key != "county_code"]
        feed_emissions_dict = {key: feed_emissions_data[key][emissions_index] for key in feed_keys}

        return feed_emissions_dict

    def estimate_emissions(self) -> None:
        """Estimates emissions associated with farmgrown feeds."""
        result = self._gather_farmgrown_feeds_emissions_and_resources_data()

    def _gather_farmgrown_feeds_emissions_and_resources_data(
        self,
    ) -> dict[str, dict[int, dict[str, Any]]] | dict[str, dict[str, dict[int, float]]]:
        """
        Gathers the yields that were harvested and fertilizer applications applied in the simulation.
        """
        result: dict[str, dict[int, dict[str, Any]]] | dict[str, dict[str, dict[int, float]]] = {
            attribute: {} for attribute in FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS
        }
        simulation_start_date: datetime = datetime.strptime(str(self.im.get_data("config.start_date")), "%Y:%j")
        for attribute, om_filter in FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS.items():
            filtered_data = self.om.filter_variables_pool(om_filter)
            date_field: str | tuple[str, str] = om_filter["date_fields"]
            if isinstance(date_field, tuple):
                year_key, day_key = date_field[0], date_field[1]
                dates = list(
                    map(
                        RufasTime.convert_year_jday_to_date,
                        filtered_data[year_key]["values"],
                        filtered_data[day_key]["values"]
                    )
                )
                simulation_days = [(event_date - simulation_start_date).days for event_date in dates]
                for i, simulation_day in enumerate(simulation_days):
                    result[attribute][simulation_day] = {
                        variable: filtered_data[variable]["values"][i]
                        for variable in filtered_data if variable not in [year_key, day_key, "DISCLAIMER"]
                    }

            elif date_field == "simulation_day":
                if attribute in ["nitrous_oxide_emissions", "ammonia_emissions"]:
                    all_fields_by_layer: dict[str, dict[int, dict[int, float]]] = {}
                    for variable, values in filtered_data.items():
                        match = re.search(r"field='([^']+)',layer='(\d+)'", variable)
                        if match:
                            field_name, layer_number = match.group(1), int(match.group(2))
                        else:
                            raise ValueError("No match found.")
                        if field_name not in all_fields_by_layer:
                            all_fields_by_layer[field_name] = {}
                        all_fields_by_layer[field_name][layer_number] = {
                            info_map["simulation_day"]: values["values"][i]
                            for i, info_map in enumerate(values["info_maps"])
                        }

                    for field_name in all_fields_by_layer:
                        simulation_days = {
                            day for layer_data in all_fields_by_layer[field_name].values() for day in layer_data
                        }

                        result[attribute][field_name] = {
                            simulation_day: sum(
                                layer_data.get(simulation_day, 0)
                                for layer_data in all_fields_by_layer[field_name].values()
                            ) for simulation_day in simulation_days
                        }
                elif attribute == "farmgrown_feed_deductions":
                    for variable, values in filtered_data.items():
                        match = re.search(r"farmgrown_feed_(\d+)_fed", variable)
                        if match:
                            feed_id = int(match.group(1))
                        else:
                            raise ValueError("No match found.")
                        result[attribute][feed_id] = {
                            info_map["simulation_day"]: values["values"][i]
                            for i, info_map in enumerate(values["info_maps"])
                        }
                else:
                    raise ValueError(f"Unknown filter key: {attribute}")
            else:
                raise ValueError(f"Invalid date field: {date_field}")
        return result

    def _transform_outputs_to_list_of_dicts(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Transforms dictionary of lists collected from the Output Manager into list of dictionaries.

        Examples
        --------
        >>> a = {'one': {'values': [1, 2, 3]}, 'two': {'values': [4, 5, 6]}}
        >>> _transform_outputs_to_list_of_dicts(a)
        [{'one': 1, 'two': 4}, {'one': 2, 'two': 5}, {'one': 3, 'two': 6}]

        """
        pass

    def _calculate_total_homegrown_feed_amounts_by_crop_type(
        self, homegrown_feeds: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Calculates the total amount of each crop species grown on the farm."""
        pass

    def _calculate_homegrown_feed_emissions(
        self,
        homegrown_feeds: list[dict[str, Any]],
        fertilizer_applications: list[dict[str, Any]],
        manure_applications: list[dict[str, Any]],
        manure_requests: list[dict[str, Any]],
    ) -> None:
        """Calculates the emissions associated with feeds grown on the farm."""
        pass

    def _collect_target_soil_characteristics(self, field_names: list[str]) -> dict[str, dict[str, Any]]:
        """Collects the emissions and soil carbon characteristics used to calculate farm-grown feed emissions."""
        pass

    def _calculate_emissions_by_field(
        self,
        field_name: str,
        feeds_grown: list[dict[str, Any]],
        field_emissions: dict[str, float],
        manure_applications: dict[str, float],
        manure_requests: dict[str, float],
        fertilizer_applications_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Partitions emissions from the field where crops/feeds were grown to those crops.
        """
        pass

    def _partition_applied_crop_fertilizer_emissions(
        self, fertilizer_application: dict[str, float], applied_crops: list[dict[str, Any]]
    ) -> None:
        """
        Partitions synthetic emissions from fertilizer applications to crop(s) whose planting and harvesting dates
        encompass the fertilizer application date.
        """
        pass

    def _filter_results(
        self, filters: dict[str, Any], date_cutoff: date, year_key: str, day_key: str
    ) -> list[dict[str, Any]]:
        """
        This method help with filtering data based on the timeframe provided.

        Parameters
        ----------
        filters: dict[str, Any]
            A filter to collect the desired data from OutputManager.
        date_cutoff: datetime
            Date before which all data collected from the Output Manager is filtered out.
        year_key: str
            How the key is named for the year data retrieved from OM.
        day_key: str
            How the key is named for the day data retrieved from OM.

        Returns
        -------
        list[dict[str, Any]]
            Filtered result of the retrieved data.

        """
        pass

    def _aggregate_data(
        self, operations: list[dict[str, Any]], all_fields: list[str], nutrients: list[str]
    ) -> dict[str, dict[str, float]]:
        """
        Aggregate nutrient data for different types of applications (fertilizer, manure, etc.).

        Parameters
        ----------
        operations : list[dict[str, Any]]
            A list of application dictionaries. Each dictionary contains the field name and nutrient amounts.
            Example: {"field_name": "Field1", "nitrogen": 50.0, "phosphorus": 20.0}
        all_fields : list[str]
            A list of field names to aggregate data for, usually combining fields with crops and fields with
            applications.
        nutrients : list[str]
            A list of nutrient keys to aggregate (e.g., ["nitrogen", "phosphorus", "potassium"]).

        Returns
        -------
        dict
            A dictionary where keys are field names and values are dictionaries of aggregated nutrient values.

        """
        pass

    def _apply_fertilizer_to_next_crop(
        self,
        fertilizer_application: dict[str, Any],
        sorted_crops: list[dict[str, Any]],
        fertilizer_application_date: date,
    ) -> bool:
        """
        Applies fertilizer to the next available crop after harvest and before the next planting.
        Returns True if fertilizer was applied, False otherwise.
        """
        pass

    def _extract_applied_crops(
        self, sorted_crops: list[dict[str, Any]], fertilizer_application_date: date
    ) -> list[dict[str, Any]]:
        """Extracts a list of crops that had fertilizer applied to them between their planting and harvesting dates.

        Parameters
        ----------
        sorted_crops : list[dict[str, Any]]
            The list of crops in the field sorted by planting date.
        fertilizer_application_date : date
            The date of the fertilizer applciation.

        Returns
        -------
        list[dict[str, Any]]
            A list of the crops whose planting and harvesting dates encompass the fertilizer application date.
        """
        pass

    def _soil_data_update(self, filters: dict[str, dict[str, Any]]) -> dict[str, int | Literal[0]]:
        """
        This method will update the soil data update according to data extracted using the filters.

        Parameters
        ----------
        filters: dict[str, dict[str, Any]]
            A dictionary of filters to retrieve data from the OM.

        Return
        ------
        dict[str, int | Literal[0]]
            The updated soil data.

        """
        pass
