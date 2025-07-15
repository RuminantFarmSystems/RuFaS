from copy import deepcopy
from dataclasses import replace
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeedStorage, PurchasedFeed
from RUFAS.data_structures.feed_storage_to_animal_connection import NASEMFeed
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


@pytest.fixture
def purchased_feed() -> PurchasedFeed:
    return PurchasedFeed(rufas_id=1, dry_matter_mass=100, storage_time=date(2024, 6, 1))


@pytest.fixture
def purchased_feed_storage() -> PurchasedFeedStorage:
    return PurchasedFeedStorage()


@pytest.fixture
def time() -> RufasTime:
    return RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2025, 3, 4))


@pytest.mark.parametrize(
    "initial_mass, mass_removed, expected", [(100.0, 50.0, 50.0), (100.0, 100.0, 0.0), (100.0, 0.0, 100.0)]
)
def test_remove_dry_matter_mass(
    purchased_feed: PurchasedFeed, initial_mass: float, mass_removed: float, expected: float
) -> None:
    """Test that dry matter mass can be removed from a feed."""
    purchased_feed.dry_matter_mass = initial_mass

    purchased_feed.remove_dry_matter_mass(mass_removed)

    assert purchased_feed.dry_matter_mass == expected


def test_receive_feed(purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed) -> None:
    """Test that a feed can be received by the storage."""
    purchased_feed_storage.receive_feed(purchased_feed)

    assert purchased_feed_storage.stored == [purchased_feed]


def test_remove_empty_crops(purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed) -> None:
    """Test that empty feeds can be removed from the storage."""
    purchased_feed.dry_matter_mass = 0.0
    purchased_feed_storage.stored = [purchased_feed]

    purchased_feed_storage.remove_empty_crops()

    assert purchased_feed_storage.stored == []


@pytest.mark.parametrize("mass, num_feeds, expected", [(100.0, 3, 300.0), (50.0, 1, 50.0), (0.0, 1, 0.0)])
def test_report_stored_purchased_feeds(
    purchased_feed_storage: PurchasedFeedStorage,
    purchased_feed: PurchasedFeed,
    time: RufasTime,
    mocker: MockerFixture,
    mass: float,
    num_feeds: int,
    expected: float,
) -> None:
    """Test that the storage can report the stored feeds."""
    expected_info_map = {
        "class": "PurchasedFeedStorage",
        "function": "report_stored_purchased_feeds",
        "simulation_day": (expected_sim_day := 3),
        "units": MeasurementUnits.KILOGRAMS,
        "rufas_id": 1,
        "mass": expected,
    }
    mocker.patch.object(RufasTime, "simulation_day", new_callable=mocker.PropertyMock, return_value=expected_sim_day)
    stored_feeds = [replace(purchased_feed, dry_matter_mass=mass) for _ in range(num_feeds)]
    purchased_feed_storage.stored = stored_feeds
    expected_call = mocker.call("stored_feed_1", expected, expected_info_map)
    add_var = mocker.patch.object(purchased_feed_storage._om, "add_variable")

    purchased_feed_storage.report_stored_purchased_feeds(time)

    assert add_var.call_args_list == [expected_call]


@pytest.mark.parametrize(
    "feed_values, expected",
    [
        ([(1, 100), (2, 50), (1, 50)], {1: 150.0, 2: 50.0}),
        ([], {}),
        ([(1, 75.0), (2, 100.0), (3, 50.0)], {1: 75.0, 2: 100.0, 3: 50.0}),
    ],
)
def test_create_consolidated_feed_report(
    purchased_feed_storage: PurchasedFeedStorage,
    purchased_feed: PurchasedFeed,
    feed_values: list[tuple[int, float]],
    expected: dict[int, float],
) -> None:
    """Test that a consolidated feed report can be created."""
    purchased_feed_storage.stored = [
        replace(purchased_feed, rufas_id=rufas_id, dry_matter_mass=mass) for rufas_id, mass in feed_values
    ]

    report = purchased_feed_storage.create_consolidated_feed_report()

    assert report == expected


