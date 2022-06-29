"""
RUFAS: Ruminant Farm Systems Model
File name: test_field.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import pytest
import logging

import numpy as np
from RUFAS.classes import Time
from RUFAS.classes import Weather
from RUFAS.routines.field.field_management import FieldManagement
from RUFAS.routines.field.crop.crop_types.corn import Corn
from RUFAS.routines.field.crop.crop_types.alfalfa import Alfalfa
from RUFAS.routines.field.soil import Soil
from RUFAS.routines.field.soil.carbon_cycling import residue_partitioning, decomp_factors, pool_gas_partitioning, carbon_cycle
from RUFAS.routines.field.crop.yields import calc_residue
LOGGER = logging.getLogger()
logging.basicConfig(level=logging.INFO)

from unittest.mock import MagicMock


def test_daily_fields_routine():
    """Unit test for function daily_fields_routine in file routines/field/field.py"""
    pass


def test_annual_fields_routine():
    """Unit test for function annual_fields_routine in file routines/field/field.py"""
    pass


def test_summarize_fields():
    """Unit test for function summarize_fields in file routines/field/field.py"""
    pass


def test_summarize_annual_variables():
    """Unit test for function summarize_annual_variables in file routines/field/field.py"""
    pass


def test_annual_reset():
    """Unit test for function annual_reset in file routines/field/field.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/biomass.py"""
    pass


def test_calc_act_biomass():
    """Unit test for function calc_act_biomass in file routines/field/crop/biomass.py"""
    pass


def test_calc_intercepted_radiation():
    """Unit test for function calc_intercepted_radiation in file routines/field/crop/biomass.py"""
    pass


def test_calc_bio_AG():
    """Unit test for function calc_bio_AG in file routines/field/crop/biomass.py"""
    pass


def test_calc_gamma_wu():
    """Unit test for function calc_gamma_wu in file routines/field/crop/biomass.py"""
    pass


def test_daily_crop_routine():
    """Unit test for function daily_crop_routine in file routines/field/crop/crop.py"""
    pass


def test_daily_reset():
    """Unit test for function daily_reset in file routines/field/crop/crop.py"""
    pass


def test_annual_variable_update():
    """Unit test for function annual_variable_update in file routines/field/crop/crop.py"""
    pass


def test_annual_crop_routine():
    """Unit test for function annual_crop_routine in file routines/field/crop/crop.py"""
    pass


def test_dormancy_routine():
    """Unit test for function dormancy_routine in file routines/field/crop/crop.py"""
    pass


def test_is_kill_year():
    """Unit test for function is_kill_year in file routines/field/crop/crop.py"""
    pass


def test_set_grow_regimen():
    """Unit test for function set_grow_regimen in file routines/field/crop/crop.py"""
    pass


def test_annual_reset():
    """Unit test for function annual_reset in file routines/field/crop/crop.py"""
    pass


def test_iterate_planting_day():
    """Unit test for function iterate_planting_day in file routines/field/crop/crop.py"""
    pass


def test_calculate_start():
    """Unit test for function calculate_start in file routines/field/crop/crop.py"""
    pass


def test_calculate_minimum_day_length():
    """Unit test for function calculate_minimum_day_length in file routines/field/crop/crop.py"""
    pass


def test_calculate_t_dorm():
    """Unit test for function calculate_t_dorm in file routines/field/crop/crop.py"""
    pass


def test_in_dormancy():
    """Unit test for function in_dormancy in file routines/field/crop/crop.py"""
    pass


def test_get_year_length():
    """Unit test for function get_year_length in file routines/field/crop/crop.py"""
    pass


def test_check_conditions_plant():
    """Unit test for function check_conditions_plant in file routines/field/crop/crop.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_gamma_reg():
    """Unit test for function calc_gamma_reg in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_w_stress():
    """Unit test for function calc_w_stress in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_t_stress():
    """Unit test for function calc_t_stress in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_n_stress():
    """Unit test for function calc_n_stress in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_phi_N():
    """Unit test for function calc_phi_N in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_p_stress():
    """Unit test for function calc_p_stress in file routines/field/crop/growth_constraints.py"""
    pass


def test_calc_phi_P():
    """Unit test for function calc_phi_P in file routines/field/crop/growth_constraints.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/heat_units.py"""
    pass


def test_calculate_fr_PHU():
    """Unit test for function calculate_fr_PHU in file routines/field/crop/heat_units.py"""
    pass


def test_calc_T_HU_min():
    """Unit test for function calc_T_HU_min in file routines/field/crop/heat_units.py"""
    pass


def test_calc_T_HU_max():
    """Unit test for function calc_T_HU_max in file routines/field/crop/heat_units.py"""
    pass


def test_calc_HU():
    """Unit test for function calc_HU in file routines/field/crop/heat_units.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/leaf_area_index.py"""
    pass


def test_calculate_shape_coefficients():
    """Unit test for function calculate_shape_coefficients in file routines/field/crop/leaf_area_index.py"""
    pass


def test_calc_fr_LAI_max():
    """Unit test for function calc_fr_LAI_max in file routines/field/crop/leaf_area_index.py"""
    pass


def test_calculate_LAI_actual():
    """Unit test for function calculate_LAI_actual in file routines/field/crop/leaf_area_index.py"""
    pass


def test_calculate_d_LAI_actual():
    """Unit test for function calculate_d_LAI_actual in file routines/field/crop/leaf_area_index.py"""
    pass


def test_calc_N_fixation():
    """Unit test for function calc_N_fixation in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_get_root_accessible_layers():
    """Unit test for function get_root_accessible_layers in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_calc_f_gr():
    """Unit test for function calc_f_gr in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_calc_f_NO3():
    """Unit test for function calc_f_NO3 in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_calc_f_sw():
    """Unit test for function calc_f_sw in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_calc_N_demand():
    """Unit test for function calc_N_demand in file routines/field/crop/nitrogen_fixation.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_fr_N():
    """Unit test for function calc_fr_N in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_n2():
    """Unit test for function calc_n2 in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_n1():
    """Unit test for function calc_n1 in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_log_term_of_shape_coefficient():
    """Unit test for function calc_log_term_of_shape_coefficient in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_bio_N_opt():
    """Unit test for function calc_bio_N_opt in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_N_up():
    """Unit test for function calc_N_up in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_act_N_up_each_layer():
    """Unit test for function calc_act_N_up_each_layer in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_N_uptake():
    """Unit test for function N_uptake in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_N_up_each_layer():
    """Unit test for function calc_N_up_each_layer in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_N_up_z():
    """Unit test for function calc_N_up_z in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_calc_bio_N():
    """Unit test for function calc_bio_N in file routines/field/crop/nitrogen_uptake.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_fr_P():
    """Unit test for function calc_fr_P in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_p2():
    """Unit test for function calc_p2 in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_p1():
    """Unit test for function calc_p1 in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_log_term_of_shape_coefficient():
    """Unit test for function calc_log_term_of_shape_coefficient in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_bio_P_opt():
    """Unit test for function calc_bio_P_opt in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_P_up():
    """Unit test for function calc_P_up in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_act_P_up_each_layer():
    """Unit test for function calc_act_P_up_each_layer in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_P_up_each_layer():
    """Unit test for function calc_P_up_each_layer in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_P_up_z():
    """Unit test for function calc_P_up_z in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_calc_bio_P():
    """Unit test for function calc_bio_P in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_P_uptake():
    """Unit test for function P_uptake in file routines/field/crop/phosphorus_uptake.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/root_development.py"""
    pass


