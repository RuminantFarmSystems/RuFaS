import math
from types import SimpleNamespace
from typing import Any, Iterator
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.intake_option import IntakeOption


@pytest.fixture(autouse=True)
def _reset_intake_options() -> Iterator[None]:
    """Restores the RationManager intake option state after each test."""
    yield
    RationManager.intake_options = None
    RationManager.intake_values = None


@pytest.fixture
def valid_ration_config() -> dict[str, Any]:
    return {
        "ration_formulation_parameters": {
            "user_defined_ration_tolerance": 0.1,
        },
        "rations": [
            {
                "animal_combination": "calf",
                "feeds": [
                    {"feed_type": 101, "ration_percentage": 50.0},
                    {"feed_type": 102, "ration_percentage": 50.0},
                ],
            },
            {
                "animal_combination": "growing",
                "feeds": [
                    {"feed_type": 201, "ration_percentage": 60.0},
                    {"feed_type": 202, "ration_percentage": 40.0},
                ],
            },
            {
                "animal_combination": "close_up",
                "feeds": [
                    {"feed_type": 301, "ration_percentage": 70.0},
                    {"feed_type": 302, "ration_percentage": 30.0},
                ],
            },
            {
                "animal_combination": "lac_cow",
                "feeds": [
                    {"feed_type": 401, "ration_percentage": 80.0},
                    {"feed_type": 402, "ration_percentage": 20.0},
                ],
            },
        ],
    }


@pytest.fixture
def invalid_ration_config() -> dict[str, Any]:
    return {
        "ration_formulation_parameters": {
            "user_defined_ration_tolerance": 0.05,
        },
        "rations": [
            {
                "animal_combination": "calf",
                "feeds": [
                    {"feed_type": 101, "ration_percentage": 65.0},
                    {"feed_type": 102, "ration_percentage": 50.0},
                ],
            },
            {
                "animal_combination": "growing",
                "feeds": [
                    {"feed_type": 201, "ration_percentage": 60.0},
                    {"feed_type": 202, "ration_percentage": 50.0},
                ],
            },
            {
                "animal_combination": "close_up",
                "feeds": [
                    {"feed_type": 301, "ration_percentage": 90.0},
                    {"feed_type": 302, "ration_percentage": 10.0},
                ],
            },
            {
                "animal_combination": "lac_cow",
                "feeds": [
                    {"feed_type": 401, "ration_percentage": 85.0},
                    {"feed_type": 402, "ration_percentage": 25.0},
                ],
            },
        ],
    }


