"""Tests for beef cow-calf biological constants and event strings.

Step 2 of the cow-calf module. Every constant is pinned to its exact
NRC 2016 / USDA source value so that a future equation-coefficient
regression surfaces immediately.
"""

import pytest

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal import animal_constants

# ---------------------------------------------------------------------------
# AnimalModuleConstants — reproduction / calving
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attr, expected",
    [
        ("BEEF_GESTATION_LENGTH_DAYS", 283),  # NRC 2016 average beef gestation
        ("BEEF_DEFAULT_WEANING_AGE_DAYS", 207),  # USDA average weaning age
        ("BEEF_HEIFER_FIRST_CALVING_AGE_DAYS", 690),  # 22-24 months midpoint ~23 mo
        ("BEEF_COW_MAX_AGE_DAYS", 5475),  # 15 years conservative longevity ceiling
        ("BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS", 63),  # 63-day breeding season
    ],
)
def test_cow_calf_int_constants(attr: str, expected: int) -> None:
    """Integer biological constants must exist with exact NRC/USDA source values."""
    assert hasattr(AnimalModuleConstants, attr), f"Missing constant: {attr}"
    assert getattr(AnimalModuleConstants, attr) == expected


@pytest.mark.parametrize(
    "attr, expected",
    [
        ("BEEF_CALF_CROP_WEANED_RATE", 0.855),  # USDA average calf crop weaned per cow exposed
        ("BEEF_STILLBIRTH_RATE", 0.035),  # 96.5% born live (USDA 2009a)
        ("BEEF_PREWEANING_SURVIVAL_RATE", 0.968),  # 96.8% of live calves survive to weaning
        ("BEEF_DEFAULT_WEANING_WEIGHT_KG", 240.0),  # USDA average weaning weight
        ("BEEF_PREWEANING_ADG_KG_D", 1.0),  # NRC reference preweaning calf gain
        ("BEEF_CALF_BIRTH_WEIGHT_KG", 35.0),  # NRC reference average birth weight
        ("BEEF_DEFAULT_MATURE_COW_WEIGHT_KG", 520.0),  # USDA average mature cow weight
        ("BEEF_COW_FORAGE_DMI_PCT_BW", 0.0225),  # 2.25% BW forage DM/d moderate condition
        ("BEEF_PREWEANING_CALF_DMI_PCT_BW", 0.0125),  # 1.25% BW preweaning forage intake
        ("BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE", 0.60),  # 55-65% mature weight at first breeding
        ("BEEF_HEIFER_TARGET_CALVING_PCT_MATURE", 0.80),  # ~80% mature weight at first calving
        ("BEEF_HEIFER_TARGET_ADG_KG_D", 0.675),  # midpoint of 0.45-0.90 kg/d target range
        ("BEEF_ANNUAL_CULL_RATE", 0.175),  # midpoint of 15-20% national average
        ("BEEF_DEFAULT_BCS_9", 5.0),  # moderate body condition on 1-9 NRC scale
    ],
)
def test_cow_calf_float_constants(attr: str, expected: float) -> None:
    """Float biological constants must exist with exact NRC/USDA source values."""
    assert hasattr(AnimalModuleConstants, attr), f"Missing constant: {attr}"
    assert getattr(AnimalModuleConstants, attr) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Source-scale correctness: BEEF_DEFAULT_BCS_9 is NOT on the dairy 1-5 scale
# ---------------------------------------------------------------------------


def test_beef_bcs_is_on_nine_point_scale() -> None:
    """BEEF_DEFAULT_BCS_9 must be between 1 and 9, confirming the NRC beef scale."""
    bcs = AnimalModuleConstants.BEEF_DEFAULT_BCS_9
    assert 1.0 <= bcs <= 9.0, f"BCS {bcs} outside 1-9 beef scale"


def test_beef_bcs_distinct_from_dairy_bcs() -> None:
    """Beef BCS constant (1-9) must not be confused with dairy BCS constant (1-5 scale)."""
    assert hasattr(AnimalModuleConstants, "DEFAULT_BODY_CONDITION_SCORE_5"), "Dairy constant must still exist"
    assert AnimalModuleConstants.BEEF_DEFAULT_BCS_9 != AnimalModuleConstants.DEFAULT_BODY_CONDITION_SCORE_5


# ---------------------------------------------------------------------------
# Rate bounds: values that are proportions must lie within [0, 1]
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attr",
    [
        "BEEF_CALF_CROP_WEANED_RATE",
        "BEEF_STILLBIRTH_RATE",
        "BEEF_PREWEANING_SURVIVAL_RATE",
        "BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE",
        "BEEF_HEIFER_TARGET_CALVING_PCT_MATURE",
        "BEEF_ANNUAL_CULL_RATE",
    ],
)
def test_cow_calf_rate_constants_in_unit_interval(attr: str) -> None:
    """All rate/proportion constants must lie strictly within (0, 1)."""
    value = getattr(AnimalModuleConstants, attr)
    assert 0.0 < value < 1.0, f"{attr}={value} is outside (0, 1)"