def test_calc_daily_root_biomass():
    """Unit test for function calc_daily_root_biomass in file routines/field/crop/root_development.py"""
    pass


def test_calc_z_root():
    """Unit test for function calc_z_root in file routines/field/crop/root_development.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/transpiration.py"""
    pass


def test_calc_max_water_uptake_each_layer():
    """Unit test for function calc_max_water_uptake_each_layer in file routines/field/crop/transpiration.py"""
    pass


def test_calc_max_water_uptake_z():
    """Unit test for function calc_max_water_uptake_z in file routines/field/crop/transpiration.py"""
    pass


def test_inc_lower_layer_uptake():
    """Unit test for function inc_lower_layer_uptake in file routines/field/crop/transpiration.py"""
    pass


def test_decrease_efficiency_of_uptake():
    """Unit test for function decrease_efficiency_of_uptake in file routines/field/crop/transpiration.py"""
    pass


def test_calc_act_water_uptake():
    """Unit test for function calc_act_water_uptake in file routines/field/crop/transpiration.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/crop/yields.py"""
    pass


def test_calc_HI_max():
    """Unit test for function calc_HI_max in file routines/field/crop/yields.py"""
    pass


def test_calc_HI_act():
    """Unit test for function calc_HI_act in file routines/field/crop/yields.py"""
    pass


