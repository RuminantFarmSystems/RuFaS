import pytest
from pytest import approx
from pytest_mock import MockerFixture

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_handlers import milking_parlor
from RUFAS.routines.manure.manure_handlers.milking_parlor import MilkingParlor


@pytest.fixture
def mock_milking_parlor() -> MilkingParlor:
    """Fixture for MilkingParlor class in file milking_parlor.py"""

    return MilkingParlor(
            num_milkings=3,
            minutes_spent_in_holding_area=30.0,
            minutes_spent_per_milking=10.0,
            wash_water_use_rate=20.0,
            fresh_water_use_rate=10.0
    )


def test_milking_parlor_init() -> None:
    """Unit test for __init__() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    num_milkings = 3
    minutes_spent_in_holding_area = 30.0
    minutes_spent_per_milking = 10.0
    wash_water_use_rate = 20.0
    fresh_water_use_rate = 10.0

    # Act
    milking_parlor = MilkingParlor(
            num_milkings=num_milkings,
            minutes_spent_in_holding_area=minutes_spent_in_holding_area,
            minutes_spent_per_milking=minutes_spent_per_milking,
            wash_water_use_rate=wash_water_use_rate,
            fresh_water_use_rate=fresh_water_use_rate
    )

    # Assert
    assert milking_parlor.num_milkings == num_milkings
    assert milking_parlor.minutes_spent_in_holding_area == minutes_spent_in_holding_area
    assert milking_parlor.minutes_spent_per_milking == minutes_spent_per_milking
    assert milking_parlor.wash_water_use_rate == wash_water_use_rate
    assert milking_parlor.fresh_water_use_rate == fresh_water_use_rate


def test_total_minutes_spent_in_holding_area(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for total_minutes_spent_in_holding_area() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_total_minutes_spent_in_holding_area = (mock_milking_parlor.num_milkings *
                                                    mock_milking_parlor.minutes_spent_in_holding_area)

    # Act
    total_minutes_spent_in_holding_area = mock_milking_parlor.total_minutes_spent_in_holding_area

    # Assert
    assert total_minutes_spent_in_holding_area == approx(expected_total_minutes_spent_in_holding_area)


def test_fraction_of_day_spent_in_holding_area(mocker: MockerFixture,
                                               mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for fraction_of_day_spent_in_holding_area() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_fraction_of_day = 0.25
    milking_parlor.total_minutes_spent_in_holding_area = 360.0
    patch_for_calc_fraction_of_day_from_minutes = mocker.patch(
            'RUFAS.routines.manure.manure_handlers.milking_parlor.MilkingParlor._calc_fraction_of_day_from_minutes',
            return_value=expected_fraction_of_day)

    # Act
    fraction_of_day = mock_milking_parlor.fraction_of_day_spent_in_holding_area

    # Assert
    assert fraction_of_day == approx(expected_fraction_of_day)
    patch_for_calc_fraction_of_day_from_minutes.assert_called_once_with(
            mock_milking_parlor.total_minutes_spent_in_holding_area)


def test_calc_wash_water_volume_used_in_holding_area(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for calc_wash_water_volume_used_in_holding_area() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    num_cows = 10
    expected_wash_water_volume_used_in_holding_area = num_cows * mock_milking_parlor.wash_water_use_rate

    # Act
    wash_water_volume_used_in_holding_area = mock_milking_parlor.calc_wash_water_volume_used_in_holding_area(num_cows)

    # Assert
    assert wash_water_volume_used_in_holding_area == approx(expected_wash_water_volume_used_in_holding_area)


def test_total_minutes_spent_milking(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for total_minutes_spent_milking() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_total_minutes_spent_milking = (mock_milking_parlor.num_milkings *
                                            mock_milking_parlor.minutes_spent_per_milking)

    # Act
    total_minutes_spent_milking = mock_milking_parlor.total_minutes_spent_milking

    # Assert
    assert total_minutes_spent_milking == approx(expected_total_minutes_spent_milking)


def test_fraction_of_day_spent_milking(mocker: MockerFixture,
                                       mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for fraction_of_day_spent_milking() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_fraction_of_day = 0.25
    milking_parlor.total_minutes_spent_milking = 360.0
    patch_for_calc_fraction_of_day_from_minutes = mocker.patch(
            'RUFAS.routines.manure.manure_handlers.milking_parlor.MilkingParlor._calc_fraction_of_day_from_minutes',
            return_value=expected_fraction_of_day)

    # Act
    fraction_of_day = mock_milking_parlor.fraction_of_day_spent_milking

    # Assert
    assert fraction_of_day == approx(expected_fraction_of_day)
    patch_for_calc_fraction_of_day_from_minutes.assert_called_once_with(
            mock_milking_parlor.total_minutes_spent_milking)


def test_calc_fresh_water_volume_used_for_milking(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for calc_fresh_water_volume_used_for_milking() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    num_cows = 10
    expected_fresh_water_volume_used_for_milking = num_cows * mock_milking_parlor.fresh_water_use_rate

    # Act
    fresh_water_volume_used_for_milking = mock_milking_parlor.calc_fresh_water_volume_used_for_milking(num_cows)

    # Assert
    assert fresh_water_volume_used_for_milking == approx(expected_fresh_water_volume_used_for_milking)


def test_total_minutes_spent_in_milking_parlor(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for total_minutes_spent_in_milking_parlor() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_total_minutes_spent_in_milking_parlor = (mock_milking_parlor.total_minutes_spent_in_holding_area +
                                                      mock_milking_parlor.total_minutes_spent_milking)

    # Act
    total_minutes_spent_in_milking_parlor = mock_milking_parlor.total_minutes_spent_in_milking_parlor

    # Assert
    assert total_minutes_spent_in_milking_parlor == approx(expected_total_minutes_spent_in_milking_parlor)


def test_total_fraction_of_day_spent_in_milking_parlor(mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for total_fraction_of_day_spent_in_milking_parlor() of class MilkingParlor in file milking_parlor.py"""

    # Arrange
    expected_total_fraction_of_day_spent_in_milking_parlor = (
            mock_milking_parlor.fraction_of_day_spent_in_holding_area +
            mock_milking_parlor.fraction_of_day_spent_milking)

    # Act
    total_fraction_of_day_spent_in_milking_parlor = mock_milking_parlor.total_fraction_of_day_spent_in_milking_parlor

    # Assert
    assert total_fraction_of_day_spent_in_milking_parlor == \
           approx(expected_total_fraction_of_day_spent_in_milking_parlor)


