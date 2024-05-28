from ..field.crop.crop_enum import CropSpecies
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

om = OutputManager()


class Emissions:
    """"""

    def __init__(self) -> None:
        pass

    def calculate_purchased_feed_emissions(self) -> None:
        homegrown_feeds = self._gather_homegrown_feeds()
        purchased_feeds = self._gather_ration_feed_totals()
        print(f"\n\n{homegrown_feeds}\n\n")
        print(f"\n\n{purchased_feeds}\n\n")

    def _gather_homegrown_feeds(self) -> list[dict[str, Any]]:
        filter = {
            "name": "Homegrown Feeds",
            "filters": ["CropManagement._record_yield.harvest_yield.field='.*'"],
            "variables": [".*"],
        }
        yields = om.filter_variables_pool(filter)

        processed_yields = self._win_just_one_for_the_zipper(yields)

        return processed_yields

    def _gather_ration_feed_totals(self) -> dict[str, float]:
        """Collects totals of feeds from rations given to animals and collapses them into single set of numbers."""
        filter = {
            "name": "Feed Ration Totals",
            "filters": ["AnimalModuleReporter.report_daily_ration.ration_daily_feed_totals.*"],
            "variables": [r"^\d+$"],
        }
        feeds = om.filter_variables_pool(filter)

        processed_feeds: dict[str, float] = {key: float(sum(feeds[key]["values"])) for key in feeds.keys()}

        return processed_feeds

    def _win_just_one_for_the_zipper(self, data: dict[str, OutputManager.pool_element_type]) -> list[dict[str, Any]]:
        keys = data.keys()
        values_list = [data[key]["values"] for key in keys]
        processed_data = [dict(zip(keys, values)) for values in zip(*values_list)]
        return processed_data

    def _calculate_actual_purchased_feeds(self, homegrown_feeds: list[dict[str, Any]], purchased_feeds: dict[str, float]) -> dict[str, float]:
        """Calculates the difference between the purchased feeds and feeds grown on the farm."""
        homegrown_totals = {key: 0.0 for key in list(CROP_SPECIES_TO_PURCHASED_FEED_ID)}
        for feed in homegrown_totals:
            yields = filter(lambda crop: crop["crop"] == feed, homegrown_feeds)
            homegrown_totals[feed] += sum([crop_yield["dry_yield"] for crop_yield in yields])

        actual_purchased_feeds = {}
        for feed_id, amount in purchased_feeds.items():
            homegrown_alternatives = {key: homegrown_totals[key] for key in homegrown_totals if feed_id in key.value}
            for key, value in homegrown_alternatives.items():
                amount_used = min(amount, value)
                amount -= amount_used
                homegrown_alternatives[key] -= amount_used

            actual_purchased_feeds[feed_id] = amount

        return actual_purchased_feeds
