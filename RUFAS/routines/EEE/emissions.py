from ..field.crop.crop_enum import CropSpecies
from ...input_manager import InputManager
from ...units import MeasurementUnits
from ...output_manager import OutputManager
from typing import Any
import re

CROP_SPECIES_TO_PURCHASED_FEED_ID = {
    CropSpecies.ALFALFA_HAY: ["100", "103", "106", "107", "108"],
    CropSpecies.ALFALFA_SILAGE: ["104", "109", "110"],
    CropSpecies.ALFALFA_BALEAGE: [],
    CropSpecies.CEREAL_RYE_HAY: [],
    CropSpecies.CEREAL_RYE_GRAIN: [],
    CropSpecies.CEREAL_RYE_SILAGE: ["144"],
    CropSpecies.CEREAL_RYE_BALEAGE: [],
    CropSpecies.CORN_GRAIN: ["40", "43", "44", "46", "47"],
    CropSpecies.CORN_SILAGE: ["50", "51", "52"],
    CropSpecies.SOYBEAN_HAY: [],
    CropSpecies.SOYBEAN_GRAIN: ["169", "170"],
    CropSpecies.TALL_FESCUE_HAY: ["18", "88", "89", "94", "95", "99"],
    CropSpecies.TALL_FESCUE_SILAGE: ["91", "97", "100"],
    CropSpecies.TALL_FESCUE_BALEAGE: [],
    CropSpecies.TRITICALE_HAY: [],
    CropSpecies.TRITICALE_GRAIN: [],
    CropSpecies.TRITICALE_SILAGE: ["187"],
    CropSpecies.TRITICALE_BALEAGE: [],
    CropSpecies.WINTER_WHEAT_HAY: ["200"],
    CropSpecies.WINTER_WHEAT_GRAIN: ["194"],
    CropSpecies.WINTER_WHEAT_SILAGE: ["198"],
    CropSpecies.WINTER_WHEAT_BALEAGE: ["195"],
}

SLICE_START = -365
SLICE_END = -364
FINAL_DAY_SLICE_START = -1

om = OutputManager()


"""
These are constants for calculating the embedded emissions of synthetic nitrogen and phosphorus fertilizer. Their units
are in kg CO2e / kg N and kg CO2e / kg P, respectively. The nitrogen and phosphorus constants reference IPCC 2021, GWP
100, the potassium constant references BASF's Eco-efficiency analysis tool.
"""
EMBEDDED_NITROGEN_FERTILIZER_EMISSIONS_FACTOR = 5.32
EMBEDDED_PHOSPHORUS_FERTILIZER_EMISSIONS_FACTOR = 3.07
EMBEDDED_POTASSIUM_FERTILIZER_EMISSIONS_FACTOR = 1.30


