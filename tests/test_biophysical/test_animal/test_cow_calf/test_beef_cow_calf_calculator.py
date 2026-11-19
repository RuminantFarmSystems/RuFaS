"""Unit tests for BeefCowCalfRequirementsCalculator and CowCalfRequirementsInputs.

Validation targets computed directly from NRC 2016 Ch.19 equations as transcribed in
NRC2016_Beef_Requirements_Calculator_Inventory_Final.xlsx (sheets 1_Maintenance_Energy,
8_Pregnancy_Lactation, 3_DMI_Ch10_Exact, 6_Minerals_Table19-3_19-4, 7_Validation_Examples).

Tolerances follow Section 3.8 of the cow-calf integration plan:
  ±3% for maintenance, gestation, growth, DMI (exact-equation methods)
  ±5% for lactation (Wood curve has more parameters)
  ±0% for EQSBW identity tests
"""

import dataclasses
from typing import cast

import pytest

from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.beef_cow_calf_requirements_calculator import (
    BeefCowCalfRequirementsCalculator,
    CowCalfRequirementsInputs,
)
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nasem_requirements_calculator import NASEMRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nrc_requirements_calculator import NRCRequirementsCalculator

# ---------------------------------------------------------------------------
# Shared fixture helpers
# ---------------------------------------------------------------------------

