import copy
from unittest.mock import MagicMock, call

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.open_lot_cbpb_calculator import OpenLotCbpbCalculator
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
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
def open_lot() -> OpenLot:
    """Returns a fixture AnaerobicLagoon."""
    return OpenLot(
        name="dummy_name",
        cover=StorageCover.NO_COVER,
        storage_time_period=18,
        surface_area=6.6
    )


@pytest.mark.parametrize("has_manure_return", [True, False])
def test_process_manure(mocker, stored_manure, received_manure, open_lot, has_manure_return):
    open_lot._stored_manure = stored_manure
    open_lot._received_manure = received_manure
    dummy_current_day_conditions = MagicMock(spec=CurrentDayConditions)
    dummy_current_day_conditions.mean_air_temperature = 20.0
    dummy_time = MagicMock(spec=Time)
    dummy_time.simulation_day = 5
    if has_manure_return:
        returned_manure = copy.copy(stored_manure)
        returned_manure.nitrogen = returned_manure.nitrogen - 6.66
        super_return_value = {"manure": returned_manure}
    else:
        super_return_value = None
    mock_super_process = mocker.patch.object(Storage, "process_manure", return_value=super_return_value)
    mock_calc_n2o = mocker.patch.object(open_lot, "_calculate_nitrous_oxide_emissions", return_value=1.11)
    mock_calc_methane = mocker.patch.object(open_lot, "calculate_ifsm_methane_emission", return_value=2.22)
    mock_calc_n_loss = mocker.patch.object(open_lot, "calculate_nitrogen_loss_from_leaching", return_value=3.33)
    mock_apply_ammonia = mocker.patch.object(open_lot, "_apply_ammonia_emission", return_value=4.44)
    mock_calc_dry_matter = mocker.patch.object(open_lot, "calculate_dry_matter_changes", return_value=5.55)
    mock_calc_total_N_loss = mocker.patch.object(open_lot, "calculate_total_nitrogen_loss_from_open_lots",
                                                 return_value=6.66)
    mock_report_manure_stream = mocker.patch.object(open_lot, "_report_manure_stream")
    mock_report_processor_output = mocker.patch.object(open_lot, "_report_processor_output")
    mocker.patch.object(ManureConstants, "SOLID_MANURE_DENSITY", new=1000)
    result = open_lot.process_manure(dummy_current_day_conditions, dummy_time)
    mock_super_process.assert_called_once_with(dummy_current_day_conditions, dummy_time)
    mock_calc_n2o.assert_called_once_with(0.02, received_manure.nitrogen)
    mock_calc_methane.assert_called_once_with(
        open_lot._received_manure.total_volatile_solids, dummy_current_day_conditions.mean_air_temperature
    )
    mock_calc_n_loss.assert_called_once_with(received_manure.nitrogen)
    mock_apply_ammonia.assert_called_once_with(received_manure.nitrogen)
    mock_calc_dry_matter.assert_called_once_with(
        methane_emission=2.22,
        degradable_volatile_solids=received_manure.degradable_volatile_solids,
        non_degradable_volatile_solids=received_manure.non_degradable_volatile_solids,
    )
    mock_calc_total_N_loss.assert_called_once_with(4.44, 3.33, 1.11)
    if has_manure_return:
        initial_nitrogen = stored_manure.nitrogen - 6.66
    else:
        initial_nitrogen = stored_manure.nitrogen
    expected_nitrogen = max(0.0, initial_nitrogen - 6.66)
    degradable_fraction = received_manure.degradable_volatile_solids / received_manure.total_solids
    expected_non_degradable = max(0.0, stored_manure.non_degradable_volatile_solids - (5.55 * degradable_fraction))
    expected_degradable = max(0.0, stored_manure.degradable_volatile_solids - (5.55 * (1 - degradable_fraction)))
    expected_total_solids = max(0.0, stored_manure.total_solids - 5.55)
    manure_to_process = open_lot._manure_to_process
    assert manure_to_process.nitrogen == pytest.approx(expected_nitrogen)
    assert manure_to_process.non_degradable_volatile_solids == pytest.approx(expected_non_degradable)
    assert manure_to_process.degradable_volatile_solids == pytest.approx(expected_degradable)
    assert manure_to_process.total_solids == pytest.approx(expected_total_solids)
    assert manure_to_process.volume == pytest.approx(manure_to_process.mass / 1000)
    if not super_return_value:
        assert open_lot._stored_manure == manure_to_process
    mock_report_manure_stream.assert_has_calls([
        call(manure_to_process, "accumulated", dummy_time.simulation_day),
        call(received_manure, "received", dummy_time.simulation_day),
    ])
    data_origin_name = open_lot.process_manure.__name__
    units = MeasurementUnits.KILOGRAMS
    mock_report_processor_output.assert_has_calls([
        call("storage_methane", 2.22, data_origin_name, units, dummy_time.simulation_day),
        call("storage_ammonia_N", 4.44, data_origin_name, units, dummy_time.simulation_day),
        call("storage_nitrous_oxide_N", 1.11, data_origin_name, units, dummy_time.simulation_day),
        call("storage_nitrogen_leached", 3.33, data_origin_name, units, dummy_time.simulation_day),
    ])
    assert result == super_return_value


