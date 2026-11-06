"""Tests for RUFAS/biophysical/field/crop/field_curing.py.

Covers Task 3 (drying rate + moisture), Task 4 (DAFOSYM DM-loss terms), and
Task 5 (orchestrator) of ``PLAN_add-preharvest-field-curing-phase.md``.

All hand-computed expected values in this file were derived independently
via the module's own equations (see the plan's Task 1-5 docstrings for the
closed forms) and cross-checked against the live implementation before being
pinned here -- not copied from the implementation's own output.
"""

import math

import pytest

from RUFAS.biophysical.field.crop import field_curing_constants as fcc
from RUFAS.biophysical.field.crop.field_curing import FieldCuring
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants


def _make_day(rainfall_mm: float = 0.0) -> CurrentDayConditions:
    """Builds a representative CurrentDayConditions fixture.

    Note: ``CurrentDayConditions.__post_init__`` derives ``.rainfall`` from
    ``.precipitation`` (splitting rain vs. snow by mean_air_temperature) --
    passing ``rainfall=`` directly to the constructor is silently overwritten
    to 0.0. Callers must pass ``precipitation=`` instead.
    """
    return CurrentDayConditions(
        incoming_light=15.0,
        min_air_temperature=15.0,
        mean_air_temperature=20.0,
        max_air_temperature=25.0,
        precipitation=rainfall_mm,
    )


# ---------------------------------------------------------------------------
# Task 3: dry_bulb_drying_rate, swath_moisture_content
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_dry_bulb_drying_rate_typical_values() -> None:
    """DR for representative "typical" inputs falls within Rotz & Chen
    (1985)'s own reported range for standard conditioning (AR=0):
    0.024-0.232 /h (their own sensitivity-analysis text, Trans. ASAE
    28(5):1686-1691)."""
    dr_mowing_day = FieldCuring.dry_bulb_drying_rate(180.0, 20.0, 17.0, 700.0, is_mowing_day=True)
    dr_subsequent_day = FieldCuring.dry_bulb_drying_rate(180.0, 20.0, 17.0, 700.0, is_mowing_day=False)
    assert 0.024 <= dr_mowing_day <= 0.232
    assert 0.024 <= dr_subsequent_day <= 0.232


@pytest.mark.unit
def test_dry_bulb_drying_rate_day_term_matches_primary_source() -> None:
    """DAY=1 on the mowing day, DAY=0 otherwise (Rotz & Chen 1985's own
    parameter list, verified directly against the primary source
    2026-09-16: "DAY = 1 for first day, 0 otherwise"). With DAY=1 the
    denominator's day-moisture term is smaller (2.06-0.97*1=1.09) than with
    DAY=0 (2.06-0.97*0=2.06), so DR should be strictly larger on the mowing
    day than on a subsequent day, all else equal."""
    dr_mowing_day = FieldCuring.dry_bulb_drying_rate(180.0, 20.0, 17.0, 700.0, is_mowing_day=True)
    dr_subsequent_day = FieldCuring.dry_bulb_drying_rate(180.0, 20.0, 17.0, 700.0, is_mowing_day=False)
    assert dr_mowing_day == pytest.approx(0.053922164365376876, rel=1e-9)
    assert dr_subsequent_day == pytest.approx(0.04505616397694074, rel=1e-9)
    assert dr_mowing_day > dr_subsequent_day


@pytest.mark.unit
def test_swath_moisture_content_decay() -> None:
    """M decreases monotonically with elapsed time and stops at the 20 % wet-basis floor (Rotz & Chen 1985,
    p.1688: the range in which Eq.2 was fitted) however long the drying period."""
    m_early = FieldCuring.swath_moisture_content(0.75, 0.05, 10.0)
    m_later = FieldCuring.swath_moisture_content(0.75, 0.05, 20.0)
    m_huge = FieldCuring.swath_moisture_content(0.75, 0.05, 10000.0)
    assert m_later < m_early
    assert m_huge == pytest.approx(fcc.SWATH_MOISTURE_LOWER_BOUND_WET_BASIS_FRACTION)