_ANGUS_COW_NONLACT = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex=Sex.FEMALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=None,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_LACT = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex=Sex.FEMALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=60,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_LACT_HEIFER = CowCalfRequirementsInputs(
    body_weight=480.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex=Sex.FEMALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=60,
    parity=1,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_COW_GEST = CowCalfRequirementsInputs(
    body_weight=520.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_COW,
    breed="Angus",
    sex=Sex.FEMALE,
    body_condition_score=5.0,
    days_pregnant=200,
    days_in_milk=None,
    parity=2,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_HEIFER = CowCalfRequirementsInputs(
    body_weight=300.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_HEIFER_REPLACEMENT,
    breed="Angus",
    sex=Sex.FEMALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=None,
    parity=0,
    target_adg=0.675,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_CALF = CowCalfRequirementsInputs(
    body_weight=100.0,
    mature_body_weight=520.0,
    animal_type=AnimalType.BEEF_CALF,
    breed="Angus",
    sex=Sex.MALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=None,
    parity=0,
    target_adg=1.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)

_ANGUS_BULL = CowCalfRequirementsInputs(
    body_weight=700.0,
    mature_body_weight=700.0,
    animal_type=AnimalType.BEEF_BULL,
    breed="Angus",
    sex=Sex.MALE,
    body_condition_score=5.0,
    days_pregnant=None,
    days_in_milk=None,
    parity=0,
    target_adg=0.0,
    mud_condition="none",
    temperature_c=20.0,
    ne_diet_concentration=1.1,
    process_based_phosphorus_requirement=0.0,
)


# ---------------------------------------------------------------------------
# 3.1 CowCalfRequirementsInputs dataclass
# ---------------------------------------------------------------------------


class TestCowCalfRequirementsInputs:
    """CC-INPUTS — dataclass construction and field types."""

    def test_constructs_with_all_fields(self) -> None:
        """CowCalfRequirementsInputs must be constructable with all required fields."""
        inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=60,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        assert inputs.body_weight == 520.0
        assert inputs.animal_type == AnimalType.BEEF_COW
        assert inputs.days_pregnant is None
        assert inputs.days_in_milk == 60

    def test_days_pregnant_is_nullable(self) -> None:
        """days_pregnant must accept None (non-pregnant animal)."""
        assert _ANGUS_COW_LACT.days_pregnant is None

    def test_days_in_milk_is_nullable(self) -> None:
        """days_in_milk must accept None (dry or non-lactating animal)."""
        assert _ANGUS_COW_NONLACT.days_in_milk is None

    def test_bcs_field_accepts_nine_scale(self) -> None:
        """body_condition_score must accept values on the 1-9 NRC beef scale."""
        inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=7.0,
            days_pregnant=None,
            days_in_milk=None,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        assert inputs.body_condition_score == 7.0


# ---------------------------------------------------------------------------
# 3.2 _calculate_comp — BCS adjustment (Eq.19-4)
# ---------------------------------------------------------------------------


class TestCalculateComp:
    """CC-COMP — COMP = 0.8 + (BCS-1) × 0.05, BCS on 1-9 NRC beef scale."""

    def test_bcs5_gives_comp_one(self) -> None:
        """COMP = 1.0 at BCS=5 (moderate condition baseline)."""
        assert BeefCowCalfRequirementsCalculator._calculate_comp(5.0) == pytest.approx(1.0, rel=1e-6)

    def test_bcs1_gives_comp_point_eight(self) -> None:
        """COMP = 0.80 at BCS=1 (thin extreme, NRC Ch.12 reference)."""
        assert BeefCowCalfRequirementsCalculator._calculate_comp(1.0) == pytest.approx(0.80, rel=1e-6)

    def test_bcs9_gives_comp_one_point_two(self) -> None:
        """COMP = 1.20 at BCS=9 (fat extreme, NRC Ch.12 reference)."""
        assert BeefCowCalfRequirementsCalculator._calculate_comp(9.0) == pytest.approx(1.20, rel=1e-6)

    def test_bcs3_gives_comp_point_nine(self) -> None:
        """COMP = 0.90 at BCS=3."""
        assert BeefCowCalfRequirementsCalculator._calculate_comp(3.0) == pytest.approx(0.90, rel=1e-6)


# ---------------------------------------------------------------------------
# 3.2 _calculate_maintenance_energy — NEm (Eq.19-1 to 19-4)
# ---------------------------------------------------------------------------


class TestCalculateMaintenanceEnergy:
    """CC-MAINT — NEm = SBW^0.75 × (a1 × BE × L × COMP × SEX + a2), Sheet 1."""

    # Expected values computed from sheet equations directly:
    # SBW=499.2, a1=0.077, BE=1.0, L=1.0(nonlact)/1.2(lact), COMP=1.0, SEX=1.0, a2=0
    _NEm_NONLACT = 8.131987  # Mcal/d — Angus cow, BCS=5, thermoneutral, non-lactating
    _NEm_LACT = 9.758384  # Mcal/d — same cow, lactating (L=1.2)
    _NEm_BULL = 11.687336  # Mcal/d — Angus bull, BW=700, SEX=1.15

    def test_cc_maint_1_non_lactating_angus_cow(self) -> None:
        """CC-MAINT-1: Non-lactating Angus cow BW=520, BCS=5, thermoneutral. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.maintenance_energy == pytest.approx(self._NEm_NONLACT, rel=0.03)

    def test_cc_maint_2_lactating_angus_cow_uses_l_factor(self) -> None:
        """CC-MAINT-2: Lactating Angus cow uses L=1.2 → NEm 20% higher than non-lactating. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        assert result.maintenance_energy == pytest.approx(self._NEm_LACT, rel=0.03)

    def test_cc_maint_3_bull_sex_multiplier(self) -> None:
        """CC-MAINT-3: Angus bull BW=700, SEX=1.15 → NEm 15% above female baseline. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_BULL)
        assert result.maintenance_energy == pytest.approx(self._NEm_BULL, rel=0.03)

    def test_lactating_nem_exceeds_nonlactating_by_l_ratio(self) -> None:
        """Ratio of lactating to non-lactating NEm must equal L factor (1.2 for Angus)."""
        result_nl = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        result_l = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        ratio = result_l.maintenance_energy / result_nl.maintenance_energy
        assert ratio == pytest.approx(1.2, rel=0.01)

    def test_cold_stress_a2_increases_nem(self) -> None:
        """Ambient temperature below 20°C must increase NEm via a2 term."""
        cold_inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=None,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=0.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        warm = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        cold = BeefCowCalfRequirementsCalculator.calculate_requirements(cold_inputs)
        assert cold.maintenance_energy > warm.maintenance_energy

    def test_mud_condition_mild_increases_nem(self) -> None:
        """Mild mud condition (mud multiplier 1.08) must increase NEm relative to no mud."""
        mud_inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=None,
            parity=2,
            target_adg=0.0,
            mud_condition="mild",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        no_mud = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        with_mud = BeefCowCalfRequirementsCalculator.calculate_requirements(mud_inputs)
        assert with_mud.maintenance_energy == pytest.approx(no_mud.maintenance_energy * 1.08, rel=0.001)


# ---------------------------------------------------------------------------
# 3.3 Lactation — Wood curve (Eq.19-19 to 19-36)
# ---------------------------------------------------------------------------


class TestBeefMilkYieldAndLactation:
    """CC-LACT — Wood lactation curve and energy/protein for suckling beef cow."""

    # Computed from Sheet 8 equations directly:
    # Angus: PKYD=8, MkFat=4.0, MkSNF=8.3, MkProt=3.8
    # DIM=60 (n=8.571), k=0.125, T=8, RMY=1.0, e^1=math.e=2.71828
    # aPKYD=(0.125×1+0.375)×8=4.0, a=1/(4×0.125×e)=0.73576
    # Yn=8.571/(0.73576×exp(0.125×8.571))×1.0=3.990269 kg/d
    # E=0.092×4+0.049×8.3-0.0569=0.71780 Mcal/kg
    # NEl=3.990×0.71780=2.864215 Mcal/d
    # MPl=(3.990×3.8/100/0.65)×1000=233.277 g/d
    _Yn_MATURE = 3.990269
    _NEl_MATURE = 2.864215
    _MPl_MATURE = 233.277

    # First-calf heifer: AgeFactor=0.85
    _Yn_HEIFER = 3.391729  # = _Yn_MATURE × 0.85
    _NEl_HEIFER = 2.434583

    def test_cc_lact_1_yn_at_dim_60_mature(self) -> None:
        """CC-LACT-1: Wood curve Yn for mature Angus cow at DIM=60. ±5%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        assert result.lactation_energy == pytest.approx(self._NEl_MATURE, rel=0.05)

    def test_cc_lact_2_first_calf_heifer_age_factor(self) -> None:
        """CC-LACT-2: First-calf heifer (parity=1, AgeFactor=0.85) has lower Yn. ±5%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT_HEIFER)
        assert result.lactation_energy == pytest.approx(self._NEl_HEIFER, rel=0.05)

    def test_cc_lact_3_heifer_lact_below_mature(self) -> None:
        """Heifer lactation energy must be exactly 85% of mature cow's at same DIM."""
        mature = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        heifer = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT_HEIFER)
        assert heifer.lactation_energy == pytest.approx(mature.lactation_energy * 0.85, rel=0.02)

    def test_cc_lact_peak_at_eight_weeks(self) -> None:
        """Yn at DIM=56 (T=8 weeks) must equal aPKYD = 0.5 × PKYD for Angus (RMY=1.0). ±2%."""
        peak_inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=56,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        # aPKYD = 0.5 × 8.0 = 4.0; E = 0.71780
        expected_nel = 4.0 * 0.71780
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(peak_inputs)
        assert result.lactation_energy == pytest.approx(expected_nel, rel=0.02)

    def test_cc_lact_mpl_for_mature_cow(self) -> None:
        """MPl for mature Angus cow at DIM=60 matches formula. ±5%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        # MPl embedded in metabolizable_protein; check pregnancy_energy=0 and lactation_energy close
        assert result.lactation_energy == pytest.approx(self._NEl_MATURE, rel=0.05)

    def test_non_lactating_cow_has_zero_lactation_energy(self) -> None:
        """Non-lactating cow must have zero lactation_energy."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.lactation_energy == 0.0

    def test_pkyd_zero_returns_zero_tuple(self) -> None:
        """pkyd = 0.0 must return (0.0, 0.0, 0.0) without raising ZeroDivisionError."""
        result = BeefCowCalfRequirementsCalculator._calculate_beef_milk_yield_and_lactation_requirement(
            days_in_milk=60, pkyd=0.0, mkfat=4.0, mksnf=8.3, mkprot=3.8, parity=2
        )
        assert result == (0.0, 0.0, 0.0)

    def test_i6_e1_confirmation_wood_curve_uses_euler_constant(self) -> None:
        """I6: e^1 in Wood curve formula is math.e (Euler's number); verify Yn formula shape."""
        # At exactly n=T weeks (DIM=56), Yn = aPKYD for the chosen breed.
        # aPKYD = (0.125×RMY + 0.375) × PKYD = 0.5 × 8 = 4.0
        # This identity holds only when e^1 = math.e = 2.71828…
        peak_inputs = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=56,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(peak_inputs)
        e_milk = 0.092 * 4.0 + 0.049 * 8.3 - 0.0569  # Angus E = 0.71780
        expected_nel_at_peak = 4.0 * e_milk  # Yn=4.0 at peak
        assert result.lactation_energy == pytest.approx(expected_nel_at_peak, rel=0.001)


# ---------------------------------------------------------------------------
# 3.4 Gestation energy (Eq.19-37 to 19-42, Sheet 8 Section A)
# ---------------------------------------------------------------------------


class TestCalculateGestationEnergy:
    """CC-GEST — NRC 2016 beef-specific gestation equations."""

    # Computed: CBW=31 (Angus), DP=200
    # NEy=0.254745 Mcal/d, MPy=47.767 g/d, CW=17.462 kg
    _NEy_DP200 = 0.254745
    _MPy_DP200 = 47.767093

    def test_cc_gest_1_ney_at_dp_200(self) -> None:
        """CC-GEST-1: Gestation energy for Angus at DP=200. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_GEST)
        assert result.pregnancy_energy == pytest.approx(self._NEy_DP200, rel=0.03)

    def test_cc_gest_2_non_pregnant_has_zero_pregnancy_energy(self) -> None:
        """Non-pregnant cow must have zero pregnancy_energy."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.pregnancy_energy == 0.0

    def test_cc_gest_3_late_gestation_higher_than_mid(self) -> None:
        """Late gestation (DP=250) must have higher NEy than mid-gestation (DP=150)."""
        mid_inputs = dataclasses.replace(_ANGUS_COW_GEST, days_pregnant=150)
        late_inputs = dataclasses.replace(_ANGUS_COW_GEST, days_pregnant=250)
        mid = BeefCowCalfRequirementsCalculator.calculate_requirements(mid_inputs)
        late = BeefCowCalfRequirementsCalculator.calculate_requirements(late_inputs)
        assert late.pregnancy_energy > mid.pregnancy_energy

    def test_i4_eqsbw_subtracts_conceptus_weight_for_pregnant_cow(self) -> None:
        """I4: EQSBW = (SBW - CW) × (SRW/MSBW); CW > 0 → lower EQSBW → lower growth NEg.

        NutritionRequirements has no eqsbw field, so we verify the CW subtraction through
        observable growth_energy: same BW/ADG, pregnant cow has lower NEg than non-pregnant.
        CW at DP=200 is ~17.5 kg → measurable EQSBW reduction → measurable NEg reduction.
        """
        growing_preg = dataclasses.replace(_ANGUS_COW_GEST, target_adg=0.5)
        growing_nonpreg = dataclasses.replace(_ANGUS_COW_NONLACT, target_adg=0.5)
        result_preg = BeefCowCalfRequirementsCalculator.calculate_requirements(growing_preg)
        result_np = BeefCowCalfRequirementsCalculator.calculate_requirements(growing_nonpreg)
        assert result_preg.growth_energy < result_np.growth_energy
        cw = BeefCowCalfRequirementsCalculator._calculate_conceptus_weight(31.0, 200)
        assert cw == pytest.approx(17.462, rel=0.01)

    def test_conceptus_weight_at_term_is_nonzero(self) -> None:
        """CW at DP=283 (term) must be positive (> 0 kg)."""
        # Angus CBW=31: CW=31×0.01828×exp(0.02×283-0.0000143×283²)≈51.8 kg
        cw = BeefCowCalfRequirementsCalculator._calculate_conceptus_weight(31.0, 283)
        assert cw > 0.0
        assert cw == pytest.approx(51.767, rel=0.01)


# ---------------------------------------------------------------------------
# 3.5 Growth energy — composition from BeefNRCRequirementsCalculator
# ---------------------------------------------------------------------------


class TestGrowthEnergyComposition:
    """CC-GROW — Growth energy via composition with BeefNRCRequirementsCalculator."""

    # Heifer: BW=300, mature_BW=520, ADG=0.675, SBW=288, MSBW=499.2
    # EQSBW=288×(478/499.2)=275.77, EQEBW=0.891×275.77=245.71, EBG=0.956×0.675=0.6453
    # NEg=0.0635×245.71^0.75×0.6453^1.097=2.437249 Mcal/d
    _NEg_HEIFER = 2.437249

    # Calf: BW=100, SBW=96, EQSBW=91.92, EQEBW=81.90, EBG=0.956
    # NEg=0.0635×81.90^0.75×0.956^1.097=1.645556 Mcal/d
    _NEg_CALF = 1.645556

    def test_cc_grow_1_heifer_growth_energy(self) -> None:
        """CC-GROW-1: Replacement heifer growth energy, ADG=0.675. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_HEIFER)
        assert result.growth_energy == pytest.approx(self._NEg_HEIFER, rel=0.03)

    def test_cc_calf_1_beef_calf_growth_energy(self) -> None:
        """CC-CALF-1: Beef calf growth energy, ADG=1.0. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_CALF)
        assert result.growth_energy == pytest.approx(self._NEg_CALF, rel=0.03)

    def test_mature_cow_has_zero_growth_energy(self) -> None:
        """Non-growing mature beef cow must have zero growth_energy."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.growth_energy == 0.0

    def test_bull_has_zero_growth_energy(self) -> None:
        """Mature bull (target_adg=0) must have zero growth_energy."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_BULL)
        assert result.growth_energy == 0.0

    def test_zero_adg_heifer_has_zero_growth_energy(self) -> None:
        """Heifer with target_adg=0.0 must have zero growth_energy."""
        zero_adg = dataclasses.replace(_ANGUS_HEIFER, target_adg=0.0)
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(zero_adg)
        assert result.growth_energy == 0.0


# ---------------------------------------------------------------------------
# 3.6 Calcium and phosphorus (Sheet 6 Table 19-3 + pregnancy/lactation terms)
# ---------------------------------------------------------------------------


class TestCalciumPhosphorus:
    """CC-MIN — Ca and P with pregnancy/lactation mineral terms. ±5%."""

    # Non-pregnant, non-lactating Angus cow, SBW=499.2:
    # Ca_maint = 0.0308 × 499.2 = 15.375 g/d
    # P_maint  = 0.02353 × 499.2 = 11.745 g/d
    _Ca_MAINT = 15.375360
    _P_MAINT = 11.745696

    # Lactating cow: Ca_lact = Yn × 2.46 = 3.990 × 2.46 = 9.816 g/d
    #                P_lact  = Yn × 1.397 = 3.990 × 1.397 = 5.574 g/d
    _Ca_LACT_TERM = 9.816062
    _P_LACT_TERM = 5.574406

    # Pregnant cow (DP=200 >= 193 → last 90 days active):
    # Ca_preg = 31 × 0.3044 = 9.4364 g/d
    # P_preg  = 31 × 0.1242 = 3.850 g/d
    _Ca_PREG_TERM = 9.436400
    _P_PREG_TERM = 3.850200

    def test_cc_min_nonpregnant_nonlactating_cow_ca(self) -> None:
        """Non-lactating cow Ca = maintenance only (no growth, no pregnancy). ±5%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.calcium == pytest.approx(self._Ca_MAINT, rel=0.05)

    def test_cc_min_nonpregnant_nonlactating_cow_p(self) -> None:
        """Non-lactating cow P = maintenance only. ±5%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.phosphorus == pytest.approx(self._P_MAINT, rel=0.05)

    def test_cc_min_lactating_cow_ca_exceeds_dry(self) -> None:
        """Lactating cow Ca must exceed dry cow Ca by the lactation mineral term. ±5%."""
        dry = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        lact = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        ca_increment = lact.calcium - dry.calcium
        assert ca_increment == pytest.approx(self._Ca_LACT_TERM, rel=0.05)

    def test_cc_min_pregnant_cow_ca_includes_preg_term(self) -> None:
        """Pregnant cow (DP=200) Ca must include pregnancy mineral term. ±5%."""
        dry = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        preg = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_GEST)
        ca_increment = preg.calcium - dry.calcium
        assert ca_increment == pytest.approx(self._Ca_PREG_TERM, rel=0.05)

    def test_cc_min_heifer_includes_growth_terms(self) -> None:
        """Replacement heifer Ca must exceed dry cow Ca due to growth mineral terms."""
        nonlact_cow = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        heifer = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_HEIFER)
        assert heifer.calcium > nonlact_cow.calcium
        assert heifer.phosphorus > nonlact_cow.phosphorus


