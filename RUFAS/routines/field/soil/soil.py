"""
RUFAS: Ruminant Farm Systems Model
File name: soil.py

Description: Driver for the soil sub-module

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
           William Donovan, wmdonovan@wisc.edu
"""

from math import exp, log
from . import infiltration, evapotranspiration, percolation, soil_temp, soil_erosion, soil_water
from ..crop import transpiration
from .nitrogen_cycling import nitrogen_cycling
from .phosphorus_cycling import phosphorus_cycling
from .carbon_cycling import carbon_cycle


def daily_soil_routine(soil, crop, field_management, weather, time):
    """
    Description:
        Executes all the daily soil routines.
    Args:
        soil: instance of the Soil class
        crop: instance of the Crop class
        field_management: instance of the FieldManagement class
        weather: instance of the Weather class
        time: instance of the Time class
    """
    daily_soil_reset(soil)

    # calculate and update the temperature of the soil layers
    soil_temp.update_all(soil, crop, weather, time)

    # calculate daily runoff
    infiltration.update_all(soil, weather, time)

    # calculate daily transpiration
    evapotranspiration.update_all(soil, crop, weather, time)

    # transpiration is defined in the crop module, but called here as a
    # component of water balance
    transpiration.update_all(soil, crop.current_crop)

    # calculate daily percolation
    percolation.update_all(soil)

    # updates daily soil water fluxes
    soil_water.update_all(soil, weather, time)

    # calculate daily soil erosion
    soil_erosion.update_all(soil, crop, weather, time)

    # calculate and update the contents of 3 organic and 2 inorganic nitrogen
    # pools
    nitrogen_cycling.update_all(soil, field_management)

    phosphorus_cycling.update_all(soil, field_management, weather, time)

    carbon_cycle.update_all(soil, crop.current_crop, weather, time)

    # update annual sums at the end of each day
    annual_variable_update(soil)


def daily_soil_reset(soil):
    soil.DRP_runoff = 0.0
    soil.DRP_drainage = 0.0


def annual_variable_update(soil):
    soil_water.update_annual_SW(soil)
    phosphorus_cycling.update_annual_P(soil)
    nitrogen_cycling.update_annual_N(soil)


