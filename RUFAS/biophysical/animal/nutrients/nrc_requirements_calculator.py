from numpy import exp

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.general_constants import GeneralConstants

from .energy_requirements_calculator import EnergyRequirementsCalculator


class NRCRequirementsCalculator(EnergyRequirementsCalculator):

    @classmethod
    def calculate_energy_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        body_condition_score_5: int,
        previous_temperature: float | None,
        animal_type: AnimalType,
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for maintenance, conceptus weight, and calf birth weight

        Calculates the estimated energy requirements for maintenance in megacalories per day,
        as well as conceptus weight (kg) and calf birth weight (kg), according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int
            Day of pregnancy (days)
        body_condition_score_5 : int
            Body condition score (score from 1 to 5)
        previous_temperature : float
            Adjustment for previous temperature
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum

        Returns
        -------
        net_energy_maintenance : float
            Net energy requirement for maintenance (mcal/day)
        conceptus_weight : float
            Conceptus weight (kg)
        calf_birth_weight : float
            Calf birth weight (kg)

        Notes
        -----
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
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            body_condition_score_9 = (body_condition_score_5 - 1) * 2 + 1
            net_energy_maintenance = (body_weight - conceptus_weight) ** (0.75) * (
                0.086 * (0.8 + (body_condition_score_9 - 1) * 0.05)
            ) + 0.0007 * (20 - previous_temperature)
        return net_energy_maintenance, conceptus_weight, calf_birth_weight

    @classmethod
    def calculate_growth_energy_requirements(
        cls,
        body_weight: float,
        mature_body_weight: float,
        conceptus_weight: float,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
        average_daily_gain_heifer: float | None, 
    ) -> tuple[float, float, float]:
        """Calculates energy requirement for growth and associated weight gain parameters.

        The estimated energy requirements for growth in megacalories per day,
        and average daily gain and estimate of shrunk body weight, in kilograms are calculated according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        conceptus_weight : float
            Conceptus weight (kg)
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum
        parity : int
            Parity number (lactation 1, 2.. n)
        calving_interval : int
            Calving interval (days)
        average_daily_gain_heifer : float
            Average daily gain (grams per day)

        Returns
        -------
        net_energy_growth : float
            Net energy requirement for growth (Mcal/d)
        average_daily_gain : float
            Average daily gain (grams per day)
        equivalent_shrunk_body_weight : float
            Equivalent shrunk body weight (kilograms)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 11 "Growth", pp. 234-243, 2001.
        """
        # Activity requirements
        # ---------------------
        # Activity requirements must be calculated after grouping and thus is in a
        # separate function
        # Growth requirements
        # ---------------------
        # [A.Cow.A.7]-[A.Heifer.A.8]
        # Mature shrunk body weight (kg)
        MSBW = 0.96 * mature_body_weight
        # [A.Cow.A.8]-[A.Heifer.A.9]
        # Shrunk body weight (kg)
        SBW = 0.96 * body_weight
        # [A.Cow.A.9]-[A.Heifer.A.10]
        # Empty body weight (kg)
        # EBW = 0.891 * SBW
        # [A.Cow.A.10]-[A.Heifer.A.11]
        # Equivalent shrunk body weight (kg)
        equivalent_shrunk_body_weight = (SBW - conceptus_weight) * (478 / MSBW)
        # [A.Cow.A.11]
        # Average Daily Gain (kg)
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            if parity == 1 and calving_interval != 0:
                average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
            elif parity == 2 and calving_interval != 0:
                average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
            else:
                average_daily_gain = 0.0
        # [A.Heifer.A.12]
        # Average Daily Gain (kg)
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            average_daily_gain = max(average_daily_gain_heifer, 0.0)
        # [A.Cow.A.12]-[A.Heifer.A.13]
        # Equivalent empty weight gain (kg)
        EQEBG = 0.956 * average_daily_gain
        # [A.Cow.A.13]-[A.Heifer.A.14]
        # Equivalent shrunk body weight (kg)
        EQEBW = 0.891 * equivalent_shrunk_body_weight
        # [A.Cow.A.14]-[A.Heifer.A.15]
        # Net energy for growth requirement (Mcal)
        net_energy_growth = 0.0635 * EQEBW**0.75 * EQEBG**1.097
        return net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight

    @classmethod
    def calculate_pregnancy_energy_requirements(cls, day_of_pregnancy: int | None, calf_birth_weight: float) -> float:
        """Calculates energy requirement for pregnancy according to NRC (2001).

        Calculates the estimated energy requirements for pregnancy in megacalories per day

        Parameters
        ----------
        day_of_pregnancy : int
            Day of pregnancy (days)
        calf_birth_weight : float
            Calf birth weight (kilograms)

        Returns
        -------
        net_energy_pregnancy : float
            Net energy requirement for pregnancy (Mcal/d)

        Notes
        -----
        # day_of_pregnancy are counted from 190 day_of_pregnancy once pregnancy is confirmed. Otherwise,
        this nutritional requirement is assumed to be zero.

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 2 "Energy", pp. 21-22, 2001.

        """
        # Pregnancy requirement
        # ---------------------
        # [A.Cow.A.15]-[A.Heifer.A.16]
        # Metabolizable energy requirement for pregnancy (Mcal)
        if day_of_pregnancy is None:
            MEpreg = 0.0
        elif day_of_pregnancy > 190:
            MEpreg = (2 * 0.00159 * day_of_pregnancy - 0.0352) * (calf_birth_weight / (45 * 0.14))
        else:
            MEpreg = 0.0
        # [A.Cow.A.16]-[A.Heifer.A.17]
        # Net energy requirement for pregnancy (Mcal)
        net_energy_pregnancy = MEpreg * 0.64
        return net_energy_pregnancy

    @classmethod
    def calculate_lactation_energy_requirements(
        cls,
        animal_type: AnimalType,
        milk_fat: float,
        milk_true_protein: float,
        milk_lactose: float,
        milk_production: float,
    ) -> float:
        """Calculates energy requirement for lactation according to NRC (2001).

        Calculates the estimated energy requirements for lactation in megacalories per day

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_fat : float
            Fat contents in milk (%)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_lactose : float
            Lactose contents in milk (%)
        milk_production: float
            Milk production (kg/d)

        Returns
        -------
        net_energy_lactation : float
            Net energy requirement for lactation (Mcal/d)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 2 "Energy", pp. 19, 2001.

        """
        # Lactation requirement
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.A.17]
            # Milk energy (Mcal/kg of milk production)
            milk_energy_Mcal_per_kg = 0.0929 * milk_fat + (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
            # [A.Cow.A.18]
            # Net energy requirement for lactation (Mcal)
            net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
        else:
            net_energy_lactation = 0.0
        return net_energy_lactation

    @classmethod
    def calculate_protein_requirement(
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
        """Protein requirement for maintenance according to NRC (2001).

        Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        conceptus_weight : float
            Conceptus weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_production: float
            Milk yield (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        calf_birth_weight : float
            Calf birth weight
        net_energy_growth : float
            Net energy requirement for growth (Mcal/d)
        average_daily_gain : float
            Average daily gain (grams per day)
        equivalent_shrunk_body_weight : float
            Equivalent shrunk body weight (kilograms)
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
        TDN_conc:
            Concentration (percent value) of Total Digestible Nutrients in previously fed ration.

        Returns
        -------
        metabolizable_protein_requirement : float
            Metabolizable protein requirement (grams per day)

        Notes
        -----
        MP_bactria: Bacteria metabolizable protein production, g
        TDN: Total digestible nutrients
        MPm: Metabolizable protein requirement for maintenance, g
        NPg: Net protein requirement for growth, g
        EffMP_NPg: Efficiency of converting metabolizable protein to net protein
        MPg: Metabolizable protein requirement for growth, g
        MPpreg: Metabolizable protein requirement for pregnancy, g
        MPlact: Metabolizable protein requirement for lactation, g

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 5 "Protein and Amino acids",pp. 67-69. 2001;

        """
        # B: PROTEIN REQUIREMENTS:
        # divided into 4 components: maintenance, growth, pregnancy, and lactation
        # --------------------------------------------
        # Maintenance Requirement
        # ---------------------
        # [A.Cow.B.1]-[A.Heifer.B.1]
        # Metabolizable protein requirement for maintenance (g)

        MP_bactria_estimate = dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * TDN_conc * 0.13

        MPm = (
            0.3 * (body_weight - conceptus_weight) ** 0.6
            + 4.1 * (body_weight - conceptus_weight) ** 0.5
            + (
                dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * 0.03
                - 0.5 * (MP_bactria_estimate / 0.68 - MP_bactria_estimate)
            )
            + 0.4 * 11.8 * dry_matter_intake_estimate / 0.67
        )
        # Growth Requirement
        # ---------------------
        # [A.Cow.B.2]-[A.Heifer.B.2]
        # Net protein requirement for growth (g)
        if average_daily_gain == 0:
            NPg = 0.0
        else:
            NPg = average_daily_gain * (268 - 29.4 * (net_energy_growth / average_daily_gain))
        # [A.Cow.B.3]-[A.Heifer.B.3]
        # Efficiency of converting metabolizable protein to net protein
        if equivalent_shrunk_body_weight <= 478:
            EffMP_NPg = (83.4 - 0.114 * equivalent_shrunk_body_weight) / 100
        else:
            EffMP_NPg = 0.28908
        # [A.Cow.B.4]-[A.Heifer.B.4]
        # Metabolizable protein requirement for growth (g)
        MPg = NPg / EffMP_NPg
        # Pregnancy Requirement
        # ---------------------
        # [A.Cow.B.5]-[A.Heifer.B.5]
        # Metabolizable protein requirement for pregnancy (g)
        if day_of_pregnancy is None:
            MPpreg = 0.0
        elif day_of_pregnancy > 190:
            MPpreg = (0.69 * day_of_pregnancy - 69.2) * (calf_birth_weight / (45 * 0.33))
        else:
            MPpreg = 0.0
        # Lactation Requirement
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.B.6]
            MPlact = milk_production * (milk_true_protein / 100) * (GeneralConstants.KG_TO_GRAMS / 0.67)
        # Total Protein Requirement  (g)
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.B.7]
            metabolizable_protein_requirement = MPm + MPg + MPpreg + MPlact
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            # [A.Heifer.B.6]
            metabolizable_protein_requirement = MPm + MPg + MPpreg
        return metabolizable_protein_requirement

    @classmethod
    def calculate_calcium_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        animal_type: AnimalType,
        average_daily_gain: float,
        milk_production: float,
    ) -> float:
        """Calculates total Calcium requirement according to NRC (2001).

        Calculates the estimated the total calcium requirement (Ca) in grams per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        average_daily_gain : float
            Average daily gain (grams per day)
        milk_production: float
            Milk yield (kg/d)

        Returns
        -------
        calcium_requirement : float
            Calcium requirement (grams per day)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 106-109. 2001.


        """
        # C: MINERAL REQUIREMENTS
        # Calcium and Phosphorus are the only requirements tracked currently
        # --------------------------------------------
        # Calcium Requirements
        # ----------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.C.1]
            # Calcium maintenance requirement (g)
            Ca_maint = 0.031 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [AnimalType.DRY_COW]:
            Ca_maint = 0.0154 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            # [A.Heifer.C.1]
            # Calcium maintenance requirement (g)
            Ca_maint = 0.0154 * body_weight + 0.08 * (body_weight / 100)
        # [A.Cow.C.2]-[A.Heifer.C.2]
        # Calcium growth requirement (g)
        Ca_growth = 9.83 * mature_body_weight**0.22 * body_weight ** (-0.22) * (average_daily_gain / 0.96)
        # [A.Cow.C.3]-[A.Heifer.C.3]
        # Calcium pregnancy requirement (g)
        if day_of_pregnancy is None:
            Ca_preg = 0.0
        elif day_of_pregnancy > 190:
            Ca_preg = 0.02456 * exp(
                (0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy
            ) - 0.02456 * exp((0.05581 - 0.00007 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
        else:
            Ca_preg = 0.0
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.C.4]
            # Calcium lactation requirement (g)
            Ca_lact = 1.22 * milk_production
            # [A.Cow.C.5]
            # Total calcium requirement (g)
            calcium_requirement: float = Ca_maint + Ca_growth + Ca_preg + Ca_lact
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            # [A.Heifer.C.4]
            # Total calcium requirement (g)
            calcium_requirement = Ca_maint + Ca_growth + Ca_preg
        return calcium_requirement

    @classmethod
    def calculate_phosphorus_requirement(
        cls,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        milk_production: float,
        animal_type: AnimalType,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
    ) -> float:
        """Calculates total Phosphorus requirement according to NRC (2001).

        Calculates the estimated the total phosphorus requirement (P) in grams per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        milk_production: float
            Milk yield (kg/d)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        average_daily_gain : float
            Average daily gain (grams per day)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg/d)

        Returns
        -------
        phosphorus_requirement : float
            Phosphorus requirement (grams per day)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 109-118. 2001.
        """
        P_growth: float = (1.2 + 4.635 * mature_body_weight**0.22 * body_weight ** (-0.22)) * (
            average_daily_gain / 0.96
        )
        if day_of_pregnancy is None:
            P_preg: float = 0.0
        elif day_of_pregnancy > 190:
            P_preg = 0.02743 * exp(
                (0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy
            ) - 0.02743 * exp((0.05527 - 0.000075 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
        else:
            P_preg = 0.0
        if animal_type in [AnimalType.LAC_COW]:
            P_maint: float = 1 * dry_matter_intake_estimate + 0.002 * body_weight
            P_lact: float = 0.9 * milk_production
            phosphorus_requirement: float = P_growth + P_preg + P_lact + P_maint
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            P_maint = 0.8 * dry_matter_intake_estimate + 0.002 * body_weight
            phosphorus_requirement = P_growth + P_preg + P_maint
        return phosphorus_requirement

    @classmethod
    def calculate_dry_matter_intake(
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
        """Calculates dry matter intake according to NRC (2001).

        Calculates the estimated total dry matter intake in kilograms per day

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        body_weight : float
            Body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        days_in_milk : int
            Days in milk (days)
        milk_production : float
            Milk yield (kg/d)
        milk_fat : float
            Fat contents in milk (%)
        net_energy_diet_concentration : float
            Metabolizable energy density of formulated ration
        days_born : float
            number of days since birth

        Returns
        -------
        dry_matter_intake_estimate : float
            Dry matter intake (kilograms per day)

        Notes
        -----
        The sum of dry matter intake of each feed is assumed to be less than
        dry matter intake estimation (Sum of Feed < dry_matter_intake_estimate).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 1 "Dry Matter Intake",
            pp. 4; and pp. 325, 2001 (Equations 1 and 2), and pp. 326 for heifers

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
    def calculate_activity_energy_requirements(
        cls,
        body_weight: float,
        housing: float,
        distance: float,
    ) -> float:
        """
        Calculates the net energy for activity requirement portion of the energy
        requirements for animals. This is separate because it must be calculated after
        grouping due to pen input args and cannot be used individually on an animal. The estimated energy requirements
         for activity in megacalories per day are calculated following either NRC or NASEM guidelines

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        housing : str
            Housing type (Barn or Grazing)
        distance : float
            Distance walked in meters.

        Returns
        -------
        net_energy_activity : float
            Net energy requirement for activity (mcal/day)

        Notes
        -----
        Note that both NRC and NASEM calculations use distance walked in kilometers,
            hence the unit conversion in the code itself.

        Activity requirement (net_energy_activity) is proportional to body weight and daily walking distance.
        Grazing system and hilly topography will cost additional energy.
            Grazing is not implemented yet in the current version of code.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.

        """
        distance_km = distance * GeneralConstants.M_TO_KM
        # Activity requirements
        # ---------------------
        # [A.Cow.A.4]-[A.Heifer.A.5]
        # Net energy for activity requirement caused by grazing system (Mcal)
        if housing == "Grazing":
            net_energy_activity1: float = 0.0012 * body_weight
        else:
            net_energy_activity1 = 0.0
        # [A.Cow.A.6]-[A.Heifer.A.7]
        # Total net energy for activity requirement (Mcal)
        net_energy_activity: float = distance_km * 0.00045 * body_weight + net_energy_activity1
        return net_energy_activity
