import datetime

import numpy as np

from RUFAS.units import MeasurementUnits
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.input_manager import InputManager
from RUFAS.time import Time

om = OutputManager()


class Weather:
    """
    The `Weather` class manages all weather data used to run a single simulation.

    Attributes
    ----------
    __precipitation : list
        Amounts of precipitation that fall on given days (mm).
    __max_daily_temperature : list
        Maximum temperatures of days (°C).
    __min_daily_temperature : list
        Minimum temperatures of days (°C).
    __mean_daily_temperature : list
        Mean temperatures of days (°C).
    __radiation : list
        Energy from the sun (MJ/m^2).
    __irrigation : list
        Amounts of irrigation applied to fields on given days (mm).
    __mean_annual_temperature : float
        Mean of mean daily temperatures over all the weather data used by the simulation (°C).

    Notes
    -----
    All attributes besides the mean annual temperature are held as two-dimensional arrays, with the first array being
    the year, and the second being the day.

    """

    def __init__(self, weather_file: dict, time: Time):
        """
        Initializes the `Weather` instance using user-supplied whether data and overall simulation parameters.

        Parameters
        ----------
        weather_file : dict
            All the weather data available to be used by the simulation.
        time : Time
            The Time instance containing time configuration information of the simulation.

        Notes
        -----
        Contains daily weather information stored in 2D lists. Data lists are in the format Data[year][julian_day].
        Allows daily information to be accessed by indexing to [time.year - 1][time.day - 1] (list indexing starts at 0,
        time starts at 1).

        """
        self.weather_data = {}
        # current_date = time.start_date

        self.check_adequate_weather_data(weather_file, time)
        start_time = time.start_date
        end_time = time.end_date

        for i in range(len(weather_file["year"])):
            year = weather_file["year"][i]
            jday = weather_file["jday"][i]
            date_key = Time.convert_year_jday_date(year, jday)

            # Only include dates within the simulation period to save on space
            if start_time <= date_key <= end_time:
                conditions = CurrentDayConditions(
                    incoming_light=weather_file["Hday"][i],
                    min_air_temperature=weather_file["low"][i],
                    mean_air_temperature=weather_file["avg"][i],
                    max_air_temperature=weather_file["high"][i],
                    precipitation=weather_file["precip"][i],
                    irrigation=weather_file["irrigation"][i],
                )
                self.weather_data[date_key] = conditions

        self.mean_annual_temperature = self._calculate_average_annual_temperature(weather_file["avg"])

        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
            "prefix": "Weather",
        }
        om.add_variable(
            "average_annual_temperature",
            self.mean_annual_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )

    def get_current_day_conditions(self, time: Time) -> CurrentDayConditions:
        """
        Creates a CurrentDayConditions object containing all the weather conditions on the current day.

        Parameters
        ----------
        time: Time
            Time object containing the current time of the simulation.

        Returns
        -------
        CurrentDayConditions
            CurrentDayConditions instance including all the weather conditions of the specified date.

        Raises
        ------
        KeyError
            While attempting to collect weather conditions that are not contained in the Weather object.

        """
        latitude = self._get_latitude()
        daylength = CurrentDayConditions.determine_daylength(
            time.current_julian_day, latitude, time.current_calendar_year
        )
        try:
            self.weather_data[time.current_date].daylength = daylength
            self.weather_data[time.current_date].annual_mean_air_temperature = self.mean_annual_temperature
        except KeyError:
            raise KeyError(
                f"Attempted to get weather conditions for day: {time.current_julian_day},"
                f" year: {time.current_calendar_year}."
            )

        return self.weather_data[time.current_date]

    def get_conditions_series(self, time: Time, starting_offset: int, ending_offset: int) -> list[CurrentDayConditions]:
        """
        Generates a series of CurrentDayConditions.

        Parameters
        ----------
        time : Time
            A time instance containing the current time information of the simulation.
        starting_offset : int
            Number of days before or after the given date to start the weather conditions series.
        ending_offset : int
            Number of days before or after the given date to end the weather conditions series.

        Returns
        -------
        list[CurrentDayConditions]
            Series of current day conditions in chronological order.

        """
        condition_list = []
        latitude = self._get_latitude()

        for i in range(starting_offset, ending_offset + 1):
            date = time.current_date + datetime.timedelta(days=i)
            daylength = CurrentDayConditions.determine_daylength(int(date.strftime("%j")), latitude, date.year)
            self.weather_data[date].daylength = daylength
            self.weather_data[date].annual_mean_air_temperature = self.mean_annual_temperature
            condition_list.append(self.weather_data[date])

        return condition_list

    def record_weather(self, time: Time) -> None:
        """
        Records the current weather conditions in the OutputManager.

        Parameters
        ----------
        time: Time
            Time object containing the current time of the simulation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.record_weather.__name__,
            "prefix": "Weather",
        }
        current_weather = self.get_current_day_conditions(time)
        om.add_variable(
            "precipitation",
            current_weather.precipitation,
            dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}),
        )
        om.add_variable("rainfall", current_weather.rainfall, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}))
        om.add_variable("snowfall", current_weather.snowfall, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS}))
        om.add_variable("daylength", current_weather.daylength, dict(info_map, **{"units": MeasurementUnits.HOURS}))
        om.add_variable(
            "maximum_temperature",
            current_weather.max_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        om.add_variable(
            "minimum_temperature",
            current_weather.min_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        om.add_variable(
            "average_temperature",
            current_weather.mean_air_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )
        om.add_variable(
            "radiation",
            current_weather.incoming_light,
            dict(info_map, **{"units": MeasurementUnits.MEGAJOULES_PER_SQUARE_METER}),
        )
        om.add_variable(
            "irrigation", current_weather.irrigation, dict(info_map, **{"units": MeasurementUnits.MILLIMETERS})
        )

    @staticmethod
    def _calculate_average_annual_temperature(
        daily_average_temperatures: list[float],
    ) -> float:
        """
        Calculates the average annual air temperature based on the daily average air temperatures.

        Parameters
        ----------
        daily_average_temperatures : list(float)
            List of daily average air temperatures in the passed to be run by the simulation (degrees C).

        Returns
        -------
        float
            The average annual air temperature (degrees C).

        Notes
        -----
        This method calculates the average annual air temperature by taking the average of all daily average air
        temperatures provided in the weather input file. Previous implementations calculated the average annual
        temperature for individual years, which led to the value fluctuating more than desired.

        This method is intended to approximate SWAT's method for calculating the average annual temperature. SWAT
        calculates average high and low temperatures for each month over every simulated year, then averages those
        values to get a single annual average air temperature for the entire simulation. The exact implementation for
        this can be found at in the SWAT source code file `readwgn.f
        <https://bitbucket.org/blacklandgrasslandmodels/swat_development/src/master/readwgn.f>`_

        """
        return np.mean(np.array(daily_average_temperatures))

    @staticmethod
    def _get_latitude() -> float:
        """
        Retrieves (one of) the latitudes stored in the InputManager.

        Returns
        -------
        float
            The latitude of the location that is being simulated (degrees).

        Notes
        -----
        If no field files have been specified for this simulation, then the latitude defaults to 43.0723 degrees (the
        latitude of Madison, WI).

        This method will use the latitude from the first field input key that is returned to it by the Input Manager.

        As of writing this, only the absolute latitude is stored in field input files, so simulations of farms in the
        southern hemisphere will use incorrect daylength values.

        """
        im = InputManager()
        info_map = {
            "class": Weather.__name__,
            "function": Weather._get_latitude.__name__,
        }

        field_input_keys = im.get_data_keys_by_properties("field_properties")

        if not field_input_keys:
            om.add_warning(
                "No location data provided to Weather.",
                "Defaulting to latitude 43.0723 (location of Madison, WI).",
                info_map,
            )
            return 43.0723

        first_field_key = field_input_keys[0]
        latitude = im.get_data(f"{first_field_key}.absolute_latitude")
        return latitude

    @staticmethod
    def check_adequate_weather_data(weather_file: dict, time: Time) -> None:
        """
        Checks that there is enough weather data to cover the whole simulation time.

        Parameters
        ----------
        weather_file: dict
            A dictionary form of the weather file.
        time: Time
            The Time instance containing time configuration information of the simulation.

        Returns
        -------
        None

        """
        years_list = weather_file["year"]
        days_list = weather_file["jday"]
        current_date = time.start_date

        while current_date != time.end_date:
            current_date_year = current_date.timetuple().tm_year
            current_date_jday = current_date.timetuple().tm_yday
            if (current_date_jday in days_list) and (current_date_year in years_list):
                current_date += datetime.timedelta(days=1)
                continue
            else:
                raise Exception
