################################################################################
#
# RUFAS: Ruminant Farm Systems Model
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
def daily_soil_routine(soil, weather, time):

    # calculate and update the temperature of the soil layers
    soil.updateSoilTemperature(
        weather.biomass[time.year-1][time.day-1],
        weather.radiation[time.year-1][time.day-1],
        weather.tAvg[time.year-1][time.day-1],
        8.41,
        time.day)

    # calculate daily runoff
    soil.dailyInfiltration(weather.rainfall[time.year-1][time.day-1])

    # calculate daily transpiration
    soil.dailyEvapotranspiration(
        weather.tMax[time.year-1][time.day-1]
        , weather.tMin[time.year-1][time.day-1]
        , weather.tAvg[time.year-1][time.day-1]
        , weather.biomass[time.year-1][time.day-1]
        , weather.radiation[time.year-1][time.day-1])

    # calculate daily percolation
    soil.dailyPercolation()

    # calculate daily soil erosion
    soil.dailySoilErosion(weather.rainfall[time.year-1][time.day-1],
                          weather.biomass[time.year-1][time.day-1],
                          time.day)


#------------------------------------------------------------------------------
# Function: daily_soil_update
# Update attributes of soil in preparation of following day
#------------------------------------------------------------------------------
def daily_soil_update(soil, weather, time):

    # update current soil water
    soil.updateCurrentSoilWater(weather.rainfall[time.year-1][time.day-1])

