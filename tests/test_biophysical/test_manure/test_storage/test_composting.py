from copy import copy
import math
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.storage.composting import Composting
from RUFAS.biophysical.manure.storage.composting_type import CompostingType
from RUFAS.biophysical.manure.storage.solids_storage_calculator import SolidsStorageCalculator
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime


def test_composting_init(mocker: MockerFixture) -> None:
    """Tests the initialization of Composting by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    Composting(
        name=(dummy_name := "dummy_name"),
        composting_type="intensive windrow",
        storage_time_period=(dummy_storage_time_period := 18),
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover=StorageCover.NO_COVER,
        storage_time_period=dummy_storage_time_period,
        surface_area=math.inf,
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
def composting_instance() -> Composting:
    compost = Composting(
        name="compost_test",
        composting_type="intensive windrow",
        storage_time_period=1,
    )
    return compost


def test_process_manure_runs_expected_steps(
    stored_manure: ManureStream,
    received_manure: ManureStream,
    composting_instance: Composting,
    mocker: MockerFixture,
) -> None:
    """Test that the process_manure method runs the expected steps."""
    composting_instance._stored_manure = stored_manure
    composting_instance._received_manure = received_manure
    mock_calc_comp_meth_emission = mocker.patch.object(
        composting_instance, "_calculate_composting_methane_emissions", return_value=1.0
    )
    mock_calc_carb_decomp = mocker.patch.object(
        SolidsStorageCalculator, "calculate_carbon_decomposition", return_value=1.0
    )
    mock_apply_dml = mocker.patch.object(composting_instance, "_apply_dry_matter_loss")
    mock_calc_n2o = mocker.patch.object(composting_instance, "_calculate_nitrous_oxide_emissions", return_value=0.5)
    mock_calc_leaching = mocker.patch.object(
        SolidsStorageCalculator, "calculate_nitrogen_loss_to_leaching", return_value=0.5
    )
    mock_calc_ammonia = mocker.patch.object(
        composting_instance, "_calculate_composting_ammonia_emissions", return_value=0.5
    )
    mock_apply_n_loss = mocker.patch.object(composting_instance, "_apply_nitrogen_losses")
    mock_report_output = mocker.patch.object(composting_instance, "_report_processor_output")
    mock_report_stream = mocker.patch.object(composting_instance, "_report_manure_stream")

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: RufasTime) -> dict[str, ManureStream]:
        composting_instance._stored_manure += composting_instance._received_manure
        composting_instance._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    mock_conditions = mocker.MagicMock(spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0)
    mock_time = mocker.MagicMock(spec=RufasTime)
    mock_time.simulation_day = 50

    result = composting_instance.process_manure(mock_conditions, mock_time)

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


def test_apply_dry_matter_loss_valid(
    composting_instance: Composting,
    stored_manure: ManureStream,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure solids are updated correctly with valid dry matter loss."""
    composting_instance._stored_manure = stored_manure
    composting_instance._received_manure = received_manure
    composting_instance._manure_to_process = copy(received_manure)
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

    composting_instance._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    manure = composting_instance._manure_to_process
    assert manure.non_degradable_volatile_solids == pytest.approx(7.89 - 4.0 * 0.5)
    assert manure.degradable_volatile_solids == pytest.approx(8.90 - 4.0 * 0.5)
    assert manure.total_solids == pytest.approx(29.01 - 4.0)


