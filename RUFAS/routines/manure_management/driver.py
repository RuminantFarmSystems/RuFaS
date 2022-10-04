from RUFAS.routines.manure_management.manure_management import ManureManagement
from RUFAS.routines.manure_management.misc.simple_animal_management import SimpleAnimalManagement
from RUFAS.weather import Weather


def daily_manure_management_routine(manure_management: ManureManagement, animal_management, weather: Weather):
    """Entry point to the manure module

    This function should coordinate the big-picture steps in the processing
    of manure data. It should call all the various functions on the
    ManureManagement object argument.

    This function will be renamed to `daily_manure_storage_routine` or
    `daily_manure_management_routine` after the wrapper function has been removed.

    """

    manure_management.update(animal_management)


