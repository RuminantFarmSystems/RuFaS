from RUFAS.units import MeasurementUnits
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()


class PurchasedFeedEmissionsEstimator:
    def __init__(self) -> None:
        info_map = {"class": self.__class__.__name__, "function": "__init__"}

        self.FIPS_county_code = im.get_data("config.FIPS_county_code")

        om.add_variable(
            "FIPS_county_code", self.FIPS_county_code, dict(info_map, **{"units": MeasurementUnits.UNITLESS})
        )

        self.feed_emissions: dict[str, float] = self._setup_feed_emissions()
        om.add_variable(
            "purchased_feed_emissions",
            self.feed_emissions,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_PER_KILOGRAM_DRY_MATTER}),
        )

        self.missing_feed_ids: list[str] = []

    def create_daily_purchased_feed_emissions_report(self, daily_feed_totals: dict[str, float]) -> dict[str, float]:
        """
        Reports the total emissions from the feeds given to a pen.

        Parameters
        ----------
        daily_feed_totals : dict[str, float]
            Maps the feed type to the amount of feed given to the pen (feed ID: kg dry matter).

        Returns
        -------
        dict[str, float]
            Maps the feed type to the amount of emissions generated in producing and delivering it (feed ID: kg CO2).

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.create_daily_purchased_feed_emissions_report.__name__,
        }

        emissions_per_feed_id = {"feed_emissions_total": 0.0}

        for feed_id, amount_fed in daily_feed_totals.items():
            if feed_id == "dry_matter_intake_total":
                continue
            if feed_id == "byproducts_total":
                continue
            if feed_id in self.missing_feed_ids:
                continue
            if feed_id not in self.feed_emissions.keys():
                om.add_warning(
                    "Missing Purchased Feed Emissions",
                    f"Missing data for RuFaS feed {feed_id}, omitting from purchased feed emissions estimation.",
                    info_map,
                )
                self.missing_feed_ids.append(feed_id)
                continue
            emissions = amount_fed * self.feed_emissions[feed_id]
            emissions_per_feed_id["feed_emissions_total"] += emissions
            emissions_per_feed_id[feed_id] = emissions
        return emissions_per_feed_id

    def _setup_feed_emissions(self) -> dict[str, float]:
        """
        Setups up the table mapping CO2 emissions to purchased feeds types.

        Returns
        -------
        dict[str, float]
            Dictionary mapping the RuFaS feed ID to the amount of CO2 emissions in kg per kg's of dry matter feed.

        Notes
        -----
        This method works by:
        - Grabbing the table that maps all available FIPS county codes to purchased feeds emissions information.
        - Finding the row (index) which contains the desired FIPS county information.
        - Grabbing the information for each available feed ID from the row found in the previous step.

        """
        feed_emissions_data = im.get_data("purchased_feeds_emissions")

        county_codes = feed_emissions_data["county_code"]
        emissions_index = county_codes.index(self.FIPS_county_code)

        feed_keys = [key for key in feed_emissions_data.keys() if key != "county_code"]
        feed_emissions_dict = {key: feed_emissions_data[key][emissions_index] for key in feed_keys}

        return feed_emissions_dict