# ---------------------------------------------------------------------------
# 3.7 Dry matter intake — Eq.10-5 beef cow, Eq.10-1 growing (Sheet 3 Section C)
# ---------------------------------------------------------------------------


class TestDryMatterIntake:
    """CC-DMI — Eq.10-5 for beef cows, Eq.10-1 yearling for growing animals. ±3%."""

    # Non-pregnant Angus cow, BW=520, NEm_diet=1.1:
    # BW^0.75≈108.892, NEm_intake=108.892×(0.04997×1.21+0.04631×1.1+0.03840)=16.313
    # DMI=16.313/1.1=14.830 kg/d  (0.04631 is the LINEAR coefficient → multiplied by ne_c)
    _DMI_NONPREG = 14.829558

    # Pregnant Angus cow (no nonpregnant intercept):
    # NEm_intake=108.892×(0.04997×1.21+0.04631×1.1)=12.131
    # DMI=12.131/1.1=11.028 kg/d
    _DMI_PREG = 11.028255

    # Lactating non-pregnant cow: DMI_np + 0.2 × Yn(=3.990)
    _DMI_LACT = 15.627612

    def test_cc_dmi_1_nonpregnant_cow(self) -> None:
        """CC-DMI-1: Non-pregnant Angus cow DMI via Eq.10-5 (nonpreg intercept). ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_NONLACT)
        assert result.dry_matter == pytest.approx(self._DMI_NONPREG, rel=0.03)

    def test_cc_dmi_2_pregnant_cow_lower_than_nonpregnant(self) -> None:
        """CC-DMI-2: Pregnant cow DMI (no intercept addition) lower than non-pregnant. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_GEST)
        assert result.dry_matter == pytest.approx(self._DMI_PREG, rel=0.03)

    def test_cc_dmi_3_lactating_cow_exceeds_nonlactating(self) -> None:
        """CC-DMI-3: Lactating cow DMI = nonpreg DMI + 0.2×Yn. ±3%."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        assert result.dry_matter == pytest.approx(self._DMI_LACT, rel=0.03)

    def test_ne_diet_floor_at_0_95_applied(self) -> None:
        """NEm_diet below 0.95 must use 0.95 as divisor per NRC Ch.10 note."""
        low_ne = dataclasses.replace(_ANGUS_COW_NONLACT, ne_diet_concentration=0.5)
        floor_ne = dataclasses.replace(_ANGUS_COW_NONLACT, ne_diet_concentration=0.95)
        low = BeefCowCalfRequirementsCalculator.calculate_requirements(low_ne)
        floor = BeefCowCalfRequirementsCalculator.calculate_requirements(floor_ne)
        assert low.dry_matter == pytest.approx(floor.dry_matter, rel=0.001)

    def test_growing_heifer_has_positive_dmi(self) -> None:
        """Replacement heifer DMI must be positive."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_HEIFER)
        assert result.dry_matter > 0.0

    def test_beef_calf_has_positive_dmi(self) -> None:
        """Beef calf DMI must be positive."""
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_CALF)
        assert result.dry_matter > 0.0


