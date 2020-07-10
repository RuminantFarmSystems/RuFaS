"""
RUFAS: Ruminant Farm Systems Model
File name: soil.py

Description: Driver for the soil sub-module

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
"""

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

    annual_variable_update(soil)


def annual_variable_update(soil):
    soil.manure_applied_annual += soil.manure_applied
    soil.fert_applied_annual += soil.fert_applied
    soil_water.update_annual_SW(soil)
    phosphorus_cycling.update_annual_P(soil)
    nitrogen_cycling.update_annual_N(soil)


# -------------------------------------------------------------------------------
# Class: Soil
#        Contains the state of the farm's soil
# -------------------------------------------------------------------------------
class Soil:
    """
    Contains the state of the farm's soil.
    """
    soil_layers = []

    def __init__(self, data):
        """
        Description:
            Constructs an instance of the Soil class by populating its arrays
            and the necessary values.

        Args:
            data: the information from the json input file
        """
        # Values Initialized by Input
        self.CN2 = data['CN2']  # unitless, user-defined curve number (empirical)

        # soil erosion attributes
        self.profile_bulk_density = data['ProfileBulkDensity']
        self.field_slope = data['FieldSlope']
        self.slope_length = data['SlopeLength']
        self.manning = data['Manning']
        self.field_size = data['FieldSize']
        self.practice_factor = data['PracticeFactor']
        self.sand = data['Sand']
        self.silt = data['Silt']

        # soil temperature attributes
        self.soil_albedo = data['SoilAlbedo']
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

        self.cover = data['SoilCoverType']
        if self.cover == "GRASSED":
            self.cover_factor = 0.8
        elif self.cover == "RESIDUE COVER":
            self.cover_factor = 0.667
        else:
            self.cover_factor = 0.5333

        self.leach = 0.0
        self.area = data['FieldSize']

        # Initialize phosphorus pools and variables
        # "pseudocode_soil" S.5.A
        self.labile_P = 0.0
        self.active_P = 0.0
        self.stable_P = 0.0
        self.org_P = 0.0
        self.soil_P = 0.0

        for layer in self.soil_layers:
            # S.5.A.1
            layer.PSP_max = -0.045 * log(layer.clay) + 0.001 * \
                            layer.labile_P - 0.035 * layer.org_C + 0.43
            layer.PSP_act = max(0.05, min(0.7, layer.PSP_max))
            layer.PSP_avg = layer.PSP_act

            # S.5.A.2
            layer.labile_P = layer.labile_P * layer.bulk_density \
                             * layer.thickness_cm * 0.1
            self.labile_P += layer.labile_P

            # S.5.A.3
            layer.active_P = layer.labile_P * (1.0 - layer.PSP_act) / layer.PSP_act
            self.active_P += layer.active_P

            # S.5.A.4
            layer.stable_P = layer.active_P * 4.0
            self.stable_P += layer.stable_P

            # S.5.A.5 TODO organic soil pools (labile_O, and active_O) are not being tracked
            layer.org_P = layer.org_C / 8.0 / 14.0 * 10000 * layer.bulk_density \
                          * layer.thickness_cm * 0.1
            self.org_P += layer.org_P

            # S.5.A.6
            layer.mass = layer.bulk_density * layer.thickness_cm * 10000

        # fertilizer
        self.fert_applied = 0.0
        self.fert_applied_annual = 0.0
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_P_available = 0.0  # avfrtp
        self.fert_P_released = 0.0  # rsfrtp
        self.depth_fact = 0.0

        # manure
        self.manure_type = None
        self.manure_moisture = 0.5
        self.manure_cov = 0.0

        self.manure_applied = 0.0
        self.manure_applied_annual = 0.0

        self.manure_mass = 0.0
        self.manure_applied = 0.0

        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0

        # soluble_p
        self.DRP_leach = 0.0
        self.DRP_runoff = 0.0

        self.DRP_runoff_annual = 0.0
        self.DRP_leach_annual = 0.0

        self.M_DRP_runoff = 0.0
        self.M_DRP_runoff_annual = 0.0

        # fert_leach
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_P_leach = 0.0
        self.PD_factor = 0.0
        self.fert_P_runoff = 0.0
        self.fert_P_runoff_annual = 0.0
        self.fert_P_leach_annual = 0.0
        self.fert_P_runoff_act = 0.0

        # manure_leach
        self.MIP_leach = 0.0
        self.MOP_leach = 0.0

        self.M_leach = 0.0

        self.MIP_leach_annual = 0.0
        self.MOP_leach_annual = 0.0

        self.M_leach_annual = 0.0

        self.MIP_runoff = 0.0
        self.MOP_runoff = 0.0

        self.MIP_runoff_annual = 0.0
        self.MOP_runoff_annual = 0.0

        self.DP = 0.0
        self.TIP_runoff = 0.0

        self.TIP_runoff_annual = 0.0

        # Phosphorus erosion
        self.sed = 0.0
        self.sed_P = 0.0
        self.sed_P_conc = 0.0
        self.enrichment_P = 0.0
        self.runoff_conc = 0.0

        # Phosphorus mass balance
        self.profile_P = 0.0
        for layer in self.soil_layers:
            self.profile_P += layer.labile_P + layer.active_P + \
                              layer.stable_P + layer.org_P

        self.initial_profile_P = self.profile_P

        self.manure_P_applied = 0.0
        self.P_calc = 0.0
        self.P_balance_difference = 0.0
        self.delta_P = 0.0

        self.P_drainage = 0.0
        self.P_runoff = 0.0
        self.P_erosion = 0.0
        self.P_uptake = 0.0

        # annual phosphorus balance
        self.manure_P_applied_annual = 0.0
        self.P_calc_annual = 0.0
        self.P_balance_difference_annual = 0.0
        self.delta_P_annual = 0.0

        self.P_drainage_annual = 0.0
        self.P_runoff_annual = 0.0
        self.P_erosion_annual = 0.0
        self.P_uptake_annual = 0.0

        # soil hydrology
        self.calculate_soil_water()  # calculate soil water in layer
        self.calculate_wilting_water()  # calculate wilting water in layer
        self.calculate_field_capacity()  # calculate field capacity water in layer
        self.calculate_saturation_water()  # calculate saturation water in layer

        self.evap_max = 0.0
        self.trans_max = 0.0
        self.ET_max = 0.0
        self.ET_act = 0.0

        # soil water mass balance
        self.profile_SW = 0.0

        for layer in self.soil_layers:
            self.profile_SW += layer.soil_water

        self.initial_profile_SW = self.profile_SW

        self.p_act = 0.0
        self.p_calc = 0.0
        self.water_balance_difference = 0.0
        self.delta_SW = 0.0

        self.runoff = 0.0
        self.evap = 0.0
        self.trans = 0.0
        self.drainage = 0.0

        self.ET_max_annual = 0.0
        self.ET_annual = 0.0

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
        self.residue = data['initial_residue']

        # soil Nitrogen
        self.decay_rate = 0.0

        self.NO3_runoff = 0.0
        self.NH4_runoff = 0.0

        self.NO3_runoff_annual = 0.0
        self.NH4_runoff_annual = 0.0

        self.NO3_drainage = 0.0
        self.NH4_drainage = 0.0
        self.active_N_drainage = 0.0

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

        self.NH4_erosion = 0.0
        self.active_N_erosion = 0.0
        self.stable_N_erosion = 0.0
        self.fresh_N_erosion = 0.0

        self.NH4_erosion_annual = 0.0
        self.active_N_erosion_annual = 0.0
        self.stable_N_erosion_annual = 0.0
        self.fresh_N_erosion_annual = 0.0

        self.N_uptake = 0.0

        self.N_uptake_annual = 0.0

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
            frac_N = 0.02
            active_N = frac_N * org_N

            # "pseudocode_soil" S.4.A.4
            stable_N = (1 - frac_N) * org_N

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

        # Nitrogen mass balance
        self.profile_N = 0.0
        for layer in self.soil_layers:
            self.profile_N += layer.NO3 + layer.NH4 + \
                              layer.org_N + layer.active_N + layer.stable_N

        self.profile_N += self.fresh_N
        self.initial_profile_N = self.profile_N

        self.manure_N_applied = 0.0
        self.N_calc = 0.0
        self.N_balance_difference = 0.0
        self.delta_N = 0.0

        self.N_drainage = 0.0
        self.N_runoff = 0.0
        self.N_erosion = 0.0
        self.N_uptake = 0.0

        # annual nitrogen balance
        self.manure_N_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.N_calc_annual = 0.0
        self.N_balance_difference_annual = 0.0
        self.delta_N_annual = 0.0

        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0
        self.N_uptake_annual = 0.0

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

            # evapotranspiration
            self.top_evap = 0.0  # evaporation demand at top of layer
            self.bottom_evap = 0.0  # evaporation demand at bottom of layer
            self.evap = 0.0  # evaporation demand at layer
            self.trans_act = 0.0  # actual transpiration for the layer (updated in crop)

            # soil temperature
            self.temperature = layer_data['InitialTemperature']

            # percolation
            self.ksat = layer_data['Ksat']  # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.perc = 0.0  # amount of water that percolates to next layer

            self.clay = layer_data['Clay']  # soil clay % in soil layer

            # Nitrogen
            self.org_C = layer_data['org_C%']

            self.temp_fac = 0.0
            self.water_fac = 0.0

            self.NO3 = 0.0
            self.NH4 = 0.0
            self.org_N = 0.0
            self.active_N = 0.0
            self.stable_N = 0.0

            self.NO3_perc = 0.0
            self.NH4_perc = 0.0
            self.active_N_perc = 0.0
            self.N_min_act = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.N_trans = 0.0
            self.nitri_volatil = 0.0

            self.de_N_rate = layer_data['DenitrificationRate']

            self.N_uptake = 0.0

            # Phosphorus
            self.soil_P = 0.0

            self.iso_slope = 0.0  # the slope of the isotherm curve
            self.iso_inter = 0.0  # the intercept of the isotherm curve

            self.DRP_leach = 0.0
            self.DRP_leach_act = 0.0
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
    def calculate_field_capacity(self):
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
    def calculate_saturation_water(self):
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
    def calculate_wilting_water(self):
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

        self.p_calc_annual = self.delta_SW_annual + \
                             self.runoff_annual + self.evap_annual + \
                             self.trans_annual + self.drainage_annual

        self.water_balance_difference_annual = self.p_act_annual - self.p_calc_annual

    def annual_phosphorus_balance(self):
        self.delta_P_annual = self.profile_P - self.initial_profile_P

        self.P_calc_annual = self.delta_P_annual + \
                             self.P_runoff_annual + self.P_drainage_annual + \
                             self.P_erosion_annual + self.P_uptake_annual

        self.P_balance_difference_annual = self.manure_P_applied_annual - self.P_calc_annual

    def annual_nitrogen_balance(self):
        self.delta_N_annual = self.profile_N - self.initial_profile_N

        self.N_calc_annual = self.delta_N_annual + \
                             self.N_runoff_annual + self.N_drainage_annual + \
                             self.N_erosion_annual + self.N_uptake_annual

        self.N_balance_difference_annual = self.manure_N_applied_annual - self.N_calc_annual

    def annual_reset(self):
        """
        Description:
            Resets the annual values for the next year.
        """

        # annual mass balance reset
        # water
        self.initial_profile_SW = self.profile_SW

        self.p_act_annual = 0
        self.p_calc_annual = 0
        self.drainage_annual = 0.0
        self.runoff_annual = 0.0
        self.evap_annual = 0.0
        self.trans_annual = 0.0

        # Nitrogen
        self.initial_profile_N = self.profile_N

        self.manure_N_applied_annual = 0.0
        self.manure_N_applied_annual = 0.0
        self.N_calc_annual = 0.0
        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0

        # Phosphorus
        self.initial_profile_P = self.profile_P

        self.manure_applied_annual = 0.0

        self.manure_P_applied_annual = 0.0
        self.P_calc_annual = 0.0
        self.P_drainage_annual = 0.0
        self.P_runoff_annual = 0.0
        self.P_erosion_annual = 0.0

        # soil hydrology
        self.ET_max_annual = 0.0
        self.ET_annual = 0.0

        # soil Nitrogen
        self.NO3_runoff_annual = 0.0
        self.NH4_runoff_annual = 0.0

        self.N_uptake_annual = 0.0

        self.NH4_erosion_annual = 0.0
        self.active_N_erosion_annual = 0.0
        self.stable_N_erosion_annual = 0.0
        self.fresh_N_erosion_annual = 0.0

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

        # soil Phosphorus
        self.fert_applied_annual = 0.0

        self.DRP_runoff_annual = 0.0
        self.DRP_leach_annual = 0.0

        self.MIP_runoff_annual = 0.0
        self.MOP_runoff_annual = 0.0

        self.MIP_leach_annual = 0.0
        self.MOP_leach_annual = 0.0

        self.M_leach_annual = 0.0

        self.TIP_runoff_annual = 0.0
        self.M_DRP_runoff_annual = 0.0
