"""
RUFAS: Ruminant Farm Systems Model
File name: classes.py

Description: Contains top level class definitions for RUFAS

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

import csv

from RUFAS import errors
from RUFAS.routines import Fields, Feed
from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure.manure_management import ManureManagement
from RUFAS.routines.manure_storage.manure_storage import ManureStorage
from RUFAS.util import Utility


class State:
    def __init__(self, data, config, weather, time):
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
        self.fields = Fields(data['fields'], time)
        input_dir = Utility.get_base_dir() / 'input'
        self.feed = Feed(Utility.read_json_file(input_dir / 'feed' / data['feed']))
        self.animal_management = AnimalManagement(
            Utility.read_json_file(input_dir / 'animal' / data['animal']), config, self.feed, weather, time)

        self.manure_storage = ManureStorage(self.animal_management)
        self.manure_management = ManureManagement(self.animal_management)

    def annual_reset(self):
        """
        Description:
            Resets all annual variables that require reset
        """

        self.fields.annual_reset()
        self.animal_management.annual_reset()
        self.manure_storage.annual_reset()

    def annual_mass_balance(self, time):
        for field in self.fields.fields.values():
            field.soil.annual_mass_balance(field.field_management, time)
        self.manure_storage.annual_mass_balance()


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
        self.seed = data['seed']

        year_length = 365
        leap_year_length = 366

        # read in the input csv file

        weather_full_path = Utility.get_base_dir() / 'input/weather' / weather_file

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # keeps track of how many lines are in the weather file
            file_line = 1
            # sets the starting and ending weather dates
            for row in readCSV:
                if len(row) == 0:
                    continue
                if file_line == 2:
                    w_start_year = int(row[0])
                    w_start_day = int(row[1])
                elif file_line > 2:
                    w_end_year = int(row[0])
                    w_end_day = int(row[1])
                file_line += 1

            # expected size of the csv file from start to end
            # to determine if the weather file has any gaps
            expected_w_file_size = 0
            if is_leap_year(w_start_year):
                expected_w_file_size += (leap_year_length - w_start_day + 1)
            else:
                expected_w_file_size += (year_length - w_start_day + 1)

            # adds the length of each year
            for i in range(w_start_year + 1, w_end_year):
                if is_leap_year(i):
                    expected_w_file_size += leap_year_length
                else:
                    expected_w_file_size += year_length

            # adds the last year
            expected_w_file_size += w_end_day

            # compares actual size of the file to expected size
            if file_line - 1 != expected_w_file_size + 1:
                print("Start and end dates of the Weather CSV file do not match the size.")
                if file_line - 1 > expected_w_file_size + 1:
                    print("There may be duplicate days in: " + weather_full_path.name)
                else:
                    print("There may be missing days in: " + weather_full_path.name)
                print("\tWeather File Size: " + str(file_line - 1)
                      + "\n\tExpected size: " + str(expected_w_file_size + 1) + "\n")

        self.w_start_year = w_start_year
        self.w_start_day = w_start_day
        self.w_end_year = w_end_year
        self.w_end_day = w_end_day

        # error statements if the start date is not within the weather data
        # special error statements for start and end years
        if self.start_year == w_start_year and self.start_day < w_start_day \
                or self.start_year < w_start_year:
            print("Start date invalid. Starting simulation on "
                  + str(w_start_year) + ":" + str(w_start_day))
            self.start_day = w_start_day
            self.start_year = w_start_year
        if self.end_year == w_end_year and self.end_day > w_end_day \
                or self.end_year > w_end_year:
            print("End date invalid. Ending simulation on "
                  + str(w_end_year) + ":" + str(w_end_day))
            self.end_day = w_end_day
            self.end_year = w_end_year

        # start date errors if the simulation starts before day 1 or after
        # the last possible day of the year
        if self.start_day < 1:
            print("Start date invalid. Starting simulation on "
                  + str(self.start_year) + ":" + str(1))
            self.start_day = 1
        if not is_leap_year(self.start_year):
            if self.start_day > year_length:
                print("Start date invalid. Starting simulation on "
                      + str(self.start_year) + ":" + str(year_length))
                self.start_day = year_length
        else:
            if self.start_day > leap_year_length:
                print("Start date invalid. Starting simulation on "
                      + str(self.start_year) + ":" + str(leap_year_length))
                self.start_day = leap_year_length

        # end date errors if the simulation ends before day 1 or after
        # the last possible day of the year
        if self.end_day < 1:
            print("End date invalid. Ending simulation on "
                  + str(self.end_year) + ":" + str(1))
            self.end_day = 1
        if not is_leap_year(self.end_year):
            if self.end_day > year_length:
                print("End date invalid. Ending simulation on "
                      + str(self.end_year) + ":" + str(year_length))
                self.end_day = year_length
        else:
            if self.end_day > leap_year_length:
                print("End date invalid. Ending simulation on "
                      + str(self.end_year) + ":" + str(leap_year_length))
                self.end_day = leap_year_length

        # checks that start date is not after end date
        if self.start_year > self.end_year \
                or (self.start_year == self.end_year and self.start_day > self.end_day):
            raise errors.JSONfileData("CONFIG", "\tThe start date must be before the end date")

        # constructs a calendar (years[]) of julian days and years, accounting for leap
        # years and mid-year start/end dates
        # each year in years starts with the calendar date at index zero and then
        # is filled with the days of the year that the program will run
        # the start and end dates will be specified by the user
        # years is used as a correctly size template for each of the weather arrays
        # in Weather()

        self.years = []

        for year in range(self.start_year, self.end_year + 1):

            if year == self.start_year == self.end_year:
                days = [None for _ in range(1, self.start_day)]
                days += [_ for _ in range(self.start_day, self.end_day + 1)]
            elif year == self.start_year:
                days = [None for _ in range(1, self.start_day)]
                if is_leap_year(year):
                    days += (_ for _ in range(self.start_day, leap_year_length + 1))
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
            while temp_year < start_year:
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

        # read in the input csv file
        weather_full_path = Utility.get_base_dir() / 'input/weather' / weather_file

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # this for loop takes the weather data and parses it into multiple
            # 2D arrays [year][day] for different weather variables used by the
            # module
            current_row = 0
            year = 0
            day = start_day
            # used to offset pointer to the start of the simulation
            # in the weather file
            counter = 0
            skips = 0
            offset = 1
            for row in readCSV:
                # limits weather data read in to the length of the simulation
                if year > len(years) - 1:
                    break

                # if a line is empty then skip it
                if len(row) == 0:
                    skips += 1
                    continue

                # sets a pointer to the start date of the simulation in the weather file
                if counter < days_to_start:
                    counter += 1
                    continue

                # row 0 contains variable names
                if current_row != 0:
                    # try/except statement to catch faulty weather data
                    try:
                        # fill data at appropriate location
                        self.rainfall[year][day - offset] = float(row[2])
                        self.T_max[year][day - offset] = float(row[3])
                        self.T_min[year][day - offset] = float(row[4])
                        self.T_avg[year][day - offset] = float(row[5])
                        self.radiation[year][day - offset] = float(row[6])
                        self.irrigation[year][day - offset] = float(row[7])
                    except(IndexError, ValueError):
                        # prints out each problematic row in the weather CSV file
                        skips += 1
                        if skips == 1:
                            print("Weather CSV file has invalid data in: " + weather_full_path.name
                                  + "\nInvalid rows that are skipped:")
                        if skips <= 5:
                            print("Row: " + str(current_row + skips + days_to_start) + "")
                        continue

                    # iterate year counter accounting for leap years
                    if day == len(years[year]):
                        year += 1
                        day = 0

                    day += 1

                current_row += 1

            # prints if there are more than 5 skipped lines in order to
            # prevent console clutter
            if skips > 5:
                print("Only printing first 5 invalid rows, there are " + str(skips)
                      + " total invalid rows")

            # calculates T_avg_annual for each year
            for i in range(len(years)):
                avg = sum(self.T_avg[i]) / (len(years[i]))
                self.T_avg_annual.append(avg)

            if len(years) > 2:
                T_avg = sum([self.T_avg_annual[j] for j in range(1, len(self.T_avg_annual) - 1)]) \
                        / (len(self.T_avg_annual) - 2)
            else:
                T_avg = sum([self.T_avg_annual[j] for j in range(len(self.T_avg_annual))]) \
                        / len(self.T_avg_annual)

            self.T_avg_annual[0] = T_avg
            self.T_avg_annual[len(self.T_avg_annual) - 1] = T_avg


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
