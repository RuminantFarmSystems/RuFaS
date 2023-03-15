"""
RUFAS: Ruminant Farm Systems Model
File name: manure_management.py

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
            Sadman Chowdhury, skc86@cornell.edu
"""
import collections
import typing
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
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_classes import ManureSeparatorFactory
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import AnaerobicDigestionAndLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_factory import ManureTreatmentFactory
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.routines.manure.output_handler.manure_management_output_handler import ManureManagementOutputHandler
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit import ReceptionPit
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


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
        """Initializes a ManureManagement object by setting up the appropriate manure
        management components as specified by the data in the animal_management object.

        Parameters
        ----------
        animal_management : AnimalManagement
            A reference to the AnimalManagement object that is one of the attributes
            of the simulation engine object.
        weather : Weather
            The Weather object used to initialize State variables.
        time : Time
            The Time object used to initialize State variables.
        manure_management_config : dict
            A dictionary that contains the configuration data for
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

        # Set up the manure management components for each animal pen.
        self._configure_manure_management_components(animal_management)

    @property
    def all_data(self) -> Dict[int, List[Tuple]]:
        """Returns all the data generated daily by different manure management components during
        the whole simulation.

        Returns
        -------
        Dict[int, List[Tuple]]
            A dictionary that stores all the data generated daily by the four main
            manure management components. Its structure is as follows:
                key = id of an animal pen
                value = a list of tuples where each tuple represents a group of daily output objects.
                    More precisely, each such tuple is of length 5, consisting of a
                    pen object, a ManureHandlerDailyOutput object, a ReceptionPitDailyOutput object,
                    a ManureSeparatorDailyOutput object, a ManureTreatmentDailyOutput object,
                    and another ManureTreatmentDailyOutput object for the anaerobic digestion treatment if it is used.

        """
        return self._all_data

    def _configure_manure_management_components(self, animal_management: AnimalManagement) -> None:
        """Configures the manure management components for each animal pen.

        Each pen is associated with the following components - bedding, manure handler,
        reception pit, manure separator, and manure treatment.

        Parameters
        ----------
        animal_management : AnimalManagement
            An AnimalManagement object obtained from the animal module.

        """
        for pen in animal_management.all_pens:
            mm_pen = ManureManagementPen(pen)

            custom_bedding_config = self.manure_management_config_handler.get_custom_bedding_config(mm_pen.bedding_type)
            self.beddings[mm_pen.id] = BeddingFactory.get_instance(
                bedding_type_name=mm_pen.bedding_type,
                custom_bedding_config=custom_bedding_config  # type: ignore
            )

            custom_manure_handler_config = \
                self.manure_management_config_handler.get_custom_manure_handler_config(mm_pen.manure_handler)
            self.manure_handlers[mm_pen.id] = ManureHandlerFactory.get_instance(
                manure_handler_type_name=mm_pen.manure_handler,
                weather=self.weather,
                time=self.time,
                custom_manure_handler_config=custom_manure_handler_config,  # type: ignore
            )

            self.reception_pits[mm_pen.id] = ReceptionPit()

            if mm_pen.manure_separator.lower() == 'none':
                self.manure_separators[mm_pen.id] = None
            else:
                custom_manure_separator_config = \
                    self.manure_management_config_handler.get_custom_manure_separator_config(mm_pen.manure_separator)
                self.manure_separators[mm_pen.id] = ManureSeparatorFactory.get_instance(
                    manure_separator_type_name=mm_pen.manure_separator,
                    custom_manure_separator_config=custom_manure_separator_config  # type: ignore
                )

            custom_manure_treatment_config = \
                self.manure_management_config_handler.get_custom_manure_treatment_config(mm_pen.manure_treatment)
            self.manure_treatments[mm_pen.id] = ManureTreatmentFactory.get_instance(
                manure_treatment_type_name=mm_pen.manure_treatment,
                weather=self.weather,
                time=self.time,
                custom_manure_treatment_config=custom_manure_treatment_config  # type: ignore
            )

    def daily_update(self, animal_management: AnimalManagement) -> None:
        """Calculates daily output data for each manure management component for each animal pen.

        On the last day of the simulation, all the data generated daily by the manure management
        components will be exported to a CSV file.

        Parameters
        ----------
        animal_management : AnimalManagement
            The current state of the AnimalManagement object.

        """
        for pen in animal_management.all_pens:
            self._pen_daily_update(animal_management.simulation_day, pen)

        if self.time.is_last_day_of_simulation:
            self.manure_management_output_handler.sort_by_pen_id_and_simulation_day()
            self.manure_management_output_handler.export_to_csv()
            self.manure_management_output_handler.produce_graphics()

    def _pen_daily_update(self, simulation_day: int, pen) -> None:
        """Calculates and stores daily output for each manure management component for a given animal pen.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen
            The animal pen for which the daily output data will be calculated.

        """
        mm_pen = ManureManagementPen(pen)

        manure_handler_daily_output = self.manure_handlers[mm_pen.id].daily_update(
            pen=mm_pen,
            bedding=self.beddings[mm_pen.id],
            sim_day=simulation_day
        )

        reception_pit_daily_output = self.reception_pits[mm_pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            pen=mm_pen,
            bedding=self.beddings[mm_pen.id]
        )

        results = self._pen_daily_update_for_separator_and_treatment(
            simulation_day=simulation_day,
            pen=mm_pen,
            manure_handler_daily_output=manure_handler_daily_output,
            reception_pit_daily_output=reception_pit_daily_output
        )

        anaerobic_digestion_daily_output = results[0]
        manure_separator_daily_output = results[1]
        manure_treatment_daily_output = results[2]
        manure_treatment_accumulated_output = results[3]

        # Put all the daily outputs into a tuple
        daily_update_output = (
            mm_pen,
            manure_handler_daily_output,
            reception_pit_daily_output,
            manure_separator_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
            anaerobic_digestion_daily_output
        )

        self._all_data[mm_pen.id].append(daily_update_output)
        self.manure_management_output_handler.append_daily_update_output_for_pen(
            simulation_day=simulation_day,
            data=daily_update_output
        )

    def _pen_daily_update_for_separator_and_treatment(self, simulation_day: int,
                                                      pen: ManureManagementPen,
                                                      manure_handler_daily_output: ManureHandlerDailyOutput,
                                                      reception_pit_daily_output: ReceptionPitDailyOutput) \
            -> Tuple[
                Optional[ManureTreatmentDailyOutput], Optional[ManureSeparatorDailyOutput],
                ManureTreatmentDailyOutput, ManureTreatmentDailyOutput]:
        """Calculates daily output for the manure separator and treatment components of a pen.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : ManureManagementPen
            The current pen.
        manure_handler_daily_output : ManureHandlerDailyOutput
            The daily output of the manure handler for the current day.
        reception_pit_daily_output : ReceptionPitDailyOutput
            The daily output of the reception pit for the current day.

        """
        anaerobic_digestion_daily_output = None
        if self._is_compound_anaerobic_manure_treatment(pen.manure_treatment):
            results = self._handle_daily_update_for_compound_anaerobic_manure_treatment(
                simulation_day=simulation_day,
                pen=pen,
                manure_handler_daily_output=manure_handler_daily_output,
                reception_pit_daily_output=reception_pit_daily_output
            )
            anaerobic_digestion_daily_output = results[0]
            manure_separator_daily_output = results[1]
            manure_treatment_daily_output = results[2]
            manure_treatment_accumulated_output = results[3]
        else:
            results = self._handle_daily_update_for_simple_manure_treatment(
                simulation_day=simulation_day,
                pen=pen,
                manure_handler_daily_output=manure_handler_daily_output,
                reception_pit_daily_output=reception_pit_daily_output
            )
            manure_separator_daily_output = results[0]
            manure_treatment_daily_output = results[1]
            manure_treatment_accumulated_output = results[2]

        return (anaerobic_digestion_daily_output, manure_separator_daily_output,
                manure_treatment_daily_output, manure_treatment_accumulated_output)

    @classmethod
    def _is_compound_anaerobic_manure_treatment(cls, manure_treatment_name: str) -> bool:
        """Returns True if the manure treatment is a compound anaerobic manure treatment, False otherwise.

        Parameters
        ----------
        manure_treatment_name : str
            The name of the manure treatment.

        Returns
        -------
        bool
            True if the manure treatment is a compound anaerobic manure treatment, False otherwise.

        """
        manure_treatment_type = ManureTreatmentType.get_type(manure_treatment_name)
        compound_anaerobic_manure_treatment_types = [
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT,
        ]
        return manure_treatment_type in compound_anaerobic_manure_treatment_types

    def _handle_daily_update_for_compound_anaerobic_manure_treatment(self, simulation_day: int,
                                                                     pen: ManureManagementPen,
                                                                     manure_handler_daily_output:
                                                                     ManureHandlerDailyOutput,
                                                                     reception_pit_daily_output:
                                                                     ReceptionPitDailyOutput) \
            -> Tuple[
                ManureTreatmentDailyOutput, Optional[ManureSeparatorDailyOutput],
                ManureTreatmentDailyOutput, ManureTreatmentDailyOutput]:
        """Handles the daily update for a compound anaerobic manure treatment.
        
        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : ManureManagementPen
            The current pen.
        manure_handler_daily_output : ManureHandlerDailyOutput
            The daily output of the manure handler for the current day.
        reception_pit_daily_output : ReceptionPitDailyOutput
            The daily output of the reception pit for the current day.    
        
        Returns
        -------
        Tuple[ManureTreatmentDailyOutput, Optional[ManureSeparatorDailyOutput], 
                ManureTreatmentDailyOutput, ManureTreatmentDailyOutput]
            The daily output of the anaerobic digestion, 
            the daily output of the manure separator, and 
            the daily output of the anaerobic lagoon, and
            the accumulated output of the anaerobic lagoon.
        
        """
        # Currently, calling the daily_update on the treatment only returns one final output
        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day,
            manure_separator=self.manure_separators[pen.id]
        )

        # To retrieve the following three intermediate results,
        # we need to access them via instance variables of the treatment object
        anaerobic_digestion_daily_output = (
            typing.cast(AnaerobicDigestionAndLagoon, self.manure_treatments[pen.id])
            .anaerobic_digestion_daily_output)

        manure_separator_daily_output = self.manure_treatments[pen.id].manure_separator_daily_output

        manure_treatment_accumulated_output = self.manure_treatments[pen.id].accumulated_output

        return (anaerobic_digestion_daily_output, manure_separator_daily_output,
                manure_treatment_daily_output, manure_treatment_accumulated_output)

    def _handle_daily_update_for_simple_manure_treatment(self, simulation_day: int,
                                                         pen: ManureManagementPen,
                                                         manure_handler_daily_output: ManureHandlerDailyOutput,
                                                         reception_pit_daily_output: ReceptionPitDailyOutput) \
            -> Tuple[Optional[ManureSeparatorDailyOutput], ManureTreatmentDailyOutput, ManureTreatmentDailyOutput]:
        """Handles the daily update for a manure treatment that is not a compound anaerobic manure treatment.

        If the given pen does not use a manure separator, the manure separator daily output will be None.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : ManureManagementPen
            The manure management pen.
        manure_handler_daily_output : ManureHandlerDailyOutput
            The manure handler daily output for the current day.
        reception_pit_daily_output : ReceptionPitDailyOutput
            The reception pit daily output for the current day.

        Returns
        -------
        Tuple[Optional[ManureSeparatorDailyOutput], ManureTreatmentDailyOutput, ManureTreatmentDailyOutput]
            The manure separator daily output and the manure treatment daily output.

        """
        manure_separator_daily_output = self.manure_separators[pen.id].daily_update(
            manure_separator_daily_input=reception_pit_daily_output
        ) if self.manure_separators[pen.id] else None

        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=manure_separator_daily_output or reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day
        )

        manure_treatment_accumulated_output = self.manure_treatments[pen.id].accumulated_output

        return manure_separator_daily_output, manure_treatment_daily_output, manure_treatment_accumulated_output


def simulate_daily_manure_management(manure_management: ManureManagement, animal_management: AnimalManagement) -> None:
    """A wrapper function for the daily_update method of the ManureManagement class.

    There is no strict reason why this function is needed. It is simply to make the code
    in the SimulationEngine more readable. It is OK to remove this function and call the
    daily_update method directly from the SimulationEngine.

    Parameters
    ----------
    manure_management : ManureManagement
        A reference to the ManureManagement object stored in the SimulationEngine.
    animal_management : AnimalManagement
        A reference to the AnimalManagement object stored in the SimulationEngine
        so the latest data can be passed to the ManureManagement object.

    """
    manure_management.daily_update(animal_management)