class EmissionsEstimator:
    def __init__(self) -> None:
        self.im = InputManager()

    def estimate_emissions(self) -> None:
        (
            homegrown_feeds,
            fertilizer_applications,
            manure_applications,
            manure_requests
        ) = self._gather_homegrown_feeds_and_fertilizer_apps()
        self._calculate_purchased_feed_emissions(homegrown_feeds)
        self._calculate_homegrown_feed_emissions(homegrown_feeds, fertilizer_applications, manure_applications, manure_requests)

    def _calculate_purchased_feed_emissions(self, homegrown_feeds: list[dict[str, Any]]) -> None:
        info_map = {"class": self.__class__.__name__, "function": self._calculate_purchased_feed_emissions.__name__}
        purchased_feeds = self._gather_ration_feed_totals()
        (actual_purchased_feed_totals,
         homegrown_feed_totals) = self._calculate_actual_purchased_feeds(homegrown_feeds, purchased_feeds)
        om.add_variable(
            "actual_purchased_feed_totals",
            actual_purchased_feed_totals,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        (
            actual_purchased_feed_emissions,
            actual_land_use_change_emissions,
        ) = self._calculate_actual_purchased_feed_emissions(actual_purchased_feed_totals)
        emissions_info_map = dict(
            info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER}
        )
        om.add_variable("actual_purchased_feed_emissions", actual_purchased_feed_emissions, emissions_info_map)
        om.add_variable("actual_land_use_change_feed_emissions", actual_land_use_change_emissions, emissions_info_map)

    def _gather_homegrown_feeds_and_fertilizer_apps(
        self,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Gathers the yields that were harvested and fertilizer applications that were applied in the last 365 days of the
        simulation.
        """
        crop_filter = {
            "name": "Homegrown Feeds",
            "description": "Collects all crop harvests that occurred in the simulation.",
            "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
            "variables": [".*"],
        }
        yields = om.filter_variables_pool(crop_filter)
        processed_yields = self._transform_outputs_to_list_of_dicts(yields)

        fertilizer_filter = {
            "name": "Fertilizer Applications",
            "description": "Collects all synthetic fertilizer applications that occurred in the simulation.",
            "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
            "variables": [".*"],
        }
        fertilizer_apps = om.filter_variables_pool(fertilizer_filter)
        processed_fert_apps = self._transform_outputs_to_list_of_dicts(fertilizer_apps)

        manure_filter = {
            "name": "Manure Applications",
            "descriptions": "Collects all manure applications that occurred in the simulation.",
            "filters": ["Field._record_manure_application\\.manure_application\\.field='.*'"],
            "variables": [".*"],
        }
        manure_apps = om.filter_variables_pool(manure_filter)
        processed_manure_apps = self._transform_outputs_to_list_of_dicts(manure_apps)

        manure_request_filter = {
            "name": "Manure Applications",
            "descriptions": "Collects all manure applications that occurred in the simulation.",
            "filters": ["Field._record_manure_application\\.manure_request\\.field='.*'"],
            "variables": [".*"],
        }
        manure_requests = om.filter_variables_pool(manure_request_filter)
        processed_manure_requests = self._transform_outputs_to_list_of_dicts(manure_requests)

        time_filter = {
            "name": "Time Filter",
            "description": "Collects the date a year before the simulation ended, to be used as a cutoff for deciding "
            "which crop yields and nutrient applications to estimate emissions for.",
            "filters": ["Time.(day|calendar_year)"],
            "slice_start": SLICE_START,
            "slice_end": SLICE_END,
        }
        date_cutoff = om.filter_variables_pool(time_filter)
        day_cutoff = date_cutoff["Time.day"]["values"][0]
        year_cutoff = date_cutoff["Time.calendar_year"]["values"][0]

        filtered_yields = list(
            filter(
                lambda crop: crop["harvest_day"] >= day_cutoff and crop["harvest_year"] >= year_cutoff, processed_yields
            )
        )

        for crop in filtered_yields:
            crop["total_dry_yield"] = crop["dry_yield"] * crop["field_size"]

        filtered_fert_apps = list(
            filter(lambda app: app["day"] >= day_cutoff and app["year"] >= year_cutoff, processed_fert_apps)
        )

        filtered_manure_apps = list(
            filter(lambda app: app["day"] >= day_cutoff and app["year"] >= year_cutoff, processed_manure_apps)
        )

        filtered_manure_requests = list(
            filter(lambda app: app["day"] >= day_cutoff and app["year"] >= year_cutoff, processed_manure_requests)
        )
        return filtered_yields, filtered_fert_apps, filtered_manure_apps, filtered_manure_requests

    def _gather_ration_feed_totals(self) -> dict[str, float]:
        """
        Collects totals of feeds from rations given to animals in the last 365 days of the simulation and collapses them
        into single set of numbers.
        """
        filter = {
            "name": "Feed Ration Totals",
            "description": "Gathers the amounts of purchased feeds fed to animals in the last year of the simulation.",
            "filters": ["AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals.*"],
            "variables": [r"^\d+$"],
            "slice_start": SLICE_START,
        }
        feeds = om.filter_variables_pool(filter)

        processed_feeds: dict[str, float] = {key: float(sum(feeds[key]["values"])) for key in feeds.keys()}

        return processed_feeds

    def _transform_outputs_to_list_of_dicts(
        self, data: dict[str, OutputManager.pool_element_type]
    ) -> list[dict[str, Any]]:
        """
        Transforms dictionary of lists collected from the Output Manager into list of dictionaries.

        Examples
        --------
        >>> a = {'one': {'values': [1, 2, 3]}, 'two': {'values': [4, 5, 6]}]}
        >>> _transform_outputs_to_list_of_dicts(a)
        [{'one': 1, 'two': 4}, {'one': 2, 'two': 5}, {'one': 3, 'two': 6}]

        """
        keys = data.keys()
        values_list = [data[key]["values"] for key in keys]
        missing_data = not all(len(values_list[index]) == len(values_list[0]) for index in range(len(values_list)))
        if missing_data:
            info_map = {"class": self.__class__.__name__, "function": self._transform_outputs_to_list_of_dicts.__name__}
            om.add_error(
                "Found unequal lengths of data while processing simulation outputs for emissions estimation.",
                "Ignoring extraneous data.",
                info_map,
            )
        processed_data = [dict(zip(keys, values)) for values in zip(*values_list)]
        return processed_data

    def _calculate_actual_purchased_feeds(
        self, homegrown_feeds: list[dict[str, Any]], purchased_feeds: dict[str, float]
    ) -> dict[str, float]:
        """
        Calculates the difference between the purchased feeds and feeds grown on the farm.
        """
        homegrown_totals = self._calculate_total_homegrown_feed_amounts_by_crop_type(homegrown_feeds)

        actual_purchased_feeds = {}
        for feed_id, amount in purchased_feeds.items():
            homegrown_alternatives = [
                crop for crop in homegrown_totals.keys() if feed_id in CROP_SPECIES_TO_PURCHASED_FEED_ID[crop]
            ]
            for homegrown_alternative in homegrown_alternatives:
                alternative_amount_available = homegrown_totals[homegrown_alternative]
                amount_used = min(amount, alternative_amount_available)
                amount -= amount_used
                homegrown_totals[homegrown_alternative] -= amount_used

            actual_purchased_feeds[feed_id] = amount

        return actual_purchased_feeds, homegrown_totals

    def _calculate_total_homegrown_feed_amounts_by_crop_type(
        self, homegrown_feeds: list[dict[str, Any]]
    ) -> dict[CropSpecies, float]:
        """Calculates the total amount of each crop species grown on the farm."""
        homegrown_totals = {key: 0.0 for key in list(CROP_SPECIES_TO_PURCHASED_FEED_ID)}
        for crop_species in homegrown_totals:
            yields = filter(lambda crop: crop["crop"] == crop_species, homegrown_feeds)
            homegrown_totals[crop_species] += sum([crop_yield["total_dry_yield"] for crop_yield in yields])
        om.add_variable(
            "homegrown_feed_totals",
            homegrown_totals,
            dict({"class": self.__class__.__name__,
                  "function": self._calculate_total_homegrown_feed_amounts_by_crop_type.__name__},
                 **{"units": MeasurementUnits.KILOGRAMS})
        )
        return homegrown_totals

    def _calculate_actual_purchased_feed_emissions(self, actual_purchased_feeds: dict[str, float]) -> dict[str, float]:
        """Calculates the emissions from feeds that were actually purchased during the simulation."""

        county_code = self.im.get_data("config.FIPS_county_code")

        purchased_feed_emissions_data = self.im.get_data("purchased_feeds_emissions")
        purchased_feed_emissions = self._get_feed_emissions_data(county_code, purchased_feed_emissions_data)

        land_use_change_emissions_data = self.im.get_data("purchased_feed_land_use_change_emissions")
        land_use_change_emissions = self._get_feed_emissions_data(county_code, land_use_change_emissions_data)

        actual_purchased_feed_emissions = {}
        actual_land_use_change_emissions = {}
        for id, amount_fed in actual_purchased_feeds.items():
            try:
                purchased_emissions = amount_fed * purchased_feed_emissions[id]
                actual_purchased_feed_emissions[id] = purchased_emissions
            except KeyError:
                info_map = {
                    "class": self.__class__.__name__,
                    "function": self._calculate_actual_purchased_feed_emissions.__name__,
                }
                om.add_warning(
                    "Missing Purchased Feed Emissions",
                    f"Missing data for RuFaS feed {id}, omitting from purchased feed emissions estimation.",
                    info_map,
                )
            try:
                land_use_emissions = amount_fed * land_use_change_emissions[id]
                actual_land_use_change_emissions[id] = land_use_emissions
            except KeyError:
                info_map = {
                    "class": self.__class__.__name__,
                    "function": self._calculate_actual_purchased_feed_emissions.__name__,
                }
                om.add_warning(
                    "Missing Land Use Change Purchased Feed Emissions",
                    f"Missing data for RuFaS feed {id}, omitting from land use change purchased feed emissions "
                    "estimation.",
                    info_map,
                )

        return actual_purchased_feed_emissions, actual_land_use_change_emissions

    def _get_feed_emissions_data(
        self, county_code: int, feed_emissions_data: dict[str, list[float]]
    ) -> dict[str, float]:
        """Grabs the appropriate list of emissions for purchased feeds for the location of the simulation."""
        county_codes = feed_emissions_data["county_code"]
        emissions_index = county_codes.index(county_code)

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
        fields_with_fertilizer_apps = {app["field_name"] for app in fertilizer_applications}
        all_fields = list(fields_with_fertilizer_apps | fields_with_crops)
        aggregated_fertilizer_apps = {key: {"nitrogen": 0.0, "phosphorus": 0.0, "potassium": 0.0} for key in all_fields}
        for app in fertilizer_applications:
            field_name = app["field_name"]
            aggregated_fertilizer_apps[field_name]["nitrogen"] += app["nitrogen"]
            aggregated_fertilizer_apps[field_name]["phosphorus"] += app["phosphorus"]
            aggregated_fertilizer_apps[field_name]["potassium"] += app["potassium"]

        fields_with_manure_apps = {app["field_name"] for app in manure_applications}
        all_fields = list(fields_with_manure_apps | fields_with_crops)
        aggregated_manure_apps = {key: {"nitrogen": 0.0, "phosphorus": 0.0} for key in all_fields}
        for app in manure_applications:
            field_name = app["field_name"]
            aggregated_manure_apps[field_name]["nitrogen"] += app["nitrogen"]
            aggregated_manure_apps[field_name]["phosphorus"] += app["phosphorus"]

        aggregated_manure_requests = {key: {"nitrogen": 0.0, "phosphorus": 0.0} for key in all_fields}
        for app in manure_requests:
            field_name = app["field_name"]
            aggregated_manure_requests[field_name]["nitrogen"] += app["nitrogen"]
            aggregated_manure_requests[field_name]["phosphorus"] += app["phosphorus"]

        grouped_soil_characteristics: dict[str, float] = self._collect_target_soil_characteristics(grouped_feeds.keys())

        crops_with_emissions = []
        for field in grouped_feeds.keys():
            crops = self._calculate_emissions_by_field(
                grouped_feeds[field],
                grouped_soil_characteristics[field],
                aggregated_fertilizer_apps[field],
                aggregated_manure_apps[field],
                aggregated_manure_requests[field],
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
                om.add_variable(f"homegrown_{crop_type}_emissions", emissions_info, info_map)

    def _collect_target_soil_characteristics(self, field_names: list[str]) -> dict[str, float]:
        """Collects the emissions and soil carbon characteristics used to calculate farm-grown feed emissions."""
        soil_info = {}
        for name in field_names:
            sanitized_name = re.escape(name)
            soil_data = {}
            ammonia_filter = {
                "name": "Soil Ammonia emissions",
                "description": "Collects the ammonia emissions from all soil layers in the field in the last year of "
                "the simulation.",
                "filters": [
                    f"FieldDataReporter.send_daily_variables.ammonia_emissions.field='{sanitized_name}',layer=.*",
                ],
                "slice_start": SLICE_START,
            }
            ammonia_emissions = om.filter_variables_pool(ammonia_filter)
            soil_data["ammonia"] = sum([sum(ammonia_emissions[key]["values"]) for key in ammonia_emissions.keys()])
            nitrous_oxide_filter = {
                "name": "Soil Nitrous Oxide emissions",
                "description": "Collects the nitrous oxide emissions from all soil layers in the field in the last year"
                " of the simulation.",
                "filters": [
                    f"FieldDataReporter.send_daily_variables.nitrous_oxide_emissions.field='{sanitized_name}',layer=.*"
                ],
                "slice_start": SLICE_START,
            }
            nitrous_oxide_emissions = om.filter_variables_pool(nitrous_oxide_filter)
            soil_data["nitrous_oxide"] = sum(
                [sum(nitrous_oxide_emissions[key]["values"]) for key in nitrous_oxide_emissions.keys()]
            )

            starting_carbon_stock_filter = {
                "name": "Starting soil profile carbon stock",
                "description": "Collects the soil carbon stock level 365 days before the simulation ended.",
                "filters": [
                    f"FieldDataReporter.send_daily_variables.total_soil_carbon_amount.field='{sanitized_name}'"
                ],
                "slice_start": SLICE_START,
                "slice_end": SLICE_END,
            }
            starting_carbon_stock = om.filter_variables_pool(starting_carbon_stock_filter)
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
            ending_carbon_stock = om.filter_variables_pool(ending_carbon_stock_filter)
            total_ending_carbon = sum([ending_carbon_stock[key]["values"][0] for key in ending_carbon_stock.keys()])

            soil_data["carbon_stock_change"] = total_ending_carbon - total_starting_carbon

            soil_info[name] = soil_data
        return soil_info

    def _calculate_emissions_by_field(
        self,
        feeds_grown: list[dict[str, Any]],
        field_emissions: dict[str, float],
        fertilizer_applications: dict[str, float],
        manure_applications: dict[str, float],
        manure_requests: dict[str,float],
    ) -> list[dict[str, Any]]:
        """
        Partitions emissions from the field where crops/feeds were grown to those crops based on their relative mass.
        """
        field_size = feeds_grown[0]["field_size"]
        total_dry_mass_per_ha_grown = sum([crop["dry_yield"] for crop in feeds_grown])

        if total_dry_mass_per_ha_grown == 0.0:
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
            return feeds_grown

        for crop in feeds_grown:
            fraction_of_total_mass_grown = crop["dry_yield"] / total_dry_mass_per_ha_grown
            crop["nitrous_oxide_emissions"] = (
                field_emissions["nitrous_oxide"] * fraction_of_total_mass_grown * field_size
            )
            crop["ammonia_emissions"] = field_emissions["ammonia"] * fraction_of_total_mass_grown * field_size
            crop["carbon_stock_change"] = field_emissions["carbon_stock_change"] * fraction_of_total_mass_grown
            crop["nitrogen_fertilizer_used"] = fertilizer_applications["nitrogen"] * fraction_of_total_mass_grown
            crop["nitrogen_fertilizer_embedded_CO2_emissions"] = (
                fertilizer_applications["nitrogen"]
                * fraction_of_total_mass_grown
                * EMBEDDED_NITROGEN_FERTILIZER_EMISSIONS_FACTOR
            )
            crop["phosphorus_fertilizer_used"] = fertilizer_applications["phosphorus"] * fraction_of_total_mass_grown
            crop["phosphorus_fertilizer_embedded_CO2_emissions"] = (
                fertilizer_applications["phosphorus"]
                * fraction_of_total_mass_grown
                * EMBEDDED_PHOSPHORUS_FERTILIZER_EMISSIONS_FACTOR
            )
            crop["potassium_fertilizer_used"] = fertilizer_applications["potassium"] * fraction_of_total_mass_grown
            crop["potassium_fertilizer_embedded_CO2_emissions"] = (
                fertilizer_applications["potassium"]
                * fraction_of_total_mass_grown
                * EMBEDDED_POTASSIUM_FERTILIZER_EMISSIONS_FACTOR
            )
            crop["manure_nitrogen_used"] = manure_applications["nitrogen"] * fraction_of_total_mass_grown
            crop["manure_nitrogen_requested"] = manure_requests["nitrogen"] * fraction_of_total_mass_grown

        return feeds_grown
