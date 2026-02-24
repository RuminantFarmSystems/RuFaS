from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.handler.handler import Handler
from RUFAS.biophysical.manure.handler.parlor_cleaning import ParlorCleaningHandler
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.user_constants import UserConstants


@pytest.fixture
def handler() -> Handler:
    """Default handler instance."""
    return Handler("handler_name", "ManualScraper", 3, 0.8, False)


def test_process_manure_parlor_cleaning(mocker: MockerFixture) -> None:
    """Tests the main process routine of handler related to parlor cleaning."""
    handler = ParlorCleaningHandler("handler_name", "ParlorCleaning", 3, 0.8, False)
    mock_fresh_water_volume_used_for_milking = mocker.patch.object(
        handler, "determine_fresh_water_volume_used_for_milking", return_value=0.0
    )
    handler.handler_type = "ParlorCleaning"
    pen = PenManureData(1, 12, AnimalCombination.LAC_COW, "freestall", 15, 13, StreamType.GENERAL)
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
        methane_production_potential=0.24,
        pen_manure_data=pen,
        bedding_non_degradable_volatile_solids=0.0
    )
    original_stream = handler.manure_stream
    add_error_patch = mocker.patch.object(handler._om, "add_error")
    add_variable_patch = mocker.patch.object(handler._om, "add_variable")
    cleaning_water_return = 100.0
    barn_temperature_return = 25.0
    cleaning_patch = mocker.patch.object(
        handler, "determine_handler_cleaning_water_volume", return_value=cleaning_water_return
    )
    temp_patch = mocker.patch.object(handler, "_determine_barn_temperature", return_value=barn_temperature_return)
    conditions = CurrentDayConditions(
        mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
    )
    time_obj = MagicMock(RufasTime)
    result = handler.process_manure(conditions, time_obj)
    add_error_patch.assert_not_called()
    expected_total_cleaning_water_volume = (cleaning_water_return + 0.0) * GeneralConstants.LITERS_TO_CUBIC_METERS
    assert add_variable_patch.call_count == 19
    assert original_stream.pen_manure_data is not None
    cleaning_patch.assert_called_once_with(
        original_stream.pen_manure_data.num_animals,
        handler.cleaning_water_use_amount,
        handler.cleaning_water_recycle_fraction,
    )
    temp_patch.assert_called_once_with(conditions.mean_air_temperature)
    expected_manure_water = (
        original_stream.water + expected_total_cleaning_water_volume * UserConstants.WATER_DENSITY_KG_PER_M3
    )

    expected_ammoniacal_nitrogen = max(0.0, original_stream.ammoniacal_nitrogen - 0.0)
    manure_result = result["manure"]
    mock_fresh_water_volume_used_for_milking.assert_called_once()
    assert manure_result.water == expected_manure_water
    assert manure_result.ammoniacal_nitrogen == expected_ammoniacal_nitrogen
    assert manure_result.nitrogen == original_stream.nitrogen
    assert manure_result.phosphorus == original_stream.phosphorus
    assert manure_result.potassium == original_stream.potassium
    assert manure_result.ash == original_stream.ash
    assert manure_result.non_degradable_volatile_solids == original_stream.non_degradable_volatile_solids
    assert manure_result.degradable_volatile_solids == original_stream.degradable_volatile_solids
    assert manure_result.volume == original_stream.volume + expected_total_cleaning_water_volume
    assert manure_result.total_solids == original_stream.total_solids
    assert manure_result.pen_manure_data is None
    assert handler.manure_stream is None


def test_process_manure(handler: Handler, mocker: MockerFixture) -> None:
    """Tests the main process routine of handler."""
    pen = PenManureData(1, 12, AnimalCombination.LAC_COW, "freestall", 15, 13, StreamType.GENERAL)
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
        methane_production_potential=0.24,
        pen_manure_data=pen,
        bedding_non_degradable_volatile_solids=0.0
    )
    original_stream = handler.manure_stream
    add_error_patch = mocker.patch.object(handler._om, "add_error")
    add_variable_patch = mocker.patch.object(handler._om, "add_variable")
    cleaning_water_return = 100.0
    barn_temperature_return = 25.0
    cleaning_patch = mocker.patch.object(
        handler, "determine_handler_cleaning_water_volume", return_value=cleaning_water_return
    )
    temp_patch = mocker.patch.object(handler, "_determine_barn_temperature", return_value=barn_temperature_return)
    conditions = CurrentDayConditions(
        mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
    )
    time_obj = MagicMock(RufasTime)
    result = handler.process_manure(conditions, time_obj)
    add_error_patch.assert_not_called()
    expected_total_cleaning_water_volume = (cleaning_water_return + 0.0) * GeneralConstants.LITERS_TO_CUBIC_METERS
    assert add_variable_patch.call_count == 17
    assert original_stream.pen_manure_data is not None
    cleaning_patch.assert_called_once_with(
        original_stream.pen_manure_data.num_animals,
        handler.cleaning_water_use_amount,
        handler.cleaning_water_recycle_fraction,
    )
    temp_patch.assert_called_once_with(conditions.mean_air_temperature)
    expected_manure_water = (
        original_stream.water + expected_total_cleaning_water_volume * UserConstants.WATER_DENSITY_KG_PER_M3
    )

    expected_ammoniacal_nitrogen = max(0.0, original_stream.ammoniacal_nitrogen - 0.0)
    manure_result = result["manure"]
    assert manure_result.water == expected_manure_water
    assert manure_result.ammoniacal_nitrogen == expected_ammoniacal_nitrogen
    assert manure_result.nitrogen == original_stream.nitrogen
    assert manure_result.phosphorus == original_stream.phosphorus
    assert manure_result.potassium == original_stream.potassium
    assert manure_result.ash == original_stream.ash
    assert manure_result.non_degradable_volatile_solids == original_stream.non_degradable_volatile_solids
    assert manure_result.degradable_volatile_solids == original_stream.degradable_volatile_solids
    assert manure_result.volume == original_stream.volume + expected_total_cleaning_water_volume
    assert manure_result.total_solids == original_stream.total_solids
    assert manure_result.pen_manure_data is None
    assert handler.manure_stream is None


