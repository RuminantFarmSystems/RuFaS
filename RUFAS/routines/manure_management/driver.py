from typing import List

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure_management.manure_management import ManureManagement, ManureStorage
from RUFAS.routines.manure_management.data_models.manure import Manure
from RUFAS.routines.manure_management.data_models.simple_animal_management import SimpleAnimalManagement
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


def daily_manure_storage_routine(manure_storage: ManureStorage, animal_management: AnimalManagement):
    """Acts a wrapper function for `daily_manure_storage_routine` function.

    After the references to `ManureStorage` in `simulation_engine.py`
    and `classes.py` are fixed, this function should be removed.

    """

    daily_manure_storage_routine_main(manure_storage.manure_management, animal_management)



def daily_manure_storage_routine_main(manure_management: ManureManagement, _animal_management: AnimalManagement):
    """Entry point to the manure module

    This function should coordinate the big-picture steps in the processing
    of manure data. It should call all the various functions on the
    ManureManagement object argument.

    This function will be renamed to `daily_manure_storage_routine` or
    `daily_manure_management_routine` after the wrapper function has been removed.

    """
    animal_management = SimpleAnimalManagement(_animal_management)
    print(animal_management)

    manure_management.reset_daily_variables()
    manure_management.update(animal_management)

    manure_management.summarize_manure_management()  # daily
    manure_management.summarize_annual_variables()  # yearly
    manure_management.summarize_total_variables()  # all time

    # Print output data
    manure_management.export_total_variables()
    print(manure_management.manure_management_output)


def compile_manure_for_all_pens(animal_management: SimpleAnimalManagement):
    """
    Combine the manure data from all the pens in an AnimalManagement object.

    Args:
        animal_management: An AnimalManagement object that stores a list
        of pens.

    Returns:
        A Manure object that sums up respective categories from all the pens.

    """

    pen_numbers = list(range(len(animal_management.all_pens)))
    return combine_manure_for_different_pens(pen_numbers, animal_management)


def combine_manure_for_different_pens(pen_numbers: List[int], animal_management: SimpleAnimalManagement):
    """
    Take a list of pen numbers and an AnimalManagement object and
    combine the manure data of those selected pens.

    Args:
        pen_numbers: a list of pen numbers, e.g. [1,2] means pen 1 and 2
        animal_management: An AnimalManagement object that stores a list
        of pens.

    Returns:
        A Manure object that sums up respective categories from
        those selected pens.

    """

    pens: List[SimplePen] = animal_management.all_pens
    total_manure = Manure()

    for i in pen_numbers:
        total_manure += pens[i].manure

    return total_manure


def daily_manure_storage_routine2(animal_management, manure_management):
    """To be removed after completing the final version `daily_manure_storage_routine`.

    """

    manure_management.reset_daily_variables0()

    compile_manure_for_all_pens(animal_management)

    for reception_pit in manure_management.reception_pits.values():
        reception_pit.update_all()

    for separator in manure_management.separators.values():
        separator.update_all()

    for treatment in manure_management.treatments:
        treatment.update_all()

    for storage in manure_management.storage.values():
        storage.update_all()

    manure_management.summarize_manure_management()
    manure_management.summarize_annual_variables()
