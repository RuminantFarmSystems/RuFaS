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
import json
from pathlib import Path
from RUFAS import util, errors
from RUFAS.routines import Field, Soil, Feed, Crop
from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.util import DatabaseReader
from RUFAS.util import read_json_file



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
        self.fields = []
        self.fields_data = data['fields']
        for field_name, field_data in self.fields_data.items():
            self.fields.append(Field(field_name, field_data, time))
        input_dir = util.get_base_dir() / 'input'
        self.feed = Feed(read_json_file(input_dir / 'feed' / data['feed']))
        self.animal_management = AnimalManagement(
            read_json_file(input_dir / 'animal' / data['animal']), config, self.feed, weather, time)

    def annual_reset(self):
        """
        Description:
            Resets all annual variables that require reset
        """

        for field in self.fields:
            field.crop.annual_reset()
            field.soil.annual_reset()
        self.animal_management.annual_reset()


class Config:

    def __init__(self, data, weather_data):

        # gets a start/end date in the format year:julian-day. That way the program
        # can start in the middle of the year
        self.weather_path_str = weather_data["weather_database"]
        self.weather_table = weather_data["weather_table_name"]
        self.dataset_ID = weather_data["dataset_ID"]

        self.start_full_date = data['start_date'].split(':')
        self.end_full_date = data['end_date'].split(':')
        self.start_year = int(self.start_date[0])
        self.end_year = int(self.end_date[0])
        self.start_day = int(self.start_date[1])
        self.end_day = int(self.end_date[1])
        self.run_tests = data['run_tests']
        year_length = 365
        leap_year_length = 366

        # read in the input csv file
        self.weather_full_path = util.get_base_dir() / self.weather_path_str
        if not self.weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        # reads database and stores dictionary values in values_DB list
        DB_reader = DatabaseReader(str(self.weather_full_path))
        values_DB = DB_reader.query(table="Observations", identifier="ID", desired_rows=[self.dataset_ID])

        # keeps track of how many lines are in the weather file
        line = len(values_DB)

        # sets the starting and ending weather dates
        w_start_year = values_DB[0]["year"]
        w_start_day = values_DB[0]["jday"]

        w_end_year = values_DB[len(values_DB) - 1]["year"]
        w_end_day = values_DB[len(values_DB) - 1]["jday"]

        # expected size of the csv file from start to end
        # to determine if the weather file has any gaps
        expected_weather_size = 0
        if is_leap_year(w_start_year):
            expected_weather_size += leap_year_length + 1 - w_start_day
        else:
            expected_weather_size += year_length + 1 - w_start_day
        for x in range(w_start_year + 1, w_end_year):
            if is_leap_year(x):
                expected_weather_size += leap_year_length
            else:
                expected_weather_size += year_length

        expected_weather_size += w_end_day

        # compares actual size of the file to expected size
        if line != expected_weather_size:
            print("Start and end dates of the Weather file do not match the size.")
            if line > expected_weather_size:
                print("There may be duplicate days in: " + self.weather_full_path.name)
            else:
                print("There may be missing days in: " + self.weather_full_path.name)
            print("\tWeather File Size: " + str(line)
                  + "\n\tExpected size: " + str(expected_weather_size) + "\n")

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

    def __init__(self, weather_data, config):
        """
        Description:
            Contains daily weather information stored in 2D lists
            Data lists are in the format Data[year][julian_day].
            Allows daily information to be accessed by indexing to
            [time.year - 1][time.day - 1] (list indexing starts at 0,
            time starts at 1)

        Args:
            weather_data: json section with the necessary weather database files
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
        self.manureN = []
        self.Taair = []

        year_length = config.year_length
        leap_year_length = config.leap_year_length

        w_start_year = config.w_start_year
        w_start_day = config.w_start_day
        start_year = config.start_year
        start_day = config.start_day
        years = config.years
        end_day = config.end_day

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
            self.rainfall.append([0 for _ in range(len(year))])
            self.T_max.append([0 for _ in range(len(year))])
            self.T_min.append([0 for _ in range(len(year))])
            self.T_avg.append([0 for _ in range(len(year))])
            self.radiation.append([0 for _ in range(len(year))])
            self.manureN.append([0 for _ in range(len(year))]) # TODO: manureN is a temporary weather file input until the manure module is implemented
            self.Taair.append([0 for _ in range(len(year))])

        # read in the input db file
        self.weather_path_str = weather_data["weather_database"]
        self.weather_table = weather_data["weather_table_name"]
        self.dataset_ID = weather_data["dataset_ID"]


        self.weather_full_path = util.get_base_dir() / self.weather_path_str

        if not self.weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        # reads database and stores dictionary values in values_DB list
        DB_reader = DatabaseReader(str(self.weather_full_path))
        values_DB = DB_reader.query(table="Observations", identifier="ID", desired_rows=[self.dataset_ID])

        # this for loop takes the weather data and parses it into multiple
        # 2D arrays [year][day] for different weather variables used by the
        # module
        current_row = 1
        year = 0
        counter = 0
        day = start_day
        skips = 0
        offset = 1
        for row in values_DB:
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

            # try/except statement to catch faulty weather data
            try:
                # fill data at appropriate location
                self.rainfall[year][day - offset] = float(row["precip"])
                self.T_max[year][day - offset] = float(row["high"])
                self.T_min[year][day - offset] = float(row["low"])
                self.T_avg[year][day - offset] = float(row["avg"])
                self.radiation[year][day - offset] = float(row["Hday"])
                # TODO: manureN is a temporary weather file input until the manure module is implemented
                self.manureN[year][day - offset] = float(row["manureN"])
                self.Taair[year][day - offset] = float(row["Taair"])
            except(IndexError, ValueError):
                # prints out each problematic row in the weather CSV file
                skips += 1
                if skips == 1:
                    print("Weather file has invalid data in: " + self.weather_full_path.name
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

        # calculates a long term average temperature over all years
        sum = 0
        for year in range(len(years)):
            if year == 0:
                sum += self.Taair[year][start_day]
            else:
                sum += self.Taair[year][0]
        long_term_avg = sum / len(years)

        # set average annual air temperature to long term average for years with incomplete data
        for year in range(len(years)):
            if year == 0 and start_day != 0:
                for day in range(len(self.Taair[year])):
                    self.Taair[year][day] = long_term_avg
            elif year == len(years) - 1 and end_day < 365:
                for day in range(len(self.Taair[year])):
                    self.Taair[year][day] = long_term_avg


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
