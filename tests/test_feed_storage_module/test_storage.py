import pytest
from pytest_mock import MockerFixture
from unittest.mock import call
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.feed_storage.storage import Storage
from RUFAS.routines.feed_storage.harvested_crop import HarvestedCrop
from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather
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
    expected_info_map = {
        "class": storage.__class__.__name__,
        "function": storage.process_degradations.__name__,
        "units": MeasurementUnits.KILOGRAMS,
    }
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_conditions = [mocker.MagicMock(autospec=CurrentDayConditions)] * 3
    mock_time = mocker.MagicMock(autospec=Time)
    mock_first_crop = mocker.MagicMock(autospec=HarvestedCrop)
    mock_second_crop = mocker.MagicMock(autospec=HarvestedCrop)
    storage.stored = [mock_first_crop, mock_second_crop]
    mock_get_conditions = mocker.patch.object(storage, "_get_conditions", return_value=mock_conditions)
    mock_dry_matter_loss = mocker.patch.object(storage, "calculate_dry_matter_loss_to_gas", return_value=loss)
    mock_recalc_percentage = mocker.patch.object(storage, "recalculate_nutrient_percentage", return_value=percentage)
    mock_add_var = mocker.patch.object(om, "add_variable")
    mock_deepcopy = mocker.patch("RUFAS.routines.feed_storage.storage.copy.deepcopy", return_value=mock_time)
    mock_reset_mass = mocker.patch.object(storage, "reset_mass_attributes_after_loss")
    mock_record = mocker.patch.object(storage, "record_stored_crops")
    expected_get_conditions_calls = [
        call(mock_first_crop.last_time_degraded, mock_time, mock_weather),
        call(mock_second_crop.last_time_degraded, mock_time, mock_weather),
    ]
    expected_dry_mass_loss_calls = [
        call(mock_first_crop, mock_conditions),
        call(mock_second_crop, mock_conditions),
    ]

    storage.process_degradations(mock_weather, mock_time)

    expected_recalculate_percentage_call_count = len(storage.stored) * 4
    expected_reset_mass_calls = [call(mock_first_crop, loss, 0.0), call(mock_second_crop, loss, 0.0)]

    mock_get_conditions.assert_has_calls(expected_get_conditions_calls)
    mock_dry_matter_loss.assert_has_calls(expected_dry_mass_loss_calls)
    assert mock_recalc_percentage.call_count == expected_recalculate_percentage_call_count
    mock_reset_mass.assert_has_calls(expected_reset_mass_calls)
    mock_add_var.assert_called_once_with("gaseous_dry_matter_loss", loss * len(storage.stored), expected_info_map)
    mock_record.assert_called_once()
    assert mock_first_crop.crude_protein_percent == percentage
    assert mock_first_crop.adf == percentage
    assert mock_first_crop.ndf == percentage
    assert mock_first_crop.sugar == percentage
    assert mock_second_crop.crude_protein_percent == percentage
    assert mock_second_crop.adf == percentage
    assert mock_second_crop.ndf == percentage
    assert mock_second_crop.sugar == percentage
    assert mock_deepcopy.call_count == 2
    assert mock_first_crop.last_time_degraded == mock_second_crop.last_time_degraded == mock_time


@pytest.mark.parametrize(
    "dry_loss,water_loss,fresh,percentage,expected_fresh,expected_percentage",
    [
        (50.0, 0.0, 1000.0, 15.0, 950.0, 10.526316),
        (200.0, 50.0, 500.0, 50.0, 250.0, 20.0),
        (150.0, 0.0, 150.0, 100.0, 0.0, 0.0),
        (0.0, 0.0, 200.0, 10.0, 200.0, 10.0),
        (0.0, 100.0, 1000.0, 10.0, 900.0, 11.11111),
    ],
)
def test_reset_mass_attributes(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    dry_loss: float,
    water_loss: float,
    fresh: float,
    percentage: float,
    expected_fresh: float,
    expected_percentage: float,
) -> None:
    """Test reset_mass_attributes method of Storage class."""
    harvested_crop.fresh_mass = fresh
    harvested_crop.dry_matter_percentage = percentage

    storage.reset_mass_attributes_after_loss(harvested_crop, dry_loss, water_loss)

    assert harvested_crop.fresh_mass == expected_fresh
    assert pytest.approx(harvested_crop.dry_matter_percentage) == expected_percentage


def test_record_stored_crops(storage: Storage, mocker: MockerFixture) -> None:
    """Test record_stored_crops method of Storage class."""
    mock_stored_mass = mocker.patch(
        "RUFAS.routines.feed_storage.storage.Storage.stored_mass", new_callable=mocker.PropertyMock
    )
    mock_total_amount = mocker.patch.object(storage, "_get_total_nutritive_amount")
    mock_add_var = mocker.patch.object(om, "add_variable")
    expected_get_total_amount_call_count = 9
    expected_add_var_call_count = 11

    storage.record_stored_crops()

    mock_stored_mass.assert_called_once()
    assert mock_total_amount.call_count == expected_get_total_amount_call_count
    assert mock_add_var.call_count == expected_add_var_call_count