def test_set_ration_feeds_maps_config_to_animal_combinations() -> None:
    """set_ration_feeds should initialize ration_feeds for all combos and map config lists correctly."""
    ration_config: dict[str, Any] = {
        "rations": [
            {"animal_combination": "calf", "feeds": [{"feed_type": 1}, {"feed_type": 2}]},
            {
                "animal_combination": "growing",
                "feeds": [{"feed_type": 3}],
            },
            {"animal_combination": "close_up", "feeds": [{"feed_type": 4}, {"feed_type": 5}, {"feed_type": 6}]},
            {"animal_combination": "lac_cow", "feeds": [{"feed_type": 7}]},
        ]
    }

    RationManager.set_ration_feeds(ration_config)

    assert RationManager.ration_feeds is not None
    ration_feeds = RationManager.ration_feeds

    assert set(ration_feeds.keys()) == set(AnimalCombination)

    assert ration_feeds[AnimalCombination.CALF] == [
        feed["feed_type"]
        for ration in ration_config["rations"]
        if ration["animal_combination"] == "calf"
        for feed in ration["feeds"]
    ]
    assert ration_feeds[AnimalCombination.GROWING] == [
        feed["feed_type"]
        for ration in ration_config["rations"]
        if ration["animal_combination"] == "growing"
        for feed in ration["feeds"]
    ]
    assert ration_feeds[AnimalCombination.CLOSE_UP] == [
        feed["feed_type"]
        for ration in ration_config["rations"]
        if ration["animal_combination"] == "close_up"
        for feed in ration["feeds"]
    ]
    assert ration_feeds[AnimalCombination.LAC_COW] == [
        feed["feed_type"]
        for ration in ration_config["rations"]
        if ration["animal_combination"] == "lac_cow"
        for feed in ration["feeds"]
    ]

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
        "ration_formulation_parameters": {"user_defined_ration_tolerance": 0.15}
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
    "animal_combination, target_dry_matter_intake, user_defined_rations, expected_output",
    [
        (
            AnimalCombination.CALF,
            3.0,
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
            10.0,
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
            12.0,
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
    target_dry_matter_intake: float,
    user_defined_rations: dict[AnimalCombination, dict[RUFAS_ID, float]],
    expected_output: dict[RUFAS_ID, float],
) -> None:
    RationManager.user_defined_rations = user_defined_rations

    result = RationManager.get_user_defined_ration(animal_combination, target_dry_matter_intake)

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


def _mock_pen(dry_matter: float = 20.0, milk: float = 40.0, growth: float = 0.9) -> SimpleNamespace:
    """Builds a lightweight pen stand-in with the attributes resolve_target_dmi reads."""
    return SimpleNamespace(
        average_nutrition_requirements=SimpleNamespace(dry_matter=dry_matter),
        average_milk_production=milk,
        average_growth=growth,
    )


def test_set_intake_options_defaults_to_predict(mocker: MockerFixture, valid_ration_config: dict[str, Any]) -> None:
    """Rations without intake keys default to the predict DMI option with no intake value."""
    mocker.patch.object(RationManager._om, "add_variable")

    RationManager.set_intake_options(valid_ration_config)

    assert RationManager.intake_options is not None
    assert RationManager.intake_values is not None
    for combination in AnimalCombination:
        assert RationManager.intake_options[combination] is IntakeOption.PREDICT_DMI
        assert RationManager.intake_values[combination] is None


def test_set_intake_options_parses_options_and_values(
    mocker: MockerFixture, valid_ration_config: dict[str, Any]
) -> None:
    """Intake options and values are parsed per animal combination and mirrored for mixed pens."""
    mock_variable = mocker.patch.object(RationManager._om, "add_variable")
    for ration in valid_ration_config["rations"]:
        if ration["animal_combination"] == "calf":
            ration["intake_option"] = "set_DMI"
            ration["intake_value"] = 3.5
        elif ration["animal_combination"] == "growing":
            ration["intake_option"] = "set_DMI_per_X"
            ration["intake_value"] = 12.0
        elif ration["animal_combination"] == "close_up":
            ration["intake_option"] = "set_DMI"
            ration["intake_value"] = 13.0
        elif ration["animal_combination"] == "lac_cow":
            ration["intake_option"] = "set_DMI_per_X"
            ration["intake_value"] = 0.682

    RationManager.set_intake_options(valid_ration_config)

    assert RationManager.intake_options[AnimalCombination.CALF] is IntakeOption.SET_DMI
    assert RationManager.intake_values[AnimalCombination.CALF] == 3.5
    assert RationManager.intake_options[AnimalCombination.GROWING] is IntakeOption.SET_DMI_PER_X
    assert RationManager.intake_values[AnimalCombination.GROWING] == 12.0
    assert RationManager.intake_options[AnimalCombination.CLOSE_UP] is IntakeOption.SET_DMI
    assert RationManager.intake_values[AnimalCombination.CLOSE_UP] == 13.0
    assert RationManager.intake_options[AnimalCombination.LAC_COW] is IntakeOption.SET_DMI_PER_X
    assert RationManager.intake_values[AnimalCombination.LAC_COW] == 0.682
    assert (
        RationManager.intake_options[AnimalCombination.GROWING_AND_CLOSE_UP]
        is RationManager.intake_options[AnimalCombination.CLOSE_UP]
    )
    assert (
        RationManager.intake_values[AnimalCombination.GROWING_AND_CLOSE_UP]
        == RationManager.intake_values[AnimalCombination.CLOSE_UP]
    )
    assert mock_variable.call_count == 4


def test_set_intake_options_missing_value_raises(mocker: MockerFixture, valid_ration_config: dict[str, Any]) -> None:
    """A DMI input option without an intake value halts the simulation."""
    mock_error = mocker.patch.object(RationManager._om, "add_error")
    valid_ration_config["rations"][3]["intake_option"] = "set_DMI"

    with pytest.raises(ValueError):
        RationManager.set_intake_options(valid_ration_config)

    mock_error.assert_called_once()


def test_set_intake_options_per_x_invalid_combination_raises(
    mocker: MockerFixture, valid_ration_config: dict[str, Any]
) -> None:
    """The DMI per X option is rejected for animal combinations without an X metric."""
    mock_error = mocker.patch.object(RationManager._om, "add_error")
    for ration in valid_ration_config["rations"]:
        if ration["animal_combination"] == "close_up":
            ration["intake_option"] = "set_DMI_per_X"
            ration["intake_value"] = 10.0

    with pytest.raises(ValueError):
        RationManager.set_intake_options(valid_ration_config)

    mock_error.assert_called_once()


def test_set_ration_feeds_resets_intake_options() -> None:
    """Configuring automated rations resets any previously configured intake options."""
    RationManager.intake_options = {AnimalCombination.LAC_COW: IntakeOption.SET_DMI}
    RationManager.intake_values = {AnimalCombination.LAC_COW: 24.0}

    RationManager.set_ration_feeds({"rations": []})

    assert RationManager.intake_options is None
    assert RationManager.intake_values is None


def test_get_intake_option_defaults_to_predict_when_unset() -> None:
    """Without configured intake options, every animal combination predicts DMI."""
    RationManager.intake_options = None

    assert RationManager.get_intake_option(AnimalCombination.LAC_COW) is IntakeOption.PREDICT_DMI
    assert RationManager.get_intake_option(None) is IntakeOption.PREDICT_DMI
    assert not RationManager.uses_dmi_input_option(AnimalCombination.LAC_COW)


@pytest.mark.parametrize(
    "option, expected_fraction, expected_boost, expected_retry",
    [
        (
            IntakeOption.PREDICT_DMI,
            AnimalModuleConstants.DMI_CONSTRAINT_FRACTION,
            AnimalModuleConstants.DMI_REQUIREMENT_BOOST,
            AnimalModuleConstants.DMI_RETRY_INCREASE_FACTOR,
        ),
        (IntakeOption.SET_DMI, 0.0, 1.0, 1.0),
        (IntakeOption.SET_DMI_PER_X, 0.0, 1.0, 1.0),
    ],
)
def test_effective_dmi_constants(
    option: IntakeOption, expected_fraction: float, expected_boost: float, expected_retry: float
) -> None:
    """DMI input options neutralize the internal DMI adjustment constants."""
    RationManager.intake_options = {AnimalCombination.LAC_COW: option}
    RationManager.intake_values = {AnimalCombination.LAC_COW: 24.0}

    assert RationManager.effective_dmi_constraint_fraction(AnimalCombination.LAC_COW) == expected_fraction
    assert RationManager.effective_dmi_requirement_boost(AnimalCombination.LAC_COW) == expected_boost
    assert RationManager.effective_dmi_retry_increase_factor(AnimalCombination.LAC_COW) == expected_retry


def test_resolve_target_dmi_predict_uses_pen_requirements() -> None:
    """The predict DMI option keeps the pen's predicted dry matter requirement."""
    RationManager.intake_options = None

    target = RationManager.resolve_target_dmi(AnimalCombination.GROWING, _mock_pen(dry_matter=11.5))

    assert target == 11.5


def test_resolve_target_dmi_predict_calf_uses_constant() -> None:
    """Calf pens keep the fixed calf dry matter intake under the predict DMI option."""
    RationManager.intake_options = None

    target = RationManager.resolve_target_dmi(AnimalCombination.CALF, _mock_pen())

    assert target == RationManager.CALF_DRY_MATTER_INTAKE


def test_resolve_target_dmi_set_dmi_uses_intake_value() -> None:
    """The set DMI option returns the user-provided intake value for every animal combination."""
    RationManager.intake_options = {
        AnimalCombination.LAC_COW: IntakeOption.SET_DMI,
        AnimalCombination.CALF: IntakeOption.SET_DMI,
    }
    RationManager.intake_values = {AnimalCombination.LAC_COW: 24.0, AnimalCombination.CALF: 3.5}

    assert RationManager.resolve_target_dmi(AnimalCombination.LAC_COW, _mock_pen()) == 24.0
    assert RationManager.resolve_target_dmi(AnimalCombination.CALF, _mock_pen()) == 3.5


def test_resolve_target_dmi_per_x_scales_by_milk_or_growth() -> None:
    """The DMI per X option multiplies the intake value by milk production or average daily gain."""
    RationManager.intake_options = {
        AnimalCombination.LAC_COW: IntakeOption.SET_DMI_PER_X,
        AnimalCombination.GROWING: IntakeOption.SET_DMI_PER_X,
    }
    RationManager.intake_values = {AnimalCombination.LAC_COW: 0.5, AnimalCombination.GROWING: 10.0}
    pen = _mock_pen(milk=40.0, growth=0.9)

    assert RationManager.resolve_target_dmi(AnimalCombination.LAC_COW, pen) == pytest.approx(20.0)
    assert RationManager.resolve_target_dmi(AnimalCombination.GROWING, pen) == pytest.approx(9.0)


def test_resolve_target_dmi_missing_value_raises() -> None:
    """A DMI input option without an intake value cannot be resolved."""
    RationManager.intake_options = {AnimalCombination.LAC_COW: IntakeOption.SET_DMI}
    RationManager.intake_values = {AnimalCombination.LAC_COW: None}

    with pytest.raises(ValueError):
        RationManager.resolve_target_dmi(AnimalCombination.LAC_COW, _mock_pen())
