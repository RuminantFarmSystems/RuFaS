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
from RUFAS.routines import Feed, Fields
from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure_management.manure_management import ManureManagement
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

        self.manure_management = ManureManagement(self.animal_management, weather, time)

    def annual_reset(self):
        """
        Description:
            Resets all annual variables that require reset
        """

        self.fields.annual_reset()
        self.animal_management.annual_reset()
        self.manure_management.annual_reset()

    def annual_mass_balance(self, time):
        for field in self.fields.fields.values():
            field.soil.annual_mass_balance(field.field_management, time)
        self.manure_management.annual_mass_balance()


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
            if Utility.is_leap_year(w_start_year):
                expected_w_file_size += (leap_year_length - w_start_day + 1)
            else:
                expected_w_file_size += (year_length - w_start_day + 1)

            # adds the length of each year
            for i in range(w_start_year + 1, w_end_year):
                if Utility.is_leap_year(i):
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
        if not Utility.is_leap_year(self.start_year):
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
        if not Utility.is_leap_year(self.end_year):
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
                if Utility.is_leap_year(year):
                    days += (_ for _ in range(self.start_day, leap_year_length + 1))
                else:
                    days += (_ for _ in range(self.start_day, year_length + 1))
            elif year == self.end_year:
                days = [_ for _ in range(1, self.end_day + 1)]
            else:
                if Utility.is_leap_year(year):
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
                if Utility.is_leap_year(self.start_year):
                    sim_length += self.leap_year_length - self.start_day
                else:
                    sim_length += self.year_length - self.start_day
            else:
                sim_length += len(self.years[i])

        return sim_length + 1


