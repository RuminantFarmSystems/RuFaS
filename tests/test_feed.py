from pytest import fixture
from pytest_mock import MockerFixture

from RUFAS.routines import Feed


@fixture
def feed(mocker: MockerFixture) -> Feed:
    """Returns an uninitialized Feed object"""

    mocker.patch("RUFAS.routines.feed.Feed.__init__", return_value=None)
    return Feed(data=mocker.MagicMock(), nutrient_standard="NASEM")


def test_get_quality_specific_feed_costs(mocker: MockerFixture, feed: Feed) -> None:
    """Unit test for function get_quality_specific_feed_costs in file routines/feed/feed.py"""

    # Arrange
    unchanged_feed_ids = [2, 26]
    feed_ids_to_be_updated = [34, 52]
    input_feed_ids = unchanged_feed_ids + feed_ids_to_be_updated

    input_feed_id_to_quality_specific_feed_id_dict = {
        2: [2],
        26: [26],
        34: [36],
        52: [54],
    }
    mocker.patch.object(
        feed,
        "get_quality_specific_purchased_feed_ids",
        input_feed_id_to_quality_specific_feed_id_dict.__getitem__,
    )
    feed.feed_costs = {"2": 0.17, "26": 0.1, "34": 0.01, "52": 0.15}

    # Act
    updated_costs = feed.get_quality_specific_feed_costs(input_feed_ids)

    # Assert
    expected_updated_costs = {"2": 0.17, "26": 0.1, "36": 0.01, "54": 0.15}
    assert updated_costs == expected_updated_costs
