from typing import Any

import pytest
from pytest_mock import MockerFixture
from scipy.stats import truncnorm

from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.hormone_delivery_schedule import HormoneDeliverySchedule
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum
from RUFAS.routines.animal.life_cycle.repro_protocol_misc import InternalReproSettings


@pytest.mark.parametrize(
    "start_day, sim_day, estrus_note,"
    "estrus_cycle, days_born, stdi, avg_estrus_cycle, std_estrus_cycle,"
    "expected_estrus_day",
    [
        # Normal estrus cycle
        (100, 120, "Test Estrus",
         20, 2.0, 100, 20, 5.0,
         120),

        # Negative estrus cycle
        (100, 120, "Negative Cycle",
         -10, 100, 2.0, 20, 5.0,
         110),

        # Very high estrus cycle
        (100, 120, "High Cycle",
         50, 100, 2.0, 20, 5.0,
         150),

        # Zero estrus cycle
        (100, 120, "Zero Cycle",
         0, 100, 2.0, 20, 5.0,
         100),

        # Different stdi values
        (100, 120, "Different STDI",
         20, 100, 1.0, 20, 5.0,
         120),
        (100, 120, "Different STDI",
         20, 100, 3.0, 20, 5.0,
         120),

        # Different average and standard deviation of estrus cycle
        (100, 120, "Different Avg and Std",
         15, 100, 2.0, 15, 4.0,
         115),
        (100, 120, "Different Avg and Std",
         25, 100, 2.0, 25, 6.0,
         125),
    ]
)
def test_simulate_estrus(mocker: MockerFixture, start_day: int, sim_day: int, estrus_note: str,
                         estrus_cycle: int, days_born: int, stdi: float,
                         avg_estrus_cycle: int, std_estrus_cycle: int,
                         expected_estrus_day: int) -> None:
    """
    Unit test for _simulate_estrus() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    patch_for_truncnorm = mocker.patch('scipy.stats.truncnorm.rvs', return_value=estrus_cycle)
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    mock_init_args = mocker.MagicMock()
    heifer = HeiferII(mock_init_args)
    heifer.days_born = days_born
    patch_for_log_event = mocker.patch.object(heifer, 'log_event')
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.STDI', stdi)
    mocker.patch.object(HeiferII, 'get_avg_estrus_cycle', return_value=avg_estrus_cycle)
    mocker.patch.object(HeiferII, 'get_std_estrus_cycle', return_value=std_estrus_cycle)

    # Act
    heifer._simulate_estrus(start_day, sim_day, estrus_note)

    # Assert
    assert heifer.estrus_day == expected_estrus_day
    patch_for_truncnorm.assert_called_with(-stdi, stdi, avg_estrus_cycle, std_estrus_cycle)
    patch_for_log_event.assert_called_with(days_born, sim_day, f'{estrus_note} on day {expected_estrus_day}')


@pytest.mark.parametrize(
    "start_day, sim_day, estrus_note, estrus_cycle, days_born, stdi, "
    "avg_estrus_cycle_after_pgf, std_estrus_cycle_after_pgf, expected_estrus_day",
    [
        # Normal estrus cycle
        (100, 120, "SynchED Estrus", 10, 100, 2.0, 10, 5.0, 110),

        # Estrus cycle exceeding max length
        (100, 120, "Long Estrus Cycle", 20, 100, 2.0, 20, 5.0, 113),

        # Negative estrus cycle
        (100, 120, "Negative Cycle", -10, 100, 2.0, 20, 5.0, 110),

        # Different stdi values
        (100, 120, "Different STDI", 10, 100, 1.0, 10, 5.0, 110),
        (100, 120, "Different STDI", 10, 100, 3.0, 10, 5.0, 110),

        # Different average and standard deviation of estrus cycle
        (100, 120, "Different Avg and Std", 8, 100, 2.0, 8, 4.0, 108),
    ]
)
def test_simulate_synch_ed_estrus(mocker: MockerFixture, start_day: int, sim_day: int, estrus_note: str,
                                  estrus_cycle: int, days_born: int, stdi: float,
                                  avg_estrus_cycle_after_pgf: int, std_estrus_cycle_after_pgf: int,
                                  expected_estrus_day: int) -> None:
    """
    Unit test for _simulate_synch_ed_estrus() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    patch_for_truncnorm = mocker.patch('scipy.stats.truncnorm.rvs', return_value=estrus_cycle)
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    mock_init_args = mocker.MagicMock()
    heifer = HeiferII(mock_init_args)
    heifer.days_born = days_born
    patch_for_log_event = mocker.patch.object(heifer, 'log_event')
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.STDI', stdi)
    mocker.patch.object(HeiferII, 'get_avg_estrus_cycle_after_pgf', return_value=avg_estrus_cycle_after_pgf)
    mocker.patch.object(HeiferII, 'get_std_estrus_cycle_after_pgf', return_value=std_estrus_cycle_after_pgf)

    # Act
    heifer._simulate_synch_ed_estrus(start_day, sim_day, estrus_note)

    # Assert
    assert heifer.estrus_day == expected_estrus_day
    patch_for_truncnorm.assert_called_with(-stdi, stdi, avg_estrus_cycle_after_pgf, std_estrus_cycle_after_pgf)
    patch_for_log_event.assert_called_with(days_born, sim_day, f'{estrus_note} on day {expected_estrus_day}')


@pytest.mark.parametrize(
    "mocked_random_value, reference_rate, expected_result",
    [
        # Random value less than reference rate
        (0.1, 0.2, True),

        # Random value greater than reference rate
        (0.3, 0.2, False),

        # Random value equal to reference rate
        (0.2, 0.2, False),

        # Very small reference rate
        (0.01, 0.001, False),
        (0.0001, 0.001, True),

        # Reference rate close to 1
        (0.99, 0.999, True),
        (0.999, 0.999, False),

        # Randomized rate of 0
        (0.0, 0.5, True),

        # Randomized rate of 1
        (1.0, 0.999, False),

        # Random and reference rates the same (not at boundaries)
        (0.5, 0.5, False),
    ]
)
def test_compare_randomized_rate_less_than(mocker: MockerFixture, mocked_random_value: float,
                                           reference_rate: float, expected_result: bool) -> None:
    """
    Unit test for _compare_randomized_rate_less_than() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.random', return_value=mocked_random_value)

    # Act
    result = HeiferII._compare_randomized_rate_less_than(reference_rate)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "event_day, sim_day, event_note",
    [
        # Normal case
        (100, 120, "Test Event 1"),

        # Event day 0
        (0, 1, "Event Day 0"),

        # Simulation day 0
        (1, 0, "Simulation Day 0"),

        # End of first year
        (365, 365, "End of Year Event"),

        # Negative event day
        (-1, 0, "Negative Event Day"),

        # Negative simulation day
        (0, -1, "Negative Simulation Day"),
    ]
)
def test_log_event(mocker: MockerFixture, event_day: int, sim_day: int, event_note: str) -> None:
    """
    Unit test for log_event() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.events = mocker.MagicMock()

    # Act
    heifer.log_event(event_day, sim_day, event_note)

    # Assert
    heifer.events.add_event.assert_called_with(event_day, sim_day, event_note)


@pytest.mark.parametrize(
    "avg_estrus_cycle_config, expected_avg_estrus_cycle",
    [
        # Normal case
        (21, 21),

        # Zero average cycle length
        (0, 0),
    ]
)
def test_get_avg_estrus_cycle(mocker: MockerFixture, avg_estrus_cycle_config: int,
                              expected_avg_estrus_cycle: int) -> None:
    """
    Unit test for get_avg_estrus_cycle() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'avg_estrus_cycle_heifer': avg_estrus_cycle_config}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII.get_avg_estrus_cycle()

    # Assert
    assert result == expected_avg_estrus_cycle


@pytest.mark.parametrize(
    "std_estrus_cycle_config, expected_std_estrus_cycle",
    [
        # Normal case
        (3.5, 3.5),

        # Zero standard deviation
        (0.0, 0.0),

        # Negative standard deviation
        (-5.0, -5.0),
    ]
)
def test_get_std_estrus_cycle(mocker: MockerFixture, std_estrus_cycle_config: float,
                              expected_std_estrus_cycle: float) -> None:
    """
    Unit test for get_std_estrus_cycle() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'std_estrus_cycle_heifer': std_estrus_cycle_config}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII.get_std_estrus_cycle()

    # Assert
    assert result == expected_std_estrus_cycle


