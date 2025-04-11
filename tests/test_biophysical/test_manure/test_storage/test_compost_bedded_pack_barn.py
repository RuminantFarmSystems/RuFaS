from copy import copy

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.compost_bedded_pack_barn import CompostBeddedPackBarn
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream

from RUFAS.rufas_time import RufasTime


def test_open_lot_init(mocker: MockerFixture) -> None:
    """Tests the initialization of Composting by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    OpenLot(name=(dummy_name := "dummy_name"), storage_time_period=(dummy_storage_time_period := 18), surface_area=10)

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover=StorageCover.NO_COVER,
        storage_time_period=dummy_storage_time_period,
        surface_area=10,
    )


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
def compost_bedded_pack_barn() -> CompostBeddedPackBarn:
    """Returns a fixture CBPB."""
    return CompostBeddedPackBarn(name="dummy_name", storage_time_period=18, surface_area=6.6)


def test_process_manure_runs_expected_steps(
    stored_manure: ManureStream,
    received_manure: ManureStream,
    compost_bedded_pack_barn: CompostBeddedPackBarn,
    mocker: MockerFixture,
) -> None:
    """Test that the process_manure method runs the expected steps."""
    compost_bedded_pack_barn._stored_manure = stored_manure
    compost_bedded_pack_barn._received_manure = received_manure
    mock_calc_comp_meth_emission = mocker.patch.object(
        SolidsStorageCalculator, "calculate_ifsm_methane_emission", return_value=1.0
    )
    mock_calc_carb_decomp = mocker.patch.object(
        SolidsStorageCalculator, "calculate_carbon_decomposition", return_value=1.0
    )
    mock_apply_dml = mocker.patch.object(compost_bedded_pack_barn, "_apply_dry_matter_loss")
    mock_calc_n2o = mocker.patch.object(compost_bedded_pack_barn, "_calculate_cbpb_nitrous_oxide_emission", return_value=0.5)
    mock_calc_leaching = mocker.patch.object(
        SolidsStorageCalculator, "calculate_nitrogen_loss_to_leaching", return_value=0.5
    )
    mock_calc_ammonia = mocker.patch.object(compost_bedded_pack_barn, "_calculate_cbpb_ammonia_emission", return_value=0.5)
    mock_apply_n_loss = mocker.patch.object(compost_bedded_pack_barn, "_apply_nitrogen_losses")
    mock_report_output = mocker.patch.object(compost_bedded_pack_barn, "_report_processor_output")
    mock_report_stream = mocker.patch.object(compost_bedded_pack_barn, "_report_manure_stream")

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        compost_bedded_pack_barn._stored_manure += compost_bedded_pack_barn._received_manure
        compost_bedded_pack_barn._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    mock_conditions = mocker.MagicMock(spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0)
    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 50

    result = compost_bedded_pack_barn.process_manure(mock_conditions, mock_time)

    mock_calc_comp_meth_emission.assert_called_once()
    mock_calc_carb_decomp.assert_called_once()
    mock_apply_dml.assert_called_once()
    mock_calc_n2o.assert_called_once()
    mock_calc_leaching.assert_called_once()
    mock_calc_ammonia.assert_called_once()
    mock_apply_n_loss.assert_called_once()

    assert mock_report_output.call_count == 5
    assert mock_report_stream.call_count == 2

    assert result == {}