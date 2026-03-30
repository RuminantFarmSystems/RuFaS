import math
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination


@pytest.fixture
def valid_ration_config() -> dict[str, dict[str, list[dict[str, int | float]] | float]]:
    return {
        "user_defined_ration_percentages": {
            "calf": [{"feed_type": 101, "ration_percentage": 50.0}, {"feed_type": 102, "ration_percentage": 50.0}],
            "growing": [{"feed_type": 201, "ration_percentage": 60.0}, {"feed_type": 202, "ration_percentage": 40.0}],
            "close_up": [{"feed_type": 301, "ration_percentage": 70.0}, {"feed_type": 302, "ration_percentage": 30.0}],
            "lac_cow": [{"feed_type": 401, "ration_percentage": 80.0}, {"feed_type": 402, "ration_percentage": 20.0}],
            "tolerance": 0.1,
        }
    }


@pytest.fixture
def invalid_ration_config() -> dict[str, dict[str, list[dict[str, int | float]] | float]]:
    return {
        "user_defined_ration_percentages": {
            "calf": [{"feed_type": 101, "ration_percentage": 55.0}, {"feed_type": 102, "ration_percentage": 50.0}],
            "growing": [{"feed_type": 201, "ration_percentage": 60.0}, {"feed_type": 202, "ration_percentage": 50.0}],
            "close_up": [{"feed_type": 301, "ration_percentage": 90.0}, {"feed_type": 302, "ration_percentage": 10.0}],
            "lac_cow": [{"feed_type": 401, "ration_percentage": 85.0}, {"feed_type": 402, "ration_percentage": 25.0}],
            "tolerance": 0.01,
        }
    }


def test_set_ration_feeds_maps_config_to_animal_combinations() -> None:
    """set_ration_feeds should initialize ration_feeds for all combos and map config lists correctly."""
    ration_config: dict[str, list[int]] = {
        "calf_feeds": [1, 2],
        "growing_feeds": [3],
        "close_up_feeds": [4, 5, 6],
        "lac_cow_feeds": [7],
    }

    RationManager.set_ration_feeds(ration_config)

    assert RationManager.ration_feeds is not None
    ration_feeds = RationManager.ration_feeds

    assert set(ration_feeds.keys()) == set(AnimalCombination)

    assert ration_feeds[AnimalCombination.CALF] == ration_config["calf_feeds"]
    assert ration_feeds[AnimalCombination.GROWING] == ration_config["growing_feeds"]
    assert ration_feeds[AnimalCombination.CLOSE_UP] == ration_config["close_up_feeds"]
    assert ration_feeds[AnimalCombination.LAC_COW] == ration_config["lac_cow_feeds"]

    for combo, value in ration_feeds.items():
        if combo not in {
            AnimalCombination.CALF,
            AnimalCombination.GROWING,
            AnimalCombination.CLOSE_UP,
            AnimalCombination.LAC_COW,
        }:
            assert value == []


def test_get_ration_feeds_returns_expected_list() -> None:
    """get_ration_feeds should return the exact list stored in ration_feeds for that animal combination."""
    fake_mapping: dict[AnimalCombination, list[int]] = {
        AnimalCombination.CALF: [1, 2],
        AnimalCombination.GROWING: [3],
        AnimalCombination.CLOSE_UP: [],
        AnimalCombination.LAC_COW: [4, 5],
    }

    RationManager.ration_feeds = fake_mapping

    result = RationManager.get_ration_feeds(AnimalCombination.CALF)

    assert result == [1, 2]
    assert RationManager.get_ration_feeds(AnimalCombination.LAC_COW) == [4, 5]


def test_set_user_defined_ration_tolerance_updates_class_attribute() -> None:
    """set_user_defined_ration_tolerance should store the tolerance value from the config."""
    config: dict[str, dict[str, list[dict[str, int | float]] | float]] = {
        "user_defined_ration_percentages": {"tolerance": 0.15}
    }

    RationManager.set_user_defined_ration_tolerance(config)

    assert RationManager.tolerance == 0.15


def test_set_user_defined_rations_valid(
    mocker: MockerFixture, valid_ration_config: dict[str, dict[str, list[dict[str, int | float]] | float]]
) -> None:
    mocker.patch.object(RationManager._om, "add_variable")
    mock_log = mocker.patch.object(RationManager._om, "add_log")

    RationManager.set_user_defined_rations(valid_ration_config)

    assert (
        RationManager.user_defined_rations[AnimalCombination.GROWING_AND_CLOSE_UP]
        == RationManager.user_defined_rations[AnimalCombination.CLOSE_UP]
    )
    mock_log.assert_called_once()


def test_set_user_defined_rations_invalid(
    mocker: MockerFixture, invalid_ration_config: dict[str, dict[str, list[dict[str, float]] | float]]
) -> None:
    mock_error = mocker.patch.object(RationManager._om, "add_error")

    with pytest.raises(ValueError):
        RationManager.set_user_defined_rations(invalid_ration_config)

    assert mock_error.call_count == 3


