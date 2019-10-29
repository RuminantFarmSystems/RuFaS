################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: classes.py
Description: Contains top level class definitions for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
################################################################################

import csv
import json
from pathlib import Path

from RUFAS import util
from RUFAS import errors

from RUFAS.routines import Field, Feed
from RUFAS.routines.animal.animal_management import AnimalManagement


# -------------------------------------------------------------------------------
# Class: State
# -------------------------------------------------------------------------------


class State:
    """Contains information about the current state of the farm.

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
    """

    def __init__(self, data, config, time):
        self.fields = []
        self.fields_data = data['fields']
        for field_name, field_data in self.fields_data.items():
            self.fields.append(Field(field_name, field_data, time))
        input_dir = util.get_base_dir() / 'Inputs'
        self.feed = Feed(read_json_file(input_dir / 'feed_storage' / data['feed']))
        self.animal_management = AnimalManagement(
            read_json_file(input_dir / 'animals' / data['animal']), config, self.feed)

    # ---------------------------------------------------------------------------
    # Method: annual_reset
    # ---------------------------------------------------------------------------
    def annual_reset(self):
        """Annual Reset"""

        # calculates water balance for the year before resetting necessary vals
        for field in self.fields:
            field.crop.annual_reset()
            field.soil.annual_reset()
        self.animal_management.annual_reset()
        self.feed.annual_reset()


def read_json_file(file_path: Path):
    try:
        if file_path.suffix == '.json':
            if not file_path.is_file():
                raise errors.UserInput(str(file_path) + ' does not exist')
        else:
            raise errors.UserInput(str(file_path) + ' is not a JSON file')

        with file_path.open('r') as f:
            data = json.load(f)

        return data

    except errors.UserInput as e:
        print(e.msg)


# -------------------------------------------------------------------------------
# Class: Config
# -------------------------------------------------------------------------------
class Config:
    """Contains configuration information of the simulation"""

    def __init__(self, data, weather_path_str):

        # gets a start/end date in the format year:julian-day. That way the program
        # can start in the middle of the year
        self.start_date = data['StartDate'].split(':')
        self.end_date = data['EndDate'].split(':')
        self.start_year = int(self.start_date[0])
        self.end_year = int(self.end_date[0])
        self.start_day = int(self.start_date[1])
        self.end_day = int(self.end_date[1])

        year_length = 365
        leap_year_length = 366

        # read in the input csv file
        weather_full_path = util.get_base_dir() / 'Inputs/weather' / weather_path_str

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # keeps track of how many lines are in the weather file
            line = 1
            # sets the starting and ending weather dates
            for row in readCSV:
                if len(row) == 0:
                    continue
                if line == 2:
                    w_start_year = int(row[0])
                    w_start_day = int(row[1])
                elif line > 2:
                    w_end_year = int(row[0])
                    w_end_day = int(row[1])
                line += 1

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
            if line - 1 != expected_weather_size + 1:
                print("Start and end dates of the Weather CSV file do not match the size.")
                if line - 1 > expected_weather_size + 1:
                    print("There may be duplicate days in: " + weather_full_path.name)
                else:
                    print("There may be missing days in: " + weather_full_path.name)
                print("\tWeather File Size: " + str(line - 1)
                      + "\n\tExpected size: " + str(expected_weather_size + 1) + "\n")

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
        
        self.sim_length = self.calc_sim_length(leap_year_length, year_length)
        self.output_dir = data['output_dir']
        self.diagnostic_dir = data['diagnostic_dir']

    def calc_sim_length(self, leap_year_length, year_length):
        '''
        Calculates and returns the length of the simulation in days.
        '''
        sim_length = 0
        for i in range(len(self.years)):
            if i == 0:
                #check for +-1
                if is_leap_year(self.start_year):
                    sim_length += leap_year_length - self.start_day
                else:
                    sim_length += year_length - self.start_day
            else:
                sim_length += len(self.years[i])
                
        return sim_length + 1
