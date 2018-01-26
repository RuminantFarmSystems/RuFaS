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
import math

#-------------------------------------------------------------------------------
# Class: State
#        Contains information about the current state of the farm
#-------------------------------------------------------------------------------
class State():

    def __init__(self):
        
        self.location = Location()
        self.soil = Soil()

        self.crops = Crops()
        self.feed = Feed()
        self.fieldOps = FieldOps()
        self.herd = Herd()
        self.housing = Housing()
        self.manure = Manure()
        pass
    
        
    #----------------------------------------------------------------------------
    # Function: annual_reset
    #
    #----------------------------------------------------------------------------
    def annual_reset(self):
        
        self.crops.annual_reset()
        self.feed.annual_reset()
        self.fieldOps.annual_reset()
        self.herd.annual_reset()
        self.housing.annual_reset()
        self.manure.annual_reset()
        self.soil.annual_reset() 
        pass

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
    
#-------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil 
#-------------------------------------------------------------------------------   
class Soil():
    listOfSoilLayers = [] 

    def _init_(self):
        self.wiltingPoint = 0.0
        self.fieldCapacity = 0.0
        self.saturation = 0.0        
        self.profileDepth = 0.0 
        self.CN2 = 0.0 # unitless, user-defined curve number (empirical)
        self.dayInfiltraiton = 0.0 # daily infiltration
        
        # daily output values
        self.runoff = 0.0
        self.Etrans = 0.0
        self.E0 = 0.0
        self.Esoil = 0.0
        
        # soil erosion attributes
        self.fieldSlope = 0.0
        self.slopeLength = 0.0
        self.manning = 0.0
        self.fieldSize = 0.0
        self.practiceFactor = 0.0
        self.orgc = 0.0
        self.sand = 0.0
        self.silt = 0.0
        self.clay = 0.0
        self.sedimentYield = 0.0

    #---------------------------------------------------------------------------
    # Class: SoilLayer
    # An instance of this class represents a layer in the soil
    #---------------------------------------------------------------------------      
    class SoilLayer():
        def __init__(self):
            self.name = None
            self.bottomDepth = 0.0 # bottom depth of soil layer
            self.depth = 0.0 # depth of soil layer
            self.fcWater = 0.0 # constant
            self.wiltingWater = 0.0 # constant
            #self.currentSoilWater = 0.0
            
            self.currentSoilWaterMM = 0.0 # soil water in layer in mm

            # Variables to calculate dailyEvapotranspiration
            self.topEsoil = 0.0 # evaporation demand at top of layer
            self.bottomEsoil = 0.0 # evaporation demand at bottom of layer
            self.layerEsoil = 0.0 # evaporation demand at layer
            
            # Variables to calculate dailyPercolation
            self.ksat = 0 # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0  
            self.perc = 0.0 # amount of water that percolates to next layer
    
    #---------------------------------------------------------------------------
    # Function: addSoilLayer
    # Adds a soil layer to the list of soil layers
    #---------------------------------------------------------------------------        
    def addSoilLayer(self, name, bd, csw, ksat):
        soilLayer = self.SoilLayer()
        soilLayer.name = name
        soilLayer.bottomDepth = bd
        #soilLayer.currentSoilWater = csw
        soilLayer.ksat = ksat        
        self.listOfSoilLayers.append(soilLayer)
        
             
    #---------------------------------------------------------------------------
    # Function: calculateFcWater
    # Calculates the amount of water in soil profile for a given layer at 
    # field capacity (mm H2O). Called when soil portion of input is read.
    #---------------------------------------------------------------------------
    def calculateFcWater(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].fcWater = (self.listOfSoilLayers[x].depth
                    * self.fieldCapacity)
            
    #---------------------------------------------------------------------------
    # Function: calculateWiltingWater
    # Calculates the amount of water in soil profile for a given layer at 
    # wilting point (mm H2O). Called when soil portion of input is read.
    #---------------------------------------------------------------------------          
    def calculateWiltingWater(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].wiltingWater = (self.listOfSoilLayers[x].
                    depth * self.wiltingPoint)           
    
    #---------------------------------------------------------------------------
    # Function: convertCurrentSoilWaterToMM
    # Calculates the amount of soil water in a given layer in millimeters.
    # Called once when soil portion of input is read.
    #---------------------------------------------------------------------------  
    def convertCurrentSoilWaterToMM(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].currentSoilWaterMM = (
                self.listOfSoilLayers[x].depth * self.fieldCapacity)        
    
    #---------------------------------------------------------------------------
    # Function: getSumSoilWater
    # Calculates the total amount of soil water in all the soil layers (mm)
    #---------------------------------------------------------------------------                                                  
    def getSumSoilWater(self):
        totalSoilWater = 0.0       
        for soilLayer in self.listOfSoilLayers:
            totalSoilWater += soilLayer.currentSoilWaterMM
        return totalSoilWater

    #---------------------------------------------------------------------------
    # Function: getSumWiltingWater
    # Calculates the total amount of wilting water in all soil layers (mm H2O)
    #---------------------------------------------------------------------------  
    def getSumWiltingWater(self):
        totalWiltingWater = 0.0       
        for soilLayer in self.listOfSoilLayers:
            totalWiltingWater += soilLayer.wiltingWater
        return totalWiltingWater
    
    #---------------------------------------------------------------------------
    # Function: dailyInfiltration
    # Uses curve number approach (equations taken from SWAT 2009 documentation)
    #---------------------------------------------------------------------------       
    def dailyInfiltration(self, dailyRainfall, cumulative): 
          
        # curve number 1
        cn1 = self.CN2 - (20 * (100 - self.CN2)) / (100
                                                    - self.CN2 + math.exp(2.533 
                                                    - 0.0636 * (100- self.CN2)))
        # curve number 3
        cn3 = self.CN2 * math.exp(0.00673 * (100 - self.CN2))
        
        # maximum value of S on any given day (mm H2O)
        sMax = 25.4 * ((1000 / cn1) - 10)

        s3 = 25.4*((1000/cn3) - 10)
        
        # amount of water in soil profile at field capacity (mm H2O)
        FC = self.profileDepth * self.fieldCapacity
        
        # amount of water in soil profile at saturation (mm H2O)
        SAT = self.profileDepth * self.saturation

        # soil water content of entire profile, excluding water held at wilting
        # point (mm H2O)
        SW = self.getSumSoilWater() - self.getSumWiltingWater()
        
        #shape coefficients
        w2 = (math.log(FC / 
                      (1 -s3 * (1/sMax)) - FC) -math.log(
                          SAT/(1-2.54*(1/sMax))- SAT
                          )) /(SAT - FC)                     
        w1 = math.log((FC / 
                       (1 - (s3) * (1/sMax)))-
                      FC)+ w2*FC                   

        # retention paramenter (mm H2O)
        s = sMax * (1 - (SW/(SW + math.exp(w1 - (w2)*(SW)))))
        
        # when the top soil is frozen, s is modified
        if(cumulative <= 0):
            s = sMax * (1-math.exp(-0.000862 * s))
        
        # daily runoff (mm H2O)
        Q = 0.0
        if float(dailyRainfall) > 0.2*s:
            Q = ((float(dailyRainfall) - 0.2*s)**2) / (float(dailyRainfall) 
                                                       + 0.8*s) 
        
        self.runoff = Q 
        
        # daily infiltration (mm H20) 
        self.dayInfiltraiton = float(dailyRainfall) - self.runoff              

    #---------------------------------------------------------------------------
    # Function: dailyEvapotranspiration
    # Uses Hargreaves method for simplicity (equations taken from SWAT 2009 
    # documentation)
    # Step 1: Calculate Potential Evapotranspiration
    # Step 2: Calculate Crop Transpiration
    # Step 3: Calculate Sublimation and Soil Evaporation
    # Step 4: Partition Esoil among different soil layers 
    #---------------------------------------------------------------------------       
    def dailyEvapotranspiration(self, jday, tMax, tMin, tAvg, biomass, latitude):
        
    # Step 1: Calculate Potential Evapotranspiration
        av = 0.2618 # angular velocity of earth's rotation (rad*h^-1)
        
        # eccentricity correction factor of earth's orbit
        ECF = 1 + 0.033*math.cos((2*math.pi*(jday))/(365))
        
        # solar declination in radians
        SD = math.asin(0.4*math.sin((2*math.pi/365)*(jday-82)))
        
        # hours of sunrise
        TSR = math.acos(math.atan(SD)*math.tan(latitude))/av
        
        # extraterrestrial radiation (MJ*m^-2*d^-1)
        H0 = (37.59)*(ECF)*((av)*(TSR)*(math.sin(SD))*(math.sin(latitude))+
                            (math.cos(SD))*(math.cos(latitude))*
                            math.sin(av*TSR))
        
        # latent heat of vaporization (MJ*kg^-1)
        LHV = 2.501 - 2.361*(10**(-3))*float(tAvg)
        
        # potential evapotranspiration (mm*d^-1)
        self.E0 = max(0.001, 0.0023*H0*(float(tMax)-float(tMin))**0.5*
                      (float(tAvg) + 17.8)/LHV)
                
    # Step 2: Calculate Crop Transpiration
        # Leaf Area Index (calculated in Crop Growth Section)
        LAI = float(biomass) / 1500
        
        # maximum transpiration on a given day (mm H2O)
        # The actual amount of transpiration may be less than this maximum 
        # amount due to lack of available water in the rooting depth of the 
        # soil profile. 
        if LAI >= 0 and LAI <= 3.0:
            self.Etrans = (self.E0 * round(LAI,3)) / 3.0
        else:
            self.Etrans = self.E0
        
    # Step 3: Calculate Sublimation and soil evaporation 
        # aboveground biomass and residue (kg*ha^-1)        
        
        # soil cover index
        soilCov = math.exp(-5.0 * ((10)**(-5)) * float(biomass))
        
        # maximum soil evaporation/sublimation on a given day (mm H2O)
        Esoil = (round(self.E0,3) - self.Etrans) * (soilCov)
        self.Esoil = min(Esoil, ((Esoil*self.E0)/(Esoil + self.Etrans)))       
       
        # If snow is present and snow water is greater than Esoil, there is no 
        # evaporation from soil. If snow water is less than Esoil, both soil 
        # and snow will contribute to Esoil. 
        
    # Step 4: Partition Esoil among different soil layers
        # FOR each soil layer, calculate Esoil at top of layer, Esoil at bottom
        # of layer and then Esoil of entire layer
        for x in range(0, len(self.listOfSoilLayers)):
            if x == 0:
                self.listOfSoilLayers[x].topEsoil = 0
                self.listOfSoilLayers[x].bottomEsoil = (Esoil *
                    self.listOfSoilLayers[x].bottomDepth/ 
                    (self.listOfSoilLayers[x].bottomDepth +  math.exp
                    (2.374 - 0.00713*self.listOfSoilLayers[x].bottomDepth)))
            else:
                self.listOfSoilLayers[x].topEsoil = (self.listOfSoilLayers[x-1].
                                                     bottomEsoil)
                self.listOfSoilLayers[x].bottomEsoil = (Esoil * 
                    self.listOfSoilLayers[x].bottomDepth/ 
                    (self.listOfSoilLayers[x].bottomDepth + math.exp
                    (2.374 - 0.00713*self.listOfSoilLayers[x].bottomDepth)))       
            
            # The evaporation demand for a given soil layer is the difference 
            # between evaporation demands at the top and bottom of the layer. 
            # One soil layer cannot compensate for the inability of another layer 
            # to meet evaporation demand. Evaporation demand not met by a soil 
            # layer results in a reduction in actual ET. 
            if (self.listOfSoilLayers[x].currentSoilWaterMM > 
                                            self.listOfSoilLayers[x].fcWater):
                self.listOfSoilLayers[x].layerEsoil= (self.listOfSoilLayers[x].
                            bottomEsoil - self.listOfSoilLayers[x].topEsoil)
            # ELSE, When soil water content is less than field capacity, Esoil 
            # for a given layer is reduced as:
            else:
                self.listOfSoilLayers[x].layerEsoil=((self.listOfSoilLayers[x].
                            bottomEsoil - self.listOfSoilLayers[x].topEsoil)*
                            math.exp(2.5*(self.listOfSoilLayers[x].
                            currentSoilWaterMM-self.listOfSoilLayers[x].fcWater)
                            /(self.listOfSoilLayers[x].fcWater-self.
                            listOfSoilLayers[x].wiltingWater)))
            
    #---------------------------------------------------------------------------
    # Function: dailyPercolation
    # (equations taken from SWAT 2009 documentation)
    #---------------------------------------------------------------------------      
    def dailyPercolation(self):   
        # Calculate value of water available for percolation FOR each layer            
        for x in range(0, len(self.listOfSoilLayers)):
            # Volume of water available for percolation (SWperc) in a soil layer
            # is the difference between SW and WP. 
            SWperc = 0.0
            if (self.listOfSoilLayers[x].currentSoilWaterMM >= 
                                            self.listOfSoilLayers[x].fcWater):
                SWperc = (self.listOfSoilLayers[x].currentSoilWaterMM - 
                          (self.listOfSoilLayers[x].fcWater))
            
            # travel time for percolation (h)
            self.listOfSoilLayers[x].TT = (((self.saturation*
                    self.listOfSoilLayers[x].depth)-
                    self.listOfSoilLayers[x].fcWater)/ 
                                               self.listOfSoilLayers[x].ksat)
            t = 24 # time step (hours)
            
            #amount of water that percolates
            self.listOfSoilLayers[x].perc = (SWperc * 
                            (1 - math.exp(-t/self.listOfSoilLayers[x].TT)))  

    #---------------------------------------------------------------------------
    # Function: updateCurrentSoilWater
    # Updates the soil water within each layer at the end of each day. The 
    # model assumes 80% of plant transpiration comes out of the top soil layer 
    # and 20% from layer 2.
    #---------------------------------------------------------------------------
    def updateCurrentSoilWater(self, rainfall):
        for x in range(0, len(self.listOfSoilLayers)):
            if x == 0:
                self.listOfSoilLayers[x].currentSoilWaterMM = (max
                    (self.listOfSoilLayers[x].wiltingWater,
                    self.listOfSoilLayers[x].currentSoilWaterMM+float(rainfall)
                    -self.runoff-self.listOfSoilLayers[x].layerEsoil
                    -self.listOfSoilLayers[x].perc-self.Etrans*0.8))
            elif x== 1:
                    self.listOfSoilLayers[x].currentSoilWaterMM = (max
                        (self.listOfSoilLayers[x].wiltingWater, 
                         self.listOfSoilLayers[x].currentSoilWaterMM
                        -self.listOfSoilLayers[x].layerEsoil
                        -self.listOfSoilLayers[x].perc
                        +self.listOfSoilLayers[x-1].perc-(self.Etrans*0.2)))
            else:
                    self.listOfSoilLayers[x].currentSoilWaterMM = (max
                        (self.listOfSoilLayers[x].wiltingWater, 
                         self.listOfSoilLayers[x].currentSoilWaterMM
                        -self.listOfSoilLayers[x].layerEsoil
                        -self.listOfSoilLayers[x].perc
                        +self.listOfSoilLayers[x-1].perc))                    

    #---------------------------------------------------------------------------
    # Function: dailySoilErosion
    # Use MUSLE approach (equations taken from SWAT 2009 documentation) to 
    # determine soil erosion
    #--------------------------------------------------------------------------- 
    def dailySoilErosion(self, rainfall, jday):
        
        # time of concentration (h)
        Tconc = ((self.slopeLength**0.6) * (self.manning**0.6)) / (
            18 * (self.fieldSlope**0.3))
        
        alphaMean = (0.02083 + (1 - math.exp(-125 / (float(rainfall) + 5))))/2
        
        # fraction of daily rain during time of concentration
        alpha = 1 - math.exp(2 * Tconc * math.log(1 - alphaMean))

        # rain amount during time of concentration (mm)
        Rtc = alpha * float(rainfall)
    
        # rainfall intensity (mm/hr)
        I = Rtc / Tconc
        
        # peak runoff rate (m**3/sec)
        Qpeak = 0.0
        if float(rainfall) != 0:
            Qpeak = ((self.runoff/float(rainfall)) * I * 
                     self.fieldSize) / 3.6
        
        # gives low factors for soils with high sand contents and high values 
        # for soils with little sand
        Fcsand = 0.2 + 0.3 * math.exp(-0.256 * self.sand * (1-
                                                (self.silt/100)))
        
        # gives low factors for soils with high clay to silt ratios
        Fclsi = (self.silt / (self.clay + self.silt))**0.3
        
        # reduces soil erodibility for soils with high organic carbon content 
        Forgc = 1 - ((0.25 * self.orgc) / (self.orgc 
                            + math.exp(3.72 - 2.95 * self.orgc)))
        
        # reduces soil erodibility for soils with high sand contents
        Fsand = 1 - (0.7 * (1 - self.sand/100) / ((1 - self.sand/100) + 
                        math.exp(-5.51 + 22.9 * (1 / (self.sand/100)))))
        
        # USLE soil erodibility factor (Mg MJ**-1 mm**-1)
        K = Fcsand * Fclsi * Forgc * Fsand
        
        
        # C is USLE cover and management factor
        # 0.05 is the minimum value for C. This is an estimate.
        # 250 (COVER) NEEDS TO BE CHANGED (BIOMASS)
        C = math.exp((math.log(0.8) - math.log(0.05)) * 
                     math.exp(-0.00115 * 250) + math.log(0.05))
        
        
        # the exponential term m is calculated as...
        m = 0.6 * (1 - math.exp(-35.835 * self.fieldSlope))
        
        # angle of the slope
        alphahill = math.tan(self.fieldSlope)
        
        # USLE topographic factor
        LS = ((self.slopeLength / 22.1)**m) * (65.41 * (math.sin(alphahill)**2)
                    + 4.56 * math.sin(alphahill) + 0.065) 
        
        # sediment yield on a given day (metric tons)
        # Qpeak is peak runoff rate (m3/sec)
        sed = 11.8 * ((self.runoff * Qpeak)**0.56
                      ) * K * C * self.practiceFactor * LS
        self.sedimentYield = sed
    
    #---------------------------------------------------------------------------
    # Function: updateDailyOutput
    # Stores the daily values that need to be printed in the 'soil summary'
    # cvs file
    #---------------------------------------------------------------------------           
    def updateDailyOutput(self, SoilSumReportHandler, rainfall,day, year):
        SoilSumReportHandler.year.append(year)
        SoilSumReportHandler.julianDay.append(day)
        SoilSumReportHandler.precip.append(rainfall)
        SoilSumReportHandler.runoff.append(self.runoff)
        SoilSumReportHandler.potentialEvapotranspiration.append(self.E0)
        SoilSumReportHandler.cropTranspiration.append(self.Etrans)
        SoilSumReportHandler.sublimation.append(self.Esoil)
        
        for x in range(0, len(self.listOfSoilLayers)):
            SoilSumReportHandler.layersSoilWater[x].append(
                                    self.listOfSoilLayers[x].currentSoilWaterMM)
            SoilSumReportHandler.layersEsoil[x].append(
                                    self.listOfSoilLayers[x].layerEsoil)
            SoilSumReportHandler.layersPerc[x].append(
                                    self.listOfSoilLayers[x].perc)
            
        SoilSumReportHandler.sedimentYield.append(self.sedimentYield)

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
