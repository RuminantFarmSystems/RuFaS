from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.handler import HandlerConfig, Handler
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.enums import AnimalCombination
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time


@pytest.fixture
def handler(mocker: MockerFixture) -> Handler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return Handler("handler_name", True, mock_manure_handler_config)


@pytest.mark.parametrize(
    "compatible",
    [True, False]
)
def test_receive_manure(compatible: bool, handler: Handler, mocker: MockerFixture) -> None:
    """Tests the basic receiving of manure."""
    mock_add_error = mocker.patch.object(handler._om, "add_error")
    mock_check = mocker.patch.object(handler, "check_manure_stream_compatibility",
                                     return_value=compatible)
    empty_stream = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=0.0,
        phosphorus=0.0,
        potassium=0.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=0.0,
        pen_manure_data=None,
    )
    handler.receive_manure(empty_stream)
    if compatible:
        mock_check.assert_called_once()
        mock_add_error.assert_not_called()
    else:
        mock_check.assert_called_once()
        mock_add_error.assert_called_once()


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
    "parent_compatibility, pen_data, expected",
    [(True, PenManureData(10, 15, AnimalCombination.LAC_COW, "abc", 15.2, 45, 2, StreamType.GENERAL), False),
     (False, None, False),
     (True, PenManureData(10, 15, AnimalCombination.LAC_COW, "freestall", 15.2, 45, 2, StreamType.GENERAL), True)]
)
def test_check_manure_stream_compatibility(parent_compatibility: bool,
                                           pen_data: None | PenManureData,
                                           expected: bool,
                                           handler: Handler,
                                           mocker: MockerFixture) -> None:
    """Tests the basic compatibility check logic."""
    mock_parent_check = mocker.patch.object(Processor, "check_manure_stream_compatibility",
                                            return_value=parent_compatibility)
    empty_stream = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=0.0,
        phosphorus=0.0,
        potassium=0.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=0.0,
        pen_manure_data=pen_data,
    )
    assert handler.check_manure_stream_compatibility(empty_stream) == expected
    mock_parent_check.assert_called_once()


def test_process_manure_error(handler: Handler, mocker: MockerFixture) -> None:
    """Tests the main logic of manure stream processing."""
    mock_add_error = mocker.patch.object(handler._om, "add_error")
    try:
        handler.process_manure(MagicMock(CurrentDayConditions), MagicMock(Time))
        assert False
    except TypeError:
        mock_add_error.assert_called_once()


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
