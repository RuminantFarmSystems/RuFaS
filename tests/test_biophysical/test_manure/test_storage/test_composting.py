from copy import copy
import pytest
from pytest_mock import MockerFixture
from RUFAS.biophysical.manure.storage.composting import Composting, CompostingType
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time


def test_enum_members_exist() -> None:
    assert CompostingType.INTENSIVE_WINDROW.name == "INTENSIVE_WINDROW"
    assert CompostingType.PASSIVE_WINDROW.name == "PASSIVE_WINDROW"
    assert CompostingType.STATIC_PILE.name == "STATIC_PILE"


def test_enum_values() -> None:
    assert CompostingType.INTENSIVE_WINDROW.value == "intensive windrow"
    assert CompostingType.PASSIVE_WINDROW.value == "passive windrow"
    assert CompostingType.STATIC_PILE.value == "static pile"


def test_enum_reverse_lookup() -> None:
    assert CompostingType("intensive windrow") == CompostingType.INTENSIVE_WINDROW
    assert CompostingType("passive windrow") == CompostingType.PASSIVE_WINDROW
    assert CompostingType("static pile") == CompostingType.STATIC_PILE


def test_invalid_enum_raises_value_error() -> None:
    with pytest.raises(ValueError) as exc_info:
        CompostingType("deep pit composting")
    assert "deep pit composting" in str(exc_info.value)


def test_composting_init(mocker: MockerFixture) -> None:
    """Tests the initialization of Composting by mocking the parent class initialization."""
    mock_processor_init = mocker.patch("RUFAS.biophysical.manure.storage.storage.Storage.__init__", return_value=None)
    Composting(
        name=(dummy_name := "dummy_name"),
        composting_type=CompostingType.INTENSIVE_WINDROW,
        storage_time_period=(dummy_storage_time_period := 18),
        surface_area=(dummy_surface_area := 6.6),
    )

    mock_processor_init.assert_called_once_with(
        name=dummy_name,
        is_housing_emissions_calculator=False,
        cover=StorageCover.NO_COVER,
        storage_time_period=dummy_storage_time_period,
        surface_area=dummy_surface_area,
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
        surface_area=1.0,
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
    mocker.patch.object(composting_instance, "_determine_outdoor_storage_temperature", return_value=20.0)
    mocker.patch.object(composting_instance, "_calculate_composting_methane_emissions", return_value=1.0)
    mocker.patch.object(composting_instance, "_calculate_carbon_decomposition", return_value=1.0)
    mocker.patch.object(composting_instance, "_apply_dry_matter_loss")
    mocker.patch.object(composting_instance, "_calculate_nitrous_oxide_emissions", return_value=0.5)
    mocker.patch.object(composting_instance, "_calculate_nitrogen_loss_to_leaching", return_value=0.5)
    mocker.patch.object(composting_instance, "_calculate_ammonia_emissions", return_value=0.5)
    mocker.patch.object(composting_instance, "_apply_nitrogen_losses")
    mocker.patch.object(composting_instance, "_report_processor_output")
    mocker.patch.object(composting_instance, "_report_manure_stream")

    def mock_process_manure_side_effect(_: CurrentDayConditions, __: Time) -> dict[str, ManureStream]:
        composting_instance._stored_manure += composting_instance._received_manure
        composting_instance._received_manure = ManureStream.make_empty_manure_stream()
        return {}

    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.Storage.process_manure",
        side_effect=mock_process_manure_side_effect,
    )

    mock_conditions = mocker.MagicMock(spec=CurrentDayConditions, precipitation=5.0, mean_air_temperature=20.0)
    mock_time = mocker.MagicMock(spec=Time)
    mock_time.simulation_day = 50

    result = composting_instance.process_manure(mock_conditions, mock_time)

    composting_instance._determine_outdoor_storage_temperature.assert_called_once()
    composting_instance._calculate_composting_methane_emissions.assert_called_once()
    composting_instance._calculate_carbon_decomposition.assert_called_once()
    composting_instance._apply_dry_matter_loss.assert_called_once()
    composting_instance._calculate_nitrous_oxide_emissions.assert_called_once()
    composting_instance._calculate_nitrogen_loss_to_leaching.assert_called_once()
    composting_instance._calculate_ammonia_emissions.assert_called_once()
    composting_instance._apply_nitrogen_losses.assert_called_once()

    assert composting_instance._report_processor_output.call_count == 5
    assert composting_instance._report_manure_stream.call_count == 2

    assert result == {}


def test_apply_dry_matter_loss_valid(composting_instance: Composting,
                                     stored_manure: ManureStream,
                                     received_manure: ManureStream,
                                     ) -> None:
    """Ensure solids are updated correctly with valid dry matter loss."""
    composting_instance._stored_manure = stored_manure
    composting_instance._received_manure = received_manure
    composting_instance._manure_to_process = copy(received_manure)
    composting_instance._calculate_dry_matter_loss = lambda m, c: 4.0
    composting_instance._calculate_degradable_volatile_solids_fraction = lambda: 0.5

    composting_instance._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    manure = composting_instance._manure_to_process
    assert manure.non_degradable_volatile_solids == pytest.approx(7.89 - 4.0 * 0.5)
    assert manure.degradable_volatile_solids == pytest.approx(8.90 - 4.0 * 0.5)
    assert manure.total_solids == pytest.approx(29.01 - 4.0)


def test_apply_dry_matter_loss_raises_value_error(composting_instance: Composting,
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
    composting_instance._calculate_dry_matter_loss = lambda m, c: 100.0
    composting_instance._calculate_degradable_volatile_solids_fraction = lambda: 0.5

    with pytest.raises(ValueError, match="Dry-matter loss calculations resulted in negative received-manure values"):
        composting_instance._apply_dry_matter_loss(methane_emission=2.0, carbon_decomposition=1.0)

    composting_instance._om.add_error.assert_called_once()
    error_args = mock_add_error.call_args[0]
    error_message = error_args[1]

    assert any(x in error_message for x in [
        "non_degradable_volatile_solids",
        "degradable_volatile_solids",
        "total_solids"
    ])
