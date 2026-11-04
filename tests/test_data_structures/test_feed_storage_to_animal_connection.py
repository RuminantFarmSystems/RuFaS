from RUFAS.input_manager import InputManager
import pytest
from pytest_mock import MockerFixture
from typing import Any

from RUFAS.data_structures.feed_storage_to_animal_connection import (
    ON_FARM_TO_PURCHASED_PRICE_RATIO,
    AvailableFeedsBuilder,
    Feed,
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


@pytest.fixture
def valid_feed_config() -> dict[str, Any]:
    return {
        "feeds": [
            {"feed_type": 23},
            {"feed_type": 44},
        ],
        "rations": [
            {
                "animal_combination": "lac_cow",
                "feeds": [
                    {"feed_type": 23},
                    {"feed_type": 44},
                ],
            }
        ],
    }


@pytest.fixture
def feed_library() -> dict[int, dict[str, Any]]:
    return {
        23: {},
        44: {},
    }


def test_validate_feed_config_accepts_valid_config(
    valid_feed_config: dict[str, Any],
    feed_library: dict[int, dict[str, Any]],
) -> None:
    """Tests that no error is raised when all configured feed types are valid."""
    AvailableFeedsBuilder._validate_feed_config(
        valid_feed_config,
        feed_library,
        NutrientStandard.NASEM,
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


def test_NASEM_feed(mock_feed: MockerFixture, mock_NASEM_feed: MockerFixture) -> None:
    """Test that NASEM feeds are initialized correctly."""
    nasem_feed = NASEMFeed(**mock_feed, **mock_NASEM_feed)

    assert nasem_feed.Name == "NASEM Feed"


def test_NRC_feed(mock_feed: MockerFixture, mock_NRC_feed: MockerFixture) -> None:
    """Test that NRC feeds are initialized correctly."""
    nrc_feed = NRCFeed(**mock_feed, **mock_NRC_feed)

    assert nrc_feed.non_fiber_carb == 0.97


@pytest.mark.parametrize(
    "nutrient_standard, nutrient_fixture_name, expected_feed_type",
    [
        (NutrientStandard.NASEM, "mock_NASEM_feed", NASEMFeed),
        (NutrientStandard.NRC, "mock_NRC_feed", NRCFeed),
    ],
)
def test_setup_available_feeds(
    mocker: MockerFixture,
    request: pytest.FixtureRequest,
    mock_feed: dict[str, Any],
    nutrient_standard: NutrientStandard,
    nutrient_fixture_name: str,
    expected_feed_type: type[Feed],
) -> None:
    """Tests setup_available_feeds builds sorted feed objects using the selected nutrient standard."""
    # Arrange
    nutritive_properties = {
        **mock_feed,
        **request.getfixturevalue(nutrient_fixture_name),
    }
    nutritive_properties.pop("rufas_id")
    nutritive_properties.pop("amount_available")
    nutritive_properties.pop("on_farm_cost")
    nutritive_properties.pop("purchase_cost")
    nutritive_properties.pop("buffer")

    feed_library = {
        44: {**nutritive_properties},
        23: {**nutritive_properties},
    }
    feed_config = {
        "feeds": [
            {"feed_type": 44, "purchased_feed_cost": 0.20, "buffer": 1.5},
            {"feed_type": 23, "purchased_feed_cost": 0.10, "buffer": 2.5},
        ]
    }

    mock_process_feed_library = mocker.patch.object(
        AvailableFeedsBuilder,
        "_process_feed_library",
        return_value=feed_library,
    )
    mock_validate_feed_config = mocker.patch.object(
        AvailableFeedsBuilder,
        "_validate_feed_config",
    )

    # Act
    actual = AvailableFeedsBuilder.setup_available_feeds(feed_config, nutrient_standard)

    # Assert
    mock_process_feed_library.assert_called_once_with(nutrient_standard)
    mock_validate_feed_config.assert_called_once_with(feed_config, feed_library, nutrient_standard)

    assert [feed.rufas_id for feed in actual] == [23, 44]
    assert all(isinstance(feed, expected_feed_type) for feed in actual)

    assert actual[0].amount_available == 0.0
    assert actual[0].purchase_cost == 0.10
    assert actual[0].on_farm_cost == 0.10 * ON_FARM_TO_PURCHASED_PRICE_RATIO
    assert actual[0].buffer == 2.5

    assert actual[1].amount_available == 0.0
    assert actual[1].purchase_cost == 0.20
    assert actual[1].on_farm_cost == 0.20 * ON_FARM_TO_PURCHASED_PRICE_RATIO
    assert actual[1].buffer == 1.5


def test_validate_feed_config_raises_error_for_feed_missing_from_library(
    valid_feed_config: dict[str, Any],
    feed_library: dict[int, dict[str, Any]],
) -> None:
    """Tests that configured feeds must exist in the selected feed library."""
    valid_feed_config["feeds"].append({"feed_type": 50})

    with pytest.raises(
        ValueError,
        match=r"The following feed_type values are not present in the selected .* feed library: \[50\]\.",
    ):
        AvailableFeedsBuilder._validate_feed_config(
            valid_feed_config,
            feed_library,
            NutrientStandard.NASEM,
        )


def test_validate_feed_config_raises_error_for_duplicate_top_level_feed_types(
    valid_feed_config: dict[str, Any],
    feed_library: dict[int, dict[str, Any]],
) -> None:
    """Tests that duplicate top-level feed definitions are rejected."""
    valid_feed_config["feeds"].append({"feed_type": 23})

    with pytest.raises(
        ValueError,
        match=r"repeated feed_type entries in the top-level 'feeds' section: \[23\]\.",
    ):
        AvailableFeedsBuilder._validate_feed_config(
            valid_feed_config,
            feed_library,
            NutrientStandard.NASEM,
        )


def test_validate_feed_config_raises_error_for_duplicate_ration_feed_types(
    valid_feed_config: dict[str, Any],
    feed_library: dict[int, dict[str, Any]],
) -> None:
    """Tests that duplicate feed types within a ration are rejected."""
    valid_feed_config["rations"][0]["feeds"].append({"feed_type": 23})

    with pytest.raises(
        ValueError,
        match=r"repeated feed_type entries in the ration for animal_combination 'lac_cow': \[23\]\.",
    ):
        AvailableFeedsBuilder._validate_feed_config(
            valid_feed_config,
            feed_library,
            NutrientStandard.NASEM,
        )


def test_validate_feed_config_raises_error_for_ration_feed_missing_from_top_level_feeds(
    valid_feed_config: dict[str, Any],
    feed_library: dict[int, dict[str, Any]],
) -> None:
    """Tests that ration feeds must be defined in the top-level feeds section."""
    valid_feed_config["rations"][0]["feeds"].append({"feed_type": 50})

    with pytest.raises(
        ValueError,
        match=(
            r"ration feed_type entries that are not defined in the top-level 'feeds' section "
            r"for animal_combination 'lac_cow': \[50\]\."
        ),
    ):
        AvailableFeedsBuilder._validate_feed_config(
            valid_feed_config,
            feed_library,
            NutrientStandard.NASEM,
        )


@pytest.mark.parametrize(
    "values, expected",
    [
        ([23, 44, 50], set()),
        ([23, 44, 23], {23}),
        ([23, 44, 23, 44], {23, 44}),
        ([23, 23, 23], {23}),
        ([], set()),
    ],
)
def test_find_feed_repeats(
    values: list[int],
    expected: set[int],
) -> None:
    """Tests that repeated feed IDs are correctly identified."""
    actual = AvailableFeedsBuilder._find_feed_repeats(values)

    assert actual == expected


@pytest.mark.parametrize(
    "nutrient_standard, expected_get_data_key",
    [
        (NutrientStandard.NASEM, "NASEM_Comp"),
        (NutrientStandard.NRC, "NRC_Comp"),
    ],
)
def test_process_feed_library(
    mocker: MockerFixture,
    nutrient_standard: NutrientStandard,
    expected_get_data_key: str,
) -> None:
    """Tests that the selected feed library is loaded, converted, indexed, and enum fields are processed."""
    # Arrange
    mock_input_manager = mocker.MagicMock()
    mocker.patch.object(InputManager, "__new__", return_value=mock_input_manager)

    feed_library = {
        "rufas_id": [23, 44],
        "feed_type": ["conc", "forage"],
        "Fd_Category": ["energy_source", "protein_source"],
        "units": ["kg", "kg"],
        "DM": [90.0, 88.0],
        "CP": [0.11, 0.12],
    }
    mock_input_manager.get_data.return_value = feed_library

    converted_feed_library = [
        {
            "rufas_id": 23,
            "feed_type": FeedComponentType.CONC.value,
            "Fd_Category": FeedCategorization.ENERGY_SOURCE.value,
            "units": MeasurementUnits.KILOGRAMS.value,
            "DM": 90.0,
            "CP": 0.11,
        },
        {
            "rufas_id": 44,
            "feed_type": FeedComponentType.FORAGE.value,
            "Fd_Category": FeedCategorization.PLANT_PROTEIN.value,
            "units": MeasurementUnits.KILOGRAMS.value,
            "DM": 88.0,
            "CP": 0.12,
        },
    ]

    mock_convert = mocker.patch(
        "RUFAS.util.Utility.convert_dict_of_lists_to_list_of_dicts",
        return_value=converted_feed_library,
    )

    # Act
    actual = AvailableFeedsBuilder._process_feed_library(nutrient_standard)

    # Assert
    mock_input_manager.get_data.assert_called_once_with(expected_get_data_key)
    mock_convert.assert_called_once_with(feed_library)

    assert set(actual) == {23, 44}
    assert "rufas_id" not in actual[23]
    assert "rufas_id" not in actual[44]

    assert actual[23]["feed_type"] == FeedComponentType.CONC
    assert actual[23]["Fd_Category"] is FeedCategorization.ENERGY_SOURCE
    assert actual[44]["Fd_Category"] is FeedCategorization.PLANT_PROTEIN
    assert actual[23]["units"] == MeasurementUnits.KILOGRAMS
    assert actual[23]["DM"] == 90.0
    assert actual[23]["CP"] == 0.11
