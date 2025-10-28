import re
from datetime import date
from typing import Any, Literal

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

SLICE_START = -365
SLICE_END = -364
FINAL_DAY_SLICE_START = -1

TIME_FILTER = {
    "name": "RufasTime Filter",
    "description": "Collects the date a year before the simulation ended, to be used as a cutoff for deciding "
    "which crop yields and nutrient applications to estimate emissions for.",
    "filters": ["RufasTime.(day|calendar_year)"],
    "slice_start": SLICE_START,
    "slice_end": SLICE_END,
}
HOMEGROWN_FEEDS_AND_FERTILIZERS_FILTERS: dict[str, dict[str, Any]] = {
    "homegrown feeds filter": {
        "name": "Homegrown Feeds",
        "description": "Collects all crop harvests that occurred in the simulation.",
        "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
        "variables": [".*"],
        "date_fields": ("harvest_year", "harvest_day"),
    },
    "fertilizer applications filter": {
        "name": "Fertilizer Applications",
        "description": "Collects all synthetic fertilizer applications that occurred in the simulation.",
        "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
        "variables": [".*"],
        "date_fields": ("year", "day"),
    },
    "manure applications filter": {
        "name": "Manure Applications",
        "description": "Collects all manure applications that occurred in the simulation.",
        "filters": ["Field._record_manure_application\\.manure_application\\.field='.*'"],
        "variables": [".*"],
        "date_fields": ("year", "day"),
    },
    "manure requests filter": {
        "name": "Manure Requests",
        "description": "Collects all manure requests that occurred in the simulation.",
        "filters": ["Field._record_manure_application\\.manure_request\\.field='.*'"],
        "variables": [".*"],
        "date_fields": ("year", "day"),
    },
}

"""
Patterns for matching purchased feed storage and totals in the output variables.
"""
PURCHASED_FEED_PATTERN = r"_(\d+)_fed_to_date.*"

