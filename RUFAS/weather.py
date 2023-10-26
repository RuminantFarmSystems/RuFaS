import numpy as np

from RUFAS.current_day_weather import CurrentDayWeather
from RUFAS.time import Time
from RUFAS.util import Utility


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

    def __init__(self, weather_file, config):
        """
        Description:
            Contains daily weather information stored in 2D lists
            Data lists are in the format Data[year][julian_day].
            Allows daily information to be accessed by indexing to
            [time.year - 1][time.day - 1] (list indexing starts at 0,
            time starts at 1)

        Args:
            weather_file: path to the weather file specified in the json file
            config: instance of the Config class containing information necessary
                to initialize the Weather object
        """

        years = config.years
        w_start_year = config.w_start_year
        w_start_day = config.w_start_day
        start_year = config.start_year
        start_day = config.start_day

        # initialize data sets
        self.rainfall = []
        self.T_max = []
        self.T_min = []
        self.T_avg = []
        self.radiation = []
        self.irrigation = []
        self.T_avg_annual = []

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
            self.rainfall.append([0.0 for _ in range(len(year))])
            self.T_max.append([0.0 for _ in range(len(year))])
            self.T_min.append([0.0 for _ in range(len(year))])
            self.T_avg.append([0.0 for _ in range(len(year))])
            self.radiation.append([0.0 for _ in range(len(year))])
            self.irrigation.append([0.0 for _ in range(len(year))])

        for i in range(len(weather_file['year'])):
            current_year = weather_file['year'][i]
            current_day = weather_file['jday'][i]

            current_year_index = current_year - start_year
            current_day_index = current_day - 1

            if not start_year <= current_year <= config.end_year:
                continue
            elif current_year == config.end_year and current_day > config.end_day:
                break

            self.rainfall[current_year_index][current_day_index] = weather_file['precip'][i]
            self.T_max[current_year_index][current_day_index] = weather_file['high'][i]
            self.T_min[current_year_index][current_day_index] = weather_file['low'][i]
            self.T_avg[current_year_index][current_day_index] = weather_file['avg'][i]
            self.radiation[current_year_index][current_day_index] = weather_file['Hday'][i]
            self.irrigation[current_year_index][current_day_index] = weather_file['irrigation'][i]

        self.T_avg_annual = self._calculate_average_annual_temperature(weather_file['avg'])

    def get_current_day_weather(self, time: Time) -> CurrentDayWeather:
        """
        Creates a CurrentDayWeather object containing all the weather conditions on the current day.

        Parameters
        ----------
        time: Time
            Time object containing the current time of the simulation.

        Returns
        -------
        CurrentDayWeather
            CurrentDayWeather instance including all the weather conditions of the specified date.

        Raises
        ------
        IndexError
            While attempting to collect weather conditions that are not contained in the Weather object.

        """
        year = time.year
        day = time.day
        month = Utility.day_to_month_conversion(time)
        daylength = CurrentDayWeather.determine_daylength(month)
        try:
            current_weather = CurrentDayWeather(incoming_light=self.radiation[year - 1][day - 1],
                                                min_air_temperature=self.T_min[year - 1][day - 1],
                                                mean_air_temperature=self.T_avg[year - 1][day - 1],
                                                max_air_temperature=self.T_max[year - 1][day - 1],
                                                annual_mean_air_temperature=self.T_avg_annual,
                                                precipitation=self.rainfall[year - 1][day - 1],
                                                irrigation=self.irrigation[year - 1][day - 1],
                                                daylength=daylength)
        except IndexError:
            raise IndexError(f"Attempted to get weather conditions for day: {time.day}, year: {time.year}.")

        return current_weather

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
