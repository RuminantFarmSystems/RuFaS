import math

from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType
from RUFAS.routines.field.crop.crop import Crop
from RUFAS.routines.field.crop.crop_data import CropData
from RUFAS.routines.field.crop.species_data_factory import CropSpecies, CropSpeciesDataFactory
from RUFAS.routines.field.manager.events import Event, PlantingEvent, HarvestEvent, FertilizerEvent, ManureEvent
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.routines.field.soil.soil import Soil
from RUFAS.routines.field.field.field_data import FieldData
from RUFAS.routines.field.field.fertilizer_application import FertilizerApplication
from RUFAS.routines.field.field.tillage_application import TillageApplication
from typing import Optional, List, Dict, Tuple
from math import exp
from RUFAS.routines.field.crop.harvest_operations import HarvestOperation
from RUFAS.routines.field.field.manure_application import ManureApplication
from RUFAS.routines.field.manager.events import TillageEvent
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest
from RUFAS.routines.manure.manure_nutrients.nutrient_request_results import NutrientRequestResults
from RUFAS.time import Time
from copy import copy

"""
This is a high-level module that represents and simulates an entire field. It is responsible for executing the daily
biophysical routines which take place in soil columns and in crops planted in the field. It is also responsible for the
management of schedules, executing, and reporting of farm management events, including planting and harvesting crops,
adding manure and fertilizer to the soil, and tilling the soil.
"""

om = OutputManager()