@pytest.mark.parametrize(
    "nutrient,dry_mass,percentages,expected",
    [
        ("crude_protein_percent", 100, [10.0, 20.0, 30.0], 60.0),
        ("adf", 45.0, [3.0, 0.0, 5.3], 3.735),
        ("ndf", 60.0, [0.0, 0.0, 0.0], 0.0),
    ],
)
def test_get_total_nutritive_amount(
    storage: Storage,
    mocker: MockerFixture,
    harvested_crop: HarvestedCrop,
    nutrient: str,
    dry_mass: float,
    percentages: list[float],
    expected: float,
) -> None:
    """Test _get_total_nutritive_amount in Storage class."""
    storage.stored = [harvested_crop] * len(percentages)
    mock_dry_matter_mass = mocker.patch(
        "RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_mass,
    )
    mock_getattr = mocker.patch("RUFAS.routines.feed_storage.storage.getattr", side_effect=percentages)
    expected_getattr_calls = [call(crop, nutrient) for crop in storage.stored]

    actual = storage._get_total_nutritive_amount(nutrient)

    assert pytest.approx(actual) == expected
    assert mock_dry_matter_mass.call_count == len(percentages)
    mock_getattr.assert_has_calls(expected_getattr_calls)


@pytest.mark.parametrize(
    "dry_matter,percentage,category,temps,expected",
    [
        (100.0, 25.0, CropCategory.ALFALFA, [20.0] * 3, 4.286303394879),
        (40.0, 20.0, CropCategory.ALFALFA, [6.0, 4.0, 6.0], 0.624),
        (150.0, 19.0, CropCategory.ALFALFA, [10.0] * 4, 0.0),
        (200.0, 23.0, CropCategory.ALFALFA, [46.0, 44.0, 46.0], 2.9016),
        (140.0, 15.0, CropCategory.CORN, [30.0, 28.0, 29.0], 1.2096),
        (80.0, 17.0, CropCategory.CORN, [30.0] * 20, 2.019438),
        (55.0, 66.0, CropCategory.GRASS, [25.0] * 2, 0.0),
        (120.0, 4.0, CropCategory.SMALL_GRAIN, [15.0], 0.0),
        (100.0, 24.0, CropCategory.GRASS, [], 0.0),
    ],
)
def test_calculate_dry_matter_loss_to_gas(
    storage: Storage,
    harvested_crop: HarvestedCrop,
    mocker: MockerFixture,
    dry_matter: float,
    percentage: float,
    category: CropCategory,
    temps: list[float],
    expected: float,
) -> None:
    """Tests calculate_dry_matter_loss_to_gas in Storage."""
    mocker.patch(
        "RUFAS.routines.feed_storage.harvested_crop.HarvestedCrop.dry_matter_mass",
        new_callable=mocker.PropertyMock,
        return_value=dry_matter,
    )
    harvested_crop.dry_matter_percentage = percentage
    harvested_crop.category = category

    mock_conditions = []
    for temp in temps:
        condition = mocker.MagicMock(autospec=CurrentDayConditions)
        condition.mean_air_temperature = temp
        mock_conditions.append(condition)

    actual = storage.calculate_dry_matter_loss_to_gas(harvested_crop, mock_conditions)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("curr_day,last_day,expected_offset", [(1, 1, None), (13, 30, None), (10, 9, 0), (100, 1, -98)])
def test_get_conditions(
    storage: Storage,
    mocker: MockerFixture,
    curr_day: int,
    last_day: int,
    expected_offset: int,
) -> None:
    """Tests _get_conditions in Storage."""
    mock_curr_time = mocker.MagicMock(autospec=Time)
    mock_curr_time.simulation_day = curr_day
    mock_last_degradation_time = mocker.MagicMock(autospec=Time)
    mock_last_degradation_time.simulation_day = last_day
    returned_conditions = [mocker.MagicMock(autospec=CurrentDayConditions)]
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_weather.get_conditions_series.return_value = returned_conditions

    actual = storage._get_conditions(mock_last_degradation_time, mock_curr_time, mock_weather)

    if expected_offset is None:
        assert actual == []
        mock_weather.get_conditions_series.assert_not_called()
    else:
        assert actual == returned_conditions
        mock_weather.get_conditions_series.assert_called_once_with(mock_curr_time, expected_offset, 0)


@pytest.mark.parametrize("dry_matter,expected", [(0.0, 540.0), (90.0, 144.0), (75.0, 210.0)])
def test_calculate_bale_density(storage: Storage, dry_matter: float, expected: float) -> None:
    """
    Test the calculate_bale_density method of the Storage class.
    """
    actual = storage.calculate_bale_density(dry_matter)

    assert actual == expected


@pytest.mark.parametrize(
    "nutrients,loss_coefficient,dry_matter_loss,dry_matter,expected,warned",
    [
        (8.0, 0.4, 20.0, 100.0, 0.0, True),
        (4.0, 0.17, 21.0, 150.0, 1.88372, False),
        (6.0, 0.0, 10.0, 100.0, 6.666667, False),
        (0.5, 0.7, 100.0, 200.0, 0.0, True),
        (3.4, 0.8, 0.0, 200.0, 3.4, False),
        (5.8, 0.08, 100.0, 100.0, 0.0, False),
    ],
)
def test_recalculate_nutrient_percentage(
    storage: Storage,
    mocker: MockerFixture,
    nutrients: float,
    loss_coefficient: float,
    dry_matter_loss: float,
    dry_matter: float,
    expected: float,
    warned: bool,
) -> None:
    """
    Test the recalculate_nutrient_percentage method of the Storage class.
    """
    mock_warn = mocker.patch.object(om, "add_warning")
    actual = storage.recalculate_nutrient_percentage(nutrients, loss_coefficient, dry_matter_loss, dry_matter)

    assert pytest.approx(actual) == expected
    if warned:
        mock_warn.assert_called_once()
    else:
        mock_warn.assert_not_called()