def test_calc_dry_down():
    """Unit test for function calc_dry_down in file routines/field/crop/yields.py"""
    pass


def test_calc_yield_max():
    """Unit test for function calc_yield_max in file routines/field/crop/yields.py"""
    pass


def test_calc_yield_act():
    """Unit test for function calc_yield_act in file routines/field/crop/yields.py"""
    pass


def test_calc_quality_assessment():
    """Unit test for function calc_quality_assessment in file routines/field/crop/yields.py"""
    pass


def test_calc_nutrient_removal():
    """Unit test for function calc_nutrient_removal in file routines/field/crop/yields.py"""
    pass


def test_calc_residue():
    """Unit test for function calc_residue in file routines/field/crop/yields.py"""
    try:
        LOGGER.info("Testing function calc_residue in yields.py")


        #tests for the annual crop
        LOGGER.info("Running tests for annual crop... Corn")

        annual_soil = MagicMock(Soil)
        annual_soil_layer = MagicMock(Soil.SoilLayer)
        annual_crop = MagicMock(Corn) 
        annual_time = MagicMock(Time)
        annual_FM = MagicMock(FieldManagement)
        annual_base_app = MagicMock(FieldManagement.BaseApplicationManagement)

        corn_attributes = {
            "fr_root" : 0,
            "biomass_actual" : 1,
            "yield_actual": 0,
            "kill_day" : 3,
            "crop_type" : 'annual',
            "accumulated_HU" : 0,
            "PHU" : 2,
            "LAI_actual" : 0,
            "bio_P" : 0,
            "bio_N" : 0
        }
        time_attributes_annual = {
            "day" : 1,
            "calendar_year" : 1990
        }
        soil_layer_attributes_annual= {
            "tillage_percent" : 0.55
        }
        annual_soil_attributes = {
            "soil_layers" : [annual_soil_layer],
            "residue" : 0
        }
        field_management_attributes_annual = {
            "managed_applications" : {
                'tillage' : annual_base_app
            }

        }
        baseApp_attributes_annual = {
            "applications" : {}
        }
        
        annual_soil_layer.configure_mock(**soil_layer_attributes_annual)
        annual_soil.configure_mock(**annual_soil_attributes)
        annual_crop.configure_mock(**corn_attributes) 
        annual_time.configure_mock(**time_attributes_annual)
        annual_base_app.configure_mock(**baseApp_attributes_annual)
        annual_FM.configure_mock(**field_management_attributes_annual)

        calc_residue(annual_soil, annual_crop, annual_FM, annual_time)

        LOGGER.info("Checking soil residue_harvest")
        np.testing.assert_almost_equal(1,annual_soil.residue_harvest) 



        #perennial crop
        LOGGER.info("Running tests for perennial crop... Alfalfa")
        perennial_soil = MagicMock(Soil)
        perennial_soil_layer = MagicMock(Soil.SoilLayer)
        perennial_crop = MagicMock(Alfalfa) 
        perennial_time = MagicMock(Time)
        perennial_FM = MagicMock(FieldManagement)
        perennial_base_app = MagicMock(FieldManagement.BaseApplicationManagement)
        

        alfalfa_attributes = {
             "fr_root" : 0,
            "biomass_actual" : 1,
            "yield_actual": 0,
            "kill_day" : 3,
            "crop_type" : 'perennial',
            "accumulated_HU" : 0,
            "PHU" : 2,
            "LAI_actual" : 0,
            "bio_P" : 0,
            "bio_N" : 0
        }
        time_attributes_perennial = {
            "day" : 1,
            "calendar_year" : 1990
        }
        soil_layer_attributes_perennial = {
            "tillage_percent" : 0.55
        }
        perennial_soil_attributes = {
            "soil_layers" : [perennial_soil_layer],
            "residue" : 0
        }
        field_management_attributes_perennial = {
            "managed_applications" : {
                'tillage' : perennial_base_app
            }

        }
        baseApp_attributes_perennial = {
            "applications" : {}
        }

        perennial_soil_layer.configure_mock(**soil_layer_attributes_perennial)
        perennial_soil.configure_mock(**perennial_soil_attributes)
        perennial_crop.configure_mock(**alfalfa_attributes) 
        perennial_time.configure_mock(**time_attributes_perennial)
        perennial_base_app.configure_mock(**baseApp_attributes_perennial)
        perennial_FM.configure_mock(**field_management_attributes_perennial)


        calc_residue(perennial_soil, perennial_crop, perennial_FM, perennial_time)

        LOGGER.info("Checking soil residue_harvest")
        np.testing.assert_almost_equal(0,perennial_soil.residue_harvest) 
        
    except:
        assert False
    


