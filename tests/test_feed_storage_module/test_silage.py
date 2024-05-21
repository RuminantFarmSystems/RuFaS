import pytest
from pytest_mock import MockerFixture
from .sample_crop_data import sample_crop_data
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.silage import Silage, Bunker, Pile, Bag
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.time import Time


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


@pytest.fixture
def bunker() -> Bunker:
    return Bunker()


@pytest.fixture
def pile() -> Pile:
    return Pile()


@pytest.fixture
def bag() -> Bag:
    return Bag()
