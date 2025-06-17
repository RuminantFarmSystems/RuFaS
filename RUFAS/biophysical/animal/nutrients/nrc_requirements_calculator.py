from numpy import exp

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.general_constants import GeneralConstants

from .nutrition_requirements_calculator import NutritionRequirementsCalculator


class NRCRequirementsCalculator(NutritionRequirementsCalculator):
    """Animal requirements calculator class, based on NRC's methodology."""

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
        previous_temperature: float | None,
        net_energy_diet_concentration: float,
        days_born: float,
        TDN_percentage: float,
        process_based_phosphorus_requirement: float,
    ) -> NutritionRequirements:
        """
        Calculates energy and nutrition requirements for an animal using the NRC methodology.

        Parameters
        ----------
        body_weight : float
            Body weight (kg).
        mature_body_weight : float
            Mature body weight (kg).
        day_of_pregnancy : int
            Day of pregnancy (days).
        body_condition_score_5 : float
            Body condition score (score from 1 to 5).
        days_in_milk : int | None
            Days in milk (days).
        average_daily_gain_heifer : float
            Average daily gain (grams per day).
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.
        parity : int
            Parity number (lactation 1, 2.. n).
        calving_interval : int
            Calving interval (days).
        milk_fat : float
            Fat contents in milk (%).
        milk_true_protein : float
            True protein contents in milk (%).
        milk_lactose : float
            Lactose contents in milk (%).
        milk_production: float
            Daily milk yield (kg).
        housing : str
            Housing type (Barn or Grazing).
        distance : float
            Distance walked (m).
        previous_temperature : float
            Adjustment for previous temperature.
        net_energy_diet_concentration : float
            Metabolizable energy density of formulated ration.
        days_born : float
            Number of days since birth (days).
        TDN_percentage : float
            Percentage of Total Digestible Nutrients in previously fed ration (%).

        Returns
        -------
        NutritionRequirements
            NutritionRequirements instance containing all the required amounts of energy and nutrition.

        """
        maintenance_requirement, conceptus_weight, calf_birth_weight = cls._calculate_maintenance_energy_requirements(
            body_weight, mature_body_weight, day_of_pregnancy, body_condition_score_5, previous_temperature, animal_type
        )
        growth_requirement, average_daily_gain, shrunk_body_weight = cls._calculate_growth_energy_requirements(
            body_weight,
            mature_body_weight,
            conceptus_weight,
            animal_type,
            parity,
            calving_interval,
            average_daily_gain_heifer,
        )
        pregnancy_requirement = cls._calculate_pregnancy_energy_requirements(day_of_pregnancy, calf_birth_weight)
        lactation_requirement = cls._calculate_lactation_energy_requirements(
            animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
        )
        dry_matter_intake = cls._calculate_dry_matter_intake(
            animal_type,
            body_weight,
            day_of_pregnancy,
            days_in_milk,
            milk_production,
            milk_fat,
            net_energy_diet_concentration,
            days_born,
        )
        protein_requirement = cls._calculate_protein_requirement(
            body_weight,
            conceptus_weight,
            day_of_pregnancy,
            animal_type,
            milk_production,
            milk_true_protein,
            calf_birth_weight,
            growth_requirement,
            average_daily_gain,
            shrunk_body_weight,
            dry_matter_intake,
            TDN_percentage,
        )
        calcium_requirement = cls._calculate_calcium_requirement(
            body_weight, mature_body_weight, day_of_pregnancy, animal_type, average_daily_gain, milk_production
        )
        phosphorus_requirement = cls._calculate_phosphorus_requirement(
            body_weight,
            mature_body_weight,
            day_of_pregnancy,
            milk_production,
            animal_type,
            average_daily_gain,
            dry_matter_intake,
        )
        activity_requirement = cls._calculate_activity_energy_requirements(body_weight, housing, distance)

        essential_amino_acids = EssentialAminoAcidRequirements(
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
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        body_condition_score_5: float,
        previous_temperature: float | None,
        animal_type: AnimalType,
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for maintenance, conceptus weight, and calf birth weight according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg).
        mature_body_weight : float
            Mature body weight (kg).
        day_of_pregnancy : int
            Day of pregnancy (days).
        body_condition_score_5 : float
            Body condition score (score from 1 to 5).
        previous_temperature : float
            Adjustment for previous temperature.
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.

        Returns
        -------
        tuple[float, float, float]
            Net energy requirement for maintenance (Mcal/day), conceptus weight (kg), and calf birth weight (kg).

        Notes
        -----
        [AN.NRC.1]
        [AN.NRC.2]
        [AN.NRC.3]
        [AN.NRC.4]
        [AN.NRC.5]
        [AN.NRC.6]
        [AN.NRC.7]
        Energy requirements for activity are not included within calculations for maintenance.

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 2 "Energy",pp. 18-25, 2001.

        """
        calf_birth_weight = mature_body_weight * 0.06275 if day_of_pregnancy else 0.0
        conceptus_weight = 0.0
        if day_of_pregnancy and day_of_pregnancy > 190:
            conceptus_weight = (18 + (day_of_pregnancy - 190) * 0.665) * (calf_birth_weight / 45)

        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            net_energy_maintenance = 0.08 * (body_weight - conceptus_weight) ** 0.75
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            body_condition_score_9 = (body_condition_score_5 - 1) * 2 + 1
            net_energy_maintenance = (body_weight - conceptus_weight) ** (0.75) * (
                0.086 * (0.8 + (body_condition_score_9 - 1) * 0.05)
            ) + 0.0007 * (20 - previous_temperature)

        return net_energy_maintenance, conceptus_weight, calf_birth_weight

    @classmethod
    def _calculate_growth_energy_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        conceptus_weight: float,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
        average_daily_gain_heifer: float | None,
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for growth, average daily gain and estimate of shrunk body weight according to NRC
        (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg).
        mature_body_weight : float
            Mature body weight (kg).
        conceptus_weight : float
            Conceptus weight (kg).
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum.
        parity : int
            Parity number (lactation 1, 2.. n).
        calving_interval : int
            Calving interval (days).
        average_daily_gain_heifer : float
            Average daily gain (grams per day).

        Notes
        ------
        [AN.NRC.13], [AN.NRC.14], [AN.NRC.15], [AN.NRC.16], [AN.NRC.17], [AN.NRC.18], [AN.NRC.19]
        [AN.NRC.20], [AN.NRC.21], [AN.NRC.22], [AN.NRC.23], [AN.NRC.24]
        Returns
        -------
        tuple[float, float, float]
            Net energy requirement for growth (Mcal/d), average daily gain (g/d), equivalent shrunk body weight (kg).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 11 "Growth", pp. 234-243, 2001.

        """
        mature_shrunk_body_weight = 0.96 * mature_body_weight

        shrunk_body_weight = 0.96 * body_weight

        equivalent_shrunk_body_weight = (shrunk_body_weight - conceptus_weight) * (478 / mature_shrunk_body_weight)

        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            if parity == 1 and calving_interval != 0:
                average_daily_gain = ((0.92 - 0.82) * mature_shrunk_body_weight) / calving_interval
            elif parity == 2 and calving_interval != 0:
                average_daily_gain = ((1 - 0.92) * mature_shrunk_body_weight) / calving_interval
            else:
                average_daily_gain = 0.0
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            average_daily_gain = max(average_daily_gain_heifer, 0.0)

        equivalent_empty_gain = 0.956 * average_daily_gain

        equivalent_shrunk_body_weight = 0.891 * equivalent_shrunk_body_weight

        net_energy_growth = 0.0635 * equivalent_shrunk_body_weight**0.75 * equivalent_empty_gain**1.097
        return net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight

    @classmethod
    def _calculate_pregnancy_energy_requirements(cls, day_of_pregnancy: int | None, calf_birth_weight: float) -> float:
        """
        Calculates energy requirement for pregnancy according to NRC (2001).

        Parameters
        ----------
        day_of_pregnancy : int
            Day of pregnancy (days).
        calf_birth_weight : float
            Calf birth weight (kg).

        Returns
        -------
        float
            Net energy requirement for pregnancy (Mcal/d).

        Notes
        -----
        [AN.NRC.25], [AN.NRC.26]
        Day_of_pregnancy are counted from 190 day_of_pregnancy once pregnancy is confirmed. Otherwise, this nutritional
        requirement is assumed to be zero.

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 2 "Energy", pp. 21-22, 2001.

        """
        if day_of_pregnancy is None:
            metabolizable_energy_pregnancy_req = 0.0
        elif day_of_pregnancy > 190:
            metabolizable_energy_pregnancy_req = (2 * 0.00159 * day_of_pregnancy - 0.0352) * (
                calf_birth_weight / (45 * 0.14)
            )
        else:
            metabolizable_energy_pregnancy_req = 0.0

        net_energy_pregnancy = metabolizable_energy_pregnancy_req * 0.64
        return net_energy_pregnancy

    @classmethod
    def _calculate_protein_requirement(
        cls,
        body_weight: float,
        conceptus_weight: float,
        day_of_pregnancy: int | None,
        animal_type: AnimalType,
        milk_production: float,
        milk_true_protein: float,
        calf_birth_weight: float,
        net_energy_growth: float,
        average_daily_gain: float,
        equivalent_shrunk_body_weight: float,
        dry_matter_intake_estimate: float,
        TDN_conc: float | None = 0.7,
    ) -> float:
        """
        Calculates the protein requirement for maintenance according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms).
        conceptus_weight : float
            Conceptus weight (kilograms).
        day_of_pregnancy : int
            Day of pregnancy (days).
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.
        milk_production: float
            Milk yield (kg/d).
        milk_true_protein : float
            True protein contents in milk (%).
        calf_birth_weight : float
            Calf birth weight.
        net_energy_growth : float
            Net energy requirement for growth (Mcal/d).
        average_daily_gain : float
            Average daily gain (grams per day).
        equivalent_shrunk_body_weight : float
            Equivalent shrunk body weight (kilograms).
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d).
        TDN_conc:
            Concentration (percent value) of Total Digestible Nutrients in previously fed ration.

        Returns
        -------
        float
            Metabolizable protein requirement (g/day).

        Notes
        -----
         [AN.NRC.29], [AN.NRC.31], [AN.NRC.32],[AN.NRC.33], [AN.NRC.34],[AN.NRC.35],
         [AN.NRC.36], [AN.NRC.37],[AN.NRC.38]
        bacteria_estimate: Bacteria metabolizable protein production (g).
        TDN: Total digestible nutrients
        maintenance: Metabolizable protein requirement for maintenance (g).
        net_growth: Net protein requirement for growth (g).
        metabolizable_to_net_efficiency: Efficiency of converting metabolizable protein to net protein
        metabolizable_growth: Metabolizable protein requirement for growth (g).
        pregnancy: Metabolizable protein requirement for pregnancy (g).
        lactation: Metabolizable protein requirement for lactation (g).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 5 "Protein and Amino acids",pp. 67-69. 2001;

        """

        bacteria_estimate = dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * TDN_conc * 0.13

        maintenance = (
            0.3 * (body_weight - conceptus_weight) ** 0.6
            + 4.1 * (body_weight - conceptus_weight) ** 0.5
            + (
                dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * 0.03
                - 0.5 * (bacteria_estimate / 0.8 - bacteria_estimate)
            )
            + 0.4 * 11.8 * dry_matter_intake_estimate / 0.67
        )

        if average_daily_gain == 0:
            net_growth = 0.0
        else:
            net_growth = average_daily_gain * (268 - 29.4 * (net_energy_growth / average_daily_gain))

        if equivalent_shrunk_body_weight <= 478:
            metabolizable_to_net_efficiency = (83.4 - 0.114 * equivalent_shrunk_body_weight) / 100
        else:
            metabolizable_to_net_efficiency = 0.28908

        metabolizable_growth = net_growth / metabolizable_to_net_efficiency

        if day_of_pregnancy is None:
            pregnancy = 0.0
        elif day_of_pregnancy > 190:
            pregnancy = (0.69 * day_of_pregnancy - 69.2) * (calf_birth_weight / (45 * 0.33))
        else:
            pregnancy = 0.0

        if animal_type in [AnimalType.LAC_COW]:
            lactation = milk_production * (milk_true_protein / 100) * (GeneralConstants.KG_TO_GRAMS / 0.67)

        if animal_type in [AnimalType.LAC_COW]:
            metabolizable_protein_requirement = maintenance + metabolizable_growth + pregnancy + lactation
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III, AnimalType.DRY_COW]:
            metabolizable_protein_requirement = maintenance + metabolizable_growth + pregnancy
        return metabolizable_protein_requirement

    @classmethod
    def _calculate_calcium_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        animal_type: AnimalType,
        average_daily_gain: float,
        milk_production: float,
    ) -> float:
        """
        Calculates total calcium requirement according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms).
        mature_body_weight : float
            Mature body weight (kilograms).
        day_of_pregnancy : int
            Day of pregnancy (days).
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.
        average_daily_gain : float
            Average daily gain (grams per day).
        milk_production: float
            Milk yield (kg/d).

        Notes
        ------
        [AN.NRC.39],[AN.NRC.41], [AN.NRC.43], [AN.NRC.45],[AN.NRC.47], [AN.NRC.49]

        Returns
        -------
        float
            Calcium requirement (grams per day).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 106-109. 2001.

        """
        if animal_type in [AnimalType.LAC_COW]:
            maintenance = 0.031 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [AnimalType.DRY_COW]:
            maintenance = 0.0154 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            maintenance = 0.0154 * body_weight + 0.08 * (body_weight / 100)

        growth = 9.83 * mature_body_weight**0.22 * body_weight ** (-0.22) * (average_daily_gain / 0.96)

        if day_of_pregnancy is None:
            pregnancy = 0.0
        elif day_of_pregnancy > 190:
            pregnancy = 0.02456 * exp((0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy) - 0.02456 * exp(
                (0.05581 - 0.00007 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1)
            )
        else:
            pregnancy = 0.0

        if animal_type in [AnimalType.LAC_COW]:
            lactation = 1.22 * milk_production
            calcium_requirement: float = maintenance + growth + pregnancy + lactation
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III, AnimalType.DRY_COW]:
            calcium_requirement = maintenance + growth + pregnancy

        return calcium_requirement

    @classmethod
    def _calculate_phosphorus_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        milk_production: float,
        animal_type: AnimalType,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
    ) -> float:
        """
        Calculates total phosphorus requirement according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms).
        mature_body_weight : float
            Mature body weight (kilograms).
        day_of_pregnancy : int
            Day of pregnancy (days).
        milk_production: float
            Milk yield (kg/d).
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.
        average_daily_gain : float
            Average daily gain (grams per day).
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg/d).

        Notes
        -------
        [AN.NRC.42], [AN.NRC.44], [AN.NRC.46],[AN.NRC.48], [AN.NRC.50]

        Returns
        -------
        float
            Phosphorus requirement (grams per day).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 109-118. 2001.

        """
        growth: float = (1.2 + 4.635 * mature_body_weight**0.22 * body_weight ** (-0.22)) * (average_daily_gain / 0.96)

        if day_of_pregnancy is None:
            pregnancy: float = 0.0
        elif day_of_pregnancy > 190:
            pregnancy = 0.02743 * exp((0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy) - 0.02743 * exp(
                (0.05527 - 0.000075 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1)
            )
        else:
            pregnancy = 0.0

        if animal_type in [AnimalType.LAC_COW]:
            maintenance: float = 1 * dry_matter_intake_estimate + 0.002 * body_weight
            lactation: float = 0.9 * milk_production
            phosphorus_requirement: float = growth + pregnancy + lactation + maintenance
        elif animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III, AnimalType.DRY_COW]:
            maintenance = 0.8 * dry_matter_intake_estimate + 0.002 * body_weight
            phosphorus_requirement = growth + pregnancy + maintenance

        return phosphorus_requirement

    @classmethod
    def _calculate_dry_matter_intake(
        cls,
        animal_type: AnimalType,
        body_weight: float,
        day_of_pregnancy: int,
        days_in_milk: int | None,
        milk_production: float,
        milk_fat: float,
        net_energy_diet_concentration: float,
        days_born: float,
    ) -> float:
        """
        Calculates dry matter intake according to NRC (2001).

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum.
        body_weight : float
            Body weight (kilograms).
        day_of_pregnancy : int
            Day of pregnancy (days).
        days_in_milk : int
            Days in milk (days).
        milk_production : float
            Milk yield (kg/d).
        milk_fat : float
            Fat contents in milk (%).
        net_energy_diet_concentration : float
            Metabolizable energy density of formulated ration.
        days_born : float
            Number of days since birth (days).

        Returns
        -------
        dry_matter_intake_estimate : float
            Dry matter intake (kilograms per day).

        Notes
        -----
        [AN.NRC.51], [AN.NRC.52], [AN.NRC.53], [AN.NRC.54], [AN.NRC.55]
        The sum of dry matter intake of each feed is assumed to be less than
        dry matter intake estimation (Sum of Feed < dry_matter_intake_estimate).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 1 "Dry Matter Intake", pp. 4; and pp. 325, 2001 (Equations 1 and 2), and pp. 326 for heifers

        """
        if net_energy_diet_concentration < 1.0:
            DivFact = 0.95
        else:
            DivFact = net_energy_diet_concentration

        if animal_type in [AnimalType.LAC_COW]:
            fat_corrected_milk_kg = (0.4 * milk_production) + (15 * milk_fat * (milk_production / 100))
            dry_matter_intake_estimate: float = (0.372 * fat_corrected_milk_kg + 0.0968 * body_weight**0.75) * (
                1 - exp(-0.192 * ((days_in_milk / 7) + 3.67))
            )
        elif animal_type in [AnimalType.DRY_COW]:
            dry_matter_intake_estimate = ((1.97 - 0.75 * exp(0.16 * (day_of_pregnancy - 280))) / 100) * body_weight
        else:
            if days_born and days_born > 365:
                value_to_use = 0.1128
            else:
                value_to_use = 0.0869
            dry_matter_intake_estimate = (
                body_weight**0.75 * (0.2435 * DivFact - 0.0466 * DivFact**2 - value_to_use) / DivFact
            )
            if day_of_pregnancy and day_of_pregnancy >= 210:
                adjustment_factor = 1 + ((210 - day_of_pregnancy) * 0.0025)
                dry_matter_intake_estimate -= adjustment_factor

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
        Calculates the net energy for activity requirement portion of the energy requirements.

        Parameters
        ----------
        body_weight : float
            Body weight (kg).
        housing : str
            Housing type (Barn or Grazing).
        distance : float
            Distance walked (m).

        Returns
        -------
        float
            Net energy requirement for activity (Mcal/day).

        Notes
        -----
        [AN.NRC.8],[AN.NRC.9], [AN.NRC.10], [AN.NRC.11], [AN.NRC.12]
        Activity requirement (net_energy_activity) is proportional to body weight and daily walking distance. Grazing
        system and hilly topography will cost additional energy. Grazing is not implemented yet in the current version
        of code.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.

        """
        distance_km = distance * GeneralConstants.M_TO_KM
        if housing == "Grazing":
            net_energy_activity1: float = 0.0012 * body_weight
        else:
            net_energy_activity1 = 0.0

        net_energy_activity: float = distance_km * 0.00045 * body_weight + net_energy_activity1
        return net_energy_activity
