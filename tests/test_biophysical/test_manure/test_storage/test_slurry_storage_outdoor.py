from copy import copy
from dataclasses import replace
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.slurry_storage_outdoor import SlurryStorageOutdoor
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


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
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
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
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
    )


@pytest.fixture
def slurry_storage_outdoor() -> SlurryStorageOutdoor:
    """Returns a fixture SlurryStorageOutdoor instance representing the outdoor slurry storage."""
    return SlurryStorageOutdoor(
        name="dummy_name",
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6,
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
        capacity=(dummy_capacity := 123456.789),
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover=dummy_cover,
        storage_time_period=dummy_storage_time_period,
        surface_area=dummy_surface_area,
        capacity=dummy_capacity,
    )


@pytest.mark.parametrize(
    "is_emptying_day, cover_type",
    [
        (True, StorageCover.NO_COVER),
        (False, StorageCover.NO_COVER),
        (True, StorageCover.COVER),
        (False, StorageCover.COVER),
        (True, StorageCover.CRUST),
        (False, StorageCover.CRUST),
        (True, StorageCover.COVER_AND_FLARE),
        (False, StorageCover.COVER_AND_FLARE),
    ],
)
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
    slurry_storage_outdoor.stored_manure, slurry_storage_outdoor._received_manure = stored_manure, received_manure
    expected_total_manure = stored_manure + received_manure

    dummy_current_day_conditions = MagicMock(auto_spec=CurrentDayConditions)
    dummy_current_day_conditions.precipitation = 12345.789
    if cover_type in [StorageCover.NO_COVER, StorageCover.CRUST]:
        precipitation_volume = (
            dummy_current_day_conditions.precipitation * GeneralConstants.MM_TO_M * slurry_storage_outdoor._surface_area
        )
        precipitation_mass = precipitation_volume * UserConstants.WATER_DENSITY_KG_PER_M3
        expected_total_manure = replace(
            expected_total_manure,
            volume=(expected_total_manure.volume + precipitation_volume),
            water=(expected_total_manure.water + precipitation_mass),
        )

    def process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        slurry_storage_outdoor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_outdoor.stored_manure = (
            ManureStream.make_empty_manure_stream() if is_emptying_day else expected_total_manure
        )
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
        slurry_storage_outdoor, "_apply_ammonia_emissions", return_value=(dummy_storage_ammonia_nitrogen := 1.23)
    )
    mock_apply_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_apply_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide_nitrogen := 4.56),
    )

    mock_report_manure_stream = mocker.patch.object(slurry_storage_outdoor, "_report_manure_stream")
    mock_report_processor_output = mocker.patch.object(slurry_storage_outdoor, "_report_processor_output")
    expected_data_origin_name = slurry_storage_outdoor.process_manure.__name__
    expected_units = MeasurementUnits.KILOGRAMS

    result = slurry_storage_outdoor.process_manure(
        dummy_current_day_conditions,
        (dummy_time := MagicMock(auto_spec=RufasTime)),
    )

    mock_base_process_manure.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_determine_outdoor_storage_temperature.assert_called_once_with(
        dummy_time.current_julian_day, ManureConstants.SLURRY_OUTDOOR_MINIMUM_TEMPERATURE
    )
    mock_apply_methane_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_ammonia_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_nitrous_oxide_emissions.assert_called_once_with(received_manure.nitrogen)
    assert mock_report_manure_stream.call_count == 2
    assert mock_report_processor_output.call_args_list == [
        call(
            "outdoor_storage_manure_temperature",
            dummy_manure_temperature,
            expected_data_origin_name,
            MeasurementUnits.DEGREES_CELSIUS,
            dummy_time.simulation_day,
        ),
        call(
            "storage_methane",
            dummy_total_storage_methane,
            expected_data_origin_name,
            expected_units,
            dummy_time.simulation_day,
        ),
        call(
            "storage_ammonia_N",
            dummy_storage_ammonia_nitrogen,
            expected_data_origin_name,
            expected_units,
            dummy_time.simulation_day,
        ),
        call(
            "storage_nitrous_oxide_N",
            dummy_storage_nitrous_oxide_nitrogen,
            expected_data_origin_name,
            expected_units,
            dummy_time.simulation_day,
        ),
        call(
            "storage_methane_burned",
            dummy_storage_methane_burned,
            expected_data_origin_name,
            expected_units,
            dummy_time.simulation_day,
        ),
    ]
    assert slurry_storage_outdoor._received_manure == ManureStream.make_empty_manure_stream()
    if is_emptying_day:
        assert slurry_storage_outdoor.stored_manure == ManureStream.make_empty_manure_stream()
        assert result == {"manure": expected_total_manure}
    else:
        assert slurry_storage_outdoor.stored_manure == expected_total_manure
        assert result == {}