@pytest.mark.parametrize(
    "avg_estrus_cycle_after_pgf_config, expected_avg_estrus_cycle_after_pgf",
    [
        # Normal case
        (18, 18),

        # Zero average cycle length
        (0, 0),

        # Negative average cycle length
        (-5, -5),
    ]
)
def test_get_avg_estrus_cycle_after_pgf(mocker: MockerFixture, avg_estrus_cycle_after_pgf_config: int,
                                        expected_avg_estrus_cycle_after_pgf: int) -> None:
    """
    Unit test for get_avg_estrus_cycle_after_pgf() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'avg_estrus_cycle_after_pgf': avg_estrus_cycle_after_pgf_config}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII.get_avg_estrus_cycle_after_pgf()

    # Assert
    assert result == expected_avg_estrus_cycle_after_pgf


@pytest.mark.parametrize(
    "std_estrus_cycle_after_pgf_config, expected_std_estrus_cycle_after_pgf",
    [
        # Normal case
        (2.5, 2.5),

        # Zero standard deviation
        (0.0, 0.0),

        # Negative standard deviation
        (-3.0, -3.0),
    ]
)
def test_get_std_estrus_cycle_after_pgf(mocker: MockerFixture, std_estrus_cycle_after_pgf_config: float,
                                        expected_std_estrus_cycle_after_pgf: float) -> None:
    """
    Unit test for get_std_estrus_cycle_after_pgf() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'std_estrus_cycle_after_pgf': std_estrus_cycle_after_pgf_config}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII.get_std_estrus_cycle_after_pgf()

    # Assert
    assert result == expected_std_estrus_cycle_after_pgf


@pytest.mark.parametrize(
    "mocked_estrus_detection_rate, expected_estrus_detection_rate",
    [
        # Normal case
        (0.5, 0.5),

        # Higher estrus detection rate
        (0.75, 0.75),

        # Zero estrus detection rate
        (0.0, 0.0),

        # 100% estrus detection rate
        (1.0, 1.0),
    ]
)
def test_get_general_estrus_detection_rate(mocker: MockerFixture, mocked_estrus_detection_rate: float,
                                           expected_estrus_detection_rate: float) -> None:
    """
    Unit test for get_general_estrus_detection_rate() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heiferII = HeiferII(mocker.MagicMock())
    patch_for_get_repro_data = mocker.patch.object(HeiferII, 'get_user_defined_repro_data',
                                                   return_value=mocked_estrus_detection_rate)

    # Act
    result = heiferII.get_general_estrus_detection_rate()

    # Assert
    assert result == expected_estrus_detection_rate
    patch_for_get_repro_data.assert_called_with('estrus_detection_rate')


@pytest.mark.parametrize(
    "mocked_estrus_detection_rate, expected_estrus_detection_rate",
    [
        # Normal case
        (0.4, 0.4),

        # Higher estrus detection rate
        (0.8, 0.8),

        # Zero estrus detection rate
        (0.0, 0.0),

        # 100% estrus detection rate
        (1.0, 1.0),
    ]
)
def test_get_user_defined_synch_ed_estrus_detection_rate(mocker: MockerFixture, mocked_estrus_detection_rate: float,
                                                         expected_estrus_detection_rate: float) -> None:
    """
    Unit test for _get_user_defined_synch_ed_estrus_detection_rate() static method of HeiferII class in
    heiferII.py file.
    """

    # Arrange
    mock_repro_sub_properties = {'estrus_detection_rate': mocked_estrus_detection_rate}
    patch_for_get_repro_sub_properties = \
        mocker.patch.object(HeiferII, 'get_user_defined_repro_sub_properties',
                            return_value=mock_repro_sub_properties)

    # Act
    result = HeiferII._get_user_defined_synch_ed_estrus_detection_rate()

    # Assert
    assert result == expected_estrus_detection_rate
    patch_for_get_repro_sub_properties.assert_called_once()


@pytest.mark.parametrize(
    "mocked_estrus_detection_rate, expected_estrus_detection_rate",
    [
        # Normal case
        (0.4, 0.4),

        # Higher estrus detection rate
        (0.8, 0.8),

        # Zero estrus detection rate
        (0.0, 0.0),

        # 100% estrus detection rate
        (1.0, 1.0),
    ]
)
def test_get_default_synch_ed_estrus_detection_rate(mocker: MockerFixture,
                                                    mocked_estrus_detection_rate: float,
                                                    expected_estrus_detection_rate: float) -> None:
    """
    Unit test for _get_default_synch_ed_estrus_detection_rate() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_heifer_repro_protocols = {
        HeiferReproProtocolEnum.SynchED.value: {
            'default_sub_properties': {
                'estrus_detection_rate': mocked_estrus_detection_rate
            }
        }
    }
    mocker.patch.object(InternalReproSettings, 'HEIFER_REPRO_PROTOCOLS', mocked_heifer_repro_protocols)

    # Act
    result = HeiferII._get_default_synch_ed_estrus_detection_rate()

    # Assert
    assert result == expected_estrus_detection_rate


@pytest.mark.parametrize(
    "repro_protocol, user_defined_rate, default_rate, expected_rate",
    [
        # Test case where the user-defined protocol is SynchED and a specific rate is returned
        (HeiferReproProtocolEnum.SynchED.value, 0.6, 0.5, 0.6),

        # Test case where the user-defined protocol is not SynchED and the default rate is returned
        ('OtherProtocol', 0.6, 0.4, 0.4),
    ]
)
def test_get_user_defined_or_default_synch_ed_estrus_detection_rate(
        mocker: MockerFixture, repro_protocol: str,
        user_defined_rate: float, default_rate: float, expected_rate: float) -> None:
    """
    Unit test for _get_user_defined_or_default_synch_ed_estrus_detection_rate() static method of HeiferII class in
    heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    mocker.patch.object(heifer, 'get_user_defined_repro_protocol', return_value=repro_protocol)
    mocker.patch.object(HeiferII, '_get_user_defined_synch_ed_estrus_detection_rate', return_value=user_defined_rate)
    mocker.patch.object(HeiferII, '_get_default_synch_ed_estrus_detection_rate', return_value=default_rate)

    # Act
    result = heifer._get_user_defined_or_default_synch_ed_estrus_detection_rate()

    # Assert
    assert result == expected_rate


@pytest.mark.parametrize(
    "mocked_conception_rate, expected_conception_rate",
    [
        # Normal case
        (0.4, 0.4),

        # Higher estrus conception rate
        (0.7, 0.7),

        # Zero estrus conception rate
        (0.0, 0.0),

        # 100% estrus conception rate
        (1.0, 1.0),
    ]
)
def test_get_general_conception_rate(mocker: MockerFixture, mocked_conception_rate: float,
                                     expected_conception_rate: float) -> None:
    """
    Unit test for get_general_conception_rate() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heiferII = HeiferII(mocker.MagicMock())
    patch_for_get_repro_data = mocker.patch.object(HeiferII, 'get_user_defined_repro_data',
                                                   return_value=mocked_conception_rate)

    # Act
    result = heiferII.get_general_conception_rate()

    # Assert
    assert result == expected_conception_rate
    patch_for_get_repro_data.assert_called_with('estrus_conception_rate')