def test_project_shrinkage(purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed) -> None:
    """Test that project_shrinkage applies shrink when days_interval > 3 and does not mutate original."""
    purchased_feed.dry_matter_mass = 10.0
    feed_info = MagicMock(NASEMFeed)
    feed_info.rufas_id = 1
    feed_info.shrink_factor = 0.1
    available_feeds = [feed_info]
    purchased_feed_storage.stored = [purchased_feed]
    original_stored = deepcopy(purchased_feed_storage.stored)

    result = purchased_feed_storage.project_shrinkage(days_interval=4, available_feeds=available_feeds)

    assert result[0].dry_matter_mass == 9.0
    assert purchased_feed_storage.stored[0].dry_matter_mass == original_stored[0].dry_matter_mass


def test_project_shrinkage_no_shrink(
    purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed
) -> None:
    """Test that project_shrinkage does not apply shrink when days_interval ≤ 3."""
    purchased_feed.dry_matter_mass = 10.0
    feed_info = MagicMock(NASEMFeed)
    feed_info.rufas_id = 1
    feed_info.shrink_factor = 0.1
    available_feeds = [feed_info]
    purchased_feed_storage.stored = [purchased_feed]

    result = purchased_feed_storage.project_shrinkage(days_interval=3, available_feeds=available_feeds)

    assert result[0].dry_matter_mass == 10.0


def test_project_shrinkage_error(purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed) -> None:
    """Test that project_shrinkage raises ValueError when feed_info is missing."""
    purchased_feed.dry_matter_mass = 10.0
    missing_feed_info = MagicMock(NASEMFeed)
    missing_feed_info.rufas_id = 16
    missing_feed_info.shrink_factor = 0.1
    available_feeds = [missing_feed_info]
    purchased_feed_storage.stored = [purchased_feed]

    with pytest.raises(ValueError):
        purchased_feed_storage.project_shrinkage(days_interval=5, available_feeds=available_feeds)


def test_process_shrinkage(
    purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed, time: RufasTime
) -> None:
    """Test the function process_shrinkage()."""
    purchased_feed.dry_matter_mass = 10.0
    feed = MagicMock(NASEMFeed)
    feed.rufas_id = 1
    feed.shrink_factor = 0.1
    available_feed = [feed]
    purchased_feed_storage.stored = [purchased_feed]

    purchased_feed_storage.process_shrinkage(time, available_feed)

    assert purchased_feed_storage.stored[0].dry_matter_mass == 9.0


def test_process_shrinkage_no_shrink(
    purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed
) -> None:
    """Test the function process_shrinkage()."""
    purchased_feed.dry_matter_mass = 10.0
    feed = MagicMock(NASEMFeed)
    feed.rufas_id = 1
    feed.shrink_factor = 0.1
    available_feed = [feed]
    purchased_feed_storage.stored = [purchased_feed]
    time = RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2024, 6, 2))

    purchased_feed_storage.process_shrinkage(time, available_feed)

    assert purchased_feed_storage.stored[0].dry_matter_mass == 10.0


def test_process_shrinkage_error(purchased_feed_storage: PurchasedFeedStorage, purchased_feed: PurchasedFeed) -> None:
    """Test the function process_shrinkage()."""
    purchased_feed.dry_matter_mass = 10.0
    feed = MagicMock(NASEMFeed)
    feed.rufas_id = 16
    feed.shrink_factor = 0.1
    available_feed = [feed]
    purchased_feed_storage.stored = [purchased_feed]
    time = RufasTime(datetime(2022, 12, 20), datetime(2025, 3, 7), datetime(2024, 6, 2))

    with pytest.raises(ValueError):
        purchased_feed_storage.process_shrinkage(time, available_feed)
