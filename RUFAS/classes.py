"""
RUFAS: Ruminant Farm Systems Model
File name: classes.py

Description: Contains top level class definitions for RUFAS

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

import numpy as np

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines import Feed
from RUFAS.routines.field.manager.field_manager import FieldManager
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.manure.manure_manager import ManureManager

im = InputManager()
om = OutputManager()


class State:
    def __init__(self, config, weather, time):
        """
        Description:
            Contains information about the current state of the farm.
            The state object represents the state of the farm at a certain instant in
            time. It contains information arranged in different objects by what routine
            they (mostly) relate to. The state object (or some of its sub-objects) will
            be passed to routines during the simulation, which may access the
            information in the different sub-objects in the state to use in its
            calculations.
            The state object should ONLY store persistent data that WILL be used in
            future calculations and/or reports.
            DO NOT store immediate operands or values that do not NEED to be accessed in
            the future or in an output report in the state object.

        Args:
            data: dictionary containing parsed information from the json file
                necessary to initialize the state
            config: instance of the Config class containing information necessary
                to initialize the state
            time: instance of the Time class containing information necessary to
                initialize the state
        """
        feed_class_config = im.get_data("feed")
        self.feed = Feed(feed_class_config)
        manure_class_config = im.get_data("manure_management")
        animal_class_config = im.get_data("animal")
        animal_class_config['manure_management_scenarios'] = manure_class_config['manure_management_scenarios']
        self.animal_manager = AnimalManager(animal_class_config, config, self.feed, weather, time)
        self.manure_manager = ManureManager(self.animal_manager, weather, time, manure_class_config)

        self.field_manager = FieldManager(manure_manager=self.manure_manager)

    def annual_reset(self):
        """
        Description:
            Resets all annual variables that require reset
        """
        self.field_manager.annual_update_routine()
        self.animal_manager.annual_reset()

    def annual_mass_balance(self, time):
        pass


class Config:

    def __init__(self, data, weather_file):
        """
        Description:
            Object containing configuration information of the simulation

        Args:
            data: dictionary containing information from the json file specified
                under "config"
            weather_file: path to the weather file specified in the json file
        """

        # gets a start/end date in the format year:julian-day. That way the program
        # can start in the middle of the year
        self.start_full_date = data['start_date'].split(':')
        self.end_full_date = data['end_date'].split(':')
        self.start_year = int(self.start_full_date[0])
        self.end_year = int(self.end_full_date[0])
        self.start_day = int(self.start_full_date[1])
        self.end_day = int(self.end_full_date[1])

        # set seed attributes
        self.set_seed = data['set_seed']
        self.seed = data['random_seed']

        # TODO: remove conditional once all json files have simulate_animals field
        self.simulate_animals = data['simulate_animals'] if 'simulate_animals' in data else True

        year_length = 365
        leap_year_length = 366

        self.w_start_year = self.start_year
        self.w_start_day = self.start_day
        self.w_end_year = self.end_year
        self.w_end_day = self.end_day

        self.years = []

        for year in range(self.start_year, self.end_year + 1):

            if year == self.start_year == self.end_year:
                days = [None for _ in range(1, self.start_day)]
                days += [_ for _ in range(self.start_day, self.end_day + 1)]
            elif year == self.start_year:
                days = [None for _ in range(1, self.start_day)]
                if is_leap_year(year):
                    days += (_ for _ in range(self.start_day,
                                              leap_year_length + 1))
                else:
                    days += (_ for _ in range(self.start_day, year_length + 1))
            elif year == self.end_year:
                days = [_ for _ in range(1, self.end_day + 1)]
            else:
                if is_leap_year(year):
                    days = [_ for _ in range(1, leap_year_length + 1)]
                else:
                    days = [_ for _ in range(1, year_length + 1)]

            self.years.append(days)

        self.leap_year_length = leap_year_length
        self.year_length = year_length

        self.sim_length = self.calc_sim_length()
        self.csv_dir = data['csv_dir']
        self.graphic_dir = data['graphic_dir']

    def calc_sim_length(self):
        """
        Description:
            Calculates and returns the length of the simulation in days.
        """
        sim_length = 0
        for i in range(len(self.years)):
            if i == 0:
                # check for leap year
                if is_leap_year(self.start_year):
                    sim_length += self.leap_year_length - self.start_day
                else:
                    sim_length += self.year_length - self.start_day
            else:
                sim_length += len(self.years[i])

        return sim_length + 1


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

        info_map = {"class": self.__class__.__name__, "function": self.__init__.__name__, "prefix": "Weather"}
        om.add_variable("average_annual_temperature(C)", self.T_avg_annual, info_map)

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


class Time:
    def __init__(self, config):
        """
        Description:
            This object is responsible for creating and tracking time in the simulation.
        Args:
            config: instance of the Config class containing information necessary
                to initialize time
        """

        calendar_year = config.start_year
        # number of years
        years = config.years

        self.start_year = calendar_year
        self.calendar_year = calendar_year
        self.years = years
        self.year = 1  # current year
        self.leap_year_length = config.leap_year_length
        self.year_length = config.year_length

        # finds the first non-null day of the first year
        for i in range(0, len(self.years[0])):
            if self.years[0][i] is None:
                continue
            else:
                self.day = self.years[0][i]
                break
        self.index = 0

    def to_str(self):
        """
        Description:
            Returns a string representation of the current time.
        Returns:
            str: a String representation of the current time in the simulation
                in the format "Year: <year> Day: <day>"
        """

        return "Year: {} Day: {}".format(self.year, self.day)

    def advance(self):
        """
        Description:
            Advances the time in the simulation by 1 day
            Automatically detects end of months and years
        """
        self.index += 1

        if self.end_year():
            self.day = 1
            self.year += 1
            self.calendar_year += 1
        else:
            self.day += 1

    def end_year(self):
        """
        Description:
            Returns a bool signifying the end of a year.
        Returns:
            bool: True if it is the end of a year, False otherwise
        """

        # if the day is > the length of the current year, then the year is over
        return self.day > len(self.years[self.year - 1])

    def end_simulation(self):
        """
        Description:
            Checks whether the simulation has ended
        Returns:
            bool: True if the simulation has ended, false otherwise
        """

        # midyear end date adjusted
        if self.year > len(self.years):
            return True
        elif self.year == len(self.years):
            return self.day > len(self.years[self.year - 1])

        return False

    @property
    def is_last_day_of_simulation(self):
        """Checks whether the current day is the last day of the simulation.

        Returns:
            bool: True if the current day is the last day of the simulation, false otherwise

        """
        if self.year == len(self.years):
            return self.day == len(self.years[self.year - 1])

        return False


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
