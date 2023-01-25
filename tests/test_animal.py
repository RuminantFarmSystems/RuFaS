"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import pytest

from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
import RUFAS.routines.animal.ration.animal_requirements
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase

@pytest.fixture
def cow() -> AnimalBase:
    initsetup = {
        'id': '1',
        'breed': 'HO',
        'birth_date': '200',
        'days_born': '201',
        'semen_type': 'conventional',
        'body_weight': 600,
        'pen_history': []
    }
    AnimalBase.nutrients = {'dummy1': 'dummyval1', 'dummy2': 'dummyval2'}
    AnimalBase.config = {'semen_type': 'dummy'}
    cow = AnimalBase(initsetup)
    return cow


@pytest.fixture
def cow_a()->dict:
    cow_a_dict = {
        'body_weight': 600,
        'mature_body_weight':650,
        'DOP':200,
        'animal_type':'cow',
        'parity':1,
        'CI':365,
        'TP_milk':3.45,
        'Fat_Milk': 4,
        'Lactose_Milk':4.9,
        'Milk':20,
        'DIM':120,
        'lactating':True,
        'BCS5':None,
        'PrevTemp':None,
        'ADG_heifer':None,
        'daily_growth':None,
        'age':1000,
        'distance':None
    }
    return cow_a_dict


@pytest.fixture
def cow_b()->dict:
    cow_b_dict = {
        'body_weight': 400,
        'mature_body_weight':650,
        'DOP':173,
        'animal_type':'cow',
        'parity':4,
        'CI':365,
        'TP_milk':3.45,
        'Fat_Milk': 4,
        'Lactose_Milk':4.9,
        'Milk':20,
        'DIM':120,
        'lactating':False,
        'BCS5':None,
        'PrevTemp':None,
        'ADG_heifer':None,
        'daily_growth':None,
        'age':1000,
        'distance':None
    }
    return cow_b_dict


@pytest.fixture
def heifer_a()->dict:
    heifer_a_dict = {
        'body_weight': 300,
        'mature_body_weight':650,
        'DOP':None,
        'animal_type':'heifer',
        'parity':None,
        'CI':None,
        'TP_milk':None,
        'Fat_Milk': None,
        'Lactose_Milk':None,
        'Milk':None,
        'DIM':None,
        'lactating':False,
        'BCS5':3,
        'PrevTemp':15,
        'ADG_heifer':1,
        'daily_growth':None,
        'age':200,
        'distance':None
    }
    return heifer_a_dict


@pytest.fixture
def heifer_b()->dict:
    heifer_b_dict = {
        'body_weight': 300,
        'mature_body_weight':650,
        'DOP':1,
        'animal_type':'heifer',
        'parity':None,
        'CI':None,
        'TP_milk':None,
        'Fat_Milk': None,
        'Lactose_Milk':None,
        'Milk':None,
        'DIM':None,
        'lactating':False,
        'BCS5':3,
        'PrevTemp':15,
        'ADG_heifer':1,
        'daily_growth':None,
        'age':200,
        'distance':None
    }
    return heifer_b_dict