# -------------------------------------------------------------------------------
# Class: Weather
# -------------------------------------------------------------------------------
class Weather:
    """
    Contains daily weather information stored in 2D lists
    Data lists are in the format Data[year][julian_day].
    """

    def __init__(self, weather_path_str, years, w_start_year, w_start_day, start_year, start_day):

        # initialize data sets
        self.rainfall = []
        self.T_max = []
        self.T_min = []
        self.T_avg = []
        self.biomass = []
        self.radiation = []
        self.manureN = []
        # TODO: manureN is a temporary weather file input until the manure module is linked with the rest of the program
        self.T_avg_annual = []

        self.evaporation = []
        self.lCows = []
        self.dCows = []
        self.heifer = []
        self.calf = []
        self.beef = []
        self.beefCalf = []

        year_length = 365
        leap_year_length = 366

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
            self.biomass.append([0 for _ in range(len(year))])
            self.radiation.append([0 for _ in range(len(year))])
            self.manureN.append([0 for _ in range(len(year))])
            # TODO: manureN is a temporary weather file input until the manure
            # TODO: module is linked with the rest of the program

            # These are not currently inputs into the weather file. They may
            # be/may have been at some point.
            # self.evaporation.append([0 for _ in range(len(year))])
            # self.lCows.append([0 for _ in range(len(year))])
            # self.dCows.append([0 for _ in range(len(year))])
            # self.heifer.append([0 for _ in range(len(year))])
            # self.calf.append([0 for _ in range(len(year))])
            # self.beef.append([0 for _ in range(len(year))])
            # self.beefCalf.append([0 for _ in range(len(year))])

        # read in the input csv file
        weather_full_path = util.get_base_dir() / 'Inputs/weather' / weather_path_str

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
            counter = 0
            day = start_day
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
                        self.biomass[year][day - offset] = float(row[6])
                        self.radiation[year][day - offset] = float(row[7])
                        self.manureN[year][day - offset] = float(row[8])  # TODO: manureN is a temporary weather file input until the manure module is linked with the rest of the program
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


# Class: Time
# -------------------------------------------------------------------------------
class Time:
    """
    This object is responsible for creating and tracking time in the simulation.
    Time is currently represented as a year and day only.
    """

    def __init__(self, years, cal_year):

        self.start_year = cal_year
        self.cal_year = cal_year
        self.years = years
        self.year = 1  # Current Year

        # finds the first non-null day of the first year
        for i in range(0, len(years[0])):
            if years[0][i] is None:
                continue
            else:
                self.day = years[0][i]
                break

    # ---------------------------------------------------------------------------
    # Method: to_str
    # ---------------------------------------------------------------------------
    def to_str(self):
        """Returns a string representation of the current time.

        Returns:
            str: a String representation of the current time in the simulation
                in the format "Year: <year> Day: <day>"
        """

        return "Year: {} Day: {}".format(self.year, self.day)

    # ---------------------------------------------------------------------------
    # Method: advance
    # ---------------------------------------------------------------------------
    def advance(self):
        """Advances the time in the simulation by 1 day

        Automatically detects end of months and years
        """

        if self.end_year():
            self.day = 1
            self.year += 1
            self.cal_year += 1
        else:
            self.day += 1

    # ---------------------------------------------------------------------------
    # Method: end_year
    # ---------------------------------------------------------------------------
    def end_year(self):
        """Returns a bool signifying the end of a year.

        Returns:
            bool: True if it is the end of a year, False otherwise
        """

        # if the day is > the length of the current year, then the year is over
        return self.day > len(self.years[self.year - 1])

    # -------------------------------------------------------------------------------
    # Function: end_simulation
    # -------------------------------------------------------------------------------
    def end_simulation(self):
        """Checks whether the simulation has ended

        Returns:
            bool: True if the simulation has ended, false otherwise
        """

        # midyear end date adjusted
        if self.year > len(self.years):
            return True
        elif self.year == len(self.years):
            return self.day > len(self.years[self.year - 1])

        return False


#
# Helper method determines if the given year is a leap year
#
def is_leap_year(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False
