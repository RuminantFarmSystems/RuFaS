from copy import copy
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor, \
    METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO, SLURRY_MANURE_DENSITY, STORAGE_HSC
from RUFAS.biophysical.manure.storage.storage import DEFAULT_PH_FOR_AMMONIA, \
    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


@pytest.fixture
def stored_manure() -> ManureStream:
    """Returns a fixture ManureStream instance representing stored manure."""
    return ManureStream(
        water=10.11,
        ammoniacal_nitrogen=20.22,
        nitrogen=30.33,
        phosphorus=40.44,
        potassium=50.55,
        ash=60.66,
        non_degradable_volatile_solids=70.77,
        degradable_volatile_solids=80.88,
        total_solids=290.01,
        volume=100.12,
        pen_manure_data=None
    )


@pytest.fixture
def received_manure() -> ManureStream:
    """Returns a fixture ManureStream instance representing received manure."""
    return ManureStream(
        water=1.23,
        ammoniacal_nitrogen=2.34,
        nitrogen=3.45,
        phosphorus=4.56,
        potassium=5.67,
        ash=6.78,
        non_degradable_volatile_solids=7.89,
        degradable_volatile_solids=8.90,
        total_solids=29.01,
        volume=10.12,
        pen_manure_data=None
    )


@pytest.fixture
def slurry_storage_underfloor() -> SlurryStorageUnderfloor:
    """Returns a fixture SlurryStorageUnderfloor instance representing the underfloor slurry storage."""
    return SlurryStorageUnderfloor(
        name="dummy_name",
        is_housing_emissions_calculator=False,
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6,
        nitrous_oxide_emissions_factor=0.01,
        capacity=123456.789
    )