def test_calculate_NRC_energy_maintenance_requirements(cow_a, cow_b, heifer_a, heifer_b):
    """Unit test for function calculate_NRC_energy_maintenance_requirements in file routines/animal/ration/animal_requirements.py"""
    result_NEmaint, result_CW, result_CBW = \
         RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(\
             cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['DOP'], cow_a['BCS5'], \
                cow_a['PrevTemp'], cow_a['animal_type'])
    assert result_NEmaint == pytest.approx(9, abs=1)
    assert result_CW == pytest.approx(22, abs=1)
    assert result_CBW == pytest.approx(41, abs=1)

    result_NEmaint, result_CW, result_CBW = \
         RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(\
             cow_b['body_weight'], cow_b['mature_body_weight'], cow_b['DOP'], cow_b['BCS5'], \
                cow_b['PrevTemp'], cow_b['animal_type'])
    assert result_NEmaint == pytest.approx(7, abs=1)
    assert result_CW == pytest.approx(0, abs=1)
    assert result_CBW == pytest.approx(41, abs=1)
    assert (result_NEmaint, result_CW, result_CBW) == \
        pytest.approx( (7,0,41), abs=1)

    result_NEmaint, result_CW, result_CBW = \
         RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(\
             heifer_a['body_weight'], heifer_a['mature_body_weight'], heifer_a['DOP'], heifer_a['BCS5'], \
                heifer_a['PrevTemp'], heifer_a['animal_type'])
    assert result_NEmaint == pytest.approx(17, abs=1)
    assert result_CW == pytest.approx(0, abs=1)
    assert result_CBW == pytest.approx(0, abs=1)

    result_NEmaint, result_CW, result_CBW = \
         RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_energy_maintenance_requirements(\
             heifer_b['body_weight'], heifer_b['mature_body_weight'], heifer_b['DOP'], heifer_b['BCS5'], \
                heifer_b['PrevTemp'], heifer_b['animal_type'])
    assert result_NEmaint == pytest.approx(17, abs=1)
    assert result_CW == pytest.approx(0, abs=1)
    assert result_CBW == pytest.approx(41, abs=1)

def test_calculate_NASEM_energy_growth_requirements(cow_a):
    """Unit test for function calculate_NRC_energy_growth_requirements in file routines/animal/ration/animal_requirements.py"""
    pass

def test_calculate_NASEM_energy_growth_requirements(cow_a):
    """Unit test for function calculate_NASEM_energy_growth_requirements in file routines/animal/ration/animal_requirements.py"""
    pass
    result_NEg, result_ADG, result_frame_weight_gain_g  = RUFAS.routines.animal.ration.animal_requirements.calculate_NASEM_energy_growth_requirements(\
        cow_a['body_weight'], cow_a['mature_body_weight'], cow_a['ADG_heifer'], cow_a['animal_type'],
                                               cow_a['parity'], cow_a['CI'])
    assert (result_NEg, result_ADG, result_frame_weight_gain_g) == pytest.approx((1.1,.17,0.45), rel=1e-1)


def test_calculate_NRC_energy_pregnancy_requirements():
    """Unit test for function calculate_NRC_energy_pregnancy_requirements in file routines/animal/ration/animal_requirements.py"""
    pass

def test_calculate_NRC_energy_lactation_requirements():
    """Unit test for function calculate_NRC_energy_lactation_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NRC_protein_requirements():
    """Unit test for function calculate_NRC_protein_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NRC_calcium_requirements():
    """Unit test for function calculate_NRC_calcium_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NRC_P_requirements():
    """Unit test for function calculate_NRC_P_requirements in file routines/animal/ration/animal_requirements.py"""
    # case 1: cow value
    result = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_P_requirements(
        600, 650, 100, 10, 'cow', 10)
    expected = 70
    assert result == pytest.approx(expected, abs=1)
    # case 2: heifer value
    result = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_P_requirements(
        600, 650, 100, 10, 'heifer', 10)
    assert result == pytest.approx(61, abs=1)
    # case 3: calf should compute nothing
    #result = RUFAS.routines.animal.ration.animal_requirements.calculate_NRC_P_requirements(
    #    600, 650, 100, 10, 'calf', 10)
    #assert result == pytest.approx(61, abs=1)
    


def test_calculate_NRC_DMI():
    """Unit test for function calculate_NRC_DMI in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_energy_lactation_requirements():
    """Unit test for function calculate_NASEM_energy_lactation_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_DMI():
    """Unit test for function calculate_NASEM_DMI in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_energy_maintenance_requirements():
    """Unit test for function calculate_NASEM_energy_maintenance_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_energy_growth_requirements():
    """Unit test for function calculate_NASEM_energy_growth_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_energy_pregnancy_requirements():
    """Unit test for function calculate_NASEM_energy_pregnancy_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_protein_requirements():
    """Unit test for function calculate_NASEM_protein_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_calcium_requirements():
    """Unit test for function calculate_NASEM_calcium_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_calculate_NASEM_P_requirements():
    """Unit test for function calculate_NASEM_P_requirements in file routines/animal/ration/animal_requirements.py"""
    pass


def test_norm():
    """Unit test for function norm in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_percentile_list():
    """Unit test for function percentile_list in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_grouping():
    """Unit test for function grouping in file routines/animal/clustering_pen_grouping.py"""
    pass


def test_update_animals():
    """Unit test for function update_animals in file routines/animal/pen.py"""
    pass


def test_call_animal_nutrient_rqmts():
    """Unit test for function call_animal_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_nutrient_rqmts():
    """Unit test for function calc_avg_nutrient_rqmts in file routines/animal/pen.py"""
    pass