@pytest.mark.parametrize(
    "mocked_conception_rate, expected_conception_rate",
    [
        # Normal case
        (0.45, 0.45),

        # Higher estrus conception rate
        (0.75, 0.75),

        # Zero estrus conception rate
        (0.0, 0.0),

        # 100% estrus conception rate
        (1.0, 1.0),
    ]
)
def test_get_user_defined_TAI_conception_rate(mocker: MockerFixture, mocked_conception_rate: float,
                                              expected_conception_rate: float) -> None:
    """
    Unit test for _get_user_defined_TAI_conception_rate() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mock_repro_sub_properties = {'conception_rate': mocked_conception_rate}
    patch_for_get_repro_sub_properties = mocker.patch.object(HeiferII, 'get_user_defined_repro_sub_properties',
                                                             return_value=mock_repro_sub_properties)

    # Act
    result = HeiferII._get_user_defined_TAI_conception_rate()

    # Assert
    assert result == expected_conception_rate
    patch_for_get_repro_sub_properties.assert_called_once()


@pytest.mark.parametrize(
    "mocked_conception_rate, expected_conception_rate",
    [
        # Normal case
        (0.3, 0.3),

        # Higher TAI conception rate
        (0.5, 0.5),

        # Zero TAI conception rate
        (0.0, 0.0),

        # 100% TAI conception rate
        (1.0, 1.0),
    ]
)
def test_get_default_TAI_conception_rate(mocker: MockerFixture, mocked_conception_rate: float,
                                         expected_conception_rate: float) -> None:
    """
    Unit test for _get_default_TAI_conception_rate() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_heifer_repro_protocols = {
        HeiferReproProtocolEnum.TAI.value: {
            'default_sub_properties': {
                'conception_rate': mocked_conception_rate
            }
        }
    }
    mocker.patch.object(InternalReproSettings, 'HEIFER_REPRO_PROTOCOLS', mocked_heifer_repro_protocols)

    # Act
    result = HeiferII._get_default_TAI_conception_rate()

    # Assert
    assert result == expected_conception_rate


@pytest.mark.parametrize(
    "repro_protocol, user_defined_rate, default_rate, expected_rate",
    [
        # Test case where the user-defined protocol is TAI and a specific rate is returned
        (HeiferReproProtocolEnum.TAI.value, 0.55, 0.45, 0.55),

        # Case where the user-defined protocol is not TAI and the default rate is returned
        ('OtherProtocol', 0.55, 0.45, 0.45),
    ]
)
def test_get_user_defined_or_default_TAI_conception_rate(mocker: MockerFixture,
                                                         repro_protocol: str, user_defined_rate: float,
                                                         default_rate: float, expected_rate: float) -> None:
    """
    Unit test for _get_user_defined_or_default_TAI_conception_rate() static method of HeiferII class in heiferII.py
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    mocker.patch.object(heifer, 'get_user_defined_repro_protocol', return_value=repro_protocol)
    mocker.patch.object(HeiferII, '_get_user_defined_TAI_conception_rate', return_value=user_defined_rate)
    mocker.patch.object(HeiferII, '_get_default_TAI_conception_rate', return_value=default_rate)

    # Act
    result = heifer._get_user_defined_or_default_TAI_conception_rate()

    # Assert
    assert result == expected_rate


@pytest.mark.parametrize(
    "initial_estrus_count, mocked_detection_outcome, detection_rate, "
    "expected_result, expected_estrus_count",
    [
        # Estrus detected, count increments
        (0, True, 0.5, True, 1),

        # Estrus not detected, count increments
        (0, False, 0.5, False, 1),

        # Estrus detected, count increments
        (5, True, 0.8, True, 6),

        # Estrus not detected, count increments
        (10, False, 0.2, False, 11),
    ]
)
def test_detect_estrus(mocker: MockerFixture, initial_estrus_count: int, mocked_detection_outcome: bool,
                       detection_rate: float, expected_result: bool, expected_estrus_count: int) -> None:
    """
    Unit test for _detect_estrus() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.estrus_count = initial_estrus_count
    patch_for_compare_randomized_rate = mocker.patch.object(HeiferII, '_compare_randomized_rate_less_than',
                                                            return_value=mocked_detection_outcome)

    # Act
    result = heifer._detect_estrus(detection_rate)

    # Assert
    assert result == expected_result
    assert heifer.estrus_count == expected_estrus_count
    patch_for_compare_randomized_rate.assert_called_once_with(detection_rate)


@pytest.mark.parametrize(
    "is_pregnant, initial_ed_days, days_born, "
    "breeding_start_day, estrus_day, sim_day, "
    "should_simulate_estrus, should_handle_estrus_detection",
    [
        # Not pregnant, on breeding start day, not on estrus day
        (False, 0, 100, 100, 105, 100, True, False),

        # Not pregnant, not on breeding start day, on estrus day
        (False, 5, 105, 100, 105, 100, False, True),

        # Not pregnant, not on breeding start day, not on estrus day
        (False, 5, 95, 100, 105, 100, False, False),

        # Pregnant, on breeding start, not estrus day
        (True, 0, 100, 100, 105, 100, True, False),

        # Pregnant, not on breeding start day, on estrus day
        (True, 5, 105, 100, 105, 100, False, True),
    ]
)
def test_execute_ed_protocol(mocker: MockerFixture, is_pregnant: bool, initial_ed_days: int, days_born: int,
                             breeding_start_day: int, estrus_day: int, sim_day: int,
                             should_simulate_estrus: bool,
                             should_handle_estrus_detection: bool) -> None:
    """
    Unit test for execute_ed_protocol() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    mocker.patch.object(HeiferII, 'is_pregnant', new_callable=mocker.PropertyMock, return_value=is_pregnant)
    heifer.ED_days = initial_ed_days
    heifer.days_born = days_born
    heifer.estrus_day = estrus_day
    mocker.patch.object(HeiferII, '_get_breeding_start_day', return_value=breeding_start_day)
    patch_for_simulate_estrus = mocker.patch.object(heifer, '_simulate_estrus', return_value=None)
    patch_for_handle_ed_estrus_detection = mocker.patch.object(heifer, '_handle_ed_estrus_detection',
                                                               return_value=None)

    # Act
    heifer.execute_ed_protocol(sim_day)

    # Assert
    if not is_pregnant:
        assert heifer.ED_days == initial_ed_days + 1
    else:
        assert heifer.ED_days == initial_ed_days

    if should_simulate_estrus:
        patch_for_simulate_estrus.assert_called_once_with(breeding_start_day, sim_day,
                                                          const.ESTRUS_DAY_SCHEDULED_NOTE)
    else:
        patch_for_simulate_estrus.assert_not_called()

    if should_handle_estrus_detection:
        patch_for_handle_ed_estrus_detection.assert_called_once_with(sim_day)
    else:
        patch_for_handle_ed_estrus_detection.assert_not_called()


@pytest.mark.parametrize(
    "days_born, sim_day, is_estrus_detected, "
    "general_estrus_detection_rate, general_conception_rate, "
    "expected_conception_rate, expected_ai_day",
    [
        # Estrus detected
        (100, 100, True, 0.5, 0.5, 0.5, 101),

        # Estrus not detected scenario
        (100, 100, False, 0.5, 0.5, None, None),
    ]
)
def test_handle_ed_estrus_detection(mocker: MockerFixture, days_born: int, sim_day: int, is_estrus_detected: bool,
                                    general_estrus_detection_rate: float, general_conception_rate: float,
                                    expected_conception_rate: float, expected_ai_day: int) -> None:
    """
    Unit test for _handle_ed_estrus_detection() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_detect_estrus = mocker.patch.object(heifer, '_detect_estrus', return_value=is_estrus_detected)
    mocker.patch.object(HeiferII, 'get_general_estrus_detection_rate', return_value=general_estrus_detection_rate)
    mocker.patch.object(HeiferII, 'get_general_conception_rate', return_value=general_conception_rate)
    patch_for_simulate_estrus = mocker.patch.object(HeiferII, '_simulate_estrus', return_value=None)

    # Act
    heifer._handle_ed_estrus_detection(sim_day)

    # Assert
    patch_for_log_event.assert_any_call(days_born, sim_day, const.ESTRUS_OCCURRED_NOTE)
    patch_for_detect_estrus.assert_called_with(general_estrus_detection_rate)
    if is_estrus_detected:
        patch_for_log_event.assert_any_call(heifer.days_born, sim_day, const.ESTRUS_DETECTED_NOTE)
        assert heifer.conception_rate == expected_conception_rate
        assert heifer.ai_day == expected_ai_day
        patch_for_log_event.assert_any_call(heifer.days_born, sim_day,
                                            f'{const.AI_DAY_SCHEDULED_NOTE} on day {expected_ai_day}')
    else:
        patch_for_simulate_estrus.assert_any_call(heifer.days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)