"""
These are constants for calculating the embedded emissions of synthetic nitrogen and phosphorus fertilizer. Their units
are in kg CO2e / kg N and kg CO2e / kg P, respectively. The nitrogen and phosphorus constants reference IPCC 2021, GWP
100, the potassium constant references BASF's Eco-efficiency analysis tool.
"""
EMBEDDED_NITROGEN_FERTILIZER_EMISSIONS_FACTOR: float = 5.32
EMBEDDED_PHOSPHORUS_FERTILIZER_EMISSIONS_FACTOR: float = 3.07
EMBEDDED_POTASSIUM_FERTILIZER_EMISSIONS_FACTOR: float = 1.30


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

    def estimate_emissions(self) -> None:
        """Estimates emissions associated with farmgrown feeds."""
        fertilizer_apps = self._gather_homegrown_feeds_and_fertilizer_apps()
        self._calculate_homegrown_feed_emissions(
            fertilizer_apps["Homegrown Feeds"],
            fertilizer_apps["Fertilizer Applications"],
            fertilizer_apps["Manure Applications"],
            fertilizer_apps["Manure Requests"],
        )

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

    def _gather_homegrown_feeds_and_fertilizer_apps(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Gathers the yields that were harvested and fertilizer applications that were applied in the last 365 days of the
        simulation.
        """
        date_variables = self.om.filter_variables_pool(TIME_FILTER)
        day_cutoff = date_variables["RufasTime.day"]["values"][0]
        year_cutoff = date_variables["RufasTime.calendar_year"]["values"][0]
        date_cutoff = RufasTime.convert_year_jday_to_date(year_cutoff, day_cutoff).date()

        results = {}
        for operation_filter_key in HOMEGROWN_FEEDS_AND_FERTILIZERS_FILTERS:
            operation_filter = HOMEGROWN_FEEDS_AND_FERTILIZERS_FILTERS[operation_filter_key]
            filtered_data = self._filter_results(operation_filter, date_cutoff, *operation_filter["date_fields"])
            results[operation_filter["name"]] = filtered_data

        for crop in results["Homegrown Feeds"]:
            crop["total_dry_yield"] = crop["dry_yield"] * crop["field_size"]

        return results

    def _transform_outputs_to_list_of_dicts(self, data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Transforms dictionary of lists collected from the Output Manager into list of dictionaries.

        Examples
        --------
        >>> a = {'one': {'values': [1, 2, 3]}, 'two': {'values': [4, 5, 6]}}
        >>> _transform_outputs_to_list_of_dicts(a)
        [{'one': 1, 'two': 4}, {'one': 2, 'two': 5}, {'one': 3, 'two': 6}]

        """
        keys = data.keys()
        values_list = [data[key]["values"] for key in keys]
        missing_data = not all(len(values_list[index]) == len(values_list[0]) for index in range(len(values_list)))
        if missing_data:
            info_map = {"class": self.__class__.__name__, "function": self._transform_outputs_to_list_of_dicts.__name__}
            self.om.add_error(
                "Found unequal lengths of data while processing simulation outputs for emissions estimation.",
                "Ignoring extraneous data.",
                info_map,
            )
        processed_data = [dict(zip(keys, values)) for values in zip(*values_list)]
        return processed_data

    def _calculate_total_homegrown_feed_amounts_by_crop_type(
        self, homegrown_feeds: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Calculates the total amount of each crop species grown on the farm."""
        homegrown_totals = {key: 0.0 for key in list(self.crop_species_to_purchased_feed_id)}
        for crop_species in homegrown_totals:
            yields = filter(lambda crop: crop["crop"] == crop_species, homegrown_feeds)
            homegrown_totals[crop_species] += sum([crop_yield["total_dry_yield"] for crop_yield in yields])
        self.om.add_variable(
            "homegrown_feed_totals",
            homegrown_totals,
            {
                "class": self.__class__.__name__,
                "function": self._calculate_total_homegrown_feed_amounts_by_crop_type.__name__,
                "units": MeasurementUnits.KILOGRAMS,
            },
        )
        return homegrown_totals

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

    def _calculate_homegrown_feed_emissions(
        self,
        homegrown_feeds: list[dict[str, Any]],
        fertilizer_applications: list[dict[str, Any]],
        manure_applications: list[dict[str, Any]],
        manure_requests: list[dict[str, Any]],
    ) -> None:
        """Calculates the emissions associated with feeds grown on the farm."""
        grouped_feeds: dict[str, list[dict[str, Any]]] = {}
        for feed in homegrown_feeds:
            field_name = feed["field_name"]
            if field_name not in grouped_feeds.keys():
                grouped_feeds[field_name] = []
            grouped_feeds[field_name].append(feed)

        fields_with_crops = set(grouped_feeds.keys())

        fields_with_manure_apps = {app["field_name"] for app in manure_applications}
        all_fields = list(fields_with_manure_apps | fields_with_crops)
        aggregated_manure_apps = self._aggregate_data(manure_applications, all_fields, ["nitrogen", "phosphorus"])

        aggregated_manure_requests = self._aggregate_data(manure_requests, all_fields, ["nitrogen", "phosphorus"])

        grouped_soil_characteristics: dict[str, dict[str, Any]] = self._collect_target_soil_characteristics(
            list(grouped_feeds.keys())
        )

        crops_with_emissions = []
        for field in grouped_feeds.keys():
            crops = self._calculate_emissions_by_field(
                field,
                grouped_feeds[field],
                grouped_soil_characteristics[field],
                aggregated_manure_apps[field],
                aggregated_manure_requests[field],
                fertilizer_applications,
            )
            crops_with_emissions.extend(crops)

        info_map = {
            "class": self.__class__.__name__,
            "function": self._calculate_homegrown_feed_emissions.__name__,
            "units": {
                "crop_type": MeasurementUnits.UNITLESS,
                "nitrous_oxide_emissions": MeasurementUnits.KILOGRAMS,
                "ammonia_emisssions": MeasurementUnits.KILOGRAMS,
                "carbon_stock_change": MeasurementUnits.KILOGRAMS_PER_HECTARE,
                "nitrogen_fertilizer_used": MeasurementUnits.KILOGRAMS,
                "nitrogen_fertilizer_embedded_CO2_emissions": MeasurementUnits.KILOGRAMS,
                "phosphorus_fertilizer_used": MeasurementUnits.KILOGRAMS,
                "phosphorus_fertilizer_embedded_CO2_emissions": MeasurementUnits.KILOGRAMS,
                "potassium_fertilizer_used": MeasurementUnits.KILOGRAMS,
                "potassium_fertilizer_embedded_CO2_emissions": MeasurementUnits.KILOGRAMS,
                "manure_nitrogen_used": MeasurementUnits.KILOGRAMS,
                "manure_nitrogen_requested": MeasurementUnits.KILOGRAMS,
                "field_name": MeasurementUnits.UNITLESS,
            },
        }
        crop_types: set[str] = {crop["crop"] for crop in crops_with_emissions}
        for crop_type in crop_types:
            crops = list(filter(lambda crop: crop["crop"] == crop_type, crops_with_emissions))
            for crop in crops:
                emissions_info = {
                    "crop_type": crop["crop"],
                    "nitrous_oxide_emissions": crop["nitrous_oxide_emissions"],
                    "ammonia_emissions": crop["ammonia_emissions"],
                    "carbon_stock_change": crop["carbon_stock_change"],
                    "nitrogen_fertilizer_used": crop["nitrogen_fertilizer_used"],
                    "nitrogen_fertilizer_embedded_CO2_emissions": crop["nitrogen_fertilizer_embedded_CO2_emissions"],
                    "phosphorus_fertilizer_used": crop["phosphorus_fertilizer_used"],
                    "phosphorus_fertilizer_embedded_CO2_emissions": crop[
                        "phosphorus_fertilizer_embedded_CO2_emissions"
                    ],
                    "potassium_fertilizer_used": crop["potassium_fertilizer_used"],
                    "potassium_fertilizer_embedded_CO2_emissions": crop["potassium_fertilizer_embedded_CO2_emissions"],
                    "manure_nitrogen_used": crop["manure_nitrogen_used"],
                    "manure_nitrogen_requested": crop["manure_nitrogen_requested"],
                    "field_name": crop["field_name"],
                }
                self.om.add_variable(f"homegrown_{crop_type}_emissions", emissions_info, info_map)

    def _collect_target_soil_characteristics(self, field_names: list[str]) -> dict[str, dict[str, Any]]:
        """Collects the emissions and soil carbon characteristics used to calculate farm-grown feed emissions."""
        soil_info = {}
        for name in field_names:
            sanitized_name = re.escape(name)
            filters: dict[str, dict[str, Any]] = {
                "ammonia": {
                    "name": "Soil Ammonia emissions",
                    "description": "Collects the ammonia emissions from all soil layers in the field in the last "
                    "year of the simulation.",
                    "filters": [
                        f"FieldDataReporter.send_daily_variables.ammonia_emissions.field='{sanitized_name}'"
                        f",layer=.*",
                    ],
                    "slice_start": SLICE_START,
                },
                "nitrous_oxide": {
                    "name": "Soil Nitrous Oxide emissions",
                    "description": "Collects the nitrous oxide emissions from all soil layers in the field in the "
                    "last year of the simulation.",
                    "filters": [
                        f"FieldDataReporter.send_daily_variables.nitrous_oxide_emissions.field='{sanitized_name}',"
                        f"layer=.*"
                    ],
                    "slice_start": SLICE_START,
                },
            }
            soil_data = self._soil_data_update(filters)

            starting_carbon_stock_filter = {
                "name": "Starting soil profile carbon stock",
                "description": "Collects the soil carbon stock level 365 days before the simulation ended.",
                "filters": [
                    f"FieldDataReporter.send_daily_variables.total_soil_carbon_amount.field='{sanitized_name}'"
                ],
                "slice_start": SLICE_START,
                "slice_end": SLICE_END,
            }

            starting_carbon_stock = self.om.filter_variables_pool(starting_carbon_stock_filter)

            total_starting_carbon = sum(
                [starting_carbon_stock[key]["values"][0] for key in starting_carbon_stock.keys()]
            )

            ending_carbon_stock_filter = {
                "name": "Ending soil profile carbon stock",
                "description": "Collects the soil carbon stock level on the last day of the simulation.",
                "filters": [
                    f"FieldDataReporter.send_daily_variables.total_soil_carbon_amount.field='{sanitized_name}'"
                ],
                "slice_start": FINAL_DAY_SLICE_START,
            }
            ending_carbon_stock = self.om.filter_variables_pool(ending_carbon_stock_filter)
            total_ending_carbon = sum([ending_carbon_stock[key]["values"][0] for key in ending_carbon_stock.keys()])

            soil_data["carbon_stock_change"] = total_ending_carbon - total_starting_carbon

            soil_info[name] = soil_data
        return soil_info

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
        field_size = feeds_grown[0]["field_size"]
        total_dry_mass_per_ha_grown = sum([crop["dry_yield"] for crop in feeds_grown])

        for crop in feeds_grown:
            crop["nitrous_oxide_emissions"] = 0.0
            crop["ammonia_emissions"] = 0.0
            crop["carbon_stock_change"] = 0.0
            crop["nitrogen_fertilizer_used"] = 0.0
            crop["nitrogen_fertilizer_embedded_CO2_emissions"] = 0.0
            crop["phosphorus_fertilizer_used"] = 0.0
            crop["phosphorus_fertilizer_embedded_CO2_emissions"] = 0.0
            crop["potassium_fertilizer_used"] = 0.0
            crop["potassium_fertilizer_embedded_CO2_emissions"] = 0.0
            crop["manure_nitrogen_used"] = 0.0
            crop["manure_nitrogen_requested"] = 0.0

        if total_dry_mass_per_ha_grown == 0.0:
            return feeds_grown

        sorted_crops = sorted(feeds_grown, key=lambda crop: (crop["planting_year"], crop["planting_day"]))
        for crop in sorted_crops:
            fraction_of_total_mass_grown = crop["dry_yield"] / total_dry_mass_per_ha_grown
            crop["nitrous_oxide_emissions"] = (
                field_emissions["nitrous_oxide"] * fraction_of_total_mass_grown * field_size
            )
            crop["ammonia_emissions"] = field_emissions["ammonia"] * fraction_of_total_mass_grown * field_size
            crop["carbon_stock_change"] = (
                field_emissions["carbon_stock_change"] * fraction_of_total_mass_grown * field_size
            )
            crop["manure_nitrogen_used"] = manure_applications["nitrogen"] * fraction_of_total_mass_grown
            crop["manure_nitrogen_requested"] = manure_requests["nitrogen"] * fraction_of_total_mass_grown

        filtered_fertilizers = [fert for fert in fertilizer_applications_data if fert["field_name"] == field_name]

        for fertilizer_application in filtered_fertilizers:
            fertilizer_application_date = RufasTime.convert_year_jday_to_date(
                fertilizer_application["year"], fertilizer_application["day"]
            ).date()
            applied_crops = self._extract_applied_crops(sorted_crops, fertilizer_application_date)
            applied = False

            if len(applied_crops) > 0:
                self._partition_applied_crop_fertilizer_emissions(fertilizer_application, applied_crops)
                applied = True
            else:
                applied = self._apply_fertilizer_to_next_crop(
                    fertilizer_application, sorted_crops, fertilizer_application_date
                )
            if not applied:
                self.om.add_warning(
                    "Fertilizer application not associated with any crops.",
                    f"Fertilizer applied on {fertilizer_application_date} did not align with any crop "
                    "planting and harvesting dates.",
                    info_map={
                        "class": self.__class__.__name__,
                        "function": self._calculate_emissions_by_field.__name__,
                    },
                )

        return sorted_crops

    def _partition_applied_crop_fertilizer_emissions(
        self, fertilizer_application: dict[str, float], applied_crops: list[dict[str, Any]]
    ) -> None:
        """
        Partitions synthetic emissions from fertilizer applications to crop(s) whose planting and harvesting dates
        encompass the fertilizer application date.
        """
        for crop in applied_crops:
            split_factor = 1 / len(applied_crops)
            crop["nitrogen_fertilizer_used"] += fertilizer_application["nitrogen"] * split_factor
            crop["nitrogen_fertilizer_embedded_CO2_emissions"] += (
                fertilizer_application["nitrogen"] * split_factor * EMBEDDED_NITROGEN_FERTILIZER_EMISSIONS_FACTOR
            )
            crop["phosphorus_fertilizer_used"] += fertilizer_application["phosphorus"] * split_factor
            crop["phosphorus_fertilizer_embedded_CO2_emissions"] += (
                fertilizer_application["phosphorus"] * split_factor * EMBEDDED_PHOSPHORUS_FERTILIZER_EMISSIONS_FACTOR
            )
            crop["potassium_fertilizer_used"] += fertilizer_application["potassium"] * split_factor
            crop["potassium_fertilizer_embedded_CO2_emissions"] += (
                fertilizer_application["potassium"] * split_factor * EMBEDDED_POTASSIUM_FERTILIZER_EMISSIONS_FACTOR
            )

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
        filtered_pools = self.om.filter_variables_pool(filters)
        processed_data = self._transform_outputs_to_list_of_dicts(filtered_pools)
        return list(
            filter(
                lambda app: RufasTime.convert_year_jday_to_date(app[year_key], app[day_key]).date() >= date_cutoff,
                processed_data,
            )
        )

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
        aggregated_data = {key: {nutrient: 0.0 for nutrient in nutrients} for key in all_fields}

        for app in operations:
            field_name = app["field_name"]
            for nutrient in nutrients:
                aggregated_data[field_name][nutrient] += app[nutrient]

        return aggregated_data

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
        for index, crop in enumerate(sorted_crops):
            crop_harvest_date = RufasTime.convert_year_jday_to_date(crop["harvest_year"], crop["harvest_day"]).date()
            next_crop_exists = index + 1 < len(sorted_crops)

            if next_crop_exists:
                next_crop = sorted_crops[index + 1]
                next_crop_planting_date = RufasTime.convert_year_jday_to_date(
                    next_crop["planting_year"], next_crop["planting_day"]
                ).date()
                if crop_harvest_date < fertilizer_application_date < next_crop_planting_date:

                    next_crop["nitrogen_fertilizer_used"] += fertilizer_application["nitrogen"]
                    next_crop["nitrogen_fertilizer_embedded_CO2_emissions"] += (
                        fertilizer_application["nitrogen"] * EMBEDDED_NITROGEN_FERTILIZER_EMISSIONS_FACTOR
                    )
                    next_crop["phosphorus_fertilizer_used"] += fertilizer_application["phosphorus"]
                    next_crop["phosphorus_fertilizer_embedded_CO2_emissions"] += (
                        fertilizer_application["phosphorus"] * EMBEDDED_PHOSPHORUS_FERTILIZER_EMISSIONS_FACTOR
                    )
                    next_crop["potassium_fertilizer_used"] += fertilizer_application["potassium"]
                    next_crop["potassium_fertilizer_embedded_CO2_emissions"] += (
                        fertilizer_application["potassium"] * EMBEDDED_POTASSIUM_FERTILIZER_EMISSIONS_FACTOR
                    )
                    return True
        return False

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
        applied_crops = []

        for crop in sorted_crops:
            crop_planting_date = RufasTime.convert_year_jday_to_date(crop["planting_year"], crop["planting_day"]).date()
            crop_harvest_date = RufasTime.convert_year_jday_to_date(crop["harvest_year"], crop["harvest_day"]).date()
            if crop_planting_date <= fertilizer_application_date < crop_harvest_date:
                applied_crops.append(crop)
        return applied_crops

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
        soil_data = {}
        for key in filters.keys():
            emissions = self.om.filter_variables_pool(filters[key])
            soil_data[key] = sum([sum(emissions[key]["values"]) for key in emissions.keys()])

        return soil_data
