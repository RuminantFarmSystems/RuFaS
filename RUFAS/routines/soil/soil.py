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

from math import exp, log
from . import infiltration, \
    evapotranspiration, percolation, soil_temp, soil_erosion, soil_water
from ..crop import transpiration
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

    # transpiration is defined in the crop module, but called here as a
    # component of water balance
    transpiration.update_all(crop.current_crop, soil, time)

    # calculate daily percolation
    percolation.update_all(soil)

    # updates daily soil water fluxes
    soil_water.update_all(soil, weather, time)

    # calculate daily soil erosion
    soil_erosion.update_all(soil, crop, weather, time)

    # calculate and update the contents of 3 organic and 2 inorganic nitrogen
    # pools
    nitrogen_cycling.update_all(soil, weather, time)

    phosphorus_cycling.update_all(soil, weather, time)

    annual_variable_update(soil)


def annual_variable_update(soil):

    soil.ET_max_annual += soil.ET_max

    soil.drainage_annual += soil.drainage
    soil.runoff_annual += soil.runoff
    soil.trans_annual += soil.trans_sum
    soil.evap_annual += soil.evap_sum
    soil.ET_annual += soil.ET_act

    soil.p_act_annual += soil.p_act


# -------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil
# -------------------------------------------------------------------------------
class Soil:
    """
    Contains the state of the farm's soil.
    """
    soil_layers = []

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
        for layer_name, layer_data in data['SoilLayers'].items():
            self.soil_layers.append(self.SoilLayer(layer_name, layer_data))

        # sort layers by bottom_depth
        self.soil_layers.sort(key=lambda x: x.bottom_depth)

        # determine profile depth
        self.profile_depth = self.soil_layers[-1].bottom_depth

        # calculate initial depth of each soil layer

        curr_thickness = 0
        for layer in self.soil_layers:
            layer.thickness = layer.bottom_depth - curr_thickness
            curr_thickness = layer.bottom_depth

        self.start_year = config.start_year

        self.cover = data['SoilCoverType']
        self.leach = 0.0
        self.area = data['FieldSize']

        self.num_soil_layers = 3
        self.thickness_cm = []
        self.CNT_day_layer = []

        x = 0
        for layer in self.soil_layers:
            # TODO careful of cm to mm, I had to add the / 10
            self.thickness_cm.append(layer.thickness / 10)

            # TODO org_C is an input
            # layer.org_C = layer.OM_percent * 0.58

            layer.PSP = -0.045 * log(layer.clay) + 0.001 * \
                        layer.labile_P - 0.035 * layer.org_C + 0.43
            layer.labile_P = layer.labile_P * layer.bulk_density \
                             * self.thickness_cm[x] * 0.1

            layer.active_P = layer.labile_P * (1.0 - layer.PSP) / layer.PSP

            layer.stable_P = layer.active_P * 4.0

            layer.org_P = layer.org_C / 8.0 / 14.0 * 10000 * layer.bulk_density \
                          * self.thickness_cm[x] * 0.1

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
        self.NH4 = 0.0
        self.SON = 0.0
        self.manure_mass_app = 0.0

        self.cows = []
        self.heifer = []
        self.dry_cow = []
        self.d_calf = []
        self.beef_cow = []
        self.b_calf = []

        # TODO temporary
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
        for layer in self.soil_layers:
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
        self.NH4_R_sum = 0.0
        self.WIP_L_sum = 0.0
        self.WOP_L_sum = 0.0
        self.NH4_L_sum = 0.0
        self.DP_sum = 0.0
        self.N_sum = 0.0
        self.SRP_MGL = 0.0
        self.runoff_IP = 0.0
        self.runoff_OP = 0.0
        self.runoff_NH4 = 0.0
        self.T_runoff_IP = 0.0

        self.calculate_soil_water()  # calculate soil water in layer
        self.calculateWiltingWater()  # calculate wilting water in layer
        self.calculateFcWater()  # calculate field capacity water in layer
        self.calculateSatWater()  # calculate saturation water in layer

        self.profile_SW = 0.0

        for layer in self.soil_layers:
            self.profile_SW += layer.soil_water

        self.initial_annual_SW = self.profile_SW

        # daily output values
        self.evap_max = 0.0
        self.trans_max = 0.0
        self.ET_max = 0.0

        # daily water balance
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
        self.ET_annual = 0.0

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
            z = layer.bottom_depth

            # "pseudocode_soil" S.4.A.1
            exp_part = exp(-z / 1000)
            NO3 = 7 * exp_part

            # "pseudocode_soil" S.4.A.2
            OrgC = layer.org_C
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
            BD = layer.bulk_density
            thickness = layer.thickness
            unit_adjustment = (BD * thickness) / 100

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

        def __init__(self, layer_name, layer_data):
            """
            Description:
                Populates the characteristic values of a soil layer.

            Args:
                layer_name: a string which is the name of this layer
                layer_data: a dictionary which stores the information for this layer
            """
            self.name = layer_name

            self.bottom_depth = layer_data['BottomDepth']
            self.bottom_depth_cm = layer_data['BottomDepth'] / 10
            self.wilting_point = layer_data['WiltingPoint']
            self.field_capacity = layer_data['FieldCapacity']
            self.saturation = layer_data['Saturation']
            self.soil_water_ratio = layer_data['SoilWaterRatio']

            self.thickness = 0.0  # thickness of soil layer
            self.fc_water = 0.0  # constant
            self.sat_water = 0.0  # constant
            self.wilting_water = 0.0  # constant
            self.soil_water = 0.0  # mm water in the soil profile

            self.bulk_density = layer_data['BulkDensity']

            # Variables to calculate daily evapotranspiration
            self.top_evap = 0.0  # evaporation demand at top of layer
            self.bottom_evap = 0.0  # evaporation demand at bottom of layer
            self.evap = 0.0  # evaporation demand at layer
            self.trans_act = 0.0  # actual transpiration for the layer (updated in crop)

            # Variables used for soil temperature
            self.temperature = layer_data['InitialTemperature']

            # Variables to calculate dailyPercolation
            self.ksat = layer_data['Ksat']  # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.perc = 0.0  # amount of water that percolates to next layer

            self.labile_P = layer_data['LabileP']  # labile P in soil layer
            self.clay = layer_data['Clay']  # soil clay % in soil layer

            # Variable to simulate nitrogen Cycling
            self.org_C = layer_data['OrgC%']
            self.activeMineralRate = layer_data['ActiveMineralRate']
            self.cationExclusionFraction = layer_data['CationExclusionFraction']
            self.denitrificationRate = layer_data['DenitrificationRate']
            self.NH4 = layer_data['NH4']

            self.temp_fac = 0.0
            self.water_fac = 0.0

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

            self.deNrate = layer_data['DenitrificationRate']
            self.fracActiveN = layer_data['FracActiveN']
            self.volatileExchangeFactor = layer_data['VolatileExchangeFac']

            # Variables to simulate phosphorus cycling
            self.OM_percent = layer_data['OM%']
            self.PSP = 0.0

            self.active_P = 0.0
            self.stable_P = 0.0
            self.org_P = 0.0
            self.P_uptake = 0.00

    # ---------------------------------------------------------------------------
    # Class: Fertilizer
    # An instance of this class represents a particular fertilizer and the date
    # of its application
    # ---------------------------------------------------------------------------
    class Fertilizer:
        """
        An instance of this class represents a particular fertilizer and the date
        of its application
        """

        def __init__(self, fert_data):
            """
            Args:
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
            Args:
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
            Args:
                uptake_name: a string which is the name of this particular uptake
                uptake_data: a dictionary which stores the information for this particular
                    uptake
            """
            self.name = uptake_name
            self.uptake_year = uptake_data['Year']
            self.P_uptake = uptake_data['PUptake']

    # ---------------------------------------------------------------------------
    # Function: calculate_soil_water
    # Calculates the amount of water in soil profile for a given layer at.
    # Called when soil portion of input is read.
    # ---------------------------------------------------------------------------
    def calculate_soil_water(self):
        for layer in self.soil_layers:
            layer.soil_water = layer.thickness * layer.soil_water_ratio

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
            layer.fc_water = layer.thickness * layer.field_capacity

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
            layer.sat_water = layer.thickness * layer.saturation

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
            layer.wilting_water = layer.thickness * layer.wilting_point

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
        self.ET_annual = 0.0

        self.p_act_annual = 0
        self.p_calc_annual = 0

        # initial annual soil water is set to soil water on the last day of the
        # previous year
        self.initial_annual_SW = self.profile_SW
