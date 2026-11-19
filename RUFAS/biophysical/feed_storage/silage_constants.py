"""
Domain constants and equation coefficients for the Silage Preseal phase (Silostg.for's ``PRESEAL``
subroutine, lines 634-714) and Feed-out phase (Silostg.for's ``FEEDOUT`` subroutine, lines 1029-1104),
kept out of ``silage.py`` per ``RUFAS/biophysical/CLAUDE.md``'s "Constants must live in dedicated
*_constants.py modules per domain; do not inline magic numbers" rule.

"""

import math

PRESEAL_K = 9.0
PRESEAL_KM = 0.055
PRESEAL_FC = 0.756
PRESEAL_ATMOSPHERIC_OXYGEN_FRACTION = 0.21
"""
Shared respiration-model constants for the Preseal phase (Silostg.for:643, PRESEAL subroutine).
K and KM are Michaelis-Menten-derived diffusion constants; FC is the CO2-dependent respiration
correction factor; PSIA is atmospheric oxygen concentration (fraction). All four are fixed across
crop types in the source.

"""

PRESEAL_INITIAL_PH = 5.8
"""Fixed initial silage pH under IFSM's no-acid-treatment default (Silostg.for:269-271, FACID=0)."""

PRESEAL_EXPOSURE_CAP_DAYS = 3.0
"""Preseal exposure time is capped at 3 days (Silostg.for:267) and floored at 0 (Silostg.for:268)."""

PRESEAL_FALLBACK_EXPOSURE_DAYS = 0.125
"""Fallback exposure time (3 hours) for the newest plot in a silo with no successor yet (Silostg.for:261)."""

PRESEAL_WATER_RETENTION_FRACTION = 1.0 - 72.0 / 180.0
"""
Fraction of respired dry matter retained as water rather than lost as gas, per Silostg.for:697,708
(spec §5.1's own citation for this fact). Silostg.for:707-708's PLOT(NPL,11)/PLOT(NPL,3) update uses
a 72/180 gas-loss ratio; solving for the resulting fresh-mass change shows only that 72/180 leaves the
crop, while the complementary 108/180 stays as retained moisture. This constant is that retained
(1 - 72/180) fraction — see the `moisture_loss_kg` sign in `Silage._finalize_preseal_loss`: only the
gas-lost fraction of dry matter leaves the crop as fresh mass, while the water-retained fraction
stays behind.
"""

PRESEAL_ALFALFA_MAX_RESPIRATION_RATE = 4.8
PRESEAL_NON_ALFALFA_MAX_RESPIRATION_RATE = 2.9
"""
Maximum daily respiration rate coefficients (``MUMAX``, per unit dry-matter fraction), by crop type
(Silostg.for:649-655): haylage/alfalfa uses the higher rate, corn silage the lower one.

"""

PRESEAL_MIN_THICKNESS_CM = 100.0
"""Minimum silage thickness (cm) used in the diffusion-path calculation (``THICK``, Silostg.for:659)."""

PRESEAL_DEPTH_M_TO_CM = 100.0
"""Depth-to-thickness unit conversion, meters to centimeters, in the same ``THICK`` term (Silostg.for:659)."""

PRESEAL_DIFFUSION_COEFFICIENT_FACTOR = 0.0086
PRESEAL_DIFFUSION_TEMPERATURE_OFFSET_C = 273.0
"""
Diffusion coefficient's temperature-scaling factor and Celsius offset (``D``, Silostg.for:660):
``D = factor * (offset_c + temperature_c)**2``. The offset is the source's own literal ``273.``, not
the full 273.15 Celsius-to-Kelvin conversion (`GeneralConstants.CELSIUS_TO_KELVIN`) — kept distinct so
this translation matches the source bit-for-bit rather than silently changing its numeric output.

"""

PRESEAL_TORTUOSITY = 2.0 / 3.0
"""Effective diffusion-path tortuosity through packed silage, fixed in the source (``TAU``, Silostg.for:661)."""