@pytest.mark.parametrize(
    "daily_nitrogen_input, expected_output, expect_exception",
    [
        (0, 0, False),
        (
            100,
            36,
            False,
        ),
        (
            1000,
            360,
            False,
        ),
        (-1, None, True),
        (-10, None, True),
    ],
)
def test_calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input: float, expected_output: float,
                                                                    expect_exception: bool, open_lot: OpenLot) -> None:
    """Test the method calculate_nitrogen_loss_in_open_lots_from_ammonia_emission()."""
    if expect_exception:
        with pytest.raises(ValueError):
            open_lot.calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input)
    else:
        assert (
            open_lot.calculate_nitrogen_loss_in_open_lots_from_ammonia_emission(daily_nitrogen_input)
            == expected_output
        )


@pytest.mark.parametrize(
    "daily_nitrogen_input, expected, expected_error",
    [
        # Standard cases
        (1.5, 0.0525, None),
        # When daily_nitrogen_input is zero
        (0.0, 0.0, None),
        # When daily_nitrogen_input is negative
        (-1.5, None, ValueError),
    ],
)
def test_nitrogen_loss_from_leaching(
    open_lot: OpenLot,
    daily_nitrogen_input: float,
    expected: float,
    expected_error: type[Exception]
) -> None:
    """
    Unit test for calculate_nitrogen_loss_from_leaching().

    This test verifies that the method correctly calculates the nitrogen loss due to leaching in a
    compost bedded pack barn given the daily nitrogen input.
    """
    if expected_error:
        with pytest.raises(expected_error):
            open_lot.calculate_nitrogen_loss_from_leaching(daily_nitrogen_input)
    else:
        actual = open_lot.calculate_nitrogen_loss_from_leaching(daily_nitrogen_input)
        assert actual == pytest.approx(expected)


def test_calculate_total_nitrogen_loss_from_open_lots(open_lot: OpenLot) -> None:
    """Tests calculate_total_nitrogen_loss_from_open_lots()."""
    assert open_lot.calculate_total_nitrogen_loss_from_open_lots(1.0, 2.0, 3.0) == 6.0


def test_apply_ammonia_emission(open_lot: OpenLot, mocker: MockerFixture) -> None:
    """Tests _apply_ammonia_emission()."""
    mock_storage_ammonia = mocker.patch.object(open_lot, "calculate_nitrogen_loss_in_open_lots_from_ammonia_emission",
                                               return_value=1.0)
    open_lot._manure_to_process.ammoniacal_nitrogen = 11
    open_lot._apply_ammonia_emission(10)
    assert open_lot._manure_to_process.ammoniacal_nitrogen == 10
    mock_storage_ammonia.assert_called_once_with(10)


def test_calculate_dry_matter_changes(open_lot: OpenLot, mocker: MockerFixture) -> None:
    """Tests for calculate_dry_matter_changes()."""
    mock_total_carbon_decomposition = mocker.patch.object(OpenLotCbpbCalculator,
                                                          "calculate_total_carbon_decomposition",
                                                          return_value=16)

    expected = open_lot.calculate_dry_matter_changes(1, 2, 3)
    assert expected == 33
    mock_total_carbon_decomposition.assert_called_once()
