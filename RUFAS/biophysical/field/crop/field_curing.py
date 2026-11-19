"""Opt-in pre-harvest field-curing phase (cutting -> storage).

Implements the swath drying-rate/moisture model of Rotz & Chen (1985) and the
DAFOSYM respiration/rain-loss/quality-shift terms of Rotz, Black, Mertens &
Buckmaster (1989), at RuFaS's daily weather resolution
(``CurrentDayConditions`` via ``Weather.get_conditions_series``). See
``field_curing_constants.py`` for every named coefficient's provenance and
``docs/scientific/crop_and_soil.tex`` (tags SC.CRP.79-85) for the full
equation registry.

Documented limitations:

1. Day/night temperature mapping -- DAFOSYM's respiration term (Eq.7) is
   defined over 12-hour day/night periods, each driven by that period's
   *average* temperature. RuFaS's weather is daily-resolution only and
   carries no true 12h-average split, so this module stands in
   ``CurrentDayConditions.max_air_temperature`` for the day period and
   ``CurrentDayConditions.min_air_temperature`` for the night period. Using
   extremes instead of averages systematically biases day-period respiration
   loss upward and night-period respiration loss downward -- a real
   approximation, not a neutral one, accepted here because no true within-day
   average is available from RuFaS's daily weather.

2. Quality (CP/NDF) concentration is only modeled under leaching
   (`FieldCuring.apply_leaching_quality_shift`, DAFOSYM Eq.11/12) -- DAFOSYM's
   respiration-driven quality-concentration equation (its own Eq.8,
   Qf = Qi/(1-RL), applied alongside Eq.7 each period) is deliberately out
   of scope for this phase. A rain-free wilt window therefore reduces DM
   mass via respiration without changing CP/NDF percentages at all, even
   though the real crop's quality would concentrate somewhat as mass is
   lost. Not implemented here; a documented scope limit, not an oversight.

3. Microbial-activity and tedding DM loss (SimForQ, Barr et al. 1994/95)
   and mechanical/machine-operation losses (mowing/raking/baler, Rotz 1995)
   are out of scope for this phase entirely -- SimForQ is hourly-native and
   RuFaS's weather is daily-only (using it would require an unsourced
   diurnal disaggregation); mechanical losses are sourced elsewhere but held
   for a separate follow-up. Only DAFOSYM respiration/rain-leaf/leaching and
   the Rotz & Chen (1985) drying curve are implemented here.
"""

import math
from dataclasses import dataclass

from RUFAS.biophysical.field.crop import field_curing_constants as fcc
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.general_constants import GeneralConstants

_DRYING_RATE_DAY_TERM_MOWING_DAY: float = 1.0
"""DAY value (Eq.5's DAY term) on the day the crop is mowed. Rotz & Chen
(1985) state this plainly in their own parameter list (Trans. ASAE
28(5):1686-1691, p.1689, under Eq.3): "DAY = 1 for first day, 0 otherwise" --
a boolean flag, not a running day count."""

_DRYING_RATE_DAY_TERM_SUBSEQUENT_DAY: float = 0.0
"""DAY value (Eq.5's DAY term) on every day after the mowing day -- see
_DRYING_RATE_DAY_TERM_MOWING_DAY above for the source."""


@dataclass
class FieldCuringResult:
    """
    Outcome of a multi-day field-curing simulation.

    Attributes
    ----------
    dry_matter_mass_kg : float
        DM mass after curing (kg).
    dry_matter_percentage : float
        DM percentage after curing.
    crude_protein_percent : float
        CP percentage after curing.
    ndf : float
        NDF percentage after curing.
    total_loss_fraction : float
        Cumulative fractional DM loss over the whole wilt window.
    """

    dry_matter_mass_kg: float
    dry_matter_percentage: float
    crude_protein_percent: float
    ndf: float
    total_loss_fraction: float


