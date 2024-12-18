from abc import ABC, abstractmethod
from typing import Any

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements


class NutritionRequirementsCalculator(ABC):

    @classmethod
    @abstractmethod
    def calculate_requirements(cls, **kwargs: dict[str, Any]) -> NutritionRequirements:
        pass

    @classmethod
    @abstractmethod
    def _calculate_maintentance_energy_requirements(cls, **kwargs: dict[str, Any]) -> tuple[float, float, float]:
        pass

    @classmethod
    @abstractmethod
    def _calculate_growth_energy_requirements(cls, **kwargs: dict[str, Any]) -> tuple[float, float, float]:
        pass

    @classmethod
    @abstractmethod
    def _calculate_pregnancy_energy_requirements(cls, **kwargs: dict[str, Any]) -> float:
        pass

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

    @classmethod
    @abstractmethod
    def _calculate_protein_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def _calculate_calcium_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def _calculate_phosphorus_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def _calculate_dry_matter_intake(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def _calculate_activity_energy_requirements(cls, **kwargs: dict[str, Any]) -> float:
        pass