def test_calc_avg_stats():
    """Unit test for function calc_avg_stats in file routines/animal/pen.py"""
    pass


def test_calc_ration():
    """Unit test for function calc_ration in file routines/animal/pen.py"""
    pass


def test_calc_manure():
    """Unit test for function calc_manure in file routines/animal/pen.py"""
    pass


def test_reset_manure():
    """Unit test for function reset_manure in file routines/animal/pen.py"""
    pass


def test_calc_avg_growth():
    """Unit test for function calc_avg_growth in file routines/animal/pen.py"""
    pass


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/pen.py"""
    pass


def test_call_p_rqmts():
    """Unit test for function call_p_rqmts in file routines/animal/pen.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/pen.py"""
    pass


def test_set_up_new_animal():
    """Unit test for function set_up_new_animal in file routines/animal/pen.py"""
    pass


def test_clear():
    """Unit test for function clear in file routines/animal/pen.py"""
    pass


def test_set_nutrient_list():
    """Unit test for function set_nutrient_list in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_config():
    """Unit test for function set_config in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_default_nutrient_rqmts():
    """Unit test for function set_default_nutrient_rqmts in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_ration():
    """Unit test for function set_ration in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_intake():
    """Unit test for function set_p_intake in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_daily_p_update():
    """Unit test for function daily_p_update in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_calc_base_manure():
    """Unit test for function calc_base_manure in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_set_p_purchased():
    """Unit test for function set_p_purchased in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_update_pen_history():
    """Unit test for function update_pen_history in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_update_body_weight_history():
    """Unit test for function update_body_weight_history in file routines/animal/life_cycle/animal_base.py"""
    pass


def test_init_from_string():
    """Unit test for function init_from_string in file routines/animal/life_cycle/animal_events.py"""
    pass


def test_add_event():
    """Unit test for function add_event in file routines/animal/life_cycle/animal_events.py"""
    pass


def test___str__():
    """Unit test for function __str__ in file routines/animal/life_cycle/animal_events.py"""
    pass


@pytest.mark.parametrize(
    "events_list, event_descriptions, expected_days",
    [
        (
            [],
            ['dummy'],
            [-1]
        ),
        (
            [(1, 2, 'event1'), (3, 4, 'event2'),
             (5, 6, 'event1'), (7, 8, 'event3')],
            ['event1', 'event2', 'event3', 'event0'],
            [5, 3, 7, -1]
        )
    ],
)
def test_get_most_recent_date(events_list, event_descriptions, expected_days):
    """Unit test for function get_most_recent_date in file routines/animal/life_cycle/animal_events.py"""
    animal_event = AnimalEvents()
    for animal_age, simulation_day, event_description in events_list:
        animal_event.add_event(animal_age, simulation_day, event_description)

    for event_description, expected in zip(event_descriptions, expected_days):
        actual = animal_event.get_most_recent_date(event_description)
        assert actual == expected


def test_next_id():
    """Unit test for function next_id in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_init_animals():
    """Unit test for function init_animals in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_calves():
    """Unit test for function get_calves in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIs():
    """Unit test for function get_heiferIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIIs():
    """Unit test for function get_heiferIIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_heiferIIIs():
    """Unit test for function get_heiferIIIs in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_cows():
    """Unit test for function get_cows in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_get_replacement_cows():
    """Unit test for function get_replacement_cows in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_initialization_db_summary():
    """Unit test for function initialization_db_summary in file routines/animal/life_cycle/animal_initialization.py"""
    pass