def test_calc_harvest_quality():
    """Unit test for function calc_harvest_quality in file routines/field/crop/yields.py"""
    pass


def test_kill():
    """Unit test for function kill in file routines/field/crop/yields.py"""
    pass


def test_cut():
    """Unit test for function cut in file routines/field/crop/yields.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/field_management/fertilizer_application.py"""
    pass


def test_formulate_fert_app():
    """Unit test for function formulate_fert_app in file routines/field/field_management/fertilizer_application.py"""
    pass


def test_fertilizer_P():
    """Unit test for function fertilizer_P in file routines/field/field_management/fertilizer_application.py"""
    pass


def test_fertilizer_N():
    """Unit test for function fertilizer_N in file routines/field/field_management/fertilizer_application.py"""
    pass


def test_fertilizer_K():
    """Unit test for function fertilizer_K in file routines/field/field_management/fertilizer_application.py"""
    pass


def test_daily_field_management_routine():
    """Unit test for function daily_field_management_routine in file routines/field/field_management/field_management.py"""
    pass


def test_daily_field_management_reset():
    """Unit test for function daily_field_management_reset in file routines/field/field_management/field_management.py"""
    pass


def test_check_conditions():
    """Unit test for function check_conditions in file routines/field/field_management/field_management.py"""
    pass


def test_update_annual_variables():
    """Unit test for function update_annual_variables in file routines/field/field_management/field_management.py"""
    pass


def test_annual_reset():
    """Unit test for function annual_reset in file routines/field/field_management/field_management.py"""
    pass


def test_populate_scheduled_applications():
    """Unit test for function populate_scheduled_applications in file routines/field/field_management/field_management.py"""
    pass


def test_populate_rotations():
    """Unit test for function populate_rotations in file routines/field/field_management/field_management.py"""
    pass


def test_schedule_application():
    """Unit test for function schedule_application in file routines/field/field_management/field_management.py"""
    pass


def test_iterate_application():
    """Unit test for function iterate_application in file routines/field/field_management/field_management.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/field_management/manure_application.py"""
    pass


def test_formulate_manure_application():
    """Unit test for function formulate_manure_application in file routines/field/field_management/manure_application.py"""
    pass


def test_added_manure_P():
    """Unit test for function added_manure_P in file routines/field/field_management/manure_application.py"""
    pass


