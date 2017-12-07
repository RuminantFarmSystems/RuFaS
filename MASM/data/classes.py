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

#-------------------------------------------------------------------------------
# Class: Config
#        Contains configuration information of the simulation
#-------------------------------------------------------------------------------     
class Config():
    
    def __init__(self):
        self.MASM_fName = "none"
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
        # Weather Data in 3D lists -> [year][month][day]
        #
        self.rainfall = [[[]]]
    
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
        if self.m > 12:
            return True
        else:
            return False
    
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