# ---------------------------------------------------------------------------
# Positive-value guards for all duration and weight constants
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attr",
    [
        "BEEF_GESTATION_LENGTH_DAYS",
        "BEEF_DEFAULT_WEANING_AGE_DAYS",
        "BEEF_HEIFER_FIRST_CALVING_AGE_DAYS",
        "BEEF_COW_MAX_AGE_DAYS",
        "BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS",
        "BEEF_DEFAULT_WEANING_WEIGHT_KG",
        "BEEF_CALF_BIRTH_WEIGHT_KG",
        "BEEF_DEFAULT_MATURE_COW_WEIGHT_KG",
        "BEEF_HEIFER_TARGET_ADG_KG_D",
    ],
)
def test_cow_calf_duration_and_weight_constants_positive(attr: str) -> None:
    """All duration and weight constants must be strictly positive."""
    value = getattr(AnimalModuleConstants, attr)
    assert value > 0, f"{attr}={value} must be > 0"


# ---------------------------------------------------------------------------
# Logical ordering: heifer development progression makes biological sense
# ---------------------------------------------------------------------------


def test_heifer_breeding_weight_below_calving_weight() -> None:
    """Breeding target weight fraction must be less than calving target weight fraction."""
    assert (
        AnimalModuleConstants.BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE
        < AnimalModuleConstants.BEEF_HEIFER_TARGET_CALVING_PCT_MATURE
    )


def test_weaning_age_less_than_first_calving_age() -> None:
    """Weaning age must be less than first calving age for heifers."""
    assert (
        AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS < AnimalModuleConstants.BEEF_HEIFER_FIRST_CALVING_AGE_DAYS
    )


def test_gestation_length_less_than_first_calving_age() -> None:
    """Gestation length must be less than first calving age (heifers must be bred before calving)."""
    assert AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS < AnimalModuleConstants.BEEF_HEIFER_FIRST_CALVING_AGE_DAYS


# ---------------------------------------------------------------------------
# animal_constants — cow-calf event strings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attr, expected_str",
    [
        ("CALF_WEANED", "calf_weaned"),
        ("COW_REBRED", "cow_rebred"),
        ("COW_OPEN_AT_PREGNANCY_CHECK", "cow_open_at_pregnancy_check"),
        ("COW_CULLED_AGE", "cow_culled_age"),
        ("COW_CULLED_OPEN", "cow_culled_open"),
        ("REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT", "replacement_heifer_reached_breeding_weight"),
        ("REPLACEMENT_HEIFER_PROMOTED_TO_COW", "replacement_heifer_promoted_to_cow"),
        ("STILLBIRTH", "stillbirth"),
    ],
)
def test_cow_calf_event_strings(attr: str, expected_str: str) -> None:
    """Cow-calf event string constants must exist with correct lowercase values."""
    assert hasattr(animal_constants, attr), f"Missing event constant: {attr}"
    assert getattr(animal_constants, attr) == expected_str


def test_event_strings_are_unique() -> None:
    """All cow-calf event strings must be distinct from each other and from feedlot events."""
    cow_calf_attrs = [
        "CALF_WEANED",
        "COW_REBRED",
        "COW_OPEN_AT_PREGNANCY_CHECK",
        "COW_CULLED_AGE",
        "COW_CULLED_OPEN",
        "REPLACEMENT_HEIFER_REACHED_BREEDING_WEIGHT",
        "REPLACEMENT_HEIFER_PROMOTED_TO_COW",
        "STILLBIRTH",
    ]
    feedlot_attrs = [
        "FEEDLOT_ARRIVAL",
        "SLAUGHTER_WEIGHT_REACHED",
        "MAX_DAYS_ON_FEED_REACHED",
    ]
    cow_calf_values = [getattr(animal_constants, a) for a in cow_calf_attrs]
    feedlot_values = [getattr(animal_constants, a) for a in feedlot_attrs]

    assert len(cow_calf_values) == len(set(cow_calf_values)), "Cow-calf event strings are not unique"
    for cc_val in cow_calf_values:
        assert cc_val not in feedlot_values, f"Cow-calf event '{cc_val}' collides with a feedlot event string"


# ---------------------------------------------------------------------------
# MappingProxyType immutability — breed lookup dicts (FIX 4 — CodeRabbit)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "attr",
    [
        "BREED_L_FACTOR",
        "BREED_CBW_KG",
        "BREED_PEAK_MILK_YIELD_KG_D",
        "BREED_MILK_FAT_PCT",
        "BREED_MILK_PROTEIN_PCT",
        "BREED_MILK_SNF_PCT",
    ],
)
def test_breed_lookup_dicts_are_immutable(attr: str) -> None:
    """Breed lookup dicts must be MappingProxyType and raise TypeError on mutation attempt."""
    mapping = getattr(AnimalModuleConstants, attr)
    with pytest.raises(TypeError):
        mapping["__test_sentinel__"] = 0.0
