"""Tests for beef cow-calf reproduction (Step 5) — PR-B.

All tests must FAIL (RED) before Step 5 is implemented and PASS (GREEN) after
implementing BeefReproductionProtocol, AnimalConfig.beef_reproduction_program,
and calculate_seasonal_conception_probability in beef_reproduction.py.
"""

from random import seed as random_seed

import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_enums import Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import BeefReproductionProtocol
from RUFAS.biophysical.animal.reproduction.beef_reproduction import calculate_seasonal_conception_probability

# ── R1–R2: BeefReproductionProtocol enum ────────────────────────────────────


@pytest.mark.unit
def test_R1_natural_service_seasonal_exists() -> None:
    """R1: BeefReproductionProtocol.NATURAL_SERVICE_SEASONAL must exist with the correct string value.

    Verifies enum member presence and value for the primary PR-B protocol.
    """
    assert BeefReproductionProtocol.NATURAL_SERVICE_SEASONAL.value == "natural_service_seasonal"


@pytest.mark.unit
def test_R2_ai_protocols_exist() -> None:
    """R2: AI_SEASONAL and AI_CONTROLLED_BREEDING enum members must exist (even though unimplemented in PR-B).

    Verifies that the full enum is declared so future PRs can enable these
    protocols without changing the enum definition.
    """
    assert BeefReproductionProtocol.AI_SEASONAL.value == "ai_seasonal"
    assert BeefReproductionProtocol.AI_CONTROLLED_BREEDING.value == "ai_controlled_breeding"


# ── R3: AnimalConfig wiring ──────────────────────────────────────────────────


@pytest.mark.unit
def test_R3_animal_config_accepts_natural_service_seasonal() -> None:
    """R3: AnimalConfig.beef_reproduction_program must accept 'natural_service_seasonal' via class attribute default.

    Verifies that Step 5.2 wires the enum into AnimalConfig with a sensible
    default so runs without an explicit beef_reproduction_program in JSON still work.
    """
    assert AnimalConfig.beef_reproduction_program == BeefReproductionProtocol.NATURAL_SERVICE_SEASONAL


# ── R4–R7: calculate_seasonal_conception_probability ─────────────────────────


@pytest.mark.unit
def test_R4_conception_probability_in_valid_range() -> None:
    """R4: calculate_seasonal_conception_probability at normal inputs must return a value in (0.0, 0.1).

    Normal inputs: BCS=5, bull_ratio=25, days_since_calving=60. Calibrated base
    rate should be approximately 0.04 (see §5.3 Notes).
    """
    prob = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=60,
    )
    assert 0.0 < prob < 0.1, f"Expected daily probability in (0.0, 0.1), got {prob}"


@pytest.mark.unit
def test_R5_postpartum_anestrus_returns_zero() -> None:
    """R5: days_since_calving < 45 must return 0.0 (postpartum anestrus guard).

    Cows that calved fewer than 45 days ago are not cycling and cannot conceive.
    """
    prob = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=44,
    )
    assert prob == 0.0


@pytest.mark.unit
def test_R6_low_bcs_reduces_probability() -> None:
    """R6: BCS < 5 must yield a lower daily probability than BCS = 5.

    NRC 2016 Ch.13 indicates that thin cows (BCS < 5 on 1-9 scale) have
    reduced conception rates due to energy deficit.
    """
    prob_normal = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=60,
    )
    prob_thin = calculate_seasonal_conception_probability(
        body_condition_score=3.0,
        bull_to_cow_ratio=25,
        days_since_calving=60,
    )
    assert prob_thin < prob_normal


@pytest.mark.unit
def test_R7_high_bull_ratio_reduces_probability() -> None:
    """R7: bull_to_cow_ratio > 30 must yield a lower probability than ratio = 25.

    Above 30:1, bulls cannot cover all cows in an 18-hour estrus window,
    reducing effective daily conception probability.
    """
    prob_normal = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=60,
    )
    prob_high_ratio = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=50,
        days_since_calving=60,
    )
    assert prob_high_ratio < prob_normal


# ── R8: Aggregate season pregnancy rate ──────────────────────────────────────