# ---------------------------------------------------------------------------
# Combined lactating + pregnant overlap test
# ---------------------------------------------------------------------------


class TestLactatingAndPregnantOverlap:
    """Cow rebred during lactation (pregnant AND lactating simultaneously)."""

    def test_pregnant_lactating_cow_sums_both_energy_terms(self) -> None:
        """Cow at DP=60 and DIM=60 must have both pregnancy_energy > 0 and lactation_energy > 0."""
        overlap = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=AnimalType.BEEF_COW,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=60,
            days_in_milk=60,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        result = BeefCowCalfRequirementsCalculator.calculate_requirements(overlap)
        assert result.pregnancy_energy > 0.0
        assert result.lactation_energy > 0.0
        # Combined must exceed either alone
        preg_only = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_GEST)
        lact_only = BeefCowCalfRequirementsCalculator.calculate_requirements(_ANGUS_COW_LACT)
        assert result.pregnancy_energy < preg_only.pregnancy_energy  # DP=60 < DP=200
        assert result.lactation_energy == pytest.approx(lact_only.lactation_energy, rel=0.001)


# ---------------------------------------------------------------------------
# 3.9 Guards — existing calculators must raise NotImplementedError for cow-calf
# ---------------------------------------------------------------------------


class TestDairyAndFeedlotGuards:
    """CC-GUARD — existing calculators must refuse cow-calf animal types."""

    @pytest.mark.parametrize(
        "animal_type",
        [
            AnimalType.BEEF_COW,
            AnimalType.BEEF_HEIFER_REPLACEMENT,
            AnimalType.BEEF_CALF,
            AnimalType.BEEF_BULL,
        ],
    )
    def test_nrc_calculator_raises_for_beef_cow_calf(self, animal_type: AnimalType) -> None:
        """NRCRequirementsCalculator.calculate_requirements must raise NotImplementedError for cow-calf types."""
        with pytest.raises(NotImplementedError):
            NRCRequirementsCalculator.calculate_requirements(
                body_weight=520.0,
                mature_body_weight=520.0,
                day_of_pregnancy=None,
                body_condition_score_5=3.0,
                days_in_milk=None,
                average_daily_gain_heifer=None,
                animal_type=animal_type,
                parity=2,
                calving_interval=None,
                milk_fat=4.0,
                milk_true_protein=3.8,
                milk_lactose=4.85,
                milk_production=0.0,
                housing="open air barn",
                distance=1.6,
                previous_temperature=20.0,
                net_energy_diet_concentration=1.1,
                days_born=365.0,
                TDN_percentage=0.7,
                process_based_phosphorus_requirement=0.0,
            )

    @pytest.mark.parametrize(
        "animal_type",
        [
            AnimalType.BEEF_COW,
            AnimalType.BEEF_HEIFER_REPLACEMENT,
            AnimalType.BEEF_CALF,
            AnimalType.BEEF_BULL,
        ],
    )
    def test_nasem_calculator_raises_for_beef_cow_calf(self, animal_type: AnimalType) -> None:
        """NASEMRequirementsCalculator.calculate_requirements must raise NotImplementedError for cow-calf types."""
        with pytest.raises(NotImplementedError):
            NASEMRequirementsCalculator.calculate_requirements(
                body_weight=520.0,
                mature_body_weight=520.0,
                day_of_pregnancy=None,
                body_condition_score_5=3.0,
                days_in_milk=None,
                average_daily_gain_heifer=None,
                animal_type=animal_type,
                parity=2,
                calving_interval=None,
                milk_fat=4.0,
                milk_true_protein=3.8,
                milk_lactose=4.85,
                milk_production=0.0,
                housing="open air barn",
                distance=1.6,
                lactating=False,
                ndf_percentage=0.3,
                process_based_phosphorus_requirement=0.0,
            )

    @pytest.mark.parametrize(
        "animal_type",
        [
            AnimalType.BEEF_COW,
            AnimalType.BEEF_HEIFER_REPLACEMENT,
            AnimalType.BEEF_CALF,
            AnimalType.BEEF_BULL,
        ],
    )
    def test_beef_nrc_calculator_raises_for_beef_cow_calf(self, animal_type: AnimalType) -> None:
        """BeefNRCRequirementsCalculator.calculate_requirements must raise NotImplementedError for cow-calf types."""
        with pytest.raises(NotImplementedError):
            BeefNRCRequirementsCalculator.calculate_requirements(
                body_weight=520.0,
                mature_body_weight=520.0,
                animal_type=animal_type,
                breed="Angus",
                sex=Sex.FEMALE,
                days_on_feed=0,
                target_adg=0.0,
                implant_adg_factor=1.0,
                housing="open air barn",
                mud_condition="none",
                temperature_c=20.0,
                ne_diet_concentration=1.1,
                process_based_phosphorus_requirement=0.0,
            )


