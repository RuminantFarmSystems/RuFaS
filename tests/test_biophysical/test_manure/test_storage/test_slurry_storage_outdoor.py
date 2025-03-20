from copy import copy
from dataclasses import replace
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor, \
    METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO, SLURRY_MANURE_DENSITY, STORAGE_HSC
from RUFAS.biophysical.manure.storage.storage import DEFAULT_PH_FOR_AMMONIA, \
    STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


@pytest.fixture
def stored_manure() -> ManureStream:
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
def slurry_storage_outdoor() -> SlurryStorageOutdoor:
    return SlurryStorageOutdoor(
        name="dummy_name",
        is_housing_emissions_calculator=False,
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6,
        nitrous_oxide_emissions_factor=0.01,
        capacity=123456.789
    )


def test_slurry_storage_outdoor_init(mocker: MockerFixture) -> None:
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    SlurryStorageOutdoor(
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


def test_process_manure_not_emptying_day_with_cover(
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    slurry_storage_outdoor._cover = StorageCover.COVER
    slurry_storage_outdoor._stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    expected_total_manure = stored_manure + received_manure
    def process_manure_side_effect(_: CurrentDayConditions, __:Time) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor._stored_manure = expected_total_manure
        return {}
    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_outdoor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    dummy_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                   + dummy_non_degradable_volatile_solids_storage_methane)
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=(0.12, 0.0)
    )
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.degradable_volatile_solids
                - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.non_degradable_volatile_solids
                - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_outdoor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_storage_outputs", return_value=None)
    mock_report_slurry_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_slurry_storage_outputs", return_value=None)

    result = slurry_storage_outdoor.process_manure(
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
    mock_calculate_cover_and_flare_methane.assert_not_called()
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_outdoor._cover],
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
            slurry_storage_outdoor._accumulated_output_prefix,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            slurry_storage_outdoor._prefix,
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
    mock_report_slurry_storage_outputs.assert_called_once_with(0.0, dummy_time)
    assert slurry_storage_outdoor._stored_manure == expected_stored_manure
    assert slurry_storage_outdoor._received_manure == ManureStream.make_empty_manure_stream()
    assert result == {}


def test_process_manure_emptying_day_with_cover(
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    slurry_storage_outdoor._cover = StorageCover.COVER
    slurry_storage_outdoor._stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    expected_total_manure = stored_manure + received_manure

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor._stored_manure = ManureStream.make_empty_manure_stream()
        return {"manure": copy(expected_total_manure)}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_outdoor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    dummy_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                   + dummy_non_degradable_volatile_solids_storage_methane)
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=(0.12, 0.0)
    )
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.degradable_volatile_solids
                - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.non_degradable_volatile_solids
                - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_outdoor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_storage_outputs", return_value=None)
    mock_report_slurry_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_slurry_storage_outputs", return_value=None)

    result = slurry_storage_outdoor.process_manure(
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
    mock_calculate_cover_and_flare_methane.assert_not_called()
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_outdoor._cover],
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
            slurry_storage_outdoor._accumulated_output_prefix,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            slurry_storage_outdoor._prefix,
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
    mock_report_slurry_storage_outputs.assert_called_once_with(0.0, dummy_time)
    assert slurry_storage_outdoor._stored_manure == ManureStream.make_empty_manure_stream()
    assert slurry_storage_outdoor._received_manure == ManureStream.make_empty_manure_stream()
    assert result["manure"] == expected_stored_manure


@pytest.mark.parametrize(
    "cover", [StorageCover.NO_COVER, StorageCover.CRUST]
)
def test_process_manure_not_emptying_day_with_no_cover_or_crust_cover(
    cover: StorageCover,
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    slurry_storage_outdoor._cover = cover
    slurry_storage_outdoor._stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    total_manure = stored_manure + received_manure

    dummy_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    dummy_current_day_conditions.precipitation = 12345.789
    precipitation_volume = (dummy_current_day_conditions.precipitation * GeneralConstants.MM_TO_M
                            * slurry_storage_outdoor._surface_area)
    precipitation_mass = precipitation_volume * GeneralConstants.WATER_DENSITY_KG_PER_M3
    expected_total_manure = replace(
        total_manure,
        volume=(total_manure.volume + precipitation_volume),
        water=(total_manure.water + precipitation_mass)
    )

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor._stored_manure = copy(expected_total_manure)
        return {}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_outdoor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    dummy_total_storage_methane = (dummy_degradable_volatile_solids_storage_methane
                                   + dummy_non_degradable_volatile_solids_storage_methane)
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=(0.12, 0.0)
    )
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.degradable_volatile_solids
                - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.non_degradable_volatile_solids
                - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_outdoor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_storage_outputs", return_value=None)
    mock_report_slurry_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_slurry_storage_outputs", return_value=None)

    slurry_storage_outdoor.process_manure(
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
    mock_calculate_cover_and_flare_methane.assert_not_called()
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_outdoor._cover],
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
            slurry_storage_outdoor._accumulated_output_prefix,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            slurry_storage_outdoor._prefix,
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
    mock_report_slurry_storage_outputs.assert_called_once_with(0.0, dummy_time)