@pytest.mark.parametrize(
    "hormones, delivery_day, sim_day, "
    "initial_GnRH_count, initial_PGF_count, "
    "expected_GnRH_count, expected_PGF_count, raises_error",
    [
        # Delivering GnRH
        (['GnRH'], 100, 100, 0, 0, 1, 0, False),

        # Delivering PGF
        (['PGF'], 100, 100, 0, 0, 0, 1, False),

        # Delivering both GnRH and PGF
        (['GnRH', 'PGF'], 100, 100, 0, 0, 1, 1, False),
        (['PGF', 'GnRH'], 100, 100, 0, 0, 1, 1, False),

        # No hormones delivered
        ([], 100, 100, 0, 0, 0, 0, False),

        # Invalid hormone
        (['InvalidHormone'], 100, 100, 0, 0, 0, 0, True),
    ]
)
def test_deliver_hormones(mocker: MockerFixture, hormones: list[str], delivery_day: int, sim_day: int,
                          initial_GnRH_count: int,
                          initial_PGF_count: int, expected_GnRH_count: int, expected_PGF_count: int,
                          raises_error: bool) -> None:
    """
    Unit test for _deliver_hormones() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.GnRH_injections = initial_GnRH_count
    heifer.PGF_injections = initial_PGF_count
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)

    # Act and Assert
    if raises_error:
        with pytest.raises(ValueError):
            heifer._deliver_hormones(hormones, delivery_day, sim_day)
    else:
        heifer._deliver_hormones(hormones, delivery_day, sim_day)
        assert heifer.GnRH_injections == expected_GnRH_count
        assert heifer.PGF_injections == expected_PGF_count
        assert patch_for_log_event.call_count == (len(hormones) if hormones else 0)


@pytest.mark.parametrize(
    "days_born, sim_day, schedule, TAI_conception_rate, "
    "expected_ai_day, expected_conception_rate",
    [
        # Test delivering hormones and setting AI day and conception rate
        (100, 110,
         {100: {'deliver_hormones': ['GnRH'], 'set_ai_day': True, 'set_conception_rate': True}},
         0.5, 100, 0.5),

        # Test only delivering hormones
        (100, 110, {100: {'deliver_hormones': ['PGF']}}, 0.5, None, None),

        # Test setting AI day only
        (100, 110, {100: {'set_ai_day': True}}, 0.5, 100, None),

        # Test setting conception rate only
        (100, 110, {100: {'set_conception_rate': True}}, 0.7, None, 0.7),

        # Test no actions for the day
        (100, 100, {101: {'deliver_hormones': ['GnRH']}}, 0.5, None, None),

        # Test with empty schedule
        (100, 100, {}, 0.5, None, None),
    ]
)
def test_execute_hormone_delivery_schedule(mocker: MockerFixture, days_born: int, sim_day: int,
                                           schedule: dict[int, dict], TAI_conception_rate: float,
                                           expected_ai_day: int, expected_conception_rate: float) -> None:
    """
    Unit test for _execute_hormone_delivery_schedule() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer._TAI_conception_rate = TAI_conception_rate
    patch_for_deliver_hormones = mocker.patch.object(heifer, '_deliver_hormones', return_value=None)
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)

    # Act
    heifer._execute_hormone_delivery_schedule(sim_day, schedule)

    # Assert
    if 'deliver_hormones' in schedule.get(days_born, {}):
        patch_for_deliver_hormones.assert_called_with(schedule[days_born]['deliver_hormones'], days_born, sim_day)
    if 'set_ai_day' in schedule.get(days_born, {}):
        assert heifer.ai_day == expected_ai_day
        patch_for_log_event.assert_called_with(days_born, sim_day,
                                               f'{const.AI_DAY_SCHEDULED_NOTE} on day {expected_ai_day}')
    if 'set_conception_rate' in schedule.get(days_born, {}):
        assert heifer.conception_rate == expected_conception_rate
    assert days_born not in schedule


@pytest.mark.parametrize(
    "breeding_start_day_config, expected_breeding_start_day",
    [
        # Normal case
        (380, 380),

        # Zero breeding start day
        (0, 0),
    ]
)
def test_get_breeding_start_day(mocker: MockerFixture, breeding_start_day_config: int,
                                expected_breeding_start_day: int) -> None:
    """
    Unit test for _get_breeding_start_day() static method of HeiferII class.
    """

    # Arrange
    mocked_config = {'breeding_start_day_h': breeding_start_day_config}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII._get_breeding_start_day()

    # Assert
    assert result == expected_breeding_start_day


@pytest.mark.parametrize(
    "attribute, heifer_data, expected_value",
    [
        # Normal cases
        ('estrus_cycle_length', {'estrus_cycle_length': 21}, 21),
        ('conception_rate', {'conception_rate': 0.5}, 0.5),

        # Invalid attribute
        ('invalid_attribute', {'estrus_cycle_length': 21}, KeyError),
    ]
)
def test_get_user_defined_repro_data(mocker: MockerFixture, attribute: str,
                                     heifer_data: dict, expected_value: Any) -> None:
    """
    Unit test for get_user_defined_repro_data() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'heifers': heifer_data}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act and Assert
    if expected_value == KeyError:
        with pytest.raises(KeyError):
            HeiferII.get_user_defined_repro_data(attribute)
    else:
        result = HeiferII.get_user_defined_repro_data(attribute)
        assert result == expected_value


@pytest.mark.parametrize(
    "mocked_repro_protocol, expected_repro_protocol",
    [
        # Normal cases
        ("ED", "ED"),
        ("TAI", "TAI"),
        ("SynchED", "SynchED"),
        ("OtherProtocol", "OtherProtocol"),
    ]
)
def test_get_user_defined_repro_protocol(mocker: MockerFixture, mocked_repro_protocol: str,
                                         expected_repro_protocol: str) -> None:
    """
    Unit test for get_user_defined_repro_protocol() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocked_config = {'heifer_repro_method': mocked_repro_protocol}
    mocker.patch.object(AnimalBase, 'config', mocked_config)

    # Act
    result = HeiferII.get_user_defined_repro_protocol()

    # Assert
    assert result == expected_repro_protocol


