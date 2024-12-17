from abc import ABC, abstractmethod
from typing import Any

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements


class NutritionRequirementsCalculator(ABC):

    @classmethod
    @abstractmethod
    def calculate_requirements(cls, **kwargs: dict[str, Any]) -> NutritionRequirements:
        pass

    @classmethod
    @abstractmethod
    def calculate_maintentance_energy_requirements(cls, **kwargs: dict[str, Any]) -> tuple[float, float, float]:
        pass

    @classmethod
    @abstractmethod
    def calculate_growth_energy_requirements(cls, **kwargs: dict[str, Any]) -> tuple[float, float, float]:
        pass

    @classmethod
    @abstractmethod
    def calculate_pregnancy_energy_requirements(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_lactation_energy_requirements(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_protein_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_calcium_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_phosphorus_requirement(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_dry_matter_intake(cls, **kwargs: dict[str, Any]) -> float:
        pass

    @classmethod
    @abstractmethod
    def calculate_activity_energy_requirements(cls, **kwargs: dict[str, Any]) -> float:
        pass
