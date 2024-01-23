from pytest_mock import MockFixture

from RUFAS.routines.animal.life_cycle.cow import Cow


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
