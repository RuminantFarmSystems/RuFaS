################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: classes.py
Description: Contains top level class definitions for RUFAS
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
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

    def __init__(self, data):

        # gets a start date in the format YYYY;julian-day. That way the program
        # can start in the middle of the year
        self.startDate = data['StartDate'].split(':')
        self.endDate = data['EndDate'].split(':')
        self.startYear = int(self.startDate[0])
        self.endYear = int(self.endDate[0])
        self.startDay = int(self.startDate[1])
        self.endDay = int(self.endDate[1]) #TODO changed from startDate to endDate

        if self.startYear == 2009 and self.startDay < 244:
            print("Start date invalid. Starting simulation on 2009:244")
            self.startDay = 244

        if self.endYear == 2016 and self.endDay > 243:
            print("End date invalid. Ending simulation on 2016:243")
            self.endDay = 243

        #TODO
        print("Start: " + str(self.startDate[0]) + ":" + str(self.startDay)
                + " | End: " + str(self.endDate[0]) + ":" + str(self.endDay))

        # constructs a calendar of julian days and years, accounting for leap
        # years and mid-year start/end dates

        cols = 0
        rows = 17
        # self.years = [[0 for i in range(cols)] for j in range(rows)]
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

    def __init__(self, weather_path_str, years):

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

        for i in years[0]:
            if str(i).isdigit() and len(str(i)) < 4:
                startDate = i
                break

        startYear = years[0][0]
        daysToStart = 0

        if startYear == 2009:
            daysToStart = startDate - 244
        elif startYear == 2010:
            daysToStart = 121 + startDate
        elif startYear == 2011:
            daysToStart = 121 + 365 + startDate
        elif startYear == 2012:
            daysToStart = 121 + 365*2 + startDate
        elif startYear == 2013:
            daysToStart = 121 + 365*2 + 366 + startDate
        elif startYear == 2014:
            daysToStart = 121 + 365*3 + 366 + startDate
        elif startYear == 2015:
            daysToStart = 121 + 365*4 + 366 + startDate
        elif startYear == 2016:
            daysToStart = 121 + 365*5 + 366 + startDate
        else:
            print("This should never happen.")

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

            # this for loop takes the 1D array of weather data [day] and parses
            # it into multiple 2D arrays [year][day] for different data points
            # used by the module
            currentRow = 0
            year = 0
            counter = 0
            for row in readCSV:
                # limits weather data read in to the length of the simulation
                if year > len(years) - 1:
                    break

                if counter < daysToStart:
                    counter += 1
                    continue

                # row 0 contains variable names
                if currentRow!= 0:
                    day = int(row[0])
                    offset = 1

                    # adjust year iteration for leap years
                    if day == 366:  # TODO Error is in leap years
                        year -= 1

                    # fill data at appropriate location
                    # TODO
                    # print("Year/Day - 1: " + str(year) + " " + str(day))

                    self.rainfall[year][day - offset] = float(row[1])
                    self.T_max[year][day - offset] = float(row[2])
                    self.T_min[year][day - offset] = float(row[3])
                    self.T_avg[year][day - offset] = float(row[4])
                    self.biomass[year][day - offset] = float(row[5])
                    self.radiation[year][day - offset] = float(row[6])
                    self.addedN[year][day - offset] = float(row[7])

                    # iterate year counter
                    if day == 365 or day == 366:
                        year += 1
                    if year == len(years) - 1 and day == len(self.rainfall[year]):
                        year += 1
                currentRow += 1

            # calculates T_avg_annual for each year
            for i in range(len(years)):
                avg = sum(self.T_avg[i]) / len(years[i])
                self.T_avg_annual.append(avg)
        test = "stop"

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
        for i in range(1, len(years[0])): #TODO changed to start at 1
            if years[0][i] == None:
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
        return self.day > (len(self.years[self.year - 1]) - 1) #TODO added - 1 at the end

    #-------------------------------------------------------------------------------
    # Function: end_simulation
    #-------------------------------------------------------------------------------
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
