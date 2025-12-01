from copy import copy
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.slurry_storage_underfloor import SlurryStorageUnderfloor
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
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
def slurry_storage_underfloor() -> SlurryStorageUnderfloor:
    """Returns a fixture SlurryStorageUnderfloor instance representing the underfloor slurry storage."""
    return SlurryStorageUnderfloor(
        name="dummy_name",
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6,
        capacity=123456.789,
    )


def test_slurry_storage_outdoor_init(mocker: MockerFixture) -> None:
    """Tests the initialization of SlurryStorageUnderfloor by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    SlurryStorageUnderfloor(
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


@pytest.mark.parametrize("is_emptying_day", [True, False])
def test_process_manure(
    is_emptying_day: bool,
    mocker: MockerFixture,
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
    received_manure: ManureStream,
) -> None:
    """Tests manure processing in the underfloor slurry storage."""
    slurry_storage_underfloor.stored_manure = stored_manure
    slurry_storage_underfloor._received_manure = received_manure
    expected_total_manure = stored_manure + received_manure

    def process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        slurry_storage_underfloor._received_manure = ManureStream.make_empty_manure_stream()
        slurry_storage_underfloor.stored_manure = (
            ManureStream.make_empty_manure_stream() if is_emptying_day else expected_total_manure
        )
        return {"manure": copy(expected_total_manure)} if is_emptying_day else {}

    mock_base_process_manure = mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure", side_effect=process_manure_side_effect
    )
    mock_determine_barn_temperature = mocker.patch.object(
        slurry_storage_underfloor,
        "_determine_barn_temperature",
        return_value=(dummy_manure_temperature := 25.0),
    )
    mock_apply_methane_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_apply_methane_emissions",
        return_value=(dummy_total_storage_methane := 10.88),
    )
    mock_apply_ammonia_emissions = mocker.patch.object(
        slurry_storage_underfloor, "_apply_ammonia_emissions", return_value=(dummy_storage_ammonia_nitrogen := 1.23)
    )
    mock_apply_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_apply_nitrous_oxide_emissions",
        return_value=(dummy_storage_nitrous_oxide_nitrogen := 4.56),
    )
    expected_data_origin_name = slurry_storage_underfloor.process_manure.__name__
    expected_units = MeasurementUnits.KILOGRAMS

    mock_report_manure_stream = mocker.patch.object(slurry_storage_underfloor, "_report_manure_stream")
    mock_report_processor_output = mocker.patch.object(slurry_storage_underfloor, "_report_processor_output")

    result = slurry_storage_underfloor.process_manure(
        (dummy_current_day_conditions := MagicMock(auto_spec=CurrentDayConditions)),
        (dummy_time := MagicMock(auto_spec=RufasTime)),
    )

    mock_base_process_manure.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_determine_barn_temperature.assert_called_once_with(
        air_temperature=dummy_current_day_conditions.mean_air_temperature
    )
    mock_apply_methane_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_ammonia_emissions.assert_called_once_with(dummy_manure_temperature)
    mock_apply_nitrous_oxide_emissions.assert_called_once_with(received_manure.nitrogen)
    assert mock_report_manure_stream.call_count == 2
    assert mock_report_processor_output.call_args_list == [
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
    ]
    assert slurry_storage_underfloor._received_manure == ManureStream.make_empty_manure_stream()
    if is_emptying_day:
        assert slurry_storage_underfloor.stored_manure == ManureStream.make_empty_manure_stream()
        assert result == {"manure": expected_total_manure}
    else:
        assert slurry_storage_underfloor.stored_manure == expected_total_manure
        assert result == {}


@pytest.mark.parametrize(
    "expected_stored_manure",
    [
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
        )
    ],
)
def test_apply_methane_emissions(
    expected_stored_manure: ManureStream,
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Tests the application of methane emissions to the stored manure."""
    slurry_storage_underfloor._manure_to_process = copy(stored_manure)

    mock_calculate_methane_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_methane_emissions",
        side_effect=[2.33, 1.88],
    )

    slurry_storage_underfloor._apply_methane_emissions(dummy_manure_temperature := 25.0)

    assert pytest.approx(slurry_storage_underfloor._manure_to_process) == expected_stored_manure
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
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
) -> None:
    """Tests that ammonia emissions calculation works correctly."""
    slurry_storage_underfloor._manure_to_process = copy(stored_manure)
    mock_calculate_ammonia_emissions = mocker.patch.object(
        slurry_storage_underfloor, "_calculate_ammonia_emissions", return_value=1.23
    )

    slurry_storage_underfloor._apply_ammonia_emissions((dummy_manure_temperature := 25.0))

    assert slurry_storage_underfloor._manure_to_process == expected_stored_manure
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=stored_manure.ammoniacal_nitrogen,
        mass=stored_manure.volume * ManureConstants.SLURRY_MANURE_DENSITY,
        density=ManureConstants.SLURRY_MANURE_DENSITY,
        temperature=dummy_manure_temperature,
        ammonia_resistance=ManureConstants.STORAGE_RESISTANCE,
        surface_area=slurry_storage_underfloor._surface_area,
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
    slurry_storage_underfloor: SlurryStorageUnderfloor,
    stored_manure: ManureStream,
    received_manure: ManureStream,
) -> None:
    """Tests that nitrous oxide emissions calculation works correctly."""
    slurry_storage_underfloor._manure_to_process = copy(stored_manure)
    slurry_storage_underfloor._cover = cover_type
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        slurry_storage_underfloor,
        "_calculate_nitrous_oxide_emissions",
        return_value=0.12,
    )

    slurry_storage_underfloor._apply_nitrous_oxide_emissions(received_manure.nitrogen)

    assert slurry_storage_underfloor._manure_to_process == expected_stored_manure
    mock_calculate_nitrous_oxide_emissions.assert_called_once_with(
        nitrous_oxide_emissions_factor=ManureConstants.STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING[cover_type],
        nitrogen_added=received_manure.nitrogen,
    )