def test_init_values():
    """Unit test for function init_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_assign_calf_values():
    """Unit test for function assign_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_get_calf_values():
    """Unit test for function get_calf_values in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/calf.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/calf.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/calf.py"""
    pass


def test_update_milk_production_history():
    """Unit test for function update_milk_production_history in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_param_value():
    """Unit test for function _determine_param_value in file routines/animal/life_cycle/cow.py"""
    pass


def test__milking_update():
    """Unit test for function _milking_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/cow.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/cow.py"""
    pass


def test_calc_daily_walking_dist():
    """Unit test for function calc_daily_walking_dist in file routines/animal/life_cycle/cow.py"""
    pass


def test_get_bw_change():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/cow.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__restart_estrus():
    """Unit test for function _restart_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__later_estrus():
    """Unit test for function _later_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/cow.py"""
    pass


def test__ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__tai_program_day_after_preg_check():
    """Unit test for function _tai_program_day_after_preg_check in file routines/animal/life_cycle/cow.py"""
    pass


def test__OvSynch56_update():
    """Unit test for function _OvSynch56_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__OvSynch48_update():
    """Unit test for function _OvSynch48_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__CoSynch72_update():
    """Unit test for function _CoSynch72_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__5dCoSynch_update():
    """Unit test for function _5dCoSynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__determine_presynch_program_day():
    """Unit test for function _determine_presynch_program_day in file routines/animal/life_cycle/cow.py"""
    pass


def test__presynch_update():
    """Unit test for function _presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__doubleovsynch_update():
    """Unit test for function _doubleovsynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__g6g_update():
    """Unit test for function _g6g_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__user_defined_presynch_update():
    """Unit test for function _user_defined_presynch_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__ed_tai_update():
    """Unit test for function _ed_tai_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__resynch_ed_tai():
    """Unit test for function _resynch_ed_tai in file routines/animal/life_cycle/cow.py"""
    pass


def test__open():
    """Unit test for function _open in file routines/animal/life_cycle/cow.py"""
    pass


def test__adjust_conception():
    """Unit test for function _adjust_conception in file routines/animal/life_cycle/cow.py"""
    pass


def test__preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__cull_update():
    """Unit test for function _cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_death_update():
    """Unit test for function death_update in file routines/animal/life_cycle/cow.py"""
    pass


def test__health_cull_update():
    """Unit test for function _health_cull_update in file routines/animal/life_cycle/cow.py"""
    pass


def test_get_heiferI_values():
    """Unit test for function get_heiferI_values in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_non_preg_bw_change():
    """Unit test for function get_non_preg_bw_change in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferI.py"""
    pass


def test_get_bw_change():
    """Unit test for function get_bw_change in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_init_values():
    """Unit test for function init_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_assign_heiferII_values():
    """Unit test for function assign_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferII_values():
    """Unit test for function get_heiferII_values in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_phosphorus_rqmts():
    """Unit test for function phosphorus_rqmts in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_estrus_day():
    """Unit test for function _determine_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__return_estrus():
    """Unit test for function _return_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__after_ai_estrus():
    """Unit test for function _after_ai_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__after_abortion_estrus():
    """Unit test for function _after_abortion_estrus in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__ed_update():
    """Unit test for function _ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_tai_program_day():
    """Unit test for function _determine_tai_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__tai_program_day_after_abortion():
    """Unit test for function _tai_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__5dCG2P_update():
    """Unit test for function _5dCG2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__5dCGP_update():
    """Unit test for function _5dCGP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__user_defined_update():
    """Unit test for function _user_defined_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__tai_update():
    """Unit test for function _tai_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_synch_ed_program_day():
    """Unit test for function _determine_synch_ed_program_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__determine_synch_ed_estrus_day():
    """Unit test for function _determine_synch_ed_estrus_day in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__synch_ed_program_day_after_abortion():
    """Unit test for function _synch_ed_program_day_after_abortion in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__2P_update():
    """Unit test for function _2P_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__CP_update():
    """Unit test for function _CP_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__synch_ed_update():
    """Unit test for function _synch_ed_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__open():
    """Unit test for function _open in file routines/animal/life_cycle/heiferII.py"""
    pass


def test__preg_update():
    """Unit test for function _preg_update in file routines/animal/life_cycle/heiferII.py"""
    pass


def test_get_heiferIII_values():
    """Unit test for function get_heiferIII_values in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_calc_nutrient_rqmts():
    """Unit test for function calc_nutrient_rqmts in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_calc_manure_excretion():
    """Unit test for function calc_manure_excretion in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_update():
    """Unit test for function update in file routines/animal/life_cycle/heiferIII.py"""
    pass