def test_added_manure_N():
    """Unit test for function added_manure_N in file routines/field/field_management/manure_application.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/field_management/tillage_application.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/evapotranspiration.py"""
    pass


def test_calc_potential_evap():
    """Unit test for function calc_potential_evap in file routines/field/soil/evapotranspiration.py"""
    pass


def test_calc_LHV():
    """Unit test for function calc_LHV in file routines/field/soil/evapotranspiration.py"""
    pass


def test_calc_crop_transpiration():
    """Unit test for function calc_crop_transpiration in file routines/field/soil/evapotranspiration.py"""
    pass


def test_calc_soil_evap():
    """Unit test for function calc_soil_evap in file routines/field/soil/evapotranspiration.py"""
    pass


def test_calc_soil_cov():
    """Unit test for function calc_soil_cov in file routines/field/soil/evapotranspiration.py"""
    pass


def test_update_evap_z():
    """Unit test for function update_evap_z in file routines/field/soil/evapotranspiration.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/infiltration.py"""
    pass


def test_calc_runoff():
    """Unit test for function calc_runoff in file routines/field/soil/infiltration.py"""
    pass


def test_calc_S():
    """Unit test for function calc_S in file routines/field/soil/infiltration.py"""
    pass


def test_calc_CN1():
    """Unit test for function calc_CN1 in file routines/field/soil/infiltration.py"""
    pass


def test_calc_CN3():
    """Unit test for function calc_CN3 in file routines/field/soil/infiltration.py"""
    pass


def test_calc_S_max():
    """Unit test for function calc_S_max in file routines/field/soil/infiltration.py"""
    pass


def test_calc_w1():
    """Unit test for function calc_w1 in file routines/field/soil/infiltration.py"""
    pass


def test_calc_w2():
    """Unit test for function calc_w2 in file routines/field/soil/infiltration.py"""
    pass


def test_calc_S3():
    """Unit test for function calc_S3 in file routines/field/soil/infiltration.py"""
    pass


def test_sum_SW():
    """Unit test for function sum_SW in file routines/field/soil/infiltration.py"""
    pass


def test_sum_WW():
    """Unit test for function sum_WW in file routines/field/soil/infiltration.py"""
    pass


def test_calc_daily_infiltration():
    """Unit test for function calc_daily_infiltration in file routines/field/soil/infiltration.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/percolation.py"""
    pass


def test_calc_daily_percolation():
    """Unit test for function calc_daily_percolation in file routines/field/soil/percolation.py"""
    pass


def test_daily_soil_routine():
    """Unit test for function daily_soil_routine in file routines/field/soil/soil.py"""
    pass


def test_daily_soil_reset():
    """Unit test for function daily_soil_reset in file routines/field/soil/soil.py"""
    pass


def test_annual_variable_update():
    """Unit test for function annual_variable_update in file routines/field/soil/soil.py"""
    pass


def test_initialize_profile_characteristics():
    """Unit test for function initialize_profile_characteristics in file routines/field/soil/soil.py"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in file routines/field/soil/soil.py"""
    pass


def test_annual_water_balance():
    """Unit test for function annual_water_balance in file routines/field/soil/soil.py"""
    pass


def test_annual_phosphorus_balance():
    """Unit test for function annual_phosphorus_balance in file routines/field/soil/soil.py"""
    pass


def test_annual_nitrogen_balance():
    """Unit test for function annual_nitrogen_balance in file routines/field/soil/soil.py"""
    pass


