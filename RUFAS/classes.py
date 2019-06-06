################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: classes.py
Description: Contains top level class definitions for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
'''
################################################################################

import csv
import math

from RUFAS import util
from RUFAS import errors
from RUFAS.routines import Soil, Animal, Feed, Crop


# -------------------------------------------------------------------------------
# Class: State
# -------------------------------------------------------------------------------
class State():
    '''Contains information about the current state of the farm.

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
    '''

    def __init__(self, data, config):
        self.soil = Soil(data['soil'], config)
        self.animal = Animal(data['animal'])
        self.feed = Feed(data['feed'])
        self.crop = Crop(data['crop'])

    # self.fieldOps = FieldOps()
    # self.herd = Herd()
    # self.housing = Housing()
    # self.manure = Manure()

    # ---------------------------------------------------------------------------
    # Method: annual_reset
    # ---------------------------------------------------------------------------
    def annual_reset(self):
        '''Annual Reset'''

        self.soil.annual_reset()
        self.animal.annual_reset()
        self.crop.annual_reset()
        self.feed.annual_reset()

    # self.fieldOps.annual_reset()
    # self.herd.annual_reset()
    # self.housing.annual_reset()
    # self.manure.annual_reset()


# -------------------------------------------------------------------------------
# Class: Config
# -------------------------------------------------------------------------------
class Config():
    '''Contains configuration information of the simulation'''

    def __init__(self, data, weather_path_str):

        # gets a start/end date in the format YYYY;julian-day. That way the program
        # can start in the middle of the year
        self.start_date = data['StartDate'].split(':')
        self.end_date = data['EndDate'].split(':')
        self.startYear = int(self.start_date[0])
        self.endYear = int(self.end_date[0])
        self.startDay = int(self.start_date[1])
        self.endDay = int(self.end_date[1])

        # read in the input csv file
        weather_full_path = util.get_base_dir() / weather_path_str

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # keeps track of how many lines are in the weather file
            counter = 1
            # sets the starting and ending weather dates
            for row in readCSV:
                if len(row) == 0:
                    continue
                if counter == 2:
                    w_start_year = int(row[0])
                    w_start_day = int(row[1])
                elif counter > 2:
                    w_end_year = int(row[0])
                    w_end_day = int(row[1])
                counter += 1

            # expected size of the csv file from start to end
            # to determine if the weather file has any gaps
            size_wCSV = 0
            if w_start_year % 4 == 0:
                size_wCSV += 367 - w_start_day
            else:
                size_wCSV += 366 - w_start_day
            for x in range(w_start_year + 1, w_end_year):
                if x % 4 == 0:
                    size_wCSV += 366
                else:
                    size_wCSV += 365
            size_wCSV += w_end_day

            # compares actual size of the file to expected size
            if counter - 1 != size_wCSV + 1:
                msg = "Start and end dates of the Weather CSV file do not match the size.\n" \
                      "There may be missing or duplicate days in: " + weather_full_path.name \
                      + "\n\tSize: " + str(counter - 1) + "\n\tExpected size: " + str(size_wCSV + 1)
                print(msg + "\n")

        self.w_start_year = w_start_year
        self.w_start_day = w_start_day
        self.w_end_year = w_end_year
        self.w_end_day = w_end_day

        # error statements if the start date is not within the weather data
        # special error statements for start and end years
        if self.startYear == w_start_year and self.startDay < w_start_day \
                or self.startYear < w_start_year:
            print("Start date invalid. Starting simulation on "
                  + str(w_start_year) + ":" + str(w_start_day))
            self.startDay = w_start_day
            self.startYear = w_start_year
        if self.endYear == w_end_year and self.endDay > w_end_day \
                or self.endYear > w_end_year:
            print("End date invalid. Ending simulation on "
                  + str(w_end_year) + ":" + str(w_end_day))
            self.endDay = w_end_day
            self.endYear = w_end_year

        # start date errors
        if not self.startYear % 4 == 0:
            if self.startDay < 1:
                print("Start date invalid. Starting simulation on "
                      + str(self.startYear) + ":" + str(1))
                self.startDay = 1
            if self.startDay > 365:
                print("Start date invalid. Starting simulation on "
                      + str(self.startYear) + ":" + str(365))
                self.startDay = 365
        else:
            if self.startDay < 1:
                print("Start date invalid. Starting simulation on "
                      + str(self.startYear) + ":" + str(1))
                self.startDay = 1
            if self.startDay > 366:
                print("Start date invalid. Starting simulation on "
                      + str(self.startYear) + ":" + str(366))
                self.startDay = 366

        # end date errors
        if not self.endYear % 4 == 0:
            if self.endDay < 1:
                print("End date invalid. Ending simulation on "
                      + str(self.endYear) + ":" + str(1))
                self.endDay = 1
            if self.endDay > 365:
                print("End date invalid. Ending simulation on "
                      + str(self.endYear) + ":" + str(365))
                self.endDay = 365
        else:
            if self.endDay < 1:
                print("End date invalid. Ending simulation on "
                      + str(self.endYear) + ":" + str(1))
                self.endDay = 1
            if self.endDay > 366:
                print("End date invalid. Ending simulation on "
                      + str(self.endYear) + ":" + str(366))
                self.endDay = 366

        # constructs a calendar of julian days and years, accounting for leap
        # years and mid-year start/end dates
        # each year in years starts with the calendar date at index zero and then
        # is filled with the days of the year that the program will run
        # the start and end dates will be specified by the user
        # years is used as a correctly size template for each of the weather arrays
        # in Weather()

        self.years = []

        for year in range(self.startYear, self.endYear + 1):

            days = [year]
            if year == self.startYear:
                days += [None for _ in range(1, self.startDay)]
                if year % 4 == 0:
                    days += (_ for _ in range(self.startDay, 367))
                else:
                    days += (_ for _ in range(self.startDay, 366))
            elif year == self.endYear:
                days += [_ for _ in range(1, self.endDay + 1)]
            else:
                if year % 4 == 0:
                    days += [_ for _ in range(1, 367)]
                else:
                    days += [_ for _ in range(1, 366)]

            self.years.append(days)

        if len(self.years) <= 0:
            raise errors.JSONfileData("CONFIG",
                                      "\tSimulation Duration must be at least 1 year")

        self.output_dir = data['output_dir']


# -------------------------------------------------------------------------------
# Class: Weather
# -------------------------------------------------------------------------------
class Weather():
    '''Contains daily weather information stored in 2D lists

    Data lists are in the format Data[year][julian_day].
    '''

    def __init__(self, weather_path_str, years, w_start_year, w_start_day):

        # initialize data sets and fill them with 0s

        self.rainfall = []
        self.T_max = []
        self.T_min = []
        self.T_avg = []
        self.biomass = []
        self.radiation = []
        self.addedN = []
        self.T_avg_annual = []

        self.evaporation = []
        self.lCows = []
        self.dCows = []
        self.heifer = []
        self.calf = []
        self.beef = []
        self.beefCalf = []

        # get the start day of the simulation
        for i in years[0]:
            if str(i).isdigit() and len(str(i)) < 4:
                start_day = i
                break

        # get the start year of the simulation
        start_year = years[0][0]

        # create the offset day from the start of the weather file to
        # the start of the next year
        if w_start_year % 4 == 0:
            w_day_offset = 366 - w_start_day
        else:
            w_day_offset = 365 - w_start_day

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
                if temp_year % 4 == 0:
                    days_to_start += 366
                else:
                    days_to_start += 365
                temp_year += 1

        # fill the weather arrays to an accurate size with zeros
        for year in years:
            self.rainfall.append([0 for _ in range(len(year) - 1)])
            self.T_max.append([0 for _ in range(len(year) - 1)])
            self.T_min.append([0 for _ in range(len(year) - 1)])
            self.T_avg.append([0 for _ in range(len(year) - 1)])
            self.biomass.append([0 for _ in range(len(year) - 1)])
            self.radiation.append([0 for _ in range(len(year) - 1)])
            self.addedN.append([0 for _ in range(len(year) - 1)])

            self.evaporation.append([0 for _ in range(len(year) - 1)])
            self.lCows.append([0 for _ in range(len(year) - 1)])
            self.dCows.append([0 for _ in range(len(year) - 1)])
            self.heifer.append([0 for _ in range(len(year) - 1)])
            self.calf.append([0 for _ in range(len(year) - 1)])
            self.beef.append([0 for _ in range(len(year) - 1)])
            self.beefCalf.append([0 for _ in range(len(year) - 1)])

        # read in the input csv file
        weather_full_path = util.get_base_dir() / weather_path_str

        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")

        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')

            # this for loop takes the weather data and parses
            # it into multiple 2D arrays [year][day] for different data points
            # used by the module
            current_row = 0
            year = 0
            counter = 0
            day = start_day
            skips = 0
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
                    offset = 1

                    # try/except statement to catch faulty weather data
                    try:
                        # fill data at appropriate location
                        self.rainfall[year][day - offset] = float(row[2])
                        self.T_max[year][day - offset] = float(row[3])
                        self.T_min[year][day - offset] = float(row[4])
                        self.T_avg[year][day - offset] = float(row[5])
                        self.biomass[year][day - offset] = float(row[6])
                        self.radiation[year][day - offset] = float(row[7])
                        self.addedN[year][day - offset] = float(row[8])

                    except (IndexError, ValueError) as e:
                        # prints out each problematic row in the weather CSV file
                        if skips == 0:
                            print("Weather CSV file has invalid data in: " + weather_full_path.name)
                            print("Invalid rows that are skipped:")

                        skips += 1
                        print("Row: " + str(current_row + skips + days_to_start) + "")
                        continue

                    # iterate year counter accounting for leap years
                    if year == len(years) - 1 and day == len(self.rainfall[year]):
                        year += 1
                    elif years[year][0] % 4 == 0:
                        if day == 366:
                            year += 1
                            day = 0
                    else:
                        if day == 365:
                            year += 1
                            day = 0
                    day += 1

                current_row += 1

            # calculates T_avg_annual for each year
            for i in range(len(years)):
                avg = sum(self.T_avg[i]) / len(years[i])
                self.T_avg_annual.append(avg)


# Class: Time
# -------------------------------------------------------------------------------
class Time():
    '''Contains information about the current time in the simulation

    This object is responsible for tracking time in the simulation
    '''

    def __init__(self, years, cal_year):

        self.cal_year = cal_year
        self.years = years
        self.year = 1  # Current Year

        # finds the first non-null day of the first year
        for i in range(1, len(years[0])):
            if years[0][i] is None:
                continue
            else:
                self.day = years[0][i]
                break

    # ---------------------------------------------------------------------------
    # Method: to_str
    # ---------------------------------------------------------------------------
    def to_str(self):
        '''Returns a string representation of the current time.

        Returns:
            str: a String representation of the current time in the simulation
                in the format "Year: <year> Day: <day>"
        '''

        return "Year: {} Day: {}".format(self.year, self.day)

    # ---------------------------------------------------------------------------
    # Method: advance
    # ---------------------------------------------------------------------------
    def advance(self):
        '''Advances the time in the simulation by 1 day

        Automatically detects end of months and years
        '''

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
        '''Returns a bool signifying the end of a year.

        Returns:
            bool: True if it is the end of a year, False otherwise
        '''

        # if the day is > the length of the current year, then the year is over
        return self.day > (len(self.years[self.year - 1]) - 1)

    # -------------------------------------------------------------------------------
    # Function: end_simulation
    # -------------------------------------------------------------------------------
    def end_simulation(self):
        '''Checks whether the simulation has ended

        Returns:
            bool: True if the simulation has ended, false otherwise
        '''

        # midyear end date adjusted
        if self.year > len(self.years):
            return True
        elif self.year == len(self.years):
            return self.day > len(self.years[self.year - 1])

        return False
