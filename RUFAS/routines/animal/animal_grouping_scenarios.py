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
    Each scenario is a dictionary of the form:    {        Pen.AnimalCombination: [List of animal types]    }  
    The animal types are the names of the animal classes as strings.  
    Important: Each scenario must be both exhaustive and non-overlapping.    - Exhaustive: Each scenario must account for all animal types.    - Non-overlapping: Each animal type must be associated with one and only one animal combination.  
    """  # TODO: Come up with better names for these scenarios.
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
    # Private cache attribute
    __type_name_by_scenario = None

    def get_animal_type_name(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]):
        """
        Gets the name of the animal type that the given animal belongs to.
        Parameters        ----------        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]            The animal to get the animal type name for.
        Returns        -------        str            The name of the animal type that the given animal belongs to.
        """
        cow_type_name_by_scenario = {
            self.CALF__GROWING__CLOSE_UP__LACCOW: lambda cow: 'LacCow' if cow.is_lactating else 'DryCow',
            self.CALF__GROWING_AND_CLOSE_UP__LACCOW: lambda cow: 'LacCow' if cow.is_lactating else 'DryCow'
        }

        if type(animal) == Cow:
            return cow_type_name_by_scenario[self](animal)
        else:
            return animal.__class__.__name__

    def find_animal_combination(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]) -> Pen.AnimalCombination:
        """
        Finds the animal combination that the given animal belongs to.
        Parameters        ----------        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]            The animal to find the animal combination for.
        Returns        -------        Pen.AnimalCombination            The animal combination that the given animal belongs to.
        """
        if self.__type_name_by_scenario is None:
            self.__type_name_by_scenario = {}
            for animal_combination, animal_type_names in self.value.items():
                for animal_type_name in animal_type_names:
                    self.__type_name_by_scenario[animal_type_name] = animal_combination

        animal_type_name = self.get_animal_type_name(animal)
        if animal_type_name in self.__type_name_by_scenario:
            return self.__type_name_by_scenario[animal_type_name]

        raise ValueError(f'Animal type {animal_type_name} is not in any animal combination for scenario {self.name}.')