@pytest.mark.parametrize(
    "sub_protocol_value",
    [
        # Normal cases
        HeiferReproProtocolEnum.TAI_5dCG2P,
        HeiferReproProtocolEnum.TAI_5dCGP,
        HeiferReproProtocolEnum.SynchED_2P,
        HeiferReproProtocolEnum.SynchED_CP
    ]
)
def test_get_user_defined_repro_sub_protocol(mocker: MockerFixture, sub_protocol_value: str) -> None:
    """
    Unit test for get_user_defined_repro_sub_protocol() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, 'get_user_defined_repro_data', return_value=sub_protocol_value)

    # Act
    result = HeiferII.get_user_defined_repro_sub_protocol()

    # Assert
    assert result == sub_protocol_value


@pytest.mark.parametrize(
    "protocol, mocked_default_sub_protocol, expected_sub_protocol",
    [
        # Normal cases
        ("TAI", "TAI_SubProtocol1", "TAI_SubProtocol1"),
        ("SynchED", "SynchED_SubProtocol1", "SynchED_SubProtocol1"),
        ("OtherProtocol", "OtherSubProtocol1", "OtherSubProtocol1"),
    ]
)
def test_get_default_repro_sub_protocol(mocker, protocol, mocked_default_sub_protocol, expected_sub_protocol):
    """
    Unit test for _get_default_repro_sub_protocol() static method.
    """

    # Arrange
    mocked_repro_protocols = {
        protocol: {
            'default_sub_protocol': mocked_default_sub_protocol
        }
    }
    mocker.patch.object(InternalReproSettings, 'HEIFER_REPRO_PROTOCOLS', mocked_repro_protocols)

    # Act
    result = HeiferII._get_default_repro_sub_protocol(protocol)

    # Assert
    assert result == expected_sub_protocol


@pytest.mark.parametrize(
    "current_program, user_defined_program, user_defined_sub_protocol, default_sub_protocol, expected_sub_protocol",
    [
        # Test case where current and user-defined programs match
        ("TAI", "TAI", "TAI_UserDefinedSub", "TAI_DefaultSub", "TAI_UserDefinedSub"),

        # Test case where current and user-defined programs do not match
        ("TAI", "SynchED", "SynchED_UserDefinedSub", "TAI_DefaultSub", "TAI_DefaultSub"),
    ]
)
def test_get_user_defined_or_default_repro_sub_protocol(
        mocker: MockerFixture, current_program: str, user_defined_program: str,
        user_defined_sub_protocol: str, default_sub_protocol: str, expected_sub_protocol: str) -> None:
    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.repro_program = current_program
    mocker.patch.object(HeiferII, 'get_user_defined_repro_protocol', return_value=user_defined_program)
    mocker.patch.object(HeiferII, 'get_user_defined_repro_sub_protocol', return_value=user_defined_sub_protocol)
    mocker.patch.object(HeiferII, '_get_default_repro_sub_protocol', return_value=default_sub_protocol)

    # Act
    result = heifer._get_user_defined_or_default_repro_sub_protocol()

    # Assert
    assert result == expected_sub_protocol


@pytest.mark.parametrize(
    "sub_properties",
    [
        # Normal case
        {"conception_rate": 0.5, "estrus_detection_rate": 0.5},

        # Empty dictionary
        {},
    ]
)
def test_get_user_defined_repro_sub_properties(mocker: MockerFixture, sub_properties: dict):
    """
    Unit test for get_user_defined_repro_sub_properties() static method of HeiferII class.
    """

    # Arrange
    mocker.patch.object(HeiferII, 'get_user_defined_repro_data', return_value=sub_properties)

    # Act
    result = HeiferII.get_user_defined_repro_sub_properties()

    # Assert
    assert result == sub_properties


@pytest.mark.parametrize(
    "days_born, sim_day, breeding_start_day, hormone_schedule, hormone_schedule_exists, "
    "repro_sub_protocol, specific_conception_rate",
    [
        # Scenarios with different conditions on breeding start day
        (100, 100, 100, None, False, "Protocol", 0.6),
        (100, 100, 100, {}, False, "Protocol", 0.7),
        (100, 100, 100, {'day': 'actions'}, True, "Protocol", 0.5),

        # Scenarios on days not being the breeding start day
        (101, 100, 100, None, False, "Protocol", 0.4),
        (101, 100, 100, {}, False, "Protocol", 0.3),
        (101, 100, 100, {'day': 'actions'}, True, "Protocol", 0.5),
    ]
)
def test_execute_tai_protocol(mocker: MockerFixture, days_born: int, sim_day: int, breeding_start_day: int,
                              hormone_schedule: dict, hormone_schedule_exists: bool, repro_sub_protocol: str,
                              specific_conception_rate: float):
    """
    Unit test for execute_tai_protocol() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer._hormone_schedule = hormone_schedule
    patch_for_set_up_hormone_schedule = mocker.patch.object(heifer, '_set_up_hormone_schedule', return_value=None)
    patch_for_execute_hormone_schedule = mocker.patch.object(heifer, '_execute_hormone_delivery_schedule',
                                                             return_value=None)
    patch_for_get_repro_sub_protocol = mocker.patch.object(HeiferII, '_get_user_defined_or_default_repro_sub_protocol',
                                                           return_value=repro_sub_protocol)
    patch_for_get_TAI_conception_rate = mocker.patch.object(
        HeiferII,
        '_get_user_defined_or_default_TAI_conception_rate',
        return_value=specific_conception_rate)
    mocker.patch.object(HeiferII, '_get_breeding_start_day', return_value=breeding_start_day)

    # Act
    heifer.execute_tai_protocol(sim_day)

    # Assert
    if days_born == breeding_start_day:
        patch_for_set_up_hormone_schedule.assert_called_once_with('heifers', repro_sub_protocol, days_born)
        patch_for_get_repro_sub_protocol.assert_called_once()
        patch_for_get_TAI_conception_rate.assert_called_once()
        assert heifer._TAI_conception_rate == specific_conception_rate
    if hormone_schedule_exists:
        patch_for_execute_hormone_schedule.assert_called_once_with(sim_day, hormone_schedule)
    else:
        patch_for_execute_hormone_schedule.assert_not_called()


@pytest.mark.parametrize(
    "days_born, sim_day, breeding_start_day, estrus_day",
    [
        # Day is breeding start day
        (100, 100, 100, 105),

        # Normal day, not breeding start day, not estrus day,
        (101, 100, 100, 105),

        # Day is estrus day
        (105, 100, 100, 105),
    ]
)
def test_execute_synch_ed_protocol(mocker: MockerFixture, days_born: int, sim_day: int, breeding_start_day: int,
                                   estrus_day: int) -> None:
    """
    Unit test for execute_synch_ed_protocol() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.estrus_day = estrus_day
    patch_for_set_up_hormone_schedule = mocker.patch.object(heifer, '_set_up_hormone_schedule', return_value=None)
    patch_for_handle_hormone_delivery = mocker.patch.object(heifer,
                                                            '_handle_synch_ed_hormone_delivery_and_set_estrus_day',
                                                            return_value=None)
    patch_for_handle_estrus_detection = mocker.patch.object(heifer, '_handle_synch_ed_estrus_detection',
                                                            return_value=None)
    mocker.patch.object(HeiferII, '_get_breeding_start_day', return_value=breeding_start_day)
    mocker.patch.object(HeiferII, '_get_user_defined_or_default_repro_sub_protocol')

    # Act
    heifer.execute_synch_ed_protocol(sim_day)

    # Assert
    if days_born == breeding_start_day:
        patch_for_set_up_hormone_schedule.assert_called_once()
    patch_for_handle_hormone_delivery.assert_called_once_with(sim_day)
    if days_born == estrus_day:
        patch_for_handle_estrus_detection.assert_called_once_with(sim_day)


@pytest.mark.parametrize(
    "animal_category, repro_sub_protocol, start_from, adjusted_schedule, should_raise_exception",
    [
        # Normal cases for heifers
        ('heifers', HeiferReproProtocolEnum.TAI_5dCG2P.value, 100, {'day': 'actions'}, False),
        ('heifers', HeiferReproProtocolEnum.TAI_5dCGP.value, 100, {'day': 'actions'}, False),
        ('heifers', HeiferReproProtocolEnum.SynchED_2P.value, 100, {'day': 'actions'}, False),
        ('heifers', HeiferReproProtocolEnum.SynchED_CP.value, 100, {'day': 'actions'}, False),

        # Normal cases for cows
        ('cows', "OvSynch 48", 100, {'day': 'actions'}, False),
        ('cows', "OvSynch 56", 100, {'day': 'actions'}, False),
        ('cows', "OvSynch 72", 100, {'day': 'actions'}, False),
        ('cows', "5d CoSynch", 100, {'day': 'actions'}, False),

        # Invalid protocol
        ('heifers', "InvalidProtocol", 100, None, True),
        ('cows', "InvalidProtocol", 100, None, True),
    ]
)
def test_set_up_hormone_schedule(mocker: MockerFixture, animal_category: str, repro_sub_protocol: str, start_from: int,
                                 adjusted_schedule: dict, should_raise_exception: bool):
    """
    Unit test for _set_up_hormone_schedule() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())

    patch_for_get_adjusted_schedule = mocker.patch.object(
        HormoneDeliverySchedule, 'get_adjusted_schedule',
        return_value=adjusted_schedule)

    # Act and Assert
    if should_raise_exception:
        with pytest.raises(Exception):
            heifer._set_up_hormone_schedule(animal_category, repro_sub_protocol, start_from)  # type: ignore
    else:
        heifer._set_up_hormone_schedule(animal_category, repro_sub_protocol, start_from)  # type: ignore
        assert heifer._hormone_schedule == adjusted_schedule
        patch_for_get_adjusted_schedule.assert_called_once_with(animal_category, repro_sub_protocol, start_from)


