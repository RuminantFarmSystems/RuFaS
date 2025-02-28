from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.single_stream_handler import SingleStreamHandler
from RUFAS.biophysical.manure.handler import HandlerConfig, Handler
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import PenManureData, ManureStream, StreamType
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time


@pytest.fixture
def handler(mocker: MockerFixture) -> SingleStreamHandler:
    """Default handler instance."""
    mock_manure_handler_config = mocker.MagicMock(auto_spec=HandlerConfig)
    return SingleStreamHandler("handler_name", False, mock_manure_handler_config)


def test_receive_manure(handler: SingleStreamHandler, mocker: MockerFixture) -> None:
    """Tests single handler's manure receiving logic."""
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


def test_receive_manure_error(handler: SingleStreamHandler, mocker: MockerFixture) -> None:
    """Tests single handler's manure receiving logic."""
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
    handler.manure_stream = manure_stream
    try:
        handler.receive_manure(manure_stream)
        assert False
    except ValueError:
        assert handler.manure_stream == manure_stream
        mock_receive.assert_called_once()


def test_process_manure(handler: SingleStreamHandler, mocker: MockerFixture) -> None:
    """Tests the main manure process of single handler."""
    pen = PenManureData(1, 12, AnimalCombination.LAC_COW, "freestall", 15, 13, 11, StreamType.GENERAL)
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
    mock_barn_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    mock_ammonia_emission = mocker.patch.object(handler, "_calculate_ammonia_emissions", return_value=12)
    mock_barn_temp = mocker.patch.object(handler, "determine_barn_temperature", return_value=16)
    mock_process = mocker.patch.object(Handler, "process_manure", return_value={"manure": stream})
    conditions = CurrentDayConditions(
        mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
    )
    handler.manure_stream = stream

    result = handler.process_manure(conditions, MagicMock(Time))

    assert result["manure"] == stream
    assert handler.ammonia_emission == 12
    mock_barn_area.assert_called_once()
    mock_process.assert_called_once()
    mock_ammonia_emission.assert_called_once()
    mock_barn_temp.assert_called_once()


def test_process_manure_error(handler: SingleStreamHandler, mocker: MockerFixture) -> None:
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


@pytest.mark.parametrize("temp, expected", [(15, 224.9), (5, 154.7)])
def test_determine_ammonia_resistance_default_hsc(temp: float, expected: float, handler: SingleStreamHandler) -> None:
    """Tests the calculation of ammonia resistance using default hsc value."""
    assert handler.determine_ammonia_resistance(temp) == expected


@pytest.mark.parametrize(
    "animal_combination,pen_type,num_stalls,barn_temperature,expected",
    [
        (AnimalCombination.LAC_COW, "test_type", 10, -100, 0.0),
        (AnimalCombination.LAC_COW, "test_type", 10, 15.3, 0.01989),
    ],
)
def test_determine_housing_methane_emissions(
    animal_combination: AnimalCombination,
    pen_type: str,
    num_stalls: int,
    barn_temperature: float,
    expected: float,
    handler: SingleStreamHandler,
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of methane emission."""
    mock_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    assert (
        handler.determine_housing_methane_emissions(animal_combination, pen_type, num_stalls, barn_temperature)
        == expected
    )
    mock_area.assert_called_once()


@pytest.mark.parametrize(
    "animal_combination,pen_type,num_stalls,barn_temperature,expected",
    [
        (AnimalCombination.LAC_COW, "test_type", 10, -100, 0.0),
        (AnimalCombination.LAC_COW, "test_type", 10, 15.3, 0.0030026),
    ],
)
def test_determine_housing_carbon_dioxide_emissions(
    animal_combination: AnimalCombination,
    pen_type: str,
    num_stalls: int,
    barn_temperature: float,
    expected: float,
    handler: SingleStreamHandler,
    mocker: MockerFixture,
) -> None:
    """Tests the calculation of carbon dioxide emission."""
    mock_area = mocker.patch.object(Handler, "determine_barn_area", return_value=10)
    assert (
        handler.determine_housing_carbon_dioxide_emissions(animal_combination, pen_type, num_stalls, barn_temperature)
        == expected
    )
    mock_area.assert_called_once()