#-------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil
#-------------------------------------------------------------------------------
class Soil():

    listOfSoilLayers = []
    fertilizerApplications = []
    manureApplications = []
    tillageOperations = []
    cropPUptakes = []


    def __init__(self, data, config):

        # Values Initialized by Input
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

        # soil temperature attributes
        self.soilAlbedo = data['SoilAlbedo']
        self.Tsurf = data['SoilLayers']['Layer1']['InitialTemperature']

        # create soil layers
        for layerName, layerData in data['SoilLayers'].items():
            self.listOfSoilLayers.append(self.SoilLayer(layerName, layerData))

        # sort layers by bottomDepth
        self.listOfSoilLayers.sort(key=lambda x: x.bottomDepth)

        # calculate initial depth of each soil layer
        for x in range(0, len(self.listOfSoilLayers)):
            if x == 0:
                self.listOfSoilLayers[x].depth = self.listOfSoilLayers[x].bottomDepth
            else:
                self.listOfSoilLayers[x].depth = (self.listOfSoilLayers[x].bottomDepth
                    - self.listOfSoilLayers[x-1].bottomDepth)
                
        # get fertilizer application information
        for fertApp, fertData in data['Fertilizers'].items():
            self.fertilizerApplications.append(self.Fertilizer(fertApp, fertData))
            
        # get manure application information
        for manureApp, manureData in data['ManureApplication'].items():
            self.manureApplications.append(self.Manure(manureApp, manureData))
            
        # get tillage application information
        for tillageApp, tillageData in data['TillageOperations'].items():
            self.tillageOperations.append(self.Tillage(tillageApp, tillageData))
            
        # get crop phosphorus uptake  information
        for uptakePApp, uptakePData in data['CropPUptake'].items():
            self.cropPUptakes.append(self.CropPUptake(uptakePApp, uptakePData))
                        
        self.convertCurrentSoilWaterToMM() # calculate initial soil water in layer
        self.calculateWiltingWater() # calculate wilting water in layer
        self.calculateFcWater() # calculate field capacity water in layer
        self.calculateSatWater() # calculate saturation water in layer

        # daily output values
        self.runoff = 0.0
        self.Etrans = 0.0
        self.E0 = 0.0
        self.Esoil = 0.0

        self.dayInfiltraiton = 0.0
        self.sedimentYield = 0.0
        self.snowCorrectedSed = 0.0

        # daily soil nitrogen values
        self.residue = data['Residue']
        self.freshNMineralRate = data['FreshNMineralRate']
        self.CToN = 0.0
        self.CToP = 0.0
        self.decayRate = 0.0
        self.freshMin = 0.0
        self.freshDecomp = 0.0

        self.freshNConc = 0.0
        self.activeNConc = 0.0
        self.stableNConc = 0.0
        self.NH4Conc = 0.0
        self.enrichmentRatio = 0.0
        self.freshNLoss = 0.0
        self.activeNLoss = 0.0
        self.stableNLoss = 0.0
        self.NH4Loss = 0.0
        self.runoffNO3Conc = 0.0
        self.NO3Runoff = 0.0
        self.runoffNH4Conc = 0.0
        self.NH4Runoff = 0.0
        
        # soil phosphorus attributes
        self.soilCoverType = data['SoilCoverType']
        self.pUptake = [[0 for x in range(366)] for y in range(config.endYear+1)]
        self.lightFactor = []
        self.yieldFactor = []
        self.summan = 0.0
        self.summanP = 0.0


    #------ INITIALIZE SOIL NITROGEN POOLS ------------------------------------
        # Calculate initial amount of NO3 in each soil layer;
        # Initial NO3 levels (kg/ha) in the soil are varied by depth as:
        for x in range(0, len(self.listOfSoilLayers)):
            # Initial NO3 levels (kg/ha) in the soil are varied by depth as:
            self.listOfSoilLayers[x].NO3 = ((7 * math.exp
                                (-self.listOfSoilLayers[x].bottomDepth /
                                1000)) * self.listOfSoilLayers[x].bulkDensity
                                 * self.listOfSoilLayers[x].depth) /100

            # Calculate initial amount of organic N in each soil layer;
            # Organic N (Active + Stable, mg/kg): is initialized as:
            self.listOfSoilLayers[x].orgN = (10 ** 4) * (
                self.listOfSoilLayers[x].orgC / 14)

            # Calculate initial amount (kg/ha) of active N in each soil layer;
            self.listOfSoilLayers[x].activeN = ((
                self.listOfSoilLayers[x].fracActiveN *
                self.listOfSoilLayers[x].orgN)*
                self.listOfSoilLayers[x].bulkDensity *
                self.listOfSoilLayers[x].depth) /100

            # Calculate initial amount (kg/ha) of stable N in each soil layer;
            self.listOfSoilLayers[x].stableN = (((1 -
                self.listOfSoilLayers[x].fracActiveN) *
                self.listOfSoilLayers[x].orgN) *
                self.listOfSoilLayers[x].bulkDensity *
                self.listOfSoilLayers[x].depth) /100

            # Calculate initial amount (kg/ha) of NH4 in each soil layer;
            self.listOfSoilLayers[x].NH4 = (self.listOfSoilLayers[x].NH4 *
                            self.listOfSoilLayers[x].bulkDensity *
                            self.listOfSoilLayers[x].depth) /100

        # Fresh N Pool --- only in top soil layer
        self.topLayerFreshN = ((0.0015*self.residue)*
                            self.listOfSoilLayers[x].bulkDensity *
                            self.listOfSoilLayers[x].depth) /100      


    #---------------------------------------------------------------------------
    # Class: SoilLayer
    # An instance of this class represents a layer in the soil
    #---------------------------------------------------------------------------
    class SoilLayer():

        def __init__(self, layerName, layerData):

            self.name = layerName

            self.bottomDepth = layerData['BottomDepth']
            self.wiltingPoint = layerData['WiltingPoint']
            self.fieldCapacity = layerData['FieldCapacity']
            self.saturation = layerData['Saturation']
            #self.currentSoilWater = layerData['StartingSoilWater']

            self.depth = 0.0 # depth of soil layer
            self.fcWater = 0.0 # constant
            self.satWater = 0.0 # constant
            self.wiltingWater = 0.0 # constant

            self.currentSoilWaterMM = 0.0 # soil water in layer in mm
            self.bulkDensity = layerData['BulkDensity']


            # Variables to calculate dailyEvapotranspiration
            self.topEsoil = 0.0 # evaporation demand at top of layer
            self.bottomEsoil = 0.0 # evaporation demand at bottom of layer
            self.layerEsoil = 0.0 # evaporation demand at layer

            # Variables used for soil temperature
            self.temperature = layerData['InitialTemperature']

            # Variables to calculate dailyPercolation
            self.ksat = layerData['Ksat'] # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.perc = 0.0 # amount of water that percolates to next layer

            self.labileP = layerData['LabileP'] # labile P in soil layer
            self.clay = layerData['Clay'] # soil clay % in soil layer


            # Variable to simulate nitrogenCycling
            self.orgC = layerData['OrgC%']
            self.activeMineralRate = layerData['ActiveMineralRate']
            self.cationExclusionFraction = layerData['CationExclusionFraction']
            self.denitrificationRate = layerData['DenitrificationRate']
            self.NH4 = layerData['NH4']

            # Initial NO3 levels (kg/ha) in the soil layer:
            self.NO3 = 0.0

            # Organic N (Active + Stable, mg/kg):
            self.orgN = 0.0

            # Initial Active N in layer:
            self.activeN = 0.0

            # Initial Stable N in layer:
            self.stableN = 0.0


            self.nMinAct = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.NO3Conc = 0.0
            self.NO3Perc = 0.0
            self.NH4Conc = 0.0
            self.NH4Perc = 0.0
            self.activeNConc = 0.0
            self.activeNPerc = 0.0
            self.nTrans = 0.0
            self.totNitriVolatil = 0.0

            self.fracActiveN = layerData['FracActiveN']
            self.volatileExchangeFactor = layerData['VolatileExchangeFac']
            
            # Variables to simulate phosphorus cycling
            self.OMpercent = layerData['OM%']
            self.soilOC = 0.0
            self.psp = 0.0
            
            self.activeP = 0.0
            self.stableP = 0.0
            self.orgP = 0.0
      
      
    #---------------------------------------------------------------------------
    # Class: Fertilizer
    # An instance of this class represents a particular fertilizer and the date
    # of its application
    #---------------------------------------------------------------------------      
    class Fertilizer():
        
        def __init__(self, FertName, FertData):
            self.name = FertName
            self.appYear = FertData['Year']
            self.appDay = FertData['JDay']
            self.fertPMass = FertData['PMass']
            self.depth = FertData['Depth']
            self.percentOnSurface = FertData['%onSurface']
            
    #---------------------------------------------------------------------------
    # Class: Manure
    # An instance of this class represents a particular manure and the date
    # of its application
    #---------------------------------------------------------------------------      
    class Manure():
        
        def __init__(self, manureName, manureData):
            self.name = manureName
            self.type = manureData['Type']
            self.appYear = manureData['Year']
            self.appDay = manureData['Jday']
            self.mass = manureData['Mass']
            self.totalP = manureData['TotalP']
            self.weip = manureData['WEIP']
            self.weop = manureData['WEOP']
            self.dryMatter = manureData['DryMatter']
            self.percentCover = manureData['%Cover']
            self.depth = manureData['Depth']
            self.percentOnSurface = manureData['%onSurface']


    #---------------------------------------------------------------------------
    # Class: Tillage
    # An instance of this class represents a particular tillage and the date
    # of its application
    #---------------------------------------------------------------------------      
    class Tillage():
        
        def __init__(self, tillageName, tillageData):
            self.name = tillageName
            self.appYear = tillageData['Year']
            self.appDay = tillageData['Jday']
            self.percentIncorporate = tillageData['%Incorporate']
            self.percentMixed = tillageData['%Mixed']
            self.depth = tillageData['Depth']
            
    #---------------------------------------------------------------------------
    # Class: CropPUptake
    # An instance of this class represents a particular uptake and the date
    # of uptake
    #---------------------------------------------------------------------------      
    class CropPUptake():
        
        def __init__(self, uptakeName, uptakeData):
            self.name = uptakeName
            self.uptakeYear = uptakeData['Year']
            self.pUptake = uptakeData['PUptake']
            
                    
    #---------------------------------------------------------------------------
    # Function: calculateFcWater
    # Calculates the amount of water in soil profile for a given layer at
    # field capacity (mm H2O). Called when soil portion of input is read.
    #---------------------------------------------------------------------------
    def calculateFcWater(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].fcWater = (self.listOfSoilLayers[x].depth
                    * self.listOfSoilLayers[x].fieldCapacity)


    #---------------------------------------------------------------------------
    # Function: calculateSatWater
    # Calculates the amount of water in soil profile for a given layer at
    # saturation (mm H2O). Called when soil portion of input is read.
    #---------------------------------------------------------------------------
    def calculateSatWater(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].satWater = (self.listOfSoilLayers[x].depth
                    * self.listOfSoilLayers[x].saturation)

    #---------------------------------------------------------------------------
    # Function: calculateWiltingWater
    # Calculates the amount of water in soil profile for a given layer at
    # wilting point (mm H2O). Called when soil portion of input is read.
    #---------------------------------------------------------------------------
    def calculateWiltingWater(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].wiltingWater = (self.listOfSoilLayers[x].
                    depth * self.listOfSoilLayers[x].wiltingPoint)

    #---------------------------------------------------------------------------
    # Function: convertCurrentSoilWaterToMM
    # Calculates the amount of soil water in a given layer in millimeters.
    # Called once when soil portion of input is read.
    #---------------------------------------------------------------------------
    def convertCurrentSoilWaterToMM(self):
        for x in range(0, len(self.listOfSoilLayers)):
            self.listOfSoilLayers[x].currentSoilWaterMM = (
                self.listOfSoilLayers[x].depth * self.listOfSoilLayers[x]
                .fieldCapacity)

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
    def dailyInfiltration(self, dailyRainfall):

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
        FC = self.profileDepth * self.listOfSoilLayers[0].fieldCapacity

        # amount of water in soil profile at saturation (mm H2O)
        SAT = self.profileDepth * self.listOfSoilLayers[0].saturation

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
        if(self.listOfSoilLayers[0].temperature <= 2):
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
    def dailyEvapotranspiration(self, tMax, tMin, tAvg, biomass, radiation):

    # Step 1: Calculate Potential Evapotranspiration
        # extraterrestrial radiation (MJ*m^-2*d^-1) --> MAKE INPUT VARIABLE
        H0 = float(radiation)

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
            self.listOfSoilLayers[x].TT = (((self.listOfSoilLayers[x].saturation
                    * self.listOfSoilLayers[x].depth)-
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
    def dailySoilErosion(self, rainfall, biomass, day):

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
        Fclsi = (self.silt / (self.listOfSoilLayers[0].clay + self.silt))**0.3

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
                     math.exp(-0.00115 * float(biomass)) + math.log(0.05))


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

        snowCorrectedSed = sed
        if day < 95 or day > 300:
            snowCorrectedSed = sed/(math.exp(3*20/25.4))
        self.snowCorrectedSed = snowCorrectedSed


    #---------------------------------------------------------------------------
    # Function: dailySoilTemperature
    # Equations taken from SWAT 2009 documentation to determine temperature of
    # soil
    #---------------------------------------------------------------------------
    def updateSoilTemperature(self, biomass, radiation, Tavg, TavgAnnual, day):

        albedoSoil = self.soilAlbedo # soil albedo constant
        bd = self.listOfSoilLayers[0].bulkDensity # soil bulk density (g/cm^3)
        CV = float(biomass) # above ground biomass and residue (kg/ha)
        Hday = float(radiation) # daily solar radiation (user input, MJ/m2)
        Tav = float(Tavg) # average daily temperature (oC)
        SW = self.getSumSoilWater() # total soil water in the profile (mm)
        ztot = self.profileDepth # total soil profile depth
        Taair = TavgAnnual # Average annual air temperature (C)

        # soil cover index
        cover = math.exp(-0.00005 * float(CV))

        # daily albedo
        albedo = 0.23 * (1 - cover) + albedoSoil * cover

        # radiation term
        radiate = (Hday * (1 - albedo) - 14) / 20

        # Temperature of a bare soil surface (C)
        Tbare = Tav + radiate * Tav

        # weight factor taking snow cover into account
        coverFactor = (CV / (CV + math.exp(7.563-0.0001297 * (-CV))))

        # snow water content on the current day (mm)
        SNOW = 0
        if day > 300 or day < 95:
            SNOW = 0.8
        snowFactor = (SNOW*10 / (SNOW*10 + math.exp(6.055-0.3002* SNOW*10)))

        # used cover factor
        bcv = max(coverFactor, snowFactor)

        # Daily soil surface temperature (C)
        self.Tsurf = (bcv * self.Tsurf) + ((1 - bcv) * Tbare)

        # scaling factor for soil water
        scale = SW / ((0.356-0.144*bd) * ztot)

        # maximum damping depth (mm)
        ddmax = 1000 + (2500 * bd) / (bd + 686 * math.exp(-5.63 * bd))

        # damping depth (mm)
        dd = ddmax * math.exp(math.log(500/ddmax) * ((1-scale)/(1+scale))**2)

        # lag coefficient
        L = 0.8

        # depth at the center of the soil layer
        z = 0.0

        # Calculate soil temperature for each soil layer
        for x in range(0, len(self.listOfSoilLayers)):

            # calculate depth at the center of the soil layer
            if x == 0:
                z = self.listOfSoilLayers[x].bottomDepth/2
            else:
                z = (self.listOfSoilLayers[x].bottomDepth +
                     self.listOfSoilLayers[x-1].bottomDepth)/2

            # soil temperature (C) at depth z (mm) on previous day
            TsoilPrev = self.listOfSoilLayers[x].temperature

            # ratio of depth at the center of soil layer to damping depth
            zd = z / dd

            # depth factor
            df = zd/ (zd + math.exp(-0.867 - 2.078 * zd))

            # soil temperature (C) at depth z (mm)
            self.listOfSoilLayers[x].temperature = (
                L * TsoilPrev) + (1-L) * (df * (Taair-self.Tsurf) + self.Tsurf)

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
                    -self.listOfSoilLayers[x].perc))#-self.Etrans*0.8))
            elif x== 1:
                    self.listOfSoilLayers[x].currentSoilWaterMM = (max
                        (self.listOfSoilLayers[x].wiltingWater,
                         self.listOfSoilLayers[x].currentSoilWaterMM
                        -self.listOfSoilLayers[x].layerEsoil
                        -self.listOfSoilLayers[x].perc
                        +self.listOfSoilLayers[x-1].perc))#-(self.Etrans*0.2)))
            else:
                    self.listOfSoilLayers[x].currentSoilWaterMM = (max
                        (self.listOfSoilLayers[x].wiltingWater,
                         self.listOfSoilLayers[x].currentSoilWaterMM
                        -self.listOfSoilLayers[x].layerEsoil
                        -self.listOfSoilLayers[x].perc
                        +self.listOfSoilLayers[x-1].perc))

    def annual_reset(self):
        pass