class Soil:

    def __init__(self, data):
        """
        Description:
            Constructs an instance of the Soil class by populating its arrays
            and the necessary values.
        Args:
            data: the information from the json input file
        """

        # soil profile
        self.CN2 = data['CN2']  # unitless, user-defined curve number (empirical)
        self.field_slope = data['field_slope']
        self.slope_length = data['slope_length']
        self.manning = data['manning']
        self.field_size = data['field_size']
        # self.practice_factor = data['practice_factor']
        self.tillage = data['tillage']
        self.sand = data['sand']
        self.silt = data['silt']

        # soil temperature
        self.soil_albedo = data['soil_albedo']
        self.T_surf = data['soil_layers']['layer_1']['initial_temperature']

        # soil layers
        self.soil_layers = []
        for layer_name, layer_data in data['soil_layers'].items():
            self.soil_layers.append(self.SoilLayer(layer_name, layer_data))

        # sort layers by bottom_depth
        self.soil_layers.sort(key=lambda x: x.bottom_depth)

        # determine profile depth
        self.profile_depth = self.soil_layers[-1].bottom_depth
        self.profile_bulk_density = 0.0

        self.cover = data['soil_cover_type']
        self.cover_factor = 0.0

        self.leach = 0.0
        self.area = data['field_size']

        self.labile_P = 0.0
        self.active_P = 0.0
        self.stable_P = 0.0
        self.org_P = 0.0
        self.soil_P = 0.0

        # fertilizer Phosphorus
        self.no_rains = 0.0
        self.fert_CNT = 0.0
        self.fert_P_available = 0.0  # avfrtp
        self.fert_P_released = 0.0  # rsfrtp
        self.depth_fact = 0.0

        # manure Phosphorus
        self.manure_type = None
        self.manure_moisture = 0.5
        self.manure_cov = 0.0

        self.manure_mass = 0.0

        self.WIP = 0.0
        self.WOP = 0.0
        self.SIP = 0.0
        self.SOP = 0.0

        # soluble_p
        self.DRP_drainage = 0.0
        self.DRP_runoff = 0.0

        self.DRP_runoff_annual = 0.0
        self.DRP_drainage_annual = 0.0

        self.M_DRP_runoff = 0.0
        self.M_DRP_runoff_annual = 0.0

        # fertilizer Phosphorus leaching
        self.fert_sorp = 0.0
        self.fert_absorbed_sum = 0.0
        self.fert_P_leached = 0.0
        self.PD_factor = 0.0
        self.fert_P_runoff = 0.0
        self.fert_P_runoff_annual = 0.0
        self.fert_P_leached_annual = 0.0
        self.fert_P_runoff_act = 0.0

        # manure Phosphorus leaching
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
        self.STP = 0.0
        self.STP_annual = 0.0

        self.profile_P = 0.0
        self.initial_profile_P = 0.0

        self.profile_P_annual = 0.0

        self.P_calc = 0.0
        self.P_balance_difference = 0.0
        self.delta_P = 0.0

        self.P_drainage = 0.0
        self.P_runoff = 0.0
        self.P_erosion = 0.0
        self.P_uptake = 0.0

        # annual Phosphorus mass balance
        self.P_calc_annual = 0.0
        self.P_balance_difference_annual = 0.0
        self.delta_P_annual = 0.0

        self.P_drainage_annual = 0.0
        self.P_runoff_annual = 0.0
        self.P_erosion_annual = 0.0
        self.P_uptake_annual = 0.0

        # soil hydrology
        self.profile_SW = 0.0
        self.initial_profile_SW = 0.0

        self.evap_max = 0.0
        self.trans_max = 0.0
        self.ET_max = 0.0
        self.ET_act = 0.0

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

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

        # soil carbon attributes
        self.residue_harvest = 0.0
        # TODO unsure what this should be initialized as
        self.AG_lignin_res_percent = 17  # tied to the reset of this variable in yields, if changed, change together
        self.BG_lignin_res_percent = 17  # tied to the reset of this variable in yields, if changed, change together

        self.curr_layer_depth = 0
        self.silt_to_clay_percent = 0.5  # TODO database item

        self.AG_L_to_N = 0
        self.BG_L_to_N = 0

        self.fresh_N = 0.0

        # Nitrogen mass balance
        self.profile_N = 0.0
        self.initial_profile_N = 0.0

        self.N_calc = 0.0
        self.N_balance_difference = 0.0
        self.delta_N = 0.0

        self.N_drainage = 0.0
        self.N_runoff = 0.0
        self.N_erosion = 0.0
        self.N_uptake = 0.0

        # annual Nitrogen mass balance
        self.N_calc_annual = 0.0
        self.N_balance_difference_annual = 0.0
        self.delta_N_annual = 0.0

        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0
        self.N_uptake_annual = 0.0

        self.K = 0.0

        self.term1 = 0.0
        self.term2 = 0.0
        self.term3 = 0.0

        self.fresh_N_average = 0.0
        self.profile_N_average = 0.0

        self.initialize_profile_characteristics()

    class SoilLayer:
        def __init__(self, layer_name, layer_data):
            """
            Description:
                An instance of this class represents a layer in the soil profile.

            Args:
                layer_name: a string which is the name of this layer
                layer_data: a dictionary which stores the information for this layer
            """
            self.name = layer_name

            # profile
            self.bottom_depth = layer_data['bottom_depth']
            self.bottom_depth_cm = self.bottom_depth / 10

            self.bulk_density = layer_data['bulk_density']
            self.mass = 0

            self.thickness = 0.0  # thickness of soil layer
            self.thickness_cm = 0.0

            self.clay = layer_data['clay']

            # Variables used for soil temperature
            self.temperature = layer_data['initial_temperature']

            # soil water
            self.wilting_point = layer_data['wilting_point']
            self.field_capacity = layer_data['field_capacity']
            self.saturation = layer_data['saturation']
            self.soil_water_percent = layer_data['soil_water_percent']

            self.fc_water = 0.0  # constant
            self.sat_water = 0.0  # constant
            self.wilting_water = 0.0  # constant
            self.soil_water = 0.0  # mm water in the soil profile

            # Variables to calculate daily evapotranspiration
            self.top_evap = 0.0  # evaporation demand at top of layer
            self.bottom_evap = 0.0  # evaporation demand at bottom of layer
            self.evap = 0.0  # evaporation demand at layer
            self.trans_act = 0.0  # actual transpiration for the layer (updated in crop)

            # Variables to calculate dailyPercolation
            self.k_sat = layer_data['K_sat']  # saturated hydraulic conductivity (mm/h)
            self.TT = 0.0
            self.percolation = 0.0  # amount of water that percolates to next layer

            # Variable to simulate nitrogen Cycling
            # self.org_C = layer_data['org_C_percent']
            self.org_C = 0
            self.active_mineral_rate = layer_data['active_mineral_rate']
            self.denitrification_rate = layer_data['denitrification_rate']
            self.NH4 = layer_data['NH4']

            # the coefficient of extraction for leaching is calibrated to 2.5
            self.Cl = 2.5

            self.temp_fac = 0.0
            self.water_fac = 0.0

            # Initial NO3 levels (kg/ha) in the soil layer:
            self.NO3 = 0.0
            self.NH4_average = 0.0
            self.NO3_average = 0.0
            self.org_N_average = 0.0
            self.active_N_average = 0.0
            self.stable_N_average = 0.0
            self.N_uptake = 0.0

            # Organic N (Active + Stable, mg/kg):
            self.org_N = 0.0

            # Initial Active N in layer:
            self.active_N = 0.0

            # Initial Stable N in layer:
            self.stable_N = 0.0

            self.NO3_percolation = 0.0
            self.NH4_percolation = 0.0
            self.active_percolation = 0.0

            self.N_min_act = 0.0
            self.nitrification = 0.0
            self.volatilization = 0.0
            self.denitrification = 0.0
            self.N_trans = 0.0
            self.tot_nitri_volatil = 0.0

            self.de_N_rate = layer_data['denitrification_rate']
            self.active_N_percent = layer_data['active_N_percent']
            self.volatile_exchange_factor = layer_data['volatile_exchange_factor']

            # Variables to simulate phosphorus cycling
            self.OM_percent = layer_data['OM_percent']

            self.soil_P = 0.0

            self.iso_slope = 0.0  # the slope of the isotherm curve
            self.iso_inter = 0.0  # the intercept of the isotherm curve

            self.DRP_leachate = 0.0
            self.DRP_leachate_act = 0.0
            self.DRP_runoff = 0.0

            self.labile_P = layer_data['labile_P']
            self.active_P = 0.0
            self.stable_P = 0.0
            self.org_P = 0.0
            self.P_uptake = 0.0

            self.labile_P_uptake = 0.0
            self.labile_P_sum = 0.0
            self.PSP_max = 0.0
            self.PSP_act = 0.0
            self.PSP_avg = 0.0

            self.pbal = 0.0
            self.days_unbalanced_labile = 0.0
            self.days_unbalanced_active = 0.0

            # C in the soil layer
            self.M_d = 0

            self.AG_met = 1250000
            self.BG_met = 1250000
            self.AG_struct = 1250000
            self.BG_struct = 1250000

            self.tillage_percent = 0.0

            self.C_active = 1250000
            self.C_slow = 1250000
            self.C_passive = 1250000

            self.AG_met_to_C_active = 0
            self.AG_struct_to_C_active = 0
            self.AG_struct_to_C_slow = 0
            self.BG_met_to_C_active = 0
            self.BG_struct_to_C_active = 0
            self.BG_struct_to_C_slow = 0

            self.AG_met_to_C_active_loss = 0
            self.AG_struct_to_C_active_loss = 0
            self.AG_struct_to_C_slow_loss = 0
            self.BG_met_to_C_active_loss = 0
            self.BG_struct_to_C_active_loss = 0
            self.BG_struct_to_C_slow_loss = 0

            self.AG_struct_to_C_active_act = 0
            self.AG_struct_to_C_slow_act = 0
            self.BG_met_to_C_active_act = 0
            self.BG_struct_to_C_active_act = 0
            self.BG_struct_to_C_slow_act = 0

            self.C_active_to_slow = 0
            self.C_active_to_passive = 0
            self.C_slow_to_active = 0
            self.C_slow_to_passive = 0
            self.C_passive_to_active = 0

            self.C_active_loss = 0
            self.C_slow_loss = 0
            self.C_passive_loss = 0

            self.C_percent = 0
            self.C = 0
            self.C_mg = 0
            self.C_g = 0
            self.C_CO2_loss = 0

            self.C_active_decomp = 0
            self.C_slow_decomp = 0
            self.C_passive_decomp = 0

            self.K = 0.0

            self.ADJ_crop_type_bio_BG = 0.0

    def initialize_profile_characteristics(self):
        if self.cover == "GRASSED":
            self.cover_factor = 0.8
        elif self.cover == "RESIDUE COVER":
            self.cover_factor = 0.667
        else:
            self.cover_factor = 0.5333

        curr_thickness = 0
        bulk_density_avg = 0.0
        for layer in self.soil_layers:
            bulk_density_avg += layer.bulk_density

            layer.thickness = layer.bottom_depth - curr_thickness
            layer.thickness_cm = layer.thickness / 10
            curr_thickness = layer.bottom_depth

            layer.soil_water = layer.thickness * layer.soil_water_percent
            layer.fc_water = layer.thickness * layer.field_capacity
            layer.sat_water = layer.thickness * layer.saturation
            layer.wilting_water = layer.thickness * layer.wilting_point
            self.profile_SW += layer.soil_water

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

            z = layer.bottom_depth

            # S.4.A.1
            exp_part = exp(-z / 1000)
            NO3 = 28 * exp_part

            # S.4.A.2
            org_C = layer.org_C
            org_N = (10 ** 4) * (org_C / 14)

            # S.4.A.3
            frac_N = 0.02
            active_N = frac_N * org_N

            # S.4.A.4
            stable_N = (1 - frac_N) * org_N

            # S.4.A.6
            NH4 = layer.NH4

            # S.4.A.7
            BD = layer.bulk_density
            thickness = layer.thickness
            unit_adjustment = (BD * thickness) / 100

            layer.NO3 = NO3 * unit_adjustment
            layer.org_N = org_N
            layer.active_N = active_N * unit_adjustment
            layer.stable_N = stable_N * unit_adjustment
            layer.NH4 = NH4 * unit_adjustment

            self.profile_N += layer.NO3 + layer.NH4 + \
                              layer.org_N + layer.active_N + layer.stable_N

            self.profile_P += layer.labile_P + layer.active_P + \
                              layer.stable_P + layer.org_P

        self.profile_bulk_density = bulk_density_avg / len(self.soil_layers)
        # S.4.A.5
        unit_adjustment = self.soil_layers[0].bulk_density * self.soil_layers[0].thickness / 100
        fresh_N = 0.0015 * self.residue
        self.fresh_N = fresh_N * unit_adjustment
        self.profile_N += self.fresh_N
        self.initial_profile_P = self.profile_P
        self.initial_profile_SW = self.profile_SW
        self.initial_profile_N = self.profile_N

    def annual_mass_balance(self, field_management, time):
        """
        Description:
            Calculates annual water balance
        """
        self.annual_water_balance()
        self.annual_phosphorus_balance(field_management, time)
        self.annual_nitrogen_balance(field_management, time)

    def annual_water_balance(self):
        self.delta_SW_annual = self.profile_SW - self.initial_profile_SW

        self.p_calc_annual = self.delta_SW_annual + \
                             self.runoff_annual + self.evap_annual + \
                             self.trans_annual + self.drainage_annual

        self.water_balance_difference_annual = self.p_act_annual - self.p_calc_annual

    def annual_phosphorus_balance(self, field_management, time):
        self.STP_annual = self.STP_annual / len(time.years[time.year - 1])

        self.delta_P_annual = self.profile_P - self.initial_profile_P

        self.P_calc_annual = self.delta_P_annual + \
                             self.P_runoff_annual + self.P_drainage_annual + \
                             self.P_erosion_annual + self.P_uptake_annual

        self.P_balance_difference_annual = field_management.manure_P_applied_annual - self.P_calc_annual

    def annual_nitrogen_balance(self, field_management, time):
        for layer in self.soil_layers:
            layer.NO3_average = layer.NO3_average / len(time.years[time.year - 1])
            layer.NH4_average = layer.NH4_average / len(time.years[time.year - 1])
            layer.active_N_average = layer.active_N_average / len(time.years[time.year - 1])
            layer.stable_N_average = layer.stable_N_average / len(time.years[time.year - 1])
            layer.org_N_average = layer.org_N_average / len(time.years[time.year - 1])

        self.fresh_N_average = self.fresh_N_average / len(time.years[time.year - 1])
        self.profile_N_average = self.profile_N_average / len(time.years[time.year - 1])

        self.delta_N_annual = self.profile_N - self.initial_profile_N

        self.N_calc_annual = self.delta_N_annual + \
                             self.N_runoff_annual + self.N_drainage_annual + \
                             self.N_erosion_annual + self.N_uptake_annual

        self.N_balance_difference_annual = field_management.manure_N_applied_annual - self.N_calc_annual

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

        self.N_calc_annual = 0.0
        self.N_drainage_annual = 0.0
        self.N_runoff_annual = 0.0
        self.N_erosion_annual = 0.0

        # Phosphorus
        self.initial_profile_P = self.profile_P

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

        self.NH4_erosion_annual = 0.0
        self.active_N_erosion_annual = 0.0
        self.stable_N_erosion_annual = 0.0
        self.fresh_N_erosion_annual = 0.0

        self.NO3_drainage_annual = 0.0
        self.NH4_drainage_annual = 0.0
        self.active_N_drainage_annual = 0.0

        # soil Phosphorus
        self.DRP_runoff_annual = 0.0
        self.DRP_drainage_annual = 0.0

        self.MIP_runoff_annual = 0.0
        self.MOP_runoff_annual = 0.0

        self.MIP_leach_annual = 0.0
        self.MOP_leach_annual = 0.0

        self.M_leach_annual = 0.0

        self.TIP_runoff_annual = 0.0
        self.M_DRP_runoff_annual = 0.0

        self.P_uptake_annual = 0.0
        self.fert_P_leached_annual = 0.0
        self.fert_P_runoff_annual = 0.0

        for layer in self.soil_layers:
            layer.NO3_average = 0.0
            layer.NH4_average = 0.0
            layer.active_N_average = 0.0
            layer.stable_N_average = 0.0
            layer.org_N_average = 0.0

        self.fresh_N_average = 0.0
        self.profile_N_average = 0.0