PRESEAL_MAX_RELATIVE_DENSITY_NUMERATOR = 3.0
"""
Numerator of the maximum-relative-density relationship (``RHOMAX = numerator / (numerator -
dry_matter_fraction)``, Silostg.for:662). Also reused by Feed-out's `calculate_feed_out_loss` (Task 3)
— `Silostg.for:1045`'s own `RHOMAX = 1./(1.-DM+DM/1.5)` is algebraically identical (``1 - DM/3 =
(3-DM)/3``, so ``1/(1-DM/3) = 3/(3-DM)``), not a coincidental reuse of the same numeric constant.

"""

PRESEAL_RELATIVE_DENSITY_CAP_FRACTION = 0.99
"""Fractional ceiling applied to relative density before it reaches the theoretical maximum (Silostg.for:663)."""

PRESEAL_DENSITY_KG_PER_M3_TO_G_PER_CM3 = 0.001
"""Bulk-density unit conversion (kg DM/m3 to g DM/cm3) used in the relative-density calculation (Silostg.for:663)."""

PRESEAL_HIGH_DRY_MATTER_THRESHOLD = 0.693
"""
Dry-matter-fraction threshold above which the respiration factor (``FD``) is fixed at its saturated
minimum (Silostg.for:665-666).
"""

PRESEAL_HIGH_DRY_MATTER_RESPIRATION_FACTOR = 0.0384
"""Saturated respiration factor used above `PRESEAL_HIGH_DRY_MATTER_THRESHOLD` (Silostg.for:666)."""

PRESEAL_LOW_DRY_MATTER_THRESHOLD = 0.20
"""Dry-matter-fraction threshold below which the respiration factor is fixed at 1.0 (Silostg.for:667,670)."""

PRESEAL_RESPIRATION_FACTOR_INTERCEPT = 1.93
PRESEAL_RESPIRATION_FACTOR_LINEAR_COEFFICIENT = 5.46
PRESEAL_RESPIRATION_FACTOR_QUADRATIC_COEFFICIENT = 3.94
"""
Quadratic respiration-factor coefficients (``FD``, Silostg.for:668), fit between
`PRESEAL_LOW_DRY_MATTER_THRESHOLD` and `PRESEAL_HIGH_DRY_MATTER_THRESHOLD`:
``intercept - linear_coefficient * dm_fraction + quadratic_coefficient * dm_fraction**2``.

"""

PRESEAL_TEMPERATURE_FACTOR_SATURATION_C = 25.0
"""
Temperature (degrees C) above which the Preseal temperature factor (``FT``) saturates at 1.0
(Silostg.for:674-675).
"""

PRESEAL_TEMPERATURE_FACTOR_COEFFICIENT = 0.178
PRESEAL_TEMPERATURE_FACTOR_RATE = 0.069
"""
Sub-saturation temperature-factor coefficients (``FT``, Silostg.for:677):
``coefficient * exp(rate * temperature_c)``.
"""

PRESEAL_PH_FACTOR_OFFSET = 3.0
PRESEAL_PH_FACTOR_SCALE = 3.5
"""pH-factor normalization constants (``FPH``, Silostg.for:679): ``(ph - offset) / scale``."""

PRESEAL_LOSS_PER_DAY_COEFFICIENT = 0.0299
"""Per-day dry-matter loss coefficient applied to the average respiration rate (``DMLPD``, Silostg.for:685)."""

PRESEAL_TEMPERATURE_RISE_ENERGY_COEFFICIENT = 8436.0
PRESEAL_TEMPERATURE_RISE_HEAT_RETENTION_FRACTION = 0.7
PRESEAL_TEMPERATURE_RISE_DENOMINATOR_COEFFICIENT_A = 2.22
PRESEAL_TEMPERATURE_RISE_DENOMINATOR_COEFFICIENT_B = 1.22
"""
Self-heating temperature-rise coefficients (``DELT``, Silostg.for:697, "TEMPERATURE RISE ASSUMING 70%
RETENTION OF HEAT GENERATED"): converts a day's DM-loss (kg) into a temperature rise (degrees C), via
``energy_coefficient * loss_today_kg * heat_retention_fraction / (denominator_a / dm_fraction -
denominator_b)``.

"""

FEEDOUT_KM = 0.00145
FEEDOUT_FC = 1.0
"""
Feed-out's own diffusion constants (``Silostg.for:1038``, ``FEEDOUT`` subroutine) — structurally the
same ``GAMMA``/``C``/``MUBAR`` diffusion-front shape as Preseal (``PRESEAL_K``/``PRESEAL_TORTUOSITY``
are reused directly below, verified algebraically identical), but with genuinely different ``KM``/
``FC`` values. Not assumed reusable without this separate citation (design spec Section 5.3.1).

"""

