import pytest
import copy
from pytest_mock import MockerFixture
from unittest.mock import call
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager
from .sample_crop_data import sample_crop_data

om = OutputManager()


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


@pytest.mark.parametrize(
    "loss,percentage,expected_loss",
    [
        (20.0, 5.0, 40.0),
        (15.0, 6.0, 30.0),
        (0.0, 0.0, 0.0),
    ],
)
def test_process_degradations(
    storage: Storage, mocker: MockerFixture, loss: float, percentage: float, expected_loss: float
) -> None:
    """
    Test the process_degradations method of the Storage class.
    """
    mock_conditions = mocker.MagicMock(autospec=CurrentDayConditions)
    mock_time = mocker.MagicMock(autospec=Time)
    mock_first_crop = mocker.MagicMock(autospec=HarvestedCrop)
    mock_second_crop = mocker.MagicMock(autospec=HarvestedCrop)
    storage.stored = [mock_first_crop, mock_second_crop]
    mock_dry_matter_loss = mocker.patch.object(storage, "calculate_dry_matter_loss_to_gas", return_value=loss)
    mock_recalc_percentage = mocker.patch.object(storage, "recalculate_nutrient_percentage", return_value=percentage)
    mock_set_mass = mocker.patch.object(storage, "set_mass_attributes_after_loss")
    mock_record = mocker.patch.object(storage, "record_stored_crops")

    storage.process_degradations(mock_conditions, mock_time)

    expected_dry_mass_loss_calls = [
        call(mock_first_crop, mock_conditions, mock_time),
        call(mock_second_crop, mock_conditions, mock_time),
    ]
    expected_recalculate_percentage_call_count = 6
    expected_set_mass_calls = [call(mock_first_crop, loss), call(mock_second_crop, loss)]

    mock_dry_matter_loss.assert_has_calls(expected_dry_mass_loss_calls)
    assert mock_recalc_percentage.call_count == expected_recalculate_percentage_call_count
    mock_set_mass.assert_has_calls(expected_set_mass_calls)
    mock_record.assert_called_once_with(expected_loss)
    mock_first_crop.crude_protein_percent = percentage
    mock_first_crop.adf = percentage
    mock_first_crop.ndf = percentage
    mock_second_crop.crude_protein_percent = percentage
    mock_second_crop.adf = percentage
    mock_second_crop.ndf = percentage


def test_give_feed(storage: Storage) -> None:
    """
    Test the give_feed method of the Storage class.
    """
    pass


@pytest.mark.parametrize(
    "loss,fresh,percentage,expected_fresh,expected_percentage",
    [
        (50.0, 1000.0, 15.0, 950.0, 10.526316),
        (200.0, 500.0, 50.0, 300.0, 16.666667),
        (150.0, 150.0, 100.0, 0.0, 0.0),
        (0.0, 200.0, 10.0, 200.0, 10.0),
    ],
)
def test_set_mass_attributes(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    loss: float,
    fresh: float,
    percentage: float,
    expected_fresh: float,
    expected_percentage: float,
) -> None:
    """Test set_mass_attributes method of Storage class."""
    harvested_crop.fresh_mass = fresh
    harvested_crop.dry_matter_percentage = percentage

    storage.set_mass_attributes_after_loss(harvested_crop, loss)

    assert harvested_crop.fresh_mass == expected_fresh
    assert pytest.approx(harvested_crop.dry_matter_percentage) == expected_percentage


@pytest.mark.parametrize("loss", (100.0, 0.0, 50.0))
def test_record_stored_crops(storage: Storage, mocker: MockerFixture, loss: float) -> None:
    """Test record_stored_crops method of Storage class."""
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage.record_stored_crops.__name__,
        "units": "kg",
    }
    mock_stored_mass = mocker.patch(
        "RUFAS.routines.feed_storage.storage.Storage.stored_mass", new_callable=mocker.PropertyMock
    )
    mock_total_amount = mocker.patch.object(storage, "_get_total_nutritive_amount")
    mock_add_var = mocker.patch.object(om, "add_variable")
    expected_get_total_amount_call_count = 9
    expected_add_var_call_count = 12

    storage.record_stored_crops(loss)

    mock_stored_mass.assert_called_once()
    assert mock_total_amount.call_count == expected_get_total_amount_call_count
    assert mock_add_var.call_count == expected_add_var_call_count
    assert call("gaseous_dry_matter_loss", loss, expected_info_map) in mock_add_var.call_args_list


@pytest.mark.parametrize(
    "nutrient,dry_mass,percentages,expected",
    [
        ("crude_protein_percent", 100, [10.0, 20.0, 30.0], 60.0),
        ("adf", 45.0, [3.0, 0.0, 5.3], 3.735),
        ("ndf", 60.0, [0.0, 0.0, 0.0], 0.0),
    ]
)
def test_get_total_nutritive_amount(storage: Storage, mocker: MockerFixture, harvested_crop: HarvestedCrop, nutrient: str, dry_mass: float, percentages: list[float], expected: float) -> None:
    """Test _get_total_nutritive_amount in Storage class."""
    storage.stored = [harvested_crop] * len(percentages)
    mock_dry_matter_mass = mocker.patch("RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass", new_callable=PropertyMock, return_value=dry_mass)
    mock_getattr = mocker.patch("builtins.getattr", side_effect=percentages)
    expected_getattr_calls = [call(crop, nutrient) for crop in storage.stored]

    actual = stored._get_total_nutritive_amount(nutrient)

    assert actual == expected


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
    storage: Storage,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    dry_matter: float,
    percentage: float,
    category: CropCategory,
    temp: float,
    expected: float,
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Sileage."""
    mocker.patch(
        "RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_matter,
    )
    harvested_crop.dry_matter_percentage = percentage
    harvested_crop.category = category
    mock_conditions = mocker.MagicMock(autospec=CurrentDayConditions)
    mock_conditions.mean_air_temperature = temp
    mock_time = mocker.MagicMock(autospec=Time)

    actual = storage.calculate_dry_matter_loss_to_gas(harvested_crop, mock_conditions, mock_time)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("dry_matter,expected", [(0.0, 540.0), (90.0, 144.0), (75.0, 210.0)])
def test_calculate_bale_density(storage: Storage, dry_matter: float, expected: float) -> None:
    """
    Test the calculate_bale_density method of the Storage class.
    """
    actual = storage.calculate_bale_density(dry_matter)

    assert actual == expected


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
def test_recalculate_nutrient_percentage(
    storage: Storage,
    nutrients: float,
    loss_coefficient: float,
    dry_matter_loss: float,
    dry_matter: float,
    expected: float,
) -> None:
    """
    Test the recalculate_nutrient_percentage method of the Storage class.
    """
    actual = storage.recalculate_nutrient_percentage(nutrients, loss_coefficient, dry_matter_loss, dry_matter)

    assert pytest.approx(actual) == expected
