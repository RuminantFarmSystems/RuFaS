from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization,
    FeedComponentType,
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
)


def test_feed_categorization() -> None:
    """Tests that FeedCategorization enum works correctly."""

    assert FeedCategorization.ANIMAL_PROTEIN.value == "Animal Protein"
    assert FeedCategorization.BY_PRODUCT_OTHER.value == "By-Product/Other"
    assert FeedCategorization.CALF_LIQUID_FEED.value == "Calf Liquid Feed"
    assert FeedCategorization.ENERGY_SOURCE.value == "Energy Source"
    assert FeedCategorization.FAT_SUPPLEMENT.value == "Fat Supplement"
    assert FeedCategorization.FATTY_ACID_SUPPLEMENT.value == "Fatty Acid Supplement"
    assert FeedCategorization.GRAIN_CROP_FORAGE.value == "Grain Crop Forage"
    assert FeedCategorization.GRASS_LEGUME_FORAGE.value == "Grass/Legume Forage"
    assert FeedCategorization.PASTURE.value == "Pasture"
    assert FeedCategorization.PLANT_PROTEIN.value == "Plant Protein"
    assert FeedCategorization.VITAMIN_MINERAL.value == "Vitamin/Mineral"


def test_feed_commponent_type() -> None:
    """Tests that FeedComponentType enum works correctly."""
    
    assert FeedComponentType.AMINOACIDS.value == "Aminoacids"
    assert FeedComponentType.FORAGE.value == "Forage"
    assert FeedComponentType.CONC.value == "Conc"
    assert FeedComponentType.MILK.value == "Milk"
    assert FeedComponentType.MINERAL.value == "Mineral"
    assert FeedComponentType.VITAMINS.value == "Vitamins"
    assert FeedComponentType.STARTER.value == "Starter"
    assert FeedComponentType.NO.value == "No"


def test_nutrient_standard() -> None:
    """Tests that NutrientStandard enum works correctly."""

    assert NutrientStandard.NASEM.value == "NASEM"
    assert NutrientStandard.NRC.value == "NRC"
