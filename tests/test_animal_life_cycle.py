import collections
from typing import Dict
from typing import List
from typing import Type

import pytest
from pytest import approx
from pytest import fixture
from pytest_mock import MockerFixture

from RUFAS.config import Config
from RUFAS.routines.animal.animal_typed_dicts import AnimalConfigTypedDict
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.animal_constants import ENTER_HERD
from RUFAS.routines.animal.life_cycle.animal_constants import INIT_HERD
from RUFAS.routines.animal.life_cycle.animal_constants import LOW_PROD_CULL
from RUFAS.routines.animal.life_cycle.animal_data import AnimalData
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.life_cycle import GenericAnimal
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.pen import Pen


@fixture
def life_cycle_manager(mocker: MockerFixture) -> LifeCycleManager:
    return LifeCycleManager(data=mocker.MagicMock(autospec=AnimalConfigTypedDict))


@pytest.mark.parametrize(
    'user_input_calving_interval, custom_avg_CI, cow_avg_CI',
    [
        (True, 400.0, -1.0),
        (False, -1.0, 500.0)
    ]
)
def test_set_avg_CI(mocker: MockerFixture,
                    life_cycle_manager: LifeCycleManager,
                    user_input_calving_interval: bool,
                    custom_avg_CI: float,
                    cow_avg_CI: float) -> None:
    """Unit test for function _set_avg_CI() in file life_cycle.py"""
    # Arrange
    mock_animal_config = {
        'use_input_calving_interval': user_input_calving_interval,
        'calving_interval': custom_avg_CI
    }
    life_cycle_manager.animal_config = mock_animal_config

    mock_init_db_summary = {
        'cow_avg_CI': cow_avg_CI
    }
    mock_animal_data = mocker.MagicMock(autospec=AnimalData)
    mock_animal_data.initialization_db_summary.return_value = mock_init_db_summary
    life_cycle_manager.animal_data = mock_animal_data
    spy_set_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')

    # Assert before
    assert life_cycle_manager.avg_CI == approx(0.0)

    # Act
    life_cycle_manager._set_avg_CI()

    # Assert after
    spy_set_avg_CI.assert_called_once()
    if user_input_calving_interval:
        assert life_cycle_manager.avg_CI == approx(custom_avg_CI)
    else:
        assert life_cycle_manager.avg_CI == approx(cow_avg_CI)
        mock_animal_data.initialization_db_summary.assert_called_once()


@pytest.mark.parametrize(
    'animal_type',
    [Calf, HeiferI, HeiferII, HeiferIII, Cow])
def test_get_animals(mocker: MockerFixture,
                     life_cycle_manager: LifeCycleManager,
                     animal_type: Type[GenericAnimal]) -> None:
    """Unit test for function _get_animals() in file life_cycle.py"""
    # Arrange
    animal_num = 10
    breed = 'HO'
    days_born = 50
    mock_animals = []
    for i in range(animal_num):
        mock_new_animal = mocker.MagicMock(autospec=animal_type)
        mock_new_animal.breed = breed
        mock_new_animal.days_born = days_born
        mock_animals.append(mock_new_animal)
    mock_animal_data = mocker.MagicMock(autospec=AnimalData)

    animal_getter_by_animal_type = {
        Calf: mock_animal_data.get_calves,
        HeiferI: mock_animal_data.get_heiferIs,
        HeiferII: mock_animal_data.get_heiferIIs,
        HeiferIII: mock_animal_data.get_heiferIIIs,
        Cow: mock_animal_data.get_cows
    }
    animal_getter_by_animal_type[animal_type].return_value = mock_animals

    spy_get_animals = mocker.spy(life_cycle_manager, '_get_animals')
    life_cycle_manager.animal_data = mock_animal_data

    # Act
    animals = life_cycle_manager._get_animals(animal_type)

    # Assert
    assert len(animals) == animal_num
    for animal in animals:
        assert animal.breed == breed
        animal.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_animals.assert_called_once_with(animal_type)
    animal_getter_by_animal_type[animal_type].assert_called_once()


