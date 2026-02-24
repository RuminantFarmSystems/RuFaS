import math
from copy import copy

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.bedded_pack import BeddedPack
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.output_manager import OutputManager

from RUFAS.rufas_time import RufasTime


def test_bedded_pack_init(mocker: MockerFixture) -> None:
    """Tests the initialization of bedded pack by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    BeddedPack(
        name=(dummy_name := "dummy_name"),
        is_mixed=True,
        storage_time_period=(dummy_storage_time_period := 18),
        surface_area=10,
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=True,
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
        methane_production_potential=0.24,
        bedding_non_degradable_volatile_solids=10
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
        methane_production_potential=0.24,
        bedding_non_degradable_volatile_solids=10
    )


@pytest.fixture
def bedded_pack() -> BeddedPack:
    """Returns a fixture bedded pack."""
    return BeddedPack(name="dummy_name", is_mixed=True, storage_time_period=18, surface_area=6.6)


def test_process_manure_runs_no_annual_temperature(
    stored_manure: ManureStream,
    received_manure: ManureStream,
    bedded_pack: BeddedPack,
    mocker: MockerFixture,
) -> None:
    """Test that the process_manure method runs the expected steps."""
    mock_add_error = mocker.patch.object(OutputManager, "add_error")
    bedded_pack.stored_manure = stored_manure
    bedded_pack._received_manure = received_manure
    mock_calc_comp_meth_emission = mocker.patch.object(
        SolidsStorageCalculator, "calculate_ifsm_methane_emission", return_value=1.0
    )
    mock_calc_carb_decomp = mocker.patch.object(
        SolidsStorageCalculator, "calculate_carbon_decomposition", return_value=1.0
    )
    mock_apply_dml = mocker.patch.object(bedded_pack, "_apply_dry_matter_loss")
    mock_calc_n2o = mocker.patch.object(bedded_pack, "_calculate_bedded_pack_nitrous_oxide_emission", return_value=0.5)
    mock_calc_leaching = mocker.patch.object(
        SolidsStorageCalculator, "calculate_nitrogen_loss_to_leaching", return_value=0.5
    )
    mock_calc_ammonia = mocker.patch.object(bedded_pack, "_calculate_bedded_pack_ammonia_emission", return_value=0.5)
    mock_apply_n_loss = mocker.patch.object(bedded_pack, "_apply_nitrogen_losses")
    mock_report_output = mocker.patch.object(bedded_pack, "_report_processor_output")
    mock_report_stream = mocker.patch.object(bedded_pack, "_report_manure_stream")

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        bedded_pack.stored_manure += bedded_pack._received_manure
        bedded_pack._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    mock_conditions = mocker.MagicMock(
        spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0, annual_mean_air_temperature=None
    )
    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 50

    result = bedded_pack.process_manure(mock_conditions, mock_time)

    mock_calc_comp_meth_emission.assert_not_called()
    mock_calc_carb_decomp.assert_called_once()
    mock_apply_dml.assert_called_once()
    mock_calc_n2o.assert_called_once()
    mock_calc_leaching.assert_called_once()
    mock_calc_ammonia.assert_called_once()
    mock_apply_n_loss.assert_called_once()
    mock_add_error.assert_called_once()

    assert mock_report_output.call_count == 5
    assert mock_report_stream.call_count == 2

    assert result == {}


def test_process_manure_runs_expected_steps(
    stored_manure: ManureStream,
    received_manure: ManureStream,
    bedded_pack: BeddedPack,
    mocker: MockerFixture,
) -> None:
    """Test that the process_manure method runs the expected steps."""
    bedded_pack.stored_manure = stored_manure
    bedded_pack._received_manure = received_manure
    mock_add_error = mocker.patch.object(OutputManager, "add_error")
    mock_calc_comp_meth_emission = mocker.patch.object(
        BeddedPack, "calculate_bedded_pack_methane_emission", return_value=1.0
    )
    mock_calc_carb_decomp = mocker.patch.object(
        SolidsStorageCalculator, "calculate_carbon_decomposition", return_value=1.0
    )
    mock_apply_dml = mocker.patch.object(bedded_pack, "_apply_dry_matter_loss")
    mock_calc_n2o = mocker.patch.object(bedded_pack, "_calculate_bedded_pack_nitrous_oxide_emission", return_value=0.5)
    mock_calc_leaching = mocker.patch.object(
        SolidsStorageCalculator, "calculate_nitrogen_loss_to_leaching", return_value=0.5
    )
    mock_calc_ammonia = mocker.patch.object(bedded_pack, "_calculate_bedded_pack_ammonia_emission", return_value=0.5)
    mock_apply_n_loss = mocker.patch.object(bedded_pack, "_apply_nitrogen_losses")
    mock_report_output = mocker.patch.object(bedded_pack, "_report_processor_output")
    mock_report_stream = mocker.patch.object(bedded_pack, "_report_manure_stream")

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        bedded_pack.stored_manure += bedded_pack._received_manure
        bedded_pack._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    mock_conditions = mocker.MagicMock(
        spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0, annual_mean_air_temperature=15
    )
    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 50

    result = bedded_pack.process_manure(mock_conditions, mock_time)

    mock_calc_comp_meth_emission.assert_called_once()
    mock_calc_carb_decomp.assert_called_once()
    mock_apply_dml.assert_called_once()
    mock_calc_n2o.assert_called_once()
    mock_calc_leaching.assert_called_once()
    mock_calc_ammonia.assert_called_once()
    mock_apply_n_loss.assert_called_once()
    mock_add_error.assert_not_called()

    assert mock_report_output.call_count == 5
    assert mock_report_stream.call_count == 2

    assert result == {}


def test_apply_dry_matter_loss_valid(
    bedded_pack: BeddedPack,
    stored_manure: ManureStream,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure solids are updated correctly with valid dry matter loss."""
    bedded_pack.stored_manure = stored_manure
    bedded_pack._received_manure = received_manure
    bedded_pack._manure_to_process = copy(received_manure)
    mocker.patch.object(
        SolidsStorageCalculator,
        "calculate_dry_matter_loss",
        return_value=4.0,
    )
    mocker.patch.object(
        SolidsStorageCalculator,
        "calculate_degradable_volatile_solids_fraction",
        return_value=0.5,
    )

    bedded_pack._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    manure = bedded_pack._manure_to_process
    assert manure.non_degradable_volatile_solids == pytest.approx(7.89 - 4.0 * 0.5)
    assert manure.degradable_volatile_solids == pytest.approx(8.90 - 4.0 * 0.5)
    assert manure.total_solids == pytest.approx(29.01 - 4.0)


