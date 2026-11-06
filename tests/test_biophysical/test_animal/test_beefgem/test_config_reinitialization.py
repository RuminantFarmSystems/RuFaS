"""Config re-initialisation must reset every conditionally-parsed field.

Every ClassVar assigned as ``if (raw := cfg.get(key)) is not None: cls.field
= T(raw)`` leaves a stale value on a second initialisation call that omits
the key -- the class attribute was never touched, so it keeps whatever the
previous call set. This is a latent trap for any process that re-initialises
AnimalConfig more than once, such as the scenario runner or a test suite.

Ten fields carry this pattern: five predate BeefGEM (stocker weights, max
days, target ADG, diet system), five were added by it (finishing system,
limit-feed percentage, compensatory gain gate, relative humidity,
conception rate multiplier). All ten are fixed together, and covered here
together, so the module has one convention rather than two.
"""

from __future__ import annotations

import math
from typing import Iterator

import pytest

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import FinishingSystem, StockerDietSystem
from RUFAS.biophysical.animal.reproduction.beef_reproduction import calculate_seasonal_conception_probability

_ALL_FIELDS = (
    "stocker_entry_weight",
    "stocker_exit_weight",
    "stocker_max_days",
    "stocker_target_adg",
    "stocker_diet_system",
    "finishing_system",
    "stocker_limit_feed_pct",
    "enable_compensatory_gain",
    "relative_humidity_pct",
    "beef_conception_rate_multiplier",
)


@pytest.fixture(autouse=True)
def _restore_all_fields() -> Iterator[None]:
    """Save and restore every field this suite may touch."""
    saved = {name: getattr(AnimalConfig, name) for name in _ALL_FIELDS}
    yield
    for name, value in saved.items():
        setattr(AnimalConfig, name, value)


# ---------------------------------------------------------------------------
# Each field resets to its declared default when the key is absent
# ---------------------------------------------------------------------------


@pytest.mark.component
def test_stocker_entry_weight_resets_on_reinit() -> None:
    """A stale entry_weight from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"entry_weight": 999.0})
    assert AnimalConfig.stocker_entry_weight == pytest.approx(999.0)
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_entry_weight == pytest.approx(AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG)


@pytest.mark.component
def test_stocker_exit_weight_resets_on_reinit() -> None:
    """A stale exit_weight from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"exit_weight": 999.0})
    assert AnimalConfig.stocker_exit_weight == pytest.approx(999.0)
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_exit_weight == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG)


@pytest.mark.component
def test_stocker_max_days_resets_on_reinit() -> None:
    """A stale max_days from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"max_days": 999})
    assert AnimalConfig.stocker_max_days == 999
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_max_days == AnimalModuleConstants.STOCKER_MAX_DAYS


@pytest.mark.component
def test_stocker_target_adg_resets_on_reinit() -> None:
    """A stale target_adg from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"target_adg": 9.0})
    assert AnimalConfig.stocker_target_adg == pytest.approx(9.0)
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_target_adg == pytest.approx(AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D)


@pytest.mark.component
def test_stocker_diet_system_resets_on_reinit() -> None:
    """A stale diet system from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"stocker_diet_system": "drylot_forage"})
    first: StockerDietSystem = AnimalConfig.stocker_diet_system
    assert first is StockerDietSystem.DRYLOT_FORAGE
    AnimalConfig._initialize_beef_stocker_config({})
    second: StockerDietSystem = AnimalConfig.stocker_diet_system
    assert second is StockerDietSystem.PASTURE


@pytest.mark.component
def test_stocker_limit_feed_pct_resets_on_reinit() -> None:
    """A stale limit_feed_pct from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"limit_feed_pct": 42.0})
    assert AnimalConfig.stocker_limit_feed_pct == pytest.approx(42.0)
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.stocker_limit_feed_pct == pytest.approx(AnimalModuleConstants.STOCKER_DEFAULT_LIMIT_FEED_PCT)


