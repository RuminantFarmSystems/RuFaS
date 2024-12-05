from numpy import exp


class NASEMRequirementsCalculator:

    @classmethod
    def calculate_energy_requirements(
        cls, body_weight: float, mature_body_weight: float, day_of_pregnancy: int | None, days_in_milk: int | None
    ) -> tuple[float, float, float]:
        """
        Calculates energy requirement for maintenance and two measures of uterine weight

        The estimated energy requirements for maintenance are calculated in megacalories per day,
        as well as gravid uterine weight and uterine weight in kg, according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int
            Day of pregnancy (days)
        days_in_milk : int
            Days in milk (lactation)

        Returns
        -------
        net_energy_maintenance : float
            Net energy requirement for maintenance (mcal/day).
        gravid_uterine_weight : float
            Gravid uterine weight (kg).
        uterine_weight : float
            Uterine weight (kg).

        Notes
        -----
        NASEM (2021) does not adjust energy requirements for environmental temperature as it assumes
        that confinement conditions already provide comfort temperature to the animals.
        This is something to consider and update for the grazing module
        Instead of calculating calf_birth_weight, NASEM (2021) also contains standards calf_birth_weight and
        mature_body_weight (tabulated values) for selected breeds (eg., Holstein)
        Instead of estimating conceptus_weight, gain in pregnancy tissues is estimated:
        (gravid_uterine_weight and uterine_weight).
        day_of_pregnancy (Day of pregnancy) was kept instead of DGest (Day ofgestation) as it is in NASEM (2021) book.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 29, 2021.

        """
        if day_of_pregnancy is None:
            net_energy_maintenance = 0.10 * body_weight**0.75
            gravid_uterine_weight = 0.0
            uterine_weight = 0.0
        else:
            calf_birth_weight = mature_body_weight * 0.06275
            gravid_uterine_weight = (calf_birth_weight * 1.825) * exp(
                -0.0243 - (0.0000245 * day_of_pregnancy) * (280 - day_of_pregnancy)
            )
            if days_in_milk is None:
                days_in_milk = 0
            uterine_weight = ((calf_birth_weight * 0.2288 - 0.204) * exp(-0.2 * days_in_milk)) + 0.204
            net_energy_maintenance = 0.10 * (body_weight - gravid_uterine_weight - uterine_weight) ** 0.75
        return net_energy_maintenance, gravid_uterine_weight, uterine_weight

    @classmethod
    def calculate_growth_energy_requirements(cls) -> tuple[float, float, float]:
        pass

    @classmethod
    def calculate_pregnancy_energy_requirements(cls) -> float:
        pass

    @classmethod
    def calculate_lactation_energy_requirements(cls) -> float:
        pass

    @classmethod
    def calculate_protein_requirement(cls) -> float:
        pass

    @classmethod
    def calculate_calcium_requirement(cls) -> float:
        pass

    @classmethod
    def calculate_phosphorus_requirement(cls) -> float:
        pass

    @classmethod
    def calculate_dry_matter_intake(cls) -> float:
        pass

    @classmethod
    def calculate_activity_energy_requirements(cls) -> float:
        pass
