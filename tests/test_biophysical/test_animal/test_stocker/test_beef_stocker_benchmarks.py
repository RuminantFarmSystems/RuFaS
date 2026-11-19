"""NRC 2016 benchmark validation — BeefStockerRequirementsCalculator.

Formal class-based re-validation of the four core NRC 2016 scenarios from Step 3
(SK-MAINT-1, SK-GROW-1, SK-DMI-1, SK-MP-1) plus three additional analytically-derived
scenarios covering cold-stress maintenance, mild-mud maintenance, and a higher ADG.

All expected values are derived analytically from NRC 2016 equations; BeefGEM is
not used as the test oracle (NRC 2000 / monthly timestep mismatch).

Source traceability per scenario is given in each test's docstring.
"""

from __future__ import annotations

import pytest

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.beef_stocker_requirements_calculator import (
    BeefStockerRequirementsCalculator,
    StockerRequirementsInputs,
)

# ---------------------------------------------------------------------------
# Shared scenario parameters
# ---------------------------------------------------------------------------

_BW: float = 280.0  # kg live weight (benchmark steer)
_MBW: float = 520.0  # kg mature body weight
_ADG_BASE: float = 0.80  # kg/d baseline
_ADG_HIGH: float = 1.20  # kg/d higher-ADG scenario
_NE_DIET: float = 1.0  # Mcal/kg DM (pasture forage)
_TEMP_THERMO: float = 20.0  # °C — cold-stress term a2 = 0
_TEMP_COLD: float = 5.0  # °C — cold-stress term a2 > 0


