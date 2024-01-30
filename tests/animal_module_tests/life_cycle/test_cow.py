from typing import Type

import pytest
from pytest_mock import MockFixture

from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import CowReproProtocolEnum, ReproStateEnum


def test_get_user_defined_milk_fat_percent(mocker: MockFixture) -> None:
    """
    Unit test for the method get_user_defined_milk_fat_percent() of the Cow class in cow.py.
    """

    # Arrange
    expected_milk_fat_percent = 3.5

    def mock_get_milk_fat_content(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in input_manager.py.
        """
        if key == 'animal.animal_config.management_decisions.milk_fat_percent':
            return expected_milk_fat_percent
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_milk_fat_content
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_milk_fat_percent = cow.get_user_defined_milk_fat_percent()

    # Assert
    assert actual_milk_fat_percent == expected_milk_fat_percent


def test_get_user_defined_milk_protein_percent(mocker: MockFixture) -> None:
    """
    Unit test for the method get_user_defined_milk_protein_percent() of the Cow class in cow.py.
    """

    # Arrange
    expected_milk_protein_percent = 3.0

    def mock_get_milk_protein_content(key: str):
        """
        Mock function for the method get_data() of the InputManager class in input_manager.py.
        """
        if key == 'animal.animal_config.management_decisions.milk_protein_percent':
            return expected_milk_protein_percent
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_milk_protein_content
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_milk_protein_percent = cow.get_user_defined_milk_protein_percent()

    # Assert
    assert actual_milk_protein_percent == expected_milk_protein_percent


@pytest.mark.parametrize(
    "calves, conception_rate, expected_conception_rate",
    [
        (0, 0.5, 0.5),
        (1, 0.5, 0.5),
        (2, 0.5, 0.45),
        (3, 0.5, 0.4),
    ]
)
def test_decrease_conception_rate_by_parity(
        mocker: MockFixture,
        calves: int,
        conception_rate: float,
        expected_conception_rate: float
) -> None:
    """
    Unit test for the _decrease_conception_rate_by_parity method of the Cow class in cow.py.
    """

    # Arrange
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    adjusted_conception_rate = cow._decrease_conception_rate_by_parity(calves, conception_rate)

    # Assert
    assert adjusted_conception_rate == expected_conception_rate


@pytest.mark.parametrize(
    "is_pregnant, days_in_milk, do_not_breed_time, should_mark_do_not_breed",
    [
        (False, 400, 300, True),
        (True, 400, 300, False),
        (False, 200, 300, False),
    ]
)
def test_check_do_not_breed_flag(
        mocker: MockFixture,
        is_pregnant: bool,
        days_in_milk: int,
        do_not_breed_time: int,
        should_mark_do_not_breed: bool
) -> None:
    """
    Unit test for the _check_do_not_breed_flag method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_in_milk = days_in_milk
    cow.do_not_breed = False
    cow.days_born = 100
    mocker.patch.object(Cow, 'is_pregnant', new_callable=mocker.PropertyMock, return_value=is_pregnant)
    mocker.patch.object(cow, 'get_do_not_breed_time', return_value=do_not_breed_time)
    patch_for_log_event = mocker.patch.object(cow, 'log_event')

    # Act
    cow._check_do_not_breed_flag(sim_day)

    # Assert
    if should_mark_do_not_breed:
        assert cow.do_not_breed
        patch_for_log_event.assert_called_once()
    else:
        assert not cow.do_not_breed
        patch_for_log_event.assert_not_called()


@pytest.mark.parametrize(
    "is_pregnant, loss_rate, expected_method_calls",
    [
        (True, 0, {'log_event': 1, 'terminate_pregnancy': 0, 'open': 0, 'is_in_state': 1}),
        (True, 1, {'log_event': 0, 'terminate_pregnancy': 1, 'open': 0, 'exit_state': 1}),
        (False, 0, {'log_event': 1, 'terminate_pregnancy': 0, 'open': 1}),
    ]
)
def test_handle_preg_check(
        mocker: MockFixture,
        is_pregnant: bool,
        loss_rate: float,
        expected_method_calls: dict[str, int]
) -> None:
    """
    Unit test for the _handle_preg_check method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    preg_check_config = {
        "loss_rate": loss_rate,
        "on_preg_loss": "Pregnancy lost",
        "on_preg": "Pregnancy continues",
        "on_not_preg": "Not pregnant"
    }
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow._repro_state_manager = mock_repro_state_manager = mocker.MagicMock()
    mocker.patch.object(Cow, 'is_pregnant', return_value=is_pregnant, new_callable=mocker.PropertyMock)
    cow.preg_diagnoses = 0
    cow.days_born = 100
    patch_for_log_event = mocker.patch.object(cow, 'log_event', return_value=None)
    mocker.patch.object(cow, '_compare_randomized_rate_less_than', return_value=(loss_rate > 0))
    patch_for_terminate_pregnancy = mocker.patch.object(cow, '_terminate_pregnancy', return_value=None)
    mocker.patch.object(cow, '_exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected')
    patch_for_open = mocker.patch.object(cow, 'open')

    # Act
    cow._handle_preg_check(preg_check_config, sim_day)

    # Assert
    assert cow.preg_diagnoses == 1
    if 'log_event' in expected_method_calls:
        assert patch_for_log_event.call_count == expected_method_calls['log_event']
    if 'terminate_pregnancy' in expected_method_calls:
        assert patch_for_terminate_pregnancy.call_count == expected_method_calls['terminate_pregnancy']
    if 'open' in expected_method_calls:
        assert patch_for_open.call_count == expected_method_calls['open']
    if 'exit_state' in expected_method_calls:
        assert mock_repro_state_manager.exit.call_count == expected_method_calls['exit_state']
    if 'is_in_state' in expected_method_calls:
        assert mock_repro_state_manager.is_in.call_count == expected_method_calls['is_in_state']


@pytest.mark.parametrize(
    "repro_program, resynch_program, expected_state, expected_method_call",
    [
        (CowReproProtocolEnum.ED.value, None,
         ReproStateEnum.WAITING_FULL_ED_CYCLE, '_simulate_estrus'),
        (CowReproProtocolEnum.TAI.value, CowReproProtocolEnum.Resynch_TAIbeforePD.value,
         None, '_handle_open_cow_in_tai_before_pd_resynch'),
        (CowReproProtocolEnum.TAI.value, CowReproProtocolEnum.Resynch_TAIafterPD.value,
         ReproStateEnum.IN_OVSYNCH, None),
        (CowReproProtocolEnum.ED_TAI.value, CowReproProtocolEnum.Resynch_TAIbeforePD.value,
         None, '_handle_open_cow_in_tai_before_pd_resynch'),
        (CowReproProtocolEnum.ED_TAI.value, CowReproProtocolEnum.Resynch_TAIafterPD.value,
         ReproStateEnum.IN_OVSYNCH, None),
        (CowReproProtocolEnum.TAI.value, CowReproProtocolEnum.Resynch_PGFatPD.value,
         None, '_handle_open_cow_in_pgf_at_pd_resynch'),
    ]
)
def test_open(mocker, repro_program, resynch_program, expected_state, expected_method_call):
    """
    Unit test for the open method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    days_born = 100
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_born = days_born
    cow.estrus_day = days_born - 1
    cow.days_in_milk = 100
    cow._num_conception_rate_decreases = 0
    cow.repro_program = repro_program
    cow._repro_state_manager = mock_repro_state_manager = mocker.MagicMock()
    mocker.patch.object(cow, 'get_resynch_program', return_value=resynch_program)
    mocker.patch.object(cow, 'log_event', return_value=None)
    mocker.patch.object(cow, 'get_avg_estrus_cycle', return_value=21)
    mocker.patch.object(cow, 'get_std_estrus_cycle', return_value=2.0)
    patch_for_expected_method = mocker.patch.object(cow, expected_method_call, return_value=None) \
        if expected_method_call else None
    patch_for_log_repro_states = mocker.patch.object(cow, '_log_repro_states', return_value=None)

    # Act
    cow.open(sim_day)

    # Assert
    assert cow._num_conception_rate_decreases == 1
    if expected_state:
        mock_repro_state_manager.enter.assert_called_once_with(expected_state)
        patch_for_log_repro_states.assert_called_once_with(sim_day)
    if expected_method_call:
        patch_for_expected_method.assert_called_once()


def test_handle_open_cow_in_pgf_at_pd_resynch(mocker: MockFixture) -> None:
    """
    Unit test for the _handle_open_cow_in_pgf_at_pd_resynch method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    days_born = 100
    avg_estrus_cycle_after_pgf = 4
    std_estrus_cycle_after_pgf = 2
    max_cycle_length = 7

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_born = days_born
    patch_for_execute_hormone_delivery_schedule = mocker.patch.object(cow, '_execute_hormone_delivery_schedule',
                                                                      return_value=None)
    patch_for_log_repro_states = mocker.patch.object(cow, '_log_repro_states',
                                                     return_value=None)
    patch_for_simulate_estrus = mocker.patch.object(cow, '_simulate_estrus',
                                                    return_value=None)
    cow._repro_state_manager = mock_repro_state_manager = mocker.MagicMock()
    mocker.patch.object(cow, 'get_avg_estrus_cycle_after_pgf',
                        return_value=avg_estrus_cycle_after_pgf)
    mocker.patch.object(cow, 'get_std_estrus_cycle_after_pgf',
                        return_value=std_estrus_cycle_after_pgf)

    # Act
    cow._handle_open_cow_in_pgf_at_pd_resynch(sim_day)

    # Assert
    single_pgf_injection_schedule = {days_born: {'deliver_hormones': ['PGF']}}
    patch_for_execute_hormone_delivery_schedule.assert_called_once_with(sim_day, single_pgf_injection_schedule)
    mock_repro_state_manager.enter.assert_called_once_with(ReproStateEnum.WAITING_SHORT_ED_CYCLE)
    patch_for_log_repro_states.assert_called_once_with(sim_day)
    patch_for_simulate_estrus.assert_called_once_with(days_born, sim_day, const.SIMULATE_ESTRUS_AFTER_PGF_NOTE,
                                                      avg_estrus_cycle_after_pgf, std_estrus_cycle_after_pgf,
                                                      max_cycle_length=max_cycle_length)


@pytest.mark.parametrize(
    "is_in_empty_state, is_waiting_full_ed_cycle, expected_enter_call, expected_exit_call, expected_log_event",
    [
        (True, False, True, False, False),
        (False, True, False, True, True),
        (True, True, True, True, True),
        (False, False, False, False, False),
    ]
)
def test_handle_open_cow_in_tai_before_pd_resynch(
        mocker: MockFixture,
        is_in_empty_state: bool,
        is_waiting_full_ed_cycle: bool,
        expected_enter_call: bool,
        expected_exit_call: bool,
        expected_log_event: bool
) -> None:
    """
    Unit test for the _handle_open_cow_in_tai_before_pd_resynch method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    days_born = 100

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_born = days_born
    cow._repro_state_manager = mock_repro_state_manager = mocker.MagicMock()
    patch_for_log_event = mocker.patch.object(cow, 'log_event', return_value=None)
    patch_for_log_repro_states = mocker.patch.object(cow, '_log_repro_states', return_value=None)
    mock_repro_state_manager.is_in_empty_state.return_value = is_in_empty_state
    mock_repro_state_manager.is_in.return_value = is_waiting_full_ed_cycle

    # Act
    cow._handle_open_cow_in_tai_before_pd_resynch(sim_day)

    # Assert
    if expected_enter_call:
        mock_repro_state_manager.enter.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)
        patch_for_log_repro_states.assert_called_once_with(sim_day)
    else:
        mock_repro_state_manager.enter.assert_not_called()

    if expected_exit_call:
        mock_repro_state_manager.exit.assert_called_once_with(ReproStateEnum.WAITING_FULL_ED_CYCLE)
    else:
        mock_repro_state_manager.exit.assert_not_called()

    if expected_log_event:
        patch_for_log_event.assert_called_once_with(cow.days_born, sim_day,
                                                    const.CANCEL_ESTRUS_DETECTION_NOTE)
    else:
        patch_for_log_event.assert_not_called()


