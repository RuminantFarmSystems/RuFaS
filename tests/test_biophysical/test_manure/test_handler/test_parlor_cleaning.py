from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.handler.handler import HandlerConfig, Handler
from RUFAS.biophysical.manure.handler.parlor_cleaning import ParlorCleaningHandler
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time


@pytest.fixture
def handler(mocker: MockerFixture) -> ParlorCleaningHandler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return ParlorCleaningHandler("handler_name", True, mock_manure_handler_config)


def test_process_manure(handler: ParlorCleaningHandler, mocker: MockerFixture) -> None:
    """Tests main process routine on valid manure stream types."""
    pen = PenManureData(1, 12, AnimalCombination.LAC_COW, "freestall", 15, 13, StreamType.GENERAL)
    stream = ManureStream(
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
        pen_manure_data=pen,
    )
    mock_milking_water_volume = mocker.patch.object(
        handler, "determine_fresh_water_volume_used_for_milking", return_value=10
    )
    conditions = CurrentDayConditions(
        mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
    )
    handler.manure_stream = stream
    mock_process = mocker.patch.object(Handler, "process_manure", return_value={"manure": stream})
    result = handler.process_manure(conditions, MagicMock(Time))

    assert result["manure"] == stream
    mock_process.assert_called_once()
    mock_milking_water_volume.assert_called_once()
    assert handler.fresh_water_volume_used_for_milking == 10


def test_process_manure_error(handler: ParlorCleaningHandler, mocker: MockerFixture) -> None:
    """Tests main process routine on invalid manure stream types."""
    handler.manure_stream = ManureStream(
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
    mock_add_error = mocker.patch.object(handler._om, "add_error")
    try:
        conditions = CurrentDayConditions(
            mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
        )
        time_obj = MagicMock(Time)
        handler.process_manure(conditions, time_obj)
        assert False
    except TypeError:
        mock_add_error.assert_called_once()


def test_receive_manure(handler: ParlorCleaningHandler, mocker: MockerFixture) -> None:
    """Test the manure receiving method."""
    manure_stream = ManureStream(
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
    mock_receive = mocker.patch.object(Handler, "receive_manure")
    handler.receive_manure(manure_stream)
    assert handler.manure_stream == manure_stream
    mock_receive.assert_called_once()


def test_receive_manure_multiple_streams(handler: ParlorCleaningHandler, mocker: MockerFixture) -> None:
    """Test the manure receiving method with multiple streams."""
    manure_stream = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=0.0,
        phosphorus=0.0,
        potassium=2.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=0.0,
        pen_manure_data=None,
    )
    mock_receive = mocker.patch.object(Handler, "receive_manure")
    handler.manure_stream = manure_stream
    handler.receive_manure(manure_stream)
    assert handler.manure_stream == ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=0.0,
        phosphorus=0.0,
        potassium=4.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=0.0,
        pen_manure_data=None,
    )
    mock_receive.assert_called_once()


@pytest.mark.parametrize("num_animals,expected", [(1, 30), (5, 150), (10, 300)])
def test_determine_fresh_water_volume_used_for_milking(
    num_animals: int, expected: float, handler: ParlorCleaningHandler
) -> None:
    """Tests the calculation of fresh water used for milking."""
    assert handler.determine_fresh_water_volume_used_for_milking(num_animals) == expected


@pytest.mark.parametrize("use_flush,expected", [(True, 3), (False, 0.0)])
def test_determine_cleaning_water_volume_in_main_barn(
    use_flush: bool, expected: float, handler: ParlorCleaningHandler, mocker: MockerFixture
) -> None:
    """Tests the calculation of the overwritten cleaning water volume."""
    handler.config.use_parlor_flush = use_flush
    mock_calc = mocker.patch.object(Handler, "determine_cleaning_water_volume_in_main_barn", return_value=expected)
    result = handler.determine_cleaning_water_volume_in_main_barn(10, 0.7, 0.7)
    if use_flush:
        assert result == expected
        mock_calc.assert_called_once()
    else:
        mock_calc.assert_not_called()
    assert result == expected