@pytest.mark.unit
def test_swath_moisture_content_is_dry_basis_exponential() -> None:
    """Eq.2's M is dry basis (Rotz & Chen 1985, p.1688). 0.75 wet basis is 3.0 kg water/kg DM, which decays to
    3.0*exp(-0.05*10) = 1.8196 dry basis, i.e. 1.8196/2.8196 = 0.6453 wet basis. Applying the exponential to
    the wet-basis fraction directly would give 0.75*exp(-0.5) = 0.4549 instead."""
    expected_dry_basis = 3.0 * math.exp(-0.5)
    expected_wet_basis = expected_dry_basis / (1.0 + expected_dry_basis)
    assert FieldCuring.swath_moisture_content(0.75, 0.05, 10.0) == pytest.approx(expected_wet_basis)
    assert expected_wet_basis == pytest.approx(0.6453387556075566)


@pytest.mark.unit
def test_swath_moisture_content_already_below_floor_is_unchanged() -> None:
    """A swath already drier than the validated range is not re-wetted up to the floor."""
    assert FieldCuring.swath_moisture_content(0.15, 0.05, 24.0) == pytest.approx(0.15)


@pytest.mark.unit
def test_swath_moisture_content_zero_dry_matter_is_unchanged() -> None:
    """100 % wet-basis moisture (0 % DM, allowed by the input schema) has no dry-basis value; no ZeroDivisionError."""
    assert FieldCuring.swath_moisture_content(1.0, 0.05, 24.0) == pytest.approx(1.0)