@pytest.mark.component
def test_enable_compensatory_gain_resets_on_reinit() -> None:
    """A stale True from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_stocker_config({"enable_compensatory_gain": True})
    assert AnimalConfig.enable_compensatory_gain is True
    AnimalConfig._initialize_beef_stocker_config({})
    assert AnimalConfig.enable_compensatory_gain is False


@pytest.mark.component
def test_finishing_system_resets_on_reinit() -> None:
    """A stale finishing system from a prior call must not survive an empty config."""
    AnimalConfig._initialize_feedlot_finishing_system({"finishing_system": "grass_fed"})
    first: FinishingSystem = AnimalConfig.finishing_system
    assert first is FinishingSystem.GRASS_FED
    AnimalConfig._initialize_feedlot_finishing_system({})
    second: FinishingSystem = AnimalConfig.finishing_system
    assert second is FinishingSystem.GRAIN_FED


@pytest.mark.component
def test_relative_humidity_resets_on_reinit() -> None:
    """A stale humidity from a prior call must not survive an empty config."""
    AnimalConfig._initialize_relative_humidity({"relative_humidity_pct": 55.0})
    assert AnimalConfig.relative_humidity_pct == pytest.approx(55.0)
    AnimalConfig._initialize_relative_humidity({})
    assert AnimalConfig.relative_humidity_pct is None


@pytest.mark.component
def test_conception_rate_multiplier_resets_on_reinit() -> None:
    """A stale multiplier from a prior call must not survive an empty config."""
    AnimalConfig._initialize_beef_cow_calf_config({"beef_cow_calf": {"conception_rate_multiplier": 2.0}})
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(2.0)
    AnimalConfig._initialize_beef_cow_calf_config({})
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# conception_rate_multiplier validation -- the dead check starts firing
# ---------------------------------------------------------------------------


@pytest.mark.component
@pytest.mark.parametrize("bad_value", [-1.0, 0.0, float("nan")])
def test_negative_zero_or_nan_multiplier_raises_at_parse_time(bad_value: float) -> None:
    """A bad multiplier must be rejected before it is ever assigned.

    validate_beef_cow_calf_config already contains this check; it was dead
    because the merged dict it validates never carried the key.
    """
    with pytest.raises(ValueError, match="conception_rate_multiplier"):
        AnimalConfig._initialize_beef_cow_calf_config({"beef_cow_calf": {"conception_rate_multiplier": bad_value}})


@pytest.mark.component
def test_rejected_multiplier_never_reaches_the_classvar() -> None:
    """A raise at parse time must leave the previous ClassVar value untouched."""
    AnimalConfig.beef_conception_rate_multiplier = 1.0
    with pytest.raises(ValueError):
        AnimalConfig._initialize_beef_cow_calf_config({"beef_cow_calf": {"conception_rate_multiplier": -5.0}})
    assert AnimalConfig.beef_conception_rate_multiplier == pytest.approx(1.0)


@pytest.mark.component
@pytest.mark.regression
def test_nan_multiplier_can_no_longer_reach_the_reproduction_function() -> None:
    """Closes the silent-sterilisation path: a NaN multiplier never gets far
    enough to reach calculate_seasonal_conception_probability.

    Before this fix, a NaN multiplier passed parse-time validation unchecked,
    reached the ClassVar, and would have made every conception probability
    NaN -- silently sterilising the herd rather than raising.
    """
    with pytest.raises(ValueError, match="conception_rate_multiplier"):
        AnimalConfig._initialize_beef_cow_calf_config({"beef_cow_calf": {"conception_rate_multiplier": float("nan")}})

    prob = calculate_seasonal_conception_probability(
        body_condition_score=5.0,
        bull_to_cow_ratio=25,
        days_since_calving=90,
        conception_rate_multiplier=AnimalConfig.beef_conception_rate_multiplier,
    )
    assert math.isfinite(prob)