def test_schedule_ovsynch_program_in_advance(mocker: MockFixture) -> None:
    """
    Unit test for the _schedule_ovsynch_program_in_advance method of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 150
    days_before_first_preg_check = 10
    days_born = 100
    first_preg_check_day = 30
    ov_synch_program = CowReproProtocolEnum.TAI_OvSynch_48.value
    ov_synch_conception_rate = 0.55

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_born = days_born
    patch_for_get_first_preg_check_day = mocker.patch.object(cow, 'get_first_preg_check_day',
                                                             return_value=first_preg_check_day)
    patch_for_get_ovsynch_program = mocker.patch.object(cow, 'get_ovsynch_program',
                                                        return_value=ov_synch_program)
    patch_for_get_ovsynch_program_conception_rate = mocker.patch.object(cow, 'get_ovsynch_program_conception_rate',
                                                                        return_value=ov_synch_conception_rate)
    patch_for_set_up_hormone_schedule = mocker.patch.object(cow, '_set_up_hormone_schedule',
                                                            return_value=None)
    patch_for_log_event = mocker.patch.object(cow, 'log_event',
                                              return_value=None)

    # Act
    cow._schedule_ovsynch_program_in_advance(sim_day, days_before_first_preg_check)

    # Assert
    hormone_schedule_start_day = days_born + first_preg_check_day - days_before_first_preg_check
    patch_for_get_first_preg_check_day.assert_called_once()
    assert patch_for_get_ovsynch_program.call_count == 2
    patch_for_set_up_hormone_schedule.assert_called_once_with('cows', ov_synch_program, hormone_schedule_start_day)
    assert cow._TAI_conception_rate == ov_synch_conception_rate
    patch_for_get_ovsynch_program_conception_rate.assert_called_once()
    patch_for_log_event.assert_called_once()


def test_exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(mocker: MockFixture) -> None:
    """
    Unit test for the _exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected method
    of the Cow class in cow.py.
    """

    # Arrange
    sim_day = 120
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.days_born = 100
    cow._repro_state_manager = mock_repro_state_manager = mocker.MagicMock()
    cow._hormone_schedule = {'SomeHormone': 'SomeSchedule'}
    patch_for_log_event = mocker.patch.object(cow, 'log_event', return_value=None)
    patch_for_get_ovsynch_program = mocker.patch.object(cow, 'get_ovsynch_program',
                                                        return_value=CowReproProtocolEnum.TAI_OvSynch_48.value)

    # Act
    cow._exit_ovsynch_program_early_when_first_preg_check_passed_or_estrus_detected(sim_day)

    # Assert
    mock_repro_state_manager.exit.assert_called_once_with(ReproStateEnum.IN_OVSYNCH)
    assert cow._hormone_schedule == {}
    patch_for_log_event.assert_called_once()
    patch_for_get_ovsynch_program.assert_called_once()


@pytest.mark.parametrize(
    "sim_day, repro_program, expected_exception, expected_repro_program", [
        (100, CowReproProtocolEnum.ED.value, None, CowReproProtocolEnum.ED.value),
        (200, CowReproProtocolEnum.TAI.value, None, CowReproProtocolEnum.TAI.value),
        (300, CowReproProtocolEnum.ED_TAI.value, None, CowReproProtocolEnum.ED_TAI.value),
        (400, "InvalidProgram", ValueError, None),
    ])
def test_set_repro_program(
        mocker: MockFixture,
        sim_day: int,
        repro_program: str,
        expected_exception: Type[Exception] | None,
        expected_repro_program: str | None
) -> None:
    """
    Unit test for the _set_repro_program method of the Cow class in cow.py.
    """

    # Arrange
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())
    cow.repro_program = "SomeProgram"
    cow.days_born = 100
    patch_for_log_event = mocker.patch.object(cow, 'log_event', return_value=None)

    if expected_exception:
        # Act & Assert
        with pytest.raises(expected_exception):
            cow._set_repro_program(sim_day, repro_program)
    else:
        # Act
        cow._set_repro_program(sim_day, repro_program)

        # Assert
        assert cow.repro_program == expected_repro_program
        patch_for_log_event.assert_called_once()


def test_get_first_preg_check_day(mocker: MockFixture) -> None:
    """
    Unit test for the method get_first_preg_check_day() of the Cow class in cow.py.
    """

    # Arrange
    expected_preg_check_day = 30

    def mock_get_preg_check_day_1(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class used in cow.py
        to get the first pregnancy check day.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_check_day_1':
            return expected_preg_check_day
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_check_day_1
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_preg_check_day = cow.get_first_preg_check_day()

    # Assert
    assert actual_preg_check_day == expected_preg_check_day


def test_get_second_preg_check_day(mocker: MockFixture) -> None:
    """
    Unit test for the method get_second_preg_check_day() of the Cow class in cow.py.
    """

    # Arrange
    expected_preg_check_day = 60

    def mock_get_preg_check_day_2(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the second pregnancy check day.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_check_day_2':
            return expected_preg_check_day
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_check_day_2
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_preg_check_day = cow.get_second_preg_check_day()

    # Assert
    assert actual_preg_check_day == expected_preg_check_day


def test_get_third_preg_check_day(mocker: MockFixture) -> None:
    """
    Unit test for the method get_third_preg_check_day() of the Cow class in cow.py.
    """

    # Arrange
    expected_preg_check_day = 90

    def mock_get_preg_check_day_3(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the third pregnancy check day.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_check_day_3':
            return expected_preg_check_day
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_check_day_3
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_preg_check_day = cow.get_third_preg_check_day()

    # Assert
    assert actual_preg_check_day == expected_preg_check_day


def test_get_first_preg_check_loss_rate(mocker: MockFixture) -> None:
    """
    Unit test for the method get_first_preg_check_loss_rate() of the Cow class in cow.py.
    """

    # Arrange
    expected_loss_rate = 0.1

    def mock_get_preg_loss_rate_1(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the first pregnancy check loss rate.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_loss_rate_1':
            return expected_loss_rate
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_loss_rate_1
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_loss_rate = cow.get_first_preg_check_loss_rate()

    # Assert
    assert actual_loss_rate == expected_loss_rate


def test_get_second_preg_check_loss_rate(mocker: MockFixture) -> None:
    """
    Unit test for the method get_second_preg_check_loss_rate() of the Cow class in cow.py.
    """

    # Arrange
    expected_loss_rate = 0.15

    def mock_get_preg_loss_rate_2(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the second pregnancy check loss rate.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_loss_rate_2':
            return expected_loss_rate
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_loss_rate_2
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_loss_rate = cow.get_second_preg_check_loss_rate()

    # Assert
    assert actual_loss_rate == expected_loss_rate


def test_get_third_preg_check_loss_rate(mocker: MockFixture) -> None:
    """
    Unit test for the method get_third_preg_check_loss_rate() of the Cow class in cow.py.
    """

    # Arrange
    expected_loss_rate = 0.2

    def mock_get_preg_loss_rate_3(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the third pregnancy check loss rate.
        """
        if key == 'animal.animal_config.from_literature.repro.preg_loss_rate_3':
            return expected_loss_rate
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_preg_loss_rate_3
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_loss_rate = cow.get_third_preg_check_loss_rate()

    # Assert
    assert actual_loss_rate == expected_loss_rate


