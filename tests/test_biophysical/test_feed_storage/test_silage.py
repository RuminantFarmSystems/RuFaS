import copy
from typing import Any
from unittest.mock import call
from dataclasses import replace
from datetime import date, datetime, timedelta
import pytest
from pytest_mock import MockerFixture

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.feed_storage.silage import Bag, Bunker, Pile, Silage
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .sample_crop_data import sample_crop_data


@pytest.fixture
def mock_silage_config() -> dict[str, str | float | list[str]]:
    return {
        "name": "silage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 500.0,
        "size": 1000.0,
        "capacity": 1_000_000.0,
    }


@pytest.fixture
def silage(mock_silage_config: dict[str, str | float | list[str]]) -> Silage:
    return Silage(config=mock_silage_config)


@pytest.fixture
def harvested_crop() -> HarvestedCrop:
    """
    Pytest fixture to create a HarvestedCrop instance for testing.

    Returns
    -------
    HarvestedCrop
        An instance of the HarvestedCrop class.
    """
    return HarvestedCrop(**sample_crop_data)


@pytest.fixture
def time() -> RufasTime:
    """
    Pytest fixture to create a RufasTime instance for testing.

    Returns
    -------
    RufasTime
        An instance of the RufasTime class.

    """
    return RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 3))


@pytest.fixture
def weather(mocker: MockerFixture, time: RufasTime) -> Weather:
    """Creates a Weather instance for testing."""
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, time)


@pytest.mark.parametrize("days_of_loss", [0, 10, 3])
def test_process_degradations(
    mocker: MockerFixture, silage: Silage, harvested_crop: HarvestedCrop, days_of_loss: int
) -> None:
    """Tests the implementation of process_degradations in the Silage class."""
    mock_weather = mocker.MagicMock(autospec=Weather)
    mock_time = mocker.MagicMock(autospec=RufasTime)
    mock_time.simulation_day = 15
    effluent_loss_days = mocker.patch.object(
        silage, "calculate_days_of_effluent_loss_to_process", return_value=days_of_loss
    )
    dry_loss = mocker.patch.object(silage, "calculate_dry_matter_loss_to_effluent", return_value=10.0)
    moisture_loss = mocker.patch.object(silage, "calculate_moisture_loss_to_effluent", return_value=20.0)
    npn_coefficient = mocker.patch.object(
        silage, "calculate_non_protein_nitrogen_after_effluent_loss", return_value=4.5
    )
    cp_coeffient = mocker.patch.object(silage, "calculate_crude_protein_after_effluent_loss", return_value=5.0)
    if days_of_loss:
        expected_mass_loss = {"dry_matter_loss": 20.0, "moisture_loss": 40.0}
    else:
        expected_mass_loss = {"dry_matter_loss": 0.0, "moisture_loss": 0.0}
    reset_attributes = mocker.patch.object(
        silage, "_calculate_mass_attributes_after_loss", return_value=expected_mass_loss
    )
    add_variable = mocker.patch.object(OutputManager, "add_variable")
    super_process_degradations = mocker.patch("RUFAS.biophysical.feed_storage.storage.Storage.process_degradations")
    second_crop = copy.deepcopy(harvested_crop)
    silage.stored = [harvested_crop, second_crop]
    expected_info_map = {
        "class": silage.__class__.__name__,
        "function": silage.process_degradations.__name__,
        "prefix": "Feed.Storage.Silage.silage",
        "units": MeasurementUnits.KILOGRAMS,
        "simulation_day": mock_time.simulation_day,
    }

    silage.process_degradations(mock_weather, mock_time)

    effluent_loss_days.assert_has_calls([call(harvested_crop, mock_time), call(second_crop, mock_time)])
    assert dry_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert moisture_loss.call_count == (len(silage.stored) if days_of_loss else 0)
    assert npn_coefficient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert cp_coeffient.call_count == (len(silage.stored) if days_of_loss else 0)
    assert reset_attributes.call_count == (len(silage.stored) if days_of_loss else 0)
    add_variable.assert_has_calls(
        [
            call("total_effluent_dry_matter_loss", expected_mass_loss["dry_matter_loss"], expected_info_map),
            call("total_effluent_moisture_loss", expected_mass_loss["moisture_loss"], expected_info_map),
        ]
    )
    super_process_degradations.assert_called_once_with(mock_weather, mock_time)


