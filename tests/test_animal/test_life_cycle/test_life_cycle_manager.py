from pytest import approx, fixture, raises
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
from RUFAS.routines.animal.life_cycle.life_cycle import calc_average, \
    LifeCycleManager, percent_calculator, remove_items_from_list_by_indices


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
    lcm = LifeCycleManager(data=mocker.MagicMock(autospec=AnimalConfigTypedDict))
    return lcm


def test__set_avg_CI_should_set_custom_avg_CI_given_user_input_CI(mocker: MockerFixture,
                                                                  life_cycle_manager) -> None:
    mock_animal_config_data = {
        'user_input_calving_interval': True,
        'calving_interval': 400.0
    }
    mock_animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)
    mock_animal_config.__getitem__.side_effect = mock_animal_config_data.__getitem__
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)

    spy__set_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')
    assert life_cycle_manager.avg_CI == approx(0.0)

    life_cycle_manager._set_avg_CI(mock_animal_config, mock_animal_initializer)

    assert life_cycle_manager.avg_CI == approx(400.0)
    spy__set_avg_CI.assert_called_once()


def test__set_avg_CI_should_use_cow_avg_CI_given_no_user_input_CI(mocker: MockerFixture,
                                                                  life_cycle_manager) -> None:
    mock_animal_config_data = {
        'user_input_calving_interval': False
    }
    mock_animal_config = mocker.MagicMock(autospec=AnimalConfigTypedDict)
    mock_animal_config.__getitem__.side_effect = mock_animal_config_data.__getitem__

    mock_init_db_summary = {
        'cow_avg_CI': 500.0
    }
    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_animal_initializer.initialization_db_summary.return_value = mock_init_db_summary

    spy__get_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')
    assert life_cycle_manager.avg_CI == approx(0.0)

    life_cycle_manager._set_avg_CI(mock_animal_config, mock_animal_initializer)

    assert life_cycle_manager.avg_CI == approx(500.0)
    spy__get_avg_CI.assert_called_once()
    mock_animal_initializer.initialization_db_summary.assert_called_once()