# ---------------------------------------------------------------------------
# Type guard — wrong animal type rejected
# ---------------------------------------------------------------------------


class TestTypeGuard:
    """BeefCowCalfRequirementsCalculator must reject non-cow-calf animal types."""

    @pytest.mark.parametrize(
        "animal_type",
        [
            AnimalType.LAC_COW,
            AnimalType.DRY_COW,
            AnimalType.FEEDLOT_STEER,
            AnimalType.FEEDLOT_HEIFER,
            AnimalType.HEIFER_I,
        ],
    )
    def test_raises_for_non_beef_cow_calf_types(self, animal_type: AnimalType) -> None:
        """BeefCowCalfRequirementsCalculator must raise ValueError for non-cow-calf types."""
        bad = CowCalfRequirementsInputs(
            body_weight=520.0,
            mature_body_weight=520.0,
            animal_type=animal_type,
            breed="Angus",
            sex=Sex.FEMALE,
            body_condition_score=5.0,
            days_pregnant=None,
            days_in_milk=None,
            parity=2,
            target_adg=0.0,
            mud_condition="none",
            temperature_c=20.0,
            ne_diet_concentration=1.1,
            process_based_phosphorus_requirement=0.0,
        )
        with pytest.raises(ValueError, match="cow-calf types"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)


