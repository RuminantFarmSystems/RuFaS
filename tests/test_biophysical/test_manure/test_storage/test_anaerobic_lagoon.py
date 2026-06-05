from copy import copy
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.anaerobic_lagoon import AnaerobicLagoon
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
def anaerobic_lagoon() -> AnaerobicLagoon:
    """Returns a fixture AnaerobicLagoon."""
    return AnaerobicLagoon(
        name="dummy_name",
        cover="no_crust_or_cover",
        storage_time_period=18,
        surface_area=6.6,
        capacity=123456.789,
    )


def test_anaerobic_lagoon_init(mocker: MockerFixture) -> None:
    """Tests the initialization of AnaerobicLagoon by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    AnaerobicLagoon(
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
    "cover, expect_precip_added, expect_flare",
    [
        (StorageCover.NO_COVER, True, False),
        (StorageCover.CRUST, True, False),
        (StorageCover.COVER, False, False),
        (StorageCover.COVER_AND_FLARE, False, True),
    ],
)
def test_process_manure_cover_behaviors(
    mocker: MockerFixture,
    anaerobic_lagoon: AnaerobicLagoon,
    stored_manure: ManureStream,
    received_manure: ManureStream,
    cover: StorageCover,
    expect_precip_added: bool,
    expect_flare: bool,
) -> None:
    """Tests anaerobic lagoon behavior under various cover types."""
    anaerobic_lagoon._cover = cover
    anaerobic_lagoon.stored_manure = stored_manure
    anaerobic_lagoon._received_manure = received_manure

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        anaerobic_lagoon.stored_manure += anaerobic_lagoon._received_manure
        anaerobic_lagoon._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    dummy_conditions = mocker.MagicMock(spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0)
    dummy_time = mocker.MagicMock(spec=RufasTime)
    dummy_time.simulation_day = 50

    mocker.patch.object(anaerobic_lagoon, "_determine_outdoor_storage_temperature", return_value=25.0)

    mock_apply_methane_emissions = mocker.patch.object(
        anaerobic_lagoon, "_apply_methane_emissions", return_value=(2.0, 0.12 if expect_flare else 0.0)
    )
    mock_apply_ammonia_emissions = mocker.patch.object(anaerobic_lagoon, "_apply_ammonia_emissions", return_value=1.0)
    mock_calculate_nitrous_oxide_emissions = mocker.patch.object(
        anaerobic_lagoon, "_calculate_nitrous_oxide_emissions", return_value=0.1
    )

    mock_report_manure_stream = mocker.patch.object(anaerobic_lagoon, "_report_manure_stream")
    mock_report_processor_output = mocker.patch.object(anaerobic_lagoon, "_report_processor_output")

    if cover in [StorageCover.NO_COVER, StorageCover.CRUST]:
        expected_precip_volume = (
            dummy_conditions.precipitation * GeneralConstants.MM_TO_M * anaerobic_lagoon._surface_area
        )
        received_manure.volume += expected_precip_volume
        received_manure.water += expected_precip_volume * UserConstants.WATER_DENSITY_KG_PER_M3

    result = anaerobic_lagoon.process_manure(dummy_conditions, dummy_time)

    mock_apply_methane_emissions.assert_called_once()
    mock_apply_ammonia_emissions.assert_called_once()
    mock_calculate_nitrous_oxide_emissions.assert_called_once()

    expected_received_manure = copy(received_manure)
    expected_received_manure.nitrogen = max(0.0, expected_received_manure.nitrogen - 0.1)

    mock_report_manure_stream.assert_has_calls(
        [
            call(anaerobic_lagoon.stored_manure, "accumulated", dummy_time.simulation_day),
            call(expected_received_manure, "received", dummy_time.simulation_day),
        ]
    )

    mock_report_processor_output.assert_has_calls(
        [
            call("storage_methane", 2.0, "process_manure", MeasurementUnits.KILOGRAMS, dummy_time.simulation_day),
            call(
                "outdoor_storage_manure_temperature",
                25.0,
                "process_manure",
                MeasurementUnits.DEGREES_CELSIUS,
                dummy_time.simulation_day,
            ),
            call(
                "storage_methane_burned",
                0.12 if expect_flare else 0.0,
                "process_manure",
                MeasurementUnits.KILOGRAMS,
                dummy_time.simulation_day,
            ),
            call("storage_ammonia_N", 1.0, "process_manure", MeasurementUnits.KILOGRAMS, dummy_time.simulation_day),
            call(
                "storage_nitrous_oxide_N", 0.1, "process_manure", MeasurementUnits.KILOGRAMS, dummy_time.simulation_day
            ),
        ]
    )

    if expect_precip_added:
        assert anaerobic_lagoon._received_manure.volume == 0.0
        assert anaerobic_lagoon.stored_manure.volume == pytest.approx(
            stored_manure.volume + received_manure.volume,
            rel=1e-6,
        )
        assert anaerobic_lagoon.stored_manure.water >= stored_manure.water + received_manure.water
    else:
        assert anaerobic_lagoon.stored_manure.volume >= stored_manure.volume + received_manure.volume
        assert anaerobic_lagoon.stored_manure.water >= stored_manure.water + received_manure.water

    assert result == {}
    assert anaerobic_lagoon._received_manure == ManureStream.make_empty_manure_stream()


@pytest.mark.parametrize(
    "cover, expected_total, expected_burned",
    [
        (StorageCover.COVER_AND_FLARE, 0.5699999999999998, 2.43),
        (StorageCover.NO_COVER, 3.0, 0.0),
    ],
)
def test_apply_methane_emissions_no_flare(
    mocker: MockerFixture,
    anaerobic_lagoon: AnaerobicLagoon,
    cover: StorageCover,
    expected_total: float,
    expected_burned: float,
) -> None:
    anaerobic_lagoon._cover = cover
    manure_temp = 25.0

    stored_manure = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=0.0,
        nitrogen=0.0,
        phosphorus=0.0,
        potassium=0.0,
        ash=0.0,
        non_degradable_volatile_solids=10.0,
        degradable_volatile_solids=20.0,
        total_solids=35.0,
        volume=0.0,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
    )
    anaerobic_lagoon._manure_to_process = stored_manure

    mocker.patch.object(anaerobic_lagoon, "_calculate_methane_emissions", side_effect=[2.0, 1.0])

    total, burned = anaerobic_lagoon._apply_methane_emissions(manure_temp)

    expected_total = expected_total
    expected_burned = expected_burned
    mass_loss = expected_total * ManureConstants.VS_TO_METHANE_LOSS_RATIO

    assert total == expected_total
    assert burned == expected_burned
    assert stored_manure.total_solids == pytest.approx(35.0 - mass_loss, rel=1e-6)
    assert stored_manure.degradable_volatile_solids == pytest.approx(
        20.0 - 2.0 * ManureConstants.VS_TO_METHANE_LOSS_RATIO, rel=1e-6
    )
    assert stored_manure.non_degradable_volatile_solids == 6.6675


def test_apply_ammonia_emissions(anaerobic_lagoon: AnaerobicLagoon, mocker: MockerFixture) -> None:
    """Tests the application of ammonia emissions in anaerobic lagoon."""
    manure_temp = 20.0
    surface_area = 15.0
    anaerobic_lagoon._surface_area = surface_area

    stored_manure = ManureStream(
        water=0.0,
        ammoniacal_nitrogen=10.0,
        nitrogen=12.0,
        phosphorus=0.0,
        potassium=0.0,
        ash=0.0,
        non_degradable_volatile_solids=0.0,
        degradable_volatile_solids=0.0,
        total_solids=0.0,
        volume=5.0,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10,
    )
    anaerobic_lagoon._manure_to_process = stored_manure
    mock_calculate_ammonia_emissions = mocker.patch.object(
        anaerobic_lagoon, "_calculate_ammonia_emissions", return_value=1.23
    )

    result = anaerobic_lagoon._apply_ammonia_emissions(manure_temp)

    assert result == 1.23
    assert stored_manure.ammoniacal_nitrogen == pytest.approx(8.77)
    assert stored_manure.nitrogen == pytest.approx(10.77)
    mock_calculate_ammonia_emissions.assert_called_once_with(
        total_ammoniacal_nitrogen=10.0,
        mass=stored_manure.volume * ManureConstants.SLURRY_MANURE_DENSITY,
        density=ManureConstants.SLURRY_MANURE_DENSITY,
        temperature=manure_temp,
        ammonia_resistance=ManureConstants.STORAGE_RESISTANCE,
        surface_area=anaerobic_lagoon._surface_area,
        pH=ManureConstants.DEFAULT_STORED_MANURE_PH,
    )