def test_annual_reset():
    """Unit test for function annual_reset in file routines/field/soil/soil.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_sed():
    """Unit test for function calc_sed in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_peak_runoff():
    """Unit test for function calc_peak_runoff in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_I():
    """Unit test for function calc_I in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_T_conc():
    """Unit test for function calc_T_conc in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_Rtc():
    """Unit test for function calc_Rtc in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_alpha():
    """Unit test for function calc_alpha in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_alpha_05():
    """Unit test for function calc_alpha_05 in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_K():
    """Unit test for function calc_K in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_Fc_sand():
    """Unit test for function calc_Fc_sand in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_Fcl_si():
    """Unit test for function calc_Fcl_si in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_F_org_C():
    """Unit test for function calc_F_org_C in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_F_sand():
    """Unit test for function calc_F_sand in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_C():
    """Unit test for function calc_C in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_LS():
    """Unit test for function calc_LS in file routines/field/soil/soil_erosion.py"""
    pass


def test_calc_m():
    """Unit test for function calc_m in file routines/field/soil/soil_erosion.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_T_soil():
    """Unit test for function calc_T_soil in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_dd():
    """Unit test for function calc_dd in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_scale():
    """Unit test for function calc_scale in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_dd_max():
    """Unit test for function calc_dd_max in file routines/field/soil/soil_temp.py"""
    pass


def test_sum_soil_water():
    """Unit test for function sum_soil_water in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_T_surf():
    """Unit test for function calc_T_surf in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_T_bare():
    """Unit test for function calc_T_bare in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_radiate():
    """Unit test for function calc_radiate in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_albedo():
    """Unit test for function calc_albedo in file routines/field/soil/soil_temp.py"""
    pass


def test_calc_bcv():
    """Unit test for function calc_bcv in file routines/field/soil/soil_temp.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/soil_water.py"""
    pass


def test_update_profile_SW():
    """Unit test for function update_profile_SW in file routines/field/soil/soil_water.py"""
    pass


def test_update_annual_SW():
    """Unit test for function update_annual_SW in file routines/field/soil/soil_water.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/carbon_cycling/carbon_cycle.py"""
    pass


def test_soil_carbon_aggregation():
    """Unit test for function soil_carbon_aggregation in file routines/field/soil/carbon_cycling/carbon_cycle.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/carbon_cycling/decomp_factors.py"""
    pass


def test_temp_factor():
    """Unit test for function temp_factor in file routines/field/soil/carbon_cycling/decomp_factors.py"""
    pass


def test_moisture_factor():
    """Unit test for function moisture_factor in file routines/field/soil/carbon_cycling/decomp_factors.py"""
    pass


