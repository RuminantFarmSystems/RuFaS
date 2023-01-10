"""
RUFAS: Ruminant Farm Systems Model
File name: test_animal.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import pytest

from mock.mock import MagicMock,mock_open, patch
from pytest_mock.plugin import MockerFixture

from RUFAS.routines.animal.ration.ration_NLP import list_reconfig
from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents
from RUFAS.simulation_engine import SimulationEngine

@pytest.fixture
def patch_simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    """Returns a mocked SimulationEngine"""
    mocker.patch(
        "RUFAS.simulation_engine.SimulationEngine._initialize_simulation")
    # mocker.patch("RUFAS.simulation_engine.SimulationEngine._advance_time")
    sim_eng = SimulationEngine("dummy_path")
    sim_eng.config = MagicMock()
    sim_eng.weather = MagicMock()
    sim_eng.time = MagicMock()
    sim_eng.state = MagicMock()
    sim_eng.output = MagicMock()

    return sim_eng


from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
@pytest.fixture
def patch_animal_object(mocker:MockerFixture)->AnimalBase:
    """returns a mocked AnimalBase"""
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.__init__")
    ####mocker.patch(
    ####    "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.update_body_weight_history")
    #animobj = AnimalBase()
    ### note: init didn't work with the below
    animobj = AnimalBase.__init__(
        id = MagicMock(),
        breed = MagicMock(),
        birth_date =  MagicMock(),
        days_born = MagicMock(),
        semen_used =  MagicMock(),
        
        body_weight = MagicMock(),
        body_weight_history = [],
        pen_history = MagicMock()
        )
    return animobj


# @pytest.fixture
# def patch_AnimalBase() -> AnimalBase:
#     patch_AnimalBase_obj = AnimalBase(MagicMock())
#     return patch_AnimalBase_obj

# from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
# @pytest.fixture
# def patch_animal_object2(mocker:MockerFixture)->AnimalBase:
#     """returns a mocked AnimalBase"""
#     # mocker.patch(
#     #     "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.__init__")
#     mocker.patch(
#         "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.update_body_weight_history")
#     animobj = patch_AnimalBase
#     return animobj


# from RUFAS.routines.animal.life_cycle.animal_base import BodyWeightHistory
# @pytest.fixture
# def patch_BodyWeightHistory(mocker:MockerFixture)->BodyWeightHistory:
#     """returns a mocked BodyWeightHistory"""
#     mocker.patch(
#         "RUFAS.routines.animal.life_cycle.animal_base.BodyWeightHistory.__init__")
#     bwhistobj = BodyWeightHistory()
#     bwhistobj.simulation_day = patch_simulation_engine.state.animal_management.simulation_day
#     bwhistobj.days_born = patch_animal_object.days_born
#     bwhistobj.body_weight = patch_animal_object.body_weight
    
#     return bwhistobj

from RUFAS.routines.animal.life_cycle.animal_base import PenHistory
@pytest.fixture
def patch_PenHistory(mocker:MockerFixture)->PenHistory:
    """returns a mocked PenHistory object"""
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.PenHistory.__init__")
    penhistobj = PenHistory()
    penhistobj.start_date = 1
    penhistobj.end_date = 1
    penhistobj.pen = 3
    penhistobj.classes_in_pen = ['LAC_COW']
    
    return penhistobj


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


def test_update_pen_history(
        patch_animal_object: AnimalBase, 
        patch_simulation_engine: SimulationEngine)-> None:
    """Unit test for function update_pen_history in file routines/animal/life_cycle/animal_base.py"""
    patch_simulation_engine.state.animal_management.simulation_day = 1
    patch_animal_object.days_born = 200
    patch_animal_object.body_weight = 600
    patch_simulation_engine._advance_time(True)
    curr_pen = 5
    classes_in_pen = 'LAC_COW'
    curr_day = patch_simulation_engine.state.animal_management.simulation_day
    # update hist with new vals, using the time and the obj itself
    patch_animal_object.update_pen_history(patch_animal_object.pen_history, \
        curr_pen,
        curr_day,
        classes_in_pen
        )
    
    expected = [3, 2, 'LAC_COW']
    actual = patch_animal_object.pen_history[-1]
    #last_pen = patch_animal_object.pen_history[-1].pen
    #assert actual == expected
    ##### assert patch_animal_object.pen_history[-1].end_date == curr_day
    ##### assert patch_animal_object.pen_history[-1].classes_in_pen == ['LAC_COW']
 
    # additional 
    # assert that the self is an animal object
    # assert that the curr_day is a date
    # assert that curr_pen is a valid pen
    # assert that the classes_in_pen is a list
    # assert that curr_day is current day in simulation
    # assert that the classes in the pen match


def test_update_body_weight_history(
        patch_animal_object: AnimalBase, 
        patch_simulation_engine: SimulationEngine,
        mocker:MockerFixture)-> None:
    mocker.patch(
        "RUFAS.simulation_engine.SimulationEngine._advance_time")
    mocker.patch(
        "RUFAS.routines.animal.life_cycle.animal_base.AnimalBase.update_body_weight_history")
    
    # """Unit test for function update_body_weight_history in file routines/animal/life_cycle/animal_base.py
    # using patches generated at start"""

    # Simple example 1 - gain 1kg on second day of sim, age = 200 days
    # patch_simulation_engine.state.animal_management.simulation_day = 1
    # assert patch_simulation_engine.state.animal_management.simulation_day == 1
    patch_animal_object.simulation_day = 1
    assert patch_animal_object.simulation_day == 1
    patch_animal_object.days_born = 200
    assert patch_animal_object.days_born == 200
    patch_animal_object.body_weight = 600
    assert patch_animal_object.body_weight == 600
    ############## patch_simulation_engine._advance_time(True)
    ############## assert patch_simulation_engine.state.animal_management.simulation_day == 2
    patch_animal_object.body_weight = 601
    assert patch_animal_object.body_weight == 601
    patch_animal_object.body_weight_history = []
    # update hist with new vals, using the time and the obj itself
    ####patch_animal_object.update_body_weight_history(patch_animal_object, \
    ####    patch_simulation_engine.state.animal_management.simulation_day)
    # patch_animal_object.update_body_weight_history(
    #     patch_simulation_engine.state.animal_management.simulation_day)
    patch_animal_object.update_body_weight_history(
        patch_animal_object.simulation_day)
 
    # the expected value, being second day of sim and 1 day older, 1kg heavier
    bwhist_expected = [1, 200, 601]
    bwhist_actual = list((patch_animal_object.body_weight_history[-1].simulation_day,\
        patch_animal_object.body_weight_history[-1].days_born,\
        patch_animal_object.body_weight_history[-1].body_weight))
    assert patch_animal_object.body_weight_history[-1].simulation_day == 1
    # assert patch_animal_object.body_weight_history[-1].days_born == 200
    # assert patch_animal_object.body_weight_history[-1].body_weight == 601
    
    # assert bwhist_actual == bwhist_expected
    #assert len(bwhist_actual) == 0 # this is wrong, but to check that it is printing an empty list


    ##### assert patch_animal_object.body_weight_history[-1].days_born[0] > 0
    # assert bwhist_actual == bwhist_expected