FEEDOUT_THICK_CM = 300.0
"""Fixed diffusion-path thickness for Feed-out (``THICK``, ``Silostg.for:1038``) — unlike Preseal's
dynamic, mass/area-derived ``thickness_cm``, Feed-out's is a fixed constant in the source."""

FEEDOUT_PSIA = 0.21
"""
Feed-out's diffusion-shape constant (``PSIA``, ``Silostg.for:1072-1076``). The source branches on
``SILTYP.EQ.2`` (bottom-unloaded tower) for ``0.105``; every other type (including Bunker and, per
the Reference Manual's "bags use tower relationships" rule, Bag) uses ``0.21``. RuFaS's `StorageType`
has no bottom-unloaded-tower analogue, so this is a flat constant here, not a per-type branch (design
spec Section 5.3.4's corrected reading — supersedes an earlier, incorrect "Bag gets 0.105" claim).

"""

FEEDOUT_MIN_DIFFUSION_C = 0.01
"""Floor on the ``C`` diffusion-front parameter (``Silostg.for:1078``, ``AMAX1(0.01,SQRT(K*GAMMA))``)."""

FEEDOUT_MIN_PHI = 0.01
"""
Below this porosity (``PHI``), Feed-out's face-diffusion loss (``DML4A``) is zeroed — the silage is
packed at maximum density and no further infiltration can occur (``Silostg.for:1081-1083``). The
feed-bunk loss (``DML4B``) is *not* gated by this — it is computed unconditionally in the source.

**This branch is mathematically unreachable given `FEEDOUT_PHI_LOADER_COEFFICIENT` (0.95, itself
fixed by `LOADER=0`)**: the minimum possible porosity is `FEEDOUT_PHI_SCALE * (1 -
FEEDOUT_PHI_LOADER_COEFFICIENT) = 0.7*(1-0.95) = 0.035`, always above this 0.01 threshold — the
source's own guard is equally unreachable there, for the identical `LOADER=0` reason
(`/challenge-plan` round 1 finding #4). Kept for literal 1:1 parity with `Silostg.for`, as free
insurance if `LOADER` is ever made configurable — not exercised by any test that claims correctness
of the branch itself (only that the function still behaves sanely near the ceiling).

"""

FEEDOUT_PHI_SCALE = 0.7
FEEDOUT_PHI_LOADER_COEFFICIENT = 0.95
"""
Feed-out's porosity formula (``PHI``, ``Silostg.for:1047``): ``PHI = scale * (1 - (loader_coefficient
+ 0.05*LOADER) * relative_density / max_relative_density)``. With ``LOADER`` fixed at 0
(``Silostg.for:1039``), the ``0.05*LOADER`` term vanishes, leaving ``loader_coefficient`` (``0.95``)
as a flat multiplier — distinct from both Preseal's and Infiltration's own porosity formulas.

"""

FEEDOUT_MUMAX_COEFFICIENT = 0.88
"""Feed-out's own maximum-respiration-rate coefficient (``MUMAX = 0.88*DM``, ``Silostg.for:1050``) —
unlike Preseal, not split by crop type at this stage (the crop-type split happens at the
``FEEDOUT_LOADER_ALFALFA_COEFFICIENT``/``FEEDOUT_LOADER_NON_ALFALFA_COEFFICIENT`` branch instead)."""

FEEDOUT_WATER_ACTIVITY_COEFFICIENT = 0.03
"""Water-activity formula coefficient (``AW = 1 - 0.03*DM/(1-DM)``, ``Silostg.for:1051``)."""