def test_apply_dry_matter_loss_raises_value_error(
    bedded_pack: BeddedPack,
    stored_manure: ManureStream,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure ValueError is raised and error is logged when losses go below zero."""
    bedded_pack.stored_manure = stored_manure
    bedded_pack._received_manure = received_manure
    bedded_pack._manure_to_process = copy(received_manure)
    bedded_pack._om = OutputManager()
    mock_add_error = mocker.patch.object(bedded_pack._om, "add_error", return_value=None)
    mocker.patch.object(
        SolidsStorageCalculator,
        "calculate_dry_matter_loss",
        return_value=100.0,
    )
    mocker.patch.object(
        SolidsStorageCalculator,
        "calculate_degradable_volatile_solids_fraction",
        return_value=0.5,
    )

    with pytest.raises(ValueError, match="Dry-matter loss calculations resulted in negative received-manure values"):
        bedded_pack._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    mock_add_error.assert_called_once()
    error_args = mock_add_error.call_args[0]
    error_message = error_args[1]

    assert any(
        x in error_message for x in ["non_degradable_volatile_solids", "degradable_volatile_solids", "total_solids"]
    )


def test_apply_nitrogen_losses_valid(bedded_pack: BeddedPack, received_manure: ManureStream) -> None:
    """Ensure nitrogen losses are applied correctly without error."""
    bedded_pack._manure_to_process = copy(received_manure)
    original_nitrogen = received_manure.nitrogen
    original_ammoniacal_nitrogen = received_manure.ammoniacal_nitrogen

    bedded_pack._apply_nitrogen_losses(
        storage_nitrous_oxide_N=1.0,
        storage_ammonia_N=1.0,
        storage_N_loss_from_leaching=1.0,
    )

    expected_nitrogen = original_nitrogen - 3.0
    expected_ammoniacal_nitrogen = original_ammoniacal_nitrogen - 1.0
    assert bedded_pack._manure_to_process.nitrogen == pytest.approx(expected_nitrogen)
    assert bedded_pack._manure_to_process.ammoniacal_nitrogen == pytest.approx(expected_ammoniacal_nitrogen)


def test_apply_nitrogen_losses_raises_value_error_for_nitrogen_losses(
    bedded_pack: BeddedPack,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure ValueError is raised and error is logged when losses exceed available nitrogen."""
    bedded_pack._manure_to_process = copy(received_manure)
    bedded_pack._manure_to_process.nitrogen = 2.0
    bedded_pack._om = OutputManager()
    mock_add_error = mocker.patch.object(bedded_pack._om, "add_error", return_value=None)

    with pytest.raises(ValueError, match="Nitrogen loss application error"):
        bedded_pack._apply_nitrogen_losses(
            storage_nitrous_oxide_N=1.0,
            storage_ammonia_N=1.0,
            storage_N_loss_from_leaching=1.5,
        )

    mock_add_error.assert_called_once()
    error_args = mock_add_error.call_args[0]
    assert "Cannot have total nitrogen losses greater than total received manure nitrogen." in error_args[1]


@pytest.mark.parametrize(
    "received_nitrogen, is_tilled, expected",
    [
        (100.0, True, 7),
        (100.0, False, 1),
    ],
)
def test_nitrous_oxide_emission(
    bedded_pack: BeddedPack, received_nitrogen: float, is_tilled: bool, expected: float
) -> None:
    result: float = bedded_pack._calculate_bedded_pack_nitrous_oxide_emission(received_nitrogen, is_tilled)
    assert result == pytest.approx(expected, rel=1e-6)


def test_nitrous_oxide_negative_input(bedded_pack: BeddedPack) -> None:
    with pytest.raises(ValueError, match="Daily nitrogen input mass must be non-negative: -1.0"):
        bedded_pack._calculate_bedded_pack_nitrous_oxide_emission(-1.0, True)


@pytest.mark.parametrize(
    "received_nitrogen, is_tilled, expected",
    [
        (200.0, True, 100),
        (200.0, False, 50),
    ],
)
def test_ammonia_emission(bedded_pack: BeddedPack, received_nitrogen: float, is_tilled: bool, expected: float) -> None:
    result: float = bedded_pack._calculate_bedded_pack_ammonia_emission(received_nitrogen, is_tilled)
    assert result == pytest.approx(expected, rel=1e-6)


def test_ammonia_negative_input(bedded_pack: BeddedPack) -> None:
    with pytest.raises(ValueError, match="Daily nitrogen input mass must be non-negative: -1.0"):
        bedded_pack._calculate_bedded_pack_ammonia_emission(-1.0, False)


def test_calculate_bedded_pack_methane_emission(bedded_pack: BeddedPack, mocker: MockerFixture) -> None:
    """Tests calculate_bedded_pack_methane_emission()."""
    mock_conversion_factor = mocker.patch.object(
        BeddedPack,
        "calculate_bedded_pack_methane_conversion_factor",
        return_value=1.0,
    )
    manure_volatile_solids = 1000.0
    expected = (manure_volatile_solids * 0.24 * 0.67 * 1.0) / 100

    actual = bedded_pack.calculate_bedded_pack_methane_emission(True, manure_volatile_solids, 1.0, 0.24)

    mock_conversion_factor.assert_called_once_with(True, 1.0)
    assert actual == pytest.approx(expected)


@pytest.mark.parametrize(
    "is_mixed, manure_temperature, expected_mcf",
    [
        # mixed
        (True, -10.0, 0.5),  # Falls in (-inf, 4.6]
        (True, 0.0, 0.5),  # “
        (True, 4.6, 0.5),  # upper bound bin 1
        (True, 4.7, 0.5),  # lower bound bin 2
        (True, 5.8, 0.5),  # upper bound bin 2 (first match)
        (True, 10.0, 1.0),  # middle bin 3
        (True, 14.0, 1.0),  # lower bound bin 4
        (True, 25.2, 1.5),  # lower bound bin 5
        # unmixed
        (False, -10.0, 21.0),
        (False, 0.0, 21.0),
        (False, 4.6, 21.0),
        (False, 4.7, 26.0),
        (False, 5.8, 26.0),
        (False, 10.0, 37.0),
        (False, 14.0, 41.0),
        (False, 25.2, 74.0),
    ],
)
def test_calculate_bedded_pack_mcf_returns_expected(
    bedded_pack: BeddedPack,
    is_mixed: bool,
    manure_temperature: float,
    expected_mcf: float,
) -> None:
    """Tests calculate_bedded_pack_mcf_returns_expected()."""
    result = bedded_pack.calculate_bedded_pack_methane_conversion_factor(is_mixed, manure_temperature)
    assert result == expected_mcf


def test_calculate_bedded_pack_mcf_raises_for_temperature_gap(bedded_pack: BeddedPack) -> None:
    """Tests calculate_bedded_pack_mcf_returns_expected() for fall back cases."""
    with pytest.raises(ValueError) as excinfo:
        bedded_pack.calculate_bedded_pack_methane_conversion_factor(True, math.nan)

    assert "out of any defined bin" in str(excinfo.value)
