from __future__ import annotations

import math
import typing
from typing import Any, Dict, List, Optional, Tuple

from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding, BeddingFactory
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.field_manure_supplier import FieldManureSupplier
from RUFAS.routines.manure.IO_helpers.manure_manager_config_handler import ManureManagerConfigHandler
from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import ManureModuleOutputManagerHelper
from RUFAS.routines.manure.manure_handlers.manure_handler_classes import BaseManureHandler, ManureHandlerFactory
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_nutrients.manure_nutrient_manager import ManureNutrientManager
from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_to_crop_soil_connection import NutrientRequest, NutrientRequestResults
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator, ManureSeparatorFactory
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion_and_lagoon import AnaerobicDigestionAndLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_factory import ManureTreatmentFactory
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.reception_pits.reception_pit import ReceptionPit
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather


class ManureManager:
    """
    A class that sets up and manages different manure management components including manure handlers,
    reception pits, manure separators, and manure storage treatments. When the simulation engine performs
    a daily simulation, it invokes the update method on an instance of this class, thereby generating
    and storing daily output data.


    Attributes
    ----------
    manure_handlers : Dict
        A dictionary that maps an animal pen's id to a ManureHandler object.
    reception_pits : Dict
        A dictionary that maps an animal pen's id to a ReceptionPit object.
    manure_separators : Dict
        A dictionary that maps an animal pen's id to a ManureSeparator object.
    manure_treatments : Dict
        A dictionary that maps an animal pen's id to a Treatment object.
    simulate_animals : bool
        Records whether animals are being simulated.

    """

    def __init__(
        self,
        pen_list: List[PenManureData],
        weather: Weather,
        time: Time,
        manure_manager_config: dict[str, Any],
        simulate_animals: bool,
    ) -> None:
        """Initializes a ManureManager object by setting up the appropriate manure
        manager components as specified by the data in the animal_manager object.

        Parameters
        ----------
        pen_list : List[PenManureData]
            List of pen manure data instances containing all needed manure information.
        weather : Weather
            The Weather object used to initialize State variables.
        time : Time
            The Time object used to initialize State variables.
        manure_manager_config : dict[str, Any]
            A dictionary that contains the configuration data for
            different manure management scenarios.
        simulate_animals : bool
            Indicates whether animals are being simulated.

        """
        self.beddings: Dict[int, BaseBedding] = {}
        self.manure_handlers: Dict[int, BaseManureHandler] = {}
        self.reception_pits: Dict[int, ReceptionPit] = {}
        self.manure_separators: Dict[int, Optional[BaseManureSeparator]] = {}
        self.manure_separators_after_digestion: Dict[int, Optional[BaseManureSeparator]] = {}
        self.manure_treatments: Dict[int, BaseManureTreatment] = {}
        self.weather = weather
        self.time = time
        self.manure_manager_config_handler = ManureManagerConfigHandler(manure_manager_config)
        self._daily_output_per_pen = []
        self._manure_nutrient_manager = ManureNutrientManager()
        self.simulate_animals = simulate_animals
        self._field_manure_supplier = FieldManureSupplier()
        self.configure_manure_manager_components(pen_list)
        self.om = OutputManager()

    def configure_manure_manager_components(self, pen_list: List[PenManureData]) -> None:
        """Configures the manure manager components for each animal pen.

        Each pen is associated with the following components - bedding, manure handler,
        reception pit, manure separator, and manure treatment.

        Parameters
        ----------
        pen_list : List[PenManureData]
            List of PenManureData instances that contain all needed manure information.
        """
        for pen in pen_list:
            mm_pen = ManureManagerPen(pen)

            bedding_config = self.manure_manager_config_handler.get_bedding_config(mm_pen.bedding_type)
            self.beddings[mm_pen.id] = BeddingFactory.get_instance(
                bedding_name=mm_pen.bedding_type,
                bedding_config=bedding_config,
            )

            manure_handler_config = self.manure_manager_config_handler.get_manure_handler_config(mm_pen.manure_handler)
            self.manure_handlers[mm_pen.id] = ManureHandlerFactory.get_manure_handler(
                configuration_name=mm_pen.manure_handler,
                weather=self.weather,
                time=self.time,
                manure_handler_config=manure_handler_config,
            )

            self.reception_pits[mm_pen.id] = ReceptionPit()

            separator_config = self.manure_manager_config_handler.get_manure_separator_config(mm_pen.manure_separator)
            separator = (
                None
                if not separator_config
                else ManureSeparatorFactory.get_instance(
                    configuration_name=mm_pen.manure_separator,
                    manure_separator_config=separator_config,
                )
            )
            self.manure_separators[mm_pen.id] = separator

            separator_config_post_digester = self.manure_manager_config_handler.get_manure_separator_config(
                mm_pen.manure_separator_after_digestion
            )
            separator_post_digester = (
                None
                if not separator_config_post_digester
                else ManureSeparatorFactory.get_instance(
                    configuration_name=mm_pen.manure_separator_after_digestion,
                    manure_separator_config=separator_config_post_digester,
                )
            )
            self.manure_separators_after_digestion[mm_pen.id] = separator_post_digester

            manure_treatment_config = self.manure_manager_config_handler.get_manure_treatment_config(
                mm_pen.manure_treatment
            )
            self.manure_treatments[mm_pen.id] = ManureTreatmentFactory.get_instance(
                configuration_name=mm_pen.manure_treatment,
                weather=self.weather,
                time=self.time,
                manure_treatment_config=manure_treatment_config,
            )

    def daily_update(self, pen_list: List[PenManureData], simulation_day: int) -> None:
        """Calculates daily output data for each manure manager component for each animal pen.

        Notes
        -----
        On the last day of the simulation, all the data generated daily by the manure manager
        components will be exported to a CSV file.

        Parameters
        ----------
        pen_list : List[Pen]
            List of pens found in AnimalManager object.
        simulation_day : int
            Day of simulation.
        """
        number_of_new_pens = len(pen_list) - len(self.manure_treatments)
        if number_of_new_pens > 0:
            self.configure_manure_manager_components(pen_list[len(self.manure_treatments) :])
        for pen in pen_list:
            self._pen_daily_update(simulation_day, pen)

        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager.get_values(ManureType.LIQUID),
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "ManureNutrientsLiquid",
            },
        )
        ManureModuleOutputManagerHelper.add_dataclass_object(
            self._manure_nutrient_manager.get_values(ManureType.SOLID),
            info_maps={
                "class": self.__class__.__name__,
                "function": self.daily_update.__name__,
                "prefix": "ManureNutrientsSolid",
            },
        )

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
            ManureTreatmentType.SLURRY_STORAGE_OUTDOOR: ManureType.LIQUID,
            ManureTreatmentType.SLURRY_STORAGE_UNDERFLOOR: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_LAGOON: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION: ManureType.LIQUID,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR: ManureType.LIQUID,
            ManureTreatmentType.COMPOST_BEDDED_PACK_BARN: ManureType.SOLID,
            ManureTreatmentType.OPEN_LOTS: ManureType.SOLID,
            ManureTreatmentType.SEPARATED_SOLIDS_STORAGE: ManureType.SOLID,
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
        Add the nutrients in the manure to the manure nutrient manager by manure type.

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

        liquid_manure_nitrogen = max(manure_treatment_daily_output.liquid_manure_nitrogen, 0.0)
        liquid_manure_phosphorus = max(manure_treatment_daily_output.liquid_manure_phosphorus, 0.0)
        liquid_manure_potassium = max(manure_treatment_daily_output.liquid_manure_potassium, 0.0)
        liquid_manure_total_solids = max(manure_treatment_daily_output.liquid_manure_total_solids, 0.0)
        liquid_total_manure_mass = max(
            (
                manure_treatment_daily_output.liquid_manure_daily_volume
                * self._get_manure_density_by_type(ManureType.LIQUID)
            ),
            0.0,
        )
        self._manure_nutrient_manager.add_nutrients(
            ManureNutrients(
                nitrogen=liquid_manure_nitrogen,
                phosphorus=liquid_manure_phosphorus,
                potassium=liquid_manure_potassium,
                dry_matter=liquid_manure_total_solids,
                total_manure_mass=liquid_total_manure_mass,
                manure_type=ManureType.LIQUID,
            )
        )

        solid_manure_phosphorus = max(manure_treatment_daily_output.solid_manure_phosphorus, 0.0)
        solid_manure_nitrogen = max(manure_treatment_daily_output.solid_manure_nitrogen, 0.0)
        solid_manure_potassium = max(manure_treatment_daily_output.solid_manure_potassium, 0.0)
        solid_manure_total_solids = max(manure_treatment_daily_output.solid_manure_total_solids, 0.0)
        solid_total_manure_mass = max(manure_treatment_daily_output.solid_manure_daily_mass, 0.0)
        self._manure_nutrient_manager.add_nutrients(
            ManureNutrients(
                nitrogen=solid_manure_nitrogen,
                phosphorus=solid_manure_phosphorus,
                potassium=solid_manure_potassium,
                dry_matter=solid_manure_total_solids,
                total_manure_mass=solid_total_manure_mass,
                manure_type=ManureType.SOLID,
            )
        )

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
        if self.simulate_animals:
            request_result, is_nutrient_request_fulfilled = self._manure_nutrient_manager.request_nutrients(request)
            self._record_manure_request_results(request_result, "on_farm_manure")
            if not is_nutrient_request_fulfilled and request.use_supplemental_manure:
                self.om.add_log(
                    "Supplemental manure needed",
                    "Attempting to fulfill manure nutrient request shortfall with supplemental manure.",
                    {"class": self.__class__.__name__, "function": self.request_nutrients.__name__},
                )
                amount_supplemental_manure_needed = self._calculate_supplemental_manure_needed(request_result, request)
                supplemental_manure = self._field_manure_supplier.request_nutrients(amount_supplemental_manure_needed)
                self._record_manure_request_results(supplemental_manure, "off_farm_manure")
                combined_manure = request_result + supplemental_manure
                return combined_manure
            return request_result
        else:
            return self._field_manure_supplier.request_nutrients(request)

    def _record_manure_request_results(
        self, manure_request_results: NutrientRequestResults | None, manure_source: str
    ) -> None:
        """
        Record the results of a manure request in the Output Manager.

        Parameters
        ----------
        manure_request_results : NutrientRequestResults | None
            The results of a manure request. If None, it means that there was no available on-farm manure.
        manure_source : str
            The source of the manure.
        """
        info_maps = {
            "class": ManureManager.__name__,
            "function": ManureManager._record_manure_request_results.__name__,
            "units": {
                "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
                "dry_matter_fraction": MeasurementUnits.FRACTION,
                "total_manure_mass": MeasurementUnits.KILOGRAMS,
                "organic_nitrogen_fraction": MeasurementUnits.FRACTION,
                "inorganic_nitrogen_fraction": MeasurementUnits.FRACTION,
                "ammonium_nitrogen_fraction": MeasurementUnits.FRACTION,
                "organic_phosphorus_fraction": MeasurementUnits.FRACTION,
                "inorganic_phosphorus_fraction": MeasurementUnits.FRACTION,
                "nitrogen": MeasurementUnits.KILOGRAMS,
                "phosphorus": MeasurementUnits.KILOGRAMS,
                "request_julian_day": MeasurementUnits.ORDINAL_DAY,
                "request_calendar_year": MeasurementUnits.CALENDAR_YEAR,
            },
        }
        if not manure_request_results:
            request_result_values = {
                "dry_matter_mass": 0.0,
                "dry_matter_fraction": 0.0,
                "total_manure_mass": 0.0,
                "organic_nitrogen_fraction": 0.0,
                "inorganic_nitrogen_fraction": 0.0,
                "ammonium_nitrogen_fraction": 0.0,
                "organic_phosphorus_fraction": 0.0,
                "inorganic_phosphorus_fraction": 0.0,
                "nitrogen": 0.0,
                "phosphorus": 0.0,
                "request_julian_day": self.time.current_julian_day,
                "request_calendar_year": self.time.current_calendar_year,
            }
            self.om.add_log(
                "Recording empty manure request result", "No manure available on farm to fulfill request.", info_maps
            )
        else:
            request_result_values = {
                "dry_matter_mass": manure_request_results.dry_matter,
                "dry_matter_fraction": manure_request_results.dry_matter_fraction,
                "total_manure_mass": manure_request_results.total_manure_mass,
                "organic_nitrogen_fraction": manure_request_results.organic_nitrogen_fraction,
                "inorganic_nitrogen_fraction": manure_request_results.inorganic_nitrogen_fraction,
                "ammonium_nitrogen_fraction": manure_request_results.ammonium_nitrogen_fraction,
                "organic_phosphorus_fraction": manure_request_results.organic_phosphorus_fraction,
                "inorganic_phosphorus_fraction": manure_request_results.inorganic_phosphorus_fraction,
                "nitrogen": manure_request_results.nitrogen,
                "phosphorus": manure_request_results.phosphorus,
                "request_julian_day": self.time.current_julian_day,
                "request_calendar_year": self.time.current_calendar_year,
            }
        self.om.add_variable(manure_source, request_result_values, info_maps)

    @staticmethod
    def _calculate_supplemental_manure_needed(
        on_farm_manure: NutrientRequestResults | None, nutrient_request: NutrientRequest
    ) -> NutrientRequest:
        """
        Calculate the amount of supplemental manure needed to fulfill the nutrient request.

        Parameters
        ----------
        on_farm_manure : NutrientRequestResults | None
            The results of the nutrient request for manure available from the farm. If None, it means that
            there was no available on-farm manure.
        nutrient_request : NutrientRequest
            The nutrient request.

        Returns
        -------
        NutrientRequest
            The request for supplemental manure needed to fulfill the original nutrient request.
        """
        remaining_nitrogen = max(0, nutrient_request.nitrogen - (on_farm_manure.nitrogen if on_farm_manure else 0))
        remaining_phosphorus = max(
            0, nutrient_request.phosphorus - (on_farm_manure.phosphorus if on_farm_manure else 0)
        )

        if math.isclose(remaining_nitrogen, 0.0, abs_tol=1e-6) and math.isclose(
            remaining_phosphorus, 0.0, abs_tol=1e-6
        ):
            return NutrientRequest(
                nitrogen=0.0,
                phosphorus=0.0,
                manure_type=nutrient_request.manure_type,
                use_supplemental_manure=True,
            )

        return NutrientRequest(
            nitrogen=remaining_nitrogen,
            phosphorus=remaining_phosphorus,
            manure_type=nutrient_request.manure_type,
            use_supplemental_manure=True,
        )

    def _pen_daily_update(self, simulation_day: int, pen: PenManureData) -> None:
        """
        Calculate daily output data for each manure manager component for a given animal pen.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.
        pen : PenManureData
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
            "prefix": f"AnimalModuleInputToManureModule_Pen_{mm_pen.id}_{mm_pen.animal_combination.name}"
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
            "prefix": f"{manure_handler_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
            f"{mm_pen.animal_combination.name}"
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
            "prefix": f"{reception_pit_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
            f"{mm_pen.animal_combination.name}"
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
        manure_separator_after_digestion_daily_output = results[2]
        manure_treatment_daily_output = results[3]
        manure_treatment_accumulated_output = results[4]

        if anaerobic_digestion_daily_output:
            anaerobic_digestion_daily_output_prefix = {
                "prefix": f"AnaerobicDigestion_{anaerobic_digestion_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
                f"{mm_pen.animal_combination.name}"
            }
            ManureModuleOutputManagerHelper.add_dataclass_object(
                anaerobic_digestion_daily_output,
                class_and_function_info_maps | anaerobic_digestion_daily_output_prefix,
                excluded_fields,
            )
        if manure_separator_daily_output:
            manure_separator_daily_output_prefix = {
                "prefix": f"{manure_separator_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
                f"{mm_pen.animal_combination.name}"
            }
            ManureModuleOutputManagerHelper.add_dataclass_object(
                manure_separator_daily_output,
                class_and_function_info_maps | manure_separator_daily_output_prefix,
                excluded_fields,
            )

        if manure_separator_after_digestion_daily_output:
            manure_separator_after_digestion_daily_output_prefix = {
                "prefix": f"ManureSeparatorAfterDigestionDailyOutput_Pen_{str(mm_pen.id)}"
                f"_{mm_pen.animal_combination.name}"
            }
            ManureModuleOutputManagerHelper.add_dataclass_object(
                manure_separator_after_digestion_daily_output,
                class_and_function_info_maps | manure_separator_after_digestion_daily_output_prefix,
                excluded_fields,
            )

        manure_treatment_daily_output_prefix = {
            "prefix": f"{manure_treatment_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
            f"{mm_pen.animal_combination.name}"
        }
        ManureModuleOutputManagerHelper.add_dataclass_object(
            manure_treatment_daily_output,
            class_and_function_info_maps | manure_treatment_daily_output_prefix,
            excluded_fields,
        )

        accumulated_manure_treatment_output_prefix = {
            "prefix": f"Accumulated_{manure_treatment_daily_output.__class__.__name__}_Pen_{mm_pen.id}_"
            f"{mm_pen.animal_combination.name}"
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
            "manure_separator_after_digestion_daily_output": manure_separator_after_digestion_daily_output,
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
            manure_separator_after_digestion_daily_output = results[2]
            manure_treatment_daily_output = results[3]
            manure_treatment_accumulated_output = results[4]
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
            manure_separator_after_digestion_daily_output = None

        return (
            anaerobic_digestion_daily_output,
            manure_separator_daily_output,
            manure_separator_after_digestion_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
        )

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
        compound_anaerobic_manure_treatment_types = {
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON.value,
            ManureTreatmentType.ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR.value,
        }
        return manure_treatment_name in compound_anaerobic_manure_treatment_types

    def _handle_daily_update_for_compound_anaerobic_manure_treatment(
        self,
        simulation_day: int,
        pen: ManureManagerPen,
        manure_handler_daily_output: ManureHandlerDailyOutput,
        reception_pit_daily_output: ReceptionPitDailyOutput,
    ) -> Tuple[
        ManureTreatmentDailyOutput,
        Optional[ManureSeparatorDailyOutput],
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
        manure_separator_daily_output = (
            self.manure_separators[pen.id].daily_update(manure_separator_daily_input=reception_pit_daily_output)
            if self.manure_separators[pen.id]
            else None
        )
        # Currently, calling the daily_update on the treatment only returns one final output
        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=manure_separator_daily_output or reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day,
            manure_separator=self.manure_separators[pen.id],
            manure_separator_after_digestion=self.manure_separators_after_digestion[pen.id],
        )

        # To retrieve the following three intermediate results,
        # we need to access them via instance variables of the treatment object
        anaerobic_digestion_daily_output = typing.cast(
            AnaerobicDigestionAndLagoon, self.manure_treatments[pen.id]
        ).anaerobic_digestion_daily_output

        manure_separator_after_digestion_daily_output = self.manure_treatments[
            pen.id
        ].manure_separator_after_digestion_daily_output

        manure_treatment_accumulated_output = self.manure_treatments[pen.id].accumulated_output

        return (
            anaerobic_digestion_daily_output,
            manure_separator_daily_output,
            manure_separator_after_digestion_daily_output,
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
            self.manure_separators[pen.id].daily_update(manure_separator_daily_input=reception_pit_daily_output)
            if self.manure_separators[pen.id]
            else None
        )

        manure_treatment_daily_output = self.manure_treatments[pen.id].daily_update(
            manure_handler_daily_output=manure_handler_daily_output,
            manure_treatment_daily_input=manure_separator_daily_output or reception_pit_daily_output,
            pen=pen,
            sim_day=simulation_day,
        )

        manure_treatment_accumulated_output = self.manure_treatments[pen.id].accumulated_output

        return (
            manure_separator_daily_output,
            manure_treatment_daily_output,
            manure_treatment_accumulated_output,
        )
