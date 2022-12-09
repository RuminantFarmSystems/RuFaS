"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
            Sadman Chowdhury, skc86@cornell.edu
"""
import collections
from typing import Dict, List, Tuple

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen

class ManureManagement:
    """
    A class that sets up and manages different manure management components including manure handlers,
    reception pits, manure separators, and manure storage treatments. When the simulation engine performs
    a daily simulation, it invokes the update method on an instance of this class, thereby generating
    and storing daily output data.

    Notes:
        This class will replace the `ManureStorage` class.

    Attributes:
            manure_handlers: a dictionary that maps an animal pen's id to a ManureHandler object.
            reception_pits: a dictionary that maps an animal pen's id to a ReceptionPit object.
            manure_separators: a dictionary that maps an animal pen's id to a ManureSeparator object.
            manure_treatments: a dictionary that maps an animal pen's id to a Treatment object.

    """

    def __init__(self, animal_management: AnimalManagement):
        """
        Initializes a ManureManagement object by setting up the appropriate manure
        management components as specified by the data in the animal_management object.

        Args:
            animal_management: A reference to the AnimalManagement object that is one of the attributes
                of the simulation engine object.

        """

        self.manure_handlers = {}
        self.reception_pits = {}
        self.manure_separators = {}
        self.manure_treatments = {}
        self._all_data = collections.defaultdict(list)
        self._setup_manure_management_components(animal_management)

    @property
    def all_data(self) -> Dict[int, List[Tuple]]:
        """
        Returns all the data generated daily by different manure management components during
        the whole simulation.

        Returns:
            A dictionary that stores all the data generated daily by the four main
            manure management components. Its structure is as follows:
                key = id of an animal pen
                value = a list of tuples where each tuple represents a group of daily output objects.
                    More precisely, each such tuple is of length 5, consisting of a
                    pen object, a ManureHandlerOutput object, a ReceptionPitOutput object,
                    a ManureSeparatorOutput object, and a ManureTreatment object.

        """

        return self._all_data

    def _setup_manure_management_components(self, animal_management: AnimalManagement) -> None:
        """
        Sets up the chain of manure management components for each animal pen as follows:
            Each pen has one of each of the following components - manure handler,
            reception pit, manure separator, and manure storage treatment.
            These four components, in that order, form a chain such that each downstream
            component stores a reference to its immediate predecessor. For example,
            any manure separator object will have a reference to its associated reception pit
            object. This design also implies that any upstream component will not be aware of its
            immediate successor, e.g., a manure handler object has no knowledge of the existence
            of the reception pit object associated with it.

        This function will only be called once during the initialization of the simulation engine's
        State instance variable.

        Args:
            animal_management: An AnimalManagement object obtained from the animal module.

        """

        # TODO: Will add the actual components in later pull requests
        for pen in animal_management.all_pens:
            mm_pen = ManureManagementPen(pen)
            self.manure_handlers[mm_pen.id] = None
            self.reception_pits[mm_pen.id] = None
            self.manure_separators[mm_pen.id] = None
            self.manure_treatments[mm_pen.id] = None

    def update(self, animal_management: AnimalManagement) -> None:
        """
        Updates this ManureManagement object by calling the update function on
        each manure management component for each animal pen.

        Args:
            animal_management: A SimpleAnimalManagement object that has been created
                from the simulation engine's AnimalManagement object.

        """

        # TODO: Will add the actual outputs in later pull requests
        for pen in animal_management.all_pens:
            mm_pen = ManureManagementPen(pen)
            manure_handler_daily_output = None
            reception_pit_daily_output = None
            manure_separator_daily_output = None
            treatment_daily_output = None

            daily_update_data = (
                mm_pen,
                manure_handler_daily_output,
                reception_pit_daily_output,
                manure_separator_daily_output,
                treatment_daily_output
            )
            self._all_data[pen.id].append(daily_update_data)


def simulate_daily_manure_management(manure_management: ManureManagement, animal_management: AnimalManagement) -> None:
    """
    Entry point to the manure management module. This function is called every time
    the SimulationEngine needs to perform daily simulation. Internally, the new manure data
    from the animal_management object will be extracted and passed through the following
    components sequentially - manure handlers, reception pits, manure separators,
    manure storage treatments - to generate daily output data. This data is then stored
    in the all_data attribute of the manure_management object.

    Args:
        manure_management: A reference to the ManureManagement object stored in the SimulationEngine.
            The internal states of this object will be updated based on the data extracted from the
            animal_management object.
        animal_management: A reference to the AnimalManagement object stored in the SimulationEngine.
            This object is treated as a read-only object so no changes are made to it.

    """

    manure_management.update(animal_management)