def test_initialize_herd():
    """Unit test for function initialize_herd in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_daily_update():
    """Unit test for function daily_update in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test__calc_average():
    """Unit test for function _calc_average in file routines/animal/life_cycle/life_cycle.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/calf_manure_excretion.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/dry_cow_manure_excretion.py"""
    pass


def test_phosphorus_excreted():
    """Unit test for function phosphorus_excreted in file routines/animal/manure/general_manure.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/growing_heifer_manure_excretion.py"""
    pass


def test_manure_calculations():
    """Unit test for function manure_calculations in file routines/animal/manure/lactating_cow_manure_excretion.py"""
    pass


def test_calc_rqmts():
    """Unit test for function optimize in file routines/animal/ration/animal_requirements.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/calf_ration.py"""
    pass


def test_calc_requirements():
    """Unit test for function calc_requirements in file routines/animal/ration/calf_ration.py"""
    pass


def test_set_globals():
    """Unit test for function set_globals in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_list_reconfig():
    """Unit test for function list_reconfig in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_objective():
    """Unit test for function objective in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEmact_constraint():
    """Unit test for function NEmact_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEl_constraint():
    """Unit test for function NEl_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NEgact_constraint():
    """Unit test for function NEgact_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_calcium_constraint():
    """Unit test for function calcium_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_phosphorus_constraint():
    """Unit test for function phosphorus_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_protien_constraint():
    """Unit test for function protien_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NDF_constraint_1():
    """Unit test for function NDF_constraint_1 in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_NDF_constraint_2():
    """Unit test for function NDF_constraint_2 in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_forage_NDF_constraint():
    """Unit test for function forage_NDF_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_fat_constraint():
    """Unit test for function fat_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_DMI_constraint():
    """Unit test for function DMI_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_energy_req_limit_constraint():
    """Unit test for function energy_req_limit_constraint in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_get_ration_vals():
    """Unit test for function get_ration_vals in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/cow_ration_NLP.py"""
    pass


def test_calc_rqmts():
    """Unit test for function calc_rqmts in file routines/animal/ration/cow_requirements.py"""
    pass


def test_energy_activity_rqmts():
    """Unit test for function energy_activity_rqmts in file routines/animal/ration/cow_requirements.py"""
    pass


def test_optimize():
    """Unit test for function optimize in file routines/animal/ration/growing_heifer_ration.py"""
    pass


def test_calculate_rqmts():
    """Unit test for function calculate_rqmts in file routines/animal/ration/growing_heifer_ration.py"""
    pass


def test_get_ration():
    """Unit test for function get_ration in file routines/animal/ration/hardcoded_ration.py"""
    pass


def test_get_nutrient_rqmts():
    """Unit test for function get_nutrient_rqmts in file routines/animal/ration/hardcoded_ration.py"""
    pass


def test_optimization():
    """Unit test for function optimization in file routines/animal/ration/ration_driver.py"""
    pass


def test_ration_formulation():
    """Unit test for function ration_formulation in file routines/animal/ration/ration_driver.py"""
    pass


def test_ration_report():
    """Unit test for function ration_report in file routines/animal/ration/ration_driver.py"""
    pass


def test_set_requirements():
    """Unit test for function set_requirements in file routines/animal/ration/ration_driver.py"""
    pass


def test_feed_nutrients():
    """Unit test for function feed_nutrients in file routines/animal/ration/ration_driver.py"""
    pass
