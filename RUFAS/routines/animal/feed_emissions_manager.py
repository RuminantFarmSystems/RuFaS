import json
import urllib.request as request

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()


class FeedEmissionsManager:

    def __init__(self):
        latitude, longitude = self._get_geographic_coordinates()

        self.county_code = self._get_county_code(latitude, longitude)
        print(f"county code: {self.county_code}")


    def _get_geographic_coordinates(self) -> (float, float):
        info_map = {
            "class": self.__class__,
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
        endpoint = "https://geo.fcc.gov/api/census/block/find?"
        query_parameters = f"latitude={latitude}&longitude={longitude}&format=json"
        call = endpoint + query_parameters

        with request.urlopen(call) as response:
            answer = response.read()
        answer = json.load(answer)

        if answer["status"] != "OK":
            info_map = {
                "class": self.__class__,
                "function": self._get_county_code.__name__
            }
            error_name = "Bad API response"
            error_message = f"Response: {answer}"
            om.add_error(error_name, error_message, info_map)
            raise ValueError(f"Bad API response: {answer}")

        county_code = answer["County"]["FIPS"]
        return county_code