class FieldCuring:
    """
    Opt-in pre-harvest field-curing phase (cutting -> storage) formulas.

    Groups the swath drying-rate/moisture model of Rotz & Chen (1985) and the
    DAFOSYM respiration/rain-loss/quality-shift terms of Rotz, Black, Mertens
    & Buckmaster (1989) as ``@staticmethod``s, matching the class+``@staticmethod``
    convention used elsewhere under ``RUFAS/biophysical/field/`` (e.g.
    ``heat_units.py``, ``leaf_area_index.py``, ``biomass_allocation.py``).
    See the module docstring above for documented limitations and
    ``field_curing_constants.py`` for every named coefficient's provenance.
    """

    @staticmethod
    def dry_bulb_drying_rate(
        solar_insolation_w_m2: float,
        dry_bulb_temp_c: float,
        soil_moisture_at_mowing: float,
        swath_density: float,
        is_mowing_day: bool,
        chemical_application_rate: float = 0.0,
    ) -> float:
        """
        Computes the swath drying-rate constant DR for one day.

        Parameters
        ----------
        solar_insolation_w_m2 : float
            Solar insolation, W/m2. Must be pre-converted by the caller from
            RuFaS's ``CurrentDayConditions.incoming_light`` (MJ/m2/day) via
            ``field_curing_constants.MJ_PER_M2_DAY_TO_W_PER_M2`` -- this
            function does not accept the raw MJ/m2 value.
        dry_bulb_temp_c : float
            Dry-bulb air temperature, deg C (Eq.5's DB is in deg C; see
            ``field_curing_constants.DRYING_RATE_DRY_BULB_COEFFICIENT``).
        soil_moisture_at_mowing : float
            Soil moisture, % dry basis.
        swath_density : float
            Swath density, g/m2.
        is_mowing_day : bool
            True on the day the crop is cut, False on every subsequent day.
        chemical_application_rate : float, default 0.0
            Chemical conditioning application rate, g solution/g DM. 0.0 (no
            chemical conditioning) is the only case RuFaS currently supports.

        Returns
        -------
        float
            Drying-rate constant DR, 1/h.

        Notes
        -----
        DR = [SI*(1+9.30*AR) + 5.42*DB] /
             [66.4*SM + SD*(2.06-0.97*DAY)*(1.55+21.9*AR) + 3037]

        References
        ----------
        [SC.CRP.79] Rotz & Chen (1985), "Alfalfa Drying Model for the Field
        Environment," Trans. ASAE 28(5):1686-1691, Eq.5, p.1689
        (dry-bulb-temperature form, chosen over the paper's Eq.4 VPD form
        because RuFaS tracks no humidity/VPD anywhere).

        """
        day_term = _DRYING_RATE_DAY_TERM_MOWING_DAY if is_mowing_day else _DRYING_RATE_DAY_TERM_SUBSEQUENT_DAY
        numerator = (
            solar_insolation_w_m2 * (1.0 + fcc.DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT * chemical_application_rate)
            + fcc.DRYING_RATE_DRY_BULB_COEFFICIENT * dry_bulb_temp_c
        )
        application_term = (
            fcc.DRYING_RATE_APPLICATION_DENOMINATOR_INTERCEPT
            + fcc.DRYING_RATE_APPLICATION_DENOMINATOR_SLOPE * chemical_application_rate
        )
        day_moisture_term = fcc.DRYING_RATE_DAY_INTERCEPT - fcc.DRYING_RATE_DAY_SLOPE * day_term
        denominator = (
            fcc.DRYING_RATE_SOIL_MOISTURE_COEFFICIENT * soil_moisture_at_mowing
            + swath_density * day_moisture_term * application_term
            + fcc.DRYING_RATE_DENOMINATOR_CONSTANT
        )
        return numerator / denominator

    @staticmethod
    def swath_moisture_content(
        initial_moisture_fraction: float, drying_rate_per_hour: float, elapsed_hours: float
    ) -> float:
        """
        Computes swath moisture content after an elapsed drying time.

        Parameters
        ----------
        initial_moisture_fraction : float
            Wet-basis moisture fraction (0-1) at the start of the period.
        drying_rate_per_hour : float
            Drying-rate constant DR, 1/h (see `FieldCuring.dry_bulb_drying_rate`).
        elapsed_hours : float
            Elapsed time since ``initial_moisture_fraction``, hours.

        Returns
        -------
        float
            Wet-basis moisture fraction (0-1) after ``elapsed_hours``. Never below
            ``SWATH_MOISTURE_LOWER_BOUND_WET_BASIS_FRACTION`` (20 % wet basis), or below the initial moisture
            if that was already drier.

        Notes
        -----
        Eq.2 is written in dry-basis moisture, M = Me + (M0 - Me)*exp(-DR*T) with Me = 0, so the wet-basis
        input is converted (M = Mwb/(1-Mwb)), dried, and converted back (Mwb = M/(1+M)). Applying Eq.2 to the
        wet-basis fraction directly overstates drying: 80 % wet basis is 4.0 kg water/kg DM, not 0.8.

        The result is floored at 20 % wet basis, the lower end of the range in which Rotz & Chen fitted and
        validated Eq.2. Below it the equation is unvalidated and would otherwise dry the swath toward 0 %
        moisture.

        A swath at 100 % wet-basis moisture (0 % dry matter, which the input schema permits) has no dry-basis
        value, so it is returned unchanged.

        References
        ----------
        [SC.CRP.80] Rotz & Chen (1985), Trans. ASAE 28(5):1686-1691, Eq.1-2 and the moisture-basis notation,
        p.1688.

        """
        if initial_moisture_fraction >= 1.0:
            return initial_moisture_fraction
        equilibrium = fcc.SWATH_MOISTURE_EQUILIBRIUM_FRACTION
        initial_dry_basis = initial_moisture_fraction / (1.0 - initial_moisture_fraction)
        dried_dry_basis = equilibrium + (initial_dry_basis - equilibrium) * math.exp(
            -drying_rate_per_hour * elapsed_hours
        )
        dried_wet_basis = dried_dry_basis / (1.0 + dried_dry_basis)
        floor = min(initial_moisture_fraction, fcc.SWATH_MOISTURE_LOWER_BOUND_WET_BASIS_FRACTION)
        return max(dried_wet_basis, floor)

    @staticmethod
    def respiration_dm_loss_fraction(avg_moisture_wet_basis_fraction: float, avg_temp_f: float) -> float:
        """
        Computes DAFOSYM's respiration dry-matter loss for one 12h period.

        Parameters
        ----------
        avg_moisture_wet_basis_fraction : float
            Average wet-basis moisture fraction (0-1) over the period (AMC).
        avg_temp_f : float
            Average air temperature over the period, deg F (AT).

        Returns
        -------
        float
            Fractional DM loss over the period. 0.0 at or below the 0.27
            wet-basis moisture threshold (respiration cessation).

        Notes
        -----
        RL = 0.00239*(AMC-0.27)*exp(0.038*AT), zero for AMC <= 0.27.

        References
        ----------
        [SC.CRP.81] Rotz, Black, Mertens & Buckmaster (1989), "DAFOSYM," Eq.7,
        p.86.

        """
        if avg_moisture_wet_basis_fraction <= fcc.FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD:
            return 0.0
        return (
            fcc.FIELD_CURING_RESPIRATION_COEFFICIENT
            * (avg_moisture_wet_basis_fraction - fcc.FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD)
            * math.exp(fcc.FIELD_CURING_RESPIRATION_TEMP_COEFFICIENT_F * avg_temp_f)
        )

    @staticmethod
    def rain_leaf_loss_fraction(rainfall_in: float) -> float:
        """
        Computes DAFOSYM's rain-induced leaf dry-matter loss for one rainy day.

        Parameters
        ----------
        rainfall_in : float
            Rainfall over the day, inches.

        Returns
        -------
        float
            Fractional leaf DM loss for the day, uncapped -- the 15% ceiling on
            cumulative loss across the whole wilt window is enforced by the
            orchestrator (`FieldCuring.simulate_field_curing`), not by this function.

        Notes
        -----
        RNLL = 0.094*RAIN_IN.

        References
        ----------
        [SC.CRP.82] Rotz, Black, Mertens & Buckmaster (1989), "DAFOSYM," Eq.9,
        p.86.

        """
        return fcc.FIELD_CURING_RAIN_LEAF_LOSS_COEFFICIENT * rainfall_in

    @staticmethod
    def rain_leaching_loss_fraction(rainfall_in: float, ndf_pct: float) -> float:
        """
        Computes DAFOSYM's rain-leaching dry-matter loss for one rainy day.

        Parameters
        ----------
        rainfall_in : float
            Rainfall over the day, inches.
        ndf_pct : float
            Neutral detergent fibre, percent (0-100) -- matches
            ``CropData.ndf_at_harvest``'s convention, not a 0-1 fraction.

        Returns
        -------
        float
            Fractional leaching DM loss for the day (RNL), clamped to
            ``field_curing_constants.FIELD_CURING_RNL_MAX`` as a numerical
            guard against the division singularity in
            `FieldCuring.apply_leaching_quality_shift`'s Eq.11.

        Notes
        -----
        RNL = (1-NDF)*(1-exp(-0.28*RAIN_IN)), where NDF is the 0-1 fraction
        (``ndf_pct * GeneralConstants.PERCENTAGE_TO_FRACTION`` -- the existing
        codebase idiom for this conversion, not an inline ``/100``).

        References
        ----------
        [SC.CRP.83] Rotz, Black, Mertens & Buckmaster (1989), "DAFOSYM," Eq.10,
        p.86.

        """
        ndf_fraction = ndf_pct * GeneralConstants.PERCENTAGE_TO_FRACTION
        raw_rnl = (1.0 - ndf_fraction) * (1.0 - math.exp(-fcc.FIELD_CURING_LEACHING_RAIN_COEFFICIENT * rainfall_in))
        return min(raw_rnl, fcc.FIELD_CURING_RNL_MAX)

    @staticmethod
    def apply_leaching_quality_shift(
        crude_protein_pct: float, ndf_pct: float, leaching_loss_fraction: float
    ) -> tuple[float, float]:
        """
        Applies DAFOSYM's leaching-driven quality shift to CP and NDF.

        Parameters
        ----------
        crude_protein_pct : float
            Crude protein, percent (0-100), before this day's leaching.
        ndf_pct : float
            Neutral detergent fibre, percent (0-100), before this day's
            leaching.
        leaching_loss_fraction : float
            Fractional leaching DM loss for the day (RNL), from
            `FieldCuring.rain_leaching_loss_fraction`.

        Returns
        -------
        tuple[float, float]
            ``(new_cp_pct, new_ndf_pct)``, both percent (0-100). Unchanged if
            ``leaching_loss_fraction <= 0``. CP is floored at 0.0 -- Eq.11 goes
            negative once RNL exceeds 1/1.2 (~0.833), well before
            ``FIELD_CURING_RNL_MAX``'s division-singularity guard is reached.

        Notes
        -----
        CPf = CPi*(1-1.2*RNL)/(1-RNL); NDFf = NDFi/(1-RNL).

        References
        ----------
        [SC.CRP.84] Rotz, Black, Mertens & Buckmaster (1989), "DAFOSYM," Eq.11
        (CP) and Eq.12 (NDF), p.86.

        """
        if leaching_loss_fraction <= 0.0:
            return crude_protein_pct, ndf_pct
        remaining_dm_fraction = 1.0 - leaching_loss_fraction
        new_cp_pct = (
            crude_protein_pct
            * (1.0 - fcc.FIELD_CURING_LEACHING_CP_MULTIPLIER * leaching_loss_fraction)
            / remaining_dm_fraction
        )
        new_ndf_pct = ndf_pct / remaining_dm_fraction
        return max(0.0, new_cp_pct), new_ndf_pct

    @staticmethod
    def celsius_to_fahrenheit(temp_c: float) -> float:
        """
        Converts a Celsius temperature to Fahrenheit.

        Parameters
        ----------
        temp_c : float
            Temperature, deg C.

        Returns
        -------
        float
            Temperature, deg F.

        Notes
        -----
        Used to convert RuFaS's Celsius weather data for DAFOSYM's Eq.7, which
        is Fahrenheit-calibrated.

        References
        ----------
        ``field_curing_constants.py``'s ``CELSIUS_TO_FAHRENHEIT_SCALE``/
        ``_OFFSET``.

        """
        return temp_c * fcc.CELSIUS_TO_FAHRENHEIT_SCALE + fcc.CELSIUS_TO_FAHRENHEIT_OFFSET

    @staticmethod
    def mm_to_inches(rainfall_mm: float) -> float:
        """
        Converts a millimeter rainfall value to inches.

        Parameters
        ----------
        rainfall_mm : float
            Rainfall, mm.

        Returns
        -------
        float
            Rainfall, inches.

        Notes
        -----
        Used to convert RuFaS's mm weather data for DAFOSYM's Eq.9/10, which
        are inches-calibrated.

        References
        ----------
        ``field_curing_constants.py``'s ``MM_TO_INCHES_DIVISOR``.

        """
        return rainfall_mm / fcc.MM_TO_INCHES_DIVISOR

    @staticmethod
    def _day_drying_rate(
        weather: CurrentDayConditions,
        swath_density: float,
        soil_moisture_at_mowing: float,
        is_mowing_day: bool,
    ) -> float:
        """
        Computes one day's drying-rate constant DR from that day's weather.

        Parameters
        ----------
        weather : CurrentDayConditions
            That day's weather (uses ``incoming_light``, ``mean_air_temperature``).
        swath_density : float
            Swath density, g/m2.
        soil_moisture_at_mowing : float
            Soil moisture, % dry basis.
        is_mowing_day : bool
            True on the day the crop is cut.

        Returns
        -------
        float
            Drying-rate constant DR, 1/h (see `FieldCuring.dry_bulb_drying_rate`).

        """
        solar_insolation_w_m2 = weather.incoming_light * fcc.MJ_PER_M2_DAY_TO_W_PER_M2
        return FieldCuring.dry_bulb_drying_rate(
            solar_insolation_w_m2=solar_insolation_w_m2,
            dry_bulb_temp_c=weather.mean_air_temperature,
            soil_moisture_at_mowing=soil_moisture_at_mowing,
            swath_density=swath_density,
            is_mowing_day=is_mowing_day,
        )

    @staticmethod
    def _day_respiration_loss_fraction(weather: CurrentDayConditions, avg_moisture_wet_basis_fraction: float) -> float:
        """
        Sums the day-period and night-period respiration loss fractions for one day.

        Parameters
        ----------
        weather : CurrentDayConditions
            That day's weather (uses ``max_air_temperature``,
            ``min_air_temperature`` as day/night period stand-ins -- see the
            module docstring for the resulting approximation bias).
        avg_moisture_wet_basis_fraction : float
            Wet-basis moisture fraction (0-1) for the day (AMC).

        Returns
        -------
        float
            Combined day-period + night-period fractional respiration DM loss.

        """
        day_temp_f = FieldCuring.celsius_to_fahrenheit(weather.max_air_temperature)
        night_temp_f = FieldCuring.celsius_to_fahrenheit(weather.min_air_temperature)
        return FieldCuring.respiration_dm_loss_fraction(
            avg_moisture_wet_basis_fraction, day_temp_f
        ) + FieldCuring.respiration_dm_loss_fraction(avg_moisture_wet_basis_fraction, night_temp_f)

    @staticmethod
    def _day_rain_losses(
        weather: CurrentDayConditions, ndf_pct: float, cumulative_rain_leaf_loss_fraction: float
    ) -> tuple[float, float]:
        """
        Computes one day's rain-leaf-loss and rain-leaching-loss fractions.

        Parameters
        ----------
        weather : CurrentDayConditions
            That day's weather (uses ``rainfall``, mm).
        ndf_pct : float
            Neutral detergent fibre, percent (0-100), for this day.
        cumulative_rain_leaf_loss_fraction : float
            Rain-leaf-loss fraction already accumulated over the wilt window so
            far, before this day.

        Returns
        -------
        tuple[float, float]
            ``(capped_rain_leaf_loss, leaching_loss)`` for this day. Both are
            ``(0.0, 0.0)`` on a dry day. ``capped_rain_leaf_loss`` is capped so
            that ``cumulative_rain_leaf_loss_fraction + capped_rain_leaf_loss``
            never exceeds ``FIELD_CURING_RAIN_LEAF_LOSS_CAP_FRACTION`` -- the
            caller is responsible for accumulating the returned value across
            the whole wilt window (see `FieldCuring.simulate_field_curing`'s
            cap-scope note).

        """
        if weather.rainfall <= 0.0:
            return 0.0, 0.0
        rainfall_in = FieldCuring.mm_to_inches(weather.rainfall)
        remaining_cap = max(0.0, fcc.FIELD_CURING_RAIN_LEAF_LOSS_CAP_FRACTION - cumulative_rain_leaf_loss_fraction)
        capped_rain_leaf_loss = min(FieldCuring.rain_leaf_loss_fraction(rainfall_in), remaining_cap)
        leaching_loss = FieldCuring.rain_leaching_loss_fraction(rainfall_in, ndf_pct)
        return capped_rain_leaf_loss, leaching_loss

    @staticmethod
    def simulate_field_curing(
        initial_dry_matter_mass_kg: float,
        initial_dry_matter_percentage: float,
        crude_protein_percent: float,
        ndf: float,
        daily_weather: list[CurrentDayConditions],
        swath_density: float,
        soil_moisture_at_mowing: float,
    ) -> FieldCuringResult:
        """
        Simulates field curing (cutting -> storage) day by day.

        Parameters
        ----------
        initial_dry_matter_mass_kg : float
            DM mass at cutting (kg).
        initial_dry_matter_percentage : float
            DM percentage at cutting (0-100).
        crude_protein_percent : float
            CP percentage at cutting (0-100).
        ndf : float
            NDF percentage at cutting (0-100).
        daily_weather : list[CurrentDayConditions]
            One entry per day of the wilt window, in order. The first entry is
            treated as the mowing day (``is_mowing_day=True`` for Eq.5's DAY
            term); all subsequent entries are not. An empty list is a no-op
            (returns the inputs unchanged, matching a 0-day wilt window).
        swath_density : float
            Swath density, g/m2 (held constant across the whole window).
        soil_moisture_at_mowing : float
            Soil moisture at mowing, % dry basis (held constant across the
            whole window).

        Returns
        -------
        FieldCuringResult
            DM mass/percentage, CP, NDF, and total fractional DM loss after the
            whole wilt window.

        Notes
        -----
        Iterates [SC.CRP.79]-[SC.CRP.84] once per day. Each day: compute that
        day's drying-rate DR from that day's weather;
        compute respiration ([SC.CRP.81], day-period + night-period) and rain
        losses ([SC.CRP.82]/[SC.CRP.83]) using the moisture at the START of the
        day (before that day's drying is applied): the moisture going into a
        period, not the moisture resulting from it. Using end-of-day moisture
        instead would zero out an entire day's respiration the instant the
        swath crosses the 0.27 threshold mid-day, even though it was wet for
        most of it. Moisture is then advanced to the end of the day (for use as
        the next day's starting point).

        **Loss compounding**: each day's fractional losses (respiration
        day-period + night-period + rain-leaf + rain-leaching) are summed into
        one daily fraction, then applied multiplicatively against that day's
        *starting* DM mass (``mass -= mass * daily_loss_fraction``) rather than
        summed against the original day-0 mass -- the standard convention for a
        compounding daily loss rate. This matches RuFaS's own Feed-out-phase
        daily-loss formula (``silage.py``'s ``_apply_feed_out_loss``:
        ``dry_matter_loss_kg = crop.dry_matter_mass * loss_fraction``, i.e.
        against the crop's *current* mass) -- verified directly 2026-09-16, but
        only on ``feature/silage-feedout-phase``, a sibling branch not yet
        merged into ``dev-msf`` (the base this branch was cut from); that
        function does not exist on this branch's tree. The design choice stands
        on its own regardless of merge status; this note records where the
        precedent lives once that branch lands. CP/NDF percentages are
        recomputed via Eq.11 (CP) and Eq.12 (NDF) against the new mass each
        day, not deferred to the end.

        **Rain-leaf cap scope**: DAFOSYM's Eq.9 states its 15% cap as "max 15%
        of total plant DM" -- a single ceiling on the whole exposure, not a
        per-day reset. This orchestrator tracks a cumulative rain-leaf-loss
        fraction across the entire wilt window and caps that running total,
        not each day's increment independently -- otherwise 2+ rainy days in
        one window could exceed 15% of the original DM in aggregate,
        contradicting Eq.9's own stated bound.

        References
        ----------
        [SC.CRP.85] Rotz & Chen (1985), Trans. ASAE 28(5):1686-1691 (drying
        curve); Rotz, Black, Mertens & Buckmaster (1989), "DAFOSYM" (DM-loss
        terms).

        """
        if not daily_weather:
            return FieldCuringResult(
                dry_matter_mass_kg=initial_dry_matter_mass_kg,
                dry_matter_percentage=initial_dry_matter_percentage,
                crude_protein_percent=crude_protein_percent,
                ndf=ndf,
                total_loss_fraction=0.0,
            )

        current_mass = initial_dry_matter_mass_kg
        current_moisture = 1.0 - initial_dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        current_cp = crude_protein_percent
        current_ndf = ndf
        cumulative_rain_leaf_loss_fraction = 0.0

        for day_index, weather in enumerate(daily_weather):
            is_mowing_day = day_index == 0

            respiration_loss = FieldCuring._day_respiration_loss_fraction(weather, current_moisture)
            rain_leaf_loss, leaching_loss = FieldCuring._day_rain_losses(
                weather, current_ndf, cumulative_rain_leaf_loss_fraction
            )
            cumulative_rain_leaf_loss_fraction += rain_leaf_loss

            daily_loss_fraction = respiration_loss + rain_leaf_loss + leaching_loss
            current_mass -= current_mass * daily_loss_fraction

            if weather.rainfall > 0.0:
                current_cp, current_ndf = FieldCuring.apply_leaching_quality_shift(
                    current_cp, current_ndf, leaching_loss
                )

            drying_rate = FieldCuring._day_drying_rate(weather, swath_density, soil_moisture_at_mowing, is_mowing_day)
            current_moisture = FieldCuring.swath_moisture_content(
                current_moisture, drying_rate, float(GeneralConstants.HOURS_PER_DAY)
            )

        total_loss_fraction = (
            (initial_dry_matter_mass_kg - current_mass) / initial_dry_matter_mass_kg
            if initial_dry_matter_mass_kg > 0.0
            else 0.0
        )
        final_dry_matter_percentage = (1.0 - current_moisture) * GeneralConstants.FRACTION_TO_PERCENTAGE

        return FieldCuringResult(
            dry_matter_mass_kg=current_mass,
            dry_matter_percentage=final_dry_matter_percentage,
            crude_protein_percent=current_cp,
            ndf=current_ndf,
            total_loss_fraction=total_loss_fraction,
        )
