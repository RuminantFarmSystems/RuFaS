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
        "Orgc": 1.2,
        "Sand": 15,
        "Silt": 65,
        "SoilAlbedo": 0.16,
        "residue": 0,
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
                "StartingSoilWater": 45,
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
            bioAG (aboveground biomass)
"""
################################################################################

from math import exp, log
from . import infiltration, \
    evapotranspiration, percolation, soil_temp, soil_erosion, soil_water
from .nitrogen_cycling import nitrogen_cycling
from .phosphorus_cycling import phosphorus_cycling


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

    # calculate daily percolation
    percolation.update_all(soil)

    # calculate daily soil erosion
    soil_erosion.update_all(soil, crop, weather, time)

    soil_water.update_all(soil, weather, time)

    # calculate and update the contents of 3 organic and 2 inorganic nitrogen
    # pools
    nitrogen_cycling.update_all(soil, weather, time)

    phosphorus_cycling.update_all(soil, weather, time)


# -------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil
# -------------------------------------------------------------------------------
class Soil:
    """
    Contains the state of the farm's soil.
    """
    listOfSoilLayers = []
    fertilizerApplications = []
    tillageOperations = []
    cropPUptakes = []

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
        self.manure = Soil.Manure(data['ManureApplication'])
        self.fertilizer = Soil.Fertilizer(data['FertilizerApplication'])
        self.tillage = Soil.Tillage(data['TillageApplication'])

        self.profileDepth = data['ProfileDepth']
        self.profileBulkDensity = data['ProfileBulkDensity']
        self.CN2 = data['CN2']  # unitless, user-defined curve number (empirical)

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
        curr_depth = 0
        for layer in self.listOfSoilLayers:
            layer.depth = layer.bottomDepth - curr_depth
            curr_depth = layer.bottomDepth

        # # get fertilizer application information
        # for fertApp, fertData in data['Fertilizers'].items():
        #     self.fertilizerApplications.append(self.Fertilizer(fertApp, fertData))
        #
        # # get tillage application information
        # for tillageApp, tillageData in data['TillageOperations'].items():
        #     self.tillageOperations.append(self.Tillage(tillageApp, tillageData))

        # # get crop phosphorus uptake  information
        # for uptakePApp, uptakePData in data['CropPUptake'].items():
        #     self.cropPUptakes.append(self.CropPUptake(uptakePApp, uptakePData))

        # TODO SurPhos
        # soil_data = data['soil']

        self.start_year = config.start_year

        self.cover = data['SoilCoverType']
        self.leach = 0.0
        self.area = data['FieldSize']

        self.soil_layers = 3
        self.thick_layer = []  # TODO I think this is already created as depth something
        self.CNT_day_layer = []

        x = 0
        for layer in self.listOfSoilLayers:

            # TODO careful of cm to mm, I had to add the / 10

            self.thick_layer.append(layer.depth / 10)

            # TODO orgC is an input
            # layer.orgC = layer.OM_percent * 0.58

            layer.PSP = -0.045 * log(layer.clay) + 0.001 * \
                        layer.labile_P - 0.035 * layer.orgC + 0.43
            layer.labile_P = layer.labile_P * layer.bulkDensity \
                             * self.thick_layer[x] * 0.1

            layer.active_P = layer.labile_P * (1.0 - layer.PSP) / layer.PSP

            layer.stable_P = layer.active_P * 4.0

            layer.org_P = layer.orgC / 8.0 / 14.0 * 10000 * layer.bulkDensity \
                          * self.thick_layer[x] * 0.1

            self.CNT_day_layer.append(0.0)

            x += 1

        # default values
        self.days = [0, 0, 0]
        self.moisture = 0.5
        self.CNT = 1
        self.manure_cov = 0.0
        self.manure_mass = 0.0
        self.cover_SLP = 0.000025
        self.count_day = [0, 0, 0]

        # fertilizer
        self.fert_applied_sum = 0.0
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_P_available = 0.0  # avfrtp
        self.fert_P_released = 0.0  # rsfrtp
        self.fact = 0.0

        # manure
        self.manure_type = 0
        self.manure_sum = 0
        self.manure_P_sum = 0
        self.manure_N_sum = 0
        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0
        self.manure_NH4 = 0.0
        self.manure_SON = 0.0
        self.manure_mass_app = 0.0

        self.cows = []
        self.heifer = []
        self.dry_cow = []
        self.d_calf = []
        self.beef_cow = []
        self.b_calf = []

        # TODO temp
        for x in range(0, 50):
            self.cows.append([0 for _ in range(0, 366)])
            self.heifer.append([0 for _ in range(0, 366)])
            self.dry_cow.append([0 for _ in range(0, 366)])
            self.d_calf.append([0 for _ in range(0, 366)])
            self.beef_cow.append([0 for _ in range(0, 366)])
            self.b_calf.append([0 for _ in range(0, 366)])

        # plow

        # solp
        self.soil_P = [0, 0, 0]
        self.SRP_sum = 0.0
        self.slope = [0, 0, 0]
        self.inter = [0, 0, 0]
        self.DRP = [0, 0, 0]
        self.water = [0, 0, 0]

        # fert_leach
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_leach = 0.0
        self.PD_factor = 0.0
        self.fert_runoff_P = 0.0
        self.fert_R_sum = 0.0
        self.fert_L_sum = 0.0
        self.fert_run = 0.0

        # p_mineralization
        self.count_it = [0, 0, 0]
        self.counts = [0, 0, 0]
        self.soil_yp = []  # soilyp
        for x in range(0, 3):
            self.soil_yp.append([0 for _ in range(0, 366)])
        self.PSP_avg = []
        for layer in self.listOfSoilLayers:
            self.PSP_avg.append(layer.PSP)
        self.pbal = [0, 0, 0]
        self.old_pbal = [0, 0, 0]
        self.lab_P_sum = [0, 0, 0]
        self.lab_P_avg = [0, 0, 0]
        self.varA = [0, 0, 0]
        self.varB = [0, 0, 0]
        self.base = [0, 0, 0]
        self.pflow = [0, 0, 0]
        self.pd_srb_fac = [0, 0, 0]
        self.pflow_r = [0, 0, 0]
        self.PSP_fac = [0, 0, 0]
        self.pflow2 = [0, 0, 0]
        self.temp_lab = [0, 0, 0]

        # manure_leach
        self.TIP_leach = 0.0
        self.TOP_leach = 0.0
        self.TN_leach = 0.0
        self.ND_factor = 0.0
        self.WIP_R_sum = 0.0
        self.WOP_R_sum = 0.0
        self.NH_R_sum = 0.0
        self.WIP_L_sum = 0.0
        self.WOP_L_sum = 0.0
        self.NH_L_sum = 0.0
        self.DP_sum = 0.0
        self.N_sum = 0.0
        self.SRP_MGL = 0.0
        self.runoff_IP = 0.0
        self.runoff_OP = 0.0
        self.runoff_NH = 0.0
        self.T_runoff_IP = 0.0
        # TODO

        self.convertCurrentSoilWaterToMM()  # calculate initial soil water in layer
        self.calculateWiltingWater()  # calculate wilting water in layer
        self.calculateFcWater()  # calculate field capacity water in layer
        self.calculateSatWater()  # calculate saturation water in layer

        # daily output values
        self.runoff = 0.0
        self.Et_max = 0.0
        self.E0 = 0.0
        self.E0_sum = 0.0
        self.Ea_sum = 0.0
        self.Esoil = 0.0
        self.dailyInfiltration = 0.0

        self.sedimentYield = 0.0

        # daily soil nitrogen values
        self.residue = data['initial_residue']
        self.freshNMineralRate = data['FreshNMineralRate']
        self.decayRate = 0.0
        self.topLayerFreshN = 0.0

        # TODO
        # soil phosphorus attributes
        # self.soilCoverType = data['SoilCoverType']
        # self.pUptake = [[0 for x in range(366)] for y in range(config.end_year + 1)]
        self.lightFactor = []
        self.yieldFactor = []
        self.summan = 0.0
        self.summanP = 0.0

        # ------ INITIALIZE SOIL NITROGEN POOLS ------------------------------------
        # Calculate initial amount of NO3 in each soil layer;
        # Initial NO3 levels (kg/ha) in the soil are varied by depth as:
        # "pseudocode_soil" S.4.A
        for layer in self.listOfSoilLayers:
            z = layer.bottomDepth

            # "pseudocode_soil" S.4.A.1
            exp_part = exp(-z / 1000)
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
            self.bottom_depth_cm = layerData['BottomDepth'] / 10
            self.wiltingPoint = layerData['WiltingPoint']
            self.fieldCapacity = layerData['FieldCapacity']
            self.saturation = layerData['Saturation']
            # self.currentSoilWater = layerData['StartingSoilWater']

            self.depth = 0.0  # depth of soil layer
            self.fcWater = 0.0  # constant
            self.satWater = 0.0  # constant
            self.wiltingWater = 0.0  # constant

            self.currentSoilWaterMM = 0.0  # soil water in layer in mm
            self.bulkDensity = layerData['BulkDensity']

            # Variables to calculate daily evapotranspiration
            self.topEsoil = 0.0  # evaporation demand at top of layer
            self.bottomEsoil = 0.0  # evaporation demand at bottom of layer
            self.layerEsoil = 0.0  # evaporation demand at layer
            self.Et_actual = 0.0  # actual transpiration for the layer (updated in crop)

            # Variables used for soil temperature
            self.temperature = layerData['InitialTemperature']

            # Variables to calculate dailyPercolation
            self.ksat = layerData['Ksat']  # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.perc = 0.0  # amount of water that percolates to next layer

            self.labile_P = layerData['LabileP']  # labile P in soil layer
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

            self.NO3Perc = 0.0
            self.NH4Perc = 0.0
            self.activePerc = 0.0
            self.nMinAct = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.nTrans = 0.0
            self.totNitriVolatil = 0.0

            self.fracActiveN = layerData['FracActiveN']
            self.volatileExchangeFactor = layerData['VolatileExchangeFac']

            # Variables to simulate phosphorus cycling
            self.OM_percent = layerData['OM%']
            self.soilOC = 0.0
            self.PSP = 0.0

            self.active_P = 0.0
            self.stable_P = 0.0
            self.org_P = 0.0
            self.p_uptake = 0.00

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

        def __init__(self, fert_data):
            """
            Constructs an instance of this class by setting the values of its necessary
            fields.

            Args:
                FertName: a string which is the name of this fertilizer
                fert_data: a dictionary which holds the rest of the information about
                    this fertilizer
            """
            self.year = fert_data['year']
            self.day = fert_data['day']
            self.mass = fert_data['mass']
            self.depth = [x / 10 for x in fert_data['depth']]
            self.surface_percent = fert_data['surf_perc']

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

        def __init__(self, manure_data):
            """
            Description:
                Constructs an instance of this class

            Args:
                manure_data: a dictionary which stores the information for this manure
            """
            self.type = manure_data['type']
            self.year = manure_data['year']
            self.day = manure_data['day']
            self.mass = manure_data['mass']
            self.P_frac = manure_data['P_frac']
            self.N_frac = manure_data['N_frac']
            self.NH4_frac = manure_data['NH4_frac']
            self.WIP_frac = manure_data['WIP_frac']
            self.WOP_frac = manure_data['WOP_frac']

            # TODO: N_frac and total_NH4_frac only exist in some SurPhos
            # TODO: data sets and are set to 0.

            self.dry_matter = manure_data['dry_matter']
            self.percent_cover = manure_data['percent_cover']
            self.depth = [x / 10 for x in manure_data['depth']]
            self.surface_percent = manure_data['surf_perc']

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

        def __init__(self, tillage_data):
            """
            Description:
                Constructs an instance of this class.

            Args:
                tillageName: a string which is the name of this tillage
                tillage_data: a dictionary which stores the information for this tillage
            """
            self.year = tillage_data['year']
            self.day = tillage_data['day']
            self.percent_incorporated = tillage_data['perc_incorporated']
            self.percent_mixed = tillage_data['perc_mixed']
            self.depth = [x / 10 for x in tillage_data['depth']]

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

        def __init__(self, uptake_name, uptake_data):
            """
            Description:
                Constructs an instance of this class.

            Args:
                uptake_name: a string which is the name of this particular uptake
                uptake_data: a dictionary which stores the information for this particular
                    uptake
            """
            self.name = uptake_name
            self.uptakeYear = uptake_data['Year']
            self.pUptake = uptake_data['PUptake']

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
        for layer in self.listOfSoilLayers:
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
        for layer in self.listOfSoilLayers:
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
        for layer in self.listOfSoilLayers:
            layer.wiltingWater = layer.depth * layer.wiltingPoint

    # ---------------------------------------------------------------------------
    # Function: convertCurrentSoilWaterToMM
    # Calculates the amount of soil water in a given layer in millimeters.
    # Called once when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def convertCurrentSoilWaterToMM(self):
        """
        Description:
            Calculates the amount of soil water in a given layer in millimeters.
            Called once when soil portion of input is read.
        """
        for layer in self.listOfSoilLayers:
            layer.currentSoilWaterMM = layer.depth * layer.fieldCapacity

    def annual_reset(self):
        """
        Description:
            Resets the E0 sum for the next year.
        """
        self.E0_sum = 0.0