def test_process_manure_error(handler: Handler, mocker: MockerFixture) -> None:
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
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=0.0
    )
    mock_add_error = mocker.patch.object(handler._om, "add_error")
    try:
        conditions = CurrentDayConditions(
            mean_air_temperature=20.0, incoming_light=15, min_air_temperature=0, max_air_temperature=30
        )
        time_obj = MagicMock(RufasTime)
        handler.process_manure(conditions, time_obj)
        assert False
    except TypeError:
        mock_add_error.assert_called_once()


@pytest.mark.parametrize("compatible", [True, False])
def test_receive_manure(compatible: bool, handler: Handler, mocker: MockerFixture) -> None:
    """Tests the basic receiving of manure."""
    mock_add_error = mocker.patch.object(handler._om, "add_error")
    mock_check = mocker.patch.object(handler, "check_manure_stream_compatibility", return_value=compatible)
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
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=0.0
    )
    if compatible:
        handler.receive_manure(empty_stream)
        mock_check.assert_called_once()
        mock_add_error.assert_not_called()
    else:
        try:
            handler.receive_manure(empty_stream)
            assert False
        except ValueError:
            mock_check.assert_called_once()
            mock_add_error.assert_called_once()


@pytest.mark.parametrize(
    "num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction,expected ",
    [(15, 0.7, 0.4, 6.3), (15, 0.5, 0.2, 6.0)],
)
def test_determine_handler_cleaning_water_volume(
    num_animals: int,
    cleaning_water_use_rate: float,
    cleaning_water_recycle_fraction: float,
    expected: float,
    handler: Handler,
) -> None:
    """Tests the calculation of cleaning water volume."""
    assert (
        handler.determine_handler_cleaning_water_volume(
            num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction
        )
        == expected
    )


@pytest.mark.parametrize(
    "num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction,expected ",
    [(15, 0.7, 0.4, 6.3), (15, 0.5, 0.2, 6.0)],
)
def test_determine_handler_cleaning_water_volume_parlor_use_flush(
    num_animals: int,
    cleaning_water_use_rate: float,
    cleaning_water_recycle_fraction: float,
    expected: float,
    handler: Handler,
) -> None:
    """Tests the calculation of cleaning water volume."""
    handler.handler_type = "ParlorCleaning"
    handler.use_parlor_flush = True
    assert (
        handler.determine_handler_cleaning_water_volume(
            num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction
        )
        == expected
    )


@pytest.mark.parametrize(
    "num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction",
    [(15, 0.7, 0.4)],
)
def test_determine_handler_cleaning_water_volume_parlor_no_flush_(
    num_animals: int,
    cleaning_water_use_rate: float,
    cleaning_water_recycle_fraction: float,
    handler: Handler,
) -> None:
    """Tests the calculation of cleaning water volume."""
    handler.handler_type = "ParlorCleaning"
    handler.use_parlor_flush = False
    assert (
        handler.determine_handler_cleaning_water_volume(
            num_animals, cleaning_water_use_rate, cleaning_water_recycle_fraction
        )
        == 0
    )


@pytest.mark.parametrize(
    "parent_compatibility, pen_data, expected",
    [
        (True, PenManureData(10, 15, AnimalCombination.LAC_COW, "abc", 15.2, 45, StreamType.GENERAL), True),
        (True, None, False),
        (True, PenManureData(10, 15, AnimalCombination.LAC_COW, "freestall", 15.2, 45, StreamType.GENERAL), True),
        (False, PenManureData(10, 15, AnimalCombination.LAC_COW, "open lot", 15.2, 45, StreamType.GENERAL), False),
    ],
)
def test_check_manure_stream_compatibility(
    parent_compatibility: bool, pen_data: None | PenManureData, expected: bool, handler: Handler, mocker: MockerFixture
) -> None:
    """Tests the basic compatibility check logic."""
    mock_parent_check = mocker.patch.object(
        Processor, "check_manure_stream_compatibility", return_value=parent_compatibility
    )
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
        methane_production_potential=0.24,
        pen_manure_data=pen_data,
        bedding_non_degradable_volatile_solids=0.0
    )
    assert handler.check_manure_stream_compatibility(empty_stream) == expected
    mock_parent_check.assert_called_once()


def test_determine_fresh_water_volume_used_for_milking(handler: Handler) -> None:
    """Test the function determine_fresh_water_volume_used_for_milking()."""
    assert handler.determine_fresh_water_volume_used_for_milking(1) == 30


def test_determine_total_cleaning_water_volume(handler: Handler) -> None:
    """Tests the function determine_total_cleaning_water_volume()."""
    assert handler.determine_total_cleaning_water_volume(1000, 1000) == 2


def test_determine_manure_water(handler: Handler) -> None:
    """Tests the function determine_manure_water()."""
    assert handler.determine_manure_water(100000, 20000) == 100019.94
