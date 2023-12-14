import numpy as np

from RUFAS.config import Config
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.input_manager import InputManager
from RUFAS.time import Time
from RUFAS.util import Utility

im = InputManager()
om = OutputManager()


def is_leap_year(year):
    """
    Description:
        Helper method determines if the given year is a leap year
    Args:
        year: an int of the year
    Returns:
        bool: True if the year is a leap year
    """
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False


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

    def __init__(self, weather_file: dict, config: Config):
        """
        Initializes the a `Weather` instance using user-supplied whether data and overall simulation parameters.

        Parameters
        ----------
        weather_file : dict
            All the weather data available to be used by the simulation.
        config : Config
            Config instance containing information about the configuration of the simulation.

        Notes
        -----
        Contains daily weather information stored in 2D lists. Data lists are in the format Data[year][julian_day].
        Allows daily information to be accessed by indexing to [time.year - 1][time.day - 1] (list indexing starts at 0,
        time starts at 1).

        """

        years = config.years
        w_start_year = config.w_start_year
        w_start_day = config.w_start_day
        start_year = config.start_year
        start_day = config.start_day

        # initialize data sets
        self.__precipitation = []
        self.__max_daily_temperature = []
        self.__min_daily_temperature = []
        self.__mean_daily_temperature = []
        self.__radiation = []
        self.__irrigation = []
        self.__mean_annual_temperature: float = None
        self.__latitude: float = self._get_latitude()

        year_length = config.year_length
        leap_year_length = config.leap_year_length

        # calculate the number of days between the beginning of
        # the weather file and the next year
        if is_leap_year(w_start_year):
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
                if is_leap_year(temp_year):
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

        for i in range(len(weather_file['year'])):
            current_year = weather_file['year'][i]
            current_day = weather_file['jday'][i]

            current_year_index = current_year - start_year
            current_day_index = current_day - 1

            if not start_year <= current_year <= config.end_year:
                continue
            elif current_year == config.end_year and current_day > config.end_day:
                break

            self.__precipitation[current_year_index][current_day_index] = weather_file['precip'][i]
            self.__max_daily_temperature[current_year_index][current_day_index] = weather_file['high'][i]
            self.__min_daily_temperature[current_year_index][current_day_index] = weather_file['low'][i]
            self.__mean_daily_temperature[current_year_index][current_day_index] = weather_file['avg'][i]
            self.__radiation[current_year_index][current_day_index] = weather_file['Hday'][i]
            self.__irrigation[current_year_index][current_day_index] = weather_file['irrigation'][i]

        self.__mean_annual_temperature = self._calculate_average_annual_temperature(weather_file['avg'])

        info_map = {"class": self.__class__.__name__, "function": self.__init__.__name__, "prefix": "Weather"}
        om.add_variable("average_annual_temperature", self.__mean_annual_temperature, info_map)

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
        year = time.year
        day = time.day
        month = Utility.day_to_month_conversion(day, time.calendar_year)
        daylength = CurrentDayConditions.determine_daylength(day, self.__latitude, month)
        try:
            current_conditions = CurrentDayConditions(
                incoming_light=self.__radiation[year - 1][day - 1],
                min_air_temperature=self.__min_daily_temperature[year - 1][day - 1],
                mean_air_temperature=self.__mean_daily_temperature[year - 1][day - 1],
                max_air_temperature=self.__max_daily_temperature[year - 1][day - 1],
                annual_mean_air_temperature=self.__mean_annual_temperature,
                precipitation=self.__precipitation[year - 1][day - 1],
                irrigation=self.__irrigation[year - 1][day - 1],
                daylength=daylength
            )
        except IndexError:
            raise IndexError(f"Attempted to get weather conditions for day: {day}, year: {year}.")

        return current_conditions

    def record_weather(self, time: Time) -> None:
        """
        Records the current weather conditions in the OutputManager.

        Parameters
        ----------
        time: Time
            Time object containing the current time of the simulation.

        """
        info_map = {"class": self.__class__.__name__, "function": self.record_weather.__name__, "prefix": "Weather"}
        current_weather = self.get_current_day_conditions(time)
        om.add_variable("precipitation", current_weather.rainfall, info_map)
        om.add_variable("rainfall", current_weather.rainfall, info_map)
        om.add_variable("snowfall", current_weather.snowfall, info_map)
        om.add_variable("daylength", current_weather.daylength, info_map)
        om.add_variable("maximum_temperature", current_weather.max_air_temperature, info_map)
        om.add_variable("minimum_temperature", current_weather.min_air_temperature, info_map)
        om.add_variable("average_temperature", current_weather.mean_air_temperature, info_map)
        om.add_variable("radiation", current_weather.incoming_light, info_map)
        om.add_variable("irrigation", current_weather.irrigation, info_map)

    @staticmethod
    def _calculate_average_annual_temperature(daily_average_temperatures: list[float]) -> float:
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

        As of writing this, only the absolute is stored in field input files, so simulations of farms in the southern
        hemisphere will use incorrect daylength values.

        """
        field_input_keys = im.get_data_keys_by_properties("field_properties")

        if not field_input_keys:
            return 43.0723

        first_field_key = field_input_keys[0]
        latitude = im.get_data(f"{first_field_key}.abs_latitude")["abs_latitude"]
        return latitude
