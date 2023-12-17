import requests

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()


class FeedEmissionsManager:

    def __init__(self):
        latitude, longitude = self._get_geographic_coordinates()

        try:
            self.county_code = self._get_county_code(latitude, longitude)
        except requests.exceptions.RequestException:
            self.county_code = 55025

        info_map = {
            "class": self.__class__.__name__,
            "function": self.__init__.__name__
        }
        om.add_variable("FIPS_code", self.county_code, info_map)

        self.feed_emissions: dict[str, float] = self._setup_feed_emissions()
        om.add_variable("purchased_feed_emissions", self.feed_emissions, info_map)

    def create_daily_purchased_feed_emissions_report(self, daily_feed_totals: dict[str, float]) -> dict[str, float]:
        """
        Reports the total emissions from the feeds given to a pen.

        Parameters
        ----------
        daily_feed_totals : dict[str, float]
            Maps the feed type to the amount of feed given to the pen (kg dry matter).

        Returns
        -------
        dict[str, float]
            Maps the feed type to the amount of emissions generated in producing and delivering it (kg).

        """
        total_emissions = 0.0
        emissions_dict = {}
        for feed_id, amount_fed in daily_feed_totals.items():
            emissions = amount_fed * self.feed_emissions[feed_id]
            total_emissions += emissions
            emissions_dict[feed_id] = emissions
        emissions_dict["feed_emissions_total"] = total_emissions
        return emissions_dict


    def _get_geographic_coordinates(self) -> (float, float):
        info_map = {
            "class": self.__class__.__name__,
            "function": self._get_geographic_coordinates.__name__
        }

        latitude = 43.073
        longitude = -89.401

        field_keys: list[str] = im.get_data_keys_by_properties("field_properties")

        if not field_keys:
            warning_name = "Default Feed Emissions data"
            warning_message = "Could not obtain feed emissions geographic attributes, defaulting to Madison, WI."
            om.add_warning(warning_name, warning_message, info_map)

            return {"latitude": latitude, "longitude": longitude}

        field_key = field_keys[0]

        latitude_data_address = f"{field_key}.absolute_latitude"
        latitude = im.get_data(latitude_data_address)

        longitude_data_address = f"{field_key}.longitude"
        longitude = im.get_data(longitude_data_address)
        longitude = abs(longitude) * -1

        return latitude, longitude

    def _get_county_code(self, latitude: float, longitude: float) -> int:
        endpoint = "https://geo.fcc.gov/api/census/block/find"
        params = {"latitude": latitude, "longitude": longitude, "format": "json"}

        response = requests.get(endpoint, params=params)
        if response.status_code != 200:
            info_map = {
                "class": self.__class__,
                "function": self._get_county_code.__name__
            }
            error_name = "Bad API response"
            error_message = f"Response: {response}"
            om.add_error(error_name, error_message, info_map)
            raise requests.exceptions.RequestException(f"Bad API response: {response.text}")

        answer = response.json()

        county_code = int(answer["County"]["FIPS"])
        return county_code

    def _setup_feed_emissions(self) -> dict[str, float]:
        feed_emissions_data = im.get_data("purchased_feeds_emissions")

        county_codes = feed_emissions_data["county_code"]
        emissions_index = county_codes.index(self.county_code)

        feed_keys = [key for key in feed_emissions_data.keys() if key != "county_code"]
        feed_emissions_dict = {key: feed_emissions_data[key][emissions_index] for key in feed_keys}

        return feed_emissions_dict
