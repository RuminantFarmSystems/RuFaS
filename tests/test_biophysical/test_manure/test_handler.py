import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.handler import HandlerConfig, Handler
from RUFAS.enums import AnimalCombination
from RUFAS.output_manager import OutputManager


@pytest.fixture
def handler(mocker: MockerFixture) -> Handler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return Handler(False, mock_manure_handler_config)


@pytest.mark.parametrize("air_temp, expected", [(-5, 5), (15, 15), (45, 30)])
def test_determine_barn_temperature(air_temp: float, expected: float, handler: Handler) -> None:
    """Tests the adjustment of barn temperature."""
    assert handler.determine_barn_temperature(air_temp) == expected


@pytest.mark.parametrize(
    "num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction,expected ",
    [(15, 0.7, 0.4, 6.3), (15, 0.5, 0.2, 6.0)],
)
def test_determine_cleaning_water_volume_in_main_barn(
    num_animals: int,
    cleaning_water_use_rate: float,
    cleaning_water_recycle_fraction: float,
    expected: float,
    handler: Handler,
) -> None:
    """Tests the calculation of cleaning water volume in barn."""
    assert (
        handler.determine_cleaning_water_volume_in_main_barn(
            num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction
        )
        == expected
    )


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
    handler: Handler,
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
        (AnimalCombination.LAC_COW, "test_type", 10, 15.3, 0.0030026),
    ],
)
def test_determine_carbon_dioxide_emissions(
    animal_combination: AnimalCombination,
    pen_type: str,
    num_stalls: int,
    barn_temperature: float,
    expected: float,
    handler: Handler,
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of carbon dioxide emission."""
    mock_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    assert (
        handler.determine_carbon_dioxide_emissions(animal_combination, pen_type, num_stalls, barn_temperature)
        == expected
    )
    mock_area.assert_called_once()


def test_determine_barn_area_error(handler: Handler, mocker: MockerFixture) -> None:
    """Tests the calculation of exposed barn area when invalid barn types were given."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    try:
        handler.determine_barn_area(AnimalCombination.LAC_COW, "error", 10)
        assert False
    except ValueError:
        mock_add_error.assert_called_once()


@pytest.mark.parametrize(
    "animal_combination, pen_type, num_stalls, expected",
    [
        (AnimalCombination.LAC_COW, "freestall", 10, 12),
        (AnimalCombination.CLOSE_UP, "freestall", 10, 10),
        (AnimalCombination.LAC_COW, "tiestall", 10, 35),
        (AnimalCombination.CLOSE_UP, "tiestall", 10, 25),
    ],
)
def test_determine_barn_area(
    animal_combination: AnimalCombination, pen_type: str, num_stalls: int, expected: float, handler: Handler
) -> None:
    """Tests the calculation of exposed barn area."""
    assert handler.determine_barn_area(animal_combination, pen_type, num_stalls) == expected


@pytest.mark.parametrize("temp, hsc, expected", [(15, 130, 112.45), (5, 224, 133.28), (5, 260, 154.7)])
def test_determine_ammonia_resistance_custom_hsc(temp: float, expected: float, hsc: float, handler: Handler) -> None:
    """Tests the calculation of ammonia resistance using custom set hsc values."""
    assert handler.determine_ammonia_resistance(temp, hsc) == expected


@pytest.mark.parametrize("temp, expected", [(15, 224.9), (5, 154.7)])
def test_determine_ammonia_resistance_default_hsc(temp: float, expected: float, handler: Handler) -> None:
    """Tests the calculation of ammonia resistance using default hsc value."""
    assert handler.determine_ammonia_resistance(temp) == expected
