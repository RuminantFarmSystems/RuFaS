import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.digester.single_handler import SingleHandler
from RUFAS.biophysical.manure.handler import HandlerConfig, Handler
from RUFAS.enums import AnimalCombination


@pytest.fixture
def handler(mocker: MockerFixture) -> SingleHandler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return SingleHandler("handler_name", False, mock_manure_handler_config)


@pytest.mark.parametrize("temp, hsc, expected", [(15, 130, 112.45), (5, 224, 133.28), (5, 260, 154.7)])
def test_determine_ammonia_resistance_custom_hsc(
    temp: float, expected: float, hsc: float, handler: SingleHandler
) -> None:
    """Tests the calculation of ammonia resistance using custom set hsc values."""
    assert handler.determine_ammonia_resistance(temp, hsc) == expected


@pytest.mark.parametrize("temp, expected", [(15, 224.9), (5, 154.7)])
def test_determine_ammonia_resistance_default_hsc(temp: float, expected: float, handler: SingleHandler) -> None:
    """Tests the calculation of ammonia resistance using default hsc value."""
    assert handler.determine_ammonia_resistance(temp) == expected


@pytest.mark.parametrize(
    "animal_combination,pen_type,num_stalls,barn_temperature,expected",
    [
        (AnimalCombination.LAC_COW, "test_type", 10, -100, 0.0),
        (AnimalCombination.LAC_COW, "test_type", 10, 15.3, 0.01989),
    ],
)
def test_determine_methane_emissions(
    animal_combination: AnimalCombination,
    pen_type: str,
    num_stalls: int,
    barn_temperature: float,
    expected: float,
    handler: SingleHandler,
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of methane emission."""
    mock_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    assert handler.determine_methane_emissions(animal_combination, pen_type, num_stalls, barn_temperature) == expected
    mock_area.assert_called_once()


@pytest.mark.parametrize(
    "animal_combination,pen_type,num_stalls,barn_temperature,expected",
    [
        (AnimalCombination.LAC_COW, "test_type", 10, -100, 0.0),
        (AnimalCombination.LAC_COW, "test_type", 10, 15.3, 0.01989),
    ],
)
def test_determine_methane_emissions(
    animal_combination: AnimalCombination,
    pen_type: str,
    num_stalls: int,
    barn_temperature: float,
    expected: float,
    handler: SingleHandler,
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of methane emission."""
    mock_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    assert handler.determine_methane_emissions(animal_combination, pen_type, num_stalls, barn_temperature) == expected
    mock_area.assert_called_once()
