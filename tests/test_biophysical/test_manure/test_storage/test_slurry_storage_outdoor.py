from copy import copy
from dataclasses import replace
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import (
    SlurryStorageOutdoor,
    METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO,
    SLURRY_MANURE_DENSITY,
    STORAGE_HSC,
)
from RUFAS.biophysical.manure.storage.storage import (
    DEFAULT_PH_FOR_AMMONIA,
    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING,
)
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


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
        pen_manure_data=None,
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
        pen_manure_data=None,
    )


@pytest.fixture
def slurry_storage_outdoor() -> SlurryStorageOutdoor:
    """Returns a fixture SlurryStorageOutdoor instance representing the outdoor slurry storage."""
    return SlurryStorageOutdoor(
        name="dummy_name",
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6,
        nitrous_oxide_emissions_factor=0.01,
        capacity=123456.789,
    )


def test_slurry_storage_outdoor_init(mocker: MockerFixture) -> None:
    """Tests the initialization of SlurryStorageOutdoor by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    SlurryStorageOutdoor(
        name=(dummy_name := "dummy_name"),
        cover=(dummy_cover := StorageCover.NO_COVER),
        storage_time_period=(dummy_storage_time_period := 18),
        surface_area=(dummy_surface_area := 6.6),
        nitrous_oxide_emissions_factor=(dummy_nitrous_oxide_emissions_factor := 0.01),
        capacity=(dummy_capacity := 123456.789),
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover=dummy_cover,
        storage_time_period=dummy_storage_time_period,
        surface_area=dummy_surface_area,
        nitrous_oxide_emissions_factor=dummy_nitrous_oxide_emissions_factor,
        capacity=dummy_capacity,
    )


@pytest.mark.parametrize("is_emptying_day, cover_type", [
    (True, StorageCover.NO_COVER),
    (False, StorageCover.NO_COVER),
    (True, StorageCover.COVER),
    (False, StorageCover.COVER),
    (True, StorageCover.CRUST),
    (False, StorageCover.CRUST),
    (True, StorageCover.COVER_AND_FLARE),
    (False, StorageCover.COVER_AND_FLARE),
])
def test_process_manure(
    is_emptying_day: bool,
    cover_type: StorageCover,
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream,
) -> None:
    """Tests manure processing on a non-emptying day with a cover on the slurry storage."""
    slurry_storage_outdoor._cover = cover_type
    slurry_storage_outdoor._stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    expected_total_manure = stored_manure + received_manure

    dummy_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    dummy_current_day_conditions.precipitation = 12345.789
    if cover_type in [StorageCover.NO_COVER, StorageCover.CRUST]:
        precipitation_volume = (dummy_current_day_conditions.precipitation * GeneralConstants.MM_TO_M
                                * slurry_storage_outdoor._surface_area)
        precipitation_mass = precipitation_volume * GeneralConstants.WATER_DENSITY_KG_PER_M3
        expected_total_manure = replace(
            expected_total_manure,
            volume=(expected_total_manure.volume + precipitation_volume),
            water=(expected_total_manure.water + precipitation_mass),
        )

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor._stored_manure = ManureStream.make_empty_manure_stream() \
            if is_emptying_day else expected_total_manure
        return {"manure": copy(expected_total_manure)} if is_emptying_day else {}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect
    )
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_outdoor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0),
    )
    mock_apply_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_apply_methane_emissions",
        return_value=(
            (dummy_storage_methane_burned := 2.33),
            (dummy_total_storage_methane := 10.88),
        ),
    )
    mock_apply_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_apply_ammonia_emissions", return_value=(dummy_storage_ammonia_nitrogen := 1.23))
    mock_apply_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_apply_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide_nitrogen := 4.56)
    )
    mock_report_slurry_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_slurry_storage_outdoor_outputs", return_value=None)

    result = slurry_storage_outdoor.process_manure(
        dummy_current_day_conditions,
        (dummy_time := MagicMock(auto_spec=Time)),
    )

    mock_base_process_manure.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_determine_outdoor_storage_temperature.assert_called_once_with(
        air_temperature=dummy_current_day_conditions.mean_air_temperature
    )
    mock_apply_methane_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_ammonia_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_nitrous_oxide_emissions.assert_called_once_with(received_manure)
    mock_report_slurry_storage_outputs.assert_called_once_with(
        dummy_total_storage_methane,
        dummy_storage_ammonia_nitrogen,
        dummy_storage_nitrous_oxide_nitrogen,
        dummy_storage_methane_burned,
        dummy_time.simulation_day
    )
    assert slurry_storage_outdoor._received_manure == ManureStream.make_empty_manure_stream()
    if is_emptying_day:
        assert slurry_storage_outdoor._stored_manure == ManureStream.make_empty_manure_stream()
        assert result == {"manure": expected_total_manure}
    else:
        assert slurry_storage_outdoor._stored_manure == expected_total_manure
        assert result == {}


@pytest.mark.parametrize("cover_type", [
    StorageCover.NO_COVER, StorageCover.CRUST, StorageCover.COVER, StorageCover.COVER_AND_FLARE
])
def test_apply_methane_emissions(
        cover_type: StorageCover,
        slurry_storage_outdoor: SlurryStorageOutdoor,
        stored_manure: ManureStream,
        mocker: MockerFixture,
) -> None:
    """Tests the application of methane emissions to the stored manure."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    slurry_storage_outdoor._cover = cover_type

    expected_stored_manure = copy(stored_manure)

    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ],
    )
    temporary_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                       + dummy_non_degradable_volatile_solids_storage_methane)
    dummy_total_storage_methane = temporary_total_storage_methane - 0.12 if cover_type == StorageCover.COVER_AND_FLARE \
        else temporary_total_storage_methane
    mock_calculate_cover_and_flare_methane_return_value = (0.12, dummy_total_storage_methane) \
        if cover_type == StorageCover.COVER_AND_FLARE else (0.0, dummy_total_storage_methane)
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=mock_calculate_cover_and_flare_methane_return_value
    )
    expected_stored_manure.total_solids = max(
        0.0, expected_stored_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
    )
    expected_stored_manure.degradable_volatile_solids = max(
        0.0,
        (expected_stored_manure.degradable_volatile_solids - dummy_degradable_volatile_solids_storage_methane
         * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
    )
    expected_stored_manure.non_degradable_volatile_solids = max(
        0.0,
        (expected_stored_manure.non_degradable_volatile_solids - dummy_non_degradable_volatile_solids_storage_methane
         * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO),
    )

    slurry_storage_outdoor._apply_methane_emissions(dummy_manure_temperature := 25.0)

    assert slurry_storage_outdoor._manure_to_process == expected_stored_manure
    assert mock_calculate_methane_emissions.call_args_list == [
        call(
            volatile_solids=stored_manure.degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=True,
        ),
        call(
            volatile_solids=stored_manure.non_degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=False,
        )
    ]
    if cover_type == StorageCover.COVER_AND_FLARE:
        mock_calculate_cover_and_flare_methane.assert_called_once_with(temporary_total_storage_methane)
    else:
        mock_calculate_cover_and_flare_methane.assert_not_called()


def test_apply_ammonia_emissions(
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
) -> None:
    """Tests that ammonia emissions calculation works correctly."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    expected_stored_manure = copy(stored_manure)
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23)
    )
    expected_stored_manure.ammoniacal_nitrogen = max(
        0.0, expected_stored_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_stored_manure.nitrogen = max(0.0, expected_stored_manure.nitrogen - dummy_storage_ammonia)

    slurry_storage_outdoor._apply_ammonia_emissions((dummy_manure_temperature := 25.0))

    assert slurry_storage_outdoor._manure_to_process == expected_stored_manure
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=stored_manure.ammoniacal_nitrogen,
        volume=stored_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )


@pytest.mark.parametrize("cover_type", [
    StorageCover.NO_COVER, StorageCover.CRUST, StorageCover.COVER, StorageCover.COVER_AND_FLARE
])
def test_apply_nitrous_oxide_emissions(
    cover_type: StorageCover,
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream,
) -> None:
    """Tests that nitrous oxide emissions calculation works correctly."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    slurry_storage_outdoor._cover = cover_type
    expected_stored_manure = copy(stored_manure)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_nitrous_oxide_emissions", return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_stored_manure.nitrogen = max(0.0, expected_stored_manure.nitrogen - dummy_storage_nitrous_oxide)

    slurry_storage_outdoor._apply_nitrous_oxide_emissions(received_manure)

    assert slurry_storage_outdoor._manure_to_process == expected_stored_manure
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[cover_type],
        nitrogen_added=received_manure.nitrogen,
    )