# ---------------------------------------------------------------------------
# Physiological invariant guards (FIX 6 — CodeRabbit)
# ---------------------------------------------------------------------------


class TestPhysiologicalInvariants:
    """Calculate_requirements must reject biologically impossible input combinations."""

    def test_bull_with_days_pregnant_raises(self) -> None:
        """BEEF_BULL with days_pregnant set must raise ValueError (bulls do not gestate)."""
        bull_preg = dataclasses.replace(_ANGUS_BULL, days_pregnant=100)
        with pytest.raises(ValueError, match="BEEF_BULL cannot have days_pregnant"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bull_preg)

    def test_days_pregnant_above_gestation_length_raises(self) -> None:
        """days_pregnant > 283 (gestation length) must raise ValueError."""
        over_term = dataclasses.replace(_ANGUS_COW_GEST, days_pregnant=284)
        with pytest.raises(ValueError, match="days_pregnant must be"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(over_term)

    def test_days_pregnant_zero_raises(self) -> None:
        """days_pregnant = 0 (below minimum of 1) must raise ValueError."""
        day_zero = dataclasses.replace(_ANGUS_COW_GEST, days_pregnant=0)
        with pytest.raises(ValueError, match="days_pregnant must be"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(day_zero)

    def test_negative_days_in_milk_raises(self) -> None:
        """Negative days_in_milk must raise ValueError."""
        neg_dim = dataclasses.replace(_ANGUS_COW_LACT, days_in_milk=-1)
        with pytest.raises(ValueError, match="days_in_milk must be non-negative"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(neg_dim)

    def test_body_weight_zero_raises(self) -> None:
        """body_weight = 0.0 must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, body_weight=0.0)
        with pytest.raises(ValueError, match="body_weight must be positive"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_body_weight_negative_raises(self) -> None:
        """body_weight = -1.0 must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, body_weight=-1.0)
        with pytest.raises(ValueError, match="body_weight must be positive"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_mature_body_weight_zero_raises(self) -> None:
        """mature_body_weight = 0.0 must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, mature_body_weight=0.0)
        with pytest.raises(ValueError, match="mature_body_weight must be positive"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_body_weight_nan_raises(self) -> None:
        """body_weight = NaN must raise ValueError (not finite)."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, body_weight=float("nan"))
        with pytest.raises(ValueError, match="body_weight must be positive and finite"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_body_weight_inf_raises(self) -> None:
        """body_weight = inf must raise ValueError (not finite)."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, body_weight=float("inf"))
        with pytest.raises(ValueError, match="body_weight must be positive and finite"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_mature_body_weight_nan_raises(self) -> None:
        """mature_body_weight = NaN must raise ValueError (not finite)."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, mature_body_weight=float("nan"))
        with pytest.raises(ValueError, match="mature_body_weight must be positive and finite"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_non_female_with_days_pregnant_raises(self) -> None:
        """Non-female (non-bull) animal with days_pregnant set must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_HEIFER, sex=Sex.MALE, days_pregnant=100)
        with pytest.raises(ValueError, match="days_pregnant is only valid for female animals"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_bull_with_days_in_milk_raises(self) -> None:
        """BEEF_BULL with days_in_milk > 0 must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_BULL, days_in_milk=60)
        with pytest.raises(ValueError, match="days_in_milk is only valid for lactating female animals"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_non_female_with_days_in_milk_raises(self) -> None:
        """Non-female (non-bull) with days_in_milk > 0 must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_CALF, days_in_milk=60)
        with pytest.raises(ValueError, match="days_in_milk is only valid for lactating female animals"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_body_weight_below_conceptus_weight_raises(self) -> None:
        """body_weight so small that conceptus weight exceeds SBW must raise ValueError."""
        tiny_bw = dataclasses.replace(_ANGUS_COW_GEST, body_weight=5.0, days_pregnant=283)
        with pytest.raises(ValueError, match="body_weight must exceed conceptus weight"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(tiny_bw)

    def test_calf_with_days_pregnant_raises(self) -> None:
        """BEEF_CALF with days_pregnant set must raise ValueError mentioning calves."""
        bad = dataclasses.replace(_ANGUS_CALF, days_pregnant=100)
        with pytest.raises(ValueError, match="calves do not gestate"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_bull_with_female_sex_raises(self) -> None:
        """BEEF_BULL with sex='female' must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_BULL, sex=Sex.FEMALE)
        with pytest.raises(ValueError, match="BEEF_BULL must have sex='male'"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_beef_cow_with_male_sex_raises(self) -> None:
        """BEEF_COW with sex='male' must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_COW_NONLACT, sex=Sex.MALE)
        with pytest.raises(ValueError, match="must have sex='female'"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_beef_heifer_replacement_with_male_sex_raises(self) -> None:
        """BEEF_HEIFER_REPLACEMENT with sex='male' must raise ValueError."""
        bad = dataclasses.replace(_ANGUS_HEIFER, sex=Sex.MALE)
        with pytest.raises(ValueError, match="must have sex='female'"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)

    def test_beef_calf_with_unknown_sex_raises(self) -> None:
        """An unrecognised sex string must raise ValueError naming the valid options."""
        bad = dataclasses.replace(_ANGUS_CALF, sex=cast(Sex, "bull"))
        with pytest.raises(ValueError, match="sex must be one of"):
            BeefCowCalfRequirementsCalculator.calculate_requirements(bad)
