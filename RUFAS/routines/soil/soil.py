################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: soil.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu

This module needs the following input in order to operate correctly:

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
        "fresh_NMineralRate": 0.05,
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
                "org_C%": 1.2,
                "NH4": 1,
                "active_N_frac": 0.02,
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
    nitrogen_cycling.update_all(soil)

    phosphorus_cycling.update_all(soil, weather, time)

    soil.annual_variable_update()

    soil.manure_app_annual += soil.manure_app
    soil.manure_P_annual += soil.manure_P


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
            layer.thickness_cm = layer.thickness / 10
            curr_thickness = layer.bottom_depth

        self.start_year = config.start_year

        self.cover = data['SoilCoverType']
        if self.cover == "GRASSED":
            self.cover_factor = 0.8
        elif self.cover == "RESIDUE COVER":
            self.cover_factor = 0.667
        else:
            self.cover_factor = 0.5333

        self.leach = 0.0
        self.area = data['FieldSize']

        # Initialize phosphorus variables
        # "pseudocode_soil" S.6.A

        self.labile_P = 0.0
        self.active_P = 0.0
        self.stable_P = 0.0
        self.org_P = 0.0
        self.soil_P = 0.0

        for layer in self.soil_layers:

            # S.6.A.1
            layer.PSP_max = -0.045 * log(layer.clay) + 0.001 * \
                            layer.labile_P - 0.035 * layer.org_C + 0.43
            layer.PSP_act = max(0.05, min(0.7, layer.PSP_max))
            layer.PSP_avg = layer.PSP_act

            # S.6.A.2
            layer.labile_P = layer.labile_P * layer.bulk_density \
                             * layer.thickness_cm * 0.1
            self.labile_P += layer.labile_P

            # S.6.A.3
            layer.active_P = layer.labile_P * (1.0 - layer.PSP_act) / layer.PSP_act
            self.active_P += layer.active_P

            # S.6.A.4
            layer.stable_P = layer.active_P * 4.0
            self.stable_P += layer.stable_P

            # S.6.A.5 TODO organic soil pools (labile_O, and active_O) are not being tracked
            layer.org_P = layer.org_C / 8.0 / 14.0 * 10000 * layer.bulk_density \
                          * layer.thickness_cm * 0.1
            self.org_P += layer.org_P

            # S.6.A.6
            layer.mass = layer.bulk_density * layer.thickness_cm * 10000

        self.manure_moisture = 0.5
        self.CNT = 1
        self.manure_cov = 0.0
        self.manure_mass = 0.0
        self.cover_SLP = 0.000025

        # fertilizer
        self.fert_applied_sum = 0.0
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_P_available = 0.0  # avfrtp
        self.fert_P_released = 0.0  # rsfrtp
        self.depth_fact = 0.0

        # manure
        self.manure_app = 0.0

        self.manure_type = 0
        self.manure_app_annual = 0

        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0

        self.manure_mass_app = 0.0

        # soluble_p
        self.DRP_leached = 0.0
        self.M_DRP_runoff = 0.0

        self.DRP_runoff_annual = 0.0
        self.DRP_leachate_annual = 0.0

        # fert_leach
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_leach = 0.0
        self.PD_factor = 0.0
        self.fert_runoff_P = 0.0
        self.fert_runoff_annual = 0.0
        self.fert_leachate_annual = 0.0
        self.fert_run = 0.0

        # manure_leach
        self.MIP_leach = 0.0
        self.MOP_leach = 0.0
        self.MIP_runoff = 0.0
        self.MOP_runoff = 0.0
        self.MIP_leach_annual = 0.0
        self.MOP_leach_annual = 0.0
        self.M_leach = 0.0
        self.DP = 0.0
        self.N_sum = 0.0
        self.TIP_runoff = 0.0

        self.TIP_runoff_annual = 0.0
        self.M_DRP_runoff_annual = 0.0

        self.WIP_runoff_annual = 0.0
        self.WOP_runoff_annual = 0.0

        self.WIP_leachate_annual = 0.0
        self.WOP_leachate_annual = 0.0

        self.calculate_soil_water()  # calculate soil water in layer
        self.calculateWiltingWater()  # calculate wilting water in layer
        self.calculateFcWater()  # calculate field capacity water in layer
        self.calculateSatWater()  # calculate saturation water in layer

        # daily output values
        self.evap_max = 0.0
        self.trans_max = 0.0
        self.ET_max = 0.0
        self.ET_act = 0.0

        # daily water balance
        self.profile_SW = 0.0

        for layer in self.soil_layers:
            self.profile_SW += layer.soil_water

        self.initial_profile_SW = self.profile_SW

        self.p_act = 0.0
        self.p_calc = 0.0
        self.water_balance_difference = 0.0
        self.delta_SW = 0.0

        self.runoff = 0.0
        self.evap_sum = 0.0
        self.trans_sum = 0.0
        self.drainage = 0.0

        # annual variables
        self.ET_max_annual = 0.0
        self.ET_annual = 0.0

        # annual water balance
        self.p_act_annual = 0.0
        self.p_calc_annual = 0.0
        self.water_balance_difference_annual = 0.0
        self.delta_SW_annual = 0.0

        self.runoff_annual = 0.0
        self.evap_annual = 0.0
        self.trans_annual = 0.0
        self.ET_annual = 0.0
        self.drainage_annual = 0.0

        self.infiltration = 0.0

        self.sed = 0.0
        self.sed_P = 0.0
        self.sed_P_conc = 0.0
        self.enrichment_P = 0.0
        self.runoff_conc = 0.0

        # daily soil nitrogen values
        self.residue = data['initial_residue']
        self.fresh_NMineralRate = data['fresh_NMineralRate']
        self.decayRate = 0.0

        # soil phosphorus attributes
        self.lightFactor = []
        self.yieldFactor = []
        self.summan = 0.0
        self.summanP = 0.0

        self.NO3_runoff = 0.0
        self.NH4_runoff = 0.0

        self.NO3_drainage = 0.0
        self.NH4_drainage = 0.0
        self.active_N_drainage = 0.0

        self.NH4_erosion = 0.0
        self.active_N_erosion = 0.0
        self.stable_N_erosion = 0.0
        self.fresh_N_erosion = 0.0

        self.NO3_runoff_annual = 0.0
        self.NH4_runoff_annual = 0.0

        self.NH4_erosion_annual = 0.0
        self.active_N_erosion_annual = 0.0
        self.stable_N_erosion_annual = 0.0
        self.fresh_N_erosion_annual = 0.0

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

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
            org_C = layer.org_C
            org_N = (10 ** 4) * (org_C / 14)

            # "pseudocode_soil" S.4.A.3
            FracN = 0.02
            active_N = FracN * org_N

            # "pseudocode_soil" S.4.A.4
            stable_N = (1 - FracN) * org_N

            # "pseudocode_soil" S.4.A.5
            res = self.residue
            fresh_N = 0.0015 * res

            # "pseudocode_soil" S.4.A.6
            NH4 = layer.NH4

            # "pseudocode_soil" S.4.A.7
            BD = layer.bulk_density
            thickness = layer.thickness
            unit_adjustment = (BD * thickness) / 100

            layer.NO3 = NO3 * unit_adjustment
            layer.org_N = org_N
            layer.active_N = active_N * unit_adjustment
            layer.stable_N = stable_N * unit_adjustment
            layer.NH4 = NH4 * unit_adjustment
            self.fresh_N = fresh_N * unit_adjustment
        # daily nitrogen balance
        self.fresh_N = 0.0

        self.profile_N = 0.0
        for layer in self.soil_layers:
            self.profile_N += layer.NO3 + layer.NH4 + \
                              layer.org_N + layer.active_N + layer.stable_N

        self.profile_N += self.fresh_N
        self.initial_profile_N = self.profile_N

        self.manure_N = 0.0
        self.N_calc = 0.0
        self.N_balance_difference = 0.0
        self.delta_N = 0.0

        self.N_drainage = 0.0
        self.N_runoff = 0.0
        self.N_erosion = 0.0
        self.N_uptake = 0.0

        # annual nitrogen balance
        self.manure_N_annual = 0.0
        self.N_calc_annual = 0.0
        self.N_balance_difference_annual = 0.0
        self.delta_N_annual = 0.0

        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0
        self.N_uptake_annual = 0.0

        # daily phosphorus balance
        self.profile_P = 0.0
        for layer in self.soil_layers:
            self.profile_P += layer.labile_P + layer.active_P + \
                              layer.stable_P + layer.org_P

        self.initial_profile_P = self.profile_P

        self.manure_P = 0.0
        self.P_calc = 0.0
        self.P_balance_difference = 0.0
        self.delta_P = 0.0

        self.P_drainage = 0.0
        self.P_runoff = 0.0
        self.P_erosion = 0.0
        self.P_uptake = 0.0

        # annual phosphorus balance
        self.manure_P_annual = 0.0
        self.P_calc_annual = 0.0
        self.P_balance_difference_annual = 0.0
        self.delta_P_annual = 0.0

        self.P_drainage_annual = 0.0
        self.P_runoff_annual = 0.0
        self.P_erosion_annual = 0.0
        self.P_uptake_annual = 0.0

    def annual_variable_update(self):

        self.ET_max_annual += self.ET_max

        self.drainage_annual += self.drainage
        self.runoff_annual += self.runoff
        self.trans_annual += self.trans_sum
        self.evap_annual += self.evap_sum
        self.ET_annual += self.ET_act

        self.p_act_annual += self.p_act

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
            self.bottom_depth_cm = self.bottom_depth / 10
            self.wilting_point = layer_data['WiltingPoint']
            self.field_capacity = layer_data['FieldCapacity']
            self.saturation = layer_data['Saturation']
            self.soil_water_ratio = layer_data['SoilWaterRatio']

            self.thickness = 0.0  # thickness of soil layer
            self.thickness_cm = 0.0

            self.fc_water = 0.0  # constant
            self.sat_water = 0.0  # constant
            self.wilting_water = 0.0  # constant
            self.soil_water = 0.0  # mm water in the soil profile

            self.bulk_density = layer_data['BulkDensity']
            self.mass = 0

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

            self.clay = layer_data['Clay']  # soil clay % in soil layer

            # Variable to simulate nitrogen Cycling
            self.org_C = layer_data['org_C%']
            self.activeMineralRate = layer_data['ActiveMineralRate']
            self.cationExclusionFraction = layer_data['CationExclusionFraction']
            self.denitrificationRate = layer_data['DenitrificationRate']
            self.NH4 = layer_data['NH4']

            self.temp_fac = 0.0
            self.water_fac = 0.0

            # Initial NO3 levels (kg/ha) in the soil layer:
            self.NO3 = 0.0

            # Organic N (Active + Stable, mg/kg):
            self.org_N = 0.0

            # Initial Active N in layer:
            self.active_N = 0.0

            # Initial Stable N in layer:
            self.stable_N = 0.0

            self.NO3_perc = 0.0
            self.NH4_perc = 0.0
            self.active_N_perc = 0.0
            self.nMinAct = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.nTrans = 0.0
            self.totNitriVolatil = 0.0

            self.deNrate = layer_data['DenitrificationRate']
            self.active_N_frac = layer_data['active_N_frac']
            self.volatileExchangeFactor = layer_data['VolatileExchangeFac']

            # Variables to simulate phosphorus cycling
            self.OM_percent = layer_data['OM%']

            # P in the soil layer
            self.soil_P = 0.0

            self.iso_slope = 0.0  # the slope of the isotherm curve
            self.iso_inter = 0.0  # the intercept of the isotherm curve

            self.DRP_leachate = 0.0
            self.DRP_leachate_act = 0.0
            self.DRP_runoff = 0.0

            self.labile_P = layer_data['LabileP']  # labile P in soil layer
            self.active_P = 0.0
            self.stable_P = 0.0
            self.org_P = 0.0
            self.P_uptake = 0.00

            self.labile_P_uptake = 0.0
            self.labile_P_sum = 0.0
            self.PSP_max = 0.0
            self.PSP_act = 0.0
            self.PSP_avg = 0.0

            self.pbal = 0.0
            self.days_unbalanced_labile = 0.0
            self.days_unbalanced_active = 0.0

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
            self.DM = manure_data['dry_matter']
            self.cover_perc = manure_data['cover_perc']
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

    def annual_mass_balance(self):
        """
        Description:
            Calculates annual water balance
        """
        self.annual_water_balance()
        self.annual_phosphorus_balance()
        self.annual_nitrogen_balance()

    def annual_water_balance(self):
        self.delta_SW_annual = self.profile_SW - self.initial_profile_SW

        self.p_calc_annual = self.delta_SW_annual \
            + self.runoff_annual + self.evap_annual + self.trans_annual \
            + self.drainage_annual

        self.water_balance_difference_annual = self.p_act_annual - self.p_calc_annual

    def annual_phosphorus_balance(self):
        self.delta_P_annual = self.profile_P - self.initial_profile_P

        self.P_calc_annual = self.delta_P_annual + \
                             self.P_runoff_annual + self.P_drainage_annual + \
                             self.P_erosion_annual + self.P_uptake_annual

        self.P_balance_difference_annual = self.manure_P_annual - self.P_calc_annual

    def annual_nitrogen_balance(self):
        self.delta_N_annual = self.profile_N - self.initial_profile_N

        self.N_calc_annual = self.delta_N_annual + \
                             self.N_runoff_annual + self.N_drainage_annual + \
                             self.N_erosion_annual + self.N_uptake_annual

        self.N_balance_difference_annual = self.manure_N_annual - self.N_calc_annual

    def annual_reset(self):
        """
        Description:
            Resets the annual values for the next year.
        """

        # annual mass balance reset
        self.initial_profile_SW = self.profile_SW

        self.p_act_annual = 0
        self.p_calc_annual = 0
        self.drainage_annual = 0.0
        self.runoff_annual = 0.0
        self.evap_annual = 0.0
        self.trans_annual = 0.0

        self.initial_profile_N = self.profile_N

        self.manure_N_annual = 0.0
        self.N_calc_annual = 0.0
        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0

        self.initial_profile_P = self.profile_P

        self.manure_app_annual = 0.0

        self.manure_P_annual = 0.0
        self.P_calc_annual = 0.0
        self.P_drainage_annual = 0.0
        self.P_runoff_annual = 0.0
        self.P_erosion_annual = 0.0

        self.ET_max_annual = 0.0
        self.ET_annual = 0.0

        self.ET_annual = 0.0

        self.NO3_runoff_annual = 0.0
        self.NH4_runoff_annual = 0.0

        self.NH4_erosion_annual = 0.0
        self.active_N_erosion_annual = 0.0
        self.stable_N_erosion_annual = 0.0
        self.fresh_N_erosion_annual = 0.0

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

        self.DRP_runoff_annual = 0.0
        self.DRP_leachate_annual = 0.0

        self.WIP_runoff_annual = 0.0
        self.WOP_runoff_annual = 0.0

        self.WIP_leachate_annual = 0.0
        self.WOP_leachate_annual = 0.0

        self.MIP_leach_annual = 0.0
        self.MOP_leach_annual = 0.0

        self.TIP_runoff_annual = 0.0
        self.M_DRP_runoff_annual = 0.0