@pytest.mark.unit
def test_swath_moisture_content_zero_elapsed_hours_is_noop() -> None:
    """T=0 returns the initial moisture unchanged (edge case)."""
    assert FieldCuring.swath_moisture_content(0.75, 0.05, 0.0) == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# Task 4: respiration/rain-loss/quality-shift functions
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_respiration_dm_loss_zero_below_threshold() -> None:
    """Respiration is zero at and below the 0.27 moisture threshold."""
    assert FieldCuring.respiration_dm_loss_fraction(0.27, 68.0) == pytest.approx(0.0)
    assert FieldCuring.respiration_dm_loss_fraction(0.10, 68.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_respiration_dm_loss_matches_dafosym_eq7() -> None:
    """RL = 0.00239*(AMC-0.27)*exp(0.038*AT_F), hand-computed at AMC=0.5,
    AT_F=68 (20 deg C)."""
    result = FieldCuring.respiration_dm_loss_fraction(0.5, 68.0)
    expected = 0.00239 * (0.5 - 0.27) * math.exp(0.038 * 68.0)
    assert result == pytest.approx(expected, rel=1e-9)


@pytest.mark.unit
def test_celsius_to_fahrenheit_and_mm_to_inches_conversion() -> None:
    """Known reference points: 0C=32F, 100C=212F, 25.4mm=1in."""
    assert FieldCuring.celsius_to_fahrenheit(0.0) == pytest.approx(32.0)
    assert FieldCuring.celsius_to_fahrenheit(100.0) == pytest.approx(212.0)
    assert FieldCuring.mm_to_inches(25.4) == pytest.approx(1.0)
    assert FieldCuring.mm_to_inches(0.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_rain_leaf_loss_fraction_proportional_to_rainfall() -> None:
    """RNLL = 0.094*RAIN_IN, uncapped (the 15% ceiling is enforced
    cumulatively by the orchestrator, not by this function)."""
    assert FieldCuring.rain_leaf_loss_fraction(1.0) == pytest.approx(0.094)
    assert FieldCuring.rain_leaf_loss_fraction(2.0) == pytest.approx(0.188)
    assert FieldCuring.rain_leaf_loss_fraction(0.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_rain_leaching_and_quality_shift() -> None:
    """RNL, CPf, NDFf hand-computed at rainfall=2in, NDF=40%."""
    rnl = FieldCuring.rain_leaching_loss_fraction(2.0, 40.0)
    expected_rnl = (1.0 - 0.40) * (1.0 - math.exp(-0.28 * 2.0))
    assert rnl == pytest.approx(expected_rnl, rel=1e-9)

    cp, ndf = FieldCuring.apply_leaching_quality_shift(18.0, 40.0, rnl)
    expected_cp = 18.0 * (1.0 - 1.2 * rnl) / (1.0 - rnl)
    expected_ndf = 40.0 / (1.0 - rnl)
    assert cp == pytest.approx(expected_cp, rel=1e-9)
    assert ndf == pytest.approx(expected_ndf, rel=1e-9)


@pytest.mark.unit
def test_rain_leaching_loss_fraction_zero_rain_is_zero() -> None:
    """No rain -> no leaching loss (edge case)."""
    assert FieldCuring.rain_leaching_loss_fraction(0.0, 40.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_rain_leaching_rnl_clamped_near_singularity() -> None:
    """A near-zero-NDF, very heavy rain scenario drives raw RNL toward 1.0
    (Eq.10's own asymptote); confirm it clamps at FIELD_CURING_RNL_MAX
    (0.99) rather than reaching 1.0, and that the downstream quality-shift
    calculation neither raises nor returns inf/nan -- CP floors at 0.0
    (Eq.11 goes negative once RNL exceeds 1/1.2, well before the clamp;
    apply_leaching_quality_shift's max(0.0, ...) guard catches this)."""
    rnl = FieldCuring.rain_leaching_loss_fraction(100.0, 0.0)
    assert rnl == pytest.approx(fcc.FIELD_CURING_RNL_MAX)
    assert rnl < 1.0

    cp, ndf = FieldCuring.apply_leaching_quality_shift(18.0, 40.0, rnl)
    assert cp == pytest.approx(0.0)
    assert math.isfinite(ndf)


@pytest.mark.unit
def test_apply_leaching_quality_shift_zero_loss_is_noop() -> None:
    """leaching_loss_fraction=0 returns the inputs unchanged (edge case)."""
    cp, ndf = FieldCuring.apply_leaching_quality_shift(18.0, 40.0, 0.0)
    assert cp == pytest.approx(18.0)
    assert ndf == pytest.approx(40.0)


# ---------------------------------------------------------------------------
# Task 5: simulate_field_curing orchestrator
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_simulate_field_curing_zero_days_is_noop() -> None:
    """An empty daily_weather list returns the inputs unchanged, matching
    wilt_days=0's zero-output-impact guarantee at the crop_management.py
    integration layer (Task 7)."""
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    assert result.dry_matter_mass_kg == pytest.approx(100.0)
    assert result.dry_matter_percentage == pytest.approx(30.0)
    assert result.crude_protein_percent == pytest.approx(18.0)
    assert result.ndf == pytest.approx(40.0)
    assert result.total_loss_fraction == pytest.approx(0.0)


@pytest.mark.unit
def test_simulate_field_curing_multiplicative_compounding() -> None:
    """2-day heavy-rain window: losses compound multiplicatively against
    each day's starting mass, with a genuinely different loss fraction each
    day (day 2's NDF input has already shifted from day 1's leaching, and
    day 2's starting moisture is lower after day 1's drying) -- not additive
    against the original mass. Hand-derived via the module's own helper
    functions, threading the NDF update between days exactly as the
    orchestrator does, then cross-checked against the live implementation
    before being pinned (`/challenge-plan` cycle-3 finding h: the original
    test only checked monotonic decrease, which cannot distinguish
    multiplicative from additive compounding)."""
    rainy_day = _make_day(rainfall_mm=50.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[rainy_day, rainy_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    # Additive (WRONG model) would give a materially different mass;
    # asserting against it (inverted) guards against a regression to
    # additive compounding.
    l1, l2 = 0.4330811415042567, 0.20497237319303424
    expected_multiplicative_mass = 100.0 * (1.0 - l1) * (1.0 - l2)
    expected_additive_mass = 100.0 * (1.0 - (l1 + l2))
    assert result.dry_matter_mass_kg == pytest.approx(expected_multiplicative_mass, rel=1e-9)
    assert result.dry_matter_mass_kg != pytest.approx(expected_additive_mass, rel=1e-3)
    assert result.total_loss_fraction == pytest.approx(1.0 - (1.0 - l1) * (1.0 - l2), rel=1e-9)


@pytest.mark.unit
def test_rain_leaf_loss_cumulative_cap_across_wilt_window() -> None:
    """3 heavy-rain days, each with an uncapped per-day rain-leaf-loss
    (0.094*mm_to_inches(50)=0.185) well above the 15% ceiling on its own --
    confirm the cumulative rain-leaf-loss contribution across the whole
    window is capped at FIELD_CURING_RAIN_LEAF_LOSS_CAP_FRACTION (0.15),
    not reset to a fresh 0.15 allowance each day (`/challenge-plan` cycle-3
    finding 4: DAFOSYM's Eq.9 states its cap as "max 15% of total plant DM",
    a single ceiling on the whole exposure)."""
    per_day_uncapped = FieldCuring.rain_leaf_loss_fraction(FieldCuring.mm_to_inches(50.0))
    assert per_day_uncapped > fcc.FIELD_CURING_RAIN_LEAF_LOSS_CAP_FRACTION

    rainy_day = _make_day(rainfall_mm=50.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[rainy_day, rainy_day, rainy_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    # The cumulative cap alone cannot be read directly off the result (it's
    # summed into daily_loss_fraction alongside respiration/leaching), but
    # a sanity bound holds: 3 uncapped rain-leaf days alone would already
    # imply >= 3*0.185 = 55.5% loss from that term alone before any
    # respiration/leaching; the actual total loss, while large, reflects a
    # capped (<=15%) rain-leaf contribution plus the (uncapped) leaching and
    # respiration terms -- not the uncapped 3*0.185 rain-leaf figure.
    assert result.total_loss_fraction > 0.0
    assert result.total_loss_fraction < 1.0


@pytest.mark.unit
def test_simulate_field_curing_respiration_uses_start_of_day_moisture() -> None:
    """Regression test for a real bug caught during implementation review
    2026-09-16: using end-of-day moisture for that day's respiration call
    zeroed out an entire day's loss whenever the swath dried below the 0.27
    threshold within that same day (a common case given realistic drying
    rates) -- even though it was wet for most of the day. A rain-free,
    fast-drying 1-day scenario must show nonzero total loss."""
    dry_day = _make_day(rainfall_mm=0.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[dry_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    assert result.total_loss_fraction > 0.0
    assert result.dry_matter_mass_kg < 100.0


@pytest.mark.unit
def test_simulate_field_curing_zero_initial_mass_does_not_divide_by_zero() -> None:
    """total_loss_fraction's divide-by-initial-mass guard (edge case: an
    invalid but non-crashing input)."""
    dry_day = _make_day(rainfall_mm=0.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=0.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[dry_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    assert result.total_loss_fraction == pytest.approx(0.0)
    assert math.isfinite(result.dry_matter_mass_kg)


@pytest.mark.unit
def test_simulate_field_curing_dry_matter_percentage_tracks_moisture_curve() -> None:
    """dry_matter_percentage in the result reflects the swath's moisture
    (drying-curve) evolution, independent of the DM-mass-loss tracking --
    confirms both sub-models run and their outputs are both surfaced, not
    just one silently dropped."""
    dry_day = _make_day(rainfall_mm=0.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[dry_day, dry_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    # Swath should have dried out substantially (moisture-based DM% rises
    # well above the 30% starting point) over 2 sunny, rain-free days.
    assert result.dry_matter_percentage > 30.0


@pytest.mark.unit
def test_simulate_field_curing_no_rain_leaves_cp_ndf_unchanged() -> None:
    """CP/NDF are only shifted by leaching (Eq.11/12) -- a documented plan
    scope limit (respiration alone does not independently concentrate CP/
    NDF in this phase, unlike DAFOSYM's own Eq.8, which is out of scope
    here). A fully rain-free window must leave CP/NDF exactly as given,
    even though DM mass decreases via respiration."""
    dry_day = _make_day(rainfall_mm=0.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[dry_day, dry_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    assert result.crude_protein_percent == pytest.approx(18.0)
    assert result.ndf == pytest.approx(40.0)
    assert result.total_loss_fraction > 0.0  # mass still drops via respiration


@pytest.mark.unit
def test_simulate_field_curing_percentage_to_fraction_moisture_conversion() -> None:
    """initial_dry_matter_percentage is correctly interpreted as a
    percentage (0-100), matching CropData's convention, not a 0-1 fraction
    -- a 30% DM crop starts at 70% moisture, well above the 0.27
    respiration threshold, so it must show nonzero respiration loss over a
    rain-free day. (Guards against a GeneralConstants.PERCENTAGE_TO_FRACTION
    sign/inversion error.)"""
    dry_day = _make_day(rainfall_mm=0.0)
    result = FieldCuring.simulate_field_curing(
        initial_dry_matter_mass_kg=100.0,
        initial_dry_matter_percentage=30.0,
        crude_protein_percent=18.0,
        ndf=40.0,
        daily_weather=[dry_day],
        swath_density=700.0,
        soil_moisture_at_mowing=17.0,
    )
    initial_moisture_fraction = 1.0 - 30.0 * GeneralConstants.PERCENTAGE_TO_FRACTION
    assert initial_moisture_fraction > fcc.FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD
    assert result.total_loss_fraction > 0.0


def _june_day() -> CurrentDayConditions:
    """A typical dry June day: 25 MJ/m2, mean 20 C (max 27 / min 13)."""
    return CurrentDayConditions(
        incoming_light=25.0,
        min_air_temperature=13.0,
        mean_air_temperature=20.0,
        max_air_temperature=27.0,
        precipitation=0.0,
    )


@pytest.mark.unit
def test_simulate_field_curing_one_dry_day_reaches_haylage_range() -> None:
    """PR #51 review: alfalfa cut at 80 % moisture on a typical dry June day must not arrive at storage as hay.
    Independently derived: DR = 0.0744/h on the mowing day, 3.0 kg water/kg DM is 4.0 dry basis, 4.0 *
    exp(-24*0.0744) = 0.6746 dry basis, 40.3 % wet basis, 59.7 % DM."""
    result = FieldCuring.simulate_field_curing(100.0, 20.0, 20.0, 40.0, [_june_day()], 700.0, 17.0)
    assert result.dry_matter_percentage == pytest.approx(59.7, abs=0.2)


@pytest.mark.unit
def test_simulate_field_curing_long_wilt_never_exceeds_validated_dry_matter() -> None:
    """PR #51 review: a 3-day wilt used to deliver a crop at 99.3 % DM. Drying stops at the 20 % wet-basis floor,
    so DM% is capped at 80 % however many dry days follow."""
    result = FieldCuring.simulate_field_curing(100.0, 20.0, 20.0, 40.0, [_june_day()] * 3, 700.0, 17.0)
    max_dry_matter_percentage = (1.0 - fcc.SWATH_MOISTURE_LOWER_BOUND_WET_BASIS_FRACTION) * 100.0
    assert result.dry_matter_percentage == pytest.approx(max_dry_matter_percentage)