@pytest.mark.parametrize(
    "animal_combination, requirements, user_defined_rations, expected_output",
    [
        (
            AnimalCombination.CALF,
            NutritionRequirements(
                maintenance_energy=10.0,
                growth_energy=5.0,
                pregnancy_energy=0.0,
                lactation_energy=8.0,
                metabolizable_protein=600.0,
                calcium=100.0,
                phosphorus=50.0,
                process_based_phosphorus=50.0,
                dry_matter=8.0,
                activity_energy=2.0,
                essential_amino_acids=EssentialAminoAcidRequirements(
                    histidine=2.0,
                    isoleucine=2.0,
                    leucine=2.0,
                    lysine=2.0,
                    methionine=2.0,
                    phenylalanine=2.0,
                    threonine=2.0,
                    thryptophan=2.0,
                    valine=2.0,
                ),
            ),
            {
                AnimalCombination.CALF: {202: 33.3, 216: 66.7},
                AnimalCombination.GROWING: {201: 60.0, 202: 40.0},
                AnimalCombination.CLOSE_UP: {301: 70.0, 302: 30.0},
                AnimalCombination.LAC_COW: {401: 80.0, 402: 20.0},
            },
            {
                202: 0.9989,
                216: 2,
            },
        ),
        (
            AnimalCombination.GROWING,
            NutritionRequirements(
                maintenance_energy=10.0,
                growth_energy=5.0,
                pregnancy_energy=0.0,
                lactation_energy=8.0,
                metabolizable_protein=600.0,
                calcium=100.0,
                phosphorus=50.0,
                process_based_phosphorus=50.0,
                dry_matter=10.0,
                activity_energy=2.0,
                essential_amino_acids=EssentialAminoAcidRequirements(
                    histidine=2.0,
                    isoleucine=2.0,
                    leucine=2.0,
                    lysine=2.0,
                    methionine=2.0,
                    phenylalanine=2.0,
                    threonine=2.0,
                    thryptophan=2.0,
                    valine=2.0,
                ),
            ),
            {
                AnimalCombination.CALF: {101: 50.0, 102: 50.0},
                AnimalCombination.GROWING: {201: 60.0, 202: 40.0},
                AnimalCombination.CLOSE_UP: {301: 70.0, 302: 30.0},
                AnimalCombination.LAC_COW: {401: 80.0, 402: 20.0},
            },
            {
                201: 6.0,
                202: 4.0,
            },
        ),
        (
            AnimalCombination.LAC_COW,
            NutritionRequirements(
                maintenance_energy=10.0,
                growth_energy=5.0,
                pregnancy_energy=0.0,
                lactation_energy=8.0,
                metabolizable_protein=600.0,
                calcium=100.0,
                phosphorus=50.0,
                process_based_phosphorus=50.0,
                dry_matter=12.0,
                activity_energy=2.0,
                essential_amino_acids=EssentialAminoAcidRequirements(
                    histidine=2.0,
                    isoleucine=2.0,
                    leucine=2.0,
                    lysine=2.0,
                    methionine=2.0,
                    phenylalanine=2.0,
                    threonine=2.0,
                    thryptophan=2.0,
                    valine=2.0,
                ),
            ),
            {
                AnimalCombination.CALF: {101: 50.0, 102: 50.0},
                AnimalCombination.GROWING: {201: 60.0, 202: 40.0},
                AnimalCombination.CLOSE_UP: {301: 70.0, 302: 30.0},
                AnimalCombination.LAC_COW: {401: 80.0, 402: 20.0},
            },
            {
                401: 9.6,
                402: 2.4,
            },
        ),
    ],
)
def test_get_user_defined_ration(
    animal_combination: AnimalCombination,
    requirements: NutritionRequirements,
    user_defined_rations: dict[AnimalCombination, dict[RUFAS_ID, float]],
    expected_output: dict[RUFAS_ID, float],
) -> None:
    RationManager.user_defined_rations = user_defined_rations

    result = RationManager.get_user_defined_ration(animal_combination, requirements)

    for key, expected_value in expected_output.items():
        assert math.isclose(result[key], expected_value, rel_tol=1e-3)


def test_get_user_defined_ration_feeds_returns_keys_for_combination() -> None:
    """get_user_defined_ration_feeds should return the list of RuFaS IDs defined for that animal combination."""

    RationManager.user_defined_rations = {
        AnimalCombination.CALF: {101: 25.0, 202: 75.0},
        AnimalCombination.GROWING: {303: 50.0},
    }

    result = RationManager.get_user_defined_ration_feeds(AnimalCombination.CALF)

    assert result == [101, 202]
    assert RationManager.get_user_defined_ration_feeds(AnimalCombination.GROWING) == [303]