def test_process_manure_not_emptying_day_with_cover_and_flare(
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream
) -> None:
    slurry_storage_outdoor._cover = StorageCover.COVER_AND_FLARE
    slurry_storage_outdoor._stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    expected_total_manure = stored_manure + received_manure

    def process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor._stored_manure = copy(expected_total_manure)
        return {}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect)
    mock_determine_outdoor_storage_temperature = mocker.patch.object(
        slurry_storage_outdoor,
        "_determine_outdoor_storage_temperature",
        return_value=(dummy_manure_temperature := 25.0)
    )
    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ]
    )
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=(dummy_methane_burned := 0.33, dummy_total_storage_methane := 3.88)
    )
    expected_total_solids = max(
        0.0, expected_total_manure.total_solids - dummy_total_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO)
    expected_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.degradable_volatile_solids
                - dummy_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    expected_non_degradable_volatile_solids = max(
        0.0,
        (
                expected_total_manure.non_degradable_volatile_solids
                - dummy_non_degradable_volatile_solids_storage_methane * METHANE_TO_METHANE_CARBON_DIOXIDE_RATIO
        )
    )
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=(dummy_storage_ammonia := 1.23))
    expected_ammoniacal_nitrogen = max(0.0, expected_total_manure.ammoniacal_nitrogen - dummy_storage_ammonia)
    expected_nitrogen = max(0.0, expected_total_manure.nitrogen - dummy_storage_ammonia)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide := 0.12)
    )
    expected_nitrogen = max(0.0, expected_nitrogen - dummy_storage_nitrous_oxide)

    mock_report_manure_stream = mocker.patch.object(
        slurry_storage_outdoor, "_report_manure_stream", return_value=None)
    mock_report_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_storage_outputs", return_value=None)
    mock_report_slurry_storage_outputs = mocker.patch.object(
        slurry_storage_outdoor, "_report_slurry_storage_outputs", return_value=None)

    slurry_storage_outdoor.process_manure(
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
    mock_calculate_cover_and_flare_methane.assert_called_once_with(
        dummy_degradable_volatile_solids_storage_methane + dummy_non_degradable_volatile_solids_storage_methane)
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=expected_total_manure.ammoniacal_nitrogen,
        volume=expected_total_manure.volume,
        density=SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=STORAGE_HSC,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=DEFAULT_PH_FOR_AMMONIA,
    )
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[
            slurry_storage_outdoor._cover],
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
            slurry_storage_outdoor._accumulated_output_prefix,
            "accumulated",
            dummy_time
        ),
        call(
            expected_received_manure,
            slurry_storage_outdoor._prefix,
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
    mock_report_slurry_storage_outputs.assert_called_once_with(dummy_methane_burned, dummy_time)


def test_report_slurry_storage_outputs(slurry_storage_outdoor: SlurryStorageOutdoor, mocker: MockerFixture) -> None:
    dummy_time = MagicMock(auto_spec=Time)
    mock_om_add_variable = mocker.patch("RUFAS.output_manager.OutputManager.add_variable")
    info_map = {
        "class": slurry_storage_outdoor.__class__.__name__,
        "function": slurry_storage_outdoor._report_storage_outputs.__name__,
        "prefix": slurry_storage_outdoor._prefix,
        "simulation_day": dummy_time.simulation_day,
        "units": MeasurementUnits.KILOGRAMS,
    }

    slurry_storage_outdoor._report_slurry_storage_outputs((dummy_storage_methane_burned := 2.56), dummy_time)

    mock_om_add_variable.assert_called_once_with("storage_methane_burned", dummy_storage_methane_burned, info_map)