class Field:

    def __init__(
            self,
            field_data: Optional[FieldData] = None,
            soil: Optional[Soil] = None,
            plantings: Optional[List[PlantingEvent]] = None,
            harvestings: Optional[List[HarvestEvent]] = None,
            custom_crop_specifications: Optional[Dict[str, Dict]] = None,
            tillage_events: Optional[List[TillageEvent]] = None,
            fertilizer_events: Optional[List[FertilizerEvent]] = None,
            fertilizer_mixes: Optional[Dict[str, Dict[str, float]]] = None,
            manure_events: Optional[List[ManureEvent]] = None,
            manure_manager: Optional[ManureManager] = None,
            feed_manager: Optional[FeedManager] = None,
    ):
        """
        Initialize the related data fields that this module will work with, or create one if none provided.

        Parameters
        ----------
        field_data : FieldData
            FieldData object that will be simulated.
        soil : Soil
            The soil component of the field.
        plantings : List[PlantingEvent]
            List of all planting events that will occur over the run of the simulation in this field.
        harvestings : List[HarvestEvent]
            List of all harvesting events that will occur over the run of the simulation in the field.
        custom_crop_specifications : Dict[str, Dict]
            Dictionary where keys are crop references and values are dictionaries containing crop specifications.
        tillage_events : List[TillageEvent]
            List of all tillage events that will occur over the run of the simulation in this field.
        fertilizer_events : List[FertilizerEvent]
            List of all fertilizer mixes available for application to this field.
        fertilizer_mixes : Dict[str, Dict[str, float]]
            List of all fertilizer mixes available for application to this field.
        manure_events : List[ManureEvent]
            Manure application interface.
        manure_manager : ManureManager
            ManureManager Object to be used during simulation

        """
        # field-wide attributes
        self.field_data = field_data or FieldData()

        # soil attributes
        self.soil = soil or Soil(soil_data=None, field_size=self.field_data.field_size)  # default soil if not given.

        # crop attributes
        self.crops: List[Crop] = list()  # empty crop list

        self.planting_events: List[PlantingEvent] = plantings or []

        self.harvest_events: List[HarvestEvent] = harvestings or []

        self.custom_crop_specifications: Dict[str, Dict] = custom_crop_specifications or {}

        # Soil amendment attributes
        self.fertilizer_applicator = FertilizerApplication(self.soil)
        """Provides interface for adding fertilizer to the field."""

        self.fertilizer_events = fertilizer_events or []

        self.available_fertilizer_mixes = fertilizer_mixes or {}
        self.available_fertilizer_mixes["100_0_0"] = {"N": 1.0, "P": 0.0, "K": 0.0}
        self.available_fertilizer_mixes["26_4_24"] = {"N": 0.26, "P": 0.04, "K": 0.24}
        """List of all fertilizer mixes available for application to this field. The 100_0_0 and 26_4_24 mixes will
            always be available as supplements to unfulfilled manure nutrient demands."""

        self.ONLY_NITROGEN_MIX = "100_0_0"
        """Constant with the name of the fertilizer mix that contains only Nitrogen."""

        self.tiller = TillageApplication(self.field_data, self.soil.data)
        """Provides interface to till the field."""

        self.tillage_events: List[TillageEvent] = tillage_events
        """List of all tillage events that will occur over the run of the simulation in this field."""

        self.manure_applicator = ManureApplication(self.soil.data)

        self.manure_events: List[ManureEvent] = manure_events or []
        """List of all manure applications that will be applied to this field."""

        info_map = {
            "class": self.__class__.__name__,
            "function": self.__init__.__name__
        }

        if manure_manager is None:
            om.add_error(
                "field_initialization_error",
                f"Attempted initialization of Field {self.field_data.name=} with no Manure Manager, failing to "
                f"initialize.",
                info_map
            )
            raise ValueError("Manure manager cannot be None.")

        self.manure_manager: ManureManager = manure_manager
        """:class:`ManureManager` instance from which manure is requested for application to the field."""

        if feed_manager is None:
            om.add_error(
                "field_initialization_error",
                f"Attempted initialization of Field {self.field_data.name=} with no Feed Manager, initializing a "
                f"FeedManager to use.",
                info_map
            )

        self.feed_manager: FeedManager = feed_manager or FeedManager()
        """:class:`FeedManager` instance which receives harvested crops."""

    def manage_field(self, time, current_conditions: CurrentDayConditions) -> None:
        """
        Main Field routine, runs all subroutines routines based on current attribute configuration.

        Parameters
        ----------
        time : Time
            Contains the current year and day that the simulation is on.
        current_conditions : CurrentDayConditions
            Contains a collection of today's conditions variables needed for field processes.

        Notes
        -----
        This method starts by executing any soil amendments that may be scheduled for the day. Then it executes the
        daily update routines for the soil profile and active crops in the field. It then plants and/or harvests crops,
        checks if active crops need to go into dormancy, and resets crop attributes in both the crops and in the field's
        data object.

        """
        # --- Soil Management---
        self._check_fertilizer_application_schedule(time)

        self._check_manure_application_schedule(time)

        self._check_tillage_schedule(time)

        # --- Whole-Field Methods ---
        # Allow non-management field processes (water/nutrient cycling) to occur
        self._execute_daily_processes(current_conditions, time)
        # ... Other ...

        # --- Crop Management ---
        self._assess_dormancy(current_conditions.daylength, current_conditions.rainfall)

        self._check_crop_planting_schedule(time)

        self._check_crop_harvest_schedule(time, current_conditions)

        self._remove_dead_crops()
        self._reset_crop_field_coverage_fractions()

    # <editor-fold desc="--- Soil Management Methods ---">
    def _execute_fertilizer_application(self, mix_name: str, requested_nitrogen: float, requested_phosphorus: float,
                                        application_depth: float, surface_remainder_fraction: float, year: int,
                                        day: int) -> None:
        """
        Executes a fertilizer application based on the requested amounts of nutrients.

        Parameters
        ----------
        mix_name : str
            The name of the mix this fertilizer application should be composed of.
        requested_nitrogen : float
            Minimum amount of nitrogen to be included in this fertilizer application (kg).
        requested_phosphorus : float
            Minimum amount of phosphorus to be included in this fertilizer application (kg).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which the fertilizer application is occurring.
        day : int
            Julian day on which this fertilizer application is occurring.

        Raises
        ------
        KeyError
            If the specified fertilizer mix is not defined in the list of available fertilizers to this field.

        Notes
        -----
        This method is responsible for determining the exact amounts of fertilizer and nutrients added to the field,
        passing those amount to the FertilizerApplication module, and recording the fertilizer application to the
        OutputManager. Because potassium requests are still not accounted for when determining the amount of fertilizer
        applied, the method checks that there is at least some nitrogen or phosphorus requested, if not it returns
        without applying any fertilizer.

        """
        if requested_nitrogen == requested_phosphorus == 0.0:
            info_map = {"class": self.__class__.__name__, "function": self._execute_fertilizer_application.__name__,
                        "prefix": f"field='{self.field_data.name}'", "date": {"year": year, "day": day}}
            log_message = "Tried to apply fertilizer with no nitrogen or phosphorus requested."
            om.add_log("fertilizer_application_log", log_message, info_map)
            return

        invalid_depth_and_remainder_fraction = (application_depth == 0.0 and surface_remainder_fraction != 1.0) or \
                                               (application_depth > 0.0 and surface_remainder_fraction == 1.0)
        error_message = "fertilizer_application_error"
        if invalid_depth_and_remainder_fraction:
            self._record_nutrient_application_error(application_depth, surface_remainder_fraction, error_message, year,
                                                    day)
            application_depth = 0.0
            surface_remainder_fraction = 1.0

        if application_depth > self.soil.data.soil_layers[-1].bottom_depth:
            self._record_nutrient_application_error(application_depth, None, error_message, year, day)
            application_depth = self.soil.data.soil_layers[-1].bottom_depth

        try:
            fertilizer_mix = self.available_fertilizer_mixes[mix_name]
        except KeyError:
            raise KeyError(f"'{self.field_data.name}': expected to have fertilizer mix for '{mix_name}', "
                           f"received '{self.available_fertilizer_mixes}'.")
        nitrogen_fraction = fertilizer_mix.get("N")
        phosphorus_fraction = fertilizer_mix.get("P")
        potassium_fraction = fertilizer_mix.get("K")

        fertilizer_applied = self._formulate_fertilizer_required(nitrogen_fraction, phosphorus_fraction,
                                                                 potassium_fraction, requested_nitrogen,
                                                                 requested_phosphorus)
        total_mass_applied = fertilizer_applied.get("total_mass")
        phosphorus_applied = fertilizer_applied.get("phosphorus_mass")
        nitrogen_applied = fertilizer_applied.get("nitrogen_mass")
        potassium_applied = fertilizer_applied.get("potassium_mass")

        # TODO: specify these fractions in fertilizer mixes - issue #573
        inorganic_nitrogen_fraction = nitrogen_applied / total_mass_applied
        ammonium_fraction = 0.0
        organic_nitrogen_fraction = 0.0

        self.fertilizer_applicator.apply_fertilizer(phosphorus_applied, total_mass_applied, inorganic_nitrogen_fraction,
                                                    ammonium_fraction, organic_nitrogen_fraction, application_depth,
                                                    surface_remainder_fraction, self.field_data.field_size)

        self._record_fertilizer_application(mix_name, total_mass_applied, nitrogen_applied, phosphorus_applied,
                                            potassium_applied, application_depth, surface_remainder_fraction, year, day)

    @staticmethod
    def _determine_optimal_fertilizer_mix(requested_nitrogen: float, requested_phosphorus: float,
                                          available_mixes: Dict[str, Dict[str, float]]) -> str:
        """
        Takes the requested nutrients of a fertilizer application and determines which fertilizer mix would fill them
        the most efficiently.

        Parameters
        ----------
        requested_nitrogen : float
            Minimum amount of nitrogen to be included in this fertilizer application.
        requested_phosphorus : float
            Minimum amount of phosphorus to be included in this fertilizer application.
        available_mixes : Dict[str, Dict[str, float]]
            List of fertilizer mixes available for application to the field.

        Returns
        -------
        str
            Name of the fertilizer mix which requires the least mass of fertilizer to fill the nutrient requests.

        Notes
        -----
        The optimal fertilizer mix is currently the one that requires the least amount of fertilizer to meet the
        demanded nutrients, but a more realistic definition of "optimal" may mean the mix that costs the least to fill
        the requested nutrients with.

        """
        optimal_mix = None
        least_fertilizer_mix_required = math.inf
        for mix_name, mix_values in available_mixes.items():
            if mix_name == "100_0_0":
                continue
            fertilizer_application = Field._formulate_fertilizer_required(mix_values["N"], mix_values["P"],
                                                                          mix_values["K"], requested_nitrogen,
                                                                          requested_phosphorus)
            total_mass = fertilizer_application["total_mass"]
            if total_mass == 0.0:
                continue
            elif total_mass < least_fertilizer_mix_required:
                optimal_mix = mix_name
                least_fertilizer_mix_required = total_mass
        return optimal_mix

    @staticmethod
    def _formulate_fertilizer_required(nitrogen_fraction: float, phosphorus_fraction: float,
                                       potassium_fraction: float, requested_nitrogen: float,
                                       requested_phosphorus: float) -> Dict[str, float]:
        """
        Determines the total mass of a specific fertilizer mix needed to meet the specified nutrient requirements.

        Parameters
        ----------
        nitrogen_fraction : float
            Fraction of fertilizer mix that is nitrogen, in range [0.0, 1.0] (unitless)
        phosphorus_fraction : float
            Fraction of fertilizer mix that is phosphorus, in range [0.0, 1.0] (unitless)
        potassium_fraction : float
            Fraction of fertilizer mix that is potassium, in range [0.0, 1.0] (unitless)
        requested_nitrogen : float
            Minimum mass of nitrogen to be included in fertilizer application (kg)
        requested_phosphorus : float
            Minimum mass of phosphorus to be included in fertilizer application (kg)

        Returns
        -------
        Dict[str, float]
            The total mass of fertilizer, and the masses of nitrogen, phosphorus, and potassium in the fertilizer.

        """
        minimum_mass_for_nitrogen = (0 if nitrogen_fraction == 0 else (requested_nitrogen / nitrogen_fraction))
        minimum_mass_for_phosphorus = (0 if phosphorus_fraction == 0 else (requested_phosphorus / phosphorus_fraction))

        total_mass = max(minimum_mass_for_nitrogen, minimum_mass_for_phosphorus)
        nitrogen_mass = total_mass * nitrogen_fraction
        phosphorus_mass = total_mass * phosphorus_fraction
        potassium_mass = total_mass * potassium_fraction
        return {"total_mass": total_mass, "nitrogen_mass": nitrogen_mass, "phosphorus_mass": phosphorus_mass,
                "potassium_mass": potassium_mass}

    def _record_fertilizer_application(self, mix_name: str, total_mass: float, nitrogen_mass: float,
                                       phosphorus_mass: float, potassium_mass: float, application_depth: float,
                                       surface_remainder_fraction: float, year: int, day: int) -> None:
        """
        Records a fertilizer application and saves it to the Output manager.

        Parameters
        ----------
        mix_name : str
            The name of the mix this fertilizer application is composed of.
        total_mass : float
            The total mass of phosphorus applied (kg).
        nitrogen_mass : float
            The mass of nitrogen applied (kg).
        phosphorus_mass : float
            The mass of phosphorus applied (kg).
        potassium_mass : float
            The mass of potassium applied (kg).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which the fertilizer application is occurring.
        day : int
            Julian day on which this fertilizer application is occurring.

        """
        info_map = {"class": self.__class__.__name__, "function": self._record_fertilizer_application.__name__,
                    "prefix": f"field='{self.field_data.name}'",
                    "mix_name": mix_name, "field_size": self.field_data.field_size}
        value = {"mass": total_mass, "nitrogen": nitrogen_mass, "phosphorus": phosphorus_mass,
                 "potassium": potassium_mass, "application_depth": application_depth,
                 "surface_remainder_fraction": surface_remainder_fraction, "year": year, "day": day}
        om.add_variable("fertilizer_application", value, info_map)

    @staticmethod
    def _construct_evaluation_manure_application(nutrient_request: NutrientRequest) -> NutrientRequestResults:
        dry_matter_fraction = 0.05
        total_manure_mass = nutrient_request.nitrogen * 479.999_883
        dry_matter_amount = total_manure_mass * dry_matter_fraction
        evaluation_request = NutrientRequestResults(
            nitrogen=nutrient_request.nitrogen,
            phosphorus=nutrient_request.phosphorus,
            total_manure_mass=total_manure_mass,
            dry_matter=dry_matter_amount,
            dry_matter_fraction=dry_matter_fraction
        )
        return evaluation_request

    def _execute_manure_application(self, requested_nitrogen: float, requested_phosphorus: float,
                                    requested_manure_type: ManureType, field_coverage: float,
                                    application_depth: float, surface_remainder_fraction: float, year: int,
                                    day: int) -> None:
        """
        Builds a manure application from the requested nutrient amounts and passes that application to the
        ManureApplication module.

        Parameters
        ----------
        requested_nitrogen : float
            Mass of nitrogen requested to be in this manure application (kg)
        requested_phosphorus : float
            Mass of phosphorus requested to be in this manure application (kg)
        requested_manure_type : ManureType
            The type of manure for which the application request will be made.
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.

        Notes
        -----
        Because potassium is not currently specified in the manure request results, it is recorded as None. This method
        also checks for invalid application depths and surface remainder fractions. If invalid values are found, they
        are corrected, an error is logged to the OutputManager, and execution continues with the new values.

        If the manure supplied by the Manure module does not meet or exceed the requested nutrients amounts, then either
        a) a warning will be raised to the OutputManager that the manure supplied was nutrient deficient, or b) an
        optimized chemical fertilizer application will be created and executed to supplement the nutrient deficiencies.
        This behavior is regulated by the `supplement_manure_nutrient_deficiencies` attribute of the `FieldData` class.

        """
        info_map = {"class": self.__class__.__name__, "function": self._execute_manure_application.__name__,
                    "prefix": f"field='{self.field_data.name}'", "date": {"year": year, "day": day}}
        if requested_nitrogen == requested_phosphorus == 0.0:
            log_message = "Tried to apply manure with no nitrogen or phosphorus requested."
            om.add_log("manure_application_log", log_message, info_map)
            return

        nutrient_request = NutrientRequest(nitrogen=requested_nitrogen, phosphorus=requested_phosphorus,
                                           manure_type=requested_manure_type)

        # manure_supplied = self.manure_manager.request_nutrients(nutrient_request)
        manure_supplied = self._construct_evaluation_manure_application(nutrient_request)

        if manure_supplied is not None:
            supplied_nitrogen = manure_supplied.nitrogen
            supplied_phosphorus = manure_supplied.phosphorus

            total_inorganic_nitrogen_fraction = \
                (manure_supplied.nitrogen / manure_supplied.dry_matter) * manure_supplied.inorganic_nitrogen_fraction
            total_organic_nitrogen_fraction = \
                (manure_supplied.nitrogen / manure_supplied.dry_matter) * manure_supplied.organic_nitrogen_fraction

            invalid_depth_and_remainder_fraction = (application_depth == 0.0 and surface_remainder_fraction != 1.0) or \
                                                   (application_depth > 0.0 and surface_remainder_fraction == 1.0)

            error_name = "manure_application_error"
            if invalid_depth_and_remainder_fraction:
                self._record_nutrient_application_error(application_depth, surface_remainder_fraction, error_name, year,
                                                        day)
                application_depth = 0.0
                surface_remainder_fraction = 1.0

            if application_depth > self.soil.data.soil_layers[-1].bottom_depth:
                self._record_nutrient_application_error(application_depth, None, error_name, year, day)
                application_depth = self.soil.data.soil_layers[-1].bottom_depth

            self.manure_applicator.apply_machine_manure(
                dry_matter_mass=manure_supplied.dry_matter,
                dry_matter_fraction=manure_supplied.dry_matter_fraction,
                total_phosphorus_mass=manure_supplied.phosphorus,
                field_coverage=field_coverage,
                application_depth=application_depth,
                surface_remainder_fraction=surface_remainder_fraction,
                field_size=self.field_data.field_size,
                inorganic_nitrogen_fraction=total_inorganic_nitrogen_fraction,
                ammonium_fraction=manure_supplied.ammonium_nitrogen_fraction,
                organic_nitrogen_fraction=total_organic_nitrogen_fraction,
                water_extractable_inorganic_phosphorus_fraction=manure_supplied.inorganic_phosphorus_fraction)

            self._record_manure_application(dry_matter_mass=manure_supplied.dry_matter,
                                            dry_matter_fraction=manure_supplied.dry_matter_fraction,
                                            field_coverage=field_coverage,
                                            nitrogen=manure_supplied.nitrogen,
                                            phosphorus=manure_supplied.phosphorus,
                                            potassium=None,
                                            application_depth=application_depth,
                                            surface_remainder_fraction=surface_remainder_fraction,
                                            year=year,
                                            day=day)
        else:
            supplied_nitrogen = 0.0
            supplied_phosphorus = 0.0

        unmet_nitrogen_demand = max(0.0, requested_nitrogen - supplied_nitrogen)
        unmet_phosphorus_demand = max(0.0, requested_phosphorus - supplied_phosphorus)

        if unmet_nitrogen_demand == 0.0 and unmet_phosphorus_demand == 0.0:
            return

        if not self.field_data.supplement_manure_nutrient_deficiencies:
            warning_name = "Nutrient deficient manure application"
            warning_message = f"Manure nitrogen deficient by {unmet_nitrogen_demand} kg, manure phosphorus " \
                              f"deficient by {unmet_phosphorus_demand} kg."
            om.add_warning(warning_name, warning_message, info_map)
            return

        if unmet_nitrogen_demand > 0.0 and unmet_phosphorus_demand == 0.0:
            optimal_mix = self.ONLY_NITROGEN_MIX
        else:
            optimal_mix = self._determine_optimal_fertilizer_mix(unmet_nitrogen_demand, unmet_phosphorus_demand,
                                                                 self.available_fertilizer_mixes)
        self._execute_fertilizer_application(optimal_mix, unmet_nitrogen_demand, unmet_phosphorus_demand,
                                             application_depth, surface_remainder_fraction, year, day)

    def _record_manure_application(self, dry_matter_mass: float, dry_matter_fraction: float, field_coverage: float,
                                   nitrogen: float, phosphorus: float, application_depth: float,
                                   surface_remainder_fraction: float, year: int, day: int,
                                   potassium: Optional[float] = None) -> None:
        """
        Records the amount of manure and related values for an individual manure application.

        Parameters
        ----------
        dry_matter_mass : float
            Dry weight equivalent of this application (kg)
        dry_matter_fraction : float
            Fraction of this manure application that is dry matter, in the range (0.0, 1.0] (unitless)
        field_coverage : float
            Fraction of the field this manure is applied to (unitless)
        nitrogen : float
            Mass of nitrogen in the manure applied (kg)
        phosphorus : float
            Mass of phosphorus in the manure applied (kg)
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.
        potassium : float, Optional
            Mass of potassium in the manure applied (kg)

        """
        info_map = {"class": self.__class__.__name__, "function": self._record_manure_application.__name__,
                    "prefix": f"field='{self.field_data.name}'", "field_size": self.field_data.field_size}
        value = {"dry_matter_mass": dry_matter_mass, "dry_matter_fraction": dry_matter_fraction,
                 "field_coverage": field_coverage, "application_depth": application_depth,
                 "surface_remainder_fraction": surface_remainder_fraction, "nitrogen": nitrogen,
                 "phosphorus": phosphorus, "potassium": potassium, "day": day, "year": year}
        om.add_variable("manure_application", value, info_map)

    def _record_nutrient_application_error(self, application_depth: float, surface_remainder_fraction: Optional[float],
                                           error_name: str, year: int, day: int) -> None:
        """
        Logs errors to the OutputManager when attempting injection applications of manure or fertilizer.

        Parameters
        ----------
        application_depth : float
            Depth of the manure or fertilizer application (mm).
        surface_remainder_fraction : Optional[float]
            Fraction of manure or fertilizer applied that remains on the soil surface after application (unitless).
        error_name : str
            Name of the error, indicating whether it occurred during manure or fertilizer application.

        Notes
        -----
        There are two possible errors that this method can log. One is an invalid combination of application depth and
        surface remainder fraction, the other is an application depth deeper than the bottom of the soil profile. The
        two are differentiated by what is passed for `surface_remainder_fraction`. If it is a number, it is the former,
        and if None, then it is the latter.

        """
        info_map = {"class": self.__class__.__name__, "function": self._record_nutrient_application_error.__name__,
                    "prefix": f"field='{self.field_data.name}'", "date": {"year": year, "day": day}}
        if surface_remainder_fraction is not None:
            error_message = f"Invalid application depth ({application_depth}) and surface remainder fraction " \
                            f"({surface_remainder_fraction}). Defaulting to application depth of 0.0 mm and a " \
                            f"surface remainder fraction of 1.0."
        else:
            error_message = f"Invalid application depth ({application_depth}) is lower than the bottom depth of " \
                            f"the soil profile, setting the application depth to be at the bottom of the soil " \
                            f"profile."
        om.add_error(error_name, error_message, info_map)

    # </editor-fold>

    # <editor-fold desc="--- Scheduling Methods ---">
    def _check_crop_planting_schedule(self, time) -> None:
        """
        Checks the list of PlantingEvents, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.

        """
        self.planting_events, todays_planting_events = self._filter_events(self.planting_events, time)
        for event in todays_planting_events:
            self._plant_crop(event.crop_reference, event.use_heat_scheduled_harvest, time)

    def _check_fertilizer_application_schedule(self, time) -> None:
        """
        Checks list of FertilizerEvents, and removes all that occur on the current day from the list.

        Parameters
        ----------
        time : Time
            Object containing the current year and day of the simulation.

        """
        self.fertilizer_events, todays_fertilizer_events = self._filter_events(self.fertilizer_events, time)
        for event in todays_fertilizer_events:
            self._execute_fertilizer_application(event.mix_name, event.nitrogen_mass, event.phosphorus_mass,
                                                 event.depth, event.surface_remainder_fraction, event.year, event.day)

    def _check_tillage_schedule(self, time) -> None:
        """
        Checks the list of Events, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.
        """
        self.tillage_events, todays_events = self._filter_events(self.tillage_events, time)
        for event in todays_events:
            self.tiller.till_soil(event.tillage_depth, event.incorporation_fraction, event.mixing_fraction,
                                  time.calendar_year, time.day)

    def _check_manure_application_schedule(self, time) -> None:
        """
        Checks list of ManureEvents, sends all that occur today to another method to be executed.

        Parameters
        ----------
        time : Time
            Object containing the current year and day of the simulation.

        """
        self.manure_events, todays_manure_events = self._filter_events(self.manure_events, time)
        for event in todays_manure_events:
            self._execute_manure_application(event.nitrogen_mass, event.phosphorus_mass, event.manure_type,
                                             event.field_coverage, event.application_depth,
                                             event.surface_remainder_fraction, event.year, event.day)

    def _check_crop_harvest_schedule(self, time: Time, current_conditions: CurrentDayConditions) -> None:
        """
        Checks for all crops for potential harvests that may happen on the current day.

        Parameters
        ----------
        time : Time
            Time object containing the current day and year of the simulation.
        current_conditions : CurrentDayConditions
            CurrentDayConditions object containing the current weather conditions of the simulated day.

        Notes
        -----
        This method checks for scheduled harvests, i.e. checks all the remaining HarvestEvents. It calls the method that
        checks if crops should be harvested based on their heat fraction.

        """
        self.harvest_events, todays_harvest_events = self._filter_events(self.harvest_events, time)
        for event in todays_harvest_events:
            self._harvest_crop(event.crop_reference, event.operation, time, current_conditions)

        self._harvest_heat_scheduled_crops(current_conditions.rainfall, time)

    def _harvest_heat_scheduled_crops(self, rainfall: float, time: Time) -> None:
        """
        Checks if any of the active plants in the field are harvested based on their heat schedule, and if so harvests
        them if they meet the heat threshold.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).

        References
        ----------
        SWAT Theoretical documentation section 5:1.1.1 (Heat Scheduling)

        """
        for crop in self.crops:
            execute_heat_scheduled_harvest = crop.data.use_heat_scheduling and \
                                             crop.data.heat_fraction >= crop.data.harvest_heat_fraction
            if execute_heat_scheduled_harvest:
                crop.crop_management.manage_harvest(
                    HarvestOperation.HARVEST_ONLY,
                    self.field_data.name,
                    self.field_data.field_size,
                    time,
                    self.soil.data,
                    self.feed_manager
                )
                self.soil.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)

    @staticmethod
    def _filter_events(all_events: List[Event], time) -> Tuple[List[Event], List[Event]]:
        """
        Filters out all events from a list that occur on the current day, and creates a new list with all the events
        that were filtered out.

        Parameters
        ----------
        all_events : List[Event]
            List of all Events that will occur over the run of the simulation in this field.
        time : Time
            Object containing the current day and year of the simulation.

        Returns
        -------
        Tuple
            A tuple containing the list of all Events that will occur in this field after the current day, and a list of
            Events that will occur on the current day.

        Notes
        -----
        This method is written to work with generic Events so that it may be used on all the different child classes of
        Event: PlantingEvent, HarvestEvent, ManureEvent, FertilizerEvent, and TillageEvent.

        """
        todays_events = []
        remaining_events = []
        for event in all_events:
            if event.occurs_today(time):
                todays_events.append(event)
            else:
                remaining_events.append(event)
        return remaining_events, todays_events

    # </editor-fold>

    # <editor-fold desc="--- Crop Management Methods ---">
    def _plant_crop(self, crop_reference: str, use_heat_scheduled_harvesting: bool, time) -> None:
        """
        Takes the information necessary to plant a crop, creates a new Crop based on it, then adds it to the field's
        list of current crops.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        time : Time
            Object containing the current year and day of the simulation.

        Raises
        ------
        KeyError
            If the crop reference is to a custom crop specification, but that specification is not present in the list
            of custom crop specifications.

        Notes
        -----
        The crop reference may contain a reference to a supported crop that already has attributes defined for it, or a
        reference to a custom crop that has user-defined attributes. This method starts by trying to determine if the
        crop is of a supported species, if so it passes it to the supported crop creation method. If not, it passes it
        to the custom crop creation method.

        The harvest method is overwritten for the crop created because that is specified directly by the user, and the
        crop id is set so that the HarvestEvents will be able to identify the correct crop in the field's list of active
        crops.

        """
        supported_species = set(item.value for item in CropSpecies)
        if crop_reference in supported_species:
            crop = self._make_supported_crop(crop_reference)
        else:
            try:
                crop_specifications = copy(self.custom_crop_specifications[crop_reference])
            except KeyError:
                raise KeyError(f"'{self.field_data.name}': expected to have crop specification for '{crop_reference}', "
                               f"received specifications for '{tuple(self.custom_crop_specifications.keys())}' crop "
                               f"types.")
            crop = self._make_crop_from_config_dict(crop_specifications)
        crop.data.use_heat_scheduling = use_heat_scheduled_harvesting
        crop.data.id = crop_reference
        crop.data.planting_year = time.calendar_year
        crop.data.planting_day = time.day

        self.crops.append(crop)

        self._record_planting(crop_reference, use_heat_scheduled_harvesting, crop.data.species, time.calendar_year,
                              time.day)

    def _record_planting(self, crop_reference: str, heat_scheduled_harvest: bool, species: str, year: int,
                         day: int) -> None:
        """
        Records a planting event to the OutputManager.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be planted.
        heat_scheduled_harvest : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        species : str
            Name of the species of the crop being planted.
        year : int
            Year in which this crop planting occurs.
        day : int
            Julian day on which this crop planting occurs.

        """
        info_map = {"class": self.__class__.__name__, "function": self._plant_crop.__name__,
                    "prefix": f"field='{self.field_data.name}'", "field_size": self.field_data.field_size,
                    "species": species}
        value = {"crop_reference": crop_reference, "heat_scheduled_harvest": heat_scheduled_harvest,
                 "date": {"year": year, "day": day}}
        om.add_variable("crop_planting", value, info_map)

    def _harvest_crop(self, crop_reference: str, harvest_operation: HarvestOperation, time: Time,
                      current_conditions: CurrentDayConditions) -> None:
        """
        Performs the specified crop operation on the specified crop.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be harvested.
        harvest_operation : HarvestOperation
            Harvest operation to be performed on the referenced crop.
        time : Time
            Object containing the current day and year of the simulation.
        current_conditions : CurrentDayConditions
            Object containing the conditions of the current simulated day.

        Notes
        -----
        This method raises two different warnings, one if multiple active crops share the same id, and one if no active
        crop is found with an id that matches the given crop reference. These are both raised as warnings and not errors
        (which would stop the simulation run) because they could both plausibly happen in a simulation run. The first
        scenario could happen if someone were to specify multiple plantings of the same crop in the same year and
        schedule them to be harvested together, and the second could happen if there was a catastrophic weather event
        that killed off a crop before it could be harvested.

        """
        crops_to_be_harvested = [crop for crop in self.crops if crop.data.id == crop_reference]

        info_map = {"class": self.__class__.__name__, "function": self._harvest_crop.__name__,
                    "prefix": f"field_name:'{self.field_data.name}'",
                    "date": {"day": time.day, "year": time.calendar_year}}
        if len(crops_to_be_harvested) > 1:
            om.add_warning("harvest_warning", "Multiple crops to be harvested by single HarvestEvent.", info_map)
        elif len(crops_to_be_harvested) < 1:
            om.add_warning("harvest_warning", "No crop found to be harvested by a HarvestEvent.", info_map)

        for crop in crops_to_be_harvested:
            crop.crop_management.manage_harvest(harvest_operation, self.field_data.name,
                                                self.field_data.field_size, time, self.soil.data, self.feed_manager)
            self.soil.carbon_cycling.residue_partition.add_residue_to_pools(current_conditions.rainfall)

    def _remove_dead_crops(self) -> None:
        """
        This method removes any crops from the field's list of active crops if they are no longer alive.
        """
        self.crops = [crop for crop in self.crops if crop.data.is_alive]

    def _reset_crop_field_coverage_fractions(self) -> None:
        """
        Resets crops to have equal field coverage while in the field.
        """
        number_of_crops_in_field = len(self.crops)
        if number_of_crops_in_field == 0:
            return

        field_coverage_fraction = 1 / number_of_crops_in_field
        for crop in self.crops:
            crop.data.field_proportion = field_coverage_fraction

    @staticmethod
    def _make_crop_from_config_dict(config: Dict) -> Crop:
        """
        Initialize a new crop from a configuration dictionary.

        Parameters
        ----------
        config : dict
            A dictionary containing specifications for the crop to be initialized.

        Details
        -------
        If the "species" key is present in the dictionary, that value is checked against the supported
        crop species. If it is supported, that supported crop is initialized. Otherwise, a custom crop is
        created (with 'custom' prepended to the species name, if given).

        Returns
        -------
        Crop
            A Crop object initialized with the desired attribute values.
        """
        if "species" in config.keys():
            accepted_species = set(item.value for item in CropSpecies)
            species = config.pop("species")

            if species in accepted_species:
                return Field._make_supported_crop(species=species, **config)
            else:
                config["species"] = "custom " + str(species)

        return Field._make_custom_crop(**config)

    @staticmethod
    def _make_supported_crop(species: str, **specs) -> Crop:
        """
        Create a crop instance with attributes determined by the species of the crop.

        Parameters
        ----------
        species : str
            One of the supported species.
        **specs : optional
            An optional set of keyword arguments passed to CropSpeciesDataFactory to customize the crop species.

        Details
        -------
        Species attributes are read from species configuration files/classes. This method of creating a crop
        does not allow for customizing crop values. It is limited to creating the default crops supported by the
        CropSpecies Enum.

        Returns
        -------
        Crop
            A Crop object initialized with the desired attribute values.
        """

        crop_species = CropSpecies(species)
        crop_data = CropSpeciesDataFactory.create_species_data(crop_species, **specs)
        return Crop(crop_data)

    @staticmethod
    def _make_custom_crop(**specs) -> Crop:
        """creates a crop instance with customized attributes.

        Args:
            **specs: an optional set of arguments, passed to CropSpeciesDataFactory that customize the
              crop species

        Details, this can be used to create a new ('unsupported') crop species/type
        """
        crop_data = CropData(**specs)
        return Crop(crop_data)

    def _assess_dormancy(self, daylength: float, rainfall: float) -> None:
        """
        Transition all crops to dormancy if they are capable of going dormant.

        Parameters
        ----------
        daylength : float
            Length of time from sunup to sundown on the current day (hours).
        rainfall : float
            Amount of rain that fell on the current day (mm).

        Notes
        -----
        If the length of the current day is at or below the dormancy threshold length, all crops that can go dormant
        should be put into dormancy. If the length is greater than the threshold length, all crops should be brought out
        of dormancy.

        """

        if daylength <= self.field_data.dormancy_threshold_daylength:
            for crop in self.crops:
                crop.dormancy.enter_dormancy(self.soil.data)
                crop.biomass_allocation.partition_biomass()
                self.soil.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)
        else:
            for crop in self.crops:
                crop.data.is_dormant = False

    # </editor-fold>

    # <editor-fold desc="--- Field-level Methods ---">
    def _execute_daily_processes(self, current_conditions: CurrentDayConditions, time) -> None:
        """Executes all daily updates on this field's soil and crop objects.

        Parameters
        ----------
        current_conditions : CurrentDayConditions
            Object containing the environment conditions on this day.
        time : Time
            Object containing the current year and day of the simulation.

        Notes
        -----
        This method is designed to make it easier to change the order of process execution, which is desirable because
        it will allow subject-matter experts to more easily experiment with different orders.

        """
        self.soil.snow.update_snow(current_day_conditions=current_conditions, day=time.day)

        total_plant_cover = self.field_data.current_residue + self._determine_total_above_ground_biomass()
        self.soil.soil_temp.daily_soil_temperature_update(current_conditions.incoming_light,
                                                          current_conditions.mean_air_temperature,
                                                          current_conditions.min_air_temperature,
                                                          current_conditions.max_air_temperature,
                                                          total_plant_cover,
                                                          self.soil.data.snow_content,
                                                          current_conditions.annual_mean_air_temperature)

        self._cycle_water(current_conditions, time)

        for crop in self.crops:
            if crop.data.is_mature or crop.data.is_dormant:
                continue

            crop.heat_units.absorb_heat_units(current_conditions.mean_air_temperature,
                                              current_conditions.min_air_temperature,
                                              current_conditions.max_air_temperature)
            crop.root_development.develop_roots()
            crop.nitrogen_incorporation.incorporate_nitrogen(self.soil.data)
            crop.phosphorus_incorporation.incorporate_phosphorus(self.soil.data)
            crop.growth_constraints.constrain_growth(crop.data.max_transpiration,
                                                     current_conditions.mean_air_temperature)
            crop.leaf_area_index.grow_canopy()
            crop.biomass_allocation.allocate_biomass(current_conditions.incoming_light)

    def _cycle_water(self, current_conditions: CurrentDayConditions, time):
        """
        Allow water to cycle through the field.

        Parameters
        ----------
        current_conditions : CurrentDayConditions
            A CurrentDayConditions object containing a collection of today's weather variables needed for field
            processes.
        time : Time
            An object containing the current year and day of the simulation.

        Notes
        -----
        This method executes all water-related processes that occur within Crop and Soil objects. Having a
        separate method to handle water processes altogether is necessary because processes that affect water in the
        soil are dependent on processes that affect water in crops and vice versa. The most complex process that is
        executed in this method is evapotranspiration, which is executed in the following order:

            - Evaporation of water in canopies of crops.
            - Sublimation of water in the snowpack (not implemented in V1).
            - Evaporation from the soil profile.
            - Transpiration from crops (the amount of water taken up by plants is equal to the amount they transpirate,
              and this amount depends on the evapotranspirative demand after water has been removed from canopies).

        It should also be noted that while this method is more messy and complex than it could be, this is a
        conscious design choice that will allow for SMEs to more easily and freely experiment with different orders
        of processes. This is necessary because there is not necessarily one correct order for processes to run in.

        """
        watering_amount = self._determine_watering_amount(rainfall=current_conditions.rainfall, year=time.year,
                                                          day=time.day, irrigation=current_conditions.irrigation)
        total_precipitation = current_conditions.rainfall + watering_amount
        precipitation_reaching_soil = self._handle_water_in_crop_canopies(total_precipitation)
        water_reaching_soil = precipitation_reaching_soil + self.soil.data.snow_melt_amount

        full_evapotranspirative_demand = self._determine_potential_evapotranspiration(
            current_conditions.incoming_light, current_conditions.max_air_temperature,
            current_conditions.min_air_temperature, current_conditions.mean_air_temperature)
        self.field_data.max_evapotranspiration = full_evapotranspirative_demand

        remaining_evapotranspirative_demand = self._evaporate_from_crop_canopies(full_evapotranspirative_demand)

        self.soil.infiltration.infiltrate(water_reaching_soil)
        self.soil.percolation.percolate(self.field_data.seasonal_high_water_table)
        self.soil.soil_erosion.erode(self.field_data.field_size, 0.02, self.field_data.current_residue,
                                     total_precipitation)
        self.soil.phosphorus_cycling.cycle_phosphorus(water_reaching_soil, self.soil.data.accumulated_runoff,
                                                      self.field_data.field_size,
                                                      current_conditions.mean_air_temperature)
        self.soil.carbon_cycling.cycle_carbon(water_reaching_soil, current_conditions.mean_air_temperature,
                                              self.field_data.field_size)
        self.soil.nitrogen_cycling.cycle_nitrogen(self.field_data.field_size)

        weighted_transpiration_total = 0.0
        weights_sum = 0.0
        for crop in self.crops:
            crop.water_dynamics.set_maximum_transpiration(remaining_evapotranspirative_demand)
            weighted_transpiration_total += crop.data.max_transpiration * crop.data.field_proportion
            weights_sum += crop.data.field_proportion

        if weights_sum == 0.0:
            weighted_average_transpiration = 0.0
        else:
            weighted_average_transpiration = weighted_transpiration_total / weights_sum

        above_ground_biomass = self._determine_total_above_ground_biomass()

        soil_evaporation_and_sublimation_amount = self._determine_soil_evaporation_and_sublimation_adjusted(
            above_ground_biomass, self.soil.data.plant_surface_residue, self.soil.data.snow_content,
            remaining_evapotranspirative_demand, weighted_average_transpiration)

        self.soil.snow.sublimate(soil_evaporation_and_sublimation_amount)
        soil_evaporation_and_sublimation_amount -= self.soil.data.water_sublimated
        remaining_evapotranspirative_demand -= self.soil.data.water_sublimated
        self.soil.evaporation.evaporate(soil_evaporation_and_sublimation_amount)
        remaining_evapotranspirative_demand -= self.soil.data.water_evaporated

        actual_evaporation = full_evapotranspirative_demand - remaining_evapotranspirative_demand

        for crop in self.crops:
            if crop.data.in_growing_season:
                crop.water_uptake.uptake_water(self.soil.data)
                crop.water_dynamics.cycle_water(actual_evaporation, crop.data.water_uptake,
                                                full_evapotranspirative_demand)
            else:
                crop.data.cumulative_evaporation = 0.0
                crop.data.cumulative_transpiration = 0.0
                crop.data.cumulative_potential_evapotranspiration = 0.0
                crop.data.cumulative_water_uptake = 0.0

    def _determine_watering_amount(self, rainfall: float, year: int, day: int, irrigation: float) -> float:
        """Manages watering of the field.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall that occurs on this day (mm)
        year : int
            Year in which this watering occurs.
        day : int
            Julian day on which this watering occurs.
        irrigation : float
            The amount of hard-coded irrigation in the weather data (mm)

        Returns
        -------
        float
            Amount of water used to irrigate the field on this day (mm)

        Notes
        -----
        This method drives the engine of irrigation for RuFaS. It tracks how much water has been added to the field by
        rainfall over a user-defined interval, and when at the end of the interval it determines how much water still
        needs to be added to the field based on how much watering has to occur over said interval (also defined by the
        user). The counter that tracks how where in the interval the simulation is and the amount of water that still
        needs to be applied are reset at the end of every interval. The water that is added to the field from the farm's
        resources is tracked on an annual basis, so that water budgeting may be accurately predicted.

        Old method of using hard-coded irrigation data will be used if there's no user specified data. If there's any
        user-specified data provided, the hard-coded irrigation will be ignored and only uses the new method.

        """
        if self.field_data.watering_occurs:
            self.field_data.current_water_deficit -= rainfall
            self.field_data.current_water_deficit = max(0.0, self.field_data.current_water_deficit)

            if self.field_data.days_into_watering_interval == self.field_data.watering_interval:
                self.field_data.days_into_watering_interval = 0
                water_applied_this_interval = self.field_data.current_water_deficit
                self.field_data.current_water_deficit = self.field_data.watering_amount_in_mm
                self.field_data.annual_irrigation_water_use_total += water_applied_this_interval
                self._record_field_watering(year=year, day=day, watering_amount=water_applied_this_interval)
                return water_applied_this_interval
            self.field_data.days_into_watering_interval += 1
            return 0.0
        elif not self.field_data.watering_occurs and irrigation > 0:
            self.field_data.annual_irrigation_water_use_total += irrigation
            self._record_field_watering(year=year, day=day, watering_amount=irrigation)
            return irrigation
        else:
            return 0.0

    def _handle_water_in_crop_canopies(self, precipitation_total: float) -> float:
        """Adds water to canopies of all the crops in the field and removes any excess water from them.

        Parameters
        ----------
        precipitation_total : float
            Total amount of precipitation that fell on the field today (mm)

        Returns
        -------
        float
            Amount of water that reaches the soil surface (mm)

        Notes
        -----
        This method accounts for the edge case that no water was lost from the crop canopy yesterday and the capacity in
        the canopy went down overnight, so water is lost from the canopy to the ground before any evapotranspiration can
        happen. A caveat is that if there is excess water in the canopy of one crop, it cannot be transferred to the
        canopy of another.

        """
        precipitation_reaching_soil = precipitation_total
        excess_canopy_water = 0
        for crop in self.crops:
            canopy_water_excess_capacity = crop.data.water_canopy_storage_capacity - crop.data.canopy_water

            excess_water_in_canopy = min(0.0, canopy_water_excess_capacity)
            excess_canopy_water += -1 * excess_water_in_canopy
            if excess_water_in_canopy != 0.0:
                crop.data.canopy_water = crop.data.water_canopy_storage_capacity

            water_taken_to_be_stored = max(0.0, canopy_water_excess_capacity)
            water_taken_to_be_stored = min(precipitation_reaching_soil, water_taken_to_be_stored)
            crop.data.canopy_water += water_taken_to_be_stored
            precipitation_reaching_soil -= water_taken_to_be_stored

        return precipitation_reaching_soil + excess_canopy_water

    def _evaporate_from_crop_canopies(self, evapotranspirative_demand: float) -> float:
        """Evaporates water from crops' canopies and reduces evapotranspirative demand accordingly.

        Parameters
        ----------
        evapotranspirative_demand : float
            Evapotranspirative demand on the field on the current day (mm)

        Returns
        -------
        float
            Evapotranspirative demand after evaporating water from crops' canopies (mm)

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.1

        Notes
        -----
        This method iterates through the crops in the field, for each determines how much water was evaporated from its
        canopy, then reduces the evapotranspirative demand by that amount. If the remaining evapotranspirative demand
        reaches 0, then no more water should be evaporated so the method stops running.

        """
        remaining_evapotranspirative_demand = evapotranspirative_demand
        for crop in self.crops:
            amount_evaporated = crop.water_dynamics.evaporate_from_canopy(remaining_evapotranspirative_demand)
            remaining_evapotranspirative_demand -= amount_evaporated
            if remaining_evapotranspirative_demand == 0.0:
                break
        return remaining_evapotranspirative_demand

    def _determine_total_above_ground_biomass(self) -> float:
        """Calculate the total amount of above-ground biomass still on the plant(s) in the field (kg / ha)"""
        total_above_ground_biomass = 0
        for crop in self.crops:
            total_above_ground_biomass += crop.data.above_ground_biomass
        return total_above_ground_biomass

    @staticmethod
    def _determine_potential_evapotranspiration(extraterrestrial_radiation: float, max_air_temp: float,
                                                min_air_temp: float, avg_air_temp: float) -> float:
        """Calculates the potential evapotranspiration for a given day.

        Parameters
        ----------
        extraterrestrial_radiation : float
            Radiation from sunlight (MJ per square meter per day).
        max_air_temp : float
            Maximum air temperature (degrees C).
        min_air_temp : float
            Minimum air temperature (degrees C).
        avg_air_temp : float
            Average air temperature (degrees C).

        Returns
        -------
        float
            Potential evapotranspiration (mm).

        References
        ----------
        SWAT Reference: 2:2.2.24

        Notes
        -----
        This method calculates the evapotranspirative demand for the entire field on any given day using the Hargreaves
        method. This method lower-bounds the potential evapotranspiration at 0.0 mm.

        If the average temperature for the day is not specified, then the average temperature for the day is calculated
        as the average of the maximum and minimum temperatures of the day.

        """
        avg_air_temp = avg_air_temp if avg_air_temp else (max_air_temp + min_air_temp) / 2
        latent_heat_vaporization = Field._determine_latent_heat_vaporization(avg_air_temp)
        potential_evapotranspiration = (0.0023 * extraterrestrial_radiation * ((max_air_temp - min_air_temp) ** 0.5)
                                        * (avg_air_temp + 17.8)) / latent_heat_vaporization
        return max(0.0, potential_evapotranspiration)

    @staticmethod
    def _determine_latent_heat_vaporization(avg_air_temp: float) -> float:
        """Determine latent heat of vaporization for a given day.

        Parameters
        ----------
        avg_air_temp : float
            Average air temperature (degrees C)

        Returns
        -------
        float
            latent heat of vaporization (MJ per kg)

        References
        ----------
        SWAT Reference: 1:2.3.6

        """
        return 2.501 - ((2.361 * (10 ** (-3))) * avg_air_temp)

    @staticmethod
    def _determine_soil_evaporation_and_sublimation_adjusted(above_ground_biomass: float, residue: float,
                                                             snow_water_content: float,
                                                             potential_evapotranspiration_adjusted: float,
                                                             transpiration: float) -> float:
        """Calculate the amount of sublimation and soil evaporation for this day, adjusted for plant use.

        Parameters
        ----------
        above_ground_biomass : float
            Mass of plant above ground (kg per hectare)
        residue : float
            Biomass separated from plant on the ground (kg per hectare)
        snow_water_content : float
            Amount of water in the snow pack (mm)
        potential_evapotranspiration_adjusted : float
            Potential evapotranspiration adjusted for evaporation of free water in canopy (mm)
        transpiration : float
            Maximum transpiration for a given day (mm)

        Returns
        -------
        float
            Soil evaporation and sublimation, adjusted for plant water use (mm)

        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.3.7, 9

        Notes
        -----
        If both the adjusted potential evapotranspiration and transpiration are 0, then it is assumed that all
        evapotranspirative demands have been met for the current day and no sublimation or evaporation from the soil
        will occur.

        """
        if potential_evapotranspiration_adjusted == transpiration == 0.0:
            return 0.0

        soil_cover_index = Field._determine_soil_cover_index(above_ground_biomass, residue, snow_water_content)
        max_soil_evaporation_sublimation = potential_evapotranspiration_adjusted * soil_cover_index
        adjusted_soil_evaporation_sublimation = \
            (max_soil_evaporation_sublimation * potential_evapotranspiration_adjusted) / \
            (max_soil_evaporation_sublimation + transpiration)
        actual_soil_evaporation_sublimation = min(max_soil_evaporation_sublimation,
                                                  adjusted_soil_evaporation_sublimation)
        return actual_soil_evaporation_sublimation

    @staticmethod
    def _determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water_content: float) -> float:
        """Calculate the soil cover index.

        Parameters
        ----------
        above_ground_biomass : float
            Mass of plant above ground (kg per hectare).
        residue : float
            Biomass separated from plant on the ground (kg per hectare).
        snow_water_content : float
            Amount of water from snow (mm).

        Returns
        -------
        Float
            Soil cover index (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 2:2.3.8

        """
        if snow_water_content > 0.5:
            return 0.5
        else:
            return exp((-5.0 * (10 ** (-5))) * (above_ground_biomass + residue))
    # </editor-fold>

    # <editor-fold desc="--- Annual Reset Methods ---">
    def perform_annual_reset(self) -> None:
        """Collect all annual accumulated totals from Field, Crop, and Soil modules, write them to some sort of output
            file, and then reset all annual totals"""
        self.soil.data.do_annual_reset()
        self.field_data.perform_annual_field_reset()
        return

    def _record_field_watering(self, year: int, day: int, watering_amount: float) -> None:
        """Record the day, year and amount of irrigation

        Parameters
        ----------
        year : int
            Year in which this watering occurs.
        day : int
            Julian day on which this watering occurs.
        watering_amount : float
            The amount of hard-coded irrigation in the weather data (mm)

        Returns
        -------
        None
        """
        info_map = {"class": self.__class__.__name__, "function": self._record_field_watering.__name__,
                    "prefix": f"field='{self.field_data.name}'", "date": {"year": year, "day": day},
                    "field_size": self.field_data.field_size, "units": "mm"}
        om.add_variable("field_watering", watering_amount, info_map)

    # </editor-fold>
