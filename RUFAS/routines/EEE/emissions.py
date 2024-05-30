from ..field.crop.crop_enum import CropSpecies
from ...input_manager import InputManager
from ...units import MeasurementUnits
from ...output_manager import OutputManager
from typing import Any

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

im = InputManager()
om = OutputManager()


class Emissions:
    """"""

    def __init__(self) -> None:
        pass

    def calculate_emissions(self) -> None:
        homegrown_feeds = self._gather_homegrown_feeds()
        self._calculate_purchased_feed_emissions(homegrown_feeds)

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
        print(f"\n\n{homegrown_feeds}\n\n")
        print(f"{purchased_feeds}\n\n")
        print(f"{actual_purchased_feed_totals}\n\n")
        print(f"{actual_purchased_feed_emissions}\n\n")

    def _gather_homegrown_feeds(self) -> list[dict[str, Any]]:
        """Gathers the yields that were harvested in the last 365 days of the simulation."""
        crop_filter = {
            "name": "Homegrown Feeds",
            "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
            "variables": [".*"],
        }
        yields = om.filter_variables_pool(crop_filter)

        processed_yields = self._win_just_one_for_the_zipper(yields)

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

        return filtered_yields

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