@pytest.mark.parametrize(
    "days_born, sim_day, initial_hormone_schedule, final_hormone_schedule",
    [
        # One entry in hormone schedule, which gets removed
        (100, 100, {'day1': 'actions'}, {}),

        # Empty hormone schedule remains unchanged
        (100, 100, {}, {}),

        # Multiple entries in hormone schedule, one entry gets removed
        (100, 100, {'day1': 'actions', 'day2': 'actions'}, {'day2': 'actions'}),
    ]
)
def test_handle_synch_ed_hormone_delivery_and_set_estrus_day(mocker: MockerFixture, days_born: int,
                                                             sim_day: int, initial_hormone_schedule: dict,
                                                             final_hormone_schedule: dict) -> None:
    """
    Unit test for _handle_synch_ed_hormone_delivery_and_set_estrus_day() method of HeiferII class
    in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer._hormone_schedule = initial_hormone_schedule.copy()

    def execute_hormone_schedule_side_effect(*args, **kwargs):
        heifer._hormone_schedule = final_hormone_schedule.copy()

    patch_for_execute_hormone_schedule = mocker.patch.object(heifer, '_execute_hormone_delivery_schedule',
                                                             side_effect=execute_hormone_schedule_side_effect)
    patch_for_simulate_synch_ed_estrus = mocker.patch.object(heifer, '_simulate_synch_ed_estrus',
                                                             return_value=None)

    # Act
    heifer._handle_synch_ed_hormone_delivery_and_set_estrus_day(sim_day)

    # Assert
    if len(initial_hormone_schedule) > 0:
        patch_for_execute_hormone_schedule.assert_called_once_with(sim_day, initial_hormone_schedule)
    if len(initial_hormone_schedule) == 1 and len(final_hormone_schedule) == 0:
        patch_for_simulate_synch_ed_estrus.assert_called_once_with(days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)
    else:
        patch_for_simulate_synch_ed_estrus.assert_not_called()

    assert heifer._hormone_schedule == final_hormone_schedule


@pytest.mark.parametrize(
    "days_born, sim_day, estrus_detected, specific_estrus_detection_rate, external_specific_conception_rate",
    [
        # Estrus detected
        (100, 100, True, 0.5, 0.6),

        # Estrus not detected
        (100, 100, False, 0.5, 0.6),
    ]
)
def test_handle_synch_ed_estrus_detection(mocker: MockerFixture, days_born: int, sim_day: int,
                                          estrus_detected: bool, specific_estrus_detection_rate: float,
                                          external_specific_conception_rate: float) -> None:
    """
    Unit test for _handle_synch_ed_estrus_detection() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_detect_estrus = mocker.patch.object(heifer, '_detect_estrus', return_value=estrus_detected)
    mocker.patch.object(HeiferII, '_get_user_defined_or_default_synch_ed_estrus_detection_rate',
                        return_value=specific_estrus_detection_rate)
    mocker.patch.object(HeiferII, '_get_user_defined_TAI_conception_rate',
                        return_value=external_specific_conception_rate)
    patch_for_handle_estrus_not_detected = mocker.patch.object(heifer, '_handle_estrus_not_detected_in_synch_ed',
                                                               return_value=None)

    # Act
    heifer._handle_synch_ed_estrus_detection(sim_day)

    # Assert
    patch_for_log_event.assert_any_call(days_born, sim_day, const.ESTRUS_OCCURRED_NOTE)
    patch_for_detect_estrus.assert_called_once_with(specific_estrus_detection_rate)
    if estrus_detected:
        patch_for_log_event.assert_any_call(days_born, sim_day, const.ESTRUS_DETECTED_NOTE)
        assert heifer.conception_rate == external_specific_conception_rate
        assert heifer.ai_day == days_born + 1
        patch_for_log_event.assert_any_call(days_born, sim_day, f'{const.AI_DAY_SCHEDULED_NOTE} on day {days_born + 1}')
    else:
        patch_for_handle_estrus_not_detected.assert_called_once_with(sim_day)


@pytest.mark.parametrize(
    "days_born, sim_day, TAI_conception_rate, expected_ai_day, internal_fallback_protocol",
    [
        # Normal cases
        (120, 120, 0.6, 121,
         {'repro_protocol': HeiferReproProtocolEnum.TAI.value,
          'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCG2P.value,
          'repro_sub_properties': {
              'conception_rate': 0.5
          }}),

        (120, 120, 0.6, 121,
         {'repro_protocol': HeiferReproProtocolEnum.TAI.value,
          'repro_sub_protocol': HeiferReproProtocolEnum.TAI_5dCGP.value,
          'repro_sub_properties': {
              'conception_rate': 0.5
          }}),
    ]
)
def test_handle_estrus_not_detected_in_synch_ed(mocker: MockerFixture, days_born: int, sim_day: int,
                                                TAI_conception_rate: float, expected_ai_day: int,
                                                internal_fallback_protocol: dict) -> None:
    """
    Unit test for _handle_estrus_not_detected_in_synch_ed() method of HeiferII class.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer._hormone_schedule = mocker.MagicMock()
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_set_repro_program = mocker.patch.object(heifer, '_set_repro_program', return_value=None)
    patch_for_set_up_hormone_schedule = mocker.patch.object(heifer, '_set_up_hormone_schedule', return_value=None)
    patch_for_execute_hormone_schedule = mocker.patch.object(heifer, '_execute_hormone_delivery_schedule',
                                                             return_value=None)
    mocker.patch.object(HeiferII, '_get_user_defined_or_default_repro_sub_protocol',
                        return_value=internal_fallback_protocol['repro_sub_protocol'])
    mocker.patch.object(InternalReproSettings, 'HEIFER_REPRO_PROTOCOLS',
                        {internal_fallback_protocol['repro_sub_protocol']: {
                            'when_estrus_not_detected': internal_fallback_protocol}})

    # Act
    heifer._handle_estrus_not_detected_in_synch_ed(sim_day)

    # Assert
    patch_for_log_event.assert_has_calls([
        mocker.call(days_born, sim_day, const.ESTRUS_NOT_DETECTED_NOTE),
        mocker.call(days_born, sim_day, const.TAI_AFTER_ESTRUS_NOT_DETECTED_IN_SYNCH_ED_NOTE)
    ])
    patch_for_set_repro_program.assert_called_with(sim_day, internal_fallback_protocol['repro_protocol'])
    patch_for_set_up_hormone_schedule.assert_called_with('heifers', internal_fallback_protocol['repro_sub_protocol'],
                                                         days_born)
    assert heifer._TAI_conception_rate == internal_fallback_protocol['repro_sub_properties']['conception_rate']
    patch_for_execute_hormone_schedule.assert_called_with(sim_day, heifer._hormone_schedule)


@pytest.mark.parametrize(
    "days_born, sim_day, initial_repro_program, new_repro_program, is_valid, should_log_event",
    [
        # Normal cases - changing the program
        (100, 100, HeiferReproProtocolEnum.ED.value, HeiferReproProtocolEnum.TAI.value, True, True),
        (100, 100, HeiferReproProtocolEnum.TAI.value, HeiferReproProtocolEnum.SynchED.value, True, True),
        (100, 100, HeiferReproProtocolEnum.SynchED.value, HeiferReproProtocolEnum.ED.value, True, True),

        # Same program - no change
        (100, 100, HeiferReproProtocolEnum.ED.value, HeiferReproProtocolEnum.ED.value, True, False),
        (100, 100, HeiferReproProtocolEnum.TAI.value, HeiferReproProtocolEnum.TAI.value, True, False),
    ]
)
def test_set_repro_program(mocker: MockerFixture, days_born: int, sim_day: int,
                           initial_repro_program: str, new_repro_program: str,
                           is_valid: bool, should_log_event: bool):
    """
    Unit test for _set_repro_program() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.repro_program = initial_repro_program
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)

    # Act and Assert
    if is_valid:
        heifer._set_repro_program(sim_day, new_repro_program)  # type: ignore
        assert heifer.repro_program == new_repro_program
        if should_log_event:
            patch_for_log_event.assert_called_once_with(
                days_born, sim_day,
                f"{const.SETTING_REPRO_PROGRAM_NOTE} from {initial_repro_program} "
                f"to {new_repro_program}")
        else:
            patch_for_log_event.assert_not_called()
    else:
        with pytest.raises(ValueError):
            heifer._set_repro_program(sim_day, new_repro_program)


