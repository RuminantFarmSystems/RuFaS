from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class NutritionRequirementsCalculator:
    """
    Holds logic for calculating animal requirements that is shared by both the NASEM and NRC methodologies.
    """

    @classmethod
    def _calculate_lactation_energy_requirements(
        cls,
        animal_type: AnimalType,
        milk_fat: float,
        milk_true_protein: float,
        milk_lactose: float,
        milk_production: float,
    ) -> float:
        """
        Calculates energy requirement for lactation.

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_fat : float
            Fat content of milk (%)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_lactose : float
            Lactose contents in milk (%)
        milk_production: float
            Daily milk yield (kg).

        Notes
        ------
        [AN.NRC.27]
        [AN.NRC.28]
        [AN.NSM.21]
        [AN.NSM.22]

        Returns
        -------
        net_energy_lactation : float
            Net energy requirement for lactation (Mcal)

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition." National Academic Press, Chapter 3 "Energy", pp. 30, 2021.
        .. [2] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 2 "Energy", pp. 19, 2001.

        """
        if animal_type in [AnimalType.LAC_COW]:
            milk_energy_Mcal_per_kg = 0.0929 * milk_fat + (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
            net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
        else:
            net_energy_lactation = 0.0
        return net_energy_lactation