@pytest.mark.parametrize(
    "cover_type, expected_stored_manure",
    [
        (
            StorageCover.NO_COVER,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.33,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=59.7911433205398,
                degradable_volatile_solids=65.35055,
                total_solids=261.95035,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=8.448656679460196,
            ),
        ),
        (
            StorageCover.CRUST,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.33,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=59.7911433205398,
                degradable_volatile_solids=65.35055,
                total_solids=261.95035,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=8.448656679460196,
            ),
        ),
        (
            StorageCover.COVER,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.33,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=59.7911433205398,
                degradable_volatile_solids=65.35055,
                total_solids=261.95035,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=8.448656679460196,
            ),
        ),
        (
            StorageCover.COVER_AND_FLARE,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.33,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=59.7911433205398,
                degradable_volatile_solids=65.35055,
                total_solids=262.75014999999996,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=8.448656679460196,
            ),
        ),
    ],
)
def test_apply_methane_emissions(
    cover_type: StorageCover,
    expected_stored_manure: ManureStream,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Tests the application of methane emissions to the stored manure."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    slurry_storage_outdoor._cover = cover_type

    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_methane_emissions",
        side_effect=[
            (dummy_degradable_volatile_solids_storage_methane := 2.33),
            (dummy_non_degradable_volatile_solids_storage_methane := 1.88),
        ],
    )
    temporary_total_storage_methane = (
        dummy_degradable_volatile_solids_storage_methane + dummy_non_degradable_volatile_solids_storage_methane
    )
    dummy_total_storage_methane = (
        temporary_total_storage_methane - 0.12
        if cover_type == StorageCover.COVER_AND_FLARE
        else temporary_total_storage_methane
    )
    mock_calculate_cover_and_flare_methane_return_value = (
        (0.12, dummy_total_storage_methane)
        if cover_type == StorageCover.COVER_AND_FLARE
        else (0.0, dummy_total_storage_methane)
    )
    mock_calculate_cover_and_flare_methane = mocker.patch.object(
        slurry_storage_outdoor,
        "_calculate_cover_and_flare_methane",
        return_value=mock_calculate_cover_and_flare_methane_return_value,
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
            volatile_solids=stored_manure.non_degradable_volatile_solids
            + stored_manure.bedding_non_degradable_volatile_solids,
            manure_temperature=dummy_manure_temperature,
            is_degradable=False,
        ),
    ]
    if cover_type == StorageCover.COVER_AND_FLARE:
        mock_calculate_cover_and_flare_methane.assert_called_once_with(temporary_total_storage_methane)
    else:
        mock_calculate_cover_and_flare_methane.assert_not_called()


@pytest.mark.parametrize(
    "expected_stored_manure",
    [
        ManureStream(
            water=10.11,
            ammoniacal_nitrogen=18.99,
            nitrogen=29.099999999999998,
            phosphorus=40.44,
            potassium=50.55,
            ash=60.66,
            non_degradable_volatile_solids=70.77,
            degradable_volatile_solids=80.88,
            total_solids=290.01,
            volume=100.12,
            methane_production_potential=0.24,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=10,
        )
    ],
)
def test_apply_ammonia_emissions(
    expected_stored_manure: ManureStream,
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
) -> None:
    """Tests that ammonia emissions calculation works correctly."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_ammonia_emissions", return_value=1.23
    )

    slurry_storage_outdoor._apply_ammonia_emissions((dummy_manure_temperature := 25.0))

    assert slurry_storage_outdoor._manure_to_process == expected_stored_manure
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=stored_manure.ammoniacal_nitrogen,
        mass=stored_manure.volume * ManureConstants.SLURRY_MANURE_DENSITY,
        density=ManureConstants.SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=ManureConstants.STORAGE_RESISTANCE,
        surface_area=slurry_storage_outdoor._surface_area,
        pH=ManureConstants.DEFAULT_STORED_MANURE_PH,
    )


@pytest.mark.parametrize(
    "cover_type, expected_stored_manure",
    [
        (
            StorageCover.NO_COVER,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.209999999999997,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=70.77,
                degradable_volatile_solids=80.88,
                total_solids=290.01,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
        (
            StorageCover.CRUST,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.209999999999997,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=70.77,
                degradable_volatile_solids=80.88,
                total_solids=290.01,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
        (
            StorageCover.COVER,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.209999999999997,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=70.77,
                degradable_volatile_solids=80.88,
                total_solids=290.01,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
        (
            StorageCover.COVER_AND_FLARE,
            ManureStream(
                water=10.11,
                ammoniacal_nitrogen=20.22,
                nitrogen=30.209999999999997,
                phosphorus=40.44,
                potassium=50.55,
                ash=60.66,
                non_degradable_volatile_solids=70.77,
                degradable_volatile_solids=80.88,
                total_solids=290.01,
                volume=100.12,
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=10,
            ),
        ),
    ],
)
def test_apply_nitrous_oxide_emissions(
    cover_type: StorageCover,
    expected_stored_manure: ManureStream,
    mocker: MockerFixture,
    slurry_storage_outdoor: SlurryStorageOutdoor,
    stored_manure: ManureStream,
    received_manure: ManureStream,
) -> None:
    """Tests that nitrous oxide emissions calculation works correctly."""
    slurry_storage_outdoor._manure_to_process = copy(stored_manure)
    slurry_storage_outdoor._cover = cover_type
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_outdoor, "_calculate_nitrous_oxide_emissions", return_value=0.12
    )

    slurry_storage_outdoor._apply_nitrous_oxide_emissions(received_manure.nitrogen)

    assert slurry_storage_outdoor._manure_to_process == expected_stored_manure
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=ManureConstants.STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[cover_type],
        nitrogen_added=received_manure.nitrogen,
    )
