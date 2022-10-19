import collections
from typing import Dict, List

from pytest import approx, fixture
from pytest_mock import MockerFixture

from RUFAS.classes import Config
from RUFAS.routines.animal.animal_typed_dicts import AnimalConfigTypedDict, HerdInfoTypedDict
from RUFAS.routines.animal.life_cycle.animal_constants import ENTER_HERD, INIT_HERD, LOW_PROD_CULL
from RUFAS.routines.animal.life_cycle.animal_initialization import AnimalInitialization
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.pen import Pen


@fixture
def herd_data() -> HerdInfoTypedDict:
    return {
        'calf_num': 80,
        'heiferI_num': 440,
        'heiferII_num': 380,
        'heiferIII_num': 50,
        'cow_num': 1000,
        'replace_num': 5000,
        'herd_num': 1000,
        'herd_init': False,
        'breed': 'HO'
    }


@fixture
def life_cycle_manager(mocker: MockerFixture) -> LifeCycleManager:
    return LifeCycleManager(data=mocker.MagicMock(autospec=AnimalConfigTypedDict))


def test_set_avg_CI(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _set_avg_CI in file life_cycle.py"""
    # Given user input calving interval,
    # the function should correctly set the user-specified average calving interval.
    custom_avg_CI = 400.0
    mock_animal_config_data = {
        'user_input_calving_interval': True,
        'calving_interval': custom_avg_CI
    }
    mock_animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)
    mock_animal_config.__contains__.side_effect = mock_animal_config_data.__contains__
    mock_animal_config.__getitem__.side_effect = mock_animal_config_data.__getitem__
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)

    spy_set_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')
    assert life_cycle_manager.avg_CI == approx(0.0)

    life_cycle_manager._set_avg_CI(mock_animal_config, mock_animal_initializer)

    assert life_cycle_manager.avg_CI == approx(custom_avg_CI)
    spy_set_avg_CI.assert_called_once()


def test_set_avg_CI_2(mocker: MockerFixture, life_cycle_manager) -> None:
    """Unit test for function _set_avg_CI in file life_cycle.py"""
    # Given no user input calving interval,
    # the function should use the cow average calving interval by default.
    cow_avg_CI = 500.0
    mock_animal_config_data = {
        'user_input_calving_interval': False
    }
    mock_animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)
    mock_animal_config.__getitem__.side_effect = mock_animal_config_data.__getitem__
    mock_init_db_summary = {
        'cow_avg_CI': cow_avg_CI
    }
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.initialization_db_summary.return_value = mock_init_db_summary

    spy_get_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')
    assert life_cycle_manager.avg_CI == approx(0.0)

    life_cycle_manager._set_avg_CI(mock_animal_config, mock_animal_initializer)

    assert life_cycle_manager.avg_CI == approx(cow_avg_CI)
    spy_get_avg_CI.assert_called_once()
    mock_animal_initializer.initialization_db_summary.assert_called_once()


def test_get_calves(mocker: MockerFixture, life_cycle_manager) -> None:
    """Unit test for function _get_calves in file life_cycle.py"""
    calf_num = 10
    breed = 'HO'
    days_born = 50
    mock_calves = []
    for i in range(calf_num):
        mock_new_calf = mocker.MagicMock(autospec=Calf)
        mock_new_calf.breed = breed
        mock_new_calf.days_born = days_born
        mock_calves.append(mock_new_calf)
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.get_calves.return_value = mock_calves
    spy_get_calves = mocker.spy(life_cycle_manager, '_get_calves')

    calves = life_cycle_manager._get_calves(calf_num, breed, mock_animal_initializer)

    assert len(calves) == calf_num
    for calf in calves:
        assert calf.breed == breed
        calf.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_calves.assert_called_once_with(calf_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_calves.assert_called_once_with(calf_num, breed)


def test_get_heiferIs(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _get_heiferIs in file life_cycle.py"""
    heiferI_num = 10
    breed = 'HO'
    days_born = 350
    mock_heiferIs = []
    for i in range(heiferI_num):
        mock_new_heiferI = mocker.MagicMock(autospec=HeiferI)
        mock_new_heiferI.breed = breed
        mock_new_heiferI.days_born = days_born
        mock_heiferIs.append(mock_new_heiferI)
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.get_heiferIs.return_value = mock_heiferIs
    spy_get_heiferIs = mocker.spy(life_cycle_manager, '_get_heiferIs')

    heiferIs = life_cycle_manager._get_heiferIs(heiferI_num, breed, mock_animal_initializer)

    assert len(heiferIs) == heiferI_num
    for heiferI in heiferIs:
        assert heiferI.breed == breed
        heiferI.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_heiferIs.assert_called_once_with(heiferI_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIs.assert_called_once_with(heiferI_num, breed)


def test_get_heiferIIs(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _get_heiferIIs in file life_cycle.py"""
    heiferII_num = 10
    breed = 'HO'
    days_born = 800
    mock_heiferIIs = []
    for i in range(heiferII_num):
        mock_new_heiferII = mocker.MagicMock(autospec=HeiferII)
        mock_new_heiferII.breed = breed
        mock_new_heiferII.days_born = days_born
        mock_heiferIIs.append(mock_new_heiferII)
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.get_heiferIIs.return_value = mock_heiferIIs
    spy_get_heiferIIs = mocker.spy(life_cycle_manager, '_get_heiferIIs')

    heiferIIs = life_cycle_manager._get_heiferIIs(heiferII_num, breed, mock_animal_initializer)

    assert len(heiferIIs) == heiferII_num
    for heiferII in heiferIIs:
        assert heiferII.breed == breed
        heiferII.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_heiferIIs.assert_called_once_with(heiferII_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIIs.assert_called_once_with(heiferII_num, breed)


def test_get_heiferIIIs(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _get_heiferIIIs in file life_cycle.py"""
    heiferIII_num = 10
    breed = 'HO'
    days_born = 650
    mock_heiferIIIs = []
    for i in range(heiferIII_num):
        mock_new_heiferIII = mocker.MagicMock(autospec=HeiferIII)
        mock_new_heiferIII.breed = breed
        mock_new_heiferIII.days_born = days_born
        mock_heiferIIIs.append(mock_new_heiferIII)
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.get_heiferIIIs.return_value = mock_heiferIIIs
    spy_get_heiferIIIs = mocker.spy(life_cycle_manager, '_get_heiferIIIs')

    heiferIIIs = life_cycle_manager._get_heiferIIIs(heiferIII_num, breed, mock_animal_initializer)

    assert len(heiferIIIs) == heiferIII_num
    for heiferIII in heiferIIIs:
        assert heiferIII.breed == breed
        heiferIII.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_heiferIIIs.assert_called_once_with(heiferIII_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIIIs.assert_called_once_with(heiferIII_num, breed)


def test_get_cows(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _get_cows in file life_cycle.py"""
    cow_num = 10
    breed = 'HO'
    days_born = 2200
    mock_cows = []
    for i in range(cow_num):
        mock_new_cow = mocker.MagicMock(autospec=Cow)
        mock_new_cow.breed = breed
        mock_new_cow.days_born = days_born
        mock_cows.append(mock_new_cow)
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.get_cows.return_value = mock_cows
    spy_get_cows = mocker.spy(life_cycle_manager, '_get_cows')

    cows = life_cycle_manager._get_cows(cow_num, breed, mock_animal_initializer)

    assert len(cows) == cow_num
    for cow in cows:
        assert cow.breed == breed
        cow.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy_get_cows.assert_called_once_with(cow_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_cows.assert_called_once_with(cow_num, breed)


def test_initialize_herd(mocker: MockerFixture, life_cycle_manager: LifeCycleManager,
                         herd_data: HerdInfoTypedDict) -> None:
    """Unit test for function initialize_herd in file life_cycle.py"""
    herd_num = herd_data['herd_num']
    calf_num = herd_data['calf_num']
    heiferI_num = herd_data['heiferI_num']
    heiferII_num = herd_data['heiferII_num']
    heiferIII_num = herd_data['heiferIII_num']
    cow_num = herd_data['cow_num']
    replace_num = herd_data['replace_num']
    herd_init = herd_data['herd_init']
    breed = herd_data['breed']
    mock_config = mocker.MagicMock(autospec=Config)

    mock_animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)
    mocker.patch.object(life_cycle_manager, 'animal_config', mock_animal_config)

    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_replacement_cows = [mocker.MagicMock(autospec=Cow) for _ in range(replace_num)]
    mock_animal_initializer.get_replacement_cows.return_value = mock_replacement_cows
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalInitialization',
                 return_value=mock_animal_initializer)

    mock_set_avg_CI = mocker.patch.object(life_cycle_manager, '_set_avg_CI')
    mock_get_calves = mocker.patch.object(life_cycle_manager, '_get_calves')
    mock_get_heiferIs = mocker.patch.object(life_cycle_manager, '_get_heiferIs')
    mock_get_heiferIIs = mocker.patch.object(life_cycle_manager, '_get_heiferIIs')
    mock_get_heiferIIIs = mocker.patch.object(life_cycle_manager, '_get_heiferIIIs')
    mock_get_cows = mocker.patch.object(life_cycle_manager, '_get_cows')

    results = life_cycle_manager.initialize_herd(herd_num, calf_num, heiferI_num, heiferII_num,
                                                 heiferIII_num, cow_num, replace_num, herd_init,
                                                 breed, mock_config)

    assert life_cycle_manager.herd_num == herd_data['herd_num']
    mock_set_avg_CI.assert_called_once_with(mock_animal_config, mock_animal_initializer)
    mock_get_calves.assert_called_once_with(calf_num, breed, mock_animal_initializer)
    mock_get_heiferIs.assert_called_once_with(heiferI_num, breed, mock_animal_initializer)
    mock_get_heiferIIs.assert_called_once_with(heiferII_num, breed, mock_animal_initializer)
    mock_get_heiferIIIs.assert_called_once_with(heiferIII_num, breed, mock_animal_initializer)
    mock_get_cows.assert_called_once_with(cow_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_replacement_cows.assert_called_once_with(replace_num, breed)
    assert life_cycle_manager.replacement_market == mock_replacement_cows
    assert len(results) == 5


def test_reset_parity(life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _reset_parity in file life_cycle.py"""
    parities = LifeCycleManager.num_cow_for_parity
    preg_times = LifeCycleManager.avg_calving_to_preg_time
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
    stats = LifeCycleManager.cull_reason_stats
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


def test_wean_calf(mocker: MockerFixture) -> None:
    """Unit test for function _wean_calf in file life_cycle.py"""
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
    LifeCycleManager._wean_calf(mock_calf, heiferIs)

    mock_calf_vals.update.assert_called_once_with({
        'body_weight_history': calf_body_weight_history,
        'pen_history': calf_pen_history
    })
    assert len(heiferIs) == 1
    assert heiferIs[0] == mock_new_heiferI  # check identity


def test_calf_to_heiferI(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _calf_to_heiferI in file life_cycle.py"""
    sim_day = 10
    mock_weaned_calf = mocker.MagicMock(autospec=Calf)
    mock_weaned_calf.update.return_value = True
    mock_wean_calf = mocker.patch.object(life_cycle_manager, '_wean_calf')

    mock_matured_calf = mocker.MagicMock(autospec=Calf)
    mock_matured_calf.update.return_value = False
    mock_matured_calf.mature_body_weight = mature_body_weight = 200.0

    mock_calves: List[Calf] = [mock_weaned_calf, mock_matured_calf]
    heiferIs: List[HeiferI] = []
    life_cycle_manager.calf_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    new_total_animal_num = life_cycle_manager._calf_to_heiferI(sim_day, mock_calves, heiferIs, total_animal_num)

    mock_weaned_calf.update.assert_called_once_with(sim_day)
    mock_wean_calf.assert_called_once_with(mock_weaned_calf, heiferIs)

    mock_matured_calf.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.calf_num == 1

    assert len(mock_calves) == 1
    assert mock_calves[0] == mock_matured_calf
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)


def test_move_heiferI_to_second_stage(mocker: MockerFixture) -> None:
    """Unit test for function _move_heiferI_to_second_stage in file life_cycle.py"""
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
        "heifer_TAI_protocol": heifer_TAI_protocol,
        "heifer_synchED_protocol": heifer_synchedED_protocol
    }
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.config', animal_base_config)

    LifeCycleManager._move_heiferI_to_second_stage(mock_heiferI, heiferIIs)

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


def test_heiferI_to_heiferII(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _heiferI_to_heiferII in file life_cycle.py"""
    sim_day = 100
    mock_heiferI_second_stage = mocker.MagicMock(autospec=HeiferI)
    mock_heiferI_second_stage.update.return_value = True
    mock_move_heiferI_to_second_stage = mocker.patch.object(life_cycle_manager,
                                                            '_move_heiferI_to_second_stage')

    mock_matured_heiferI = mocker.MagicMock(autospec=HeiferI)
    mock_matured_heiferI.update.return_value = False
    mock_matured_heiferI.mature_body_weight = mature_body_weight = 400.0

    mock_heiferIs: List[HeiferI] = [mock_heiferI_second_stage, mock_matured_heiferI]
    mock_heiferIIs: List[HeiferII] = []
    life_cycle_manager.heiferI_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    new_total_animal_num = life_cycle_manager._heiferI_to_heiferII(sim_day, mock_heiferIs,
                                                                   mock_heiferIIs,
                                                                   total_animal_num)

    mock_heiferI_second_stage.update.assert_called_once_with(sim_day)
    mock_move_heiferI_to_second_stage.assert_called_once_with(mock_heiferI_second_stage, mock_heiferIIs)

    mock_matured_heiferI.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.heiferI_num == 1

    assert len(mock_heiferIs) == 1
    assert mock_heiferIs[0] == mock_matured_heiferI
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)


def test_move_heiferII_to_third_stage(mocker: MockerFixture) -> None:
    """Unit test for function _move_heiferII_to_third_stage in file life_cycle.py"""
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
    LifeCycleManager._move_heiferII_to_third_stage(mock_heiferII, heiferIIIs)

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


def test_keep_heiferII_as_pregnant(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _keep_heiferII_as_pregnant in file life_cycle.py"""
    # Set up
    mock_heiferII = mocker.MagicMock(autospec=HeiferII)
    spy_extract_repro_stats = mocker.spy(life_cycle_manager, '_extract_repro_stats_from_heiferII')

    total_animal_num = 10
    life_cycle_manager.avg_mature_body_weight = 20.0
    mock_heiferII.mature_body_weight = 42.0

    preg_heifer_num = 10
    life_cycle_manager.avg_breeding_to_preg_time = 20.0
    mock_heiferII.breeding_to_preg_time = 42.0

    # Before
    assert life_cycle_manager.heiferII_num == 0
    assert life_cycle_manager.avg_mature_body_weight == approx(20.0)
    assert life_cycle_manager.avg_breeding_to_preg_time == approx(20.0)

    # Act
    result = life_cycle_manager._keep_heiferII_as_pregnant(mock_heiferII, total_animal_num, preg_heifer_num)
    new_total_animal_num, new_preg_heifer_num = result

    # After
    assert life_cycle_manager.heiferII_num == 1
    assert new_total_animal_num == 11
    assert life_cycle_manager.avg_mature_body_weight == approx(22.0)
    assert new_preg_heifer_num == 11
    assert life_cycle_manager.avg_breeding_to_preg_time == approx(22.0)
    spy_extract_repro_stats.assert_called_once()


def test_heiferII_to_heiferIII(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _heiferII_to_heiferIII in file life_cycle.py"""
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
    mock_move_heiferII_to_third_stage = mocker.patch.object(life_cycle_manager,
                                                            '_move_heiferII_to_third_stage')

    mock_heiferII_pregnant_stage = mocker.MagicMock(autospec=HeiferII)
    mock_heiferII_pregnant_stage.update.return_value = [False, False]  # cull_stage = False, third_stage = False
    mock_keep_heiferII_as_pregnant = mocker.patch.object(life_cycle_manager,
                                                         '_keep_heiferII_as_pregnant')
    mock_keep_heiferII_as_pregnant.return_value = (1, 1)  # new_total_animal_num = 1, new_preg_heifer_num = 1
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
    result = life_cycle_manager._heiferII_to_heiferIII(sim_day, mock_heiferIIs,
                                                       mock_heiferIIIs, preg_heifer_num,
                                                       total_animal_num)
    new_total_animal_num, new_preg_heifer_num = result

    # After
    assert life_cycle_manager.culled_heifer_num == 1
    assert life_cycle_manager.avg_heifer_culling_age == approx(100.0)
    assert len(life_cycle_manager.culled_heifers) == 1
    assert life_cycle_manager.culled_heifers[0] == mock_heiferII_cull_stage
    mock_heiferII_cull_stage.update.assert_called_once_with(sim_day)

    mock_move_heiferII_to_third_stage.assert_called_once_with(mock_heiferII_third_stage, mock_heiferIIIs)

    mock_keep_heiferII_as_pregnant.assert_called_once_with(mock_heiferII_pregnant_stage,
                                                           total_animal_num, preg_heifer_num)
    assert new_total_animal_num == 1
    assert new_preg_heifer_num == 1
    assert len(mock_heiferIIs) == 1
    assert mock_heiferIIs[0] == mock_heiferII_pregnant_stage


def test_move_heiferIII_to_cow_stage(mocker: MockerFixture) -> None:
    """Unit test for function _move_heiferIII_to_cow_stage in file life_cycle.py"""
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
        "cow_presynch_protocol": cow_presynch_protocol,
        "cow_TAI_protocol": cow_TAI_protocol,
        "cow_resynch_protocol": cow_resynch_protocol
    }
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalBase.config', animal_base_config)

    # Act
    LifeCycleManager._move_heiferIII_to_cow_stage(mock_heiferIII, cows)

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


def test_heiferIII_to_cow(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    """Unit test for function _heiferIII_to_cow in file life_cycle.py"""
    sim_day = 400
    mock_heiferIII_cow_stage = mocker.MagicMock(autospec=HeiferIII)
    mock_heiferIII_cow_stage.update.return_value = True
    mock_move_heiferIII_to_cow_stage = mocker.patch.object(life_cycle_manager,
                                                           '_move_heiferIII_to_cow_stage')

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
    new_total_animal_num = life_cycle_manager._heiferIII_to_cow(sim_day, mock_heiferIIIs,
                                                                mock_cows,
                                                                total_animal_num)

    # Assert after
    mock_heiferIII_cow_stage.update.assert_called_once_with(sim_day)
    mock_move_heiferIII_to_cow_stage.assert_called_once_with(mock_heiferIII_cow_stage, mock_cows)

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
    ids_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, ids_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 53
    assert len(mock_cows) == 50
    assert len(life_cycle_manager.sold_heifers) == 2
    assert life_cycle_manager.sold_heifer_num == 2
    assert ids_removed == [54, 53]
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
    ids_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, ids_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 53
    assert len(mock_cows) == 50
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0
    assert len(ids_removed) == 0
    # ---------------------------------------------------------------

    # Case 3: len(heiferIIIs) == 0
    # Arrange
    life_cycle_manager.herd_num = 100
    mock_heiferIIIs: List[HeiferIII] = []
    mock_cows: List[Cow] = [mocker.MagicMock(autospec=Cow)] * 104
    ids_removed = []
    life_cycle_manager.sold_heifers = []
    life_cycle_manager.sold_heifer_num = 0

    # Assert before
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0

    # Act
    life_cycle_manager._check_if_heifers_need_to_be_sold(mock_heiferIIIs, mock_cows, ids_removed)

    # Assert after
    assert len(mock_heiferIIIs) == 0
    assert len(mock_cows) == 104
    assert len(life_cycle_manager.sold_heifers) == 0
    assert life_cycle_manager.sold_heifer_num == 0
    assert len(ids_removed) == 0


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
    """Unit test for function _cull_cow in file life_cycle.py"""

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
    assert LifeCycleManager.cull_reason_stats[LOW_PROD_CULL] == 0
    assert len(life_cycle_manager.parity_culling_stats_range) == 0

    # Act
    life_cycle_manager._cull_cow(mock_cow)

    # Assert
    assert len(life_cycle_manager.culled_cows) == 1
    assert len(life_cycle_manager.cull_reason_stats_range) == 1
    assert LOW_PROD_CULL in life_cycle_manager.cull_reason_stats_range
    assert life_cycle_manager.cull_reason_stats_range[LOW_PROD_CULL] == 1
    assert LifeCycleManager.cull_reason_stats[LOW_PROD_CULL] == 1

    assert len(life_cycle_manager.parity_culling_stats_range) == 1
    assert parity in life_cycle_manager.parity_culling_stats_range
    assert life_cycle_manager.parity_culling_stats_range[parity] == 1

    assert life_cycle_manager.culled_cow_num == 1
    assert life_cycle_manager.avg_cow_culling_age == approx(100.0)


def test_handle_cow_body_weight():
    pass


def test_handle_cow_milking():
    pass


def test__handle_cow_days_in_milk():
    pass


def test_handle_cow_days_in_preg():
    pass


def test_handle_cow_calves():
    pass


def test_handle_cow_ci():
    pass


def test_extract_repro_stats_from_cow():
    pass


def test_handle_new_born():
    pass


def test__cull_cows_and_record_stats(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    pass
