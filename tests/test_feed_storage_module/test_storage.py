import pytest
from pytest_mock import MockerFixture
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.time import Time
from .sample_crop_data import sample_crop_data


@pytest.fixture
def storage() -> Storage:
    """
    Pytest fixture to create a Storage instance for testing.

    Returns
    -------
    Storage
        An instance of the Storage class.
    """
    return Storage()


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


def test_stored_mass(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    assert storage.stored_mass == 0.0  # Initially empty
    storage.receive_crop(harvested_crop)
    storage.receive_crop(harvested_crop)
    assert storage.stored_mass == 200.0  # After adding a crop


def test_successful_receive_crop(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.receive_crop(harvested_crop)
    assert len(storage.stored) == 1
    assert storage.stored[0].fresh_mass == harvested_crop.fresh_mass
    assert storage.stored[0].storage_time.day == harvested_crop.storage_time.day
    assert storage.stored[0].storage_time.year == harvested_crop.storage_time.year


def test_receive_crop_exceeds_capacity(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.capacity = 50.0  # Set a smaller capacity
    with pytest.raises(Exception) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "exceeds the storage capacity" in str(excinfo.value)


def test_receive_unacceptable_crop(storage: Storage) -> None:
    storage.acceptable_crops = [CropCategory.ALFALFA]
    incompatible_crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data  # type: ignore[arg-type]
    )
    with pytest.raises(ValueError):
        storage.receive_crop(incompatible_crop)


def test_receive_crop_without_acceptable_crops(storage: Storage, harvested_crop: HarvestedCrop) -> None:
    storage.acceptable_crops = []

    with pytest.raises(NotImplementedError) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "Storage.acceptable_crops is not populated" in str(excinfo.value)


def test_process_degradations(storage: Storage) -> None:
    """
    Test the process_degradations method of the Storage class.
    """
    with pytest.raises(NotImplementedError) as e:
        storage.process_degradations()
    assert "Cannot use Storage.process_degradations, use a child class." in str(e.value)


def test_give_feed(storage: Storage) -> None:
    """
    Test the give_feed method of the Storage class.
    """
    pass


@pytest.mark.parametrize(
    "dry_matter,percentage,category,temp,expected",
    [
        (100.0, 25.0, CropCategory.ALFALFA, 20.0, 1.378),
        (40.0, 20.0, CropCategory.ALFALFA, 6.0, 0.624),
        (150.0, 19.0, CropCategory.ALFALFA, 10.0, 0.0),
        (200.0, 23.0, CropCategory.ALFALFA, 46.0, 0.0),
        (140.0, 15.0, CropCategory.CORN, 30.0, 1.2096),
        (55.0, 66.0, CropCategory.GRASS, 25.0, 0.0),
        (120.0, 4.0, CropCategory.SMALL_GRAIN, 15.0, 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_gas(
    storage: Storage, harvested_crop: HarvestedCrop, mocker: MockerFixture, dry_matter: float, percentage: float, category: CropCategory, temp: float, expected: float
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Sileage."""
    mocker.patch("RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass", new_callable=mocker.PropertyMock, return_value=dry_matter)
    harvested_crop.dry_matter_percentage = percentage
    harvested_crop.category = category
    mock_conditions = mocker.MagicMock(autospec=CurrentDayConditions)
    mock_conditions.mean_air_temperature = temp
    mock_time = mocker.MagicMock(autospec=Time)

    actual = storage.calculate_dry_matter_loss_to_gas(harvested_crop, mock_conditions, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "dry_matter,density,expected",
    [
        (100.0, 100.0, 0.0),
        (92.5, 600.0, 233813.848370),
        (75.0, 10_000.0, 13327549.589989),
    ],
)
def test_calculate_heat_generated(storage: Storage, dry_matter: float, density: float, expected: float) -> None:
    """
    Test the calculate_heat_generated method of the Storage class.
    """
    actual = storage.calculate_heat_generated(dry_matter, density)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("dry_matter,expected", [(0.0, 540.0), (90.0, 144.0), (75.0, 210.0)])
def test_calculate_bale_density(storage: Storage, dry_matter: float, expected: float) -> None:
    """
    Test the calculate_bale_density method of the Storage class.
    """
    actual = storage.calculate_bale_density(dry_matter)

    assert actual == expected


def test_recalculate_nutrient_fractions(storage: Storage) -> None:
    """
    Test the recalculate_nutrient_fractions method of the Storage class.
    """
    with pytest.raises(NotImplementedError) as e:
        storage.recalculate_nutrient_fractions()
    assert "Cannot use Storage.recalculate_nutrient_fractions, use a child class." in str(e.value)


@pytest.mark.parametrize(
    "nutrients,loss_coefficient,dry_matter_loss,dry_matter,expected",
    [
        (8.0, 0.4, 20.0, 100.0, 1.9),
        (4.0, 0.17, 21.0, 150.0, 0.623488),
        (6.0, 0.0, 10.0, 100.0, 0.666667),
        (0.5, 0.7, 100.0, 200.0, 0.0),
        (3.4, 0.8, 0.0, 200.0, 0.0),
    ],
)
def test_recalculate_nutrient_concentration(
    storage: Storage,
    nutrients: float,
    loss_coefficient: float,
    dry_matter_loss: float,
    dry_matter: float,
    expected: float,
) -> None:
    """
    Test the recalculate_nutrient_concentration method of the Storage class.
    """
    actual = storage.recalculate_nutrient_concentration(nutrients, loss_coefficient, dry_matter_loss, dry_matter)

    assert pytest.approx(actual) == expected
