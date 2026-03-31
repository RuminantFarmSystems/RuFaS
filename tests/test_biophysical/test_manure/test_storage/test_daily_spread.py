import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.storage.daily_spread import DailySpread
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime


@pytest.fixture
def daily_spread_instance() -> DailySpread:
    spread = DailySpread(
        name="daily_spread_test",
        cover="no_crust_or_cover",
        surface_area=1,
    )
    return spread


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
        bedding_non_degradable_volatile_solids=10
    )


def test_daily_spread_init(mocker: MockerFixture) -> None:
    """Tests the initialization of DailySpread by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    DailySpread(
        name=(dummy_name := "dummy_name"),
        cover="no_crust_or_cover",
        surface_area=100,
    )
    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover="no_crust_or_cover",
        storage_time_period=1,
        surface_area=100,
    )


def test_process_manure(
    received_manure: ManureStream, daily_spread_instance: DailySpread, mocker: MockerFixture
) -> None:
    """Tests the process_manure() function"""
    mock_conditions = mocker.MagicMock(
        spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0, annual_mean_air_temperature=15
    )
    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 50
    daily_spread_instance._received_manure = received_manure
    mock_report = mocker.patch.object(Processor, "_report_manure_stream")
    mock_process = mocker.patch.object(Storage, "process_manure")

    daily_spread_instance.process_manure(mock_conditions, mock_time)

    mock_report.assert_called_once_with(received_manure, "received", 50)
    mock_process.assert_called_once_with(mock_conditions, mock_time)


def test_receive_manure(received_manure: ManureStream, daily_spread_instance: DailySpread) -> None:
    """Tests overwritten receive_manure function."""
    daily_spread_instance.receive_manure(received_manure)

    assert daily_spread_instance._received_manure == received_manure
