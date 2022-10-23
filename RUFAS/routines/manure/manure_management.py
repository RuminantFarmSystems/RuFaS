"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Description:


Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
            Sadman Chowdhury, skc86@cornell.edu
"""
import collections
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.beddings.bedding_classes import BeddingFactory
from RUFAS.routines.manure.input_handler.manure_management_config_handler import ManureManagementConfigHandler
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import BaseManureHandler
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import ManureHandlerFactory
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorFactory
from RUFAS.routines.manure.manure_treatments.manure_treatment_classes import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_classes import ManureTreatmentFactory
from RUFAS.routines.manure.output_handler.manure_management_output_handler import ManureManagementOutputHandler
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit import ReceptionPit


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

    def __init__(self,
                 animal_management: AnimalManagement,
                 weather,
                 time,
                 manure_management_config):
        """
        Initializes a ManureManagement object by setting up the appropriate manure
        management components as specified by the data in the animal_management object.

        Args:
            animal_management: A reference to the AnimalManagement object that is one of the attributes
                of the simulation engine object.
            weather: The Weather object used to initialize State variables.
            time: The Time object used to initialize State variables.
            manure_management_config: A dictionary that contains the configuration data for
                different manure management scenarios.

        """
        self.beddings: Dict[int, BaseBedding] = {}
        self.manure_handlers: Dict[int, BaseManureHandler] = {}
        self.reception_pits: Dict[int, ReceptionPit] = {}
        self.manure_separators: Dict[int, Optional[BaseManureSeparator]] = {}
        self.manure_treatments: Dict[int, BaseManureTreatment] = {}
        self.weather = weather
        self.time = time
        self.manure_management_config_handler = ManureManagementConfigHandler(manure_management_config)
        self.manure_management_output_handler = ManureManagementOutputHandler()
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

        for pen in animal_management.all_pens:
            mm_pen = ManureManagementPen(pen)

            custom_bedding_config = self.manure_management_config_handler.get_custom_bedding_config(mm_pen.bedding_type)
            self.beddings[pen.id] = BeddingFactory.get_instance(
                    bedding_type_name=mm_pen.bedding_type,
                    custom_bedding_config=custom_bedding_config
            )

            custom_manure_handler_config = \
                self.manure_management_config_handler.get_custom_manure_handler_config(mm_pen.manure_handler)
            self.manure_handlers[mm_pen.id] = ManureHandlerFactory.get_instance(
                    manure_handler_type_name=mm_pen.manure_handler,
                    custom_manure_handler_config=custom_manure_handler_config
            )

            self.reception_pits[mm_pen.id] = ReceptionPit()

            if mm_pen.manure_separator == 'none':
                self.manure_separators[mm_pen.id] = None
            else:
                custom_manure_separator_config = \
                    self.manure_management_config_handler.get_custom_manure_separator_config(mm_pen.manure_separator)
                self.manure_separators[mm_pen.id] = ManureSeparatorFactory.get_instance(
                        manure_separator_type_name=mm_pen.manure_separator,
                        custom_manure_separator_config=custom_manure_separator_config
                )

            custom_manure_treatment_config = \
                self.manure_management_config_handler.get_custom_manure_treatment_config(mm_pen.manure_treatment)
            self.manure_treatments[mm_pen.id] = ManureTreatmentFactory.get_instance(
                    manure_treatment_type_name=mm_pen.manure_treatment,
                    weather=self.weather,
                    time=self.time,
                    custom_manure_treatment_config=custom_manure_treatment_config
            )

    def update(self, animal_management: AnimalManagement) -> None:
        """
        Updates this ManureManagement object by calling the update function on
        each manure management component for each animal pen.

        Args:
            animal_management: A SimpleAnimalManagement object that has been created
                from the simulation engine's AnimalManagement object.

        """
        for pen in animal_management.all_pens:
            mm_pen = ManureManagementPen(pen)

            manure_handler_daily_output = \
                self.manure_handlers[mm_pen.id].daily_update(
                        pen=mm_pen,
                        bedding=self.beddings[mm_pen.id],
                        sim_day=animal_management.simulation_day
                )

            reception_pit_daily_output = \
                self.reception_pits[mm_pen.id].daily_update(
                        manure_handler_daily_output=manure_handler_daily_output,
                        pen=mm_pen,
                        bedding=self.beddings[mm_pen.id]
                )

            if self.manure_separators[mm_pen.id] is None:
                manure_separator_daily_output = None
            else:
                manure_separator_daily_output = \
                    self.manure_separators[mm_pen.id].daily_update(
                            reception_pit_daily_output=reception_pit_daily_output
                    )

            treatment_daily_output = \
                self.manure_treatments[mm_pen.id].daily_update(
                        reception_pit_daily_output=reception_pit_daily_output,
                        manure_separator_daily_output=manure_separator_daily_output,
                        sim_day=animal_management.simulation_day
                )

            daily_update_data = (
                mm_pen,
                manure_handler_daily_output,
                reception_pit_daily_output,
                manure_separator_daily_output,
                treatment_daily_output
            )
            self._all_data[pen.id].append(daily_update_data)

        self.manure_management_output_handler.append_last_output(self._all_data, animal_management.simulation_day)
        self.manure_management_output_handler.sort_by_pen_id_and_sim_day()
        self.manure_management_output_handler.export_all_data_to_csv()


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
