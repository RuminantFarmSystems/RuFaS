"""Tests for the beef herd summary reporter.

Verifies:
- get_beef_herd_summary returns exactly four keys
- An empty herd returns 0.0 for each rather than raising
- calf_crop_pct, replacement_rate_pct and mean_cow_bcs against known herds
- The survivor bias in calf_crop_pct, pinned so it stays visible
- mean_calving_interval_days across the full event history
- Cows with fewer than two calvings are excluded from the interval mean
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.herd_manager import HerdManager

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EXPECTED_KEYS: frozenset[str] = frozenset(
    {
        "calf_crop_pct",
        "mean_calving_interval_days",
        "replacement_rate_pct",
        "mean_cow_bcs",
    }
)

_DEFAULT_BCS: float = 5.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cow(
    times_calved: int = 0,
    body_condition_score_9: float = _DEFAULT_BCS,
    calving_ages: tuple[int, ...] = (),
) -> Animal:
    """Construct a minimal BEEF_COW carrying only what the summary reads.

    Parameters
    ----------
    times_calved : int
        Lifetime calving count.
    body_condition_score_9 : float
        Body condition on the 1-9 beef scale.
    calving_ages : tuple[int, ...]
        Ages in days at which BEEF_CALVING events were recorded.

    Returns
    -------
    Animal
        A bare BEEF_COW with the summary-relevant attributes set.

    """
    cow: Animal = Animal.__new__(Animal)
    cow.animal_type = AnimalType.BEEF_COW
    cow.times_calved = times_calved
    cow.body_condition_score_9 = body_condition_score_9
    cow.events = AnimalEvents()
    for age in calving_ages:
        cow.events.add_event(age, 0, animal_constants.BEEF_CALVING)
    return cow


def _make_heifer() -> Animal:
    """Construct a minimal BEEF_HEIFER_REPLACEMENT."""
    heifer: Animal = Animal.__new__(Animal)
    heifer.animal_type = AnimalType.BEEF_HEIFER_REPLACEMENT
    return heifer


def _make_herd(cows: list[Animal] | None = None, heifers: list[Animal] | None = None) -> MagicMock:
    """Return a herd manager stub exposing only the two cohort lists the summary reads.

    spec=HerdManager blocks any attribute read the test never set and that
    is not a real HerdManager attribute, so a typo or a rename in the
    reporter surfaces as an AttributeError rather than a fresh silent
    MagicMock. Assignment itself is unrestricted by plain spec=, so setting
    beef_cows/beef_replacement_heifers here works even though they are
    instance attributes rather than class-level ones.
    """
    herd: MagicMock = MagicMock(spec=HerdManager)
    herd.beef_cows = cows if cows is not None else []
    herd.beef_replacement_heifers = heifers if heifers is not None else []
    return herd


def _summary(cows: list[Animal] | None = None, heifers: list[Animal] | None = None) -> dict[str, float]:
    """Build a herd and return its summary."""
    return AnimalModuleReporter.get_beef_herd_summary(_make_herd(cows, heifers))


# ---------------------------------------------------------------------------
# Shape — exactly four keys
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_summary_returns_exactly_the_four_expected_keys() -> None:
    """The summary must carry the four implemented metrics and nothing else."""
    assert set(_summary([_make_cow()]).keys()) == _EXPECTED_KEYS


@pytest.mark.unit
@pytest.mark.parametrize(
    "cut_key",
    [
        "mean_stocker_adg_kg_d",
        "mean_feedlot_adg_kg_d",
        "mean_feedlot_days_on_feed",
        "total_enteric_ch4_g_d",
    ],
)
def test_summary_omits_the_unwired_metrics(cut_key: str) -> None:
    """The four metrics with no backing state must be absent, not zero.

    Returning them as 0.0 would be indistinguishable from a real zero. They are
    cut until the exit-performance accumulator exists.
    """
    assert cut_key not in _summary([_make_cow()])


@pytest.mark.unit
def test_summary_values_are_all_floats() -> None:
    """Every value must be a float, as the return annotation promises."""
    for value in _summary([_make_cow(times_calved=2, calving_ages=(1000, 1365))]).values():
        assert isinstance(value, float)


# ---------------------------------------------------------------------------
# Empty herd — zeros, not exceptions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_empty_herd_returns_zero_for_every_metric() -> None:
    """An empty herd must return 0.0 for all four metrics without raising."""
    summary = _summary()
    assert set(summary.keys()) == _EXPECTED_KEYS
    for value in summary.values():
        assert value == pytest.approx(0.0)


@pytest.mark.unit
def test_heifers_without_cows_does_not_divide_by_zero() -> None:
    """Replacement heifers with no cows must not raise on the zero denominator."""
    summary = _summary(cows=[], heifers=[_make_heifer(), _make_heifer()])
    assert summary["replacement_rate_pct"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# calf_crop_pct
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_calf_crop_pct_against_a_known_herd() -> None:
    """Four cows with six calvings between them give 150%."""
    cows = [
        _make_cow(times_calved=2),
        _make_cow(times_calved=2),
        _make_cow(times_calved=1),
        _make_cow(times_calved=1),
    ]
    assert _summary(cows)["calf_crop_pct"] == pytest.approx(150.0)


@pytest.mark.unit
def test_calf_crop_pct_is_zero_when_no_cow_has_calved() -> None:
    """Cows that have never calved give a zero calf crop, not a division error."""
    assert _summary([_make_cow(), _make_cow()])["calf_crop_pct"] == pytest.approx(0.0)


@pytest.mark.unit
def test_calf_crop_pct_survivor_bias_is_upward() -> None:
    """Removing a barren cow mid-run raises the reported figure.

    Pins the documented bias: the denominator counts cows currently in the herd,
    not cows exposed during the breeding season. A cow culled after failing to
    conceive leaves beef_cows, so she stops depressing the ratio and the figure
    rises even though no extra calf was born.
    """
    productive = [_make_cow(times_calved=1), _make_cow(times_calved=1)]
    barren = _make_cow(times_calved=0)

    with_barren_still_present = _summary(productive + [barren])["calf_crop_pct"]
    after_barren_culled = _summary(productive)["calf_crop_pct"]

    assert with_barren_still_present == pytest.approx(200.0 / 3.0)
    assert after_barren_culled == pytest.approx(100.0)
    assert after_barren_culled > with_barren_still_present


# ---------------------------------------------------------------------------
# replacement_rate_pct and mean_cow_bcs
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_replacement_rate_against_known_counts() -> None:
    """Five heifers against twenty cows gives 25%."""
    summary = _summary(cows=[_make_cow() for _ in range(20)], heifers=[_make_heifer() for _ in range(5)])
    assert summary["replacement_rate_pct"] == pytest.approx(25.0)


@pytest.mark.unit
def test_mean_cow_bcs_against_known_scores() -> None:
    """The mean of 4.0, 5.0 and 6.0 is 5.0."""
    cows = [
        _make_cow(body_condition_score_9=4.0),
        _make_cow(body_condition_score_9=5.0),
        _make_cow(body_condition_score_9=6.0),
    ]
    assert _summary(cows)["mean_cow_bcs"] == pytest.approx(5.0)


@pytest.mark.unit
def test_mean_cow_bcs_ignores_replacement_heifers() -> None:
    """Only cows contribute to mean BCS; heifers are a separate cohort."""
    cows = [_make_cow(body_condition_score_9=6.0)]
    assert _summary(cows, heifers=[_make_heifer()])["mean_cow_bcs"] == pytest.approx(6.0)


# ---------------------------------------------------------------------------
# mean_calving_interval_days
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_calving_interval_with_three_calvings() -> None:
    """Calvings at 1000, 1365 and 1730 days give two 365-day intervals."""
    cow = _make_cow(times_calved=3, calving_ages=(1000, 1365, 1730))
    assert _summary([cow])["mean_calving_interval_days"] == pytest.approx(365.0)


@pytest.mark.unit
def test_calving_interval_averages_uneven_gaps() -> None:
    """Calvings at 1000, 1300 and 1700 give intervals of 300 and 400, mean 350."""
    cow = _make_cow(times_calved=3, calving_ages=(1000, 1300, 1700))
    assert _summary([cow])["mean_calving_interval_days"] == pytest.approx(350.0)


@pytest.mark.unit
def test_calving_interval_excludes_cows_with_one_calving() -> None:
    """A first-calf cow contributes no interval and must not drag the mean down."""
    cows = [
        _make_cow(times_calved=3, calving_ages=(1000, 1365, 1730)),
        _make_cow(times_calved=1, calving_ages=(900,)),
    ]
    assert _summary(cows)["mean_calving_interval_days"] == pytest.approx(365.0)


@pytest.mark.unit
def test_calving_interval_excludes_cows_with_no_calvings() -> None:
    """Cows that have never calved contribute nothing to the interval mean."""
    cows = [
        _make_cow(times_calved=2, calving_ages=(1000, 1400)),
        _make_cow(times_calved=0),
    ]
    assert _summary(cows)["mean_calving_interval_days"] == pytest.approx(400.0)


@pytest.mark.unit
def test_calving_interval_is_zero_when_no_cow_has_two_calvings() -> None:
    """With no eligible cow the interval is 0.0, not a division error."""
    cows = [_make_cow(times_calved=1, calving_ages=(900,)), _make_cow(times_calved=0)]
    assert _summary(cows)["mean_calving_interval_days"] == pytest.approx(0.0)


@pytest.mark.unit
def test_calving_interval_averages_across_several_cows() -> None:
    """Intervals from different cows are pooled, not averaged per cow first."""
    cows = [
        _make_cow(times_calved=2, calving_ages=(1000, 1300)),
        _make_cow(times_calved=2, calving_ages=(1000, 1400)),
    ]
    assert _summary(cows)["mean_calving_interval_days"] == pytest.approx(350.0)