def test_get_do_not_breed_time(mocker: MockFixture) -> None:
    """
    Unit test for the method get_do_not_breed_time() of the Cow class in cow.py.
    """

    # Arrange
    expected_do_not_breed_time = 200

    def mock_get_do_not_breed_time(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the do-not-breed time.
        """
        if key == 'animal.animal_config.management_decisions.do_not_breed_time':
            return expected_do_not_breed_time
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_do_not_breed_time
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_do_not_breed_time = cow.get_do_not_breed_time()

    # Assert
    assert actual_do_not_breed_time == expected_do_not_breed_time


def test_get_avg_estrus_cycle(mocker: MockFixture) -> None:
    """
    Unit test for the method get_avg_estrus_cycle() of the Cow class in cow.py.
    """

    # Arrange
    expected_avg_estrus_cycle = 21

    def mock_get_avg_estrus_cycle(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the average estrus cycle length.
        """
        if key == 'animal.animal_config.from_literature.repro.avg_estrus_cycle_cow':
            return expected_avg_estrus_cycle
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_avg_estrus_cycle
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_avg_estrus_cycle = cow.get_avg_estrus_cycle()

    # Assert
    assert actual_avg_estrus_cycle == expected_avg_estrus_cycle


def test_get_std_estrus_cycle(mocker: MockFixture) -> None:
    """
    Unit test for the method get_std_estrus_cycle() of the Cow class in cow.py.
    """

    # Arrange
    expected_std_estrus_cycle = 2.0

    def mock_get_std_estrus_cycle(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the standard deviation of the estrus cycle.
        """
        if key == 'animal.animal_config.from_literature.repro.std_estrus_cycle_cow':
            return expected_std_estrus_cycle
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_std_estrus_cycle
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_std_estrus_cycle = cow.get_std_estrus_cycle()

    # Assert
    assert actual_std_estrus_cycle == expected_std_estrus_cycle


def test_get_avg_estrus_cycle_return(mocker: MockFixture) -> None:
    """
    Unit test for the method get_avg_estrus_cycle_return() of the Cow class in cow.py.
    """

    # Arrange
    expected_avg_estrus_cycle_return = 18

    def mock_get_avg_estrus_cycle_return(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the average return estrus cycle length.
        """
        if key == 'animal.animal_config.from_literature.repro.avg_estrus_cycle_return':
            return expected_avg_estrus_cycle_return
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_avg_estrus_cycle_return
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_avg_estrus_cycle_return = cow.get_avg_estrus_cycle_return()

    # Assert
    assert actual_avg_estrus_cycle_return == expected_avg_estrus_cycle_return


def test_get_std_estrus_cycle_return(mocker: MockFixture) -> None:
    """
    Unit test for the method get_std_estrus_cycle_return() of the Cow class in cow.py.
    """

    # Arrange
    expected_std_estrus_cycle_return = 1.5

    def mock_get_std_estrus_cycle_return(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the standard deviation of the return estrus cycle.
        """
        if key == 'animal.animal_config.from_literature.repro.std_estrus_cycle_return':
            return expected_std_estrus_cycle_return
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_std_estrus_cycle_return
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_std_estrus_cycle_return = cow.get_std_estrus_cycle_return()

    # Assert
    assert actual_std_estrus_cycle_return == expected_std_estrus_cycle_return


def test_get_voluntary_waiting_period(mocker: MockFixture) -> None:
    """
    Unit test for the method get_voluntary_waiting_period() of the Cow class in cow.py.
    """

    # Arrange
    expected_voluntary_waiting_period = 60

    def mock_get_voluntary_waiting_period(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the voluntary waiting period for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.voluntary_waiting_period':
            return expected_voluntary_waiting_period
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_voluntary_waiting_period
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_voluntary_waiting_period = cow.get_voluntary_waiting_period()

    # Assert
    assert actual_voluntary_waiting_period == expected_voluntary_waiting_period


def test_get_presynch_program_start_day(mocker: MockFixture) -> None:
    """
    Unit test for the method get_presynch_program_start_day() of the Cow class in cow.py.
    """

    # Arrange
    expected_presynch_program_start_day = 35

    def mock_get_presynch_program_start_day(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the presynch program start day for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.presynch_program_start_day':
            return expected_presynch_program_start_day
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_presynch_program_start_day
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_presynch_program_start_day = cow.get_presynch_program_start_day()

    # Assert
    assert actual_presynch_program_start_day == expected_presynch_program_start_day


def test_get_ovsynch_program_start_day(mocker: MockFixture) -> None:
    """
    Unit test for the method get_ovsynch_program_start_day() of the Cow class in cow.py.
    """

    # Arrange
    expected_ovsynch_program_start_day = 45

    def mock_get_ovsynch_program_start_day(key: str) -> int | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the OvSynch program start day for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.ovsynch_program_start_day':
            return expected_ovsynch_program_start_day
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_ovsynch_program_start_day
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_ovsynch_program_start_day = cow.get_ovsynch_program_start_day()

    # Assert
    assert actual_ovsynch_program_start_day == expected_ovsynch_program_start_day


def test_get_conception_rate_decrease(mocker: MockFixture) -> None:
    """
    Unit test for the method get_conception_rate_decrease() of the Cow class in cow.py.
    """

    # Arrange
    expected_conception_rate_decrease = 0.1

    def mock_get_conception_rate_decrease(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the conception rate decrease for cows during rebreeding.
        """
        if key == 'animal.animal_config.farm_level.repro.conception_rate_decrease':
            return expected_conception_rate_decrease
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_conception_rate_decrease
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_conception_rate_decrease = cow.get_conception_rate_decrease()

    # Assert
    assert actual_conception_rate_decrease == expected_conception_rate_decrease


def test_get_user_defined_repro_protocol(mocker: MockFixture) -> None:
    """
    Unit test for the method get_user_defined_repro_protocol() of the Cow class in cow.py.
    """

    # Arrange
    expected_repro_protocol = 'TAI'

    def mock_get_user_defined_repro_protocol(key: str) -> str | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the user-defined reproduction protocol for cows.
        """
        if key == 'animal.animal_config.management_decisions.cow_repro_method':
            return expected_repro_protocol
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_user_defined_repro_protocol
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_repro_protocol = cow.get_user_defined_repro_protocol()

    # Assert
    assert actual_repro_protocol == expected_repro_protocol


def test_get_ovsynch_program(mocker: MockFixture) -> None:
    """
    Unit test for the method get_ovsynch_program() of the Cow class in cow.py.
    """

    # Arrange
    expected_ovsynch_program = 'OvSynch 48'

    def mock_get_ovsynch_program(key: str) -> str | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the OvSynch program for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.ovsynch_program':
            return expected_ovsynch_program
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_ovsynch_program
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_ovsynch_program = cow.get_ovsynch_program()

    # Assert
    assert actual_ovsynch_program == expected_ovsynch_program


def test_get_presynch_program(mocker: MockFixture) -> None:
    """
    Unit test for the method get_presynch_program() of the Cow class in cow.py.
    """

    # Arrange
    expected_presynch_program = 'PreSynch'

    def mock_get_presynch_program(key: str) -> str | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the presynch program for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.presynch_program':
            return expected_presynch_program
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_presynch_program
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_presynch_program = cow.get_presynch_program()

    # Assert
    assert actual_presynch_program == expected_presynch_program


def test_get_resynch_program(mocker: MockFixture) -> None:
    """
    Unit test for the method get_resynch_program() of the Cow class in cow.py.
    """

    # Arrange
    expected_resynch_program = 'TAIBeforePD'

    def mock_get_resynch_program(key: str) -> str | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the resynch program for cows.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.resynch_program':
            return expected_resynch_program
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_resynch_program
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_resynch_program = cow.get_resynch_program()

    # Assert
    assert actual_resynch_program == expected_resynch_program


def test_get_ovsynch_program_conception_rate(mocker: MockFixture) -> None:
    """
    Unit test for the method get_ovsynch_program_conception_rate() of the Cow class in cow.py.
    """

    # Arrange
    expected_conception_rate = 0.55

    def mock_get_ovsynch_program_conception_rate(key: str) -> float | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the conception rate for OvSynch programs.
        """
        if key == 'animal.animal_config.farm_level.repro.cows.ovsynch_program_conception_rate':
            return expected_conception_rate
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_get_ovsynch_program_conception_rate
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_conception_rate = cow.get_ovsynch_program_conception_rate()

    # Assert
    assert actual_conception_rate == expected_conception_rate


def test_should_decrease_conception_rate_in_rebreeding(mocker: MockFixture) -> None:
    """
    Unit test for the method should_decrease_conception_rate_in_rebreeding() of the Cow class in cow.py.
    """

    # Arrange
    expected_decision = True

    def mock_should_decrease_conception_rate_in_rebreeding(key: str) -> bool | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the user choice for decreasing conception rate during rebreeding.
        """
        if key == 'animal.animal_config.farm_level.repro.decrease_conception_rate_in_rebreeding':
            return expected_decision
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_should_decrease_conception_rate_in_rebreeding
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_decision = cow.should_decrease_conception_rate_in_rebreeding()

    # Assert
    assert actual_decision == expected_decision


def test_should_decrease_conception_rate_by_parity(mocker: MockFixture) -> None:
    """
    Unit test for the method should_decrease_conception_rate_by_parity() of the Cow class in cow.py.
    """

    # Arrange
    expected_user_choice = True

    def mock_should_decrease_conception_rate_by_parity(key: str) -> bool | None:
        """
        Mock function for the method get_data() of the InputManager class in cow.py
        to get the user choice for decreasing conception rate based on the cow's parity.
        """
        if key == 'animal.animal_config.farm_level.repro.decrease_conception_rate_by_parity':
            return expected_user_choice
        return None

    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.im.get_data',
        side_effect=mock_should_decrease_conception_rate_by_parity
    )
    mocker.patch(
        'RUFAS.routines.animal.life_cycle.cow.Cow.__init__',
        return_value=None
    )
    cow = Cow(args=mocker.MagicMock())

    # Act
    actual_user_choice = cow.should_decrease_conception_rate_by_parity()

    # Assert
    assert actual_user_choice == expected_user_choice