def test_apply_dry_matter_loss_raises_value_error(
    composting_instance: Composting,
    stored_manure: ManureStream,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure ValueError is raised and error is logged when losses go below zero."""
    composting_instance._stored_manure = stored_manure
    composting_instance._received_manure = received_manure
    composting_instance._manure_to_process = copy(received_manure)
    composting_instance._om = OutputManager()
    mock_add_error = mocker.patch.object(composting_instance._om, "add_error", return_value=None)
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
        composting_instance._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    mock_add_error.assert_called_once()
    error_args = mock_add_error.call_args[0]
    error_message = error_args[1]

    assert any(
        x in error_message for x in ["non_degradable_volatile_solids", "degradable_volatile_solids", "total_solids"]
    )


def test_apply_nitrogen_losses_valid(composting_instance: Composting, received_manure: ManureStream) -> None:
    """Ensure nitrogen losses are applied correctly without error."""
    composting_instance._manure_to_process = copy(received_manure)
    original_nitrogen = received_manure.nitrogen
    original_ammoniacal_nitrogen = received_manure.ammoniacal_nitrogen

    composting_instance._apply_nitrogen_losses(
        storage_nitrous_oxide_N=1.0,
        storage_ammonia_N=1.0,
        storage_N_loss_from_leaching=1.0,
    )

    expected_nitrogen = original_nitrogen - 3.0
    expected_ammoniacal_nitrogen = original_ammoniacal_nitrogen - 1.0
    assert composting_instance._manure_to_process.nitrogen == pytest.approx(expected_nitrogen)
    assert composting_instance._manure_to_process.ammoniacal_nitrogen == pytest.approx(expected_ammoniacal_nitrogen)


def test_apply_nitrogen_losses_raises_value_error(
    composting_instance: Composting,
    received_manure: ManureStream,
    mocker: MockerFixture,
) -> None:
    """Ensure ValueError is raised and error is logged when losses exceed available nitrogen."""
    composting_instance._manure_to_process = copy(received_manure)
    composting_instance._manure_to_process.nitrogen = 2.0
    composting_instance._om = OutputManager()
    mock_add_error = mocker.patch.object(composting_instance._om, "add_error", return_value=None)

    with pytest.raises(ValueError, match="Nitrogen loss application error"):
        composting_instance._apply_nitrogen_losses(
            storage_nitrous_oxide_N=1.0,
            storage_ammonia_N=1.0,
            storage_N_loss_from_leaching=1.5,
        )

    mock_add_error.assert_called_once()
    error_args = mock_add_error.call_args[0]
    assert "Cannot have total nitrogen losses greater than total received manure nitrogen." in error_args[1]


def test_calculate_composting_ammonia_emissions() -> None:
    """Test ammonia emission calculation with a simple input."""
    composting_type = CompostingType.PASSIVE_WINDROW
    received_nitrogen = 12.0

    expected = 0.45 * 12.0
    result = Composting._calculate_composting_ammonia_emissions(composting_type, received_nitrogen)

    assert result == pytest.approx(expected)


def test_calculate_nitrous_oxide_emissions() -> None:
    """Test nitrous oxide emission calculation with a simple input."""
    nitrous_oxide_fraction = 0.02
    received_nitrogen = 50.0

    expected = 0.02 * 50.0
    result = Composting._calculate_nitrous_oxide_emissions(nitrous_oxide_fraction, received_nitrogen)

    assert result == pytest.approx(expected)


def test_calculate_composting_methane_emissions(mocker: MockerFixture) -> None:
    """Test composting methane emissions calculation."""
    manure_temperature = 25.0
    manure_volatile_solids = 100.0
    dummy_mcf = 0.01
    expected = manure_volatile_solids * (0.24 * 0.67 * dummy_mcf)

    mocker.patch.object(
        Composting,
        "_calculate_methane_conversion_factor",
        return_value=dummy_mcf,
    )

    result = Composting._calculate_composting_methane_emissions(
        manure_temperature,
        manure_volatile_solids,
        CompostingType.PASSIVE_WINDROW,
    )

    assert result == pytest.approx(expected)


@pytest.mark.parametrize(
    "composting_type, temperature, expected",
    [
        (CompostingType.STATIC_PILE, 10.0, ManureConstants.MCF_COMPOSTING_STATIC_PILE),
        (
            CompostingType.PASSIVE_WINDROW,
            ManureConstants.MCF_LOWER_BOUND_TEMPERATURE - 1,
            ManureConstants.MCF_COMPOSTING_WINDROW_LOW,
        ),
        (
            CompostingType.PASSIVE_WINDROW,
            ManureConstants.MCF_LOWER_BOUND_TEMPERATURE,
            ManureConstants.MCF_COMPOSTING_WINDROW_MEDIUM,
        ),
        (
            CompostingType.INTENSIVE_WINDROW,
            ManureConstants.MCF_UPPER_BOUND_TEMPERATURE,
            ManureConstants.MCF_COMPOSTING_WINDROW_MEDIUM,
        ),
        (
            CompostingType.INTENSIVE_WINDROW,
            ManureConstants.MCF_UPPER_BOUND_TEMPERATURE + 1,
            ManureConstants.MCF_COMPOSTING_WINDROW_HIGH,
        ),
    ],
)
def test_calculate_methane_conversion_factor(
    composting_type: CompostingType, temperature: float, expected: float
) -> None:
    """Test MCF value returned based on composting type and temperature."""
    result = Composting._calculate_methane_conversion_factor(temperature, composting_type)
    assert result == expected
