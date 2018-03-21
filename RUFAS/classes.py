################################################################################
#
# RUFAS: Ruminant Farm Systems Model
#
# classes.py - Contains class definitions
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import csv
import math

from RUFAS import util
from RUFAS import errors
from RUFAS.routines import Soil, Animal

#-------------------------------------------------------------------------------
# Class: State
#        Contains information about the current state of the farm
#-------------------------------------------------------------------------------
class State():

    def __init__(self, data):
        
        self.soil = Soil(data['soil'])
        self.animal = Animal(data['animal'])
        
        #self.crops = Crops()
        #self.feed = Feed()
        #self.fieldOps = FieldOps()
        #self.herd = Herd()
        #self.housing = Housing()
        #self.manure = Manure()   
        
    #----------------------------------------------------------------------------
    # Function: annual_reset
    #
    #----------------------------------------------------------------------------
    def annual_reset(self):
        
        self.soil.annual_reset() 
        self.animal.annual_reset()

        #self.crops.annual_reset()
        #self.feed.annual_reset()
        #self.fieldOps.annual_reset()
        #self.herd.annual_reset()
        #self.housing.annual_reset()
        #self.manure.annual_reset()
    
#-------------------------------------------------------------------------------
# Class: Config
#        Contains configuration information of the simulation
#-------------------------------------------------------------------------------
class Config():

    def __init__(self, data):
        
        if data['duration'] <= 0:
            raise errors.JSONfileData("CONFIG",
                                      "\tSimulation Duration must be at least 1 year")
        
        self.duration = data['duration']
        self.output_dir = data['output_dir']

#-------------------------------------------------------------------------------
# Class: Weather
#        Contains daily weather information stored in 3D lists
#        Data lists are in the format Data[year][julian_day]
#-------------------------------------------------------------------------------
class Weather():

    def __init__(self, weather_path_str, duration):

        #
        # Weather Data in 2D lists -> [year][julianDay]
        #
        self.rainfall = [[0 for _ in range(365)]for _ in range(duration)]
        self.tMax = [[0 for _ in range(365)]for _ in range(duration)]
        self.tMin = [[0 for _ in range(365)]for _ in range(duration)]
        self.tAvg = [[0 for _ in range(365)]for _ in range(duration)]
        self.biomass = [[0 for _ in range(365)]for _ in range(duration)]
        self.radiation = [[0 for _ in range(365)]for _ in range(duration)]
    
        rainfallData = []
        tMaxData = []
        tMinData = []
        tAvgData = []
        bioMassData = []
        radiationData = []
        
        weather_full_path = util.get_base_dir() / weather_path_str
        
        if not weather_full_path.is_file():
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file specified does not exist")
            
        #
        # Read data from CSV file
        # Data read is in the format data[day]
        # 1D list of length total number of days in the whole weather file
        #
        with weather_full_path.open('r') as f:
            readCSV = csv.reader(f, delimiter=',')
                
            currentRow = 0
            for row in readCSV:
                if currentRow != 0:
                    # 1) Read rainfall data
                    rainfallData.append(row[1])
                    
                    # 2) Read max temperature data
                    tMaxData.append(row[2])
                    
                    # 3) Read min temperature data
                    tMinData.append(row[3])
                    
                    # 4) Read avg temperature data
                    tAvgData.append(row[4])
                    
                    # 5) Read biomass data
                    bioMassData.append(row[5])
                    
                    # 6) Read radiation data
                    radiationData.append(row[6])
    
                currentRow += 1
        
        # Make sure weather data length matchs simulation duaration
        weather_file_years = math.floor(currentRow / 365)
        if weather_file_years != duration:
            raise errors.JSONfileData("WEATHER",
                                      "\tWeather file contains " +
                                      str(weather_file_years) +
                                      "\n\tSimulation specifies " + str(duration) +
                                      " years")
        #
        # Put weather data into the format:
        #    data[year][julian_day]
        #
         
        # 1) Update Rainfall in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(rainfallData):
                    break
                else:
                    self.rainfall[i][j] = rainfallData[i*365 + j]
        
        # 2) Update Max Temperature in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(tMaxData):
                    break
                else:
                    self.tMax[i][j] = tMaxData[i*365 + j]
                    
        # 3) Update Min Temperature in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(tMinData):
                    break
                else:
                    self.tMin[i][j] = tMinData[i*365 + j]
        
        # 4) Update Avg Temperature in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(tAvgData):
                    break
                else:
                    self.tAvg[i][j] = tAvgData[i*365 + j] 
                    
        # 5) Update biomass in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(bioMassData):
                    break
                else:
                    self.biomass[i][j] = bioMassData[i*365 + j]
                    
        # 6) Update radiation in weather
        for i in range(0, duration):
            for j in range(0, 365):
                if (i*365+j) >= len(radiationData):
                    break
                else:
                    self.radiation[i][j] = radiationData[i*365 + j]
       
#-------------------------------------------------------------------------------
# Class: Time
#        Contains information about the current time in the simulation
#        This object is responsible for tracking time in the simulation
#-------------------------------------------------------------------------------
class Time():

    def __init__(self):
        
        self.d = 1  # Current Day
        self.m = 1  # Current Month
        self.y = 1  # Current Year

    #----------------------------------------------------------------------------
    # Function: to_str
    # Returns: a String representation of the current time in the simulation in
    #          the format "d/m/y"
    #----------------------------------------------------------------------------
    def to_str(self):
        return "{}/{}/{}".format(self.d, self.m, self.y)
    
    #----------------------------------------------------------------------------
    # Function: julian_day
    # Returns: the julian day of the year
    #----------------------------------------------------------------------------    
    def julian_day(self):
        
        day_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        julian_day = 0
        for i in range(0, self.m - 1):
            julian_day += day_in_months[i]
        julian_day += self.d
        
        return julian_day

    #---------------------------------------------------------------------------
    # Function: advance
    #           Advances the time in the simulation by 1 day
    #           Automatically detects end of months and years
    #---------------------------------------------------------------------------
    def advance(self):
        if self.end_year():
            self.d = 1
            self.m = 1
            self.y += 1
        elif self.end_month():
            self.d = 1
            self.m += 1
        else:
            self.d += 1

    #---------------------------------------------------------------------------
    # Function: end_year
    # Returns: True if it is the end of a year
    #          False if it is not the end of a year
    #---------------------------------------------------------------------------
    def end_year(self):
        return self.m > 12

    #---------------------------------------------------------------------------
    # Function: end_month
    # Returns: True if it is the end of a month
    #          False if it is not the end of a month
    #---------------------------------------------------------------------------
    def end_month(self):
        if (self.d > 30) and (self.m == 4 or self.m == 6 or
                              self.m == 9 or self.m == 11):
            return True
        elif (self.d > 31) and (self.m == 1 or self.m == 3 or self.m == 5 or
                                self.m == 7 or self.m == 8 or self.m == 10 or
                                self.m == 12):
            return True
        elif self.d > 28 and self.m == 2:
            return True
        else:
            return False
