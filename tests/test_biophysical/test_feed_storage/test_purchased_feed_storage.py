from dataclasses import replace
from datetime import date, datetime

from mock import MagicMock, call
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.feed_storage.purchased_feed_storage import PurchasedFeedStorage, PurchasedFeed
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


@pytest.fixture
def purchased_feed() -> PurchasedFeed:
    return PurchasedFeed(rufas_id=1, dry_matter_mass=100, storage_time=date(2024, 6, 1))


@pytest.fixture
def mock_available_feeds() -> list[Feed]:
    feed_1, feed_2, feed_3, feed_4, feed_5 = (MagicMock(auto_spec=Feed) for _ in range(5))
    feed_1.rufas_id, feed_2.rufas_id, feed_3.rufas_id, feed_4.rufas_id, feed_5.rufas_id = 1, 2, 3, 4, 5
    feed_1.buffer, feed_2.buffer, feed_3.buffer, feed_4.buffer, feed_5.buffer = 1, 2, 3, 4, 5
    return [feed_1, feed_2, feed_3, feed_4, feed_5]


@pytest.fixture
def purchased_feed_storage(mock_available_feeds: list[Feed]) -> PurchasedFeedStorage:
    return PurchasedFeedStorage(available_feeds=mock_available_feeds)


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
    mocker: MockerFixture,
    mass: float,
    num_feeds: int,
    expected: float,
    time: RufasTime,
) -> None:
    """Test that the storage can report the stored feeds."""
    mock_time = time

    expected_info_map = {
        "class": "PurchasedFeedStorage",
        "function": "report_stored_purchased_feeds",
        "simulation_day": time.simulation_day,
        "units": MeasurementUnits.KILOGRAMS,
        "suffix": "mock_suffix",
    }

    stored_feeds = [replace(purchased_feed, dry_matter_mass=mass) for _ in range(num_feeds)]
    purchased_feed_storage.stored = stored_feeds

    add_var = mocker.patch.object(purchased_feed_storage._om, "add_variable")

    purchased_feed_storage.report_stored_purchased_feeds(mock_time.simulation_day, "mock_suffix")

    assert call("stored_feed_1", expected, expected_info_map) in add_var.call_args_list


@pytest.mark.parametrize(
    "feed_values, expected",
    [
        (
            [(1, 100), (2, 50), (1, 50)],
            {1: 150.0, 2: 50.0, 3: 0.0, 4: 0.0, 5: 0.0},
        ),
        (
            [],
            {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
        ),
        (
            [(1, 75.0), (2, 100.0), (3, 50.0)],
            {1: 75.0, 2: 100.0, 3: 50.0, 4: 0.0, 5: 0.0},
        ),
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
