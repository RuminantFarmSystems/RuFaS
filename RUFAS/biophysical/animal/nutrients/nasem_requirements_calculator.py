from numpy import exp

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.ration.amino_acid import AminoAcidCalculator
from RUFAS.general_constants import GeneralConstants
from RUFAS.user_constants import UserConstants

from .nutrition_requirements_calculator import NutritionRequirementsCalculator


"""Calculator for the amino acid requirements of an animal."""
AMINO_ACID_CALCULATOR = AminoAcidCalculator()


class NASEMRequirementsCalculator(NutritionRequirementsCalculator):
    """Animal requirements calculator class, based on NASEM's methodology."""

    @classmethod
    def calculate_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        body_condition_score_5: float,
        days_in_milk: int | None,
        average_daily_gain_heifer: float | None,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
        milk_fat: float,
        milk_true_protein: float,
        milk_lactose: float,
        milk_production: float,
        housing: str,
        distance: float,
        lactating: bool,
        ndf_percentage: float,
        process_based_phosphorus_requirement: float,
    ) -> NutritionRequirements:
        """
        Calculates energy and nutrition requirements for an animal using the NASEM methodology.

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int | None
            Day of pregnancy. None if the animal is not pregnant.
        day_of_pregnancy : int | None
            Day of pregnancy. None if the animal is not pregnant.
        body_condition_score_5 : float
            Body condition score (score; scale from 1 to 5)
        days_in_milk : int | None
            Days in milk. None if the animal is not milking.
        average_daily_gain_heifer : float
            Average daily gain (g).
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum.
        parity : int
            Lactation count of the animal.
        calving_interval : int | None
            Calving interval (days).
        milk_fat : float
            Fat content of milk (%)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_lactose : float
            Lactose contents in milk (%)
        milk_production: float
            Daily milk yield (kg).
        housing : str
            Housing type (Barn or Grazing)
        distance : float
            Distance walked (meters).
        lactating : bool
            True if the animal is milking, else false.
        ndf_percentage : float
            Percentage of Neutral Detergent Fiber in previously fed ration.

        Returns
        -------
        NutritionRequirements
            NutritionRequirements instance containing all the required amounts of energy and nutrition.

        """
        maintenance_requirement, gravid_uterine_weight, uterine_weight = cls._calculate_maintenance_energy_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, days_in_milk
        )
        growth_requirement, average_daily_gain, frame_weight_gain = cls._calculate_growth_energy_requirements(
            body_weight, mature_body_weight, average_daily_gain_heifer, animal_type, parity, calving_interval
        )
        pregnancy_requirement, gravid_uterine_weight_gain = cls._calculate_pregnancy_energy_requirements(
            lactating, day_of_pregnancy, days_in_milk, gravid_uterine_weight, uterine_weight
        )
        lactation_requirement = cls._calculate_lactation_energy_requirements(
            animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
        )
        dry_matter_intake = cls._calculate_dry_matter_intake(
            body_weight,
            mature_body_weight,
            days_in_milk,
            lactating,
            lactation_requirement,
            parity,
            body_condition_score_5,
            ndf_percentage,
        )
        protein_requirement = cls._calculate_protein_requirement(
            lactating,
            body_weight,
            frame_weight_gain,
            gravid_uterine_weight_gain,
            dry_matter_intake,
            milk_true_protein,
            milk_production,
            ndf_percentage,
        )
        calcium_requirement = cls._calculate_calcium_requirement(
            body_weight,
            mature_body_weight,
            day_of_pregnancy,
            average_daily_gain,
            dry_matter_intake,
            milk_true_protein,
            milk_production,
            parity,
        )
        phosphorus_requirement = cls._calculate_phosphorus_requirement(
            body_weight,
            mature_body_weight,
            animal_type,
            day_of_pregnancy,
            average_daily_gain,
            dry_matter_intake,
            milk_true_protein,
            milk_production,
            parity,
        )
        activity_requirement = cls._calculate_activity_energy_requirements(body_weight, housing, distance)

        essential_amino_acids = AMINO_ACID_CALCULATOR.calculate_essential_amino_acid_requirements(
            animal_type=animal_type,
            lactating=lactating,
            body_weight=body_weight,
            frame_weight_gain=frame_weight_gain,
            gravid_uterine_weight_gain=gravid_uterine_weight_gain,
            dry_matter_intake_estimate=dry_matter_intake,
            milk_true_protein=milk_true_protein,
            milk_production=milk_production,
            NDF_conc=ndf_percentage,
        )

        return NutritionRequirements(
            maintenance_energy=maintenance_requirement,
            growth_energy=growth_requirement,
            pregnancy_energy=pregnancy_requirement,
            lactation_energy=lactation_requirement,
            metabolizable_protein=protein_requirement,
            calcium=calcium_requirement,
            phosphorus=phosphorus_requirement,
            process_based_phosphorus=process_based_phosphorus_requirement,
            dry_matter=dry_matter_intake,
            activity_energy=activity_requirement,
            essential_amino_acids=essential_amino_acids,
        )

    @classmethod
    def _calculate_maintenance_energy_requirements(
        cls, body_weight: float, mature_body_weight: float, day_of_pregnancy: int | None, days_in_milk: int | None
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for maintenance, gravid uterine weight, and uterine weight according to NASEM
        (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int | None
            Day of pregnancy. None if the animal is not pregnant.
        days_in_milk : int | None
            Days in milk. None if the animal is not milking.

        Returns
        -------
        tuple[float, float, float]
            Net energy requirement for maintenance (Mcal), gravid uterine weight (kg), and uterine weight (kg).

        Notes
        -----
        [AN.NSM.1], [AN.NSM.2], [AN.NSM.3], [AN.NSM.4], [AN.NSM.5]

        NASEM (2021)[1] does not adjust energy requirements for environmental temperature as it assumes that confinement
        conditions already provide comfort temperature to the animals. This is something to consider and update for the
        grazing module. Instead of calculating `calf_birth_weight`, NASEM (2021) also contains standards
        `calf_birth_weight` and mature_body_weight (tabulated values) for selected breeds (eg., Holstein).Instead of
        estimating conceptus_weight, gain in pregnancy tissues is estimated: `gravid_uterine_weight` and
        `uterine_weight`. `day_of_pregnancy` (Day of pregnancy) was kept instead of DGest (Day ofgestation) as it is in
        NASEM (2021) book.

         References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 29, 2021.

        """
        if day_of_pregnancy is None:
            net_energy_maintenance = 0.10 * body_weight**0.75
            gravid_uterine_weight = 0.0
            uterine_weight = 0.0
        else:
            calf_birth_weight = mature_body_weight * 0.06275
            gravid_uterine_weight = (calf_birth_weight * 1.825) * exp(
                -(0.0243 - (0.0000245 * day_of_pregnancy)) * (280 - day_of_pregnancy)
            )
            if days_in_milk is None:
                days_in_milk = 0
            uterine_weight = ((calf_birth_weight * 0.2288 - 0.204) * exp(-0.2 * days_in_milk)) + 0.204
            net_energy_maintenance = 0.10 * (body_weight - gravid_uterine_weight - uterine_weight) ** 0.75
        return net_energy_maintenance, gravid_uterine_weight, uterine_weight

    @classmethod
    def _calculate_growth_energy_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        average_daily_gain_heifer: float | None,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for growth, and associated growth metrics according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg).
        mature_body_weight : float
            Mature body weight (kg).
        average_daily_gain_heifer : float
            Average daily gain (g).
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum.
        parity : int
            Lactation count of the animal.
        calving_interval : int | None
            Calving interval (days).

        Returns
        -------
        tuple[float, float, float]
            Net energy requirement for frame growth (Mcal), average daily gain (g), and accretion of both fat and
            protein in carcass (g)

        Notes
        -----
        [AN.NSM.11], [AN.NSM.12], [AN.NSM.13], [AN.NSM.14], [AN.NSM.15], [AN.NSM.16], [AN.NSM.17]
        In NASEM (2021)[1], body frame gain (fat + protein) corresponds to the true growth and it is part of the
        calculation which is further partitioned to body reserves or condition gain (or loss), and pregnancy-associated
        gain (considered a pregnancy requirement).

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 32-35, 2021.

        """
        MSBW = 0.96 * mature_body_weight
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            if parity == 1 and calving_interval != 0:
                average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
            elif parity == 2 and calving_interval != 0:
                average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
            else:
                average_daily_gain = 0.0
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            average_daily_gain = max(average_daily_gain_heifer, 0.0)
        else:
            average_daily_gain = 0.0
        EBG = 0.85 * average_daily_gain
        if average_daily_gain == 0:
            average_daily_gain = 0.00001
        FatADG = (0.067 + 0.375 * (body_weight / mature_body_weight)) * EBG / average_daily_gain
        ProtADG = (0.201 - 0.081 * (body_weight / mature_body_weight)) * EBG / average_daily_gain
        frame_weight_gain = FatADG + ProtADG
        REFADG = (9.4 * FatADG + 5.55 * ProtADG) * average_daily_gain
        net_energy_growth = REFADG / 0.61
        return net_energy_growth, average_daily_gain, frame_weight_gain

    @classmethod
    def _calculate_pregnancy_energy_requirements(
        cls,
        lactating: bool,
        day_of_pregnancy: int | None,
        days_in_milk: int | None,
        gravid_uterine_weight: float,
        uterine_weight: float,
    ) -> tuple[float, float]:
        """
        Calculates energy requirement for pregnancy and gravid uterine weight gain

        Parameters
        ----------
        lactating : bool
            True if the animal is milking, else false.
        day_of_pregnancy : int
            Day of pregnancy
        days_in_milk : int
            Days in milk (lactation, days)
        gravid_uterine_weight : float
            Gravid uterine weight (kg)
        uterine_weight : float
            Uterine weight (kg)

        Returns
        -------
        tuple[float, float]
            Net energy requirement for pregnancy (Mcal) and daily energy requirement associated to increased gain of
            reproductive tissues as pregnancy advances (Mcal)

        Notes
        -----
        [AN.NSM.18], [AN.NSM.19], [AN.NSM.20]
        Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to gestation energy efficiency of 0.14;
        and ME to net_energy_lactation efficiency of 0.66.MEpreg = Metabolizable energy requirement for pregnancy,
            Mcal net_energy_lactation/day
        day_of_pregnancy are counted from day 12 of pregnancy once it was confirmed and goes until day 280
            day_of_pregnancy.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 31-32, 2021.

        """

        if day_of_pregnancy is not None:
            gravid_uterine_weight_gain = (0.0243 - (0.0000245 * day_of_pregnancy)) * gravid_uterine_weight
        elif lactating and days_in_milk < 100:
            gravid_uterine_weight_gain = -0.2 * days_in_milk * (uterine_weight - 0.204)
        else:
            gravid_uterine_weight_gain = 0.0

        if gravid_uterine_weight_gain > 0:
            net_energy_pregnancy = gravid_uterine_weight_gain * (0.882 / 0.14) * 0.66
        else:
            net_energy_pregnancy = gravid_uterine_weight_gain * (0.882 / 0.14)
        return net_energy_pregnancy, gravid_uterine_weight_gain

    @classmethod
    def _calculate_protein_requirement(
        cls,
        lactating: bool,
        body_weight: float,
        frame_weight_gain: float,
        gravid_uterine_weight_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        NDF_conc: float,
    ) -> float:
        """
        Calculates protein requirement for maintenance according to NASEM (2021).

        Parameters
        ----------
        lactating : bool
            True if the animal is lactating, else false.
        body_weight : float
            Body weight (kg)
        frame_weight_gain : float
            Frame weight gain refers to the accretion of both fat and protein in carcass (g)
        gravid_uterine_weight_gain : float
            Daily energy requirement associated with increased gain of reproductive tissues as pregnancy advances (Mcal)
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production: float
            Milk yield (kg)
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.

        Returns
        -------
        metabolizable_protein_requirement : float
            Total metabolizable protein requirement (g).

        Notes
        -----
        [AN.NSM.23],[AN.NSM.24],[AN.NSM.25],[AN.NSM.26],[AN.NSM.27],
        [AN.NSM.28],[AN.NSM.29],[AN.NSM.30],[AN.NSM.31], [AN.NSM.36], [AN.NSM.37], [AN.NSM.38], [AN.NSM.39]
        As in the NRC (2021), the protein requirement is also divided into four components: maintenance, growth,
        pregnancy, and lactation (all of them on a metabolizable protein basis (MP, g).
        The MP is defined as the sum of rumen undegraded protein (RUP + microbial protein (MCP).
        MP requirements for maintenance includes: scurf + endogenous urinary loss + metabolic fecal protein.
        Current versions of RuFaS code for both NRC and NASEM do not split MP into physiological functions.
        - scurf_net_protein_req: Net protein requirement for scurf, g
        - endogenous_urine_protein_req: Net protein requirement for endogenous urinary excretion, g
        - metabolic_fecal_crude_protein_req: Crude protein in metabolic fecal protein, g
        - net_metabolic_fecal_crude_protein_req: Net protein requirement for metabolic fecal protein, g
        - frame_growth_net_req: Net protein requirement for body frame weight gain, g
        - gestation_net_protein_req: Net protein requirement for pregnancy, g
        - milk_net_protein_req: Net protein in milk, or milk true protein yield, g
        - target_efficiencies_metabolic_protein: Proposed target efficiencies of converting metabolizable protein to
            export proteins and body gain.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 6 "Protein", pp. 69-104, 2021.

        """
        scurf_net_protein_req: float = 0.20 * body_weight ** (0.60) * 0.85
        endogenous_urine_protein_req: float = 53 * UserConstants.NITROGEN_TO_PROTEIN * body_weight * 0.001
        metabolic_fecal_crude_protein_req: float = (11.62 + 0.134 * NDF_conc) * dry_matter_intake_estimate
        net_metabolic_fecal_crude_protein_req: float = metabolic_fecal_crude_protein_req * 0.73
        frame_growth_net_req: float = frame_weight_gain * 0.11 * 0.86
        gestation_net_protein_req: float = gravid_uterine_weight_gain * 125
        milk_net_protein_req: float = (
            milk_true_protein * GeneralConstants.PERCENTAGE_TO_FRACTION * milk_production * GeneralConstants.KG_TO_GRAMS
        )
        target_efficiencies_metabolic_protein: float = 0.69

        if lactating:
            metabolizable_protein_requirement: float = (
                scurf_net_protein_req
                + net_metabolic_fecal_crude_protein_req
                + milk_net_protein_req
                + frame_growth_net_req
            ) / target_efficiencies_metabolic_protein
        else:
            metabolizable_protein_requirement = (
                scurf_net_protein_req + net_metabolic_fecal_crude_protein_req
            ) / target_efficiencies_metabolic_protein + (frame_growth_net_req / 0.40)
        gestation_denominator = 0.33 if gestation_net_protein_req > 0.0 else 1.0
        metabolizable_protein_requirement += (
            gestation_net_protein_req / gestation_denominator
        ) + endogenous_urine_protein_req

        return metabolizable_protein_requirement

    @classmethod
    def _calculate_calcium_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        parity: int,
    ) -> float:
        """
        Calculates total Calcium requirement according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int | None
            Day of pregnancy (days)
        average_daily_gain : float
            Average daily gain (g)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production : float
            Milk yield (kg)
        parity : int
            Parity number (lactation 1, 2.. n)

        Returns
        -------
        calcium_requirement : float
            Calcium requirement (g)

        Notes
        -----
        [AN.NSM.40], [AN.NSM.42], [AN.NSM.44], [AN.NSM.46], [AN.NSM.48]
        NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 7 "Minerals" pp. 106-110, 2021.

        """
        maintenance_req: float = 0.90 * dry_matter_intake_estimate

        if parity <= 2:
            growth_req: float = ((9.83 * mature_body_weight**-0.22) * body_weight**-0.22) * average_daily_gain
        else:
            growth_req = 0.0

        if day_of_pregnancy is None:
            pregnancy_req: float = 0.0
        else:
            pregnancy_req = 0.02456 * exp((0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy) - 0.02456 * exp(
                (0.05581 - 0.00007 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1)
            ) * (body_weight / 715)

        lactation_req: float = (0.295 + 0.239 * milk_true_protein) * milk_production

        calcium_requirement: float = maintenance_req + growth_req + pregnancy_req + lactation_req
        return max(calcium_requirement, AnimalModuleConstants.MINIMUM_CALCIUM)

    @classmethod
    def _calculate_phosphorus_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        animal_type: AnimalType,
        day_of_pregnancy: int | None,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        parity: int,
    ) -> float:
        """
        Calculates total Phosphorus requirement according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        day_of_pregnancy : int
            Day of pregnancy (days)
        average_daily_gain : float
            Average daily gain (g)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production: float
            Milk yield (kg)
        parity : int
            Parity number (lactation 1, 2.. n)

        Returns
        -------
        phosphorus_requirement : float
            Phosphorus requirement (g)

        Notes
        -----
        [AN.NSM.41], [AN.NSM.43], [AN.NSM.45], [AN.NSM.47], [AN.NSM.49]
        NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 7 "Minerals" pp. 112, 2021.

        """
        if animal_type in [AnimalType.LAC_COW]:
            maintenance_req: float = dry_matter_intake_estimate + 0.0006 * body_weight
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III, AnimalType.DRY_COW]:
            maintenance_req = 0.8 * dry_matter_intake_estimate + 0.0006 * body_weight
        else:
            maintenance_req = 0.0

        if parity <= 2:
            growth_req: float = (1.2 + 4.635 * mature_body_weight**0.22 * body_weight**-0.22) * average_daily_gain
        else:
            growth_req = 0.0

        if day_of_pregnancy is None or day_of_pregnancy < 190:
            pregnancy_req: float = 0.0
        else:
            pregnancy_req = (
                (
                    0.02743 * exp((0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy)
                    - 0.02743 * exp((0.05527 - 0.000075 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
                )
                * body_weight
                / 715
            )

        lactation_req = milk_production * (0.49 + 0.13 * milk_true_protein)

        phosphorus_requirement: float = maintenance_req + growth_req + pregnancy_req + lactation_req

        return max(phosphorus_requirement, AnimalModuleConstants.MINIMUM_PHOSPHORUS)

    @classmethod
    def _calculate_dry_matter_intake(
        cls,
        body_weight: float,
        mature_body_weight: float,
        days_in_milk: int | None,
        lactating: bool,
        net_energy_lactation: float,
        parity: int,
        body_condition_score_5: float,
        NDF_conc: float,
    ) -> float:
        """
        Calculates estimated dry matter intake according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        days_in_milk : int | None
            Days in milk (days)
        lactating : bool
            True if animal is lactating, else false.
        net_energy_lactation : float
            Net energy for lactation
        parity : int
            Parity number
        body_condition_score_5 : float
            Body condition score (score; scale from 1 to 5)
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.

        Returns
        -------
        dry_matter_intake_estimate : float
            Dry matter intake (kg).

        Notes
        -----
        [AN.NSM.50],[AN.NSM.51]
        The sum of dry matter intake of each feed is assumed to be less than
        dry matter intake estimation (Sum of Feed < DMIest).
        There are additional equation in NASEM (2021) book including neutral detergent concentrations in the diet
        for both lactating (page 12) and growing animals (page 14). [1]

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 2 "Dry matter intake" pp. 7-20, 2021.

        """
        if lactating:
            parity_adjustment_factor = 1 if parity > 1 else 0
            dry_matter_intake_estimate = (
                (3.7 + parity_adjustment_factor * 5.7)
                + 0.305 * net_energy_lactation
                + 0.022 * body_weight
                + (-0.689 - 1.87 * parity_adjustment_factor) * body_condition_score_5
            ) * (1 - (0.212 + parity_adjustment_factor * 0.136) * exp(-0.053 * days_in_milk))
        else:
            dry_matter_intake_estimate = (
                0.0226 * mature_body_weight * (1 - exp(-1.47 * (body_weight / mature_body_weight)))
            ) - (
                0.082
                * (
                    NDF_conc
                    - (
                        23.1
                        + 56 * (body_weight / mature_body_weight)
                        - 30.6 * (body_weight / mature_body_weight) ** 2.0
                    )
                )
            )
        return max(
            dry_matter_intake_estimate,
            AnimalModuleConstants.MINIMUM_DAILY_DMI_RATIO * body_weight,
            AnimalModuleConstants.MINIMUM_DMI,
        )

    @classmethod
    def _calculate_activity_energy_requirements(
        cls,
        body_weight: float,
        housing: str,
        distance: float,
    ) -> float:
        """
        Calculates the net energy for activity requirement portion of the energy requirements for animals.

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        housing : str
            Housing type (Barn or Grazing)
        distance : float
            Distance walked (meters).

        Returns
        -------
        net_energy_activity : float
            Net energy requirement for activity (Mcal)

        Notes
        -----
        [AN.NSM.6]. [AN.NSM.7], [AN.NSM.8], [AN.NSM.9], [AN.NSM.10]
         NASEM calculations use distance walked in kilometers, hence the unit conversion. Activity requirement
        (net_energy_activity) is proportional to body weight and daily walking distance. Grazing system and hilly
        topography will cost additional energy. Grazing is not implemented yet in the current version of code.

        This is separate because it must be calculated after grouping due to pen input args and cannot be used
        individually on an animal.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.

        """
        distance_km = distance * GeneralConstants.M_TO_KM
        if housing == "Barn":
            net_energy_activity = distance_km * 0.00035 * body_weight
        elif housing == "Grazing":
            nonpasturekgDMI: float = 1.0
            net_energy_activity = distance_km * body_weight * 0.75 * (600 - 12 * nonpasturekgDMI) / 600
        else:
            net_energy_activity = 0.0
        return net_energy_activity
