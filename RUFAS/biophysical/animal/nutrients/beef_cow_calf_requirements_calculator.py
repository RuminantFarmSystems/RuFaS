"""Beef NRC 2016 nutrition requirements calculator for the cow-calf phase.

References: NRC (2016) Nutrient Requirements of Beef Cattle, 8th ed.
  Ch. 10 (Feed Intake, Eq.10-1 and 10-5), Ch. 11 (Maintenance), Ch. 13 (Cow-Calf),
  Ch. 19 (Model Equations: 19-1 to 19-42, 19-69).

Full cold/heat stress model (EI, TI, LCT, MEcs via Ch.16) is a named future
enhancement — only the a2 cold-stress term is implemented here (same as feedlot).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.beef_nrc_requirements_calculator import BeefNRCRequirementsCalculator
from RUFAS.biophysical.animal.nutrients.nutrition_requirements_calculator import NutritionRequirementsCalculator
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


@dataclass
class CowCalfRequirementsInputs:
    """
    Inputs for BeefCowCalfRequirementsCalculator.calculate_requirements().

    Attributes
    ----------
    body_weight : float
        Live body weight, non-pregnant basis (kg). Does NOT include conceptus mass.
    mature_body_weight : float
        Frame-based mature body weight (kg); used to derive MSBW and EQSBW.
    animal_type : AnimalType
        Must be BEEF_COW, BEEF_HEIFER_REPLACEMENT, BEEF_CALF, or BEEF_BULL.
    breed : str
        Breed string for NRC 2016 Table 19-1 lookups (BE, L, CBW, PKYD, milk composition).
    sex : Sex
        Sex enum member; drives SEX multiplier in NEm.
    body_condition_score : float
        Body condition score on the NRC 2016 beef 1–9 scale.
    days_pregnant : int | None
        Day of gestation (1–283). None if not pregnant.
    days_in_milk : int | None
        Days in milk (DIM). None if not lactating.
    parity : int
        0 = heifer (never calved), 1 = first-calf, ≥ 2 = mature cow.
    target_adg : float
        Target average daily gain (kg/d live weight). Zero for non-growing animals.
    mud_condition : str
        'none', 'mild', or 'severe'; drives NRC 2016 mud multiplier.
    temperature_c : float
        Ambient temperature (°C) for cold-stress a2 term.
    ne_diet_concentration : float
        NEm concentration of the current ration (Mcal/kg DM).
    process_based_phosphorus_requirement : float
        Phosphorus requirement from the process-based submodule (g/d).

    """

    body_weight: float
    mature_body_weight: float
    animal_type: AnimalType
    breed: str
    sex: Sex
    body_condition_score: float
    days_pregnant: int | None
    days_in_milk: int | None
    parity: int
    target_adg: float
    mud_condition: str
    temperature_c: float
    ne_diet_concentration: float
    process_based_phosphorus_requirement: float


class BeefCowCalfRequirementsCalculator(NutritionRequirementsCalculator):
    """Nutrition requirements calculator for the beef cow-calf phase — NRC 2016 (Beef)."""

    @classmethod
    def calculate_requirements(cls, inputs: CowCalfRequirementsInputs) -> NutritionRequirements:
        """
        Calculate all nutritional requirements for a beef cow-calf animal.

        Parameters
        ----------
        inputs : CowCalfRequirementsInputs
            Fully populated input dataclass.

        Returns
        -------
        NutritionRequirements
            Nutrition requirements including pregnancy, lactation, and growth terms.

        Raises
        ------
        ValueError
            If any physiological invariant is violated (see _validate_inputs),
            or if conceptus weight exceeds shrunk body weight for a pregnant animal.

        """
        if inputs.animal_type.is_beef_stocker:
            raise NotImplementedError(f"Use BeefStockerRequirementsCalculator for {inputs.animal_type.value}.")
        cls._validate_inputs(inputs)

        cbw: float = AnimalModuleConstants.BREED_CBW_KG.get(
            inputs.breed, AnimalModuleConstants.BEEF_CALF_BIRTH_WEIGHT_KG
        )
        pkyd: float = AnimalModuleConstants.BREED_PEAK_MILK_YIELD_KG_D.get(inputs.breed, 8.0)
        mkfat: float = AnimalModuleConstants.BREED_MILK_FAT_PCT.get(inputs.breed, 4.0)
        mksnf: float = AnimalModuleConstants.BREED_MILK_SNF_PCT.get(inputs.breed, 8.3)
        mkprot: float = AnimalModuleConstants.BREED_MILK_PROTEIN_PCT.get(inputs.breed, 3.8)

        sbw: float = BeefNRCRequirementsCalculator._calculate_sbw(inputs.body_weight)
        msbw: float = inputs.mature_body_weight * 0.96

        ne_preg: float = 0.0
        mp_preg: float = 0.0
        cw: float = 0.0
        if inputs.days_pregnant is not None:
            ne_preg, mp_preg, cw = cls._calculate_gestation_energy(cbw, inputs.days_pregnant)
            if cw >= sbw:
                raise ValueError(
                    f"body_weight must exceed conceptus weight for pregnant animals; "
                    f"shrunk body weight={sbw:.3f}, conceptus weight={cw:.3f}."
                )

        eqsbw: float = BeefNRCRequirementsCalculator._calculate_eqsbw(sbw - cw, msbw)

        ne_growth: float = 0.0
        np_growth: float = 0.0
        if inputs.target_adg > 0.0:
            eqebw: float = BeefNRCRequirementsCalculator._calculate_eqebw(eqsbw)
            ebg: float = inputs.target_adg * 0.956
            ne_growth = BeefNRCRequirementsCalculator._calculate_growth_energy(eqebw, ebg)
            np_growth = BeefNRCRequirementsCalculator._calculate_np_growth(inputs.target_adg, ne_growth)

        yn: float = 0.0
        ne_lact: float = 0.0
        mp_lact: float = 0.0
        is_lactating: bool = inputs.days_in_milk is not None and inputs.days_in_milk > 0
        if is_lactating and inputs.days_in_milk is not None:
            yn, ne_lact, mp_lact = cls._calculate_beef_milk_yield_and_lactation_requirement(
                inputs.days_in_milk, pkyd, mkfat, mksnf, mkprot, inputs.parity
            )

        ne_maint: float = cls._calculate_maintenance_energy(
            sbw,
            inputs.breed,
            inputs.sex,
            inputs.body_condition_score,
            is_lactating,
            inputs.temperature_c,
            inputs.mud_condition,
        )

        mp_base: float = BeefNRCRequirementsCalculator._calculate_metabolizable_protein(
            inputs.body_weight, np_growth, eqsbw
        )

        calcium, phosphorus = cls._calculate_calcium_phosphorus(sbw, np_growth, yn, inputs.days_pregnant, cbw)

        dmi: float = cls._calculate_dmi(
            inputs.body_weight,
            inputs.ne_diet_concentration,
            yn,
            inputs.animal_type,
            inputs.days_pregnant is not None,
        )

        empty_aa = EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        )

        return NutritionRequirements(
            maintenance_energy=ne_maint,
            growth_energy=ne_growth,
            pregnancy_energy=ne_preg,
            lactation_energy=ne_lact,
            metabolizable_protein=mp_base + mp_preg + mp_lact,
            calcium=calcium,
            phosphorus=phosphorus,
            process_based_phosphorus=inputs.process_based_phosphorus_requirement,
            dry_matter=dmi,
            activity_energy=0.0,
            essential_amino_acids=empty_aa,
        )

    @staticmethod
    def _validate_inputs(inputs: CowCalfRequirementsInputs) -> None:
        """
        Validate CowCalfRequirementsInputs and raise ValueError on any violation.

        Parameters
        ----------
        inputs : CowCalfRequirementsInputs
            Fully populated input dataclass.

        Raises
        ------
        ValueError
            If animal_type is not a beef cow-calf type; if sex is not a
            recognised value; if animal_type and sex are inconsistent; if a
            calf, bull, or non-female has days_pregnant;
            if days_pregnant is out of range; if days_in_milk is negative or set
            on a non-lactating animal; or if body_weight / mature_body_weight are
            not positive and finite.

        """
        if not inputs.animal_type.is_beef_cow_calf:
            raise ValueError(
                f"BeefCowCalfRequirementsCalculator only handles cow-calf types; " f"got {inputs.animal_type.value}."
            )
        if inputs.days_pregnant is not None:
            BeefCowCalfRequirementsCalculator._validate_pregnancy_constraints(inputs)
        if inputs.days_pregnant is not None and not (
            1 <= inputs.days_pregnant <= AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
        ):
            raise ValueError(
                f"days_pregnant must be between 1 and "
                f"{AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS}; "
                f"got {inputs.days_pregnant}."
            )
        BeefCowCalfRequirementsCalculator._validate_sex_constraints(inputs)
        if inputs.days_in_milk is not None and inputs.days_in_milk < 0:
            raise ValueError(f"days_in_milk must be non-negative; got {inputs.days_in_milk}.")
        if (
            inputs.days_in_milk is not None
            and inputs.days_in_milk > 0
            and (inputs.animal_type is not AnimalType.BEEF_COW or inputs.sex != Sex.FEMALE)
        ):
            raise ValueError("days_in_milk is only valid for lactating female animals.")
        if not math.isfinite(inputs.body_weight) or inputs.body_weight <= 0.0:
            raise ValueError(f"body_weight must be positive and finite, got {inputs.body_weight}")
        if not math.isfinite(inputs.mature_body_weight) or inputs.mature_body_weight <= 0.0:
            raise ValueError(f"mature_body_weight must be positive and finite, got {inputs.mature_body_weight}")

    @staticmethod
    def _validate_pregnancy_constraints(inputs: CowCalfRequirementsInputs) -> None:
        """
        Validate pregnancy-specific constraints (only called when days_pregnant is not None).

        Parameters
        ----------
        inputs : CowCalfRequirementsInputs
            Input dataclass with days_pregnant confirmed not None by the caller.

        Raises
        ------
        ValueError
            If animal_type cannot gestate (BEEF_CALF or BEEF_BULL), or if sex
            is not 'female'.

        """
        if inputs.animal_type is AnimalType.BEEF_CALF:
            raise ValueError("BEEF_CALF cannot have days_pregnant set; calves do not gestate.")
        if inputs.animal_type is AnimalType.BEEF_BULL:
            raise ValueError("BEEF_BULL cannot have days_pregnant set; bulls do not gestate.")
        if inputs.sex != Sex.FEMALE:
            raise ValueError("days_pregnant is only valid for female animals.")

    @staticmethod
    def _validate_sex_constraints(inputs: CowCalfRequirementsInputs) -> None:
        """
        Validate that sex is a recognised value and is consistent with animal_type.

        Parameters
        ----------
        inputs : CowCalfRequirementsInputs
            Fully populated input dataclass.

        Raises
        ------
        ValueError
            If sex is not in SEX_NEm_MULTIPLIER, or if sex is inconsistent with
            animal_type (BEEF_BULL must be 'male'; BEEF_COW/HEIFER must be 'female').

        """
        if inputs.sex not in AnimalModuleConstants.SEX_NEm_MULTIPLIER:
            valid_sexes = ", ".join(sorted(k.value for k in AnimalModuleConstants.SEX_NEm_MULTIPLIER))
            raise ValueError(f"sex must be one of {valid_sexes}; got {inputs.sex}.")
        if inputs.animal_type is AnimalType.BEEF_BULL and inputs.sex != Sex.MALE:
            raise ValueError("BEEF_BULL must have sex='male'.")
        if inputs.animal_type in (AnimalType.BEEF_COW, AnimalType.BEEF_HEIFER_REPLACEMENT) and inputs.sex != Sex.FEMALE:
            raise ValueError(f"{inputs.animal_type.value} must have sex='female'.")

    @staticmethod
    def _calculate_comp(bcs: float) -> float:
        """
        Body condition adjustment factor for NEm (COMP).

        Parameters
        ----------
        bcs : float
            Body condition score on the NRC 2016 beef 1–9 scale.

        Returns
        -------
        float
            COMP = 0.8 + (BCS − 1) × 0.05. NRC 2016 Ch. 12.

        """
        return 0.8 + (bcs - 1.0) * 0.05

    @staticmethod
    def _calculate_conceptus_weight(cbw: float, days_pregnant: int) -> float:
        """
        Gravid uterus (conceptus) weight during gestation.

        Parameters
        ----------
        cbw : float
            Breed-specific calf birth weight (kg) from NRC 2016 Table 19-1.
        days_pregnant : int
            Day of gestation (1–283).

        Returns
        -------
        float
            CW (kg). NRC 2016 Eq. 19-69.

        """
        dp: float = float(days_pregnant)
        return cbw * 0.01828 * math.exp(0.02 * dp - 0.0000143 * dp**2)

    @classmethod
    def _calculate_maintenance_energy(
        cls,
        sbw: float,
        breed: str,
        sex: Sex,
        bcs: float,
        is_lactating: bool,
        temperature_c: float,
        mud_condition: str,
    ) -> float:
        """
        Net energy for maintenance (Mcal/d).

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        breed : str
            Breed string for NRC 2016 Table 19-1 BE and L lookups.
        sex : Sex
            Sex enum member for NRC 2016 Table 19-1 SEX multiplier.
        bcs : float
            Body condition score (1–9 beef scale) for COMP adjustment.
        is_lactating : bool
            True if the animal is currently lactating; gates the L factor.
        temperature_c : float
            Ambient temperature (°C); drives cold-stress a2 addition.
        mud_condition : str
            'none', 'mild', or 'severe'; drives mud multiplier.

        Returns
        -------
        float
            NEm (Mcal/d). NRC 2016 Eq. 19-1 to 19-4.

        """
        be: float = AnimalModuleConstants.BREED_NEm_MULTIPLIER.get(breed, 1.0)
        l_factor: float = AnimalModuleConstants.BREED_L_FACTOR.get(breed, 1.2) if is_lactating else 1.0
        comp: float = cls._calculate_comp(bcs)
        sex_mult: float = AnimalModuleConstants.SEX_NEm_MULTIPLIER.get(sex, 1.0)
        a2: float = max(0.0, 0.0007 * (20.0 - temperature_c))
        ne_m: float = sbw**0.75 * (0.077 * be * l_factor * comp * sex_mult + a2)
        mud_map: dict[str, float] = {
            "none": AnimalModuleConstants.MUD_NEm_MULTIPLIER_NONE,
            "mild": AnimalModuleConstants.MUD_NEm_MULTIPLIER_MILD,
            "severe": AnimalModuleConstants.MUD_NEm_MULTIPLIER_SEVERE,
        }
        return ne_m * mud_map.get(mud_condition, 1.0)

    @staticmethod
    def _calculate_gestation_energy(
        cbw: float,
        days_pregnant: int,
    ) -> tuple[float, float, float]:
        """
        Net energy, metabolizable protein, and conceptus weight for gestation.

        Parameters
        ----------
        cbw : float
            Breed-specific calf birth weight (kg) from NRC 2016 Table 19-1.
        days_pregnant : int
            Day of gestation (1–283).

        Returns
        -------
        tuple[float, float, float]
            (NEy Mcal/d, MPy g/d, CW kg). NRC 2016 Eq. 19-37, 19-40, 19-41, 19-69.

        """
        dp: float = float(days_pregnant)
        ney: float = cbw * (0.05855 - 0.0000996 * dp) * math.exp(0.0323 * dp - 0.0000275 * dp**2) / 1000.0
        ypn: float = cbw * (0.001669 - 0.00000211 * dp) * math.exp(0.0278 * dp - 0.0000176 * dp**2) * 6.25
        mpy: float = ypn / AnimalModuleConstants.BEEF_LACTATION_MP_EFFICIENCY
        cw: float = BeefCowCalfRequirementsCalculator._calculate_conceptus_weight(cbw, days_pregnant)
        return ney, mpy, cw

    @staticmethod
    def _calculate_beef_milk_yield_and_lactation_requirement(
        days_in_milk: int,
        pkyd: float,
        mkfat: float,
        mksnf: float,
        mkprot: float,
        parity: int,
        rmy: float = 1.0,
    ) -> tuple[float, float, float]:
        """
        Beef cow milk yield (Wood curve) and lactation NE and MP requirements.

        Parameters
        ----------
        days_in_milk : int
            Days in milk (DIM).
        pkyd : float
            Breed peak milk yield (kg/d) from NRC 2016 Table 19-1.
        mkfat : float
            Milk fat percentage.
        mksnf : float
            Milk solids-not-fat percentage.
        mkprot : float
            Milk protein percentage.
        parity : int
            1 = first-calf heifer (AgeFactor 0.85); ≥ 2 = mature (AgeFactor 1.0).
        rmy : float, optional
            Relative milk yield versus breed standard (1.0 = average).

        Returns
        -------
        tuple[float, float, float]
            (Yn kg/d, NEl Mcal/d, MPl g/d). NRC 2016 Eq. 19-19 to 19-29.
            e^1 in Wood formula is math.e = 2.71828… (I6 verified).

        """
        n: float = days_in_milk / 7.0
        k: float = 1.0 / AnimalModuleConstants.WOOD_PEAK_WEEK
        if pkyd <= 0.0:
            return 0.0, 0.0, 0.0
        apkyd: float = (0.125 * rmy + 0.375) * pkyd
        a: float = 1.0 / (apkyd * k * math.e)
        age_factor: float = (
            AnimalModuleConstants.WOOD_FIRST_CALF_AGE_FACTOR
            if parity == 1
            else AnimalModuleConstants.WOOD_MATURE_AGE_FACTOR
        )
        yn: float = (n / (a * math.exp(k * n))) * age_factor
        energy_density: float = 0.092 * mkfat + 0.049 * mksnf - 0.0569
        nel: float = yn * energy_density
        yprotn: float = yn * mkprot / 100.0
        mpl: float = (yprotn / AnimalModuleConstants.BEEF_LACTATION_MP_EFFICIENCY) * 1000.0
        return yn, nel, mpl

    @staticmethod
    def _calculate_calcium_phosphorus(
        sbw: float,
        np_growth: float,
        yn: float,
        days_pregnant: int | None,
        cbw: float,
    ) -> tuple[float, float]:
        """
        Dietary calcium and phosphorus requirements (g/d).

        All coefficients are dietary values (absorption efficiency already
        incorporated per NRC 2016 Table 19-3: e.g. 0.0308 = 0.0154/0.50 for Ca maint).

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        np_growth : float
            Net protein deposited in gain (g/d); 0 for non-growing animals.
        yn : float
            Milk yield (kg/d); 0 for non-lactating animals.
        days_pregnant : int | None
            Day of gestation (1–283). None if not pregnant.
        cbw : float
            Breed-specific calf birth weight (kg).

        Returns
        -------
        tuple[float, float]
            (Ca g/d, P g/d). Pregnancy terms activate only in last 90 days of gestation.

        """
        preg_threshold: int = (
            AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS - AnimalModuleConstants.BEEF_PREG_LAST_DAYS
        )
        in_last_90d: bool = days_pregnant is not None and days_pregnant >= preg_threshold
        ca_preg: float = AnimalModuleConstants.BEEF_CA_PREG_COEFF * cbw if in_last_90d else 0.0
        p_preg: float = AnimalModuleConstants.BEEF_P_PREG_COEFF * cbw if in_last_90d else 0.0

        calcium: float = (
            AnimalModuleConstants.BEEF_CA_MAINT_COEFF * sbw
            + AnimalModuleConstants.BEEF_CA_GROWTH_COEFF * np_growth
            + AnimalModuleConstants.BEEF_CA_LACT_COEFF * yn
            + ca_preg
        )
        phosphorus: float = (
            AnimalModuleConstants.BEEF_P_MAINT_COEFF * sbw
            + AnimalModuleConstants.BEEF_P_GROWTH_COEFF * np_growth
            + AnimalModuleConstants.BEEF_P_LACT_COEFF * yn
            + p_preg
        )
        return calcium, phosphorus

    @classmethod
    def _calculate_dmi(
        cls,
        body_weight: float,
        ne_diet_concentration: float,
        yn: float,
        animal_type: AnimalType,
        is_pregnant: bool,
    ) -> float:
        """
        Predicted dry matter intake (kg/d).

        Parameters
        ----------
        body_weight : float
            Live body weight, non-pregnant basis (kg).
        ne_diet_concentration : float
            NEm concentration of the ration (Mcal/kg DM).
        yn : float
            Milk yield (kg/d); adds 0.2 × Yn for lactating cows.
        animal_type : AnimalType
            BEEF_HEIFER_REPLACEMENT and BEEF_CALF use Eq.10-1 (yearling);
            BEEF_COW and BEEF_BULL use Eq.10-5 (cow).
        is_pregnant : bool
            True if pregnant; removes the non-pregnant intercept in Eq.10-5.

        Returns
        -------
        float
            Predicted DMI (kg/d). NRC 2016 Eq. 10-5 (cows/bulls) or Eq. 10-1 (growing).

        """
        ne_c: float = max(ne_diet_concentration, 0.95)
        bw075: float = body_weight**0.75

        if animal_type in (AnimalType.BEEF_HEIFER_REPLACEMENT, AnimalType.BEEF_CALF):
            ne_m_intake: float = bw075 * (0.2435 * ne_c - 0.0466 * ne_c**2 - 0.0869)
            return ne_m_intake / ne_c if ne_m_intake > 0.0 else 0.0

        intercept: float = 0.0 if is_pregnant else AnimalModuleConstants.BEEF_DMI_COW_INTERCEPT_NP
        ne_m_intake = bw075 * (
            AnimalModuleConstants.BEEF_DMI_COW_NE_QUAD * ne_c**2
            + AnimalModuleConstants.BEEF_DMI_COW_NE_LINEAR * ne_c
            + intercept
        )
        dmi: float = ne_m_intake / ne_c if ne_m_intake > 0.0 else 0.0
        return dmi + AnimalModuleConstants.BEEF_DMI_COW_LACT_ADJUST * yn
