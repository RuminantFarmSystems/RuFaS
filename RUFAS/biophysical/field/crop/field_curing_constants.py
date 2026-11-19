"""Constants for the opt-in pre-harvest field-curing phase (cutting -> storage).

Two source groups, each cited per-constant below:

- DAFOSYM respiration/rain terms (Eq.7, 9, 10, 11) -- Rotz, C.A., Black, J.R.,
  Mertens, D.R. & Buckmaster, D.R. (1989), "DAFOSYM: A Model of the Dairy
  Forage System," *J. Prod. Agric.* 2(1):83-91.
- Rotz & Chen (1985) drying-rate coefficients (Eq.1/2/5) -- Rotz, C.A. & Chen,
  Y. (1985), "Alfalfa Drying Model for the Field Environment," *Trans. ASAE*
  28(5):1686-1691.

Both are primary sources. Full entries are in
``docs/scientific/resources/crop_and_soil.bib``.
"""

CELSIUS_TO_FAHRENHEIT_SCALE: float = 9.0 / 5.0
"""Multiplicative term of the C-to-F conversion used by DAFOSYM's
Fahrenheit-calibrated respiration equation (Eq.7). Not present anywhere in
`RUFAS/general_constants.py`'s `GeneralConstants` (checked 2026-09-16 --
that class, not `RUFAS/units.py`, is where reusable conversion factors like
`MM_TO_M`/`KCAL_TO_MJ`/`CELSIUS_TO_KELVIN` actually live; `units.py` is only
the `MeasurementUnits` label Enum) -- defined here, scoped to this module's
own DAFOSYM calls only."""

CELSIUS_TO_FAHRENHEIT_OFFSET: float = 32.0
"""Additive term of the C-to-F conversion, paired with
CELSIUS_TO_FAHRENHEIT_SCALE above."""

MM_TO_INCHES_DIVISOR: float = 25.4
"""Unit conversion for DAFOSYM's inches-calibrated rain equations (Eq.9,
10) against RuFaS's mm weather data. Same "not in GeneralConstants, defined
here" reasoning as CELSIUS_TO_FAHRENHEIT_SCALE above."""

FIELD_CURING_RESPIRATION_COEFFICIENT: float = 0.00239
"""Leading coefficient of DAFOSYM's respiration loss,
RL = 0.00239*(AMC-0.27)*exp(0.038*AT_F), fraction DM lost per 12h period.
Rotz, Black, Mertens & Buckmaster (1989), DAFOSYM, Eq.7, p.86."""

FIELD_CURING_RESPIRATION_MOISTURE_THRESHOLD: float = 0.27
"""Wet-basis moisture threshold (AMC) below which DAFOSYM's respiration
loss (Eq.7) is zero. Rotz, Black, Mertens & Buckmaster (1989), DAFOSYM,
Eq.7, p.86."""

FIELD_CURING_RESPIRATION_TEMP_COEFFICIENT_F: float = 0.038
"""Temperature-exponent coefficient of DAFOSYM's respiration loss (Eq.7),
applied to AT_F, avg temp in deg F (convert from RuFaS's Celsius input via
CELSIUS_TO_FAHRENHEIT_SCALE/OFFSET before calling). Rotz, Black, Mertens &
Buckmaster (1989), DAFOSYM, Eq.7, p.86."""

FIELD_CURING_RAIN_LEAF_LOSS_COEFFICIENT: float = 0.094
"""Coefficient of DAFOSYM's rain-induced leaf DM loss,
RNLL = 0.094*RAIN_IN. RAIN_IN = rainfall, inches (convert from RuFaS's mm
input via MM_TO_INCHES_DIVISOR before calling). Rotz, Black, Mertens &
Buckmaster (1989), DAFOSYM, Eq.9, p.86."""

FIELD_CURING_RAIN_LEAF_LOSS_CAP_FRACTION: float = 0.15
"""Ceiling on RNLL (rain-induced leaf DM loss) as a fraction of plant DM.
Rotz, Black, Mertens & Buckmaster (1989), DAFOSYM, Eq.9, p.86."""

FIELD_CURING_LEACHING_RAIN_COEFFICIENT: float = 0.28
"""Rain leaching loss RNL = (1-NDF)*(1-exp(-0.28*RAIN_IN)). RAIN_IN =
rainfall, inches (same conversion as FIELD_CURING_RAIN_LEAF_LOSS_COEFFICIENT
above). Rotz, Black, Mertens & Buckmaster (1989), DAFOSYM, Eq.10, p.86."""

FIELD_CURING_LEACHING_CP_MULTIPLIER: float = 1.2
"""CP change under leaching: CPf = CPi*(1-1.2*RNL)/(1-RNL). Rotz, Black,
Mertens & Buckmaster (1989), DAFOSYM, Eq.11, p.86."""

FIELD_CURING_RNL_MAX: float = 0.99
"""Numerical guard, not a DAFOSYM threshold: CPf = CPi*(1-1.2*RNL)/(1-RNL)
(Eq.11) has a division singularity as RNL -> 1 (possible for a low-NDF crop
under heavy accumulated rain). RNL is clamped to this value before use in
Eq.11/Eq.12, the same "numerical guard, not a scientific threshold" pattern
as `BEEF_DMI_MIN_NE_CONCENTRATION` (RUFAS/biophysical/CLAUDE.md's own cited
example)."""

DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT: float = 9.30
"""Chemical-conditioning multiplier on the solar-insolation term of Rotz &
Chen (1985)'s drying-rate constant DR (dry-bulb-temperature form, Eq.5):
DR = [SI*(1+9.30*AR) + 5.42*DB] /
     [66.4*SM + SD*(2.06-0.97*DAY)*(1.55+21.9*AR) + 3037]
"Alfalfa Drying Model for the Field Environment," Trans. ASAE 28(5):
1686-1691, Eq.5, R2=0.75 (model development). Chosen over the paper's Eq.4
(VPD form) because RuFaS tracks no humidity/VPD anywhere (CurrentDayConditions
has no such field) -- SI/DB are directly available (incoming_light,
mean_air_temperature); AR (chemical conditioning) is fixed at 0.0 pending
any chemical-conditioning input, matching RuFaS's current absence of that
concept."""

DRYING_RATE_DRY_BULB_COEFFICIENT: float = 5.42
"""Dry-bulb-temperature (DB) coefficient of Eq.5's numerator -- see
DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation and
citation.

DB is dry-bulb air temperature in deg C. Rotz & Chen (1985), Trans. ASAE
28(5):1686-1691, Table 2 (p.1690) lists "Dry bulb temperature" in deg C (10 to
40, typical 30) for the Eq.5 sensitivity analysis, and the table's own values
reproduce under Celsius: with DB = 30, SD = 450 g/m2, SM = 17 %db and DAY = 1,
Eq.5 gives DR = 0.033/h at SI = 0 and 0.226/h at SI = 950 W/m2, the table's
minimum and maximum solar-insolation rows. A Fahrenheit reading does not
reproduce them."""

DRYING_RATE_SOIL_MOISTURE_COEFFICIENT: float = 66.4
"""Soil-moisture (SM) coefficient of Eq.5's denominator -- see
DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation and
citation."""

DRYING_RATE_DAY_INTERCEPT: float = 2.06
"""Intercept of the DAY (mowing-day indicator) term in Eq.5's denominator --
see DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation
and citation."""

DRYING_RATE_DAY_SLOPE: float = 0.97
"""Slope of the DAY (mowing-day indicator) term in Eq.5's denominator --
see DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation
and citation."""

DRYING_RATE_APPLICATION_DENOMINATOR_INTERCEPT: float = 1.55
"""Intercept of the chemical-application-rate (AR) term in Eq.5's
denominator -- see DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the
full equation and citation."""

DRYING_RATE_APPLICATION_DENOMINATOR_SLOPE: float = 21.9
"""Slope of the chemical-application-rate (AR) term in Eq.5's denominator --
see DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation
and citation."""

DRYING_RATE_DENOMINATOR_CONSTANT: float = 3037.0
"""Additive constant in Eq.5's denominator -- see
DRYING_RATE_SOLAR_APPLICATION_COEFFICIENT above for the full equation and
citation."""

MJ_PER_M2_DAY_TO_W_PER_M2: float = 1_000_000.0 / 86_400.0
"""Converts RuFaS's `CurrentDayConditions.incoming_light` (MJ/m2 -- the
dataclass's own docstring says only "Incoming light radiation energy
(MJ/m^2)", not explicitly "daily total"; treating it as one is a reasonable
but not literally-confirmed inference from context) into the average W/m2
(instantaneous power flux) that Rotz & Chen (1985) states `SI` is measured in
(Rotz & Chen 1985, Trans. ASAE 28(5):1686-1691, p.1689, parameter list
under Eq.3: 'SI = solar insolation, W/m2'). Standard J/s <-> J/day identity
(1e6 J/MJ / 86400 s/day).

This yields a daily-mean SI, which is consistent with the paper. Solar
insolation was measured hourly (p.1687), and DR is linear in SI (Eq.5), so DR
computed from the daily-mean SI equals the time-averaged DR. The paper states
(p.1688, after Eq.1) that M(t) = M0*exp(-DR*T) predicts the same end-of-day
moisture regardless of how the day is divided into periods, as long as the
average DR over those periods is used. Limitation: the paper excluded
early-morning (before 10:00) and dew-wetted cases (p.1687), so applying a
daily-mean DR over 24 h also credits night-time hours (SI = 0) with the
dry-bulb term's drying, which the paper did not calibrate."""

SWATH_MOISTURE_EQUILIBRIUM_FRACTION: float = 0.0
"""Equilibrium moisture content, dry basis (kg water/kg DM), in Eq.2:
M = M0*exp(-DR*T) reduces to this when Me = 0. Rotz & Chen (1985), Trans.
ASAE 28(5):1686-1691, p.1688: Me = 0 gave the best fit (R2 about 0.6, against
about 0.4 for an equilibrium moisture from Savoie et al. 1982) in the
80-20 % wet-basis range. Me is dry basis like M itself (Eq.1 notation)."""

SWATH_MOISTURE_LOWER_BOUND_WET_BASIS_FRACTION: float = 0.20
"""Wet-basis moisture fraction below which Eq.2 is not applied further: the
swath stops drying at this value. Rotz & Chen (1985), Trans. ASAE
28(5):1686-1691, p.1688: the model gave the best fit "in the range of 80 to
20 % moisture content (wb)", and cases where the samples had dropped below
20 % wb were excluded from model development (pp.1687, 1689), so Eq.2 is not
validated below this value. A crop already drier than this at cutting is left
unchanged."""
