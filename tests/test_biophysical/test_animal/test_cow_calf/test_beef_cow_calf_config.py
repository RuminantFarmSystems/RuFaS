"""Tests for beef cow-calf AnimalConfig parameters — Step 2.

Verifies that AnimalConfig holds all new beef cow-calf class attributes
with correct defaults, and that initialize_animal_config() correctly
reads them from a beef_cow_calf section in the input JSON.
"""

from collections.abc import Generator
from typing import Any

import pytest
import pytest_mock

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import BeefPostWeaningDestination

# ---------------------------------------------------------------------------
# Autouse fixture: restore AnimalConfig class state after every test
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_animal_config_state() -> Generator[None, None, None]:
    """Save and restore AnimalConfig beef attributes around each test.

    initialize_animal_config() sets all ten beef ClassVars; saving them
    explicitly ensures teardown is predictable and type-safe.

    Yields
    ------
    None
        Yields control to the test body; restores state on teardown.
    """
    saved_breeding_season_start_day = AnimalConfig.beef_breeding_season_start_day
    saved_breeding_season_length = AnimalConfig.beef_breeding_season_length
    saved_weaning_age_days = AnimalConfig.beef_weaning_age_days
    saved_weaning_weight_kg = AnimalConfig.beef_weaning_weight_kg
    saved_creep_feeding_enabled = AnimalConfig.beef_creep_feeding_enabled
    saved_post_weaning_destination = AnimalConfig.beef_post_weaning_destination
    saved_mature_cow_weight_kg = AnimalConfig.beef_mature_cow_weight_kg
    saved_natural_service_bull_ratio = AnimalConfig.beef_natural_service_bull_ratio
    saved_cow_cull_rate_annual = AnimalConfig.beef_cow_cull_rate_annual
    saved_reproduction_program = AnimalConfig.beef_reproduction_program
    yield
    AnimalConfig.beef_breeding_season_start_day = saved_breeding_season_start_day
    AnimalConfig.beef_breeding_season_length = saved_breeding_season_length
    AnimalConfig.beef_weaning_age_days = saved_weaning_age_days
    AnimalConfig.beef_weaning_weight_kg = saved_weaning_weight_kg
    AnimalConfig.beef_creep_feeding_enabled = saved_creep_feeding_enabled
    AnimalConfig.beef_post_weaning_destination = saved_post_weaning_destination
    AnimalConfig.beef_mature_cow_weight_kg = saved_mature_cow_weight_kg
    AnimalConfig.beef_natural_service_bull_ratio = saved_natural_service_bull_ratio
    AnimalConfig.beef_cow_cull_rate_annual = saved_cow_cull_rate_annual
    AnimalConfig.beef_reproduction_program = saved_reproduction_program


# ---------------------------------------------------------------------------
# Default class-attribute values (no initialize needed)
# ---------------------------------------------------------------------------


def test_beef_breeding_season_start_day_default() -> None:
    """beef_breeding_season_start_day default must be a positive day-of-year integer."""
    val = AnimalConfig.beef_breeding_season_start_day
    assert isinstance(val, int)
    assert 1 <= val <= 365


def test_beef_breeding_season_length_default() -> None:
    """beef_breeding_season_length default must equal BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS."""
    assert AnimalConfig.beef_breeding_season_length == AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS


def test_beef_weaning_age_days_default() -> None:
    """beef_weaning_age_days default must equal BEEF_DEFAULT_WEANING_AGE_DAYS."""
    assert AnimalConfig.beef_weaning_age_days == AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS


def test_beef_weaning_weight_kg_default_is_none_or_positive() -> None:
    """beef_weaning_weight_kg default is None (age-only trigger) or a positive float."""
    val = AnimalConfig.beef_weaning_weight_kg
    assert val is None or (isinstance(val, float) and val > 0)


def test_beef_creep_feeding_enabled_default_is_bool() -> None:
    """beef_creep_feeding_enabled default must be a bool."""
    assert isinstance(AnimalConfig.beef_creep_feeding_enabled, bool)


def test_beef_post_weaning_destination_default_valid() -> None:
    """beef_post_weaning_destination default must be BeefPostWeaningDestination.SELL."""
    assert AnimalConfig.beef_post_weaning_destination is BeefPostWeaningDestination.SELL


def test_beef_mature_cow_weight_kg_default() -> None:
    """beef_mature_cow_weight_kg default must equal BEEF_DEFAULT_MATURE_COW_WEIGHT_KG."""
    assert AnimalConfig.beef_mature_cow_weight_kg == pytest.approx(
        AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    )


def test_beef_natural_service_bull_ratio_default_in_range() -> None:
    """beef_natural_service_bull_ratio default must be in the NRC reference range (20-30:1)."""
    ratio = AnimalConfig.beef_natural_service_bull_ratio
    assert isinstance(ratio, int)
    assert 20 <= ratio <= 30