# def test_update_body_weight_history_v2(patch_simulation_engine: SimulationEngine, patch_animal_object: AnimalBase):
#     """Unit test for function update_body_weight_history in file routines/animal/life_cycle/animal_base.py
#     using patches generated at start"""
#     #animalexample = AnimalBase(1,1)
#     # Case 1 - gain 1kg on second day of sim, age = 200 days
#     patch_simulation_engine.state.animal_management.simulation_day = 1
#     patch_animal_object.days_born = 200
#     patch_animal_object.body_weight = 600
#     patch_simulation_engine._advance_time(True)
#     patch_animal_object.body_weight = 601
#     # update hist with new vals, using the time and the obj itself
#     patch_animal_object.update_body_weight_history(patch_animal_object, \
#         patch_simulation_engine.state.animal_management.simulation_day)
#     # the expected value, being second day of sim and 1 day older, ikg heavier
#     bwhist_expected = [2, 201, 601]
#     bwhist_actual = patch_animal_object.body_weight_history[-1]
#     assert bwhist_actual == bwhist_expected


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
    result = list_reconfig([1,2,3,4])
    expected = [1,1,1,2,2,2,3,3,3,4,4,4]
    assert result == expected
    result2 = list_reconfig(['1','2','3','4'])
    expected2 = ['1','1','1','2','2','2','3','3','3','4','4','4']
    assert result2 == expected2


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