def test_initialize_herd(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function initialize_herd() in file life_cycle.py"""
    mock_config = mocker.MagicMock(autospec=Config)
    breed = 'HO'
    herd_data = {
        'calf_num': 80,
        'heiferI_num': 440,
        'heiferII_num': 380,
        'heiferIII_num_springers': 50,
        'cow_num': 1000,
        'replace_num': 5000,
        'herd_num': 1000,
        'breed': breed,
    }

    life_cycle_manager.animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)

    mock_animal_data = mocker.MagicMock(autospec=AnimalData)
    mock_replacement_cows = [mocker.MagicMock(autospec=Cow) for _ in range(herd_data['replace_num'])]
    mock_animal_data.get_replacement_cows.return_value = mock_replacement_cows
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalData',
                 return_value=mock_animal_data)

    patch_set_avg_CI = mocker.patch.object(life_cycle_manager, '_set_avg_CI')
    patch_get_animals = mocker.patch.object(life_cycle_manager, '_get_animals')

    results = life_cycle_manager.initialize_herd(mock_config, herd_data, False, False, False)

    assert life_cycle_manager.herd_num == herd_data['herd_num']
    patch_set_avg_CI.assert_called_once()
    assert patch_get_animals.call_count == 5
    assert patch_get_animals.call_args_list[0] == mocker.call(Calf)
    assert patch_get_animals.call_args_list[1] == mocker.call(HeiferI)
    assert patch_get_animals.call_args_list[2] == mocker.call(HeiferII)
    assert patch_get_animals.call_args_list[3] == mocker.call(HeiferIII)
    assert patch_get_animals.call_args_list[4] == mocker.call(Cow)
    mock_animal_data.get_replacement_cows.assert_called_once_with()
    assert life_cycle_manager.replacement_market == mock_replacement_cows
    assert len(results) == 5


def test_reset_parity(life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _reset_parity in file life_cycle.py"""
    parities = life_cycle_manager.num_cow_for_parity
    preg_times = life_cycle_manager.avg_calving_to_preg_time
    count_per_parity = 10
    avg_calving_to_preg_time_default = 10.0
    avg_age_for_parity_default = 200.0
    avg_age_for_calving_default = 100.0
    cow_num = len(parities) * count_per_parity
    for parity in parities:
        parities[parity] = count_per_parity
        preg_times[parity] = avg_calving_to_preg_time_default
        life_cycle_manager.percent_cow_for_parity[parity] = \
            count_per_parity * 100 / cow_num
        life_cycle_manager.avg_age_for_parity[parity] = avg_age_for_parity_default
        life_cycle_manager.avg_age_for_calving[parity] = avg_age_for_calving_default

    life_cycle_manager._reset_parity()

    for parity in parities:
        assert parities[parity] == 0
        assert preg_times[parity] == 0
        assert life_cycle_manager.percent_cow_for_parity[parity] == approx(0.0)
        assert life_cycle_manager.avg_age_for_parity[parity] == approx(0.0)
        assert life_cycle_manager.avg_age_for_calving[parity] == approx(0.0)


def test_reset_cull_reason_stats(life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _reset_cull_reason_stats in file life_cycle.py"""
    stats = life_cycle_manager.cull_reason_stats
    num_reasons = len(stats)
    count_per_reason = 10
    life_cycle_manager.culled_cow_num = num_reasons * count_per_reason
    for cull_reason in stats:
        stats[cull_reason] = count_per_reason
        life_cycle_manager.cull_reason_stats_percent[cull_reason] = \
            count_per_reason * 100.0 / life_cycle_manager.culled_cow_num

    life_cycle_manager._reset_cull_reason_stats()

    for cull_reason in stats:
        assert stats[cull_reason] == 0
        assert life_cycle_manager.cull_reason_stats_percent[cull_reason] == approx(0.0)


def test_convert_calf_to_heiferI(mocker: MockerFixture) -> None:
    """Unit test for function _convert_calf_to_heiferI in file life_cycle.py"""
    calf_body_weight_history = [10.0, 20.0]
    calf_pen_history = [mocker.MagicMock(autospec=Pen) for _ in range(2)]

    mock_calf = mocker.MagicMock(autospec=Calf)
    mock_calf.body_weight_history = calf_body_weight_history
    mock_calf.pen_history = calf_pen_history

    mock_calf_vals = mocker.MagicMock(autospec=Dict)
    mock_calf.get_calf_values.return_value = mock_calf_vals

    heiferIs: List[HeiferI] = []
    mock_new_heiferI = mocker.MagicMock(autospec=HeiferI)
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.HeiferI',
                 return_value=mock_new_heiferI)
    LifeCycleManager._convert_calf_to_heiferI(mock_calf, heiferIs)

    mock_calf_vals.update.assert_called_once_with({
        'body_weight_history': calf_body_weight_history,
        'pen_history': calf_pen_history
    })
    assert len(heiferIs) == 1
    assert heiferIs[0] == mock_new_heiferI  # check identity


def test_evaluate_calves_for_weaning(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _evaluate_calves_for_weaning in file life_cycle.py"""
    sim_day = 10
    mock_weaned_calf = mocker.MagicMock(autospec=Calf)
    mock_weaned_calf.update.return_value = True
    patch_convert_calf_to_heiferI = mocker.patch.object(life_cycle_manager, '_convert_calf_to_heiferI')

    mock_matured_calf = mocker.MagicMock(autospec=Calf)
    mock_matured_calf.update.return_value = False
    mock_matured_calf.mature_body_weight = mature_body_weight = 200.0

    mock_calves: List[Calf] = [mock_weaned_calf, mock_matured_calf]
    heiferIs: List[HeiferI] = []
    life_cycle_manager.calf_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    new_total_animal_num = life_cycle_manager._evaluate_calves_for_weaning(sim_day, mock_calves, heiferIs,
                                                                           total_animal_num)

    mock_weaned_calf.update.assert_called_once_with(sim_day)
    patch_convert_calf_to_heiferI.assert_called_once_with(mock_weaned_calf, heiferIs)

    mock_matured_calf.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.calf_num == 1

    assert len(mock_calves) == 1
    assert mock_calves[0] == mock_matured_calf
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)


def test_convert_heiferI_to_heiferII(mocker: MockerFixture) -> None:
    """Unit test for function _convert_heiferI_to_heiferII in file life_cycle.py"""
    heiferI_body_weight_history = [30.0, 40.0]
    heiferI_pen_history = [mocker.MagicMock(autospec=Pen) for _ in range(2)]

    mock_heiferI = mocker.MagicMock(autospec=HeiferI)
    mock_heiferI.body_weight_history = heiferI_body_weight_history
    mock_heiferI.pen_history = heiferI_pen_history

    mock_heiferI_vals = mocker.MagicMock(autospec=Dict)
    mock_heiferI.get_heiferI_values.return_value = mock_heiferI_vals

    heiferIIs: List[HeiferII] = []
    mock_new_heiferII = mocker.MagicMock(autospec=HeiferII)
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.HeiferII',
                 return_value=mock_new_heiferII)

    heifer_repro_method = 'TAI'
    heifer_TAI_protocol = 'd5CG2P'
    heifer_synchedED_protocol = '2P'
    animal_base_config = {
        "heifer_repro_method": heifer_repro_method,
        "heifer_repro_programs": {
            "heifer_TAI_protocol": heifer_TAI_protocol,
            "heifer_synchED_protocol": heifer_synchedED_protocol
        }
    }
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.config', animal_base_config)

    LifeCycleManager._convert_heiferI_to_heiferII(mock_heiferI, heiferIIs)

    assert mock_heiferI_vals.update.mock_calls == [
        mocker.call({
            'body_weight_history': heiferI_body_weight_history,
            'pen_history': heiferI_pen_history
        }),
        mocker.call(repro_program=heifer_repro_method),
        mocker.call(tai_method_h=heifer_TAI_protocol),
        mocker.call(synch_ed_method_h=heifer_synchedED_protocol)
    ]

    assert len(heiferIIs) == 1
    assert heiferIIs[0] == mock_new_heiferII  # check identity


