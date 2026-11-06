"""Beef NRC 2016 nutrition requirements calculator.

References: NRC (2016) Nutrient Requirements of Beef Cattle, 8th ed.
  Ch. 10 (Feed Intake), Ch. 11 (Maintenance), Ch. 12 (Growth), Ch. 6 (Protein),
  Ch. 7 (Minerals), Ch. 19 (Model Equations).
"""

from __future__ import annotations

import math

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import Sex
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nutrition_requirements_calculator import (
    NutritionRequirementsCalculator,
)
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.general_constants import GeneralConstants


class BeefNRCRequirementsCalculator(NutritionRequirementsCalculator):
    """Nutrition requirements calculator for feedlot cattle — NRC 2016 (Beef)."""

    @classmethod
    def calculate_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        animal_type: AnimalType,
        breed: str,
        sex: Sex,
        days_on_feed: int,
        target_adg: float,
        implant_adg_factor: float,
        housing: str,
        mud_condition: str,
        temperature_c: float,
        ne_diet_concentration: float,
        process_based_phosphorus_requirement: float,
        relative_humidity_pct: float | None = None,
        compensatory_gain_factor: float = 1.0,
    ) -> NutritionRequirements:
        """
        Calculate all nutritional requirements for a feedlot finishing animal.

        Parameters
        ----------
        body_weight : float
            Live body weight (kg).
        mature_body_weight : float
            Frame-based mature body weight (kg); used to derive MSBW and EQSBW.
        animal_type : AnimalType
            Must be FEEDLOT_STEER or FEEDLOT_HEIFER.
        breed : str
            Breed string (e.g. 'Angus') for NRC 2016 Table 19-1 BE lookup.
        sex : Sex
            Sex enum member for NRC 2016 Table 19-1 SEX multiplier.
        days_on_feed : int
            Days since pen placement; drives receiving-period DMI adjustment.
        target_adg : float
            Target average daily gain (kg/d live weight).
        implant_adg_factor : float
            ADG multiplier from growth implant (1.0 = no implant).
        housing : str
            'Barn' or 'Open_Lot' (reserved for future activity adjustments).
        mud_condition : str
            'none', 'mild', or 'severe'; drives NRC 2016 mud multiplier.
        temperature_c : float
            Ambient temperature for cold-stress a2 term (°C).
        ne_diet_concentration : float
            NEm concentration of the current ration (Mcal/kg DM).
        process_based_phosphorus_requirement : float
            Phosphorus requirement from the process-based submodule (g/d).
        relative_humidity_pct : float | None
            Relative humidity (0-100%) for the THI heat stress modifiers.
            ``None`` disables heat stress and leaves DMI and maintenance
            energy unchanged.
        compensatory_gain_factor : float
            ADG multiplier earned by prior nutritional restriction. 1.0 means
            no compensatory gain. Clamped to ``CG_MAX_ADG_MULTIPLIER``.

        Returns
        -------
        NutritionRequirements
            All nutritional requirements; pregnancy/lactation/activity fields = 0.

        """
        if animal_type.is_beef_stocker:
            raise NotImplementedError(f"Use BeefStockerRequirementsCalculator for {animal_type.value}.")
        if animal_type.is_beef_cow_calf:
            raise NotImplementedError(
                f"BeefNRCRequirementsCalculator is feedlot-only. "
                f"Use BeefCowCalfRequirementsCalculator for {animal_type.value}."
            )
        if not animal_type.is_feedlot:
            raise ValueError(
                f"BeefNRCRequirementsCalculator only handles feedlot animal types, " f"got {animal_type.value}."
            )

        sbw = cls._calculate_sbw(body_weight)
        msbw = mature_body_weight * 0.96
        eqsbw = cls._calculate_eqsbw(sbw, msbw)
        eqebw = cls._calculate_eqebw(eqsbw)

        cls.validate_compensatory_gain_factor(compensatory_gain_factor)
        effective_adg = cls._apply_compensatory_gain(target_adg * implant_adg_factor, compensatory_gain_factor)
        ebg = effective_adg * 0.956  # EBG = 0.956 × ADG (NRC 2016 Ch. 12)

        ne_maintenance = cls._calculate_maintenance_energy(sbw, breed, sex, housing, mud_condition, temperature_c)
        ne_growth = cls._calculate_growth_energy(eqebw, ebg)

        np_growth = cls._calculate_np_growth(effective_adg, ne_growth)
        mp = cls._calculate_metabolizable_protein(body_weight, np_growth, eqsbw)

        calcium = cls._calculate_calcium(sbw, np_growth)
        phosphorus = cls._calculate_phosphorus(sbw, np_growth)

        dmi = cls._calculate_dmi(body_weight, ne_diet_concentration, days_on_feed)

        cls.validate_relative_humidity(relative_humidity_pct)
        dmi, ne_maintenance = cls._apply_heat_stress(dmi, ne_maintenance, temperature_c, relative_humidity_pct)

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
            maintenance_energy=ne_maintenance,
            growth_energy=ne_growth,
            pregnancy_energy=0.0,
            lactation_energy=0.0,
            metabolizable_protein=mp,
            calcium=calcium,
            phosphorus=phosphorus,
            process_based_phosphorus=process_based_phosphorus_requirement,
            dry_matter=dmi,
            activity_energy=0.0,
            essential_amino_acids=empty_aa,
        )

    @staticmethod
    def _calculate_sbw(body_weight: float) -> float:
        """
        Shrunk body weight — removes gut fill.

        Parameters
        ----------
        body_weight : float
            Live body weight (kg).

        Returns
        -------
        float
            SBW = 0.96 × BW (kg). NRC 2016 Ch. 11.

        """
        return body_weight * 0.96

    @staticmethod
    def _calculate_ebw(sbw: float) -> float:
        """
        Empty body weight from shrunk body weight.

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).

        Returns
        -------
        float
            EBW = 0.891 × SBW (kg). NRC 2016 Ch. 12.

        """
        return sbw * 0.891

    @staticmethod
    def _calculate_eqsbw(sbw: float, msbw: float, srw: float = 478.0) -> float:
        """
        Equivalent shrunk body weight — normalises across frame sizes.

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        msbw : float
            Mature SBW = 0.96 × mature_BW (kg).
        srw : float, optional
            Standard reference weight for Choice-grade steer (kg).
            NRC 2016 Table 12-2 default is 478 kg.

        Returns
        -------
        float
            EQSBW = SBW × (SRW / MSBW) (kg). NRC 2016 Ch. 12.

        """
        return sbw * (srw / msbw)

    @staticmethod
    def _calculate_eqebw(eqsbw: float) -> float:
        """
        Equivalent empty body weight.

        Parameters
        ----------
        eqsbw : float
            Equivalent shrunk body weight (kg).

        Returns
        -------
        float
            EQEBW = 0.891 × EQSBW (kg). Used as weight basis in NEg equation.

        """
        return eqsbw * 0.891

    @staticmethod
    def calculate_thi(temperature_c: float, relative_humidity_pct: float) -> float:
        """
        Temperature-Humidity Index for beef cattle heat stress.

        Parameters
        ----------
        temperature_c : float
            Dry-bulb air temperature (°C).
        relative_humidity_pct : float
            Relative humidity (0-100%).

        Returns
        -------
        float
            THI value. Values above 72 indicate heat stress.

        Notes
        -----
        THI = T_F - (0.55 - 0.0055 x RH) x (T_F - 58), with T_F = 1.8 x T + 32
        (BEEF_THI_HUMIDITY_INTERCEPT, BEEF_THI_HUMIDITY_SLOPE,
        BEEF_THI_REFERENCE_TEMPERATURE_F).

        The second bracket is ``T_F - 58`` (equivalently ``1.8 * T - 26``),
        not ``T_F - 26``. The two
        differ by 32 and the wrong form understates THI by roughly 3.5 units
        at 30 °C / 80% RH, which would silently suppress heat stress
        throughout. At 30 °C / 80% RH this yields 82.92.

        Source: NRC 2016 Ch. 11 (Maintenance, heat stress NEhs).
        """
        temperature_f = (
            GeneralConstants.CELSIUS_TO_FAHRENHEIT_SCALE * temperature_c + GeneralConstants.CELSIUS_TO_FAHRENHEIT_OFFSET
        )
        humidity_factor = (
            AnimalModuleConstants.BEEF_THI_HUMIDITY_INTERCEPT
            - AnimalModuleConstants.BEEF_THI_HUMIDITY_SLOPE * relative_humidity_pct
        )
        temperature_above_reference_f = temperature_f - AnimalModuleConstants.BEEF_THI_REFERENCE_TEMPERATURE_F
        return temperature_f - humidity_factor * temperature_above_reference_f

    @staticmethod
    def _interpolate_heat_stress(thi: float, multipliers: tuple[float, ...]) -> float:
        """
        Piecewise-linear heat stress multiplier for a given THI.

        Parameters
        ----------
        thi : float
            Temperature-Humidity Index, from :meth:`calculate_thi`.
        multipliers : tuple[float, ...]
            Multiplier at each anchor in ``BEEF_THI_BREAKPOINTS``, same length
            and paired one-to-one.

        Returns
        -------
        float
            Below the first anchor, the first multiplier; above the last, the
            last; between anchors, linearly interpolated.

        Raises
        ------
        ValueError
            If ``multipliers`` is not the same length as the anchor tuple.
            Adding an anchor without its multiplier would otherwise shift the
            whole response silently.
        """
        breakpoints = AnimalModuleConstants.BEEF_THI_BREAKPOINTS
        if len(multipliers) != len(breakpoints):
            raise ValueError(
                f"heat stress multipliers must pair one-to-one with BEEF_THI_BREAKPOINTS: "
                f"got {len(multipliers)} multipliers for {len(breakpoints)} anchors"
            )
        if thi <= breakpoints[0]:
            return multipliers[0]
        if thi >= breakpoints[-1]:
            return multipliers[-1]
        for index in range(len(breakpoints) - 1):
            if breakpoints[index] <= thi < breakpoints[index + 1]:
                span = breakpoints[index + 1] - breakpoints[index]
                fraction = (thi - breakpoints[index]) / span
                return multipliers[index] + fraction * (multipliers[index + 1] - multipliers[index])
        return multipliers[-1]

    @classmethod
    def _apply_heat_stress(
        cls,
        dmi: float,
        ne_maintenance: float,
        temperature_c: float,
        relative_humidity_pct: float | None,
    ) -> tuple[float, float]:
        """
        Scale DMI and maintenance energy for heat stress.

        Parameters
        ----------
        dmi : float
            Predicted dry matter intake before heat stress (kg/d).
        ne_maintenance : float
            Maintenance energy before heat stress (Mcal/d).
        temperature_c : float
            Ambient temperature (°C).
        relative_humidity_pct : float | None
            Relative humidity (0-100%). ``None`` disables heat stress and
            returns both values unchanged.

        Returns
        -------
        tuple[float, float]
            The heat-stress-adjusted ``(dmi, ne_maintenance)``.

        Notes
        -----
        Applied once per animal at the ``calculate_requirements`` level rather
        than inside ``_calculate_maintenance_energy``, which the stocker
        calculator also calls — putting it there would apply the multiplier
        twice on the feedlot path.

        No lower floor on DMI is needed: every multiplier is positive and the
        interpolation is bounded by the tuple.
        """
        if relative_humidity_pct is None:
            return dmi, ne_maintenance
        thi = cls.calculate_thi(temperature_c, relative_humidity_pct)
        dmi_factor = cls._interpolate_heat_stress(thi, AnimalModuleConstants.BEEF_HEAT_STRESS_DMI_MULTIPLIERS)
        nem_factor = cls._interpolate_heat_stress(thi, AnimalModuleConstants.BEEF_HEAT_STRESS_NEM_MULTIPLIERS)
        return dmi * dmi_factor, ne_maintenance * nem_factor

    @staticmethod
    def validate_compensatory_gain_factor(compensatory_gain_factor: float) -> None:
        """
        Raise ValueError for a compensatory gain factor below 1.0 or non-finite.

        Parameters
        ----------
        compensatory_gain_factor : float
            Multiplier to check. 1.0 means no compensatory gain.

        Raises
        ------
        ValueError
            If the value is NaN, infinite, or below 1.0. Compensatory gain is
            an uplift; a value below 1.0 is a caller error rather than a
            growth penalty.
        """
        if not math.isfinite(compensatory_gain_factor) or compensatory_gain_factor < 1.0:
            raise ValueError(f"compensatory_gain_factor must be >= 1.0 and finite, got {compensatory_gain_factor}")

    @staticmethod
    def _apply_compensatory_gain(base_adg: float, compensatory_gain_factor: float) -> float:
        """
        Scale a base ADG by the compensatory gain factor, under the ceiling.

        Parameters
        ----------
        base_adg : float
            ADG after every other multiplier, the implant factor included
            (kg/d). This is what the uplift scales.
        compensatory_gain_factor : float
            ADG multiplier earned by prior nutritional restriction.

        Returns
        -------
        float
            ``base_adg`` scaled by the factor, with the factor itself clamped
            to ``CG_MAX_ADG_MULTIPLIER``.

        Notes
        -----
        The ceiling bounds the compensatory uplift, not total ADG. Capping the
        product against ``target_adg`` would clip the implant factor whenever
        it exceeded the ceiling — changing feedlot growth for a user who never
        enabled compensatory gain.

        The factor is clamped here rather than trusted from the caller, so one
        built elsewhere cannot push growth past what is biologically plausible.

        Both the nutrition calculators and the feedlot body-weight update call
        this, so the two cannot drift apart.
        """
        return base_adg * min(compensatory_gain_factor, AnimalModuleConstants.CG_MAX_ADG_MULTIPLIER)

    @staticmethod
    def validate_relative_humidity(relative_humidity_pct: float | None) -> None:
        """
        Raise ValueError for a humidity outside 0-100% or non-finite.

        Parameters
        ----------
        relative_humidity_pct : float | None
            Relative humidity to check. ``None`` is valid and disables heat
            stress.

        Raises
        ------
        ValueError
            If the value is NaN, infinite, or outside the inclusive 0-100 range.
        """
        if relative_humidity_pct is None:
            return
        if not math.isfinite(relative_humidity_pct) or not 0.0 <= relative_humidity_pct <= 100.0:
            raise ValueError(f"relative_humidity_pct must be 0-100 and finite, got {relative_humidity_pct}")

    @classmethod
    def _calculate_maintenance_energy(
        cls,
        sbw: float,
        breed: str,
        sex: Sex,
        housing: str,
        mud_condition: str,
        temperature_c: float,
    ) -> float:
        """
        Net energy for maintenance (Mcal/d).

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        breed : str
            Breed string for NRC 2016 Table 19-1 BE multiplier.
        sex : Sex
            Sex enum member for NRC 2016 Table 19-1 SEX multiplier.
        housing : str
            Housing type (reserved; not used in current implementation).
        mud_condition : str
            Pen mud depth: 'none', 'mild', or 'severe'.
        temperature_c : float
            Ambient temperature for cold-stress a2 addition (°C).

        Returns
        -------
        float
            NEm (Mcal/d). Base formula NRC 2016 Eq. 11-1.
            Cold-stress a2 term added when temperature < 20 °C (Eq. 11-2).

        """
        be: float = AnimalModuleConstants.BREED_NEm_MULTIPLIER.get(breed, 1.0)
        sex_mult: float = AnimalModuleConstants.SEX_NEm_MULTIPLIER.get(sex, 1.00)
        sbw075: float = sbw**0.75

        # a2 cold-stress addition; zero at thermoneutral (Tp >= 20 °C)
        a2 = max(0.0, 0.0007 * (20.0 - temperature_c))
        ne_m = sbw075 * (0.077 * be * sex_mult + a2)

        mud_multiplier_map = {
            "none": AnimalModuleConstants.MUD_NEm_MULTIPLIER_NONE,
            "mild": AnimalModuleConstants.MUD_NEm_MULTIPLIER_MILD,
            "severe": AnimalModuleConstants.MUD_NEm_MULTIPLIER_SEVERE,
        }
        ne_m *= mud_multiplier_map.get(mud_condition, 1.00)

        return ne_m

    @staticmethod
    def _calculate_growth_energy(eqebw: float, ebg: float) -> float:
        """
        Net energy for growth — retained energy (Mcal/d).

        Parameters
        ----------
        eqebw : float
            Equivalent empty body weight (kg). Use EQEBW = 0.891 × EQSBW.
        ebg : float
            Empty body gain (kg/d). Use EBG = 0.956 × ADG.

        Returns
        -------
        float
            RE = NEg (Mcal/d). NRC 2016 Ch. 12 Eq. 12-3.

        """
        if ebg <= 0.0:
            return 0.0
        eqebw_075: float = eqebw**0.75
        ebg_1097: float = ebg**1.097
        return 0.0635 * eqebw_075 * ebg_1097

    @staticmethod
    def _calculate_np_growth(adg: float, ne_growth: float) -> float:
        """
        Net protein deposited in gain (g/d).

        Parameters
        ----------
        adg : float
            Effective average daily gain — live weight basis (kg/d).
        ne_growth : float
            NEg / retained energy (Mcal/d).

        Returns
        -------
        float
            NPg (g/d) = ADG × (268 - 29.4 × RE/ADG). NRC 2016 Ch. 6.

        """
        if adg <= 0.0 or ne_growth <= 0.0:
            return 0.0
        return max(0.0, adg * (268.0 - 29.4 * ne_growth / adg))

    @staticmethod
    def _calculate_metabolizable_protein(
        body_weight: float,
        np_growth: float,
        eqsbw: float,
    ) -> float:
        """
        Metabolizable protein requirement (g/d).

        Parameters
        ----------
        body_weight : float
            Live body weight (kg). MPm uses live BW^0.75, not SBW.
        np_growth : float
            Net protein in gain (g/d) from _calculate_np_growth.
        eqsbw : float
            Equivalent shrunk body weight (kg). Drives MP efficiency for gain.

        Returns
        -------
        float
            MP (g/d) = MPm + MPg. NRC 2016 Ch. 6 / Box 12-1.

        """
        bw075: float = body_weight**0.75
        mp_maintenance: float = 3.8 * bw075  # live BW per Box 12-1
        if np_growth > 0.0:
            eff_g = max(0.492, 0.834 - 0.00114 * eqsbw)
            mp_growth = np_growth / eff_g
        else:
            mp_growth = 0.0
        return mp_maintenance + mp_growth

    @staticmethod
    def _calculate_calcium(sbw: float, np_growth: float) -> float:
        """
        Dietary calcium requirement (g/d).

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        np_growth : float
            Net protein deposited in gain (g/d).

        Returns
        -------
        float
            Ca (g/d) = net_Ca / 0.50 absorption efficiency.
            NRC 2016 Table 19-3: net_Ca = 0.0308×SBW + NPg×0.142.

        """
        net_ca = 0.0308 * sbw + np_growth * 0.142
        return net_ca / 0.50

    @staticmethod
    def _calculate_phosphorus(sbw: float, np_growth: float) -> float:
        """
        Dietary phosphorus requirement (g/d).

        Parameters
        ----------
        sbw : float
            Shrunk body weight (kg).
        np_growth : float
            Net protein deposited in gain (g/d).

        Returns
        -------
        float
            P (g/d) = net_P / 0.68 absorption efficiency.
            NRC 2016 Table 19-3: net_P = 0.02353×SBW + NPg×0.05735.

        """
        net_p = 0.02353 * sbw + np_growth * 0.05735
        return net_p / 0.68

    @classmethod
    def _calculate_dmi(
        cls,
        body_weight: float,
        ne_diet_concentration: float,
        days_on_feed: int,
    ) -> float:
        """
        Predicted dry matter intake for yearling feedlot cattle (kg/d).

        Parameters
        ----------
        body_weight : float
            Live body weight (kg).
        ne_diet_concentration : float
            NEm concentration of the ration (Mcal/kg DM).
        days_on_feed : int
            Days since pen placement; drives receiving-period adjustment.

        Returns
        -------
        float
            Predicted DMI (kg/d). NRC 2016 Eq. 10-1.

        """
        ne_c: float = max(ne_diet_concentration, 0.95)
        bw075: float = body_weight**0.75
        ne_m_intake: float = bw075 * (0.2435 * ne_c - 0.0466 * ne_c**2 - 0.0869)
        dmi = ne_m_intake / ne_c if ne_m_intake > 0.0 else 0.0

        if days_on_feed <= AnimalModuleConstants.RECEIVING_PERIOD_DAYS:
            dmi *= AnimalModuleConstants.RECEIVING_DMI_FRACTION

        return max(dmi, AnimalModuleConstants.FEEDLOT_MIN_DMI_RATIO * body_weight)
