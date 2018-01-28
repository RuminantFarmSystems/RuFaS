################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# classes.py - Contains various class definitions
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

from MASM.routines import Soil

#-------------------------------------------------------------------------------
# Class: State
#        Contains information about the current state of the farm
#-------------------------------------------------------------------------------
class State():

    def __init__(self):
        
        self.location = Location()
        self.soil = Soil()
        
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

        #self.crops.annual_reset()
        #self.feed.annual_reset()
        #self.fieldOps.annual_reset()
        #self.herd.annual_reset()
        #self.housing.annual_reset()
        #self.manure.annual_reset()

#-------------------------------------------------------------------------------
# Class: Location
#        Contains the state of the farm's location 
#-------------------------------------------------------------------------------  
class Location():
    
    def __init__(self):
        self.latitude = 0.0
    
    def annual_reset(self):
        pass
    
#-------------------------------------------------------------------------------
# Class: Config
#        Contains configuration information of the simulation
#-------------------------------------------------------------------------------
class Config():

    def __init__(self):

        self.fName = "none"
        self.years = 1
        self.iterations = 0
        self.iterate = False
    
    #----------------------------------------------------------------------------
    # Function: modify_parameters
    #
    #----------------------------------------------------------------------------
    def modify_parameters(self, i):
        pass

#-------------------------------------------------------------------------------
# Class: Weather
#        Contains daily weather information stored in 3D lists
#        Data lists are in the format Data[year][month][day]
#-------------------------------------------------------------------------------
class Weather():

    def __init__(self):

        #
        # Weather Data in 2D lists -> [year][julianDay]
        #
        self.rainfall = [[]]
        self.tMax = [[]]
        self.tMin = [[]]
        self.tAvg = [[]]
        self.biomass = [[]]
        
        self.cumulative = 1.0
       
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
        self.i = 1  # Current Iteration number

    #----------------------------------------------------------------------------
    # Function: to_str
    # Returns: a String representation of the current time in the simulation in
    #          the format "d/m/y Rep: r"
    #----------------------------------------------------------------------------
    def to_str(self):
        return "{}/{}/{} Iteration: {}".format(self.d, self.m, self.y, self.i)

    #----------------------------------------------------------------------------
    # Function: MMDD_to_JulianDay
    # Returns: returns the julian day of the year given a particular month and 
    # dat
    #----------------------------------------------------------------------------    
    def MMDD_to_JulianDay(self, month, date):
        dayInMonths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        julianDay = 0
        for i in range(0, month-1):
            julianDay += dayInMonths[i]
        julianDay += date
        return julianDay
    
    #----------------------------------------------------------------------------
    # Function: julian_day
    # Returns: returns the julian day of the year given a particular month and 
    # dat
    #----------------------------------------------------------------------------    
    def julian_day(self):
        
        day_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        julian_day = 0
        for i in range(0, self.m - 1):
            julian_day += day_in_months[i]
        julian_day += self.d
        
        return julian_day
    
    #---------------------------------------------------------------------------
    # Function: advance_iteration
    #           Resets the time at the end of a simulation cycle
    #           Sets day, month, and year to 1 and increments i
    #---------------------------------------------------------------------------
    def advance_iteration(self):
        self.y = 1
        self.m = 1
        self.d = 1
        self.i += 1

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
        
# UNUSED CLASSES
"""    
#-------------------------------------------------------------------------------
# Class: Crops
#        Contains the state of the farm's crops 
#-------------------------------------------------------------------------------  
class Crops():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass

#-------------------------------------------------------------------------------
# Class: Feed
#        Contains the state of the farm's feed 
#-------------------------------------------------------------------------------  
class Feed():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass
        

#-------------------------------------------------------------------------------
# Class: FieldOps
#        Contains the state of the farm's field operations 
#-------------------------------------------------------------------------------  
class FieldOps():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass
    
#-------------------------------------------------------------------------------
# Class: Herd
#        Contains the state of the farm's herd 
#-------------------------------------------------------------------------------  
class Herd():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass
    

#-------------------------------------------------------------------------------
# Class: Housing
#        Contains the state of the farm's housing 
#-------------------------------------------------------------------------------  
class Housing():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass

#-------------------------------------------------------------------------------
# Class: Manure
#        Contains the state of the farm's manure 
#-------------------------------------------------------------------------------  
class Manure():
    def __init__(self):
        pass
    
    def annual_reset(self):
        pass
        
"""
