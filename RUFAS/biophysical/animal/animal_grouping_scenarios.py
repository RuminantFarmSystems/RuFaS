from enum import Enum
from typing import Dict, List

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination


class AnimalGroupingScenario(Enum):
    """
    The different scenarios for grouping animals on a farm.
    Each scenario is a dictionary of the form: { AnimalCombination: [List of animal types/subtypes] }


    """

    # TODO: Probably change the names of these scenarios to be more concise/descriptive. Add other scenarios as needed.
    #  Issue #1205

    CALF__GROWING__CLOSE_UP__LACCOW = {
        AnimalCombination.CALF: [AnimalType.CALF],
        AnimalCombination.GROWING: [AnimalType.HEIFER_I, AnimalType.HEIFER_II],
        AnimalCombination.CLOSE_UP: [AnimalType.HEIFER_III, AnimalType.DRY_COW],
        AnimalCombination.LAC_COW: [AnimalType.LAC_COW],
    }

    CALF__GROWING_AND_CLOSE_UP__LACCOW = {
        AnimalCombination.CALF: [AnimalType.CALF],
        AnimalCombination.GROWING_AND_CLOSE_UP: [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ],
        AnimalCombination.LAC_COW: [AnimalType.LAC_COW],
    }

    def __init__(self, value: Dict[AnimalCombination, List[str]]):
        """
        Initialize the AnimalGroupingScenario.

        Parameters
        ----------
        value : Dict[AnimalCombination, List[str]]
            The value of the AnimalGroupingScenario.

        """

        self._value_ = value

        self._animal_combination_by_animal_type: Dict[AnimalType, AnimalCombination] = {}
        for animal_combination, animal_types in self.value.items():
            for animal_type in animal_types:
                self._animal_combination_by_animal_type[animal_type] = animal_combination

    # Currently, we don't have subtypes for calves, heiferIs, heiferIIs, and heiferIIIs.
    def _get_calf_type(self, calf: Animal) -> AnimalType:
        """
        Get the animal subtype of the given calf.

        Parameters
        ----------
        calf : Animal
            The calf to get the animal subtype of.

        Returns
        -------
        AnimalType
            The animal subtype of the given calf.

        """

        return AnimalType.CALF

    def _get_heiferI_type(self, heiferI: Animal) -> AnimalType:
        """
        Get the animal subtype of the given heiferI.

        Parameters
        ----------
        heiferI : Animal
            The heiferI to get the animal subtype of.

        Returns
        -------
        AnimalType
            The animal subtype of the given heiferI.

        """

        return AnimalType.HEIFER_I

    def _get_heiferII_type(self, heiferII: Animal) -> AnimalType:
        """
        Get the animal subtype of the given heiferII.

        Parameters
        ----------
        heiferII : Animal
            The heiferII to get the animal subtype of.

        Returns
        -------
        AnimalType
            The animal subtype of the given heiferII.

        """

        return AnimalType.HEIFER_II

    def _get_heiferIII_type(self, heiferIII: Animal) -> AnimalType:
        """
        Get the animal subtype of the given heiferIII.

        Parameters
        ----------
        heiferIII : Animal
            The heiferIII to get the animal subtype of.

        Returns
        -------
        AnimalType
            The animal subtype of the given heiferIII.

        """

        return AnimalType.HEIFER_III

    def _get_cow_type(self, cow: Animal) -> AnimalType:
        """
        Get the animal subtype of the given cow.

        Parameters
        ----------
        cow : Animal
            The cow to get the animal subtype of.

        Returns
        -------
        AnimalType
            The animal subtype of the given cow.

        """

        cow_subtype_by_scenario = {
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW: (
                AnimalType.LAC_COW if cow.is_lactating else AnimalType.DRY_COW
            ),
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW: (
                AnimalType.LAC_COW if cow.is_lactating else AnimalType.DRY_COW
            ),
        }
        return cow_subtype_by_scenario[self]

    def get_animal_type(self, animal: Animal) -> AnimalType:
        """
        Get the animal type of the given animal.

        Parameters
        ----------
        animal : Animal
            The animal to get the animal type of.

        Returns
        -------
        AnimalType
            The animal type of the given animal.

        """

        return animal.animal_type  # type: ignore

    def find_animal_combination(self, animal: Animal) -> AnimalCombination:
        """
        Find the animal combination that the given animal belongs to.

        Parameters
        ----------
        animal : Animal
            The animal to find the animal combination for.

        Returns
        -------
        AnimalCombination
            The animal combination that the given animal belongs to.

        """

        animal_type = self.get_animal_type(animal)
        return self._animal_combination_by_animal_type[animal_type]
