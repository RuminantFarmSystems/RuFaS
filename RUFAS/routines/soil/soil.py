################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: soil.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil
           William Donovan, wmdonovan@wisc.edu

This module needs the following inputs in order to operate correctly:

    These are attributes of a soil profile that need to be specified in the json input
    file. The values on the right are just examples from a soil profile with 1 layer.

        "ProfileDepth": 450,
        "ProfileBulkDensity": 1.4,
        "CN2": 85.00
        "FieldSlope": 0.02,
        "SlopeLength": 3,
        "Manning": 0.4,
        "FieldSize": 1.0,
        "PracticeFactor": 0.08,
        "Sand": 15,
        "Silt": 65,
        "SoilAlbedo": 0.16,
        "initial_residue": 0,
        "FreshNMineralRate": 0.05,
        "SoilCoverType": "BARE",

        These are attributes defined for each layer of the soil profile. Any
        number of profiles may be specified, but they all require the following
        information. The values on the right are examples.

        "SoilLayers":

            "Layer1":

                "BottomDepth": 150,
                "WiltingPoint": 0.1,
                "FieldCapacity": 0.30,
                "Saturation": 0.5,
                "Ksat": 20,
                "CationExclusionFraction": 0.0,
                "Clay": 20,
                "InitialTemperature": 15.77575,
                "BulkDensity": 1.4,
                "OrgC%": 1.2,
                "NH4": 1,
                "FracActiveN": 0.02,
                "LabileP": 15,
                "ActiveMineralRate": 0.0003,
                "VolatileExchangeFac": 0.15,
                "DenitrificationRate": 0.05,
                "SoilWaterRatio": 0.3,
                "OM%": 1.9

            "Layer2":
                ...

        Each layer needs to be specified in a similar manner

        The following are attributes of a fertilizer application. No fertilizer
        applications need be specified for the module to run, but for any that
        are specified, the following attributes are needed. Again, the values
        on the right are simply examples

        "Fertilizers":

            "Application1":

                "Year": 2008
                "JDay": 179,
                "PMass": 25.0,
                "Depth": 3.0,
                "%onSurface": 0.25

            "Application2":

                ...

        The following are attributes of a manure application. No manure
        applications need be specified for the module to run, but for any that
        are specified, the following attributes are needed. The values on the
        right should serve as examples.

        "ManureApplication":

            "Application1":

                "Type": "DAIRY",
                "Year": 2009,
                "Jday": 200
                "Mass": 1000.0,
                "TotalP": 0.025,
                "WEIP": 0.50,
                "WEOP": 0.05,
                "DryMatter": 0.05,
                "%Cover": 0.5,
                "Depth": 0.0,
                "%onSurface": 100.0

            "Application2":

                ...

        The following are attributes of a tillage operation. No tillage
        operation need be specified for the module to run, but for any operation
        that is specified, the following attributes are needed. Values on the
        right are examples.

        "TillageOperations":

            "Operation1":

                "Year": 2008,
                "Jday": 365,
                "%Incorporate": 0.5,
                "%Mixed": 0.30,
                "Depth": 15.0,

            "Operation2":

                ...

        The following are attributes of Phosphorus Uptake.
        TODO: This will likely be removed after implementing P_Cycling

        "CropPUptake":

            "Uptake1":

                "Year": 2008,
                "PUptake": 15.0

            "Uptake2":

                ...

    From the weather class, the following will be needed:
        T_min
        T_max
        radiation
        rainfall
        T_avg

    From the crop class, the following will be needed:
        crops_list

        And the following attributes of a crop type:
            bio_AG (aboveground biomass)
