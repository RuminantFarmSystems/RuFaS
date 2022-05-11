from pytest import approx, fixture, raises
from pytest_mock import MockerFixture

from RUFAS.routines.animal.life_cycle.animal_constants import INIT_HERD
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.life_cycle import calc_average, \
    LifeCycleManager, percent_calculator, remove_items_from_list_by_indices


@fixture
def herd_data():
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
    data = mocker.MagicMock()
    lcm = LifeCycleManager(data)
    return lcm


def test__set_avg_CI_should_set_custom_avg_CI_given_user_input_CI(mocker: MockerFixture,
                                                                  life_cycle_manager: LifeCycleManager) -> None:
    data = {
        'user_input_calving_interval': True,
        'calving_interval': 400.0
    }
    mocker.patch.object(life_cycle_manager, 'animal_config', data)
    spy__set_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')

    assert life_cycle_manager.avg_CI == approx(0.0)
    life_cycle_manager._set_avg_CI()
    assert life_cycle_manager.avg_CI == approx(400.0)

    spy__set_avg_CI.assert_called_once()


def test__set_avg_CI_should_use_cow_avg_CI_given_no_user_input_CI(mocker: MockerFixture, life_cycle_manager) -> None:
    data = {
        'user_input_calving_interval': False,
    }
    mocker.patch.object(life_cycle_manager, 'animal_config', data)

    mock_animal_initializer = mocker.MagicMock()
    mock_animal_initializer.initialization_db_summary.return_value = {'cow_avg_CI': 500.0}
    mocker.patch.object(life_cycle_manager, 'animal_initializer', mock_animal_initializer)
    spy__get_avg_CI = mocker.spy(life_cycle_manager, '_set_avg_CI')

    assert life_cycle_manager.avg_CI == approx(0.0)
    life_cycle_manager._set_avg_CI()
    assert life_cycle_manager.avg_CI == approx(500.0)

    spy__get_avg_CI.assert_called_once()
    mock_animal_initializer.initialization_db_summary.assert_called_once()


def test__get_calves(mocker: MockerFixture, life_cycle_manager: LifeCycleManager) -> None:
    calf_num = 10
    breed = 'HO'
    days_born = 50

    mock_calves = []
    for i in range(calf_num):
        new_calf = mocker.MagicMock(autospec=Calf)
        new_calf.breed = breed
        new_calf.days_born = days_born
        mock_calves.append(new_calf)

    mock_animal_initializer = mocker.MagicMock()
    mock_animal_initializer.get_calves.return_value = mock_calves
    mocker.patch.object(life_cycle_manager, 'animal_initializer', mock_animal_initializer)

    spy__get_calves = mocker.spy(life_cycle_manager, '_get_calves')
    calves = life_cycle_manager._get_calves(calf_num, breed)

    spy__get_calves.assert_called_once_with(calf_num, breed)
    mock_animal_initializer.get_calves.assert_called_once_with(calf_num, breed)

    assert len(calves) == calf_num
    for idx, calf in enumerate(calves):
        assert calf.breed == 'HO'
        calf.events.add_event.assert_called_once_with(days_born, 0, INIT_HERD)


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
