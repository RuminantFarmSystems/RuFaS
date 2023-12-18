import requests

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()


class PurchasedFeedEmissionsEstimator:

    def __init__(self):
        latitude, longitude = self._get_geographic_coordinates()

        dane_county_wi_FIPS_county_code = 55025
        try:
            self.FIPS_county_code = self._get_county_code(latitude, longitude)
        except requests.exceptions.RequestException:
            self.FIPS_county_code = dane_county_wi_FIPS_county_code

        info_map = {
            "class": self.__class__.__name__,
            "function": self.__init__.__name__
        }
        om.add_variable("FIPS_county_code", self.FIPS_county_code, info_map)

        self.feed_emissions: dict[str, float] = self._setup_feed_emissions()
        om.add_variable("purchased_feed_emissions", self.feed_emissions, info_map)

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
            "function": self.create_daily_purchased_feed_emissions_report.__name__
        }

        emissions_per_feed_id = {"feed_emissions_total": 0}

        for feed_id, amount_fed in daily_feed_totals.items():
            if feed_id == "dry_matter_intake_total":
                continue
            if feed_id in self.missing_feed_ids:
                continue
            if feed_id not in self.feed_emissions.keys():
                om.add_warning(
                    "Missing Purchased Feed Emissions",
                    f"Missing purchased feed emissions data for RuFaS feed {feed_id}.",
                    info_map
                )
                self.missing_feed_ids.append(feed_id)
                continue
            emissions = amount_fed * self.feed_emissions[feed_id]
            emissions_per_feed_id["feed_emissions_total"] += emissions
            emissions_per_feed_id[feed_id] = emissions
        return emissions_per_feed_id

    def _get_geographic_coordinates(self) -> (float, float):
        info_map = {
            "class": self.__class__.__name__,
            "function": self._get_geographic_coordinates.__name__
        }

        madison_wi_latitude = 43.073
        madison_wi_longitude = -89.401

        field_keys: list[str] = im.get_data_keys_by_properties("field_properties")

        if not field_keys:
            warning_name = "Default Feed Emissions data"
            warning_message = "Could not obtain feed emissions geographic attributes, defaulting to Madison, WI."
            om.add_warning(warning_name, warning_message, info_map)

            return {"latitude": madison_wi_latitude, "longitude": madison_wi_longitude}

        latitude = im.get_data(f"{field_keys[0]}.absolute_latitude")

        longitude = im.get_data(f"{field_keys[0]}.longitude")

        longitude = abs(longitude) * -1

        return latitude, longitude

    def _get_county_code(self, latitude: float, longitude: float) -> int:
        info_map = {
            "class": self.__class__,
            "function": self._get_county_code.__name__
        }

        endpoint = "https://geo.fcc.gov/api/census/block/find"
        params = {"latitude": latitude, "longitude": longitude, "format": "json"}

        max_attempts = 3
        for attempt_count in range(max_attempts):

            om.add_log(
                "Feed Emissions API Call",
                f"Calling the FCC's FIPS County Code API, attempt: {attempt_count}",
                info_map
            )
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                answer = response.json()
                om.add_log(
                    "Successful Feed Emissions API Call",
                    f"Got successful response from the FCC's FIPS County Code API on {attempt_count=}",

                    info_map
                )
                return int(answer["County"]["FIPS"])
            om.add_error(
                "Error Feed Emissions API Call",
                f"FCC's FIPS County Code API {attempt_count=} failed with {response.status_code=}.",

                info_map
            )

        om.add_error(
            "All Feed Emissions API Calls Failed",
            f"Tried calling the FCC's FIPS county code API, all {attempts} failed.",
            info_map
        )
        raise requests.exceptions.RequestException("Could not obtain FIPS county code from FCC API.")

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

        feed_keys = [key for key in feed_emissions_data.keys() if key != "FIPS_county_code"]
        feed_emissions_dict = {key: feed_emissions_data[key][emissions_index] for key in feed_keys}

        return feed_emissions_dict
