import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.open_lot import OpenLot
from RUFAS.biophysical.manure.storage.open_lot_cbpb_calculator import OpenLotCbpbCalculator
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.data_structures.animal_to_manure_connection import ManureStream


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
        surface_area=6.6,
        nitrous_oxide_emissions_factor=0.01
    )


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
                                                          "total_carbon_decomposition",
                                                          return_value=16)

    expected = open_lot.calculate_dry_matter_changes(1, 2, 3)
    assert expected == 33
    mock_total_carbon_decomposition.assert_called_once()


def test_process_manure(open_lot: OpenLot) -> None:
    """Tests the process_manure routine of open lot."""
