import pytest
from unittest.mock import call
from pytest_mock import MockerFixture
import copy
from .sample_crop_data import sample_crop_data
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.silage import Silage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.units import MeasurementUnits
from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.output_manager import OutputManager


om = OutputManager()


@pytest.fixture
def silage() -> Silage:
    return Silage()


@pytest.fixture
def harvested_crop() -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    category = CropCategory.SMALL_GRAIN
    crop_type = CropType.WHEAT
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)  # type: ignore[arg-type]


def test_acceptable_crops(silage: Silage):
    assert silage.acceptable_crops == [
        CropCategory.ALFALFA,
        CropCategory.CORN,
        CropCategory.GRASS,
        CropCategory.SMALL_GRAIN,
    ]


@pytest.mark.parametrize("days_of_loss", [(0), (10), (3)])
def test_process_degradations(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop, days_of_loss: int
) -> None:
    """Tests the implementation of process_degradations in the Silage class."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=Time)
    effluent_loss_days = mocker.patch.object(
        silage, "calculate_days_of_effluent_loss_to_process", return_value=days_of_loss
    )
    dry_loss = mocker.patch.object(silage, "calculate_dry_matter_loss_to_effluent", return_value=10.0)
    moisture_loss = mocker.patch.object(silage, "calculate_moisture_loss_to_effluent", return_value=20.0)
    npn_coefficient = mocker.patch.object(
        silage, "calculate_non_protein_nitrogen_after_effluent_loss", return_value=4.5
    )
    cp_coeffient = mocker.patch.object(silage, "calculate_crude_protein_after_effluent_loss", return_value=5.0)
    reset_attributes = mocker.patch.object(silage, "reset_mass_attributes_after_loss")
    add_variable = mocker.patch.object(om, "add_variable")
    super_process_degradations = mocker.patch("RUFAS.routines.feed_storage.storage.Storage.process_degradations")
    second_crop = copy.deepcopy(harvested_crop)
    silage.stored = [harvested_crop, second_crop]
    expected_info_map = {
        "class": silage.__class__.__name__,
        "function": silage.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
    }
    expected_dry_loss = 20.0 if days_of_loss else 0.0
    expected_moisture_loss = 40.0 if days_of_loss else 0.0

    silage.process_degradations(mock_weather, mock_time)

    effluent_loss_days.assert_has_calls([call(harvested_crop, mock_time), call(second_crop, mock_time)])
    assert dry_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert moisture_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert npn_coefficient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert cp_coeffient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert reset_attributes.call_count == (len(silage.stored) if days_of_loss else 0)
    add_variable.assert_has_calls(
        [
            call("total_effluent_dry_matter_loss", expected_dry_loss, expected_info_map),
            call("total_effluent_moisture_loss", expected_moisture_loss, expected_info_map),
        ]
    )
    super_process_degradations.assert_called_once_with(mock_weather, mock_time)


@pytest.mark.parametrize(
    "day_stored,last_day_processed,current,expected",
    [(1, 1, 6, 5), (1, 3, 3, 0), (40, 45, 50, 5), (40, 45, 55, 5), (10, 22, 25, 0)],
)
def test_calculate_days_of_effluent_loss_to_process(
    mocker: MockerFixture,
    silage: Silage,
    harvested_crop: HarvestedCrop,
    day_stored: int,
    last_day_processed: int,
    current: int,
    expected: int,
) -> None:
    """Tests calculate_days_of_effluent_loss_to_process in Silage."""
    mock_time_stored = mocker.MagicMock(autospec=Time)
    mock_time_stored.simulation_day = day_stored
    mock_last_time_degraded = mocker.MagicMock(autospec=Time)
    mock_last_time_degraded.simulation_day = last_day_processed
    mock_current_time = mocker.MagicMock(autospec=Time)
    mock_current_time.simulation_day = current
    harvested_crop.storage_time = mock_time_stored
    harvested_crop.last_time_degraded = mock_last_time_degraded

    actual = silage.calculate_days_of_effluent_loss_to_process(harvested_crop, mock_current_time)

    assert actual == expected


@pytest.mark.parametrize(
    "max_effluent,days,expected", [(100.0, 10.0, 10.35), (55.0, 0, 0.0), (80.0, 4, 3.312), (120.0, 8, 9.936)]
)
def test_calculate_dry_matter_loss_to_effluent(silage: Silage, max_effluent: float, days: int, expected: float) -> None:
    """Tests calculate_dry_matter_loss_to_effluent in Silage."""
    actual = silage.calculate_dry_matter_loss_to_effluent(max_effluent, days)

    assert actual == expected


@pytest.mark.parametrize(
    "max_effluent,days,expected", [(100.0, 10.0, 89.65), (70.0, 0, 0.0), (90.0, 7, 56.4795), (150.0, 3, 40.3425)]
)
def test_calculate_moisture_loss_to_effluent(silage: Silage, max_effluent: float, days: int, expected: float) -> None:
    """Tests calculate_moisture_loss_to_effluent in Silage."""
    actual = silage.calculate_moisture_loss_to_effluent(max_effluent, days)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "npn,cp,loss_frac,expected",
    [(4.0, 8.0, 0.02, 4.0092731), (2.5, 4.4, 0.05, 2.525287), (0.0, 3.6, 0.01, 0.0)],
)
def test_calculate_non_protein_nitrogen_after_effluent_loss(
    silage: Silage, npn: float, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_non_protein_nitrogen_loss_coefficient in Silage."""
    actual = silage.calculate_non_protein_nitrogen_after_effluent_loss(npn, cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("cp,loss_frac,expected", [(5.6, 0.033, 5.78086866), (2.2, 0.04, 2.27916666), (0.0, 0.05, 0.0)])
def test_calculate_crude_protein_after_effluent_loss(
    silage: Silage, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_crude_protein_loss_coefficient in Silage."""
    actual = silage.calculate_crude_protein_after_effluent_loss(cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


@pytest.fixture
def pile() -> Pile:
    return Pile()


@pytest.fixture
def bag() -> Bag:
    return Bag()