def test_slurry_storage_outdoor_init(mocker: MockerFixture) -> None:
    """Tests the initialization of SlurryStorageUnderfloor by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    SlurryStorageUnderfloor(
        name=(dummy_name := "dummy_name"),
        is_housing_emissions_calculator=(dummy_is_housing_emissions_calculator := False),
        cover=(dummy_cover := StorageCover.NO_COVER),
        storage_time_period=(dummy_storage_time_period := 18),
        surface_area=(dummy_surface_area := 6.6),
        nitrous_oxide_emissions_factor=(dummy_nitrous_oxide_emissions_factor := 0.01),
        capacity=(dummy_capacity := 123456.789)
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=dummy_is_housing_emissions_calculator,
        cover=dummy_cover,
        storage_time_period=dummy_storage_time_period,
        surface_area=dummy_surface_area,
        nitrous_oxide_emissions_factor=dummy_nitrous_oxide_emissions_factor,
        capacity=dummy_capacity
    )


def test_process_manure_not_emptying_day(
    mocker: MockerFixture,
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    """Tests manure processing on a non-emptying day in the underfloor slurry storage."""
    slurry_storage_underfloor._stored_manure = stored_manure
    slurry_storage_underfloor._received_manure = received_manure
    expected_total_manure = stored_manure + received_manure

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_underfloor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_underfloor._stored_manure = expected_total_manure
        return {}
    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_underfloor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    dummy_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                   + dummy_non_degradable_volatile_solids_storage_methane)
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (expected_total_manure.degradable_volatile_solids
         - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (expected_total_manure.non_degradable_volatile_solids
         - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_underfloor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_underfloor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_underfloor, "_report_storage_outputs", return_value=None)

    result = slurry_storage_underfloor.process_manure(
        (dummy_current_day_conditions := MagicMock(auto_spec=CurrentDayConditions)),
        (dummy_time := MagicMock(auto_spec=Time))
    )

    mock_base_process_manure.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_determine_outdoor_storage_temperature.assert_called_once_with(
        air_temperature=dummy_current_day_conditions.mean_air_temperature)
    assert mock_calculate_methane_emissions.call_args_list == [
        call(
            volatile_solids=expected_total_manure.degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=True
        ),
        call(
            volatile_solids=expected_total_manure.non_degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=False
        ),
    ]
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_underfloor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_underfloor._cover],
        nitrogen_added=received_manure.nitrogen,
    )
    expected_stored_manure = ManureStream(
        water=expected_total_manure.water,
        ammoniacal_nitrogen=expected_ammoniacal_nitrogen,
        nitrogen=expected_nitrogen,
        phosphorus=expected_total_manure.phosphorus,
        potassium=expected_total_manure.potassium,
        ash=expected_total_manure.ash,
        non_degradable_volatile_solids=expected_non_degradable_volatile_solids,
        degradable_volatile_solids=expected_degradable_volatile_solids,
        total_solids=expected_total_solids,
        volume=expected_total_manure.volume,
        pen_manure_data=None
    )
    expected_received_manure = received_manure
    assert mock_report_manure_stream.call_args_list == [
        call(
            expected_stored_manure,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            "received",
            dummy_time
        ),
    ]
    mock_report_storage_outputs.assert_called_once_with(
        dummy_total_storage_methane,
        dummy_storage_ammonia,
        dummy_storage_nitrous_oxide,
        dummy_time
    )
    assert slurry_storage_underfloor._stored_manure == expected_stored_manure
    assert slurry_storage_underfloor._received_manure == ManureStream.make_empty_manure_stream()
    assert result == {}


def test_process_manure_emptying_day(
    mocker: MockerFixture,
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    """Tests manure processing on an emptying day in the underfloor slurry storage."""
    slurry_storage_underfloor._stored_manure = stored_manure
    slurry_storage_underfloor._received_manure = received_manure
    expected_total_manure = stored_manure + received_manure

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_underfloor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_underfloor._stored_manure = ManureStream.make_empty_manure_stream()
        return {"manure": copy(expected_total_manure)}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_underfloor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    dummy_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                   + dummy_non_degradable_volatile_solids_storage_methane)
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (expected_total_manure.degradable_volatile_solids
         - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (expected_total_manure.non_degradable_volatile_solids
         - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_underfloor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_underfloor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_underfloor, "_report_storage_outputs", return_value=None)

    result = slurry_storage_underfloor.process_manure(
        (dummy_current_day_conditions := MagicMock(auto_spec=CurrentDayConditions)),
        (dummy_time := MagicMock(auto_spec=Time))
    )

    mock_base_process_manure.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_determine_outdoor_storage_temperature.assert_called_once_with(
        air_temperature=dummy_current_day_conditions.mean_air_temperature)
    assert mock_calculate_methane_emissions.call_args_list == [
        call(
            volatile_solids=expected_total_manure.degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=True
        ),
        call(
            volatile_solids=expected_total_manure.non_degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=False
        ),
    ]
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_underfloor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_underfloor._cover],
        nitrogen_added=received_manure.nitrogen,
    )
    expected_stored_manure = ManureStream(
        water=expected_total_manure.water,
        ammoniacal_nitrogen=expected_ammoniacal_nitrogen,
        nitrogen=expected_nitrogen,
        phosphorus=expected_total_manure.phosphorus,
        potassium=expected_total_manure.potassium,
        ash=expected_total_manure.ash,
        non_degradable_volatile_solids=expected_non_degradable_volatile_solids,
        degradable_volatile_solids=expected_degradable_volatile_solids,
        total_solids=expected_total_solids,
        volume=expected_total_manure.volume,
        pen_manure_data=None
    )
    expected_received_manure = received_manure
    assert mock_report_manure_stream.call_args_list == [
        call(
            expected_stored_manure,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            "received",
            dummy_time
        ),
    ]
    mock_report_storage_outputs.assert_called_once_with(
        dummy_total_storage_methane,
        dummy_storage_ammonia,
        dummy_storage_nitrous_oxide,
        dummy_time
    )
    assert slurry_storage_underfloor._stored_manure == ManureStream.make_empty_manure_stream()
    assert slurry_storage_underfloor._received_manure == ManureStream.make_empty_manure_stream()
    assert result["manure"] == expected_stored_manure
