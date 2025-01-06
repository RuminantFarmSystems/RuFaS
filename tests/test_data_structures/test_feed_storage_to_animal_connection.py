import pytest

from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization,
    FeedComponentType,
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
)


@pytest.mark.parametrize(
    "category, expected",
    [
        ("Animal Protein", FeedCategorization.ANIMAL_PROTEIN),
        ("Calf Liquid Feed", FeedCategorization.CALF_LIQUID_FEED),
        ("Grain Crop Forage", FeedCategorization.GRAIN_CROP_FORAGE),
    ]
)
def test_feed_categorization(category: str, expected: FeedCategorization) -> None:
    """Tests that FeedCategorization enum works correctly."""
    actual = FeedCategorization(category)

    assert actual == expected



