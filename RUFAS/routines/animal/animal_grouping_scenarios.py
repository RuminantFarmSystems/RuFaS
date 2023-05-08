from enum import Enum
from typing import Union

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.pen import Pen


class AnimalGroupingScenario(Enum):
    """  
    The different scenarios for animal grouping.  
    Each scenario is a dictionary of the form: { Pen.AnimalCombination: [List of animal type names] }
    The animal type names are the names of the animal classes as strings.

    Notes:
        Each scenario must be both exhaustive and non-overlapping.

        - Exhaustive: Each scenario must account for all animal types and subtypes present in that scenario.
        - Non-overlapping: Each animal type or subtype must be associated with one and only one animal combination.

    """
    # TODO: Probably change the names of these scenarios to be more descriptive. Add other scenarios as needed.

    CALF__GROWING__CLOSE_UP__LACCOW = {
        Pen.AnimalCombination.CALF: ['Calf'],
        Pen.AnimalCombination.GROWING: ['HeiferI', 'HeiferII'],
        Pen.AnimalCombination.CLOSE_UP: ['HeiferIII', 'DryCow'],
        Pen.AnimalCombination.LAC_COW: ['LacCow']
    }

    CALF__GROWING_AND_CLOSE_UP__LACCOW = {
        Pen.AnimalCombination.CALF: ['Calf'],
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP: ['HeiferI', 'HeiferII', 'HeiferIII', 'DryCow'],
        Pen.AnimalCombination.LAC_COW: ['LacCow']
    }

    def __init__(self, value):
        """
        Initialize the AnimalGroupingScenario.

        Parameters
        ----------
        value : Dict[Pen.AnimalCombination, List[str]]
            The value of the AnimalGroupingScenario.

        """

        self._value_ = value

        self._animal_combination_by_animal_name = {}  # key: animal type name, value: animal combination
        for animal_combination, animal_type_names in self.value.items():
            for animal_type_name in animal_type_names:
                self._animal_combination_by_animal_name[animal_type_name] = animal_combination

    # Currently, we don't have subtypes for calves, heiferIs, heiferIIs, and heiferIIIs.
    # Therefore, their names are the same as their class names.
    def _get_calf_name(self, calf: Calf) -> str:
        return 'Calf'

    def _get_heiferI_name(self, heiferI: HeiferI) -> str:
        return 'HeiferI'

    def _get_heiferII_name(self, heiferII: HeiferII) -> str:
        return 'HeiferII'

    def _get_heiferIII_name(self, heiferIII: HeiferIII) -> str:
        return 'HeiferIII'

    def _get_cow_name(self, cow: Cow) -> str:
        """
        Get the name of the subtype that the given cow belongs to.

        Here, we create subtypes of cow based on certain characteristics depending on the current grouping scenario.

        Make sure the subtype names must match those listed in the scenario dictionary above.

        Parameters
        ----------
        cow : Cow
            The cow to get the subtype name for.

        Returns
        -------
        str
            The name of the subtype that the given cow belongs to.

        """
        cow_name_by_scenario = {
            AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW: 'LacCow' if cow.is_lactating else 'DryCow',
            AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW: 'LacCow' if cow.is_lactating else 'DryCow'
        }
        return cow_name_by_scenario[self]

    def get_all_animal_names(self) -> list[str]:
        """
        Get a list of all animal names in the scenario.

        Returns
        -------
        list[str]
            A list of all animal names in the scenario.

        """

        return list(self._animal_combination_by_animal_name.keys())

    def get_animal_name(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]):
        """
        Get the name of the given animal.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            The animal to get the animal name for.

        Returns
        -------
        str
            The name of the given animal.

        """

        return {
            Calf: self._get_calf_name,
            HeiferI: self._get_heiferI_name,
            HeiferII: self._get_heiferII_name,
            HeiferIII: self._get_heiferIII_name,
            Cow: self._get_cow_name
        }[type(animal)](animal)  # type: ignore

    def find_animal_combination(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]) -> Pen.AnimalCombination:
        """
        Find the animal combination that the given animal belongs to.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            The animal to find the animal combination for.

        Returns
        -------
        Pen.AnimalCombination
            The animal combination that the given animal belongs to.

        """

        animal_name = self.get_animal_name(animal)
        return self._animal_combination_by_animal_name[animal_name]