def _make_inputs(**overrides: object) -> StockerRequirementsInputs:
    """
    Build a StockerRequirementsInputs from benchmark defaults with optional overrides.

    Parameters
    ----------
    **overrides : object
        Field values to replace in the default benchmark scenario.

    Returns
    -------
    StockerRequirementsInputs
        Benchmark inputs for 280 kg Angus steer, thermoneutral, no mud, ADG=0.80.

    """
    defaults: dict[str, object] = {
        "animal_type": AnimalType.BEEF_STOCKER_STEER,
        "sex": Sex.STEER,
        "body_weight": _BW,
        "mature_body_weight": _MBW,
        "breed": "Angus",
        "target_adg": _ADG_BASE,
        "temperature_c": _TEMP_THERMO,
        "ne_diet_concentration": _NE_DIET,
        "mud_condition": AnimalModuleConstants.BEEF_MUD_CONDITION_NONE,
    }
    defaults.update(overrides)
    return StockerRequirementsInputs(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Analytically-derived expected values
# ---------------------------------------------------------------------------

# SK-MAINT-1: NEm = SBW^0.75 × 0.077 × BE × SEX  (no cold, no mud)
#   SBW=268.8, SBW^0.75≈66.39, BE=1.00 (Angus), SEX=1.00 (steer), a2=0
#   NEm = 66.39 × 0.077 = 5.112 Mcal/d
#   Source: NRC 2016 Eq.11-1; Sheet 7_Validation_Examples / Ch.11 base maintenance
_SK_MAINT_1_NEM: float = 5.112

# SK-MAINT-2: cold stress at T=5°C adds a2 = 0.0007 × (20 - 5) = 0.0105
#   NEm = 66.39 × (0.077 + 0.0105) = 66.39 × 0.0875 = 5.809 Mcal/d
#   Source: NRC 2016 Eq.11-2 (cold-stress increment); Ch.11 §Cold and Wet
_SK_MAINT_2_NEM: float = 5.809

# SK-MAINT-3: mild mud at thermoneutral; NRC 2016 mud multiplier = 1.08
#   NEm = 5.112 × 1.08 = 5.521 Mcal/d
#   Source: NRC 2016 Ch.11 §Mud table; mild = 8% increase in maintenance
_SK_MAINT_3_NEM: float = 5.521

# SK-GROW-1: NEg via NRC 2016 Eq.12-3, ADG=0.80 kg/d
#   MSBW=499.2, EQSBW=257.39, EQEBW=229.33, EBG=0.7648
#   NEg = 0.0635 × 229.33^0.75 × 0.7648^1.097 ≈ 2.789 Mcal/d
#   Source: NRC 2016 Eq.12-3; Sheet 7_Validation_Examples / Ch.12 NEg
_SK_GROW_1_NEG: float = 2.789

# SK-GROW-2: NEg at ADG=1.20 kg/d (same BW and mature BW as SK-GROW-1)
#   EBG=1.1472, EQEBW unchanged (229.33)
#   NEg = 0.0635 × 229.33^0.75 × 1.1472^1.097 ≈ 4.351 Mcal/d
#   Source: NRC 2016 Eq.12-3; Ch.12 §Varying ADG
_SK_GROW_2_NEG: float = 4.351

# SK-DMI-1: DMI via NRC 2016 Eq.10-5 at forage NE_m=1.0 Mcal/kg DM
#   BW^0.75=68.45, ne_c=1.0
#   ne_m_intake = 68.45 × (0.04997 × 1.0² + 0.04631 × 1.0) = 6.592
#   DMI = 6.592 / 1.0 = 6.592 kg/d
#   Source: NRC 2016 Eq.10-5; Sheet 7_Validation_Examples / Sheet 3 (DMI model)
_SK_DMI_1_DMI: float = 6.592

# SK-MP-1: MP for 280 kg steer at ADG 0.80 kg/d
#   MPm = 3.8 × BW^0.75 = 260.10 g/d
#   NPg = 268.8 × 0.0493 × (0.956 × 0.80)^1.097 × 1.12 ≈ 132.4 g/d
#   eff_g = max(0.492, 0.834 - 0.00114 × 257.39) = 0.540
#   MPg = 132.4 / 0.540 = 245.2 g/d   → MP ≈ 505 g/d
#   Source: NRC 2016 Ch.6 / Box 12-1 (MP for growing cattle)
_SK_MP_1_MP: float = 505.0


# ---------------------------------------------------------------------------
# Benchmark class
# ---------------------------------------------------------------------------


@pytest.mark.nrc2016
class TestStockerNRC2016Benchmarks:
    """Formal NRC 2016 benchmark validation for the beef stocker requirements calculator.

    All scenarios reference a 280 kg Angus BEEF_STOCKER_STEER at ADG 0.80 kg/d unless
    stated otherwise. Expected values are derived analytically from NRC 2016 equations;
    each docstring cites the specific equation/chapter used.

    Energy tolerances: ±3% (NRC 2016 Table/Eq precision).
    Protein tolerance: ±5% (additional intermediate rounding in MP chain).
    """

    def test_sk_maint_1_thermoneutral_no_mud(self) -> None:
        """SK-MAINT-1: NEm for 280 kg Angus steer, thermoneutral (T=20°C), no mud.

        Source: NRC 2016 Eq.11-1 and Sheet 7_Validation_Examples (Ch.11 base
        maintenance).  NEm = SBW^0.75 × 0.077 × BE × SEX.  SBW=268.8 kg,
        SBW^0.75≈66.39, BE=1.00 (Angus), SEX=1.00 (steer), a2=0 (thermoneutral).
        Expected ≈ 5.112 Mcal/d, tolerance ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs())
        assert result.maintenance_energy == pytest.approx(_SK_MAINT_1_NEM, rel=0.03)

    def test_sk_maint_2_cold_stress_5c(self) -> None:
        """SK-MAINT-2: NEm at cold temperature (T=5°C) — cold-stress increment active.

        Source: NRC 2016 Eq.11-2 (cold-stress addition); Ch.11 §Cold and Wet.
        Cold-stress term: a2 = max(0, 0.0007 × (20 − T_c)) = 0.0007 × 15 = 0.0105.
        NEm = 66.39 × (0.077 + 0.0105) = 66.39 × 0.0875 ≈ 5.809 Mcal/d, ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs(temperature_c=_TEMP_COLD))
        assert result.maintenance_energy == pytest.approx(_SK_MAINT_2_NEM, rel=0.03)

    def test_sk_maint_3_mild_mud_thermoneutral(self) -> None:
        """SK-MAINT-3: NEm with mild mud at thermoneutral — mud multiplier 1.08.

        Source: NRC 2016 Ch.11 §Mud table; mild mud increases maintenance energy
        by 8%.  NEm = SK-MAINT-1 × 1.08 = 5.112 × 1.08 ≈ 5.521 Mcal/d, ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs(mud_condition="mild"))
        assert result.maintenance_energy == pytest.approx(_SK_MAINT_3_NEM, rel=0.03)

    def test_sk_grow_1_adg_0_80(self) -> None:
        """SK-GROW-1: NEg for 280 kg steer at ADG 0.80 kg/d.

        Source: NRC 2016 Eq.12-3 and Sheet 7_Validation_Examples (Ch.12 NEg).
        NEg = 0.0635 × EQEBW^0.75 × EBG^1.097.
        MSBW=499.2, EQSBW=257.39, EQEBW=229.33, EBG=0.7648.
        Expected ≈ 2.789 Mcal/d, tolerance ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs())
        assert result.growth_energy == pytest.approx(_SK_GROW_1_NEG, rel=0.03)

    def test_sk_grow_2_adg_1_20(self) -> None:
        """SK-GROW-2: NEg for 280 kg steer at ADG 1.20 kg/d (higher intake scenario).

        Source: NRC 2016 Eq.12-3; Ch.12 §Varying ADG.
        Same BW/mature BW as SK-GROW-1; only EBG changes to 1.1472.
        NEg = 0.0635 × 229.33^0.75 × 1.1472^1.097 ≈ 4.351 Mcal/d, ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs(target_adg=_ADG_HIGH))
        assert result.growth_energy == pytest.approx(_SK_GROW_2_NEG, rel=0.03)

    def test_sk_dmi_1_ne_1_0(self) -> None:
        """SK-DMI-1: DMI for 280 kg steer at forage NE_m = 1.0 Mcal/kg DM.

        Source: NRC 2016 Eq.10-5 (forage-based growing cattle); Sheet 7_Validation_Examples /
        Sheet 3 (DMI model).  No pregnancy intercept, no lactation term.
        BW^0.75=68.45, ne_c=1.0, DMI ≈ 6.592 kg/d, tolerance ±3%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs())
        assert result.dry_matter == pytest.approx(_SK_DMI_1_DMI, rel=0.03)

    def test_sk_mp_1_adg_0_80(self) -> None:
        """SK-MP-1: metabolizable protein for 280 kg steer at ADG 0.80 kg/d.

        Source: NRC 2016 Ch.6 / Box 12-1 (MP for growing cattle).
        MPm = 3.8 × BW^0.75 = 260.10 g/d.
        NPg ≈ 132.4 g/d; eff_g = max(0.492, 0.834 − 0.00114 × EQSBW) ≈ 0.540.
        MPg ≈ 245.2 g/d; MP = MPm + MPg ≈ 505 g/d, tolerance ±5%.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        result = BeefStockerRequirementsCalculator.calculate_requirements(_make_inputs())
        assert result.metabolizable_protein == pytest.approx(_SK_MP_1_MP, rel=0.05)