"""
################################################################################

import math
from . import nitrogen_cycling, phosphorus_cycling, infiltration, \
    evapotranspiration, percolation, soil_temp, soil_erosion, soil_water
from ..crop import transpiration


# ------------------------------------------------------------------------------
# Function: daily_soil_routine
# Executes all the daily soil routines
# ------------------------------------------------------------------------------
def daily_soil_routine(soil, crop, weather, time):
    """
    Description:
        Executes all the daily soil routines.

    Args:
        soil: instance of the Soil class
        crop: instance of the Crop class
        weather: instance of the Weather class
        time: instance of the Time class
    """
    # calculate and update the temperature of the soil layers
    soil_temp.update_all(soil, crop, weather, time)

    # calculate daily runoff
    infiltration.update_all(soil, weather, time)

    # calculate daily transpiration
    evapotranspiration.update_all(soil, crop, weather, time)

    # transpiration is defined in the crop module, but called here as a
    # component of water balance
    transpiration.update_all(crop.crops_list['corn'], soil, time)

    # calculate daily percolation
    percolation.update_all(soil)

    # updates daily soil water fluxes
    soil_water.update_all(soil, weather, time)

    # calculate daily soil erosion
    soil_erosion.update_all(soil, crop, weather, time)

    # calculate and update the contents of 3 organic and 2 inorganic nitrogen
    # pools
    nitrogen_cycling.update_all(soil, weather, time)


# -------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil
# -------------------------------------------------------------------------------
class Soil:
    """
    Contains the state of the farm's soil.
    """
    soil_layers = []
    fertilizerApplications = []
    manureApplications = []
    tillageOperations = []
    cropPUptakes = []  # TODO temporary?

    def __init__(self, data, config):
        """
        Description:
            Constructs an instance of the Soil class by populating its arrays
            and the necessary values.

        Args:
            data: the information from the json input file
            config: instance of the Config class
        """
        # Values Initialized by Input
        self.profileBulkDensity = data['ProfileBulkDensity']
        self.CN2 = data['CN2']  # unitless, user-defined curve number (empirical)

        # soil erosion attributes
        self.fieldSlope = data['FieldSlope']
        self.slopeLength = data['SlopeLength']
        self.manning = data['Manning']
        self.fieldSize = data['FieldSize']
        self.practiceFactor = data['PracticeFactor']
        self.sand = data['Sand']
        self.silt = data['Silt']

        # soil temperature attributes
        self.soilAlbedo = data['SoilAlbedo']
        self.Tsurf = data['SoilLayers']['Layer1']['InitialTemperature']

        # create soil layers
        for layerName, layerData in data['SoilLayers'].items():
            self.soil_layers.append(self.SoilLayer(layerName, layerData))

        # sort layers by bottomDepth
        self.soil_layers.sort(key=lambda x: x.bottomDepth)
        
        # determine profile depth
        self.profile_depth = self.soil_layers[-1].bottomDepth
        
        # calculate initial depth of each soil layer
        curr_depth = 0
        for layer in self.soil_layers:
            layer.depth = layer.bottomDepth - curr_depth
            curr_depth = layer.bottomDepth

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

        self.calculateSoilWater()  # calculate soil water in layer
        self.calculateWiltingWater()  # calculate wilting water in layer
        self.calculateFcWater()  # calculate field capacity water in layer
        self.calculateSatWater()  # calculate saturation water in layer

        self.profile_SW = 0.0

        for layer in self.soil_layers:
            self.profile_SW += layer.soil_water

        # daily output values
        self.evap_max = 0.0
        self.trans_max = 0.0
        self.ET_max = 0.0

        # daily water balance
        self.profile_SW = 0.0
        self.delta_SW = 0.0
        self.runoff = 0.0
        self.evap_sum = 0.0
        self.trans_sum = 0.0
        self.drainage = 0.0

        self.p_act = 0.0
        self.p_calc = 0.0

        self.water_balance_difference = 0.0

        # annual variables
        self.ET_max_annual = 0.0

        # annual water balance
        self.annual_delta_SW = 0.0
        self.runoff_annual = 0.0
        self.evap_annual = 0.0
        self.trans_annual = 0.0
        self.ET_annual = 0.0
        self.drainage_annual = 0.0

        self.p_act_annual = 0.0
        self.p_calc_annual = 0.0

        self.annual_water_balance_difference = 0.0

        self.infiltration = 0.0

        self.sedimentYield = 0.0

        # daily soil nitrogen values
        self.residue = data['initial_residue']
        self.freshNMineralRate = data['FreshNMineralRate']
        self.decayRate = 0.0
        self.topLayerFreshN = 0.0

        # soil phosphorus attributes
        self.soilCoverType = data['SoilCoverType']
        self.pUptake = [[0 for x in range(366)] for y in range(config.end_year + 1)]  # TODO pUptake flag
        self.lightFactor = []
        self.yieldFactor = []
        self.summan = 0.0
        self.summanP = 0.0


        self.NO3_runoff = 0.0
        self.NH4_runoff = 0.0

        self.NH4_erosion = 0.0
        self.activeN_erosion = 0.0
        self.stableN_erosion = 0.0
        self.freshN_erosion = 0.0

        # ------ INITIALIZE SOIL NITROGEN POOLS ------------------------------------
        # Calculate initial amount of NO3 in each soil layer;
        # Initial NO3 levels (kg/ha) in the soil are varied by depth as:
        # "pseudocode_soil" S.4.A
        for layer in self.soil_layers:
            z = layer.bottomDepth

            # "pseudocode_soil" S.4.A.1
            exp_part = math.exp(-z / 1000)
            NO3 = 7 * exp_part

            # "pseudocode_soil" S.4.A.2
            OrgC = layer.orgC
            OrgN = (10 ** 4) * (OrgC / 14)

            # "pseudocode_soil" S.4.A.3
            FracN = 0.02
            activeN = FracN * OrgN

            # "pseudocode_soil" S.4.A.4
            stableN = (1 - FracN) * OrgN

            # "pseudocode_soil" S.4.A.5
            res = self.residue
            FreshN = 0.0015 * res

            # "pseudocode_soil" S.4.A.6
            NH4 = layer.NH4

            # "pseudocode_soil" S.4.A.7
            BD = layer.bulkDensity
            depth = layer.depth
            unit_adjustment = (BD * depth) / 100

            layer.NO3 = NO3 * unit_adjustment
            layer.orgN = OrgN
            layer.activeN = activeN * unit_adjustment
            layer.stableN = stableN * unit_adjustment
            layer.NH4 = NH4 * unit_adjustment
            layer.topLayerFreshN = FreshN * unit_adjustment

        for layer in self.soil_layers:
            self.profile_SW += layer.soil_water

        self.initial_annual_SW = self.profile_SW

    # ---------------------------------------------------------------------------
    # Class: SoilLayer
    # An instance of this class represents a layer in the soil
    # ---------------------------------------------------------------------------
    class SoilLayer:
        """
        An instance of this class represents a layer in the soil.
        """

        def __init__(self, layerName, layerData):
            """
            Description:
                Populates the characteristic values of a soil layer.

            Args:
                layerName: a string which is the name of this layer
                layerData: a dictionary which stores the information for this layer
            """
            self.name = layerName

            self.bottomDepth = layerData['BottomDepth']
            self.soilWaterRatio = layerData['SoilWaterRatio']
            self.wiltingPoint = layerData['WiltingPoint']
            self.fieldCapacity = layerData['FieldCapacity']
            self.saturation = layerData['Saturation']

            self.soil_water = 0.0  # mm water in the soil profile
            self.depth = 0.0  # depth of soil layer
            self.fcWater = 0.0  # calculated constant
            self.satWater = 0.0  # calculated constant
            self.wiltingWater = 0.0  # calculated constant

            self.bulkDensity = layerData['BulkDensity']

            # Variables to calculate daily evapotranspiration
            self.top_evap = 0.0  # evaporation demand at top of layer
            self.bottom_evap = 0.0  # evaporation demand at bottom of layer
            self.evap = 0.0  # evaporation demand at layer
            self.trans_act = 0.0  # actual transpiration for the layer (updated in crop)

            # Variables used for soil temperature
            self.temperature = layerData['InitialTemperature']

            # Variables to calculate dailyPercolation
            self.ksat = layerData['Ksat']  # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.perc = 0.0  # amount of water that percolates to next layer

            self.labileP = layerData['LabileP']  # labile P in soil layer
            self.clay = layerData['Clay']  # soil clay % in soil layer

            # Variable to simulate nitrogen Cycling
            self.orgC = layerData['OrgC%']
            self.activeMineralRate = layerData['ActiveMineralRate']
            self.cationExclusionFraction = layerData['CationExclusionFraction']
            self.denitrificationRate = layerData['DenitrificationRate']
            self.NH4 = layerData['NH4']

            self.tempFac = 0.0
            self.waterFac = 0.0

            # Initial NO3 levels (kg/ha) in the soil layer:
            self.NO3 = 0.0

            # Organic N (Active + Stable, mg/kg):
            self.orgN = 0.0

            # Initial Active N in layer:
            self.activeN = 0.0

            # Initial Stable N in layer:
            self.stableN = 0.

            self.NO3_perc = 0.0
            self.NH4_perc = 0.0
            self.active_perc = 0.0
            self.nMinAct = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.nTrans = 0.0
            self.totNitriVolatil = 0.0

            self.deNrate = layerData['DenitrificationRate']
            self.fracActiveN = layerData['FracActiveN']
            self.volatileExchangeFactor = layerData['VolatileExchangeFac']

            # Variables to simulate phosphorus cycling
            self.OMpercent = layerData['OM%']
            self.soilOC = 0.0
            self.psp = 0.0

            self.activeP = 0.0
            self.stableP = 0.0
            self.orgP = 0.0

    # ---------------------------------------------------------------------------
    # Class: Fertilizer
    # An instance of this class represents a particular fertilizer and the date
    # of its application
    # ---------------------------------------------------------------------------
    class Fertilizer:
        """
        Description:
            An instance of this class represents a particular fertilizer and the date
        of its application.
        """

        def __init__(self, FertName, FertData):
            """
            Constructs an instance of this class by setting the values of its necessary
            fields.

            Args:
                FertName: a string which is the name of this fertilizer
                FertData: a dictionary which holds the rest of the information about
                    this fertilizer
            """
            self.name = FertName
            self.appYear = FertData['Year']
            self.appDay = FertData['JDay']
            self.fertPMass = FertData['PMass']
            self.depth = FertData['Depth']
            self.percentOnSurface = FertData['%onSurface']

    # ---------------------------------------------------------------------------
    # Class: Manure
    # An instance of this class represents a particular manure and the date
    # of its application
    # ---------------------------------------------------------------------------
    class Manure:
        """
        An instance of this class represents a particular manure and the date
        of its application
        """

        def __init__(self, manureName, manureData):
            """
            Description:
                Constructs an instance of this class

            Args:
                manureName: a string which represents the name is this manure
                manureData: a dictionary which stores the information for this manure
            """
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

    # ---------------------------------------------------------------------------
    # Class: Tillage
    # An instance of this class represents a particular tillage and the date
    # of its application
    # ---------------------------------------------------------------------------
    class Tillage:
        """
        An instance of this class represents a particular tillage and the date
        of its application
        """

        def __init__(self, tillageName, tillageData):
            """
            Description:
                Constructs an instance of this class.

            Args:
                tillageName: a string which is the name of this tillage
                tillageData: a dictionary which stores the information for this tillage
            """
            self.name = tillageName
            self.appYear = tillageData['Year']
            self.appDay = tillageData['Jday']
            self.percentIncorporate = tillageData['%Incorporate']
            self.percentMixed = tillageData['%Mixed']
            self.depth = tillageData['Depth']

    # ---------------------------------------------------------------------------
    # Class: CropPUptake
    # An instance of this class represents a particular uptake and the date
    # of uptake
    # ---------------------------------------------------------------------------
    class CropPUptake:
        """
        An instance of this class represents a particular uptake and the date
        of uptake
        """

        def __init__(self, uptakeName, uptakeData):
            """
            Description:
                Constructs an instance of this class.

            Args:
                uptakeName: a string which is the name of this particular uptake
                uptakeData: a dictionary which stores the information for this particular
                    uptake
            """
            self.name = uptakeName
            self.uptakeYear = uptakeData['Year']
            self.pUptake = uptakeData['PUptake']

    # ---------------------------------------------------------------------------
    # Function: calculateSoilWater
    # Calculates the initial amount of water in soil profile for a given layer.
    # Called when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def calculateSoilWater(self):
        for layer in self.soil_layers:
            layer.soil_water = layer.depth * layer.soilWaterRatio

    # ---------------------------------------------------------------------------
    # Function: calculateFcWater
    # Calculates the amount of water in soil profile for a given layer at
    # field capacity (mm H2O). Called when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def calculateFcWater(self):
        """
        Description:
            Calculates the amount of water in soil profile for a given layer at
            field capacity (mm H2O). Called when soil portion of input is read.
        """
        for layer in self.soil_layers:
            layer.fcWater = layer.depth * layer.fieldCapacity

    # ---------------------------------------------------------------------------
    # Function: calculateSatWater
    # Calculates the amount of water in soil profile for a given layer at
    # saturation (mm H2O). Called when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def calculateSatWater(self):
        """
        Description:
            Calculates the amount of water in soil profile for a given layer at
            saturation (mm H2O). Called when soil portion of input is read.
        """
        for layer in self.soil_layers:
            layer.satWater = layer.depth * layer.saturation

    # ---------------------------------------------------------------------------
    # Function: calculateWiltingWater
    # Calculates the amount of water in soil profile for a given layer at
    # wilting point (mm H2O). Called when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def calculateWiltingWater(self):
        """
        Description:
            Calculates the amount of water in soil profile for a given layer at
            wilting point (mm H2O). Called when soil portion of input is read.
        """
        for layer in self.soil_layers:
            layer.wiltingWater = layer.depth * layer.wiltingPoint

    def calculate_annual_water_balance(self):
        """
        Description:
            Calculates annual water balance
        """
        self.annual_delta_SW = self.profile_SW - self.initial_annual_SW

        self.p_calc_annual = self.annual_delta_SW \
            + self.runoff_annual + self.evap_annual + self.trans_annual \
            + self.drainage_annual

        self.annual_water_balance_difference = self.p_act_annual - self.p_calc_annual

    def annual_reset(self):
        """
        Description:
            Resets the annual values for the next year.
        """

        self.ET_max_annual = 0.0
        self.evap_annual = 0.0
        self.trans_annual = 0.0
        self.ET_annual = 0.0
        self.drainage_annual = 0.0
        self.runoff_annual = 0.0

        self.p_act_annual = 0
        self.p_calc_annual = 0

        # initial annual soil water is set to soil water on the last day of the
        # previous year
        self.initial_annual_SW = self.profile_SW
