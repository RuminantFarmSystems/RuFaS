import pytest
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
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


def test_calculate_dry_matter_loss_to_gas(storage: Storage) -> None:
    """
    Test the calculate_dry_matter_loss_to_gas method of the Storage class.
    """
    with pytest.raises(NotImplementedError) as e:
        storage.calculate_dry_matter_loss_to_gas(100.0, 30)
    assert "Cannot use Storage.calculate_dry_matter_loss_to_gas, use a child class." in str(e.value)


@pytest.mark.parametrize(
    "dry_matter,mass,expected",
    [
        (31, 100.0, 0.0),
        (30, 100.0, 0.0),
        (25, 200.0, 10.0),
        (1, 150.0, 43.5),
        (0, 250.0, 75.0),
    ],
)
def test_estimate_maximum_effluent(storage: Storage, dry_matter: float, mass: float, expected: float) -> None:
    """
    Test the estimate_maximum_effluent method of the Storage class.
    """
    actual = storage.estimate_maximum_effluent(dry_matter, mass)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "dry_matter,max_effluent,days,expected",
    [
        (100.0, 25.0, 8, 0.0207),
        (350.0, 40.0, 2, 0.002365714),
        (30.0, 55.0, 12, 0.2277),
        (400.0, 12.0, 1, 0.0003105),
        (100.0, 0.0, 4, 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_effluent(
    storage: Storage, dry_matter: float, max_effluent: float, days: int, expected: float
) -> None:
    """
    Test the calculate_dry_matter_loss_to_effluent method of the Storage class.
    """
    actual = storage.calculate_dry_matter_loss_to_effluent(dry_matter, max_effluent, days)

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
