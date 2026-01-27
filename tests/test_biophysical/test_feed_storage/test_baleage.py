from typing import Any
from unittest.mock import MagicMock

import pytest
from dataclasses import replace
from datetime import datetime
from pytest_mock import MockerFixture

from RUFAS.biophysical.feed_storage.baleage import Baleage, INITIAL_LOSS_PERIOD
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

from .sample_crop_data import sample_crop_data


@pytest.fixture
def mock_baleage_config() -> dict[str, Any]:
    """Pytest fixture to create a mock baleage configuration dictionary."""
    return {
        "name": "baleage",
        "rufas_id": 1,
        "field_names": ["field_1"],
        "crop_name": "corn",
        "initial_storage_dry_matter": 45.0,
        "post_wilting_moisture_percentage": 40.0,
        "bale_density": 200.0,
        "capacity": 1_000_000.0,
    }


@pytest.fixture
def baleage(mock_baleage_config: dict[str, Any]) -> Baleage:
    """
    Pytest fixture to create a Baleage instance for testing.

    Returns
    -------
    Baleage
        An instance of the Baleage class.

    """
    return Baleage(config=mock_baleage_config)


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
def weather(mocker: MockerFixture) -> Weather:
    """
    Pytest fixture to create a Weather instance for testing.

    Returns
    -------
    Weather
        An instance of the Weather class.

    """
    mocker.patch.object(Weather, "__init__", return_value=None)
    return Weather({}, MagicMock(auto_spec=RufasTime))


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


def test_process_degradations(
    baleage: Baleage,
    harvested_crop: HarvestedCrop,
    time: RufasTime,
    weather: Weather,
    mocker: MockerFixture,
) -> None:
    """Tests process_degradations in Hay."""
    baleage.stored = [harvested_crop]
    baleage.post_wilting_moisture_percentage = 45
    mock_moisture_loss = mocker.patch.object(baleage, "_process_moisture_loss")
    mock_storage_process_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.process_degradations"
    )

    baleage.process_degradations(weather, time)

    mock_moisture_loss.assert_called_once_with(time, INITIAL_LOSS_PERIOD, 45)
    mock_storage_process_degradations.assert_called_once_with(weather, time)


def test_project_degradations(
    baleage: Baleage,
    harvested_crop: HarvestedCrop,
    weather: Weather,
    time: RufasTime,
    mocker: MockerFixture,
) -> None:
    """Tests project_degradations in Hay."""
    baleage.stored = [replace(harvested_crop, dry_matter_mass=1000.0) for _ in range(3)]
    baleage.post_wilting_moisture_percentage = 43.0
    crops_with_moisture_loss = [replace(crop, dry_matter_mass=900.0) for crop in baleage.stored]
    crops_with_all_loss = [replace(crop, dry_matter_mass=800.0) for crop in baleage.stored]
    project_moisture_loss = mocker.patch.object(
        baleage, "_project_moisture_loss", return_value=crops_with_moisture_loss
    )
    project_degradations = mocker.patch(
        "RUFAS.biophysical.feed_storage.storage.Storage.project_degradations", return_value=crops_with_all_loss
    )

    actual = baleage.project_degradations(baleage.stored, weather, time)

    assert actual == crops_with_all_loss
    project_moisture_loss.assert_called_once_with(baleage.stored, time, INITIAL_LOSS_PERIOD, 43.0)
    project_degradations.assert_called_once_with(crops_with_moisture_loss, weather, time)


def test_calculate_protein_loss(baleage: Baleage) -> None:
    """Tests calculate_protein_loss() in Baleage."""
    baleage.calculate_protein_loss()