def test__get_calves(mocker: MockerFixture, life_cycle_manager) -> None:
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
    spy__get_calves = mocker.spy(life_cycle_manager, '_get_calves')

    calves = life_cycle_manager._get_calves(calf_num, breed, mock_animal_initializer)

    assert len(calves) == calf_num
    for calf in calves:
        assert calf.breed == breed
        calf.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy__get_calves.assert_called_once_with(calf_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_calves.assert_called_once_with(calf_num, breed)


def test__get_heiferIs(mocker: MockerFixture, life_cycle_manager) -> None:
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
    spy__get_heiferIs = mocker.spy(life_cycle_manager, '_get_heiferIs')

    heiferIs = life_cycle_manager._get_heiferIs(heiferI_num, breed, mock_animal_initializer)

    assert len(heiferIs) == heiferI_num
    for heiferI in heiferIs:
        assert heiferI.breed == breed
        heiferI.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy__get_heiferIs.assert_called_once_with(heiferI_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIs.assert_called_once_with(heiferI_num, breed)


def test__get_heiferIIs(mocker: MockerFixture, life_cycle_manager) -> None:
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
    spy__get_heiferIIs = mocker.spy(life_cycle_manager, '_get_heiferIIs')

    heiferIIs = life_cycle_manager._get_heiferIIs(heiferII_num, breed, mock_animal_initializer)

    assert len(heiferIIs) == heiferII_num
    for heiferII in heiferIIs:
        assert heiferII.breed == breed
        heiferII.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy__get_heiferIIs.assert_called_once_with(heiferII_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIIs.assert_called_once_with(heiferII_num, breed)


def test__get_heiferIIIs(mocker: MockerFixture, life_cycle_manager) -> None:
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
    spy__get_heiferIIIs = mocker.spy(life_cycle_manager, '_get_heiferIIIs')

    heiferIIIs = life_cycle_manager._get_heiferIIIs(heiferIII_num, breed, mock_animal_initializer)

    assert len(heiferIIIs) == heiferIII_num
    for heiferIII in heiferIIIs:
        assert heiferIII.breed == breed
        heiferIII.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy__get_heiferIIIs.assert_called_once_with(heiferIII_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_heiferIIIs.assert_called_once_with(heiferIII_num, breed)


def test__get_cows(mocker: MockerFixture, life_cycle_manager) -> None:
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
    spy__get_cows = mocker.spy(life_cycle_manager, '_get_cows')

    cows = life_cycle_manager._get_cows(cow_num, breed, mock_animal_initializer)

    assert len(cows) == cow_num
    for cow in cows:
        assert cow.breed == breed
        cow.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)

    spy__get_cows.assert_called_once_with(cow_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_cows.assert_called_once_with(cow_num, breed)


def test_initialize_herd(mocker: MockerFixture, life_cycle_manager, herd_data: HerdInfoTypedDict) -> None:
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

    spy__set_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')
    spy__get_calves = mocker.spy(life_cycle_manager, '_get_calves')
    spy__get_heiferIs = mocker.spy(life_cycle_manager, '_get_heiferIs')
    spy__get_heiferIIs = mocker.spy(life_cycle_manager, '_get_heiferIIs')
    spy__get_heiferIIIs = mocker.spy(life_cycle_manager, '_get_heiferIIIs')
    spy__get_cows = mocker.spy(life_cycle_manager, '_get_cows')

    mock_animal_initializer = mocker.MagicMock(autospec=AnimalInitialization)
    mock_replacement_cows = [mocker.MagicMock(autospec=Cow) for _ in range(replace_num)]
    mock_animal_initializer.get_replacement_cows.return_value = mock_replacement_cows
    mocker.patch('RUFAS.routines.animal.life_cycle.life_cycle.AnimalInitialization',
                 return_value=mock_animal_initializer)

    results = life_cycle_manager.initialize_herd(herd_num, calf_num, heiferI_num, heiferII_num,
                                                 heiferIII_num, cow_num, replace_num, herd_init,
                                                 breed, mock_config)

    assert life_cycle_manager.herd_num == herd_data['herd_num']
    spy__set_avg_CI.assert_called_once_with(mock_animal_config, mock_animal_initializer)
    spy__get_calves.assert_called_once_with(calf_num, breed, mock_animal_initializer)
    spy__get_heiferIs.assert_called_once_with(heiferI_num, breed, mock_animal_initializer)
    spy__get_heiferIIs.assert_called_once_with(heiferII_num, breed, mock_animal_initializer)
    spy__get_heiferIIIs.assert_called_once_with(heiferIII_num, breed, mock_animal_initializer)
    spy__get_cows.assert_called_once_with(cow_num, breed, mock_animal_initializer)
    mock_animal_initializer.get_replacement_cows.assert_called_once_with(replace_num, breed)
    assert life_cycle_manager.replacement_market == mock_replacement_cows
    assert len(results) == 5


def test_calc_average_should_pass_given_valid_inputs() -> None:
    result = calc_average(num_values=9, cur_avg=5, new_value=6)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 10
    assert actual_new_avg == approx(5.1)  # (9 * 5 + 6) / 10


def test_calc_average_should_pass_given_zero_count_and_zero_avg() -> None:
    result = calc_average(num_values=0, cur_avg=0.0, new_value=6.0)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 1
    assert actual_new_avg == approx(6.0)


def test_calc_average_should_pass_given_one_count_and_zero_avg() -> None:
    result = calc_average(num_values=1, cur_avg=0.0, new_value=6.0)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 2
    assert actual_new_avg == approx(3.0)


def test_remove_items_from_list_by_indices_should_do_nothing_given_empty_list_and_empty_removed_indices() -> None:
    arr = []
    removed_idx = []
    remove_items_from_list_by_indices(arr, removed_idx)
    assert len(arr) == 0


def test_remove_items_from_list_by_indices_should_do_nothing_given_nonempty_list_and_empty_removed_indices() -> None:
    arr = [0, 1, 2]
    removed_idx = []
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [0, 1, 2]


def test_remove_items_from_list_by_indices_should_get_empty_list_given_sized_one_list_and_one_removed_index() -> None:
    arr = [0]
    removed_idx = [0]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert len(arr) == 0


def test_remove_items_from_list_by_indices_should_pass_given_sized_two_list_and_one_removed_index() -> None:
    arr = [10, 20]
    removed_idx = [0]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [20]

    arr = [10, 20]
    removed_idx = [1]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [10]


def test_remove_items_from_list_by_indices_should_pass_given_sized_three_list_and_two_removed_indices() -> None:
    arr = [10, 20, 30]
    removed_idx = [0, 1]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [30]

    arr = [10, 20, 30]
    removed_idx = [1, 2]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [10]

    arr = [10, 20, 30]
    removed_idx = [0, 2]
    remove_items_from_list_by_indices(arr, removed_idx)
    assert arr == [20]


def test_remove_items_from_list_by_indices_should_raise_index_error_given_empty_list_and_nonempty_removed_indices() \
        -> None:
    arr = []
    removed_idx = [0]
    with raises(IndexError):
        remove_items_from_list_by_indices(arr, removed_idx)


def test_percent_calculator_should_get_numerator_as_pct_given_denominator_100() -> None:
    pc = percent_calculator(denominator=100)
    assert pc(0.0) == approx(0.0)
    assert pc(12.3) == approx(12.3)
    assert pc(100.0) == approx(100.0)


def test_percent_calculator_should_pass_given_valid_denominator() -> None:
    pc = percent_calculator(denominator=20)
    assert pc(0) == approx(0.0)
    assert pc(20) == approx(100.0)
    assert pc(8) == approx(40.0)
    assert pc(-8) == approx(-40.0)
    assert pc(24) == approx(120.0)


def test_percent_calculator_should_raise_zero_division_error_given_denominator_0() -> None:
    pc = percent_calculator(denominator=0)
    with raises(ZeroDivisionError):
        pc(1.0)
