from pytest_mock import MockFixture

from RUFAS.routines.animal.life_cycle.cow import Cow


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