@pytest.mark.parametrize(
    "abortion_day, sim_day",
    [
        # Normal case
        (100, 120),

        # Abortion day is sim day
        (100, 100),

        # Abortion day is close to sim day
        (100, 101),

        # Abortion day is far from sim day
        (100, 200),
    ]
)
def test_open(mocker: MockerFixture, abortion_day: int, sim_day: int) -> None:
    """
    Unit test for open() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.abortion_day = abortion_day
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_set_repro_program = mocker.patch.object(heifer, '_set_repro_program', return_value=None)
    patch_for_simulate_estrus = mocker.patch.object(heifer, '_simulate_estrus', return_value=None)

    # Act
    heifer.open(sim_day)

    # Assert
    patch_for_log_event.assert_called_once_with(abortion_day, sim_day, const.REBREEDING_NOTE)
    patch_for_set_repro_program.assert_called_once_with(sim_day, 'ED')
    patch_for_simulate_estrus.assert_called_once_with(abortion_day, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)


@pytest.mark.parametrize(
    "days_in_preg, expected_result",
    [
        # Normal cases
        (0, False),
        (1, True),
        (10, True),

        # Invalid cases
        (-1, False),
    ]
)
def test_is_pregnant(mocker: MockerFixture, days_in_preg: int, expected_result: bool) -> None:
    """
    Unit test for is_pregnant property of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_in_preg = days_in_preg

    # Act
    result = heifer.is_pregnant

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "days_born, sim_day, semen_type, conception_rate, conception_successful, "
    "initial_semen_num, initial_AI_times, expected_semen_num, expected_AI_times",
    [
        # Test different semen types, conception rates, and conception outcomes
        (100, 120, "TypeA", 0.5, True, 0, 0, 1, 1),
        (150, 170, "TypeB", 0.4, False, 1, 2, 2, 3),
        (200, 220, "TypeC", 0.6, True, 3, 4, 4, 5),
        (250, 270, "TypeD", 0.3, False, 5, 6, 6, 7),
    ]
)
def test_perform_ai(mocker: MockerFixture, days_born: int, sim_day: int, semen_type: str,
                    conception_rate: float, conception_successful: bool, initial_semen_num: int, initial_AI_times: int,
                    expected_semen_num: int, expected_AI_times: int) -> None:
    """
    Unit test for _perform_ai() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.conception_rate = conception_rate
    heifer.semen_num = initial_semen_num
    heifer.AI_times = initial_AI_times

    mocker.patch.object(AnimalBase, 'config', {"semen_type": semen_type})
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_compare_rate = mocker.patch.object(heifer, '_compare_randomized_rate_less_than',
                                                 return_value=conception_successful)
    patch_for_successful_conception = mocker.patch.object(heifer, '_handle_successful_conception',
                                                          return_value=None)
    patch_for_failed_conception = mocker.patch.object(heifer, '_handle_failed_conception',
                                                      return_value=None)
    patch_for_increment_ai_counts = mocker.patch.object(heifer, '_increment_ai_counts', return_value=None)
    patch_for_increment_successful_conceptions = mocker.patch.object(heifer, '_increment_successful_conceptions',
                                                                     return_value=None)

    # Act
    heifer._perform_ai(sim_day)

    # Assert
    patch_for_log_event.assert_any_call(days_born, sim_day, const.AI_PERFORMED_NOTE)
    patch_for_log_event.assert_any_call(days_born, sim_day, const.INSEMINATED_W_BASE + semen_type)
    assert heifer.semen_num == expected_semen_num
    assert heifer.AI_times == expected_AI_times
    patch_for_compare_rate.assert_called_once_with(conception_rate)
    patch_for_increment_ai_counts.assert_called_once()

    if conception_successful:
        patch_for_successful_conception.assert_called_once_with(sim_day)
        patch_for_failed_conception.assert_not_called()
        patch_for_increment_successful_conceptions.assert_called_once()
    else:
        patch_for_successful_conception.assert_not_called()
        patch_for_failed_conception.assert_called_once_with(sim_day)


@pytest.mark.parametrize(
    "days_born, sim_day",
    [
        # Normal cases
        (100, 120),
        (200, 220),
        (150, 180),
    ]
)
def test_handle_successful_conception(mocker: MockerFixture, days_born: int, sim_day: int) -> None:
    """
    Unit test for _handle_successful_conception() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born

    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_initialize_pregnancy_parameters = mocker.patch.object(heifer, '_initialize_pregnancy_parameters',
                                                                    return_value=None)

    # Act
    heifer._handle_successful_conception(sim_day)

    # Assert
    patch_for_log_event.assert_called_once_with(days_born, sim_day, const.HEIFER_PREG)
    patch_for_initialize_pregnancy_parameters.assert_called_once()


@pytest.mark.parametrize(
    "days_born, sim_day",
    [
        # Normal cases
        (100, 120),
        (200, 220),
        (150, 180),
    ]
)
def test_handle_failed_conception(mocker: MockerFixture, days_born: int, sim_day: int) -> None:
    """
    Unit test for _handle_failed_conception() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born

    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_set_repro_program = mocker.patch.object(heifer, '_set_repro_program', return_value=None)
    patch_for_simulate_estrus = mocker.patch.object(heifer, '_simulate_estrus', return_value=None)

    # Act
    heifer._handle_failed_conception(sim_day)

    # Assert
    patch_for_log_event.assert_called_once_with(days_born, sim_day, const.HEIFER_NOT_PREG)
    patch_for_set_repro_program.assert_called_once_with(sim_day, 'ED')
    patch_for_simulate_estrus.assert_called_once_with(days_born, sim_day, const.ESTRUS_DAY_SCHEDULED_NOTE)


@pytest.mark.parametrize(
    "avg_gestation_len, std_gestation_len, stdi, rvs_return",
    [
        # Normal cases
        (280, 10, 2, 279),
        (285, 5, 1, 286),
        (283, 7, 3, 282),
    ]
)
def test_calculate_gestation_length(mocker: MockerFixture, avg_gestation_len: int,
                                    std_gestation_len: int, stdi: float,
                                    rvs_return: int) -> None:
    """
    Unit test for _calculate_gestation_length() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(AnimalBase, 'config', {
        "avg_gestation_len": avg_gestation_len,
        "std_gestation_len": std_gestation_len
    })
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.STDI', stdi)

    patch_for_truncnorm_rvs = mocker.patch.object(truncnorm, 'rvs', return_value=rvs_return)

    # Act
    result = HeiferII._calculate_gestation_length()

    # Assert
    patch_for_truncnorm_rvs.assert_called_once_with(
        -stdi, stdi, avg_gestation_len, std_gestation_len
    )
    assert result == rvs_return


