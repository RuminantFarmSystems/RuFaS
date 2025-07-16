import pytest
from pytest_mock import MockerFixture
from typing import Any

from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization,
    FeedComponentType,
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
)
from RUFAS.units import MeasurementUnits


@pytest.fixture
def mock_feed() -> dict[str, Any]:
    """Values of a mock Feed instance."""

    return {
        "rufas_id": 1,
        "Fd_Category": FeedCategorization.ENERGY_SOURCE,
        "feed_type": FeedComponentType.CONC,
        "DM": 90.0,
        "ash": 0.0,
        "CP": 0.11,
        "N_A": 0.12,
        "N_B": 0.13,
        "N_C": 0.14,
        "Kd": 0.15,
        "dRUP": 0.16,
        "ADICP": 0.17,
        "NDICP": 0.18,
        "ADF": 0.19,
        "NDF": 0.2,
        "lignin": 0.21,
        "starch": 0.22,
        "EE": 0.23,
        "calcium": 0.24,
        "phosphorus": 0.25,
        "magnesium": 0.26,
        "potassium": 0.27,
        "sodium": 0.28,
        "chlorine": 0.29,
        "sulfur": 0.30,
        "is_fat": False,
        "is_wetforage": False,
        "units": MeasurementUnits.KILOGRAMS,
        "limit": 0.31,
        "lower_limit": 0.0,
        "TDN": 0.33,
        "DE": 0.34,
        "amount_available": 0.35,
        "on_farm_cost": 0.36,
        "purchase_cost": 0.37,
    }


@pytest.fixture
def mock_NASEM_feed() -> dict[str, Any]:
    """Values of a mock NASEM feed instance."""

    return {
        "Name": "NASEM Feed",
        "RUP": 0.4,
        "sol_prot": 0.41,
        "NDF48": 0.42,
        "WSC": 0.43,
        "FA": 0.44,
        "DE_Base": 0.45,
        "copper": 0.46,
        "iron": 0.47,
        "manganese": 0.48,
        "zinc": 0.49,
        "molibdenum": 0.5,
        "chromium": 0.51,
        "cobalt": 0.52,
        "iodine": 0.53,
        "selenium": 0.54,
        "arginine": 0.55,
        "histidine": 0.56,
        "isoleucine": 0.57,
        "leucine": 0.58,
        "lysine": 0.59,
        "methionine": 0.6,
        "phenylalanine": 0.61,
        "threonine": 0.62,
        "triptophan": 0.63,
        "valine": 0.64,
        "C120_FA": 0.65,
        "C140_FA": 0.66,
        "C160_FA": 0.67,
        "C161_FA": 0.68,
        "C180_FA": 0.69,
        "C181t_FA": 0.7,
        "C181c_FA": 0.71,
        "C182_FA": 0.72,
        "C183_FA": 0.73,
        "otherFA_FA": 0.74,
        "NPN_source": 0.75,
        "starch_digested": 0.76,
        "FA_dig": 0.77,
        "P_inorg": 0.78,
        "P_org": 0.79,
        "B_Carotene": 0.8,
        "biotin": 0.81,
        "choline": 0.82,
        "niacin": 0.83,
        "Vit_A": 0.84,
        "Vit_D": 0.85,
        "Vit_E": 0.86,
        "Abs_calcium": 0.87,
        "Abs_phosphorus": 0.88,
        "Abs_sodium": 0.89,
        "Abs_chloride": 0.9,
        "Abs_potassium": 0.91,
        "Abs_copper": 0.92,
        "Abs_iron": 0.93,
        "Abs_magnesium": 0.94,
        "Abs_manganesum": 0.95,
        "Abs_zinc": 0.96,
        "buffer": 0.0,
    }


@pytest.fixture
def mock_NRC_feed() -> dict[str, Any]:
    """Values of a mock NRC feed instance."""

    return {"non_fiber_carb": 0.97, "PAF": 0.98, "buffer": 0.0}


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


def test_NASEM_feed(mock_feed: MockerFixture, mock_NASEM_feed: MockerFixture) -> None:
    """Test that NASEM feeds are initialized correctly."""
    nasem_feed = NASEMFeed(**mock_feed, **mock_NASEM_feed)

    assert nasem_feed.Name == "NASEM Feed"


def test_NRC_feed(mock_feed: MockerFixture, mock_NRC_feed: MockerFixture) -> None:
    """Test that NRC feeds are initialized correctly."""
    nrc_feed = NRCFeed(**mock_feed, **mock_NRC_feed)

    assert nrc_feed.non_fiber_carb == 0.97
