from ..field.crop.crop_enum import CropSpecies
from ...input_manager import InputManager
from ...units import MeasurementUnits
from ...output_manager import OutputManager
from typing import Any
import re

CROP_SPECIES_TO_PURCHASED_FEED_ID = {
    CropSpecies.ALFALFA_HAY: ["106", "107", "108"],
    CropSpecies.ALFALFA_SILAGE: [],
    CropSpecies.ALFALFA_BALEAGE: [],
    CropSpecies.CEREAL_RYE_HAY: [],
    CropSpecies.CEREAL_RYE_GRAIN: [],
    CropSpecies.CEREAL_RYE_SILAGE: [],
    CropSpecies.CEREAL_RYE_BALEAGE: [],
    CropSpecies.CORN_GRAIN: ["40", "43", "44", "46", "47"],
    CropSpecies.CORN_SILAGE: ["50", "50", "51"],
    CropSpecies.SOYBEAN_HAY: [],
    CropSpecies.SOYBEAN_GRAIN: [],
    CropSpecies.TALL_FESCUE_HAY: [],
    CropSpecies.TALL_FESCUE_SILAGE: [],
    CropSpecies.TALL_FESCUE_BALEAGE: [],
    CropSpecies.TRITICALE_HAY: [],
    CropSpecies.TRITICALE_GRAIN: [],
    CropSpecies.TRITICALE_SILAGE: [],
    CropSpecies.TRITICALE_BALEAGE: [],
    CropSpecies.WINTER_WHEAT_HAY: [],
    CropSpecies.WINTER_WHEAT_GRAIN: [],
    CropSpecies.WINTER_WHEAT_SILAGE: [],
    CropSpecies.WINTER_WHEAT_BALEAGE: [],
}

SLICE_START = -365
SLICE_END = -364
FINAL_DAY_SLICE_START = -1

im = InputManager()
om = OutputManager()


