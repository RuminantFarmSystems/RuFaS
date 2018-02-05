################################################################################
#
# MASM: Modular Agricultural Systems Modeling Environment
#
# soil.py - 
#
# Authors: Kass Chupongstimun
#          Jit Patil
#
################################################################################

import math

#------------------------------------------------------------------------------
# Function: daily_soil_routine
# Executes all the daily soil routines
#------------------------------------------------------------------------------
def daily_soil_routine(soil, location, weather, time):
                   
    # calculate daily runoff 
    soil.dailyInfiltration(weather.rainfall[time.y-1]
                                  [time.julian_day()-1],
                                  weather.cumulative)
    
    # calculate daily transpiration 
    soil.dailyEvapotranspiration(time.julian_day()
        , weather.tMax[time.y-1][time.julian_day()-1]
        , weather.tMin[time.y-1][time.julian_day()-1]
        , weather.tAvg[time.y-1][time.julian_day()-1]
        , weather.biomass[time.y-1][time.julian_day()-1]
        , location.latitude)
        
    # calculate daily percolation
    soil.dailyPercolation()  
        
    # calculate daily soil erosion
    soil.dailySoilErosion(weather.rainfall[time.y-1]
        [time.julian_day()-1], 
        time.julian_day()) 
                        
        
#------------------------------------------------------------------------------
# Function: daily_soil_update
# Update attributes of soil in preparation of following day
#------------------------------------------------------------------------------
def daily_soil_update(soil, weather, time):
                
    # update indicator (var cumulative) of whether soil is frozen
    if float(weather.tAvg[time.y-1][time.julian_day()-1]) > 0:
        weather.cumulative = max(-10, min(20, weather.cumulative + 1.0))
    else:
        weather.cumulative = max(-10, min(20, weather.cumulative - 1.0))
            
    # update current soil water    
    soil.updateCurrentSoilWater(weather.rainfall[time.y-1]
        [time.julian_day()-1]) 

#-------------------------------------------------------------------------------
# Function: read_soil_layer
# Reads the data-fields associated with a layer of soil from the json file 
#-------------------------------------------------------------------------------        
def read_soil_layer(layerName, f, so):
    
    bottomDepth = 0.0
    currentSoilWater = 0.0
    kSat = 0.0
    
    for key, value in f.items():
        if(key == "BottomDepth"):
            bottomDepth = value   
        elif(key == "StartingSoilWater"):
            currentSoilWater = value
        elif(key == "Ksat"):
            kSat = value
        
    so.addSoilLayer(layerName, bottomDepth, currentSoilWater, kSat)
#-------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil 
#-------------------------------------------------------------------------------   
class Soil():
    
    listOfSoilLayers = [] 

    def __init__(self, data):
        
    # Values Initialized by Input
        self.wiltingPoint = data['WiltingPoint']
        self.fieldCapacity = data['FieldCapacity']
        self.saturation = data['Saturation']        
        self.profileDepth = data['ProfileDepth']
        self.CN2 = data['CN2'] # unitless, user-defined curve number (empirical)
     
        # soil erosion attributes
        self.fieldSlope = data['FieldSlope']
        self.slopeLength = data['SlopeLength']
        self.manning = data['Manning']
        self.fieldSize = data['FieldSize']
        self.practiceFactor = data['PracticeFactor']
        self.orgc = data['Orgc']
        self.sand = data['Sand']
        self.silt = data['Silt']
        self.clay = data['CN2']
        
        # daily output values
        self.runoff = 0.0
        self.Etrans = 0.0
        self.E0 = 0.0
        self.Esoil = 0.0
        
        self.dayInfiltraiton = 0.0 # daily infiltration
        self.sedimentYield = 0.0
        
        for layerName, layer in data["SoilLayers"].items():
            self.addSoilLayer(layerName, layer['BottomDepth'], layer['Ksat'])
            
        # sort layers by bottomDepth 
        self.listOfSoilLayers.sort(key=lambda x: x.bottomDepth) 
        
        # calculate initial depth of each soil layer
        for x in range(0, len(self.listOfSoilLayers)):
            if x == 0:
                self.listOfSoilLayers[x].depth = self.listOfSoilLayers[x].bottomDepth
            else:   
                self.listOfSoilLayers[x].depth = (self.listOfSoilLayers[x].bottomDepth
                    - self.listOfSoilLayers[x-1].bottomDepth)
        
        self.convertCurrentSoilWaterToMM() # calculate initial soil water in layer
        self.calculateWiltingWater() # calculate wilting water in layer
        self.calculateFcWater() # calculate field capacity water in layer

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
    def addSoilLayer(self, name, bd, ksat):
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
    
    def annual_reset(self):
        pass
    