def test_beef_cow_cull_rate_annual_default() -> None:
    """beef_cow_cull_rate_annual default must equal BEEF_ANNUAL_CULL_RATE."""
    assert AnimalConfig.beef_cow_cull_rate_annual == pytest.approx(AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE)


# ---------------------------------------------------------------------------
# Type annotations: check the right types are stored
# ---------------------------------------------------------------------------


def test_beef_weaning_weight_kg_annotation_allows_none() -> None:
    """beef_weaning_weight_kg annotation must be float | None (nullable)."""
    hints = AnimalConfig.__annotations__
    assert "beef_weaning_weight_kg" in hints
    hint = hints["beef_weaning_weight_kg"]
    # Accept both 'float | None' (union) and 'Optional[float]' style
    hint_str = str(hint)
    assert "float" in hint_str and "None" in hint_str, f"Expected 'float | None' annotation, got: {hint_str}"


# ---------------------------------------------------------------------------
# initialize_animal_config reads beef_cow_calf section from JSON
# ---------------------------------------------------------------------------


def _make_mock_animal_config_data(beef_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build a minimal animal_config_data dict with the beef_cow_calf section."""
    beef_section: dict[str, Any] = {
        "breeding_season_start_day": 90,
        "breeding_season_length": 63,
        "weaning_age_days": 207,
        "weaning_weight_kg": None,
        "creep_feeding_enabled": False,
        "post_weaning_destination": BeefPostWeaningDestination.SELL.value,
        "mature_cow_weight_kg": 520.0,
        "natural_service_bull_ratio": 25,
        "cow_cull_rate_annual": 0.175,
    }
    if beef_overrides:
        beef_section.update(beef_overrides)

    return {
        "farm_level": {
            "calf": {
                "wean_day": 60,
                "wean_length": 7,
                "male_calf_rate_conventional_semen": 0.53,
                "male_calf_rate_sexed_semen": 0.10,
                "keep_female_calf_rate": 1.0,
            },
            "bodyweight": {
                "target_heifer_preg_day": 399,
                "birth_weight_avg_ho": 43.9,
                "birth_weight_std_ho": 1.0,
                "birth_weight_avg_je": 27.2,
                "birth_weight_std_je": 1.0,
                "mature_body_weight_avg": 740.1,
                "mature_body_weight_std": 73.5,
            },
            "repro": {
                "prefresh_day": 21,
                "calving_interval": 400,
                "avg_gestation_len": 276,
                "std_gestation_len": 6,
                "voluntary_waiting_period": 50,
                "conception_rate_decrease": 0.026,
                "decrease_conception_rate_in_rebreeding": False,
                "decrease_conception_rate_by_parity": False,
                "heifers": {
                    "estrus_detection_rate": 0.9,
                    "estrus_conception_rate": 0.6,
                    "repro_sub_protocol": "5dCG2P",
                    "repro_sub_properties": {
                        "conception_rate": 0.6,
                        "estrus_detection_rate": 0.9,
                    },
                },
                "cows": {
                    "estrus_detection_rate": 0.5,
                    "ED_conception_rate": 0.6,
                    "presynch_program": "Double OvSynch",
                    "ovsynch_program": "OvSynch 56",
                    "resynch_program": "TAIafterPD",
                    "ovsynch_program_start_day": 64,
                    "ovsynch_program_conception_rate": 0.6,
                    "presynch_program_start_day": 50,
                },
            },
        },
        "management_decisions": {
            "breeding_start_day_h": 380,
            "heifer_repro_method": "ED",
            "cow_repro_method": "ED-TAI",
            "semen_type": "conventional",
            "days_in_preg_when_dry": 218,
            "heifer_repro_cull_time": 500,
            "do_not_breed_time": 185,
            "cow_times_milked_per_day": 3,
            "milk_fat_percent": 4.0,
            "milk_protein_percent": 3.2,
        },
        "from_literature": {
            "life_cycle": {"still_birth_rate": 0.065},
            "repro": {
                "avg_estrus_cycle_return": 23,
                "std_estrus_cycle_return": 6.0,
                "avg_estrus_cycle_heifer": 21,
                "std_estrus_cycle_heifer": 2.5,
                "avg_estrus_cycle_cow": 21,
                "std_estrus_cycle_cow": 4.0,
                "avg_estrus_cycle_after_pgf": 5,
                "std_estrus_cycle_after_pgf": 2.0,
                "preg_check_day_1": 32,
                "preg_loss_rate_1": 0.02,
                "preg_check_day_2": 60,
                "preg_loss_rate_2": 0.096,
                "preg_check_day_3": 200,
                "preg_loss_rate_3": 0.017,
            },
            "culling": {
                "parity_death_prob": [0.039, 0.056, 0.085, 0.117],
                "death_day_prob": [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.60, 0.65, 0.70, 0.77, 0.83, 0.89, 0.95, 1],
                "parity_cull_prob": [0.169, 0.233, 0.301, 0.408],
                "cull_day_count": [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530],
                "feet_leg_cull": {"probability": 0.1633, "cull_day_prob": [0] * 14},
                "injury_cull": {"probability": 0.2883, "cull_day_prob": [0] * 14},
                "mastitis_cull": {"probability": 0.2439, "cull_day_prob": [0] * 14},
                "disease_cull": {"probability": 0.1391, "cull_day_prob": [0] * 14},
                "udder_cull": {"probability": 0.0645, "cull_day_prob": [0] * 14},
                "unknown_cull": {"probability": 0.1009, "cull_day_prob": [0] * 14},
            },
        },
        "beef_cow_calf": beef_section,
    }


def _make_mock_animal_data(beef_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "animal_config": _make_mock_animal_config_data(beef_overrides),
        "methane_model": {
            "calves": "Pattanaik",
            "heiferIs": "IPCC",
            "heiferIIs": "IPCC",
            "heiferIIIs": "IPCC",
            "cow": {"dry cows": "IPCC", "lactating cows": "IPCC"},
        },
        "methane_mitigation": {
            "methane_mitigation_method": "None",
            "methane_mitigation_additive_amount": 0.0,
        },
        "herd_information": {"simulate_genetics": False},
    }


def test_initialize_sets_beef_breeding_season_start_day(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_breeding_season_start_day from the input JSON."""
    _mock_im(mocker, beef_overrides={"breeding_season_start_day": 90})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_breeding_season_start_day == 90


def test_initialize_sets_beef_breeding_season_length(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_breeding_season_length from the input JSON."""
    _mock_im(mocker, beef_overrides={"breeding_season_length": 63})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_breeding_season_length == 63


def test_initialize_sets_beef_weaning_age_days(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_weaning_age_days from the input JSON."""
    _mock_im(mocker, beef_overrides={"weaning_age_days": 180})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_weaning_age_days == 180


def test_initialize_sets_beef_weaning_weight_none(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores None for beef_weaning_weight_kg when not in JSON."""
    _mock_im(mocker, beef_overrides={"weaning_weight_kg": None})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_weaning_weight_kg is None


def test_initialize_sets_beef_weaning_weight_float(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores a positive float for beef_weaning_weight_kg when provided."""
    _mock_im(mocker, beef_overrides={"weaning_weight_kg": 240.0})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_weaning_weight_kg == pytest.approx(240.0)


def test_initialize_sets_beef_creep_feeding_enabled(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_creep_feeding_enabled from the input JSON."""
    _mock_im(mocker, beef_overrides={"creep_feeding_enabled": True})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_creep_feeding_enabled is True


def test_initialize_sets_beef_post_weaning_destination(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_post_weaning_destination from the input JSON."""
    _mock_im(mocker, beef_overrides={"post_weaning_destination": BeefPostWeaningDestination.DIRECT_TO_FEEDLOT.value})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_post_weaning_destination is BeefPostWeaningDestination.DIRECT_TO_FEEDLOT


def test_initialize_sets_beef_mature_cow_weight_kg(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_mature_cow_weight_kg from the input JSON."""
    _mock_im(mocker, beef_overrides={"mature_cow_weight_kg": 540.0})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_mature_cow_weight_kg == pytest.approx(540.0)


def test_initialize_sets_beef_natural_service_bull_ratio(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_natural_service_bull_ratio from the input JSON."""
    _mock_im(mocker, beef_overrides={"natural_service_bull_ratio": 25})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_natural_service_bull_ratio == 25


def test_initialize_sets_beef_cow_cull_rate_annual(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config stores beef_cow_cull_rate_annual from the input JSON."""
    _mock_im(mocker, beef_overrides={"cow_cull_rate_annual": 0.20})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_cow_cull_rate_annual == pytest.approx(0.20)


def test_initialize_beef_section_missing_uses_defaults(mocker: pytest_mock.MockerFixture) -> None:
    """If beef_cow_calf section is absent from JSON, defaults are used (not KeyError)."""
    animal_data = _make_mock_animal_data()
    del animal_data["animal_config"]["beef_cow_calf"]

    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")
    mock_im = mock_im_cls.return_value
    mock_im.get_data.side_effect = _make_get_data_side_effect(animal_data)

    AnimalConfig.initialize_animal_config()

    # All beef attributes must still be set (to their defaults)
    assert AnimalConfig.beef_weaning_age_days == AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    assert AnimalConfig.beef_mature_cow_weight_kg == pytest.approx(
        AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    )
    assert AnimalConfig.beef_breeding_season_length == AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    assert AnimalConfig.beef_cow_cull_rate_annual == pytest.approx(AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_get_data_side_effect(animal_data: dict[str, Any]) -> Any:
    """Return a side_effect callable for InputManager.get_data used in tests."""
    side_effects: dict[str, Any] = {
        "animal": animal_data,
        "feed.ration_formulation_parameters.milk_reduction_maximum": 5.0,
        "animal_mean_phenotype": {"birth_year": []},
        "animal_top_listing_semen": {"year_month": []},
    }

    def get_data(key: str) -> Any:
        return side_effects[key]

    return get_data


def _mock_im(mocker: pytest_mock.MockerFixture, beef_overrides: dict[str, Any] | None = None) -> None:
    """Patch InputManager and OutputManager for initialize_animal_config calls."""
    animal_data = _make_mock_animal_data(beef_overrides)
    mock_im_cls = mocker.patch("RUFAS.biophysical.animal.animal_config.InputManager")
    mocker.patch("RUFAS.biophysical.animal.animal_config.OutputManager")
    mock_im = mock_im_cls.return_value
    mock_im.get_data.side_effect = _make_get_data_side_effect(animal_data)


# ---------------------------------------------------------------------------
# beef_post_weaning_destination validation (FIX 2 — CodeRabbit)
# ---------------------------------------------------------------------------


_IMPLEMENTED_DESTINATIONS = (
    BeefPostWeaningDestination.SELL,
    BeefPostWeaningDestination.REPLACEMENT_HEIFER,
    BeefPostWeaningDestination.DIRECT_TO_FEEDLOT,
)


@pytest.mark.parametrize("dest", _IMPLEMENTED_DESTINATIONS)
def test_initialize_valid_post_weaning_destinations_accepted(
    dest: BeefPostWeaningDestination, mocker: pytest_mock.MockerFixture
) -> None:
    """SELL, REPLACEMENT_HEIFER, and DIRECT_TO_FEEDLOT must be accepted without error."""
    _mock_im(mocker, beef_overrides={"post_weaning_destination": dest.value})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_post_weaning_destination is dest


def test_initialize_stocker_destination_raises_not_implemented(mocker: pytest_mock.MockerFixture) -> None:
    """'stocker' post_weaning_destination must raise NotImplementedError at config init (not at weaning time).

    STOCKER is a valid enum member but requires the stocker module (Segment 3)
    which is not yet implemented. Rejecting it early at config time gives a clear
    error before any animal reaches weaning age.
    """
    _mock_im(mocker, beef_overrides={"post_weaning_destination": BeefPostWeaningDestination.STOCKER.value})
    with pytest.raises(NotImplementedError, match="STOCKER"):
        AnimalConfig.initialize_animal_config()


def test_initialize_invalid_post_weaning_destination_raises(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config must raise ValueError for an unrecognised destination."""
    _mock_im(mocker, beef_overrides={"post_weaning_destination": "auction"})
    with pytest.raises(ValueError, match="Invalid beef post-weaning destination"):
        AnimalConfig.initialize_animal_config()


def test_initialize_invalid_reproduction_program_raises(mocker: pytest_mock.MockerFixture) -> None:
    """initialize_animal_config must raise ValueError for an unrecognised reproduction_program.

    Verifies that a clear, user-facing error message is returned listing valid
    options (FIX 3 — mirrors the post_weaning_destination validation pattern).
    """
    _mock_im(mocker, beef_overrides={"reproduction_program": "synchronized_timed_ai"})
    with pytest.raises(ValueError, match="Invalid beef reproduction program"):
        AnimalConfig.initialize_animal_config()
# ---------------------------------------------------------------------------
# None-safe assignment block (FIX 1 — CodeRabbit Round 3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "key",
    [
        "mature_cow_weight_kg",
        "weaning_age_days",
        "breeding_season_length",
        "natural_service_bull_ratio",
    ],
)
def test_initialize_explicit_none_for_validated_key_uses_default(key: str, mocker: pytest_mock.MockerFixture) -> None:
    """An explicit None in the beef_cow_calf section must not raise TypeError.

    Each of the four keys covered by merged_beef_cfg must fall back to its default
    when present but set to None, rather than propagating None to int()/float().

    Parameters
    ----------
    key : str
        The beef_cow_calf config key to set to None.
    mocker : pytest_mock.MockerFixture
        pytest-mock fixture for patching InputManager.
    """
    _mock_im(mocker, beef_overrides={key: None})
    AnimalConfig.initialize_animal_config()
    assert AnimalConfig.beef_mature_cow_weight_kg == pytest.approx(
        AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    )
    assert AnimalConfig.beef_weaning_age_days == AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    assert AnimalConfig.beef_breeding_season_length == AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    assert AnimalConfig.beef_natural_service_bull_ratio == 25