class Emissions:
    """"""

    def __init__(self) -> None:
        pass

    def calculate_emissions(self) -> None:
        homegrown_feeds, fertilizer_applications = self._gather_homegrown_feeds_and_fertilizer_apps()
        self._calculate_purchased_feed_emissions(homegrown_feeds)
        self._calculate_homegrown_feed_emissions(homegrown_feeds, fertilizer_applications)

    def _calculate_purchased_feed_emissions(self, homegrown_feeds: list[dict[str, Any]]) -> None:
        info_map = {"class": self.__class__.__name__, "function": self._calculate_purchased_feed_emissions.__name__}
        purchased_feeds = self._gather_ration_feed_totals()
        actual_purchased_feed_totals = self._calculate_actual_purchased_feeds(homegrown_feeds, purchased_feeds)
        om.add_variable(
            "actual_purchased_feed_totals",
            actual_purchased_feed_totals,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        actual_purchased_feed_emissions = self._calculate_actual_purchased_feed_emissions(actual_purchased_feed_totals)
        om.add_variable(
            "actual_purchased_feed_emissions",
            actual_purchased_feed_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER}),
        )

    def _gather_homegrown_feeds_and_fertilizer_apps(self) -> tuple[list[dict[str, Any]]]:
        """
        Gathers the yields that were harvested and fertilizer applications that were applied in the last 365 days of the
        simulation.
        """
        crop_filter = {
            "name": "Homegrown Feeds",
            "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
            "variables": [".*"],
        }
        yields = om.filter_variables_pool(crop_filter)
        processed_yields = self._win_just_one_for_the_zipper(yields)

        fertilizer_filter = {
            "name": "Fertilizer Applications",
            "filters": ["Field._record_fertilizer_application\\.fertilizer_application\\.field='.*'"],
            "variables": [".*"],
        }
        fertilizer_apps = om.filter_variables_pool(fertilizer_filter)
        processed_apps = self._win_just_one_for_the_zipper(fertilizer_apps)

        time_filter = {
            "name": "Time Filter",
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

        filtered_apps = list(
            filter(lambda app: app["day"] >= day_cutoff and app["year"] >= year_cutoff, processed_apps)
        )

        return filtered_yields, filtered_apps

    def _gather_ration_feed_totals(self) -> dict[str, float]:
        """
        Collects totals of feeds from rations given to animals in the last 365 days of the simulation and collapses them
        into single set of numbers.
        """
        filter = {
            "name": "Feed Ration Totals",
            "filters": ["AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals.*"],
            "variables": [r"^\d+$"],
            "slice_start": SLICE_START,
        }
        feeds = om.filter_variables_pool(filter)

        processed_feeds: dict[str, float] = {key: float(sum(feeds[key]["values"])) for key in feeds.keys()}

        return processed_feeds

    def _win_just_one_for_the_zipper(self, data: dict[str, OutputManager.pool_element_type]) -> list[dict[str, Any]]:
        """TODO: change name unless everyone agrees it's funny enough to keep."""
        keys = data.keys()
        values_list = [data[key]["values"] for key in keys]
        processed_data = [dict(zip(keys, values)) for values in zip(*values_list)]
        return processed_data

    def _calculate_actual_purchased_feeds(
        self, homegrown_feeds: list[dict[str, Any]], purchased_feeds: dict[str, float]
    ) -> dict[str, float]:
        """
        Calculates the difference between the purchased feeds and feeds grown on the farm.

        Notes
        -----
        This method assumes that there will be a one-to-many mapping between Crop Species and RuFaS Feed IDs.

        """
        homegrown_totals = {key: 0.0 for key in list(CROP_SPECIES_TO_PURCHASED_FEED_ID)}
        for crop_species in homegrown_totals:
            yields = filter(lambda crop: crop["crop"] == crop_species, homegrown_feeds)
            homegrown_totals[crop_species] += sum([crop_yield["total_dry_yield"] for crop_yield in yields])

        actual_purchased_feeds = {}
        for feed_id, amount in purchased_feeds.items():
            homegrown_alternatives = {
                crop: crop_yield
                for crop, crop_yield in homegrown_totals.items()
                if feed_id in CROP_SPECIES_TO_PURCHASED_FEED_ID[crop]
            }
            for key, value in homegrown_alternatives.items():
                amount_used = min(amount, value)
                amount -= amount_used
                homegrown_alternatives[key] -= amount_used

            actual_purchased_feeds[feed_id] = amount

        return actual_purchased_feeds

    def _calculate_actual_purchased_feed_emissions(self, actual_purchased_feeds: dict[str, float]) -> dict[str, float]:
        """Calculates the emissions from feeds that were actually purchased during the simulation."""
        feed_emissions = self._get_feed_emissions_data()

        actual_purchased_feed_emissions = {}
        for id, amount_fed in actual_purchased_feeds.items():
            try:
                emissions = amount_fed * feed_emissions[id]
                actual_purchased_feed_emissions[id] = emissions
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

        return actual_purchased_feed_emissions

    def _get_feed_emissions_data(self) -> dict[str, float]:
        """Grabs the appropriate list of emissions for purchased feeds for the location of the simulation."""
        county_code = im.get_data("config.FIPS_county_code")
        feed_emissions_data = im.get_data("purchased_feeds_emissions")

        county_codes = feed_emissions_data["county_code"]
        emissions_index = county_codes.index(county_code)

        feed_keys = [key for key in feed_emissions_data.keys() if key != "FIPS_county_code"]
        feed_emissions_dict = {key: feed_emissions_data[key][emissions_index] for key in feed_keys}

        return feed_emissions_dict

    def _calculate_homegrown_feed_emissions(
        self, homegrown_feeds: list[dict[str, Any]], fertilizer_applications: list[dict[str, Any]]
    ) -> None:
        """Calculates the emissions associated with feeds grown on the farm."""
        grouped_feeds = {}
        for feed in homegrown_feeds:
            field_name = feed["field_name"]
            if field_name not in grouped_feeds.keys():
                grouped_feeds[field_name] = []
            grouped_feeds[field_name].append(feed)

        fields_with_crops = set(grouped_feeds.keys())
        fields_with_fertilizer_apps = {app["field_name"] for app in fertilizer_applications}
        all_fields = list(fields_with_fertilizer_apps | fields_with_crops)
        aggregated_fertilizer_apps = {key: {"nitrogen": 0.0, "phosphorus": 0.0} for key in all_fields}
        for app in fertilizer_applications:
            field_name = app["field_name"]
            aggregated_fertilizer_apps[field_name]["nitrogen"] += app["nitrogen"]
            aggregated_fertilizer_apps[field_name]["phosphorus"] += app["phosphorus"]

        grouped_soil_characteristics = self._collect_target_soil_characteristics(grouped_feeds.keys())

        crops_with_emissions = []
        for field in grouped_feeds.keys():
            crops = self._calculate_emissions_by_field(
                grouped_feeds[field], grouped_soil_characteristics[field], aggregated_fertilizer_apps[field]
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
                "phosphorus_fertilizer_used": MeasurementUnits.KILOGRAMS,
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
                    "phosphorus_fertilizer_used": crop["phosphorus_fertilizer_used"],
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
                "filters": [
                    f"FieldDataReporter.send_daily_variables.ammonia_emissions.field='{sanitized_name}',layer=.*",
                ],
                "slice_start": SLICE_START,
            }
            ammonia_emissions = om.filter_variables_pool(ammonia_filter)
            soil_data["ammonia"] = sum([sum(ammonia_emissions[key]["values"]) for key in ammonia_emissions.keys()])
            nitrous_oxide_filter = {
                "name": "Soil Nitrous Oxide emissions",
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
    ) -> list[dict[str, Any]]:
        """
        Partitions emissions from the field where crops/feeds were grown to those crops based on their relative mass.
        """
        field_size = feeds_grown[0]["field_size"]
        total_dry_mass_per_ha_grown = sum([crop["dry_yield"] for crop in feeds_grown])
        # TODO: Check that total dry mass is not 0

        for crop in feeds_grown:
            fraction_of_total_mass_grown = crop["dry_yield"] / total_dry_mass_per_ha_grown
            crop["nitrous_oxide_emissions"] = (
                field_emissions["nitrous_oxide"] * fraction_of_total_mass_grown * field_size
            )
            crop["ammonia_emissions"] = field_emissions["ammonia"] * fraction_of_total_mass_grown * field_size
            crop["carbon_stock_change"] = field_emissions["carbon_stock_change"] * fraction_of_total_mass_grown
            crop["nitrogen_fertilizer_used"] = fertilizer_applications["nitrogen"] * fraction_of_total_mass_grown
            crop["phosphorus_fertilizer_used"] = fertilizer_applications["phosphorus"] * fraction_of_total_mass_grown

        return feeds_grown
