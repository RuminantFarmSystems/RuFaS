import re
from collections import defaultdict
from datetime import datetime
from typing import Any

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
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
        "variables": ["dry_yield", "crop", "harvest_year", "harvest_day", "field_name", "harvest_type"],
        "date_fields": ("harvest_year", "harvest_day"),
        "use_filter_key_name": True,
    },
    "nitrous_oxide_emissions": {
        "name": "Nitrous Oxide Emissions",
        "description": "Collects the nitrous oxide emissions of all soil layers across all fields in the simulation.",
        "filters": [
            "FieldDataReporter.send_soil_layer_daily_variables.nitrous_oxide_emissions",
            ".*RufasTime.simulation_day.*",
        ],
        "date_fields": "simulation_day",
        "use_filter_key_name": True,
    },
    "ammonia_emissions": {
        "name": "Ammonia Emissions",
        "description": "Collects the ammonia emissions of all soil layers across all fields in the simulation.",
        "filters": [
            "FieldDataReporter.send_soil_layer_daily_variables.ammonia_emissions",
            ".*RufasTime.simulation_day.*",
        ],
        "date_fields": "simulation_day",
        "use_filter_key_name": True,
    },
    "fertilizer_applications": {
        "name": "Fertilizer Applications",
        "description": "Collects all synthetic fertilizer applications that occurred in the simulation.",
        "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
        "variables": ["nitrogen", "phosphorus", "potassium", "field_name", "field_size", "year", "day"],
        "date_fields": ("year", "day"),
        "use_filter_key_name": True,
    },
    "manure_applications": {
        "name": "Manure Applications",
        "description": "Collects all manure applications that occurred in the simulation.",
        "filters": ["Field._record_manure_application\\.manure_application\\.field='.*'"],
        "variables": ["nitrogen", "field_name", "field_size", "year", "day"],
        "date_fields": ("year", "day"),
        "use_filter_key_name": True,
    },
    "crop_received": {
        "name": "Crop Received",
        "description": "Collects all crop received events that occurred in the simulation.",
        "filters": ["Feed.*.crop_received"],
        "variables": [
            "field_name",
            "crop_name",
            "feed_id",
        ],
        "use_filter_key_name": True,
    },
    "farmgrown_feed_deductions": {
        "name": "Farmgrown Feed Deductions",
        "description": "Collects all farmgrown feeds fed to animals in the simulation.",
        "filters": ["FeedManager._log_feed_deductions.farmgrown_feed_.*_fed"],
        "date_fields": "simulation_day",
        "use_filter_key_name": True,
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

    def calculate_purchased_feed_emissions(
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
            "function": self.calculate_purchased_feed_emissions.__name__,
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

    def estimate_farmgrown_feed_emissions(self) -> None:
        """Estimates the emissions and resources used associated with farmgrown feeds production."""
        config_data = self.im.get_data("config")
        simulation_start_date: datetime = datetime.strptime(str(config_data["start_date"]), "%Y:%j")
        simulation_end_date: datetime = datetime.strptime(str(config_data["end_date"]), "%Y:%j")
        all_simulation_days = list(range(0, (simulation_end_date - simulation_start_date).days + 1))

        emission_data = self._parse_farmgrown_feeds_emission_data()

        resource_data = self._parse_manure_and_fertilizer_application_data(simulation_start_date)

        crop_to_feed_id_mapping = self._parse_crop_to_feed_id_mapping()

        harvest_yield_data = self._parse_harvest_data(crop_to_feed_id_mapping, simulation_start_date)

        feed_deductions_data = self._parse_farmgrown_feed_deductions_data(all_simulation_days)

        daily_farmgrown_feed_emissions_and_resources = self._calculate_daily_farmgrown_feed_emissions_and_resources(
            emission_data, resource_data, harvest_yield_data, all_simulation_days
        )

        daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id = (
            self._calculate_daily_farmgrown_feed_fed_emissions_and_resources(
                daily_farmgrown_feed_emissions_and_resources, feed_deductions_data, all_simulation_days
            )
        )

        self._report_daily_farmgrown_feed_fed_emissions_and_resources(
            daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id
        )

        farm_grown_feeds_fed_to_animals = list(daily_farmgrown_feed_fed_emissions_and_resources_by_feed_id.keys())
        self._calculate_and_report_lca_emissions(farm_grown_feeds_fed_to_animals, feed_deductions_data)

    def _parse_farmgrown_feeds_emission_data(self) -> dict[str, dict[str, dict[int, float]]]:
        """
        Parses farmgrown feeds emission data from the OutputManager and returns a dictionary with emission data for
        each field on every simulation day.

        Notes
        -----
        The farmgrown feeds Nitrous Oxide and Ammonia emission data has unit kg/ha.
        """
        emission_data: dict[str, dict[str, dict[int, float]]] = defaultdict(dict)
        for filter_key in ["nitrous_oxide_emissions", "ammonia_emissions"]:
            filtered_data = self.om.filter_variables_pool(FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS[filter_key])
            all_fields_by_layer: dict[str, dict[int, dict[int, float]]] = defaultdict(dict)
            simulation_days: list[int] = filtered_data["RufasTime.simulation_day"]["values"]
            for variable, values in filtered_data.items():
                if variable == "RufasTime.simulation_day":
                    continue
                match = re.search(r"field='([^']+)',layer='(\d+)'", variable)
                if match:
                    field_name, layer_number = match.group(1), int(match.group(2))
                else:
                    raise ValueError(f"No field name and layer match found for {variable}.")
                if field_name not in all_fields_by_layer:
                    all_fields_by_layer[field_name] = {}

                all_fields_by_layer[field_name][layer_number] = dict(zip(simulation_days, values["values"]))
            for field_name in all_fields_by_layer:
                emission_data[filter_key][field_name] = {
                    simulation_day: sum(
                        layer_data.get(simulation_day, 0) for layer_data in all_fields_by_layer[field_name].values()
                    )
                    for simulation_day in simulation_days
                }
        return emission_data

    def _parse_manure_and_fertilizer_application_data(
        self,
        simulation_start_date: datetime,
    ) -> dict[str, dict[str, dict[int, dict[str, float]]]]:
        """
        Parses manure and fertilizer application data from the OutputManager and returns a dictionary with
        application data for each field by simulation day.

        Notes
        -----
        The manure and fertilizer application data has unit kg/ha.
        """
        resource_data: dict[str, dict[str, dict[int, dict[str, float]]]] = defaultdict(dict)
        for filter_key in ["manure_applications", "fertilizer_applications"]:
            resource_filter = FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS[filter_key]
            filtered_data = self.om.filter_variables_pool(resource_filter)

            if len(filtered_data) == 0:
                continue

            date_field: tuple[str, str] = resource_filter["date_fields"]
            year_key, day_key = date_field[0], date_field[1]
            dates = list(
                map(
                    RufasTime.convert_year_jday_to_date,
                    filtered_data[year_key]["values"],
                    filtered_data[day_key]["values"],
                )
            )
            simulation_days = [(event_date - simulation_start_date).days for event_date in dates]
            for i, simulation_day in enumerate(simulation_days):
                field_name = filtered_data["field_name"]["values"][i]
                field_size: float = filtered_data["field_size"]["values"][i]
                if field_name not in resource_data[filter_key]:
                    resource_data[filter_key][field_name] = {}
                resource_data[filter_key][field_name][simulation_day] = {
                    variable: filtered_data[variable]["values"][i] / field_size
                    for variable in filtered_data
                    if variable not in [year_key, day_key, "field_name", "field_size", "DISCLAIMER"]
                }

        return resource_data

    def _parse_farmgrown_feed_deductions_data(
        self,
        all_simulation_days: list[int],
    ) -> dict[RUFAS_ID, dict[int, float]]:
        """Parses farmgrown feed deductions data by feed_id and simulation day from the simulation OutputManager."""
        filtered_data = self.om.filter_variables_pool(
            FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS["farmgrown_feed_deductions"]
        )
        feed_deduction_by_feed_id: dict[RUFAS_ID, dict[int, float]] = defaultdict(dict)
        for variable_name, variable_contents in filtered_data.items():
            match = re.search(r"farmgrown_feed_(\d+)_fed", variable_name)
            if match:
                feed_id = int(match.group(1))
            else:
                raise ValueError(f"No feed_id match found for {variable_name}.")
            values_list = variable_contents.get("values", [])

            matched = {values_list[i]["simulation_day"]: values_list[i]["amount"] for i in range(len(values_list))}

            feed_deduction_by_feed_id[feed_id] = {day: matched.get(day, 0.0) for day in all_simulation_days}

            feed_deduction_by_feed_id[feed_id] = dict(sorted(feed_deduction_by_feed_id[feed_id].items()))

        return feed_deduction_by_feed_id

    def _parse_crop_to_feed_id_mapping(self) -> dict[tuple[str, str], RUFAS_ID]:
        """Parses the mapping of crop names and field names to RUFAS feed IDs."""
        raw_received_crop_data = self.om.filter_variables_pool(
            FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS["crop_received"]
        )
        received_crop_dict = {key: values["values"] for key, values in raw_received_crop_data.items()}
        received_crop_list = Utility.convert_dict_of_lists_to_list_of_dicts(received_crop_dict)
        crop_to_feed_id_mapping = {
            (datapoint["field_name"], datapoint["crop_name"]): datapoint["feed_id"] for datapoint in received_crop_list
        }
        return crop_to_feed_id_mapping

    def _parse_harvest_data(
        self, crop_to_feed_id_mapping: dict[tuple[str, str], RUFAS_ID], simulation_start_date: datetime
    ) -> dict[str, dict[int, dict[str, Any]]]:
        """
        Parses harvest data by field name and simulation day from the simulation OutputManager.

        Notes
        -----
        The harvest dry yield data has unit kg/ha.
        """
        harvest_data: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)

        harvest_filter = FARMGROWN_FEEDS_EMISSIONS_AND_RESOURCES_FILTERS["harvest_yield"]
        filtered_data = self.om.filter_variables_pool(harvest_filter)
        if len(filtered_data) == 0:
            return harvest_data
        date_field: tuple[str, str] = harvest_filter["date_fields"]
        year_key, day_key = date_field[0], date_field[1]
        for i, field_name in enumerate(filtered_data["field_name"]["values"]):
            crop_name = filtered_data["crop"]["values"][i]
            feed_id = crop_to_feed_id_mapping.get((field_name, crop_name), None)
            harvest_dry_yield_data = filtered_data["dry_yield"]["values"][i]
            harvest_type = filtered_data["harvest_type"]["values"][i]
            harvest_year, harvest_day = filtered_data[year_key]["values"][i], filtered_data[day_key]["values"][i]
            harvest_simulation_day = (
                RufasTime.convert_year_jday_to_date(harvest_year, harvest_day) - simulation_start_date
            ).days

            harvest_data[field_name][harvest_simulation_day] = {
                "field_name": field_name,
                "crop": crop_name,
                "feed_id": feed_id,
                "dry_yield": harvest_dry_yield_data,
                "harvest_type": harvest_type,
            }

        return harvest_data

    def _calculate_daily_farmgrown_feed_emissions_and_resources(
        self,
        emission_data: dict[str, dict[str, dict[int, float]]],
        resource_data: dict[str, dict[str, dict[int, dict[str, float]]]],
        harvest_yield_by_field: dict[str, dict[int, dict[str, Any]]],
        all_simulation_days: list[int],
    ) -> dict[RUFAS_ID, dict[int, dict[str, float]]]:
        """
        Calculates daily emissions and resources used for farmgrown feeds production.

        Parameters
        ----------
        emission_data : dict[str, dict[str, dict[int, float]]]
            The Nitrous Oxide and Ammonia emission data for farmgrown feeds, (kg/ha).
        resource_data : dict[str, dict[str, dict[int, dict[str, float]]]]
            The manure and fertilizer application data for farmgrown feeds, (kg/ha).
        harvest_yield_by_field : dict[str, dict[int, dict[str, Any]]]
            The harvest dry yield data for farmgrown feeds, (kg/ha).
        all_simulation_days : list[int]
            A list of all simulation days.

        Returns
        -------
        dict[RUFAS_ID, dict[int, dict[str, float]]]
            The calculated daily emissions and resources used for farmgrown feeds production.
        """

        total_farmgrown_feed_emission_and_resource_by_feed_id: dict[RUFAS_ID, dict[str, float]] = defaultdict(dict)
        total_harvest_dry_yield_by_feed_id: dict[RUFAS_ID, float] = defaultdict(float)
        daily_farmgrown_feed_emission_and_resource_by_feed_id: dict[RUFAS_ID, dict[int, dict[str, float]]] = (
            defaultdict(dict)
        )

        harvest_dates_by_feed_id = self._calculate_harvest_dates_by_feed_id(harvest_yield_by_field)

        for field_name in harvest_yield_by_field:
            harvest_dates = sorted(list(harvest_yield_by_field[field_name].keys()))
            last_harvest_date = -1
            for harvest_date in harvest_dates:
                feed_id = harvest_yield_by_field[field_name][harvest_date]["feed_id"]
                if feed_id is None:
                    last_harvest_date = harvest_date
                    continue
                if feed_id not in total_farmgrown_feed_emission_and_resource_by_feed_id:
                    total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id] = {
                        "nitrous_oxide_emissions": 0.0,
                        "ammonia_emissions": 0.0,
                        "fertilizer_N": 0.0,
                        "fertilizer_P": 0.0,
                        "fertilizer_K": 0.0,
                        "manure_N": 0.0,
                    }
                total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["nitrous_oxide_emissions"] += sum(
                    [
                        emission_data["nitrous_oxide_emissions"][field_name][simulation_day]
                        for simulation_day in emission_data["nitrous_oxide_emissions"][field_name]
                        if last_harvest_date < simulation_day <= harvest_date
                    ],
                    start=0.0,
                )
                total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["ammonia_emissions"] += sum(
                    [
                        emission_data["ammonia_emissions"][field_name][simulation_day]
                        for simulation_day in emission_data["ammonia_emissions"][field_name]
                        if last_harvest_date < simulation_day <= harvest_date
                    ],
                    start=0.0,
                )
                if field_name in resource_data.get("fertilizer_applications", {}):
                    total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["fertilizer_N"] += sum(
                        [
                            resource_data["fertilizer_applications"][field_name][simulation_day]["nitrogen"]
                            for simulation_day in resource_data["fertilizer_applications"][field_name]
                            if last_harvest_date < simulation_day <= harvest_date
                        ],
                        start=0.0,
                    )
                    total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["fertilizer_P"] += sum(
                        [
                            resource_data["fertilizer_applications"][field_name][simulation_day]["phosphorus"]
                            for simulation_day in resource_data["fertilizer_applications"][field_name]
                            if last_harvest_date < simulation_day <= harvest_date
                        ],
                        start=0.0,
                    )
                    total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["fertilizer_K"] += sum(
                        [
                            resource_data["fertilizer_applications"][field_name][simulation_day]["potassium"]
                            for simulation_day in resource_data["fertilizer_applications"][field_name]
                            if last_harvest_date < simulation_day <= harvest_date
                        ],
                        start=0.0,
                    )
                if field_name in resource_data.get("manure_applications", {}):
                    total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]["manure_N"] += sum(
                        [
                            resource_data["manure_applications"][field_name][simulation_day]["nitrogen"]
                            for simulation_day in resource_data["manure_applications"][field_name]
                            if last_harvest_date < simulation_day <= harvest_date
                        ],
                        start=0.0,
                    )

                next_harvest_date_for_feed_id = (
                    harvest_dates_by_feed_id[feed_id][harvest_dates_by_feed_id[feed_id].index(harvest_date) + 1]
                    if harvest_dates_by_feed_id[feed_id].index(harvest_date) + 1
                    < len(harvest_dates_by_feed_id[feed_id])
                    else max(all_simulation_days)
                )

                total_harvest_dry_yield_by_feed_id[feed_id] += harvest_yield_by_field[field_name][harvest_date][
                    "dry_yield"
                ]
                total_dry_yield = total_harvest_dry_yield_by_feed_id[feed_id]
                total_emission_and_resource = total_farmgrown_feed_emission_and_resource_by_feed_id[feed_id]
                for simulation_day in range(harvest_date, next_harvest_date_for_feed_id + 1):
                    daily_farmgrown_feed_emission_and_resource_by_feed_id[feed_id][simulation_day] = {
                        "nitrous_oxide_emissions": (
                            total_emission_and_resource["nitrous_oxide_emissions"] / total_dry_yield
                        ),
                        "ammonia_emissions": (total_emission_and_resource["ammonia_emissions"] / total_dry_yield),
                        "fertilizer_N": (total_emission_and_resource["fertilizer_N"] / total_dry_yield),
                        "fertilizer_P": (total_emission_and_resource["fertilizer_P"] / total_dry_yield),
                        "fertilizer_K": (total_emission_and_resource["fertilizer_K"] / total_dry_yield),
                        "manure_N": (total_emission_and_resource["manure_N"] / total_dry_yield),
                    }

                last_harvest_date = harvest_date
        for (
            feed_id,
            daily_farmgrown_feed_emission_and_resource,
        ) in daily_farmgrown_feed_emission_and_resource_by_feed_id.items():
            remaining_days = [
                remaining_day
                for remaining_day in all_simulation_days
                if remaining_day not in daily_farmgrown_feed_emission_and_resource
            ]
            for remaining_day in remaining_days:
                daily_farmgrown_feed_emission_and_resource_by_feed_id[feed_id][remaining_day] = {
                    "nitrous_oxide_emissions": 0.0,
                    "ammonia_emissions": 0.0,
                    "fertilizer_N": 0.0,
                    "fertilizer_P": 0.0,
                    "fertilizer_K": 0.0,
                    "manure_N": 0.0,
                }
            daily_farmgrown_feed_emission_and_resource_by_feed_id[feed_id] = dict(
                sorted(daily_farmgrown_feed_emission_and_resource_by_feed_id[feed_id].items())
            )
        return daily_farmgrown_feed_emission_and_resource_by_feed_id

    def _calculate_harvest_dates_by_feed_id(
        self, harvest_yield_by_field: dict[str, dict[int, dict[str, Any]]]
    ) -> dict[RUFAS_ID, list[int]]:
        """
        Generates a mapping of feed IDs to their respective harvest dates based on the
        harvest data of multiple fields.

        Parameters
        ----------
        harvest_yield_by_field : dict: dict[str, dict[int, dict[str, Any]]]
            A dictionary containing harvest data organized by field name. Each field
            name maps to another dictionary where keys represent harvest dates, and
            values are dictionaries containing details like "feed_id".

        Returns
        -------
        dict: dict[RUFAS_ID, list[int]]
            A dictionary where each key is a feed ID, and the value is a sorted list
            of harvest dates associated with that feed ID.
        """
        all_feed_ids = set(
            harvest_yield_by_field[field_name][harvest_date]["feed_id"]
            for field_name in harvest_yield_by_field
            for harvest_date in sorted(list(harvest_yield_by_field[field_name].keys()))
        )
        harvest_dates_by_feed_id = {}
        for feed_id in all_feed_ids:
            harvest_dates = []
            for field_name in harvest_yield_by_field:
                for harvest_date in harvest_yield_by_field[field_name]:
                    if harvest_yield_by_field[field_name][harvest_date]["feed_id"] == feed_id:
                        harvest_dates.append(harvest_date)
            harvest_dates_by_feed_id[feed_id] = sorted(harvest_dates)
        return harvest_dates_by_feed_id

    def _calculate_daily_farmgrown_feed_fed_emissions_and_resources(
        self,
        daily_farmgrown_feed_emissions_and_resources: dict[RUFAS_ID, dict[int, dict[str, float]]],
        feed_deductions_data: dict[RUFAS_ID, dict[int, float]],
        all_simulation_days: list[int],
    ) -> dict[RUFAS_ID, dict[int, dict[str, float]]]:
        """Calculates daily farmgrown feed emissions and resources used for farmgrown feeds fed to the animals."""
        daily_farmgrown_feed_fed_emissions_and_resources: dict[RUFAS_ID, dict[int, dict[str, float]]] = defaultdict(
            dict
        )
        for feed_id, feed_deductions in feed_deductions_data.items():
            if feed_id not in daily_farmgrown_feed_emissions_and_resources:
                continue
            for simulation_day in all_simulation_days:
                feed_deduction = feed_deductions.get(simulation_day, 0.0)
                data_for_feed_id_for_day = daily_farmgrown_feed_emissions_and_resources[feed_id][simulation_day]
                daily_farmgrown_feed_fed_emissions_and_resources[feed_id][simulation_day] = {
                    "nitrous_oxide_emissions": data_for_feed_id_for_day["nitrous_oxide_emissions"] * feed_deduction,
                    "ammonia_emissions": data_for_feed_id_for_day["ammonia_emissions"] * feed_deduction,
                    "fertilizer_N": data_for_feed_id_for_day["fertilizer_N"] * feed_deduction,
                    "fertilizer_P": data_for_feed_id_for_day["fertilizer_P"] * feed_deduction,
                    "fertilizer_K": data_for_feed_id_for_day["fertilizer_K"] * feed_deduction,
                    "manure_N": data_for_feed_id_for_day["manure_N"] * feed_deduction,
                }
        return daily_farmgrown_feed_fed_emissions_and_resources

    def _report_daily_farmgrown_feed_fed_emissions_and_resources(
        self,
        daily_farmgrown_feed_fed_emissions_and_resources: dict[RUFAS_ID, dict[int, dict[str, float]]],
    ) -> None:
        """Reports the emissions and resources for daily farmgrown feeds fed to the animals."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._report_daily_farmgrown_feed_fed_emissions_and_resources.__name__,
        }
        for feed_id, daily_data_for_feed_id in daily_farmgrown_feed_fed_emissions_and_resources.items():
            n2o_emissions_outputs = [
                (
                    {f"direct_n2o_nitrogen_emissions_for_feed_{feed_id}": data_for_day["nitrous_oxide_emissions"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(n2o_emissions_outputs, first_info_map_only=False)

            ammonia_emissions_outputs = [
                (
                    {f"ammonia_nitrogen_emissions_for_feed_{feed_id}": data_for_day["ammonia_emissions"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(ammonia_emissions_outputs, first_info_map_only=False)

            fertilizer_N_outputs = [
                (
                    {f"nitrogen_fertilizer_applied_for_feed_{feed_id}": data_for_day["fertilizer_N"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(fertilizer_N_outputs, first_info_map_only=False)

            fertilizer_P_outputs = [
                (
                    {f"phosphorus_fertilizer_applied_for_feed_{feed_id}": data_for_day["fertilizer_P"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(fertilizer_P_outputs, first_info_map_only=False)

            fertilizer_K_outputs = [
                (
                    {f"potassium_fertilizer_applied_for_feed_{feed_id}": data_for_day["fertilizer_K"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(fertilizer_K_outputs, first_info_map_only=False)

            manure_N_outputs = [
                (
                    {f"manure_nitrogen_applied_for_feed_{feed_id}": data_for_day["manure_N"]},
                    {**info_map, "units": MeasurementUnits.KILOGRAMS, "simulation_day": simulation_day},
                )
                for simulation_day, data_for_day in daily_data_for_feed_id.items()
            ]
            self.om.add_variable_bulk(manure_N_outputs, first_info_map_only=False)

    def _calculate_and_report_lca_emissions(
        self, farm_grown_feeds_fed_to_animals: list[RUFAS_ID], feed_deductions_data: dict[RUFAS_ID, dict[int, float]]
    ) -> None:
        """Calculates and reports LCA and Land-Use-Change emissions."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self._calculate_and_report_lca_emissions.__name__,
            "units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ,
        }

        lca_emissions_by_simulation_day: dict[int, dict[RUFAS_ID, float]] = defaultdict(dict)
        luc_emissions_by_simulation_day: dict[int, dict[RUFAS_ID, float]] = defaultdict(dict)
        for feed_id in farm_grown_feeds_fed_to_animals:
            feed_deductions_for_feed_id_by_simulation_day = feed_deductions_data[feed_id]

            lca_factor = self.purchased_feed_emissions_by_location.get(str(feed_id))
            if lca_factor is not None:
                for simulation_day, feed_amount in feed_deductions_for_feed_id_by_simulation_day.items():
                    lca_emissions_by_simulation_day[simulation_day].update({feed_id: feed_amount * lca_factor})
                lca_outputs = [
                    (
                        {f"lca_carbon_emissions_for_feed_{feed_id}": lca_emissions_for_day[feed_id]},
                        {**info_map, "simulation_day": simulation_day},
                    )
                    for simulation_day, lca_emissions_for_day in lca_emissions_by_simulation_day.items()
                ]
                self.om.add_variable_bulk(lca_outputs, first_info_map_only=False)

            luc_factor = self.land_use_change_emissions_by_location.get(str(feed_id))
            if luc_factor is not None:
                for simulation_day, feed_amount in feed_deductions_for_feed_id_by_simulation_day.items():
                    luc_emissions_by_simulation_day[simulation_day].update({feed_id: feed_amount * luc_factor})
                luc_outputs = [
                    (
                        {f"lca_land_use_change_emissions_for_feed_{feed_id}": luc_emissions_for_day[feed_id]},
                        {**info_map, "simulation_day": simulation_day},
                    )
                    for simulation_day, luc_emissions_for_day in luc_emissions_by_simulation_day.items()
                ]
                self.om.add_variable_bulk(luc_outputs, first_info_map_only=False)