def test_report_slurry_storage_outputs(slurry_storage_outdoor: SlurryStorageOutdoor, mocker: MockerFixture) -> None:
    """Tests the reporting of slurry storage outputs of methane burned during the process."""
    data_origin_name = slurry_storage_outdoor._report_slurry_storage_outdoor_outputs.__name__
    units = MeasurementUnits.KILOGRAMS

    mock_report_processor_output = mocker.patch.object(slurry_storage_outdoor, "_report_processor_output")

    slurry_storage_outdoor._report_slurry_storage_outdoor_outputs(
        (dummy_storage_methane := 1.23),
        (dummy_storage_ammonia_nitrogen := 4.56),
        (dummy_storage_nitrous_oxide_nitrogen := 7.89),
        (dummy_storage_methane_burned := 10.11),
        dummy_simulation_day := 12345,
    )

    assert mock_report_processor_output.call_args_list == [
        call("storage_methane", dummy_storage_methane, data_origin_name, units, dummy_simulation_day),
        call("storage_ammonia_N", dummy_storage_ammonia_nitrogen, data_origin_name, units, dummy_simulation_day),
        call(
            "storage_nitrous_oxide_N",
            dummy_storage_nitrous_oxide_nitrogen,
            data_origin_name,
            units,
            dummy_simulation_day
        ),
        call("storage_methane_burned", dummy_storage_methane_burned, data_origin_name, units, dummy_simulation_day),
    ]
