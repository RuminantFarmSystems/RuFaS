from datetime import date
import numpy as np

from RUFAS.general_constants import GeneralConstants
from RUFAS.units import MeasurementUnits
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.input_manager import InputManager
from RUFAS.time import Time
from RUFAS.util import Utility

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
        Initializes the a `Weather` instance using user-supplied whether data and overall simulation parameters.

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
        self.im = InputManager()
        self.weather_data = {}
        current_date = time.start_date
        for i in range(len(weather_file["year"])):
            year = weather_file["year"][i]
            jday = weather_file["jday"][i]
            date_key = time.convert_simulation_day_to_date(jday)
            if time.start_date <= date_key <= time.end_date:
                conditions = CurrentDayConditions(
                    incoming_light=weather_file["Hday"][i], min_air_temperature=weather_file["low"][i],
                    mean_air_temperature=weather_file["avg"][i], max_air_temperature=weather_file["high"][i],
                    precipitation=weather_file["precip"][i], irrigation=weather_file["irrigation"][i]
                )
                self.weather_data[date_key] = conditions
            self.check_adequate_weather_data()

        years = time.years
        w_start_year = time.start_year_int
        w_start_day = time.start_day
        start_year = time.start_year_int
        start_day = time.start_day

        # initialize data sets
        self.__precipitation = []
        self.__max_daily_temperature = []
        self.__min_daily_temperature = []
        self.__mean_daily_temperature = []
        self.__radiation = []
        self.__irrigation = []
        self.__mean_annual_temperature: float = None
        self.__latitude: float = self._get_latitude()

        year_length = GeneralConstants.YEAR_LENGTH
        leap_year_length = GeneralConstants.LEAP_YEAR_LENGTH

        # calculate the number of days between the beginning of
        # the weather file and the next year
        if Utility.is_leap_year(w_start_year):
            w_day_offset = leap_year_length - w_start_day
        else:
            w_day_offset = year_length - w_start_day

        # calculates the amount of days between the start day of the weather
        # file and the start day of the simulation
        if start_year == w_start_year:
            days_to_start = start_day - w_start_day
        elif start_year == w_start_year + 1:
            days_to_start = w_day_offset + start_day
        else:
            days_to_start = w_day_offset + start_day
            temp_year = w_start_year + 1
            while temp_year != start_year:
                if Utility.is_leap_year(temp_year):
                    days_to_start += leap_year_length
                else:
                    days_to_start += year_length
                temp_year += 1

        # fill the weather arrays with zeros for the size of each year in years[]
        for year in years:
            self.__precipitation.append([0.0 for _ in range(len(year))])
            self.__max_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__min_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__mean_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__radiation.append([0.0 for _ in range(len(year))])
            self.__irrigation.append([0.0 for _ in range(len(year))])

        for i in range(len(weather_file["year"])):
            current_year = weather_file["year"][i]
            current_day = weather_file["jday"][i]

            current_year_index = current_year - start_year
            current_day_index = current_day - 1

            if not start_year <= current_year <= time.end_year_int:
                continue
            elif current_year == time.end_year_int and current_day > time.end_day:
                break

            self.__precipitation[current_year_index][current_day_index] = weather_file["precip"][i]
            self.__max_daily_temperature[current_year_index][current_day_index] = weather_file["high"][i]
            self.__min_daily_temperature[current_year_index][current_day_index] = weather_file["low"][i]
            self.__mean_daily_temperature[current_year_index][current_day_index] = weather_file["avg"][i]
            self.__radiation[current_year_index][current_day_index] = weather_file["Hday"][i]
            self.__irrigation[current_year_index][current_day_index] = weather_file["irrigation"][i]

        self.__mean_annual_temperature = self._calculate_average_annual_temperature(weather_file["avg"])

        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
            "prefix": "Weather",
        }
        om.add_variable(
            "average_annual_temperature",
            self.__mean_annual_temperature,
            dict(info_map, **{"units": MeasurementUnits.DEGREES_CELSIUS}),
        )

        # fill the weather arrays with zeros for the size of each year in years[]
        for year in years:
            self.__precipitation.append([0.0 for _ in range(len(year))])
            self.__max_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__min_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__mean_daily_temperature.append([0.0 for _ in range(len(year))])
            self.__radiation.append([0.0 for _ in range(len(year))])
            self.__irrigation.append([0.0 for _ in range(len(year))])

        for i in range(len(weather_file["year"])):
            current_year = weather_file["year"][i]
            current_day = weather_file["jday"][i]

            current_year_index = current_year - start_year
            current_day_index = current_day - 1

            if not start_year <= current_year <= time.end_year_int:
                continue
            elif current_year == time.end_year_int and current_day > time.end_day:
                break

            self.__precipitation[current_year_index][current_day_index] = weather_file["precip"][i]
            self.__max_daily_temperature[current_year_index][current_day_index] = weather_file["high"][i]
            self.__min_daily_temperature[current_year_index][current_day_index] = weather_file["low"][i]
            self.__mean_daily_temperature[current_year_index][current_day_index] = weather_file["avg"][i]
            self.__radiation[current_year_index][current_day_index] = weather_file["Hday"][i]
            self.__irrigation[current_year_index][current_day_index] = weather_file["irrigation"][i]

        self.__mean_annual_temperature = self._calculate_average_annual_temperature(weather_file["avg"])

        info_map = {
            "class": self.__class__.__name__,
            "function": "__init__",
            "prefix": "Weather",
        }
        om.add_variable(
            "average_annual_temperature",
            self.__mean_annual_temperature,
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
        IndexError
            While attempting to collect weather conditions that are not contained in the Weather object.

        """
        year = time.current_simulation_year
        day = time.current_julian_day
        daylength = CurrentDayConditions.determine_daylength(day, self.__latitude, time.current_calendar_year)
        try:
            current_conditions = CurrentDayConditions(
                incoming_light=self.__radiation[year - 1][day - 1],
                min_air_temperature=self.__min_daily_temperature[year - 1][day - 1],
                mean_air_temperature=self.__mean_daily_temperature[year - 1][day - 1],
                max_air_temperature=self.__max_daily_temperature[year - 1][day - 1],
                annual_mean_air_temperature=self.__mean_annual_temperature,
                precipitation=self.__precipitation[year - 1][day - 1],
                irrigation=self.__irrigation[year - 1][day - 1],
                daylength=daylength,
            )
        except IndexError:
            raise IndexError(f"Attempted to get weather conditions for day: {day}, year: {year}.")

        return current_conditions

    def get_conditions_series(self, time: Time, starting_offset: int, ending_offset: int) -> list[CurrentDayConditions]:
        """
        Generates a series of CurrentDayConditions.

        Parameters
        ----------
        time : Time
            Time instance containing the current time information of the simulation.
        starting_offset : int
            Number of days before or after the given date to start the weather conditions series.
        ending_offset : int
            Number of days before or after the given date to end the weather conditions series.

        Returns
        -------
        list[CurrentDayConditions]
            Series of current day conditions in chronological order.

        """
        current_date = Utility.convert_ordinal_date_to_month_date(time.current_calendar_year, time.current_julian_day)
        date_series = Utility.generate_time_series(current_date, starting_offset, ending_offset)

        starting_year_index = time.current_simulation_year - (current_date.year - date_series[0].year)
        starting_day_index = date_series[0].toordinal() - date(date_series[0].year, 1, 1).toordinal() + 1
        ending_year_index = time.current_simulation_year + (date_series[-1].year - current_date.year)
        ending_day_index = date_series[-1].toordinal() - date(date_series[-1].year, 1, 1).toordinal() + 1
        conditions_series = []
        for year in range(starting_year_index, ending_year_index + 1):
            if starting_year_index == ending_year_index:
                start_day = starting_day_index
                end_day = ending_day_index
            elif year == starting_year_index:
                start_day = starting_day_index
                end_day = len(self.__mean_daily_temperature[year]) - 1
            elif year == ending_year_index:
                start_day = 0
                end_day = ending_day_index
            else:
                start_day = 0
                end_day = len(self.__mean_daily_temperature[year]) - 1

            for day in range(start_day, end_day + 1):
                daylength = CurrentDayConditions.determine_daylength(day, self.__latitude, time.start_year_int + year)
                conditions = CurrentDayConditions(
                    incoming_light=self.__radiation[year - 1][day - 1],
                    min_air_temperature=self.__min_daily_temperature[year - 1][day - 1],
                    mean_air_temperature=self.__mean_daily_temperature[year - 1][day - 1],
                    max_air_temperature=self.__max_daily_temperature[year - 1][day - 1],
                    annual_mean_air_temperature=self.__mean_annual_temperature,
                    precipitation=self.__precipitation[year - 1][day - 1],
                    irrigation=self.__irrigation[year - 1][day - 1],
                    daylength=daylength,
                )
                conditions_series.append(conditions)
        return conditions_series

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

    def check_adequate_weather_data(self):
        pass
