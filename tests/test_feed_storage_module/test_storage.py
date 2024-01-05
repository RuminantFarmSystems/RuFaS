from typing import Dict
import pytest
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from .sample_crop_data import sample_crop_data  # noqa F401


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
def harvested_crop(sample_crop_data: Dict[str, float]) -> HarvestedCrop:  # noqa F811
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    category = CropCategory.SMALL_GRAIN
    crop_type = CropType.WHEAT
    return HarvestedCrop(category=category, type=crop_type, **sample_crop_data)


def test_stored_mass(storage: Storage, harvested_crop: HarvestedCrop):
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    assert storage.stored_mass == 0.0  # Initially empty
    storage.receive_crop(harvested_crop)
    storage.receive_crop(harvested_crop)
    assert storage.stored_mass == 200.0  # After adding a crop


def test_successful_receive_crop(storage: Storage, harvested_crop: HarvestedCrop):
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.receive_crop(harvested_crop)
    assert len(storage.stored) == 1
    assert storage.stored[0].fresh_mass == harvested_crop.fresh_mass
    assert storage.stored[0].storage_time.day == harvested_crop.storage_time.day
    assert storage.stored[0].storage_time.year == harvested_crop.storage_time.year


def test_receive_crop_exceeds_capacity(storage: Storage, harvested_crop: HarvestedCrop):
    storage.acceptable_crops = [CropCategory.SMALL_GRAIN]
    storage.capacity = 50.0  # Set a smaller capacity
    with pytest.raises(Exception) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "exceeds the storage capacity" in str(excinfo.value)


def test_receive_unacceptable_crop(
    storage: Storage, sample_crop_data: Dict[str, float]
):
    storage.acceptable_crops = [CropCategory.ALFALFA]
    incompatible_crop = HarvestedCrop(
        category=CropCategory.SMALL_GRAIN, type=CropType.WHEAT, **sample_crop_data
    )
    with pytest.raises(ValueError):
        storage.receive_crop(incompatible_crop)


def test_receive_crop_without_acceptable_crops(
    storage: Storage, harvested_crop: HarvestedCrop
):
    storage.acceptable_crops = []

    with pytest.raises(NotImplementedError) as excinfo:
        storage.receive_crop(harvested_crop)
    assert "Storage.acceptable_crops is not populated" in str(excinfo.value)


def test_process_degradations(storage: Storage):
    """
    Test the process_degradations method of the Storage class.
    """
    pass


def test_give_feed(storage: Storage):
    """
    Test the give_feed method of the Storage class.
    """
    pass


def test_calculate_dry_matter_loss_to_gas(storage: Storage):
    """
    Test the calculate_dry_matter_loss_to_gas method of the Storage class.
    """
    pass


def test_calculate_dry_matter_loss_to_effluent(storage: Storage):
    """
    Test the calculate_dry_matter_loss_to_effluent method of the Storage class.
    """
    pass


def test_calculate_protein_degradation(storage: Storage):
    """
    Test the calculate_protein_degradation method of the Storage class.
    """
    pass


def test_calculate_heat_generated(storage: Storage):
    """
    Test the calculate_heat_generated method of the Storage class.
    """
    pass


def test_calculate_bale_density(storage: Storage):
    """
    Test the calculate_bale_density method of the Storage class.
    """
    pass


def test_recalculate_nutrient_fractions(storage: Storage):
    """
    Test the recalculate_nutrient_fractions method of the Storage class.
    """
    pass