def test_project_degradations(
    silage: Silage,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    weather: Weather,
    mocker: MockerFixture,
) -> None:
    """Test that project_degradations functions as expected."""
    effluent_loss_values = {
        "dry_matter_mass": 800.0,
        "dry_matter_percentage": 14.0,
        "non_protein_nitrogen": 3.0,
        "crude_protein_percent": 5.0,
        "dry_matter_loss": 20.0,
        "moisture_loss": 20.0,
    }
    expected_loss_values = {
        "dry_matter_mass": 800.0,
        "dry_matter_percentage": 14.0,
        "non_protein_nitrogen": 3.0,
        "crude_protein_percent": 5.0,
    }
    silage.stored = [replace(harvested_crop) for _ in range(3)]
    degraded_crops = [replace(crop, **expected_loss_values) for crop in silage.stored]
    calc_effluent_loss = mocker.patch.object(
        silage, "_calculate_effluent_loss", side_effect=[copy.copy(effluent_loss_values) for _ in range(3)]
    )
    process_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.project_degradations", return_value=degraded_crops
    )

    actual = silage.project_degradations(silage.stored, weather, time)

    for crop in actual:
        assert crop.dry_matter_mass == expected_loss_values["dry_matter_mass"]
        assert pytest.approx(crop.dry_matter_percentage) == expected_loss_values["dry_matter_percentage"]
        assert crop.non_protein_nitrogen == expected_loss_values["non_protein_nitrogen"]
        assert crop.crude_protein_percent == expected_loss_values["crude_protein_percent"]
    calc_effluent_loss.assert_has_calls([mocker.call(crop, time) for crop in silage.stored])
    process_degradations.assert_called_once_with(degraded_crops, weather, time)


@pytest.mark.parametrize(
    "day_stored, last_day_processed, current, expected",
    [
        (1, 1, 6, 5),
        (1, 3, 3, 0),
        (40, 45, 50, 5),
        (40, 45, 55, 10),
        (10, 22, 25, 3),
    ],
)
def test_calculate_days_of_effluent_loss_to_process(
    silage: Silage,
    time: RufasTime,
    harvested_crop: HarvestedCrop,
    day_stored: int,
    last_day_processed: int,
    current: int,
    expected: int,
) -> None:
    """Tests calculate_days_of_effluent_loss_to_process in Silage."""
    storage_date = date(2024, 6, 1)
    harvested_crop.storage_time = storage_date + timedelta(days=day_stored - 1)
    harvested_crop.last_time_degraded = storage_date + timedelta(days=last_day_processed - 1)
    time.current_date = datetime(2024, 6, 1) + timedelta(days=current - 1)

    actual = silage.calculate_days_of_effluent_loss_to_process(harvested_crop, time)
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
    [(4.0, 25.0, 0.02, 1.63934426), (8.0, 50.0, 0.05, 5.15463917), (0.0, 3.6, 0.01, 0.0), (4.0, 20.0, 0.0, 4.0)],
)
def test_calculate_non_protein_nitrogen_after_effluent_loss(
    silage: Silage, npn: float, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_non_protein_nitrogen_loss_coefficient in Silage."""
    actual = silage.calculate_non_protein_nitrogen_after_effluent_loss(npn, cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "cp,loss_frac,expected", [(5.6, 0.033, 4.767322), (2.2, 0.04, 1.041667), (0.0, 0.05, 0.0), (8.7, 0.0, 8.7)]
)
def test_calculate_crude_protein_after_effluent_loss(
    silage: Silage, cp: float, loss_frac: float, expected: float
) -> None:
    """Tests calculate_crude_protein_loss_coefficient in Silage."""
    actual = silage.calculate_crude_protein_after_effluent_loss(cp, loss_frac)

    assert pytest.approx(actual) == expected


@pytest.fixture
def bunker(mock_silage_config: dict[str, str | float | list[str]]) -> Bunker:
    return Bunker(config=mock_silage_config)


@pytest.fixture
def pile(mock_silage_config: dict[str, str | float | list[str]]) -> Pile:
    return Pile(config=mock_silage_config)


@pytest.fixture
def bag(mock_silage_config: dict[str, str | float | list[str]]) -> Bag:
    return Bag(config=mock_silage_config)


def test_bag_init(mock_silage_config: dict[str, Any], mocker: MockerFixture) -> None:
    """Tests that the Bag class is initialized correctly."""
    mock_silage_init = mocker.patch("RUFAS.biophysical.feed_storage.silage.Silage.__init__")
    bag = Bag(config=mock_silage_config)
    assert bag.bag_size == mock_silage_config.get("size")
    mock_silage_init.assert_called_once_with(mock_silage_config)