def test_evaluate_heiferIs_for_transitioning_to_heiferIIs(mocker: MockerFixture,
                                                          life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _evaluate_heiferIs_for_transitioning_to_heiferIIs in file life_cycle.py"""
    sim_day = 100
    mock_heiferI_second_stage = mocker.MagicMock(autospec=HeiferI)
    mock_heiferI_second_stage.update.return_value = True
    patch_convert_heiferI_to_heiferII = mocker.patch.object(life_cycle_manager,
                                                            '_convert_heiferI_to_heiferII')

    mock_matured_heiferI = mocker.MagicMock(autospec=HeiferI)
    mock_matured_heiferI.update.return_value = False
    mock_matured_heiferI.mature_body_weight = mature_body_weight = 400.0

    mock_heiferIs: List[HeiferI] = [mock_heiferI_second_stage, mock_matured_heiferI]
    mock_heiferIIs: List[HeiferII] = []
    life_cycle_manager.heiferI_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    new_total_animal_num = life_cycle_manager._evaluate_heiferIs_for_transitioning_to_heiferIIs(sim_day, mock_heiferIs,
                                                                                                mock_heiferIIs,
                                                                                                total_animal_num)

    mock_heiferI_second_stage.update.assert_called_once_with(sim_day)
    patch_convert_heiferI_to_heiferII.assert_called_once_with(mock_heiferI_second_stage, mock_heiferIIs)

    mock_matured_heiferI.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.heiferI_num == 1

    assert len(mock_heiferIs) == 1
    assert mock_heiferIs[0] == mock_matured_heiferI
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)


def test_convert_heiferII_to_heiferIII(mocker: MockerFixture) -> None:
    """Unit test for function _convert_heiferII_to_heiferIII in file life_cycle.py"""
    heiferII_body_weight_history = [50.0, 60.0]
    heiferII_pen_history = [mocker.MagicMock(autospec=Pen) for _ in range(2)]
    heiferII_conceptus_weight = 10.0
    heiferII_calf_birth_weight = 20.0

    mock_heiferII = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII.body_weight_history = heiferII_body_weight_history
    mock_heiferII.pen_history = heiferII_pen_history
    mock_heiferII.conceptus_weight = heiferII_conceptus_weight
    mock_heiferII.calf_birth_weight = heiferII_calf_birth_weight

    mock_heiferII_vals = mocker.MagicMock(autospec=Dict)
    mock_heiferII.get_heiferII_values.return_value = mock_heiferII_vals

    heiferIIIs: List[HeiferIII] = []
    mock_new_heiferIII = mocker.MagicMock(autospec=HeiferIII)
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.HeiferIII',
                 return_value=mock_new_heiferIII)
    LifeCycleManager._convert_heiferII_to_heiferIII(mock_heiferII, heiferIIIs)

    mock_heiferII_vals.update.assert_called_once_with({
        'body_weight_history': heiferII_body_weight_history,
        'pen_history': heiferII_pen_history,
        'conceptus_weight': heiferII_conceptus_weight,
        'calf_birth_weight': heiferII_calf_birth_weight
    })
    assert len(heiferIIIs) == 1
    assert heiferIIIs[0] == mock_new_heiferIII  # check identity


def test_extract_repro_stats_from_heiferII(mocker: MockerFixture,
                                           life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _extract_repro_stats_from_heiferII in file life_cycle.py"""
    mock_data = {
        'CIDR_count': 10,
        'GnRH_injections': 20,
        'PGF_injections': 30,
        'preg_diagnoses': 40,
        'semen_num': 50,
        'AI_times': 60,
        'ED_days': 70
    }
    mock_heiferII = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII.CIDR_count = mock_data['CIDR_count']
    mock_heiferII.GnRH_injections = mock_data['GnRH_injections']
    mock_heiferII.PGF_injections = mock_data['PGF_injections']
    mock_heiferII.preg_diagnoses = mock_data['preg_diagnoses']
    mock_heiferII.semen_num = mock_data['semen_num']
    mock_heiferII.AI_times = mock_data['AI_times']
    mock_heiferII.ED_days = mock_data['ED_days']

    spy_extract_repro_stats = mocker.spy(life_cycle_manager, '_extract_repro_stats_from_heiferII')

    # Before
    assert life_cycle_manager.CIDR_count == 0
    assert life_cycle_manager.GnRH_injection_num_h == 0
    assert life_cycle_manager.PGF_injection_num_h == 0
    assert life_cycle_manager.preg_check_num_h == 0
    assert life_cycle_manager.semen_num_h == 0
    assert life_cycle_manager.ai_num_h == 0
    assert life_cycle_manager.ed_period_h == 0

    life_cycle_manager._extract_repro_stats_from_heiferII(mock_heiferII)

    # After
    spy_extract_repro_stats.assert_called_once_with(mock_heiferII)
    # assert life_cycle_manager.CIDR_count == mock_data['CIDR_count']
    assert life_cycle_manager.GnRH_injection_num_h == mock_data['GnRH_injections']
    assert life_cycle_manager.PGF_injection_num_h == mock_data['PGF_injections']
    assert life_cycle_manager.preg_check_num_h == mock_data['preg_diagnoses']
    assert life_cycle_manager.semen_num_h == mock_data['semen_num']
    assert life_cycle_manager.ai_num_h == mock_data['AI_times']
    assert life_cycle_manager.ed_period_h == mock_data['ED_days']


def test_remain_heiferII(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _remain_heiferII in file life_cycle.py"""
    # Arrange
    mock_heiferII = mocker.MagicMock(autospec=HeiferII)
    total_animal_num = 10
    life_cycle_manager.avg_mature_body_weight = 20.0
    mock_heiferII.mature_body_weight = 42.0

    preg_heifer_num = 10
    life_cycle_manager.avg_breeding_to_preg_time = 20.0
    mock_heiferII.breeding_to_preg_time = 42.0

    # Assert before
    assert life_cycle_manager.heiferII_num == 0
    assert life_cycle_manager.avg_mature_body_weight == approx(20.0)
    assert life_cycle_manager.avg_breeding_to_preg_time == approx(20.0)

    # Act
    result = life_cycle_manager._remain_heiferII(mock_heiferII, total_animal_num, preg_heifer_num)
    new_total_animal_num, new_preg_heifer_num = result

    # Assert after
    assert life_cycle_manager.heiferII_num == 1
    assert new_total_animal_num == 11
    assert life_cycle_manager.avg_mature_body_weight == approx(22.0)
    assert new_preg_heifer_num == 11
    assert life_cycle_manager.avg_breeding_to_preg_time == approx(22.0)


def test_evaluate_heiferIIs_for_transitioning_to_heiferIIIs(mocker: MockerFixture,
                                                            life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _evaluate_heiferIIs_for_transitioning_to_heiferIIIs in file life_cycle.py"""
    # Set up
    sim_day = 300
    mock_heiferII_cull_stage = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII_cull_stage.update.return_value = [True, False]  # cull_stage = True, third_stage = False
    mock_heiferII_cull_stage.days_born = 100
    life_cycle_manager.culled_heifer_num = 0
    life_cycle_manager.avg_heifer_culling_age = 0.0
    life_cycle_manager.culled_heifers = []

    mock_heiferII_third_stage = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII_third_stage.update.return_value = [False, True]  # cull_stage = False, third_stage = True
    patch_convert_heiferII_to_heiferIII = mocker.patch.object(life_cycle_manager,
                                                              '_convert_heiferII_to_heiferIII')

    mock_heiferII_pregnant_stage = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII_pregnant_stage.update.return_value = [False, False]  # cull_stage = False, third_stage = False
    patch_remain_heiferII = mocker.patch.object(life_cycle_manager,
                                                '_remain_heiferII')
    patch_remain_heiferII.return_value = (1, 1)  # new_total_animal_num = 1, new_preg_heifer_num = 1
    total_animal_num = 0
    preg_heifer_num = 0

    mock_heiferIIs: List[HeiferIII] = [mock_heiferII_cull_stage,
                                       mock_heiferII_third_stage,
                                       mock_heiferII_pregnant_stage]
    mock_heiferIIIs: List[HeiferIII] = []

    # Before
    assert life_cycle_manager.culled_heifer_num == 0
    assert life_cycle_manager.avg_heifer_culling_age == approx(0.0)
    assert len(life_cycle_manager.culled_heifers) == 0

    # Act
    result = life_cycle_manager._evaluate_heiferIIs_for_transitioning_to_heiferIIIs(sim_day, mock_heiferIIs,
                                                                                    mock_heiferIIIs, preg_heifer_num,
                                                                                    total_animal_num)
    new_total_animal_num, new_preg_heifer_num = result

    # After
    assert life_cycle_manager.culled_heifer_num == 1
    assert life_cycle_manager.avg_heifer_culling_age == approx(100.0)
    assert len(life_cycle_manager.culled_heifers) == 1
    assert life_cycle_manager.culled_heifers[0] == mock_heiferII_cull_stage
    mock_heiferII_cull_stage.update.assert_called_once_with(sim_day)

    patch_convert_heiferII_to_heiferIII.assert_called_once_with(mock_heiferII_third_stage, mock_heiferIIIs)

    patch_remain_heiferII.assert_called_once_with(mock_heiferII_pregnant_stage,
                                                  total_animal_num, preg_heifer_num)
    assert new_total_animal_num == 1
    assert new_preg_heifer_num == 1
    assert len(mock_heiferIIs) == 1
    assert mock_heiferIIs[0] == mock_heiferII_pregnant_stage


def test_move_heiferIII_to_cow_stage(mocker: MockerFixture) -> None:
    """Unit test for function _convert_heiferIII_to_cow in file life_cycle.py"""
    # Arrange
    heiferIII_body_weight_history = [30.0, 40.0]
    heiferIII_pen_history = [mocker.MagicMock(autospec=Pen) for _ in range(2)]
    heiferIII_conceptus_weight = 10.0
    heiferIII_calf_birth_weight = 20.0

    mock_heiferIII = mocker.MagicMock(autospec=HeiferIII)
    mock_heiferIII.body_weight_history = heiferIII_body_weight_history
    mock_heiferIII.pen_history = heiferIII_pen_history
    mock_heiferIII.conceptus_weight = heiferIII_conceptus_weight
    mock_heiferIII.calf_birth_weight = heiferIII_calf_birth_weight

    mock_heiferIII_vals = mocker.MagicMock(autospec=Dict)
    mock_heiferIII.get_heiferIII_values.return_value = mock_heiferIII_vals

    cows: List[Cow] = []
    mock_new_cow = mocker.MagicMock(autospec=Cow)
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.Cow',
                 return_value=mock_new_cow)

    cow_repro_method = 'TAI'
    cow_presynch_protocol = 'Double OvSynch'
    cow_TAI_protocol = 'OvSynch 56'
    cow_resynch_protocol = 'TAIafterPD'
    animal_base_config = {
        "cow_repro_method": cow_repro_method,
        "cow_repro_programs": {
            "cow_presynch_protocol": cow_presynch_protocol,
            "cow_TAI_protocol": cow_TAI_protocol,
            "cow_resynch_protocol": cow_resynch_protocol
        }
    }
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.config', animal_base_config)

    # Act
    LifeCycleManager._convert_heiferIII_to_cow(mock_heiferIII, cows)

    # Assert
    assert mock_heiferIII_vals.update.mock_calls == [
        mocker.call({
            'body_weight_history': heiferIII_body_weight_history,
            'pen_history': heiferIII_pen_history,
            'conceptus_weight': heiferIII_conceptus_weight,
            'calf_birth_weight': heiferIII_calf_birth_weight
        }),
        mocker.call(repro_program=cow_repro_method),
        mocker.call(presynch_method=cow_presynch_protocol),
        mocker.call(tai_method_c=cow_TAI_protocol),
        mocker.call(resynch_method=cow_resynch_protocol)
    ]

    assert len(cows) == 1
    assert cows[0] == mock_new_cow  # check identity


def test_transition_heiferIII_to_cow(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _evaluate_heiferIIIs_for_transitioning_to_cows in file life_cycle.py"""
    sim_day = 400
    mock_heiferIII_cow_stage = mocker.MagicMock(autospec=HeiferIII)
    mock_heiferIII_cow_stage.update.return_value = True
    patch_convert_heiferIII_to_cow = mocker.patch.object(life_cycle_manager,
                                                         '_convert_heiferIII_to_cow')

    mock_matured_heiferIII = mocker.MagicMock(autospec=HeiferIII)
    mock_matured_heiferIII.update.return_value = False
    mock_matured_heiferIII.mature_body_weight = mature_body_weight = 600.0

    mock_heiferIIIs: List[HeiferIII] = [mock_heiferIII_cow_stage, mock_matured_heiferIII]
    mock_cows: List[Cow] = []
    life_cycle_manager.heiferIII_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    # Assert before
    assert life_cycle_manager.heiferIII_num == 0
    assert total_animal_num == 0
    assert life_cycle_manager.avg_mature_body_weight == approx(0.0)

    # Act
    new_total_animal_num = life_cycle_manager._evaluate_heiferIIIs_for_transitioning_to_cows(sim_day, mock_heiferIIIs,
                                                                                             mock_cows,
                                                                                             total_animal_num)

    # Assert after
    mock_heiferIII_cow_stage.update.assert_called_once_with(sim_day)
    patch_convert_heiferIII_to_cow.assert_called_once_with(mock_heiferIII_cow_stage, mock_cows)

    mock_matured_heiferIII.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.heiferIII_num == 1

    assert len(mock_heiferIIIs) == 1
    assert mock_heiferIIIs[0] == mock_matured_heiferIII
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)


def test_check_if_heifers_need_to_be_sold(mocker: MockerFixture,
                                          life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _check_if_heifers_need_to_be_sold in file life_cycle.py"""

    # Case 1: len(heiferIIIs) + len(cows) > herd_num * 1.03 AND len(heiferIIIs) > 0
    # Arrange
    life_cycle_manager.herd_num = 100
    mock_heiferIIIs: List[HeiferIII] = []
    for i in range(55):
        mock_heiferIII = mocker.MagicMock(autospec=HeiferIII)
        mock_heiferIII.id = i
        mock_heiferIIIs.append(mock_heiferIII)
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 50
    animals_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, animals_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 53
    assert len(mock_cows) == 50
    assert len(life_cycle_manager.sold_heifers) == 2
    assert life_cycle_manager.sold_heifer_num == 2
    assert len(animals_removed) == 2
    # ---------------------------------------------------------------

    # Case 2: len(heiferIIIs) + len(cows) <= herd_num * 1.03
    # Arrange
    life_cycle_manager.herd_num = 100
    mock_heiferIIIs: List[HeiferIII] = []
    for i in range(53):
        mock_heiferIII = mocker.MagicMock(autospec=HeiferIII)
        mock_heiferIII.id = i
        mock_heiferIIIs.append(mock_heiferIII)
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 50
    animals_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, animals_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 53
    assert len(mock_cows) == 50
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0
    assert len(animals_removed) == 0
    # ---------------------------------------------------------------

    # Case 3: len(heiferIIIs) == 0
    # Arrange
    life_cycle_manager.herd_num = 100
    mock_heiferIIIs: List[HeiferIII] = []
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 104
    animals_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, animals_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 0
    assert len(mock_cows) == 104
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0
    assert len(animals_removed) == 0


def test_check_if_replacement_heifers_needed(mocker: MockerFixture,
                                             life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _check_if_replacement_heifers_needed in file life_cycle.py"""

    # Case 1: len(cows) + len(heiferIIIs) + bought_heifer_num < herd_num * 1.01 AND sim_day > 1
    # Arrange
    sim_day = 100
    days_born = 30
    mock_heiferIIIs: List[HeiferIII] = [mocker.MagicMock(autospec=HeiferIII)] * 50
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 50
    animals_added = []
    life_cycle_manager.bought_heifer_num = 0
    life_cycle_manager.herd_num = 100

    life_cycle_manager.replacement_market = []
    for i in range(10):
        mock_replacement = mocker.MagicMock(autospec=Cow)
        mock_replacement.id = i
        mock_replacement.days_born = days_born
        life_cycle_manager.replacement_market.append(mock_replacement)

    # Assert before
    assert life_cycle_manager.bought_heifer_num == 0

    # Act
    life_cycle_manager._check_if_replacement_heifers_needed(sim_day, mock_heiferIIIs,
                                                            mock_cows, animals_added)

    # Assert after
    assert life_cycle_manager.bought_heifer_num == 1
    assert len(animals_added) == 1
    assert animals_added[0].id == 0
    animals_added[0].events.add_event.assert_called_once_with(days_born, sim_day, ENTER_HERD)
    animals_added[0].set_p_purchased.assert_called_once()
    # ---------------------------------------------------------------

    # Case 2: len(cows) + len(heiferIIIs) + bought_heifer_num >= herd_num * 1.01
    # Arrange
    sim_day = 100
    days_born = 30
    mock_heiferIIIs: List[HeiferIII] = [mocker.MagicMock(autospec=HeiferIII)] * 51
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 50
    animals_added = []
    life_cycle_manager.bought_heifer_num = 0
    life_cycle_manager.herd_num = 100

    life_cycle_manager.replacement_market = []
    for i in range(10):
        mock_replacement = mocker.MagicMock(autospec=Cow)
        mock_replacement.id = i
        mock_replacement.days_born = days_born
        life_cycle_manager.replacement_market.append(mock_replacement)

    # Assert before
    assert life_cycle_manager.bought_heifer_num == 0

    # Act
    life_cycle_manager._check_if_replacement_heifers_needed(sim_day, mock_heiferIIIs,
                                                            mock_cows, animals_added)

    # Assert after
    assert life_cycle_manager.bought_heifer_num == 0
    assert len(mock_heiferIIIs) == 51
    assert len(mock_cows) == 50
    assert len(animals_added) == 0

    # ---------------------------------------------------------------

    # Case 3: sim_day == 1
    # Arrange
    sim_day = 1
    days_born = 30
    mock_heiferIIIs: List[HeiferIII] = [mocker.MagicMock(autospec=HeiferIII)] * 50
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 50
    animals_added = []
    life_cycle_manager.bought_heifer_num = 0
    life_cycle_manager.herd_num = 100

    life_cycle_manager.replacement_market = []
    for i in range(10):
        mock_replacement = mocker.MagicMock(autospec=Cow)
        mock_replacement.id = i
        mock_replacement.days_born = days_born
        life_cycle_manager.replacement_market.append(mock_replacement)

    # Assert before
    assert life_cycle_manager.bought_heifer_num == 0

    # Act
    life_cycle_manager._check_if_replacement_heifers_needed(sim_day, mock_heiferIIIs,
                                                            mock_cows, animals_added)

    # Assert after
    assert life_cycle_manager.bought_heifer_num == 0
    assert len(mock_heiferIIIs) == 50
    assert len(mock_cows) == 50
    assert len(animals_added) == 0


def test_cull_cow(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _cull_cow() in file life_cycle.py"""
    # Arrange
    mock_cow: Cow = mocker.MagicMock(autospec=Cow)
    mock_cow.cull_reason = LOW_PROD_CULL
    life_cycle_manager.culled_cows = []
    life_cycle_manager.cull_reason_stats_range = collections.defaultdict(int)
    life_cycle_manager._reset_cull_reason_stats()

    parity = 3
    mock_cow.calves = parity
    life_cycle_manager.parity_culling_stats_range = collections.defaultdict(int)

    mock_cow.days_born = 100
    life_cycle_manager.culled_cow_num = 0
    life_cycle_manager.avg_cow_culling_age = 0

    # Assert before
    assert len(life_cycle_manager.culled_cows) == 0
    assert len(life_cycle_manager.cull_reason_stats_range) == 0
    assert life_cycle_manager.cull_reason_stats[LOW_PROD_CULL] == 0
    assert len(life_cycle_manager.parity_culling_stats_range) == 0

    # Act
    life_cycle_manager._cull_cow(mock_cow)

    # Assert
    assert len(life_cycle_manager.culled_cows) == 1
    assert len(life_cycle_manager.cull_reason_stats_range) == 1
    assert LOW_PROD_CULL in life_cycle_manager.cull_reason_stats_range
    assert life_cycle_manager.cull_reason_stats_range[LOW_PROD_CULL] == 1
    assert life_cycle_manager.cull_reason_stats[LOW_PROD_CULL] == 1

    assert len(life_cycle_manager.parity_culling_stats_range) == 1
    assert parity in life_cycle_manager.parity_culling_stats_range
    assert life_cycle_manager.parity_culling_stats_range[parity] == 1

    assert life_cycle_manager.culled_cow_num == 1
    assert life_cycle_manager.avg_cow_culling_age == approx(100.0)


def test_handle_cow_body_weight_and_parity(mocker: MockerFixture,
                                           life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _handle_cow_body_weight_and_parity() in file life_cycle.py"""
    # Arrange
    total_animal_num = 100
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.body_weight = 1100.0
    mock_cow.calves = 20
    mock_cow.mature_body_weight = 1300.0

    life_cycle_manager.cow_num = 10
    life_cycle_manager.avg_cow_body_weight = 1000.0
    life_cycle_manager.avg_parity_num = 2.0
    life_cycle_manager.avg_mature_body_weight = 1200.0

    expected_new_cow_num = 11
    expected_new_avg_cow_body_weight = (life_cycle_manager.avg_cow_body_weight *
                                        life_cycle_manager.cow_num +
                                        mock_cow.body_weight) / expected_new_cow_num
    expected_new_avg_parity_num = (life_cycle_manager.avg_parity_num *
                                   life_cycle_manager.cow_num +
                                   mock_cow.calves) / expected_new_cow_num

    expected_new_total_animal_num = total_animal_num + 1
    expected_new_avg_mature_body_weight = (life_cycle_manager.avg_mature_body_weight *
                                           total_animal_num +
                                           mock_cow.mature_body_weight) / expected_new_total_animal_num
    spy_handle_cow_body_weight = mocker.spy(life_cycle_manager, '_handle_cow_body_weight_and_parity')

    # Act
    new_total_animal_num = life_cycle_manager._handle_cow_body_weight_and_parity(mock_cow, total_animal_num)

    # Assert
    assert new_total_animal_num == expected_new_total_animal_num
    assert life_cycle_manager.cow_num == expected_new_cow_num
    assert life_cycle_manager.avg_cow_body_weight == approx(expected_new_avg_cow_body_weight)
    assert life_cycle_manager.avg_parity_num == approx(expected_new_avg_parity_num)
    assert life_cycle_manager.avg_mature_body_weight == approx(expected_new_avg_mature_body_weight)
    spy_handle_cow_body_weight.assert_called_once_with(mock_cow, total_animal_num)


@pytest.mark.parametrize('is_cow_milking', [True, False])
def test_handle_cow_milking(mocker: MockerFixture,
                            life_cycle_manager: LifeCycleManager,
                            is_cow_milking: bool) -> None:
    """Unit test for function _handle_cow_milking() in file life_cycle.py"""
    # Arrange
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.milking = is_cow_milking
    mock_cow.estimated_daily_milk_produced = 15.0
    mock_cow.days_in_milk = 8

    life_cycle_manager.daily_milk_production = 100
    life_cycle_manager.milking_cow_num = 20
    life_cycle_manager.avg_days_in_milk = 7
    life_cycle_manager.vwp_cow_num = 2
    life_cycle_manager.animal_config = {
        'voluntary_waiting_period': 9,
    }
    life_cycle_manager.dry_cow_num = 5

    expected_new_milking_cow_num = life_cycle_manager.milking_cow_num + 1
    expected_new_avg_days_in_milk = (life_cycle_manager.avg_days_in_milk * life_cycle_manager.milking_cow_num +
                                     mock_cow.days_in_milk) / expected_new_milking_cow_num
    expected_vwp_cow_num = life_cycle_manager.vwp_cow_num + 1
    expected_new_dry_cow_num = life_cycle_manager.dry_cow_num + 1
    spy_handle_cow_milking = mocker.spy(life_cycle_manager, '_handle_cow_milking')

    # Act
    life_cycle_manager._handle_cow_milking(mock_cow)

    # Assert
    spy_handle_cow_milking.assert_called_once_with(mock_cow)
    if is_cow_milking:
        assert life_cycle_manager.milking_cow_num == expected_new_milking_cow_num
        assert life_cycle_manager.avg_days_in_milk == approx(expected_new_avg_days_in_milk)
        assert life_cycle_manager.vwp_cow_num == expected_vwp_cow_num
    else:
        assert life_cycle_manager.dry_cow_num == expected_new_dry_cow_num


@pytest.mark.parametrize('days_in_preg', [0, 1, 8])
def test_handle_cow_days_in_preg(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                                 days_in_preg: int) -> None:
    """Unit test for function _handle_cow_days_in_preg() in file life_cycle.py"""
    # Arrange
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.days_in_preg = days_in_preg

    life_cycle_manager.preg_cow_num = 20
    life_cycle_manager.avg_days_in_preg = 7.0
    life_cycle_manager.open_cow_num = 5

    expected_new_pregnant_cow_num = life_cycle_manager.preg_cow_num + 1
    expected_new_avg_days_in_preg = (life_cycle_manager.avg_days_in_preg * life_cycle_manager.preg_cow_num +
                                     mock_cow.days_in_preg) / expected_new_pregnant_cow_num
    expected_new_open_cow_num = life_cycle_manager.open_cow_num + 1
    spy_handle_cow_days_in_preg = mocker.spy(life_cycle_manager, '_handle_cow_days_in_preg')

    # Act
    life_cycle_manager._handle_cow_days_in_preg(mock_cow)

    # Assert
    spy_handle_cow_days_in_preg.assert_called_once_with(mock_cow)
    if mock_cow.days_in_preg > 0:
        assert life_cycle_manager.preg_cow_num == expected_new_pregnant_cow_num
        assert life_cycle_manager.avg_days_in_preg == approx(expected_new_avg_days_in_preg)
    else:
        assert life_cycle_manager.open_cow_num == expected_new_open_cow_num


@pytest.mark.parametrize('cow_CI', [0, 1])
def test_handle_cow_CI(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                       cow_CI: int) -> None:
    """Unit test for function _handle_cow_CI() in file life_cycle.py"""
    # Arrange
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.CI = cow_CI
    calving_interval_avail_num = 5
    life_cycle_manager.avg_calving_interval = 7.0
    expected_new_calving_interval_avail_num = calving_interval_avail_num + 1
    expected_new_avg_calving_interval = (life_cycle_manager.avg_calving_interval * calving_interval_avail_num +
                                         mock_cow.CI) / expected_new_calving_interval_avail_num
    spy_handle_cow_CI = mocker.spy(life_cycle_manager, '_handle_cow_CI')

    # Act
    new_calving_interval_avail_num = life_cycle_manager._handle_cow_CI(mock_cow, calving_interval_avail_num)

    # Assert
    spy_handle_cow_CI.assert_called_once_with(mock_cow, calving_interval_avail_num)
    if mock_cow.CI != 0:
        assert new_calving_interval_avail_num == expected_new_calving_interval_avail_num
        assert life_cycle_manager.avg_calving_interval == approx(expected_new_avg_calving_interval)
    else:
        assert new_calving_interval_avail_num == calving_interval_avail_num


def test_extract_repro_stats_from_cow(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _extract_repro_stats_from_cow() in file life_cycle.py"""
    # Arrange
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.GnRH_injections = 1
    mock_cow.PGF_injections = 2
    mock_cow.preg_diagnoses = 3
    mock_cow.semen_num = 4
    mock_cow.AI_times = 5

    life_cycle_manager.GnRH_injection_num = 1
    life_cycle_manager.PGF_injection_num = 1
    life_cycle_manager.preg_check_num = 1
    life_cycle_manager.semen_num = 1
    life_cycle_manager.ai_num = 1

    expected_GnRH_injection_num = life_cycle_manager.GnRH_injection_num + mock_cow.GnRH_injections
    expected_PGF_injections = life_cycle_manager.PGF_injection_num + mock_cow.PGF_injections
    expected_preg_check_num = life_cycle_manager.preg_check_num + mock_cow.preg_diagnoses
    expected_semen_num = life_cycle_manager.semen_num + mock_cow.semen_num
    expected_ai_num = life_cycle_manager.ai_num + mock_cow.AI_times

    spy_extract_repro_stats_from_cow = mocker.spy(life_cycle_manager, '_extract_repro_stats_from_cow')

    # Act
    life_cycle_manager._extract_repro_stats_from_cow(mock_cow)

    # Assert
    spy_extract_repro_stats_from_cow.assert_called_once_with(mock_cow)
    assert life_cycle_manager.GnRH_injection_num == expected_GnRH_injection_num
    assert life_cycle_manager.PGF_injection_num == expected_PGF_injections
    assert life_cycle_manager.preg_check_num == expected_preg_check_num
    assert life_cycle_manager.semen_num == expected_semen_num
    assert life_cycle_manager.ai_num == expected_ai_num


@pytest.mark.parametrize('is_calf_culled, is_calf_sold',
                         [(True, True),
                          (True, False),
                          (False, True),
                          (False, True)
                          ])
def test_handle_new_born(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                         is_calf_culled: bool,
                         is_calf_sold: bool) -> None:
    # Arrange
    sim_day = 1
    life_cycle_manager.sold_calf_num = sold_calf_num = 0
    mock_animal_data = mocker.MagicMock(autospec=AnimalData)
    mock_animal_data.next_id.return_value = calf_id = 100
    life_cycle_manager.animal_data = mock_animal_data
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.p_animal = p_animal = 1.0
    mock_cow.p_gest_for_calf = p_gest_for_calf = 2.0
    mock_cow.p_growth = p_growth = 3.0
    mock_cow.dP_reserves = dP_reserves = 4.0
    mock_cow.calf_birth_weight = calf_birth_weight = 5.0
    expected_cow_p_animal = p_animal - p_gest_for_calf + p_growth + dP_reserves

    mock_calf = mocker.MagicMock(autospec=Calf)
    mock_calf.days_born = calf_days_born = 6
    mock_calf.culled = is_calf_culled
    mock_calf.sold = is_calf_sold
    patch_for_mock_calf = mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.Calf',
                                       return_value=mock_calf)
    calves_born = []

    # Act
    life_cycle_manager._handle_new_born(sim_day, mock_cow, calves_born)

    # Assert
    assert mock_cow.p_animal == expected_cow_p_animal
    assert mock_cow.p_gest_for_calf == approx(0.0)
    assert mock_cow.calf_birth_weight == approx(0.0)
    patch_for_mock_calf.assert_called_once_with({
        'id': calf_id,
        'breed': 'HO',
        'birth_date': sim_day,
        'days_born': 0,
        'p_init': p_gest_for_calf,
        'birth_weight': calf_birth_weight
    })
    if not is_calf_culled and not is_calf_sold:
        mock_calf.events.add_event.assert_called_once_with(calf_days_born, sim_day, animal_constants.ENTER_HERD)
        assert len(calves_born) == 1
        assert calves_born[0] == mock_calf
    if is_calf_sold:
        assert life_cycle_manager.sold_calf_num == sold_calf_num + 1


@pytest.mark.parametrize('cow_calves', [1, 2, 3, 4])
def test_handle_cow_calves(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                           cow_calves: int) -> None:
    """Unit test for function _handle_cow_calves() in file life_cycle.py."""
    # Arrange
    mock_cow = mocker.MagicMock(autospec=Cow)
    mock_cow.calves = cow_calves
    key = 'greater_than_3' if cow_calves > 3 else str(cow_calves)
    calving_age_avail_num = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    calf_to_preg_time_avail_num = calving_age_avail_num.copy()
    spy_handle_cow_calves = mocker.spy(life_cycle_manager, '_handle_cow_calves')

    mock_cow.days_born = 300
    expected_avg_age_for_parity_for_key = 300.0

    mock_cow.events.get_most_recent_date.return_value = 100
    expected_avg_age_for_calving_for_key = 100.0

    mock_cow.calving_to_preg_time = 200
    expected_avg_calving_to_preg_time = 200.0

    # Act
    life_cycle_manager._handle_cow_calves(mock_cow, calving_age_avail_num, calf_to_preg_time_avail_num)

    # Assert
    spy_handle_cow_calves.assert_called_once_with(mock_cow, calving_age_avail_num, calf_to_preg_time_avail_num)
    assert life_cycle_manager.num_cow_for_parity[key] == 1
    assert life_cycle_manager.avg_age_for_parity[key] == approx(expected_avg_age_for_parity_for_key)

    mock_cow.events.get_most_recent_date.assert_called_once_with(animal_constants.NEW_BIRTH)
    assert calving_age_avail_num[key] == 1
    assert life_cycle_manager.avg_age_for_calving[key] == approx(expected_avg_age_for_calving_for_key)

    assert calf_to_preg_time_avail_num[key] == 1
    assert life_cycle_manager.avg_calving_to_preg_time[key] == approx(expected_avg_calving_to_preg_time)


@pytest.mark.parametrize('total_animal_num', [0, 50, 100])
def test_calculate_herd_percentages(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                                    total_animal_num: int) -> None:
    """Unit test for function _calculate_herd_percentages() in file life_cycle.py."""
    # Arrange
    calf_num = heiferI_num = heiferII_num = heiferIII_num = cow_num = 0
    if total_animal_num > 0:
        life_cycle_manager.calf_num = calf_num = int(0.2 * total_animal_num)
        life_cycle_manager.heiferI_num = heiferI_num = int(0.2 * total_animal_num)
        life_cycle_manager.heiferII_num = heiferII_num = int(0.2 * total_animal_num)
        life_cycle_manager.heiferIII_num = heiferIII_num = int(0.2 * total_animal_num)
        life_cycle_manager.cow_num = cow_num = (total_animal_num - calf_num - heiferI_num
                                                - heiferII_num - heiferIII_num)
    spy_calc_herd_percentages = mocker.spy(life_cycle_manager, '_calculate_herd_percentages')

    # Act
    life_cycle_manager._calculate_herd_percentages(total_animal_num)

    # Assert
    spy_calc_herd_percentages.assert_called_once_with(total_animal_num)
    if total_animal_num > 0:
        assert life_cycle_manager.calf_percent == approx(calf_num * 100.0 / total_animal_num)
        assert life_cycle_manager.heiferI_percent == approx(heiferI_num * 100.0 / total_animal_num)
        assert life_cycle_manager.heiferII_percent == approx(heiferII_num * 100.0 / total_animal_num)
        assert life_cycle_manager.heiferIII_percent == approx(heiferIII_num * 100.0 / total_animal_num)
        assert life_cycle_manager.cow_percent == approx(cow_num * 100.0 / total_animal_num)
    elif total_animal_num == 0:
        assert life_cycle_manager.calf_percent == approx(0.0)
        assert life_cycle_manager.heiferI_percent == approx(0.0)
        assert life_cycle_manager.heiferII_percent == approx(0.0)
        assert life_cycle_manager.heiferIII_percent == approx(0.0)
        assert life_cycle_manager.cow_percent == approx(0.0)


@pytest.mark.parametrize('cow_num', [0, 50, 100])
def test_calc_cow_percentages(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                              cow_num: int) -> None:
    """Unit test for function _calculate_cow_percentages() in file life_cycle.py."""
    # Arrange
    dry_cow_num = milking_cow_num = preg_cow_num = open_cow_num = 0
    life_cycle_manager.cow_num = cow_num
    if cow_num > 0:
        life_cycle_manager.dry_cow_num = dry_cow_num = int(0.2 * cow_num)
        life_cycle_manager.milking_cow_num = milking_cow_num = int(0.2 * cow_num)
        life_cycle_manager.preg_cow_num = preg_cow_num = int(0.2 * cow_num)
        life_cycle_manager.open_cow_num = open_cow_num = int(0.2 * cow_num)
    spy_calc_cow_percentages = mocker.spy(life_cycle_manager, '_calculate_cow_percentages')

    # Act
    life_cycle_manager._calculate_cow_percentages()

    # Assert
    spy_calc_cow_percentages.assert_called_once()
    if cow_num > 0:
        assert life_cycle_manager.dry_cow_percent == approx(dry_cow_num * 100.0 / cow_num)
        assert life_cycle_manager.milking_cow_percent == approx(milking_cow_num * 100.0 / cow_num)
        assert life_cycle_manager.preg_cow_percent == approx(preg_cow_num * 100.0 / cow_num)
        assert life_cycle_manager.non_preg_cow_percent == approx(open_cow_num * 100.0 / cow_num)
    elif cow_num == 0:
        assert life_cycle_manager.dry_cow_percent == approx(0.0)
        assert life_cycle_manager.milking_cow_percent == approx(0.0)
        assert life_cycle_manager.preg_cow_percent == approx(0.0)
        assert life_cycle_manager.non_preg_cow_percent == approx(0.0)


@pytest.mark.parametrize('culled_cow_num', [0, 50, 100])
def test_calc_cull_reason_stats_percent(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                                        culled_cow_num: int) -> None:
    """Unit test for function _calculate_cull_reason_stats_percent() in file life_cycle.py."""
    # Arrange
    life_cycle_manager.culled_cow_num = culled_cow_num
    num_reasons = len(life_cycle_manager.cull_reason_stats)
    life_cycle_manager.cull_reason_stats.update({
        animal_constants.DEATH_CULL: int(culled_cow_num / num_reasons),
        animal_constants.LOW_PROD_CULL: int(culled_cow_num / num_reasons),
        animal_constants.LAMENESS_CULL: int(culled_cow_num / num_reasons),
        animal_constants.INJURY_CULL: int(culled_cow_num / num_reasons),
        animal_constants.MASTITIS_CULL: int(culled_cow_num / num_reasons),
        animal_constants.DISEASE_CULL: int(culled_cow_num / num_reasons),
        animal_constants.UDDER_CULL: int(culled_cow_num / num_reasons),
        animal_constants.UNKNOWN_CULL: 0  # Initialized with 0
    })
    life_cycle_manager.cull_reason_stats[animal_constants.UNKNOWN_CULL] = \
        culled_cow_num - sum(life_cycle_manager.cull_reason_stats.values())

    spy_calc_cull_reason_stats_percent = mocker.spy(life_cycle_manager, '_calculate_cull_reason_stats_percent')

    # Act
    life_cycle_manager._calculate_cull_reason_stats_percent()

    # Assert
    spy_calc_cull_reason_stats_percent.assert_called_once()
    for cull_reason in life_cycle_manager.cull_reason_stats_percent:
        if culled_cow_num > 0:
            assert life_cycle_manager.cull_reason_stats_percent[cull_reason] == \
                   approx(life_cycle_manager.cull_reason_stats[cull_reason] * 100.0 / culled_cow_num)
        elif culled_cow_num == 0:
            assert life_cycle_manager.cull_reason_stats_percent[cull_reason] == approx(0.0)


@pytest.mark.parametrize('cow_num', [0, 50, 100])
def test_calc_percent_cow_per_parity(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                                     cow_num: int) -> None:
    """Unit test for function _calculate_percent_cow_per_parity() in file life_cycle.py."""
    # Arrange
    life_cycle_manager.cow_num = cow_num
    num_parities = len(life_cycle_manager.num_cow_for_parity)
    life_cycle_manager.num_cow_for_parity.update({
        '1': int(cow_num / num_parities),
        '2': int(cow_num / num_parities),
        '3': int(cow_num / num_parities),
        'greater_than_3': 0
    })
    life_cycle_manager.num_cow_for_parity['greater_than_3'] = \
        cow_num - sum(life_cycle_manager.num_cow_for_parity.values())

    spy_calc_percent_cow_per_parity = mocker.spy(life_cycle_manager, '_calculate_percent_cow_per_parity')

    # Act
    life_cycle_manager._calculate_percent_cow_per_parity()

    # Assert
    spy_calc_percent_cow_per_parity.assert_called_once()
    for parity in life_cycle_manager.num_cow_for_parity:
        if cow_num > 0:
            assert life_cycle_manager.percent_cow_for_parity[parity] == \
                   approx(life_cycle_manager.num_cow_for_parity[parity] * 100.0 / cow_num)
        elif cow_num == 0:
            assert life_cycle_manager.percent_cow_for_parity[parity] == approx(0.0)


def test_cull_cows_and_record_stats(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    # Arrange
    sim_day = 1
    mock_cows = []
    num_cows = 10
    calves_born = []
    animals_removed = []
    removed_cows_idx = []
    total_animal_num_start = 0
    current_total_animal_num = total_animal_num_start
    total_animal_num_side_effect = []
    num_cows_culled = 0
    num_new_born = 0
    life_cycle_manager.avg_CI = avg_CI = 365
    for i in range(num_cows):
        mock_cow = mocker.MagicMock()
        mock_cow.id = i
        is_culled = i % 2 == 0
        has_new_born = i % 3 == 0
        mock_cow.update.return_value = (None, None, None, is_culled, has_new_born)
        if is_culled:
            animals_removed.append(mock_cow)
            removed_cows_idx.append(i)
            num_cows_culled += 1
        else:
            current_total_animal_num += 1
            total_animal_num_side_effect.append(current_total_animal_num)
        if has_new_born:
            num_new_born += 1
        mock_cows.append(mock_cow)
    num_cows_not_culled = num_cows - num_cows_culled
    mock_cows_original = mock_cows.copy()
    calving_interval_avail_num = 0
    calving_age_avail_num = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    calf_to_preg_time_avail_num = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }

    patch_for_cull_cow = mocker.patch.object(life_cycle_manager, '_cull_cow')

    patch_for_handle_cow_body_weight_and_parity = mocker.patch.object(
        life_cycle_manager,
        '_handle_cow_body_weight_and_parity',
        side_effect=total_animal_num_side_effect
    )
    patch_for_handle_cow_milking = mocker.patch.object(life_cycle_manager, '_handle_cow_milking')
    patch_for_handle_cow_days_in_preg = mocker.patch.object(life_cycle_manager, '_handle_cow_days_in_preg')
    patch_for_handle_cow_calves = mocker.patch.object(life_cycle_manager, '_handle_cow_calves')
    patch_for_handle_cow_CI = mocker.patch.object(
        life_cycle_manager,
        '_handle_cow_CI',
        return_value=calving_interval_avail_num
    )
    patch_for_extract_repro_stats_from_cow = mocker.patch.object(life_cycle_manager, '_extract_repro_stats_from_cow')

    patch_for_handle_new_born = mocker.patch.object(life_cycle_manager, '_handle_new_born')
    patch_for_remove_items_from_list_by_indices = mocker.patch(
        'RUFAS.routines.animal.life_cycle.life_cycle.Utility.remove_items_from_list_by_indices')

    # Act
    actual_total_animal_num = life_cycle_manager._cull_cows_and_record_stats(sim_day, mock_cows,
                                                                             calves_born, animals_removed,
                                                                             total_animal_num_start)

    # Assert
    for cow in mock_cows_original:
        cow.update.assert_called_once_with(sim_day, avg_CI)
        _, _, _, is_culled, has_new_born = cow.update.return_value
        if is_culled:
            assert cow in animals_removed
            assert cow.id in removed_cows_idx
        else:
            patch_for_handle_cow_body_weight_and_parity.assert_any_call(cow,
                                                                        total_animal_num_side_effect.pop(0) - 1)
            patch_for_handle_cow_milking.assert_any_call(cow)
            patch_for_handle_cow_days_in_preg.assert_any_call(cow)
            patch_for_handle_cow_calves.assert_any_call(cow, calving_age_avail_num,
                                                        calf_to_preg_time_avail_num)
            patch_for_handle_cow_CI.assert_any_call(cow, calving_interval_avail_num)
            patch_for_extract_repro_stats_from_cow.assert_any_call(cow)
        if has_new_born:
            patch_for_handle_new_born.assert_any_call(sim_day, cow, calves_born)

    assert patch_for_cull_cow.call_count == num_cows_culled
    assert patch_for_handle_cow_body_weight_and_parity.call_count == num_cows_not_culled
    assert patch_for_handle_cow_milking.call_count == num_cows_not_culled
    assert patch_for_handle_cow_days_in_preg.call_count == num_cows_not_culled
    assert patch_for_handle_cow_calves.call_count == num_cows_not_culled
    assert patch_for_handle_cow_CI.call_count == num_cows_not_culled
    assert patch_for_extract_repro_stats_from_cow.call_count == num_cows_not_culled
    assert patch_for_handle_new_born.call_count == num_new_born

    patch_for_remove_items_from_list_by_indices.assert_called_once_with(mock_cows_original, removed_cows_idx)
    assert actual_total_animal_num == current_total_animal_num


def test_reset_daily_stats(life_cycle_manager: LifeCycleManager) -> None:
    # Arrange
    life_cycle_manager.calf_num = 1
    life_cycle_manager.heiferI_num = 2
    life_cycle_manager.heiferII_num = 3
    life_cycle_manager.heiferIII_num = 4
    life_cycle_manager.cow_num = 5

    life_cycle_manager.sold_calf_num = 6
    life_cycle_manager.sold_heifer_num = 7
    life_cycle_manager.bought_heifer_num = 8
    life_cycle_manager.culled_heifer_num = 9
    life_cycle_manager.culled_cow_num = 10

    life_cycle_manager.calf_percent = 11.0
    life_cycle_manager.heiferI_percent = 12.0
    life_cycle_manager.heiferII_percent = 13.0
    life_cycle_manager.heiferIII_percent = 14.0
    life_cycle_manager.cow_percent = 15.0

    life_cycle_manager.CIDR_count = 16
    life_cycle_manager.preg_check_num_h = 17
    life_cycle_manager.preg_check_num = 18
    life_cycle_manager.GnRH_injection_num_h = 19
    life_cycle_manager.GnRH_injection_num = 20
    life_cycle_manager.PGF_injection_num_h = 21
    life_cycle_manager.PGF_injection_num = 22
    life_cycle_manager.ai_num_h = 23
    life_cycle_manager.ai_num = 24
    life_cycle_manager.semen_num_h = 25
    life_cycle_manager.semen_num = 26
    life_cycle_manager.ed_period_h = 27

    life_cycle_manager.open_cow_num = 28
    life_cycle_manager.preg_cow_num = 29
    life_cycle_manager.vwp_cow_num = 30
    life_cycle_manager.milking_cow_num = 31
    life_cycle_manager.dry_cow_num = 32

    life_cycle_manager.preg_cow_percent = 33
    life_cycle_manager.dry_cow_percent = 34
    life_cycle_manager.milking_cow_percent = 35
    life_cycle_manager.non_preg_cow_percent = 36

    life_cycle_manager.daily_milk_production = 37
    life_cycle_manager.avg_days_in_milk = 38
    life_cycle_manager.avg_days_in_preg = 39
    life_cycle_manager.avg_cow_body_weight = 40
    life_cycle_manager.avg_parity_num = 41

    life_cycle_manager.avg_calving_interval = 42
    life_cycle_manager.avg_breeding_to_preg_time = 43
    life_cycle_manager.avg_heifer_culling_age = 44
    life_cycle_manager.avg_cow_culling_age = 45
    life_cycle_manager.avg_mature_body_weight = 46

    # Act
    life_cycle_manager._reset_daily_stats()

    # Assert
    assert life_cycle_manager.calf_num == 0
    assert life_cycle_manager.heiferI_num == 0
    assert life_cycle_manager.heiferII_num == 0
    assert life_cycle_manager.heiferIII_num == 0
    assert life_cycle_manager.cow_num == 0

    assert life_cycle_manager.sold_calf_num == 0
    assert life_cycle_manager.sold_heifer_num == 0
    assert life_cycle_manager.bought_heifer_num == 0
    assert life_cycle_manager.culled_heifer_num == 0
    assert life_cycle_manager.culled_cow_num == 0

    assert life_cycle_manager.calf_percent == approx(0.0)
    assert life_cycle_manager.heiferI_percent == approx(0.0)
    assert life_cycle_manager.heiferII_percent == approx(0.0)
    assert life_cycle_manager.heiferIII_percent == approx(0.0)
    assert life_cycle_manager.cow_percent == approx(0.0)

    assert life_cycle_manager.CIDR_count == 0
    assert life_cycle_manager.preg_check_num_h == 0
    assert life_cycle_manager.preg_check_num == 0
    assert life_cycle_manager.GnRH_injection_num_h == 0
    assert life_cycle_manager.GnRH_injection_num == 0
    assert life_cycle_manager.PGF_injection_num_h == 0
    assert life_cycle_manager.PGF_injection_num == 0
    assert life_cycle_manager.ai_num_h == 0
    assert life_cycle_manager.ai_num == 0
    assert life_cycle_manager.semen_num_h == 0
    assert life_cycle_manager.semen_num == 0
    assert life_cycle_manager.ed_period_h == 0

    assert life_cycle_manager.open_cow_num == 0
    assert life_cycle_manager.preg_cow_num == 0
    assert life_cycle_manager.vwp_cow_num == 0
    assert life_cycle_manager.milking_cow_num == 0
    assert life_cycle_manager.dry_cow_num == 0

    assert life_cycle_manager.preg_cow_percent == approx(0.0)
    assert life_cycle_manager.dry_cow_percent == approx(0.0)
    assert life_cycle_manager.milking_cow_percent == approx(0.0)
    assert life_cycle_manager.non_preg_cow_percent == approx(0.0)

    assert life_cycle_manager.daily_milk_production == approx(0.0)
    assert life_cycle_manager.avg_days_in_milk == approx(0.0)
    assert life_cycle_manager.avg_days_in_preg == approx(0.0)
    assert life_cycle_manager.avg_cow_body_weight == approx(0.0)
    assert life_cycle_manager.avg_parity_num == approx(0.0)

    assert life_cycle_manager.avg_calving_interval == approx(0.0)
    assert life_cycle_manager.avg_breeding_to_preg_time == approx(0.0)
    assert life_cycle_manager.avg_heifer_culling_age == approx(0.0)
    assert life_cycle_manager.avg_cow_culling_age == approx(0.0)
    assert life_cycle_manager.avg_mature_body_weight == approx(0.0)
