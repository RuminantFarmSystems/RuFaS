"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
            Sadman Chowdhury, skc86@cornell.edu
"""
import collections

from RUFAS.routines.manure_management.misc.simple_animal_management import SimpleAnimalManagement

from RUFAS.routines.animal.animal_management import AnimalManagement


class ManureManagement:
    """
    A class that manages different components of the whole manure processing procedure.

    Notes:
        This class should replace the `ManureStorage` class.

    """

    def __init__(self, animal_management: AnimalManagement):
        """
        Initializes a ManureManagement object.

        Args:
            animal_management: An AnimalManagement object from the animal module.

        """

        self._manure_handlers = {}
        self._reception_pits = {}
        self._manure_separators = {}
        self._treatments = {}
        self._all_data = collections.defaultdict(list)
        self._build(SimpleAnimalManagement(animal_management))

    @property
    def all_data(self):
        """
        Return all the manure data generated during the whole simulation.

        Returns:
            A dictionary that stores all the manure data.

        """

        return self._all_data

    def _build(self, simple_animal_management: SimpleAnimalManagement) -> None:
        """
        Set up all the manure components.

        Args:
            simple_animal_management: A SimpleAnimalManagement object.

        """

        # TODO: Will add the actual components in later pull requests
        for pen in simple_animal_management.all_pens:
            self._manure_handlers[pen.id] = None
            self._reception_pits[pen.id] = None
            self._manure_separators[pen.id] = None
            self._treatments[pen.id] = None

    def update(self, simple_animal_management: SimpleAnimalManagement) -> None:
        """
        Update all the components and subcomponents given new information
        from the SimpleAnimalManagement object passed in.

        Args:
            simple_animal_management: A SimpleAnimalManagement object.

        """

        # TODO: Will add the actual outputs in later pull requests
        for pen in simple_animal_management.all_pens:
            manure_handler_daily_output = None
            reception_pit_daily_output = None
            manure_separator_daily_output = None
            treatment_daily_output = None

            daily_update_data = (
                pen,
                manure_handler_daily_output,
                reception_pit_daily_output,
                manure_separator_daily_output,
                treatment_daily_output
            )
            self._all_data[pen.id].append(daily_update_data)


def daily_manure_management_routine(manure_management: ManureManagement, animal_management: AnimalManagement) -> None:
    """
    Entry point to the manure management module.

    Args:
        manure_management: A ManureManagement object.
        animal_management: An AnimalManagement object from the animal module.

    """

    sam = SimpleAnimalManagement(animal_management)
    manure_management.update(sam)
