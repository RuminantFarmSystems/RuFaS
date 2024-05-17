import requests

from RUFAS.units import MeasurementUnits
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

im = InputManager()
om = OutputManager()

# The default county to be simulated by RuFaS is Dane County, WI.
DEFAULT_FIPS_COUNTY_CODE = 55025


class PurchasedFeedEmissionsEstimator:
    def __init__(self):
        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
        }

        try:
            self.FIPS_county_code = self._get_county_code()
        except requests.exceptions.RequestException or ValueError:
            om.add_warning(
                "Purchased Feed Emissions Estimator could not get valid simulation location.",
                f"Simulated location for calculating purchased feed emissions is being set to "
                f"{DEFAULT_FIPS_COUNTY_CODE=}.",
                info_map,
            )
            self.FIPS_county_code = DEFAULT_FIPS_COUNTY_CODE

        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
        }
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

        emissions_per_feed_id = {"feed_emissions_total": 0}

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

    def _get_county_code(self) -> int:
        """Gets the FIPS county code.

        Returns
        -------
        int
            FIPS county code.

        Raises
        ------
        ValueError
            If the location is not found.
        ValueError
            If the return value from the FCC's API is null.
        requests.exceptions.RequestException
            If the max attempts to reach FCC's API was reached and all attempts failed.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._get_county_code.__name__,
        }

        county_code_from_input = im.get_data("config.FIPS_county_code")
        if county_code_from_input is not None:
            return county_code_from_input

        om.add_log(
            "Feed Emissions Estimator found null FIPS county code in Input Manager.",
            "Attempting to find FIPS code using simulation location.",
            info_map,
        )

        location = self._get_geographic_coordinates()
        if not location:
            om.add_warning(
                "Feed Emissions Estimator could not find simulated location.",
                f"Defaulting to {DEFAULT_FIPS_COUNTY_CODE=}.",
                info_map,
            )
            raise ValueError("Could not find simulated location.")

        latitude = location[0]
        longitude = location[1]

        endpoint = "https://geo.fcc.gov/api/census/block/find"
        params = {"latitude": latitude, "longitude": longitude, "format": "json"}

        info_map["API_endpoint"] = endpoint
        info_map["API_call_parameters"] = params

        max_attempts = 3
        for attempt_count in range(max_attempts):
            om.add_log(
                "Feed Emissions API Call",
                f"Calling the FCC's FIPS County Code API, attempt: {attempt_count}",
                info_map,
            )
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                answer = response.json()
                returned_FIPS_code = answer["County"]["FIPS"]

                if returned_FIPS_code is None:
                    om.add_error(
                        "Null value returned by Feed Emissions API Call",
                        "Received a null value in a successful response from the FCC's FIPS County Code API.",
                        info_map,
                    )
                    raise ValueError("Null value returned by FCC's API.")

                om.add_log(
                    "Successful Feed Emissions API Call",
                    f"Got successful response from the FCC's FIPS County Code API on {attempt_count=}",
                    info_map,
                )
                return int(returned_FIPS_code)
            om.add_error(
                "Error Feed Emissions API Call",
                f"FCC's FIPS County Code API {attempt_count=} failed with {response.status_code=}.",
                info_map,
            )

        om.add_error(
            "All Feed Emissions API Calls Failed",
            f"Tried calling the FCC's FIPS county code API, all {max_attempts} failed.",
            info_map,
        )
        raise requests.exceptions.RequestException("Could not obtain FIPS county code from FCC API.")

    @staticmethod
    def _get_geographic_coordinates() -> (float, float) or None:
        field_keys: list[str] = im.get_data_keys_by_properties("field_properties")

        if not field_keys:
            return None

        latitude = im.get_data(f"{field_keys[0]}.absolute_latitude")

        longitude = im.get_data(f"{field_keys[0]}.longitude")

        return latitude, longitude

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