def test_calc_total_water_volume_used_in_milking_parlor(mocker: MockerFixture,
                                                        mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for calc_total_water_volume_used_in_milking_parlor() in file milking_parlor.py"""

    # Arrange
    num_cows = 10
    wash_water_volume_used_in_holding_area = 100.0
    fresh_water_volume_used_for_milking = 200.0
    patch_for_calc_wash_water_volume_used_in_holding_area = mocker.patch(
            'RUFAS.routines.manure.manure_handlers.milking_parlor.MilkingParlor'
            '.calc_wash_water_volume_used_in_holding_area',
            return_value=wash_water_volume_used_in_holding_area)
    patch_for_calc_fresh_water_volume_used_for_milking = mocker.patch(
            'RUFAS.routines.manure.manure_handlers.milking_parlor.MilkingParlor'
            '.calc_fresh_water_volume_used_for_milking',
            return_value=fresh_water_volume_used_for_milking)
    expected_total_water_volume_used_in_milking_parlor = (wash_water_volume_used_in_holding_area +
                                                          fresh_water_volume_used_for_milking)

    # Act
    total_water_volume_used_in_milking_parlor = mock_milking_parlor.calc_total_water_volume_used_in_milking_parlor(
            num_cows)

    # Assert
    assert total_water_volume_used_in_milking_parlor == approx(expected_total_water_volume_used_in_milking_parlor)
    patch_for_calc_wash_water_volume_used_in_holding_area.assert_called_once_with(num_cows)
    patch_for_calc_fresh_water_volume_used_for_milking.assert_called_once_with(num_cows)


@pytest.mark.parametrize('num_cows', [10, 0])
def test_calc_manure_mass_deposited_in_milking_parlor(num_cows: int,
                                                      mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for calc_manure_mass_deposited_in_milking_parlor() in file milking_parlor.py"""

    # Arrange
    manure_mass = 100.0

    # Act
    manure_mass_deposited_in_milking_parlor = mock_milking_parlor.calc_manure_mass_deposited_in_milking_parlor(
            num_cows, manure_mass)

    # Assert
    if num_cows > 0:
        assert manure_mass_deposited_in_milking_parlor == \
               approx(manure_mass * mock_milking_parlor.total_fraction_of_day_spent_in_milking_parlor)
    else:
        assert manure_mass_deposited_in_milking_parlor == approx(0.0)


def test_calc_manure_volume_deposited_in_milking_parlor(mocker: MockerFixture,
                                                        mock_milking_parlor: MilkingParlor) -> None:
    """Unit test for calc_manure_volume_deposited_in_milking_parlor() in file milking_parlor.py"""

    # Arrange
    num_cows = 10
    manure_mass = 100.0
    manure_mass_deposited_in_milking_parlor = 50.0
    patch_for_calc_manure_mass_deposited_in_milking_parlor = mocker.patch(
            'RUFAS.routines.manure.manure_handlers.milking_parlor.MilkingParlor'
            '.calc_manure_mass_deposited_in_milking_parlor',
            return_value=manure_mass_deposited_in_milking_parlor)
    expected_manure_volume_deposited_in_milking_parlor = (manure_mass_deposited_in_milking_parlor /
                                                          ManureConstants.MANURE_DENSITY)

    # Act
    manure_volume_deposited_in_milking_parlor = mock_milking_parlor.calc_manure_volume_deposited_in_milking_parlor(
            num_cows, manure_mass)

    # Assert
    assert manure_volume_deposited_in_milking_parlor == approx(expected_manure_volume_deposited_in_milking_parlor)
    patch_for_calc_manure_mass_deposited_in_milking_parlor.assert_called_once_with(num_cows, manure_mass)


def test_calc_fraction_of_day_from_minutes() -> None:
    """Unit test for _calc_fraction_of_day_from_minutes() in file milking_parlor.py"""

    # Arrange
    minutes = 60
    expected_fraction_of_day = minutes / 1440

    # Act
    fraction_of_day = MilkingParlor._calc_fraction_of_day_from_minutes(minutes)

    # Assert
    assert fraction_of_day == approx(expected_fraction_of_day)
