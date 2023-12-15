from __future__ import annotations

import typing
import random
from typing import Dict
from typing import Optional
from typing import Tuple

from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.manure.IO_helpers.manure_manager_config_handler import (
    ManureManagerConfigHandler,
)
from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import (
    ManureModuleOutputManagerHelper,
)
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.beddings.bedding_classes import BeddingFactory
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    BaseManureHandler,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import (
    ManureHandlerFactory,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import (
    ManureHandlerDailyOutput,
)
from RUFAS.routines.manure.manure_nutrients.manure_nutrient_manager import (
    ManureNutrientManager,
)
from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import (
    NutrientRequestResults,
)
from RUFAS.routines.manure.manure_separators.manure_separator_classes import (
    BaseManureSeparator,
)
from RUFAS.routines.manure.manure_separators.manure_separator_classes import (
    ManureSeparatorFactory,
)
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import (
    ManureSeparatorDailyOutput,
)
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import (
    AnaerobicDigestionAndLagoon,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_factory import (
    ManureTreatmentFactory,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.reception_pits.reception_pit import ReceptionPit
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import (
    ReceptionPitDailyOutput,
)


class ManureManager:
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

    def __init__(
            self, animal_manager: AnimalManager, weather, time, manure_manager_config
    ):
        """Initializes a ManureManager object by setting up the appropriate manure
        manager components as specified by the data in the animal_manager object.

        Parameters
        ----------
        animal_manager : AnimalManager
            A reference to the AnimalManager object that is one of the attributes
            of the simulation engine object.
        weather : Weather
            The Weather object used to initialize State variables.
        time : Time
            The Time object used to initialize State variables.
        manure_manager_config : dict
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
        self.manure_manager_config_handler = ManureManagerConfigHandler(
            manure_manager_config
        )
        self._daily_output_per_pen = []
        self._manure_nutrient_manager = ManureNutrientManager()
        self._manure_nutrient_manager_by_manure_type = {
            ManureType.SLURRY: ManureNutrientManager(),
            ManureType.LIQUID: ManureNutrientManager(),
            ManureType.SOLID: ManureNutrientManager(),
        }

        self._configure_manure_manager_components(animal_manager)

    @property
    def data(self) -> list[dict]:
        """
        Get all the daily output data for each animal pen.

        Returns
        -------
        list[dict]
            A list of dictionaries containing the daily output data for each animal pen.
            The keys and their associated data types of each dictionary are as follows:
            {
                'simulation_day': int,
                'pen': ManureManagerPen,
                'animal_manure_excretions': PenManure,
                'manure_handler_daily_output': ManureHandlerDailyOutput,
                'reception_pit_daily_output': ReceptionPitDailyOutput,
                'manure_separator_daily_output': ManureSeparatorDailyOutput,
                'manure_treatment_daily_output': ManureTreatmentDailyOutput,
                'manure_treatment_accumulated_output': ManureTreatmentDailyOutput,
                'anaerobic_digestion_daily_output': ManureTreatmentDailyOutput
            }

        """
        return self._daily_output_per_pen

    def _configure_manure_manager_components(
            self, animal_manager: AnimalManager
    ) -> None:
        """Configures the manure manager components for each animal pen.

        Each pen is associated with the following components - bedding, manure handler,
        reception pit, manure separator, and manure treatment.

        Parameters
        ----------
        animal_manager : AnimalManager
            An AnimalManager object obtained from the animal module.

        """
        for pen in animal_manager.all_pens:
            mm_pen = ManureManagerPen(pen)

            custom_bedding_config = (
                self.manure_manager_config_handler.get_custom_bedding_config(
                    mm_pen.bedding_type
                )
            )
            self.beddings[mm_pen.id] = BeddingFactory.get_instance(
                bedding_type_name=mm_pen.bedding_type,
                custom_bedding_config=custom_bedding_config,  # type: ignore
            )

            custom_manure_handler_config = (
                self.manure_manager_config_handler.get_custom_manure_handler_config(
                    mm_pen.manure_handler
                )
            )
            self.manure_handlers[mm_pen.id] = ManureHandlerFactory.get_instance(
                manure_handler_type_name=mm_pen.manure_handler,
                weather=self.weather,
                time=self.time,
                custom_manure_handler_config=custom_manure_handler_config,  # type: ignore
            )

            self.reception_pits[mm_pen.id] = ReceptionPit()

            if mm_pen.manure_separator.lower() == "none":
                self.manure_separators[mm_pen.id] = None
            else:
                custom_manure_separator_config = self.manure_manager_config_handler.get_custom_manure_separator_config(
                    mm_pen.manure_separator
                )
                self.manure_separators[mm_pen.id] = ManureSeparatorFactory.get_instance(
                    manure_separator_type_name=mm_pen.manure_separator,
                    custom_manure_separator_config=custom_manure_separator_config,  # type: ignore
                )

            custom_manure_treatment_config = (
                self.manure_manager_config_handler.get_custom_manure_treatment_config(
                    mm_pen.manure_treatment
                )
            )
            self.manure_treatments[mm_pen.id] = ManureTreatmentFactory.get_instance(
                manure_treatment_type_name=mm_pen.manure_treatment,
                weather=self.weather,
                time=self.time,
                custom_manure_treatment_config=custom_manure_treatment_config,  # type: ignore
            )

    def daily_update(self, animal_manager: AnimalManager) -> None:
        """Calculates daily output data for each manure manager component for each animal pen.

        On the last day of the simulation, all the data generated daily by the manure manager
        components will be exported to a CSV file.

        Parameters
        ----------
        animal_manager : AnimalManager
            The current state of the AnimalManager object.

        """
        for pen in animal_manager.all_pens:
            self._pen_daily_update(animal_manager.simulation_day, pen)

        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager.values,
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "ManureNutrients",
            }
        )

        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager_by_manure_type[ManureType.SLURRY].values,
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "SlurryManureNutrients",
            }
        )

        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager_by_manure_type[ManureType.LIQUID].values,
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "LiquidManureNutrients",
            }
        )

        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager_by_manure_type[ManureType.SOLID].values,
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "SolidManureNutrients",
            }
        )

        # Simulate random nutrient requests
        random_integer = random.randint(1, 30)
        if random_integer % 3 == 0:
            request = NutrientRequest(
                nitrogen=(self._manure_nutrient_manager_by_manure_type[ManureType.LIQUID].values.nitrogen *
                          random.random()),
                phosphorus=(self._manure_nutrient_manager_by_manure_type[ManureType.LIQUID].values.phosphorus *
                            random.random()),
            )
            request_results = self.request_nutrients_by_manure_type(ManureType.LIQUID, request)
            # self._manure_nutrient_manager._remove_nutrients(request_results)
            # self.request_nutrients(request)
        elif random_integer % 5 == 0:
            request = NutrientRequest(
                nitrogen=(self._manure_nutrient_manager_by_manure_type[ManureType.SLURRY].values.nitrogen *
                          random.random()),
                phosphorus=(self._manure_nutrient_manager_by_manure_type[ManureType.SLURRY].values.phosphorus *
                            random.random()),
            )
            request_results = self.request_nutrients_by_manure_type(ManureType.SLURRY, request)
            # self._manure_nutrient_manager._remove_nutrients(request_results)
            # self.request_nutrients(request)
        # elif random_integer % 7 == 0:
        #     request = NutrientRequest(
        #         nitrogen=(self._manure_nutrient_manager_by_manure_type[ManureType.SOLID].values.nitrogen *
        #                   random.random()),
        #         phosphorus=(self._manure_nutrient_manager_by_manure_type[ManureType.SOLID].values.phosphorus *
        #                     random.random()),
        #     )
        #     request_results = self.request_nutrients_by_manure_type(ManureType.SOLID, request)
        #     # self._manure_nutrient_manager._remove_nutrients(request_results)
        #     # self.request_nutrients(request)

        # The difficulty is if we support both a general request and a specific request,
        # If we make a general request, we don't know yet how to decide which manure pool to get the
        # nutrients from.

    @staticmethod
    def _get_manure_type(treatment_type: ManureTreatmentType) -> ManureType:
        """
        Look up the type of manure produced by a given manure treatment system.

        This method is used to map the type of treatment system to the type of manure it produces.
        This mapping is based on a predefined relationship between the treatment types and manure types.

        Parameters
        ----------
        treatment_type : ManureTreatmentType
            The type of manure treatment system.

        Returns
        -------
        ManureType
            The type of manure produced by the given manure treatment system. The possible values are
            specified in the definition of the enum class :class:`ManureType`.

        """
        manure_type_by_treatment_type = {
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: ManureType.SLURRY,
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: ManureType.SLURRY,
            ManureTreatmentType.ANAEROBIC_LAGOON: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SPLIT: ManureType.LIQUID,
            ManureTreatmentType.COMPOST_BEDDED_PACK_BARN: ManureType.SOLID,
            ManureTreatmentType.OPEN_LOTS: ManureType.SOLID,
        }
        return manure_type_by_treatment_type[treatment_type]

    @staticmethod
    def _get_manure_density_by_type(manure_type: ManureType) -> float:
        """
        Look up the density of manure based on the given type. The specific density values are
        specified in the class :class:`ManureConstants`.

        Parameters
        ----------
        manure_type : ManureType
            The type of manure.

        Returns
        -------
        float
            The density of manure based on the given type.
        """

        manure_density_by_manure_type = {
            ManureType.SLURRY: ManureConstants.SLURRY_MANURE_DENSITY,
            ManureType.LIQUID: ManureConstants.LIQUID_MANURE_DENSITY,
            ManureType.SOLID: ManureConstants.SOLID_MANURE_DENSITY,
        }
        return manure_density_by_manure_type[manure_type]

    def _add_manure_nutrients(
            self,
            pen: ManureManagerPen,
            manure_treatment_daily_output: ManureTreatmentDailyOutput,
    ) -> None:
        """
        Add the nutrients in the manure produced by a given pen to the manure nutrient manager.

        Parameters
        ----------
        pen : ManureManagerPen
            A pen object to look up the type of its manure treatment system.
        manure_treatment_daily_output : ManureTreatmentDailyOutput
            The daily output data of the manure treatment system.

        Returns
        -------
        None
        """

        nitrogen = max(
            manure_treatment_daily_output.liquid_manure_nitrogen
            + manure_treatment_daily_output.sludge_manure_nitrogen
            + manure_treatment_daily_output.solid_manure_nitrogen,
            0.0
        )

        phosphorus = max(
            manure_treatment_daily_output.liquid_manure_phosphorus
            + manure_treatment_daily_output.sludge_manure_phosphorus
            + manure_treatment_daily_output.solid_manure_phosphorus,
            0.0
        )

        potassium = max(
            manure_treatment_daily_output.liquid_manure_potassium
            + manure_treatment_daily_output.sludge_manure_potassium
            + manure_treatment_daily_output.solid_manure_potassium,
            0.0,
        )

        dry_matter = max(
            manure_treatment_daily_output.liquid_manure_total_solids
            + manure_treatment_daily_output.sludge_manure_total_solids
            + manure_treatment_daily_output.solid_manure_total_solids,
            0.0,
        )

        total_manure_mass = max(
            manure_treatment_daily_output.liquid_manure_daily_volume
            * self._get_manure_density_by_type(ManureType.LIQUID)
            + manure_treatment_daily_output.sludge_manure_daily_volume
            * self._get_manure_density_by_type(ManureType.SLURRY)
            + manure_treatment_daily_output.solid_manure_daily_mass,
            0.0
        )

        self._manure_nutrient_manager.add_nutrients(
            ManureNutrients(
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                dry_matter=dry_matter,
                total_manure_mass=total_manure_mass,
            )
        )

        # TODO: Check whether we should look up the manure type from the current manure management system
        # and then add the nutrients to the corresponding manure nutrient manager.
        # For example, a slurry storage can produce both liquid and sludge manure.

        self._manure_nutrient_manager_by_manure_type[ManureType.SLURRY].add_nutrients(
            ManureNutrients(
                nitrogen=manure_treatment_daily_output.sludge_manure_nitrogen,
                phosphorus=manure_treatment_daily_output.sludge_manure_phosphorus,
                potassium=manure_treatment_daily_output.sludge_manure_potassium,
                dry_matter=manure_treatment_daily_output.sludge_manure_total_solids,
                total_manure_mass=(manure_treatment_daily_output.sludge_manure_daily_volume
                                   * self._get_manure_density_by_type(ManureType.SLURRY)),
            )
        )

        self._manure_nutrient_manager_by_manure_type[ManureType.LIQUID].add_nutrients(
            ManureNutrients(
                nitrogen=manure_treatment_daily_output.liquid_manure_nitrogen,
                phosphorus=manure_treatment_daily_output.liquid_manure_phosphorus,
                potassium=manure_treatment_daily_output.liquid_manure_potassium,
                dry_matter=manure_treatment_daily_output.liquid_manure_total_solids,
                total_manure_mass=(manure_treatment_daily_output.liquid_manure_daily_volume
                                   * self._get_manure_density_by_type(ManureType.LIQUID)),
            )
        )

        self._manure_nutrient_manager_by_manure_type[ManureType.SOLID].add_nutrients(
            ManureNutrients(
                nitrogen=manure_treatment_daily_output.solid_manure_nitrogen,
                phosphorus=manure_treatment_daily_output.solid_manure_phosphorus,
                potassium=manure_treatment_daily_output.solid_manure_potassium,
                dry_matter=manure_treatment_daily_output.solid_manure_total_solids,
                total_manure_mass=manure_treatment_daily_output.solid_manure_daily_mass,
            )
        )

# remove
    def request_nutrients(self, request: NutrientRequest) -> NutrientRequestResults:
        """
        Handle the request for specific nutrients from the crop and soil module.
        This method evaluates the nutrient request made by considering both nitrogen and phosphorus
        quantities desired. It calculates the projected manure mass that would satisfy the request
        and checks against the nutrients available in the manager.

        If the request can be fulfilled either partially or wholly, the corresponding amount of nutrients
        is subtracted from the manager's internal bookkeeping. The method then returns the results of
        the nutrient request, which detail the amounts of nutrients that can be provided to fulfill the request.
        If the request cannot be fulfilled at all, the method will return None.

        Notes
        -----
        This is a wrapper method that calls the request_nutrients method of the manure nutrient manager.

        Parameters
        ----------
        request : NutrientRequest
            The specific nutrient request, including quantities of nitrogen and phosphorus.
        Returns
        -------
        NutrientRequestResults | None
            The results of the nutrient request, detailed in a `NutrientRequestResults` object, which includes
            the amount of nitrogen, phosphorus, total manure mass, dry matter, and others that
            can be provided to fulfill the request.
            Returns None if the request cannot be fulfilled.
        """

        return self._manure_nutrient_manager.request_nutrients(request)

    def request_nutrients_by_manure_type(self,
                                         manure_type: ManureType,
                                         request: NutrientRequest,
                                         ) -> NutrientRequestResults:
        """
        Handle the request for specific nutrients from the crop and soil module by manure type.

        Parameters
        ----------
        manure_type : ManureType
            The type of manure. The possible values are specified in the definition of
            the enum class :class:`ManureType`.
        request : NutrientRequest
            The specific nutrient request, including quantities of nitrogen and phosphorus.

        Returns
        -------
        NutrientRequestResults | None
            The results of the nutrient request, detailed in a `NutrientRequestResults` object, which includes
            the amount of nitrogen, phosphorus, total manure mass, dry matter, and others that
            can be provided to fulfill the request.
            Returns None if the request cannot be fulfilled.

        Raises
        ------
        KeyError
            If the given manure type is invalid.
        """

        if manure_type not in self._manure_nutrient_manager_by_manure_type:
            raise KeyError(f"Invalid manure type: {manure_type}")

        return self._manure_nutrient_manager_by_manure_type[manure_type].request_nutrients(request)

    def _pen_daily_update(self, simulation_day: int, pen) -> None:
        """
        Calculate daily output data for each manure manager component for a given animal pen.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen
            The animal pen for which the daily output data will be calculated.

        Returns
        -------
        None

        """

        mm_pen = ManureManagerPen(pen)
        class_and_function_info_maps = {
            "class": self.__class__.__name__,
            "function": self._pen_daily_update.__name__,
        }
        excluded_fields = ["pen_id", "simulation_day"]

        pen_manure_prefix = {
            "prefix": "AnimalModuleInputToManureModule_Pen_" + str(mm_pen.id)
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            mm_pen.manure,
            class_and_function_info_maps | pen_manure_prefix,
            excluded_fields,
        )

        manure_handler_daily_output = self.manure_handlers[mm_pen.id].daily_update(
            pen=mm_pen, bedding=self.beddings[mm_pen.id], sim_day=simulation_day
        )

        manure_handler_daily_output_prefix = {
            "prefix": manure_handler_daily_output.__class__.__name__ + "_Pen_" + str(mm_pen.id)
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            manure_handler_daily_output,
            class_and_function_info_maps | manure_handler_daily_output_prefix,
            excluded_fields,
        )

        reception_pit_daily_output = self.reception_pits[mm_pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            pen=mm_pen,
            bedding=self.beddings[mm_pen.id],
        )

        reception_pit_daily_output_prefix = {
            "prefix": reception_pit_daily_output.__class__.__name__ + "_Pen_" + str(mm_pen.id)
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            reception_pit_daily_output,
            class_and_function_info_maps | reception_pit_daily_output_prefix,
            excluded_fields,
        )

        results = self._pen_daily_update_for_separator_and_treatment(
            simulation_day=simulation_day,
            pen=mm_pen,
            manure_handler_daily_output=manure_handler_daily_output,
            reception_pit_daily_output=reception_pit_daily_output,
        )

        anaerobic_digestion_daily_output = results[0]
        manure_separator_daily_output = results[1]
        manure_treatment_daily_output = results[2]
        manure_treatment_accumulated_output = results[3]

        if anaerobic_digestion_daily_output:
            anaerobic_digestion_daily_output_prefix = {
                "prefix": "AnaerobicDigestion_"
                          + anaerobic_digestion_daily_output.__class__.__name__
                          + "_Pen_"
                          + str(mm_pen.id)
            }
            ManureModuleOutputManagerHelper.add_dataclass_object(
                anaerobic_digestion_daily_output,
                class_and_function_info_maps | anaerobic_digestion_daily_output_prefix,
                excluded_fields,
            )
        if manure_separator_daily_output:
            manure_separator_daily_output_prefix = {
                "prefix": manure_separator_daily_output.__class__.__name__ + "_Pen_" + str(mm_pen.id)
            }
            ManureModuleOutputManagerHelper.add_dataclass_object(
                manure_separator_daily_output,
                class_and_function_info_maps | manure_separator_daily_output_prefix,
                excluded_fields,
            )

        manure_treatment_daily_output_prefix = {
            "prefix": manure_treatment_daily_output.__class__.__name__ + "_Pen_" + str(mm_pen.id)
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            manure_treatment_daily_output,
            class_and_function_info_maps | manure_treatment_daily_output_prefix,
            excluded_fields,
        )

        accumulated_manure_treatment_output_prefix = {
            "prefix": "Accumulated_"
                      + manure_treatment_daily_output.__class__.__name__
                      + "_Pen_"
                      + str(mm_pen.id)
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            manure_treatment_accumulated_output,
            class_and_function_info_maps | accumulated_manure_treatment_output_prefix,
            excluded_fields,
        )

        daily_output_data = {
            "simulation_day": simulation_day,
            "pen": mm_pen,
            "animal_manure_excretions": mm_pen.manure,
            "manure_handler_daily_output": manure_handler_daily_output,
            "reception_pit_daily_output": reception_pit_daily_output,
            "manure_separator_daily_output": manure_separator_daily_output,
            "manure_treatment_daily_output": manure_treatment_daily_output,
            "manure_treatment_accumulated_output": manure_treatment_accumulated_output,
            "anaerobic_digestion_daily_output": anaerobic_digestion_daily_output,
        }

        self._add_manure_nutrients(mm_pen, manure_treatment_daily_output)

        self._daily_output_per_pen.append(daily_output_data)

    def _pen_daily_update_for_separator_and_treatment(
            self,
            simulation_day: int,
            pen: ManureManagerPen,
            manure_handler_daily_output: ManureHandlerDailyOutput,
            reception_pit_daily_output: ReceptionPitDailyOutput,
    ) -> Tuple[
        Optional[ManureTreatmentDailyOutput],
        Optional[ManureSeparatorDailyOutput],
        ManureTreatmentDailyOutput,
        ManureTreatmentDailyOutput,
    ]:
        """Calculates daily output for the manure separator and treatment components of a pen.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : ManureManagerPen
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
                reception_pit_daily_output=reception_pit_daily_output,
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
                reception_pit_daily_output=reception_pit_daily_output,
            )
            manure_separator_daily_output = results[0]  # type: ignore
            manure_treatment_daily_output = results[1]  # type: ignore
            manure_treatment_accumulated_output = results[2]  # type: ignore

        return (
            anaerobic_digestion_daily_output,
            manure_separator_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
        )

    @classmethod
    def _is_compound_anaerobic_manure_treatment(
            cls, manure_treatment_name: str
    ) -> bool:
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

    def _handle_daily_update_for_compound_anaerobic_manure_treatment(
            self,
            simulation_day: int,
            pen: ManureManagerPen,
            manure_handler_daily_output: ManureHandlerDailyOutput,
            reception_pit_daily_output: ReceptionPitDailyOutput,
    ) -> Tuple[
        ManureTreatmentDailyOutput,
        Optional[ManureSeparatorDailyOutput],
        ManureTreatmentDailyOutput,
        ManureTreatmentDailyOutput,
    ]:
        """Handles the daily update for a compound anaerobic manure treatment.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : ManureManagerPen
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
            the daily output of the manure separator,
            the daily output of the anaerobic lagoon, and
            the accumulated output of the anaerobic lagoon.

        """
        # Currently, calling the daily_update on the treatment only returns one final output
        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day,
            manure_separator=self.manure_separators[pen.id],
        )

        # To retrieve the following three intermediate results,
        # we need to access them via instance variables of the treatment object
        anaerobic_digestion_daily_output = typing.cast(
            AnaerobicDigestionAndLagoon, self.manure_treatments[pen.id]
        ).anaerobic_digestion_daily_output

        manure_separator_daily_output = self.manure_treatments[
            pen.id
        ].manure_separator_daily_output

        manure_treatment_accumulated_output = self.manure_treatments[
            pen.id
        ].accumulated_output

        return (
            anaerobic_digestion_daily_output,
            manure_separator_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
        )

    def _handle_daily_update_for_simple_manure_treatment(
            self,
            simulation_day: int,
            pen: ManureManagerPen,
            manure_handler_daily_output: ManureHandlerDailyOutput,
            reception_pit_daily_output: ReceptionPitDailyOutput,
    ) -> Tuple[
        Optional[ManureSeparatorDailyOutput],
        ManureTreatmentDailyOutput,
        ManureTreatmentDailyOutput,
    ]:
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
        manure_separator_daily_output = (
            self.manure_separators[pen.id].daily_update(
                manure_separator_daily_input=reception_pit_daily_output
            )
            if self.manure_separators[pen.id]
            else None
        )

        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=manure_separator_daily_output or reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day,
        )

        manure_treatment_accumulated_output = self.manure_treatments[
            pen.id
        ].accumulated_output

        return (
            manure_separator_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
        )


def simulate_daily_manure_manager(
        manure_manager: ManureManager, animal_manager: AnimalManager
) -> None:
    """A wrapper function for the daily_update method of the ManureManager class.

    There is no strict reason why this function is needed. It is simply to make the code
    in the SimulationEngine more readable. It is OK to remove this function and call the
    daily_update method directly from the SimulationEngine.

    Parameters
    ----------
    manure_manager : ManureManager
        A reference to the ManureManager object stored in the SimulationEngine.
    animal_manager : AnimalManager
        A reference to the AnimalManager object stored in the SimulationEngine
        so the latest data can be passed to the ManureManager object.

    """
    manure_manager.daily_update(animal_manager)
