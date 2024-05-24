from ...output_manager import OutputManager
from typing import Any


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