FEEDOUT_WATER_ACTIVITY_LOW_THRESHOLD = 0.9233
FEEDOUT_WATER_ACTIVITY_HIGH_THRESHOLD = 0.9931
FEEDOUT_WATER_ACTIVITY_HIGH_INTERCEPT = 13.733
FEEDOUT_WATER_ACTIVITY_HIGH_SLOPE = 12.821
FEEDOUT_WATER_ACTIVITY_MID_SLOPE = 14.306
FEEDOUT_WATER_ACTIVITY_MID_INTERCEPT = 13.208
"""
Piecewise water-activity respiration factor (``FD``, ``Silostg.for:1052-1058``): ``0.0`` below
`FEEDOUT_WATER_ACTIVITY_LOW_THRESHOLD`; ``HIGH_INTERCEPT - HIGH_SLOPE*AW`` above
`FEEDOUT_WATER_ACTIVITY_HIGH_THRESHOLD`; ``MID_SLOPE*AW - MID_INTERCEPT`` in between.

"""

FEEDOUT_TEMPERATURE_C = 18.0
"""
Fixed "temperature at feeding time" (``FDTMP``, ``Silostg.for:295``) — a silo-level constant set
once, unconditionally, before any crop-type or storage-type dispatch, not derived from
``crop.temperature`` (which Preseal tracks and updates via self-heating; Feed-out does not read it).

"""

FEEDOUT_TEMPERATURE_FACTOR_LOW_TEMP_COEFFICIENT_A = 36.1
FEEDOUT_TEMPERATURE_FACTOR_LOW_TEMP_COEFFICIENT_B = 10830.0
FEEDOUT_TEMPERATURE_FACTOR = math.exp(
    FEEDOUT_TEMPERATURE_FACTOR_LOW_TEMP_COEFFICIENT_A
    - FEEDOUT_TEMPERATURE_FACTOR_LOW_TEMP_COEFFICIENT_B
    / (FEEDOUT_TEMPERATURE_C + PRESEAL_DIFFUSION_TEMPERATURE_OFFSET_C)
)
"""
Feed-out's temperature factor (``FT``, ``Silostg.for:1059-1069``) is piecewise on ``FDTMP``, but
`FEEDOUT_TEMPERATURE_C` (18.0) always satisfies the source's own ``FDTMP.LT.20.0`` branch — the other
three branches are unreachable given the fixed temperature, so (per the same pre-resolution pattern as
`PRESEAL_INITIAL_PH`) this is the branch's value precomputed once at import time, not a live formula
with dead branches kept around.

"""

FEEDOUT_LOADER_ALFALFA_COEFFICIENT = 1.37
FEEDOUT_LOADER_NON_ALFALFA_COEFFICIENT = 1.18
"""
Crop-type-dependent ``DML4A`` coefficients (``Silostg.for:1085,1087``): ``(1.37 - 0.29*LOADER)`` for
alfalfa/grass (``PLOT(NN,1).GE.4``), ``(1.18 - 0.10*LOADER)`` otherwise. With `LOADER` fixed at 0
(``Silostg.for:1039``), the ``LOADER``-dependent terms vanish, leaving these two flat coefficients.
Crop type uses `HarvestedCrop.is_alfalfa` (alfalfa vs. non-alfalfa only) — the source's actual
"alfalfa or grass" condition is not distinguishable in RuFaS, the same simplification Preseal already
made for its own crop-type-dependent `PRESEAL_ALFALFA_MAX_RESPIRATION_RATE` split.

"""

FEEDOUT_RATE_DENOMINATOR_DAYS = 365.0
"""Feed-out rate is total stored dry matter divided by this many days (``FDRTE``, ``Silostg.for:233,242``
— design spec Section 5.3.3, a static per-storage average, not a `FeedManager`-derived daily amount)."""

FEEDOUT_BUNK_TIME_DAYS = 0.125
"""
Fixed feed-bunk exposure time for the ``DML4B`` term (``Silostg.for:1092``, "0.125 DAYS BUNK TIME
ASSUMED"). **Not** the same constant as `PRESEAL_FALLBACK_EXPOSURE_DAYS` despite the equal numeric
value (3 hours) — that constant is `PLOT(NPL,9)`'s Preseal-specific fallback (``Silostg.for:261``),
a different subroutine with no connection to this one; the two Fortran literals coincide by chance,
not by shared derivation (`/challenge-plan` round 1 finding #3).

"""

FEEDOUT_SECTION_WINDOW_DAYS = 10.0
"""Each Bunker/Pile vertical section represents this many days' worth of feed-out at the storage's
current rate (``NVS = floor(total_DM / (10*FDRTE))``, ``Silostg.for:920``)."""