@pytest.mark.unit
def test_R8_aggregate_season_pregnancy_rate_near_usda_benchmark() -> None:
    """R8: 1000 cows × 63-day season at BCS=5 and ratio=25 must achieve a pregnancy rate in [0.75, 0.99].

    The USDA benchmark is ~91.5% calved-per-cow-exposed (excluding stillbirth
    and preweaning mortality). The base_daily_prob in calculate_seasonal_conception_probability
    is calibrated for this target. Tolerance band [0.75, 0.99] is intentionally wide
    to accommodate RNG variance across different seeds.
    """
    random_seed(42)
    n_cows = 1000
    season_length = 63
    daily_prob = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=60,
    )
    import random

    conceived = sum(1 for _ in range(n_cows) if any(random.random() < daily_prob for _ in range(season_length)))
    pregnancy_rate = conceived / n_cows
    assert 0.75 <= pregnancy_rate <= 0.99, f"Expected seasonal pregnancy rate in [0.75, 0.99], got {pregnancy_rate:.3f}"


# ── R9–R10: Unimplemented protocol guards ────────────────────────────────────


@pytest.mark.unit
def test_R9_ai_seasonal_raises_not_implemented(mocker: MockerFixture) -> None:
    """R9: AI_SEASONAL protocol dispatch must raise NotImplementedError with a clear message.

    PR-B only implements NATURAL_SERVICE_SEASONAL. AI protocols are enum stubs
    that raise NotImplementedError to provide a clear path for future PRs.
    """
    from unittest.mock import MagicMock
    from RUFAS.biophysical.animal.animal import Animal
    from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents

    mocker.patch.object(AnimalConfig, "beef_reproduction_program", new=BeefReproductionProtocol.AI_SEASONAL)

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_COW
    animal.body_weight = 520.0
    animal.days_born = 730
    animal.breed = Breed.AN
    animal.sex = Sex.FEMALE
    animal.times_calved = 1
    animal.is_open = True
    animal.days_since_calving = 60
    animal.days_in_breeding_season = None
    animal.calf_at_side = None
    animal.dam = None
    animal.lactation_day = 0
    animal._breeding_weight_event_fired = False
    animal._days_in_pregnancy = 0
    animal._future_cull_date = None
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    animal.body_condition_score_9 = 5.0
    t = MagicMock()
    t.simulation_day = 100
    t.day_of_year = 120
    from datetime import date

    t.current_date = date(2025, 4, 30)

    with pytest.raises(NotImplementedError, match="AI_SEASONAL"):
        animal._beef_daily_reproduction_update(t)


@pytest.mark.unit
def test_R10_ai_controlled_breeding_raises_not_implemented(mocker: MockerFixture) -> None:
    """R10: AI_CONTROLLED_BREEDING protocol dispatch must raise NotImplementedError.

    Symmetric guard to R9 for the second unimplemented protocol.
    """
    from unittest.mock import MagicMock
    from RUFAS.biophysical.animal.animal import Animal
    from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents

    mocker.patch.object(AnimalConfig, "beef_reproduction_program", new=BeefReproductionProtocol.AI_CONTROLLED_BREEDING)

    animal: Animal = Animal.__new__(Animal)
    animal.animal_type = AnimalType.BEEF_COW
    animal.body_weight = 520.0
    animal.days_born = 730
    animal.breed = Breed.AN
    animal.sex = Sex.FEMALE
    animal.times_calved = 1
    animal.is_open = True
    animal.days_since_calving = 60
    animal.days_in_breeding_season = None
    animal.calf_at_side = None
    animal.dam = None
    animal.lactation_day = 0
    animal._breeding_weight_event_fired = False
    animal._days_in_pregnancy = 0
    animal._future_cull_date = None
    animal.events = AnimalEvents()
    animal.sold_at_day = None
    animal.cull_reason = ""
    animal.om = MagicMock()
    animal.body_condition_score_9 = 5.0
    t = MagicMock()
    t.simulation_day = 100
    t.day_of_year = 120
    from datetime import date

    t.current_date = date(2025, 4, 30)

    with pytest.raises(NotImplementedError, match="AI_CONTROLLED_BREEDING"):
        animal._beef_daily_reproduction_update(t)