def test_update_all_pool_gas_partitioning():
    """Unit test for function update_all in file routines/field/soil/carbon_cycling/pool_gas_partitioning.py"""
    try:
        LOGGER.info("Testing function: update_all")
        test_soil = MagicMock(Soil)
        test_soil_layer = MagicMock(Soil.SoilLayer)
        test_time = MagicMock(Time)
        test_weather = MagicMock(Weather)
        test_crop_type = MagicMock(Corn)

        layer_attributes = {
            "water_fac": 0.0,
            "AG_met": 1250000,
            "BG_met": 1250000,
            "tillage_percent": 0.0,
            "AG_struct": 1250000,
            "BG_struct": 1250000,
            "thickness": 0.0,
            "C_active": 1250000,
            "C_slow": 1250000,
            "C_passive": 1250000,
            "AG_struct_to_C_active" : 0,
            "AG_struct_to_C_slow" : 0
        }
        soil_attributes = {
            "soil_layers": [test_soil_layer],
            "AG_lignin_res_percent": 17,
            "residue_harvest": 0.0,
            "BG_lignin_res_percent": 17,
            "profile_depth": 279.4,
            "silt_to_clay_percent": 0.5
        }
        weather_attributes = {
            "T_avg": [[0]],
            "rainfall": [[0]]
        }
        time_attributes = {
            "year": 1,
            "day": 1
        }
        corn_attributes = {
            "bio_AG" : 0,
            "bio_BG": 0,
            "fr_N": 0,
            "extracted" : True
        }
        test_soil.configure_mock(**soil_attributes)
        test_soil_layer.configure_mock(**layer_attributes)
        test_weather.configure_mock(**weather_attributes)
        test_time.configure_mock(**time_attributes)
        test_crop_type.configure_mock(**corn_attributes)

        decomp_factors.update_all(test_soil, test_weather, test_time)
        residue_partitioning.update_all(soil=test_soil, crop_type=test_crop_type, weather=test_weather,
                                        time=test_time)
        pool_gas_partitioning.update_all(test_soil)

        LOGGER.info("Checking changes to soil layers")
        LOGGER.info("Checking Layer 0")
        layer0 = test_soil.soil_layers[0]
        np.testing.assert_almost_equal(0.03505788081471571, layer0.AG_met_to_C_active_loss)
        np.testing.assert_almost_equal(0.028683720666585574, layer0.AG_met_to_C_active_act)
        np.testing.assert_almost_equal(8.77950623625564e-05, layer0.AG_struct_to_C_active_loss)
        np.testing.assert_almost_equal(0.00010730507622090227, layer0.AG_struct_to_C_active_act)
        np.testing.assert_almost_equal(5.85300415750376e-05, layer0.AG_struct_to_C_slow_loss)
        np.testing.assert_almost_equal(0.00013657009700842107, layer0.AG_struct_to_C_slow_act)
        np.testing.assert_almost_equal(0.043822351018394635, layer0.BG_met_to_C_active_loss)
        np.testing.assert_almost_equal(0.035854650833231964, layer0.BG_met_to_C_active_act)
        np.testing.assert_almost_equal(0.009609046423306167, layer0.BG_struct_to_C_active_loss)
        np.testing.assert_almost_equal(0.011744390072929762, layer0.BG_struct_to_C_active_act)
        np.testing.assert_almost_equal(0.006406030948870778, layer0.BG_struct_to_C_slow_loss)
        np.testing.assert_almost_equal(0.014947405547365148, layer0.BG_struct_to_C_slow_act)
        np.testing.assert_almost_equal(0.00019510013858345867,layer0.AG_struct_to_C_active)
        np.testing.assert_almost_equal(0.00019510013858345867,layer0.AG_struct_to_C_slow)
        np.testing.assert_almost_equal(0,test_crop_type.bio_AG)

        assert True
    except:
        assert False


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/carbon_cycling/residue_partitioning.py"""
    pass


def test_residue_partitioning():
    """Unit test for function residue_partitioning in file routines/field/soil/carbon_cycling/residue_partitioning.py"""
    LOGGER.info("Testing function: residue_partitioning")
    try:
        test_soil = MagicMock(Soil)
        test_soil_layer = MagicMock(Soil.SoilLayer)
        test_time = MagicMock(Time)
        test_weather = MagicMock(Weather)
        test_crop_type = MagicMock(Corn)

        layer_attributes = {
            "water_fac": 0.0,
            "AG_met": 1250000,
            "BG_met": 1250000,
            "tillage_percent": 0.0,
            "AG_struct": 1250000,
            "BG_struct": 1250000,
            "thickness": 0.0,
            "C_active": 1250000,
            "C_slow": 1250000,
            "C_passive": 1250000,
            "M_d": 0,
            "AG_struct_to_C_active_loss": 0,
            "AG_struct_to_C_active" : 0,
            "AG_struct_to_C_slow" : 0,
            "ADJ_crop_type_bio_BG" : 0
        }
        soil_attributes = {
            "soil_layers": [test_soil_layer],
            "AG_lignin_res_percent": 17,
            "residue_harvest": 0.0,
            "BG_lignin_res_percent": 17,
            "profile_depth": 279.4,
            "AG_L_to_N" : 0
        }
        weather_attributes = {
            "T_avg": [[0]],
            "rainfall": [[0]]
        }
        time_attributes = {
            "year": 1,
            "day": 1
        }
        corn_attributes = {
            "bio_BG": 0,
            "fr_N": 0,
            "extracted" : "true",
            "bio_AG" : 0
        }
        test_soil.configure_mock(**soil_attributes)
        test_soil_layer.configure_mock(**layer_attributes)
        test_weather.configure_mock(**weather_attributes)
        test_time.configure_mock(**time_attributes)
        test_crop_type.configure_mock(**corn_attributes)

        decomp_factors.temp_factor(test_soil, test_weather, test_time)
        residue_partitioning.residue_partitioning(soil=test_soil, crop_type=test_crop_type, weather=test_weather,
                                                    time=test_time)

        LOGGER.info("Checking changes to soil")
        np.testing.assert_almost_equal(17.0, test_soil.AG_lignin_res_percent)
        np.testing.assert_almost_equal(0.425, test_soil.AG_L_to_N)

        LOGGER.info("Checking ADJ_crop_type_bio_BG for soil layers")
        layer0 = test_soil.soil_layers[0]
        np.testing.assert_almost_equal(0, layer0.ADJ_crop_type_bio_BG)
        np.testing.assert_almost_equal(17, test_soil.AG_lignin_res_percent)
        np.testing.assert_almost_equal(0.425, test_soil.AG_L_to_N)
        np.testing.assert_almost_equal(0, layer0.AG_met_to_C_active)
        np.testing.assert_almost_equal(1250000.0, layer0.AG_met)
        np.testing.assert_almost_equal(1250000.0, layer0.AG_struct)
        np.testing.assert_almost_equal(0, layer0.AG_struct_to_C_active)
        np.testing.assert_almost_equal(0, layer0.AG_struct_to_C_slow)
        np.testing.assert_almost_equal(17.0, test_soil.BG_lignin_res_percent)
        np.testing.assert_almost_equal(0, layer0.BG_met_to_C_active)
        np.testing.assert_almost_equal(1250000.0, layer0.BG_met)
        np.testing.assert_almost_equal(0, layer0.BG_struct_to_C_active)
        np.testing.assert_almost_equal(0, layer0.BG_struct_to_C_slow)
        np.testing.assert_almost_equal(1250000.0, layer0.BG_struct)



        assert True
    except: 
        assert False


def test_denitrification():
    """Unit test for function denitrification in file routines/field/soil/nitrogen_cycling/denitrification.py"""
    pass


def test_humus_mineralization():
    """Unit test for function humus_mineralization in file routines/field/soil/nitrogen_cycling/humus_mineralization.py"""
    pass


def test_leaching_runoff_erosion():
    """Unit test for function leaching_runoff_erosion in file routines/field/soil/nitrogen_cycling/leaching_runoff_erosion.py"""
    pass


def test_mineralization_decomp():
    """Unit test for function mineralization_decomp in file routines/field/soil/nitrogen_cycling/mineralization_decomp.py"""
    pass


def test_nitrification_volatilization():
    """Unit test for function nitrification_volatilization in file routines/field/soil/nitrogen_cycling/nitrification_volatilization.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/nitrogen_cycling/nitrogen_cycling.py"""
    pass


def test_calc_temp_factors():
    """Unit test for function calc_temp_factors in file routines/field/soil/nitrogen_cycling/nitrogen_cycling.py"""
    pass


def test_calc_water_factors():
    """Unit test for function calc_water_factors in file routines/field/soil/nitrogen_cycling/nitrogen_cycling.py"""
    pass


def test_update_profile_N():
    """Unit test for function update_profile_N in file routines/field/soil/nitrogen_cycling/nitrogen_cycling.py"""
    pass


def test_update_annual_N():
    """Unit test for function update_annual_N in file routines/field/soil/nitrogen_cycling/nitrogen_cycling.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/erosion.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/fert_leach.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/manure_leach.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/phosphorus_cycling.py"""
    pass


def test_update_profile_P():
    """Unit test for function update_profile_P in file routines/field/soil/phosphorus_cycling/phosphorus_cycling.py"""
    pass


def test_update_annual_P():
    """Unit test for function update_annual_P in file routines/field/soil/phosphorus_cycling/phosphorus_cycling.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/P_mineralization.py"""
    pass


def test_update_all():
    """Unit test for function update_all in file routines/field/soil/phosphorus_cycling/soluble_P.py"""
    pass
