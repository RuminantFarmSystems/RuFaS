from typing import Dict, List

from pytest import approx, fixture
from pytest_mock import MockerFixture

from RUFAS.classes import Config
from RUFAS.routines.animal.animal_typed_dicts import AnimalConfigTypedDict, HerdInfoTypedDict
from RUFAS.routines.animal.life_cycle.animal_constants import INIT_HERD
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
        mock_new_heiferIII = mocker.MagicMock(autospec=HeiferII)
        mock_new_heiferIII.breed = breed
        mock_new_heiferIII.days_born = days_born
        mock_heiferIIs.append(mock_new_heiferIII)
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


def test_initialize_herd(mocker: MockerFixture, life_cycle_manager, herd_data: HerdInfoTypedDict) -> None:
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
    calf_pen_history = [mocker.MagicMock(autospec=Pen) for _ in range(3)]

    calf = mocker.MagicMock(autospec=Calf)
    calf.body_weight_history = calf_body_weight_history
    calf.pen_history = calf_pen_history

    mock_args = mocker.MagicMock(autospec=Dict)
    calf.get_calf_values.return_value = mock_args

    heiferIs: List[HeiferI] = []
    mock_new_heiferI = mocker.MagicMock(autospec=HeiferI)
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.HeiferI',
                 return_value=mock_new_heiferI)
    LifeCycleManager._wean_calf(calf, heiferIs)

    mock_args.update.assert_called_once_with({
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
    mock__wean_calf = mocker.patch.object(life_cycle_manager, '_wean_calf')

    mock_matured_calf = mocker.MagicMock(autospec=Calf)
    mock_matured_calf.update.return_value = False
    mock_matured_calf.mature_body_weight = mature_body_weight = 200.0

    calves: List[Calf] = [mock_weaned_calf, mock_matured_calf]
    heiferIs: List[HeiferI] = []
    life_cycle_manager.calf_num = 0
    total_animal_num = 0
    life_cycle_manager.avg_mature_body_weight = 0.0

    new_total_animal_num = life_cycle_manager._calf_to_heiferI(sim_day, calves, heiferIs, total_animal_num)

    mock_weaned_calf.update.assert_called_once_with(sim_day)
    mock__wean_calf.assert_called_once_with(mock_weaned_calf, heiferIs)

    mock_matured_calf.update.assert_called_once_with(sim_day)
    assert life_cycle_manager.calf_num == 1

    assert len(calves) == 1
    assert calves[0] == mock_matured_calf
    assert new_total_animal_num == 1
    assert life_cycle_manager.avg_mature_body_weight == approx(mature_body_weight)