@pytest.mark.parametrize(
    "breed, avg_weight, std_weight, stdi, rvs_return",
    [
        # Normal cases
        ('HO', 40.0, 5.0, 2.0, 39.0),
        ('JE', 35.0, 4.0, 1.5, 36.5),
        ('HO', 42.0, 6.0, 2.5, 41.0),
        ('JE', 33.0, 3.5, 1.0, 32.0),
    ]
)
def test_calculate_calf_birth_weight(mocker: MockerFixture, breed: str, avg_weight: float, std_weight: float,
                                     stdi: float, rvs_return: float) -> None:
    """
    Unit test for _calculate_calf_birth_weight() static method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(AnimalBase, 'config', {
        f"birth_weight_avg_{breed.lower()}": avg_weight,
        f"birth_weight_std_{breed.lower()}": std_weight
    })
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.STDI', stdi)

    patch_for_truncnorm_rvs = mocker.patch.object(truncnorm, 'rvs', return_value=rvs_return)

    # Act
    result = HeiferII._calculate_calf_birth_weight(breed)  # type: ignore

    # Assert
    patch_for_truncnorm_rvs.assert_called_once_with(
        -stdi, stdi, avg_weight, std_weight
    )
    assert result == rvs_return


@pytest.mark.parametrize(
    "days_born, breeding_start_day, gestation_length, calf_birth_weight, breed",
    [
        # Normal cases
        (100, 80, 280, 40.0, 'HO'),
        (120, 90, 285, 35.0, 'JE'),
        (150, 100, 283, 42.0, 'HO'),
        (130, 95, 270, 38.0, 'JE'),
    ]
)
def test_initialize_pregnancy_parameters(mocker: MockerFixture, days_born: int,
                                         breeding_start_day: int, gestation_length: int,
                                         calf_birth_weight: float, breed: str) -> None:
    """
    Unit test for _initialize_pregnancy_parameters() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.breed = breed

    mocker.patch.object(HeiferII, '_get_breeding_start_day', return_value=breeding_start_day)
    mocker.patch.object(HeiferII, '_calculate_gestation_length', return_value=gestation_length)
    patch_for_calculate_calf_birth_weight = \
        mocker.patch.object(HeiferII, '_calculate_calf_birth_weight', return_value=calf_birth_weight)

    # Act
    heifer._initialize_pregnancy_parameters()

    # Assert
    assert heifer.days_in_preg == 1
    assert heifer.abortion_day == 0
    assert heifer.breeding_to_preg_time == days_born - breeding_start_day
    assert heifer.gestation_length == gestation_length
    assert heifer.calf_birth_weight == calf_birth_weight
    patch_for_calculate_calf_birth_weight.assert_called_once_with(breed)


@pytest.mark.parametrize(
    "days_born, ai_day, sim_day, preg_check_day_1, preg_check_day_2, preg_check_day_3",
    [
        # Days born = ai day + preg check day 1
        (115, 100, 120, 15, 45, 90),

        # Days born = ai day + preg check day 2
        (145, 100, 160, 15, 45, 90),

        # Days born = ai day + preg check day 3
        (190, 100, 200, 15, 45, 90),

        # Days born != ai day + preg check day 1, 2, or 3
        (100, 100, 120, 15, 45, 90),
    ]
)
def test_preg_update(mocker: MockerFixture, days_born: int, ai_day: int, sim_day: int,
                     preg_check_day_1: int, preg_check_day_2: int, preg_check_day_3: int) -> None:
    """
    Unit test for preg_update() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.ai_day = ai_day
    heifer.days_born = days_born

    mocker.patch.object(AnimalBase, 'config', {
        "preg_check_day_1": preg_check_day_1,
        "preg_check_day_2": preg_check_day_2,
        "preg_check_day_3": preg_check_day_3,

        "preg_loss_rate_1": "dummy",
        "preg_loss_rate_2": "dummy",
        "preg_loss_rate_3": "dummy",
    })

    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_LOSS_BEFORE_1', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_CHECK_1_PREG', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_CHECK_1_NOT_PREG', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_LOSS_BTWN_1_AND_2', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_CHECK_2_PREG', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_LOSS_BTWN_2_AND_3', "dummy")
    mocker.patch('RUFAS.routines.animal.life_cycle.heiferII.const.PREG_CHECK_3_PREG', "dummy")

    patch_for_handle_preg_check = mocker.patch.object(heifer, '_handle_preg_check', return_value=None)

    # Act
    heifer.preg_update(sim_day)

    # Assert
    if days_born in [ai_day + preg_check_day_1, ai_day + preg_check_day_2, ai_day + preg_check_day_3]:
        patch_for_handle_preg_check.assert_called_once()
    else:
        patch_for_handle_preg_check.assert_not_called()


@pytest.mark.parametrize(
    "days_born, initial_preg_diagnoses, is_pregnant, loss_rate,"
    "compare_randomized_rate_result, has_on_not_preg, sim_day, expected_preg_diagnoses",
    [
        # Pregnant, pregnancy lost
        (100, 0, True, 0.2, True, False, 120, 1),

        # Pregnant, pregnancy not lost
        (105, 1, True, 0.2, False, False, 120, 2),

        # Not pregnant, with on_not_preg configuration
        (110, 2, False, 0.2, None, True, 120, 3),

        # Not pregnant, without on_not_preg configuration
        (115, 3, False, 0.2, None, False, 120, 4),
    ]
)
def test_handle_preg_check(mocker: MockerFixture, days_born: int, initial_preg_diagnoses: int,
                           is_pregnant: bool, loss_rate: float, compare_randomized_rate_result: bool,
                           has_on_not_preg: bool, sim_day: int, expected_preg_diagnoses: int) -> None:
    """
    Unit test for _handle_preg_check() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    preg_check_config = {
        "loss_rate": loss_rate,
        "on_preg_loss": "PregLossEvent",
        "on_preg": "PregEvent",
    }

    if has_on_not_preg:
        preg_check_config["on_not_preg"] = "NotPregEvent"

    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.preg_diagnoses = initial_preg_diagnoses

    mocker.patch.object(HeiferII, 'is_pregnant', new_callable=mocker.PropertyMock, return_value=is_pregnant)
    mocker.patch.object(HeiferII, '_compare_randomized_rate_less_than', return_value=compare_randomized_rate_result)
    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_terminate_pregnancy = mocker.patch.object(heifer, '_terminate_pregnancy', return_value=None)
    patch_for_open = mocker.patch.object(heifer, 'open', return_value=None)

    # Act
    heifer._handle_preg_check(preg_check_config, sim_day)

    # Assert
    assert heifer.preg_diagnoses == expected_preg_diagnoses
    if is_pregnant:
        if compare_randomized_rate_result:
            patch_for_terminate_pregnancy.assert_called_once_with("PregLossEvent", sim_day)
            patch_for_log_event.assert_not_called()
        else:
            patch_for_log_event.assert_called_once_with(days_born, sim_day, "PregEvent")
    elif has_on_not_preg:
        patch_for_log_event.assert_called_once_with(days_born, sim_day, "NotPregEvent")
        assert heifer.abortion_day == days_born
        patch_for_open.assert_called_once_with(sim_day)
    else:
        patch_for_log_event.assert_not_called()
        patch_for_open.assert_not_called()


@pytest.mark.parametrize(
    "days_born, sim_day, preg_loss_const, "
    "initial_days_in_preg, initial_body_weight, initial_conceptus_weight",
    [
        # Normal cases
        (100, 120, "PregLoss", 20, 500, 5),
        (150, 170, "PregLoss", 30, 550, 10),
    ]
)
def test_terminate_pregnancy(mocker: MockerFixture, days_born: int, sim_day: int, preg_loss_const: str,
                             initial_days_in_preg: int, initial_body_weight: float,
                             initial_conceptus_weight: float) -> None:
    """
    Unit test for _terminate_pregnancy() method of HeiferII class in heiferII.py file.
    """

    # Arrange
    mocker.patch.object(HeiferII, '__init__', return_value=None)
    heifer = HeiferII(mocker.MagicMock())
    heifer.days_born = days_born
    heifer.days_in_preg = initial_days_in_preg
    heifer.body_weight = initial_body_weight
    heifer.conceptus_weight = initial_conceptus_weight

    patch_for_log_event = mocker.patch.object(heifer, 'log_event', return_value=None)
    patch_for_open = mocker.patch.object(heifer, 'open', return_value=None)

    # Act
    heifer._terminate_pregnancy(preg_loss_const, sim_day)

    # Assert
    patch_for_log_event.assert_called_once_with(days_born, sim_day, preg_loss_const)
    assert heifer.abortion_day == days_born
    assert heifer.days_in_preg == 0
    assert heifer.body_weight == initial_body_weight - initial_conceptus_weight
    assert heifer.conceptus_weight == 0
    assert heifer.calf_birth_weight == 0
    assert heifer.p_gest_for_calf == 0
    patch_for_open.assert_called_once_with(sim_day)
