import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import FeedInRation, NutritionSupplyCalculator
from RUFAS.data_structures.feed_storage_animal_connection import Feed


@pytest.fixture
def feeds(mocker: MockerFixture) -> tuple[Feed, Feed, Feed]:
    """Mock feeds to be used for testing."""
    mocker.patch.object(Feed, "__init__", return_value=None)
    return [Feed(), Feed(), Feed()]


@pytest.mark.parametrize(
    "ee, feed_amounts, expected",
    [
        ((2.1, 1.0, 0.0), (10.0, 20.0, 0.5), 0.41),
        ((0.0, 0.0, 0.0), (20.0, 20.0, 20.0), 0.0),
        ((3.0, 3.0, 3.0), (10.0, 20.0, 15.0), 1.35),
    ]
)
def test_calculate_fat_content(feeds: tuple[Feed, Feed, Feed], ee: tuple[float, float, float], feed_amounts: tuple[float, float, float], expected: float) -> None:
    """Test that fat content of a ration is calculated correctly."""
    feeds[0].EE, feeds[1].EE, feeds[2].EE = ee
    feeds_in_ration = [
        FeedInRation(feed_amounts[0], feeds[0]),
        FeedInRation(feed_amounts[1], feeds[1]),
        FeedInRation(feed_amounts[2], feeds[2]),
    ]

    actual = NutritionSupplyCalculator._calculate_fat_content(feeds_in_ration)

    assert pytest.approx(actual) == expected
    