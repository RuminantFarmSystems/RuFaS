import math
from math import exp
from typing import Dict, List, Optional, Sequence

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.events import (
    BaseFieldManagementEvent,
    FertilizerEvent,
    HarvestEvent,
    ManureEvent,
    PlantingEvent,
    TillageEvent,
)
from RUFAS.data_structures.manure_supplement_methods import ManureSupplementMethod
from RUFAS.data_structures.manure_to_crop_soil_connection import (
    ManureEventNutrientRequest,
    ManureEventNutrientRequestResults,
    NutrientRequest,
    NutrientRequestResults,
)
from RUFAS.data_structures.manure_types import ManureType
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.crop.crop import Crop
from RUFAS.biophysical.field.crop.harvest_operations import HarvestOperation
from RUFAS.biophysical.field.field.fertilizer_application import FertilizerApplication
from RUFAS.biophysical.field.field.field_data import FieldData
from RUFAS.biophysical.field.field.manure_application import ManureApplication
from RUFAS.biophysical.field.field.tillage_application import TillageApplication
from RUFAS.biophysical.field.soil.soil import Soil
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class Field:
    """
    This is a high-level class that represents and simulates an entire field. It is responsible for executing the daily
    biophysical routines which take place in soil columns and in crops planted in the field. It is also responsible for
    the management of schedules, executing, and reporting of farm management events,
    including planting and harvesting crops, adding manure and fertilizer to the soil, and tilling the soil.

    Parameters
    ----------
    field_data : FieldData, default=None
        FieldData object that will be simulated.
    soil : Soil, default=None
        The soil component of the field.
    plantings : List[PlantingEvent], default=None
        List of all planting events that will occur over the run of the simulation in this field.
    harvestings : List[HarvestEvent], default=None
        List of all harvesting events that will occur over the run of the simulation in the field.
    custom_crop_specifications : dict[str, dict[str, Any]], default=None
        Dictionary where keys are crop references and values are dictionaries containing crop specifications.
    tillage_events : List[TillageEvent], default=None
        List of all tillage events that will occur over the run of the simulation in this field.
    fertilizer_events : List[FertilizerEvent], default=None
        List of all fertilizer mixes available for application to this field.
    fertilizer_mixes : Dict[str, Dict[str, float]], default=None
        List of all fertilizer mixes available for application to this field.
    manure_events : List[ManureEvent], default=None
        Manure application interface.

    Attributes
    ----------
    field_data : FieldData
        Reference to the FieldData object
    soil : Soil
        Reference to the Soil object
    crops : List[Crop]
        Reference to the list of Crop objects
    planting_events : List[PlantingEvent]
        Reference to the list of PlantingEvent objects
    harvest_events : List[HarvestEvent]
        Reference to the list of HarvestEvent objects
    custom_crop_specifications : dict[str, dict[str, Any]]
        Reference to the custom crop specifications dictionary.
    fertilizer_applicator : FertilizerApplication(self.soil)
        Provides interface for adding fertilizer to the field
    fertilizer_events : List
        Reference to the list of FertilizerEvent objects
    available_fertilizer_mixes : Dict
        List of all fertilizer mixes available for application to this field. The 100_0_0 and 26_4_24 mixes will
        always be available as supplements to unfulfilled manure nutrient demands.
    ONLY_NITROGEN_MIX : str
        Constant with the name of the fertilizer mix that contains only Nitrogen.
    tiller : TillageApplication
        Provides interface to till the field.
    tillage_events: List[TillageEvent]
        List of all tillage events that will occur over the run of the simulation in this field.
    manure_applicator = ManureApplication
        List of ManureApplication objects.
    manure_events: List[ManureEvent]
        List of all manure applications that will be applied to this field.

    Methods
    -------
    manage_field(time, current_conditions: CurrentDayConditions) -> list[HarvestedCrop]:
        Main Field routine, runs all subroutines routines based on current attribute configuration.

    """

    def __init__(
        self,
        field_data: Optional[FieldData] = None,
        soil: Optional[Soil] = None,
        plantings: Optional[List[PlantingEvent]] = None,
        harvestings: Optional[List[HarvestEvent]] = None,
        tillage_events: Optional[List[TillageEvent]] = None,
        fertilizer_events: Optional[List[FertilizerEvent]] = None,
        fertilizer_mixes: Optional[Dict[str, Dict[str, float]]] = None,
        manure_events: Optional[List[ManureEvent]] = None,
    ) -> None:
        # field-wide attributes
        self.om = OutputManager()
        self.field_data = field_data or FieldData()

        # soil attributes
        self.soil = soil or Soil(soil_data=None, field_size=self.field_data.field_size)  # default soil if not given.

        # crop attributes
        self.crops: list[Crop] = list()  # empty crop list

        self.planting_events: list[PlantingEvent] = plantings or []

        self.harvest_events: list[HarvestEvent] = harvestings or []

        # Soil amendment attributes
        self.fertilizer_applicator = FertilizerApplication(self.soil)

        self.fertilizer_events = fertilizer_events or []

        self.available_fertilizer_mixes = fertilizer_mixes or {}
        self.available_fertilizer_mixes["100_0_0"] = {"N": 1.0, "P": 0.0, "K": 0.0, "ammonium_fraction": 0.0}
        self.available_fertilizer_mixes["26_4_24"] = {"N": 0.26, "P": 0.04, "K": 0.24, "ammonium_fraction": 0.0}

        self.ONLY_NITROGEN_MIX = "100_0_0"
        self.tiller = TillageApplication(self.field_data, self.soil.data)

        self.tillage_events: list[TillageEvent] | None = tillage_events

        self.manure_applicator = ManureApplication(self.soil.data)

        self.manure_events: list[ManureEvent] = manure_events or []

    def manage_field(
        self,
        time: RufasTime,
        current_conditions: CurrentDayConditions,
        manure_applications: list[ManureEventNutrientRequestResults],
    ) -> list[HarvestedCrop]:
        """
        Main Field routine, runs all subroutines routines based on current attribute configuration.

        Parameters
        ----------
        time : RufasTime
            Contains the current year and day that the simulation is on.
        current_conditions : CurrentDayConditions
            Contains a collection of today's conditions variables needed for field processes.
        manure_applications : list[ManureEventNutrientRequestResults]
            List of manure events and the results of the nutrient requests for each event.

        Returns
        -------
        list[HarvestedCrop]
            List of crops that have been harvested from the field.

        Notes
        -----
        This method starts by executing any soil amendments that may be scheduled for the day. Then it executes the
        daily update routines for the soil profile and active crops in the field. It then plants and/or harvests crops,
        checks if active crops need to go into dormancy, and resets crop attributes in both the crops and in the field's
        data object.

        """
        # --- Soil Management---
        self._check_fertilizer_application_schedule(time)

        for manure_application in manure_applications:
            manure_event = manure_application.event
            manure_request_results = manure_application.nutrient_request_results
            self._execute_manure_application(
                requested_nitrogen=manure_event.nitrogen_mass,
                requested_phosphorus=manure_event.phosphorus_mass,
                requested_manure_type=manure_event.manure_type,
                field_coverage=manure_event.field_coverage,
                application_depth=manure_event.application_depth,
                surface_remainder_fraction=manure_event.surface_remainder_fraction,
                year=manure_event.year,
                day=manure_event.day,
                manure_supplied=manure_request_results,
                manure_supplement_method=manure_event.manure_supplement_method,
            )

        self._check_tillage_schedule(time)

        # --- Whole-Field Methods ---
        # Allow non-management field processes (water/nutrient cycling) to occur
        self._execute_daily_processes(current_conditions, time)
        # ... Other ...

        # --- Crop Management ---
        self._assess_dormancy(current_conditions.daylength, current_conditions.rainfall)

        self._check_crop_planting_schedule(time)

        harvested_crops: list[HarvestedCrop] = self._check_crop_harvest_schedule(time, current_conditions)

        self._remove_dead_crops()
        self._reset_crop_field_coverage_fractions()

        return harvested_crops

    # <editor-fold desc="--- Soil Management Methods ---">
    def _execute_fertilizer_application(
        self,
        mix_name: str,
        requested_nitrogen: float,
        requested_phosphorus: float,
        requested_potassium: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ) -> None:
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
        requested_potassium : float
            Minimum amount of potassium to be included in this fertilizer application (kg).
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
        if requested_nitrogen == requested_phosphorus == requested_potassium == 0.0:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._execute_fertilizer_application.__name__,
                "suffix": f"field='{self.field_data.name}'",
                "year": year,
                "day": day,
            }
            log_message = "Tried to apply fertilizer with no nitrogen, phosphorus, or potassium requested."
            self.om.add_log("fertilizer_application_log", log_message, info_map)
            return

        invalid_depth_and_remainder_fraction = (application_depth == 0.0 and surface_remainder_fraction != 1.0) or (
            application_depth > 0.0 and surface_remainder_fraction == 1.0
        )
        error_message = "fertilizer_application_error"
        if invalid_depth_and_remainder_fraction:
            self._record_nutrient_application_error(
                application_depth, surface_remainder_fraction, error_message, year, day
            )
            application_depth = 0.0
            surface_remainder_fraction = 1.0

        if application_depth > self.soil.data.soil_layers[-1].bottom_depth:
            self._record_nutrient_application_error(application_depth, None, error_message, year, day)
            application_depth = self.soil.data.soil_layers[-1].bottom_depth

        try:
            fertilizer_mix = self.available_fertilizer_mixes[mix_name]
        except KeyError:
            raise KeyError(
                f"'{self.field_data.name}': expected to have fertilizer mix for '{mix_name}', "
                f"received '{self.available_fertilizer_mixes}'."
            )
        nitrogen_fraction = fertilizer_mix.get("N")
        phosphorus_fraction = fertilizer_mix.get("P")
        potassium_fraction = fertilizer_mix.get("K")
        ammonium_fraction = fertilizer_mix.get("ammonium_fraction")

        fertilizer_applied = self._formulate_fertilizer_required(
            nitrogen_fraction,
            phosphorus_fraction,
            potassium_fraction,
            requested_nitrogen,
            requested_phosphorus,
            requested_potassium,
        )
        total_mass_applied = fertilizer_applied.get("total_mass")
        phosphorus_applied = fertilizer_applied.get("phosphorus_mass")
        nitrogen_applied = fertilizer_applied.get("nitrogen_mass")
        potassium_applied = fertilizer_applied.get("potassium_mass")

        self.fertilizer_applicator.apply_fertilizer(
            phosphorus_applied,
            nitrogen_applied,
            ammonium_fraction,
            application_depth,
            surface_remainder_fraction,
            self.field_data.field_size,
        )

        self._record_fertilizer_application(
            mix_name,
            total_mass_applied,
            nitrogen_applied,
            phosphorus_applied,
            potassium_applied,
            ammonium_fraction,
            application_depth,
            surface_remainder_fraction,
            year,
            day,
        )

    @staticmethod
    def _determine_optimal_fertilizer_mix(
        requested_nitrogen: float,
        requested_phosphorus: float,
        available_mixes: Dict[str, Dict[str, float]],
    ) -> str:
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
            fertilizer_application = Field._formulate_fertilizer_required(
                mix_values["N"],
                mix_values["P"],
                mix_values["K"],
                requested_nitrogen,
                requested_phosphorus,
                0.0,
            )
            total_mass = fertilizer_application["total_mass"]
            if total_mass == 0.0:
                continue
            elif total_mass < least_fertilizer_mix_required:
                optimal_mix = mix_name
                least_fertilizer_mix_required = total_mass
        return optimal_mix

    @staticmethod
    def _formulate_fertilizer_required(
        nitrogen_fraction: float,
        phosphorus_fraction: float,
        potassium_fraction: float,
        requested_nitrogen: float,
        requested_phosphorus: float,
        requested_potassium: float,
    ) -> Dict[str, float]:
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
        requested_potassium : float
            Minimum mass of potassium to be included in fertilizer application (kg)

        Returns
        -------
        Dict[str, float]
            The total mass of fertilizer, and the masses of nitrogen, phosphorus, and potassium in the fertilizer.

        """
        minimum_mass_for_nitrogen = 0 if nitrogen_fraction == 0 else (requested_nitrogen / nitrogen_fraction)
        minimum_mass_for_phosphorus = 0 if phosphorus_fraction == 0 else (requested_phosphorus / phosphorus_fraction)
        minimum_mass_for_potassium = 0 if potassium_fraction == 0 else (requested_potassium / potassium_fraction)

        total_mass = max(minimum_mass_for_nitrogen, minimum_mass_for_phosphorus, minimum_mass_for_potassium)
        nitrogen_mass = total_mass * nitrogen_fraction
        phosphorus_mass = total_mass * phosphorus_fraction
        potassium_mass = total_mass * potassium_fraction
        return {
            "total_mass": total_mass,
            "nitrogen_mass": nitrogen_mass,
            "phosphorus_mass": phosphorus_mass,
            "potassium_mass": potassium_mass,
        }

    def _record_fertilizer_application(
        self,
        mix_name: str,
        total_mass: float,
        nitrogen_mass: float,
        phosphorus_mass: float,
        potassium_mass: float,
        ammonium_fraction: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ) -> None:
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
        ammonium_fraction : float
            Fraction of requested nitrogen which is ammonium and not nitrate (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which the fertilizer application is occurring.
        day : int
            Julian day on which this fertilizer application is occurring.

        """
        units = {
            "mass": MeasurementUnits.KILOGRAMS,
            "nitrogen": MeasurementUnits.KILOGRAMS,
            "phosphorus": MeasurementUnits.KILOGRAMS,
            "potassium": MeasurementUnits.KILOGRAMS,
            "ammonium_fraction": MeasurementUnits.UNITLESS,
            "application_depth": MeasurementUnits.MILLIMETERS,
            "surface_remainder_fraction": MeasurementUnits.UNITLESS,
            "year": MeasurementUnits.CALENDAR_YEAR,
            "day": MeasurementUnits.ORDINAL_DAY,
            "field_size": MeasurementUnits.HECTARE,
            "field_name": MeasurementUnits.UNITLESS,
            "average_clay_percent": MeasurementUnits.PERCENT,
        }
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_fertilizer_application.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "mix_name": mix_name,
            "units": units,
        }
        value = {
            "mass": total_mass,
            "nitrogen": nitrogen_mass,
            "phosphorus": phosphorus_mass,
            "potassium": potassium_mass,
            "ammonium_fraction": ammonium_fraction,
            "application_depth": application_depth,
            "surface_remainder_fraction": surface_remainder_fraction,
            "year": year,
            "day": day,
            "field_size": self.field_data.field_size,
            "field_name": self.field_data.name,
            "average_clay_percent": self.soil.data.average_clay_percent,
        }
        self.om.add_variable("fertilizer_application", value, info_map)

    def _execute_manure_application(
        self,
        requested_nitrogen: float,
        requested_phosphorus: float,
        requested_manure_type: ManureType,
        field_coverage: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
        manure_supplied: NutrientRequestResults | None,
        manure_supplement_method: ManureSupplementMethod,
    ) -> None:
        """
        Executes a manure application based on the requested amounts of nutrients.

        Parameters
        ----------
        requested_nitrogen : float
            Minimum amount of nitrogen to be included in this manure application (kg).
        requested_phosphorus : float
            Minimum amount of phosphorus to be included in this manure application (kg).
        requested_manure_type : ManureType
            Enum option indicating the type of manure applied.
        field_coverage : float
            Fraction of the field this manure is applied to (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.
        manure_supplied : NutrientRequestResults | None
            An object containing the information that defines a manure application.
        manure_supplement_method : ManureSupplementMethod
            Enum option indicating how to supplement the manure application.
        """
        if manure_supplied:
            application_summary = self._apply_and_record_manure_application(
                manure_supplied,
                requested_manure_type,
                field_coverage,
                application_depth,
                surface_remainder_fraction,
                year,
                day,
            )
        else:
            application_summary = {
                "supplied_nitrogen": 0.0,
                "supplied_phosphorus": 0.0,
                "application_depth": application_depth,
                "surface_remainder_fraction": surface_remainder_fraction,
            }

        self._record_manure_application(
            dry_matter_mass=0.0,
            dry_matter_fraction=0.0,
            field_coverage=field_coverage,
            nitrogen=requested_nitrogen,
            phosphorus=requested_phosphorus,
            potassium=None,
            application_depth=application_summary["application_depth"],
            surface_remainder_fraction=application_summary["surface_remainder_fraction"],
            year=year,
            day=day,
            output_name="manure_request",
        )

        self._handle_unmet_nutrients(
            requested_nitrogen,
            requested_phosphorus,
            application_summary["supplied_nitrogen"],
            application_summary["supplied_phosphorus"],
            application_summary["application_depth"],
            application_summary["surface_remainder_fraction"],
            manure_supplement_method,
            year,
            day,
        )

    def _apply_and_record_manure_application(
        self,
        manure_supplied: NutrientRequestResults,
        manure_type: ManureType,
        field_coverage: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ) -> dict[str, float]:
        """
        Applies the manure and records the application.

        Parameters
        ----------
        manure_supplied : NutrientRequestResults
            An object containing the information that defines a manure application.
        manure_type : ManureType
            Enum option indicating the type of manure applied.
        field_coverage : float
            Fraction of the field this manure is applied to (unitless).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.

        Returns
        -------
        tuple[float, float, float, float]
            The supplied nitrogen and phosphorus amounts, application depth, and surface remainder fraction.
        """
        self._add_manure_water(manure_supplied, manure_type)

        supplied_nitrogen = manure_supplied.nitrogen
        supplied_phosphorus = manure_supplied.phosphorus

        application_depth, surface_remainder_fraction = self._validate_application_depth_and_fraction(
            application_depth, surface_remainder_fraction, year, day
        )

        self.manure_applicator.apply_machine_manure(
            dry_matter_mass=manure_supplied.dry_matter,
            dry_matter_fraction=manure_supplied.dry_matter_fraction,
            total_phosphorus_mass=supplied_phosphorus,
            field_coverage=field_coverage,
            application_depth=application_depth,
            surface_remainder_fraction=surface_remainder_fraction,
            field_size=self.field_data.field_size,
            inorganic_nitrogen_fraction=(supplied_nitrogen / manure_supplied.dry_matter)
            * manure_supplied.inorganic_nitrogen_fraction,
            ammonium_fraction=manure_supplied.ammonium_nitrogen_fraction,
            organic_nitrogen_fraction=(supplied_nitrogen / manure_supplied.dry_matter)
            * manure_supplied.organic_nitrogen_fraction,
            water_extractable_inorganic_phosphorus_fraction=manure_supplied.inorganic_phosphorus_fraction,
        )

        self._record_manure_application(
            dry_matter_mass=manure_supplied.dry_matter,
            dry_matter_fraction=manure_supplied.dry_matter_fraction,
            field_coverage=field_coverage,
            nitrogen=supplied_nitrogen,
            phosphorus=supplied_phosphorus,
            potassium=None,
            application_depth=application_depth,
            surface_remainder_fraction=surface_remainder_fraction,
            year=year,
            day=day,
            output_name="manure_application",
        )

        return {
            "supplied_nitrogen": supplied_nitrogen,
            "supplied_phosphorus": supplied_phosphorus,
            "application_depth": application_depth,
            "surface_remainder_fraction": surface_remainder_fraction,
        }

    def _validate_application_depth_and_fraction(
        self,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
    ) -> tuple[float, float]:
        """
        Validates the application depth and surface remainder fraction for a manure application.

        Parameters
        ----------
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.

        Returns
        -------
        tuple[float, float]
            The validated application depth and surface remainder fraction.

        Raises
        ------
        ValueError
            If the soil layers are not initialized or if the bottom depth is not set for the last soil layer.
        """
        error_name = "manure_application_error"

        if (application_depth == 0.0 and surface_remainder_fraction != 1.0) or (
            application_depth > 0.0 and surface_remainder_fraction == 1.0
        ):
            self._record_nutrient_application_error(
                application_depth, surface_remainder_fraction, error_name, year, day
            )
            return 0.0, 1.0

        soil_layers = self.soil.data.soil_layers
        if not soil_layers:
            raise ValueError("soil_layers is not initialized")

        bottom_layer = soil_layers[-1]
        if bottom_layer.bottom_depth is None:
            raise ValueError("bottom_depth is not set for the last soil layer")

        max_depth = bottom_layer.bottom_depth
        if application_depth > max_depth:
            self._record_nutrient_application_error(application_depth, None, error_name, year, day)
            application_depth = max_depth

        return application_depth, surface_remainder_fraction

    def _handle_unmet_nutrients(
        self,
        requested_nitrogen: float,
        requested_phosphorus: float,
        supplied_nitrogen: float,
        supplied_phosphorus: float,
        application_depth: float,
        surface_remainder_fraction: float,
        method: ManureSupplementMethod,
        year: int,
        day: int,
    ) -> None:
        """
        Handles the situation where the manure application does not meet the requested nutrient requirements.

        Parameters
        ----------
        requested_nitrogen : float
            Minimum amount of nitrogen to be included in this manure application (kg).
        requested_phosphorus : float
            Minimum amount of phosphorus to be included in this manure application (kg).
        supplied_nitrogen : float
            Amount of nitrogen supplied by the manure application (kg).
        supplied_phosphorus : float
            Amount of phosphorus supplied by the manure application (kg).
        application_depth : float
            Depth at which fertilizer is injected into the soil (mm).
        surface_remainder_fraction : float
            Fraction of fertilizer applied that remains on the soil surface after application (unitless).
        method : ManureSupplementMethod
            Enum option indicating how to supplement the manure application.
        year : int
            Calendar year in which this manure application occurs.
        day : int
            Julian day on which this manure application occurs.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._handle_unmet_nutrients.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "year": year,
            "day": day,
        }
        unmet_n = max(0.0, requested_nitrogen - supplied_nitrogen)
        unmet_p = max(0.0, requested_phosphorus - supplied_phosphorus)

        if unmet_n == 0.0 and unmet_p == 0.0:
            self.om.add_log("Manure Application Log", "Manure fulfilled all nutrient requests.", info_map)
            return

        if method in [ManureSupplementMethod.NONE, ManureSupplementMethod.MANURE]:
            warning_msg = f"Manure nitrogen deficient by {unmet_n} kg, phosphorus deficient by {unmet_p} kg."
            self.om.add_warning("Nutrient deficient manure application", warning_msg, info_map)
            return
        elif method in [
            ManureSupplementMethod.SYNTHETIC_FERTILIZER,
            ManureSupplementMethod.SYNTHETIC_FERTILIZER_AND_MANURE,
        ]:
            self.om.add_log(
                "Manure Application Log",
                "Manure did not fulfill all nutrient requests. Supplementing with synthetic fertilizer.",
                info_map,
            )

            optimal_mix = (
                self.ONLY_NITROGEN_MIX
                if unmet_n > 0.0 and unmet_p == 0.0
                else self._determine_optimal_fertilizer_mix(unmet_n, unmet_p, self.available_fertilizer_mixes)
            )

            self._execute_fertilizer_application(
                optimal_mix,
                unmet_n,
                unmet_p,
                0,
                application_depth,
                surface_remainder_fraction,
                year,
                day,
            )
        else:
            self.om.add_warning(
                "Manure Application Warning",
                f"Manure did not fulfill nutrient requests ({unmet_n} kg N, {unmet_p} kg P), "
                f"but no supplementation was performed due to unrecognized or unsupported method: {method}.",
                info_map,
            )

    def _record_manure_application(
        self,
        dry_matter_mass: float,
        dry_matter_fraction: float,
        field_coverage: float,
        nitrogen: float,
        phosphorus: float,
        application_depth: float,
        surface_remainder_fraction: float,
        year: int,
        day: int,
        output_name: str,
        potassium: Optional[float] = None,
    ) -> None:
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
        units = {
            "dry_matter_mass": MeasurementUnits.DRY_KILOGRAMS,
            "dry_matter_fraction": MeasurementUnits.FRACTION,
            "field_coverage": MeasurementUnits.UNITLESS,
            "application_depth": MeasurementUnits.MILLIMETERS,
            "surface_remainder_fraction": MeasurementUnits.UNITLESS,
            "nitrogen": MeasurementUnits.KILOGRAMS,
            "phosphorus": MeasurementUnits.KILOGRAMS,
            "potassium": MeasurementUnits.KILOGRAMS,
            "day": MeasurementUnits.ORDINAL_DAY,
            "year": MeasurementUnits.CALENDAR_YEAR,
            "field_size": MeasurementUnits.HECTARE,
            "field_name": MeasurementUnits.UNITLESS,
            "average_clay_percent": MeasurementUnits.PERCENT,
        }
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_manure_application.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "units": units,
        }
        value = {
            "dry_matter_mass": dry_matter_mass,
            "dry_matter_fraction": dry_matter_fraction,
            "field_coverage": field_coverage,
            "application_depth": application_depth,
            "surface_remainder_fraction": surface_remainder_fraction,
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "day": day,
            "year": year,
            "field_size": self.field_data.field_size,
            "field_name": self.field_data.name,
            "average_clay_percent": self.soil.data.average_clay_percent,
        }
        self.om.add_variable(output_name, value, info_map)

    def _add_manure_water(self, manure_application: NutrientRequestResults, manure_type: ManureType) -> None:
        """
        Records the water from a manure application so it can be added to the soil.

        Parameters
        ----------
        manure_application : NutrientRequestResults
            An object containing the infomation that defines a manure application.
        manure_type : ManureType
            Enum option indicating if the manure applied was solid or liquid.

        Notes
        -----
        This method only records manure water to be applied to a field if it comes from an application of liquid manure.
        When extracting the amount of water applied in the manure application, the conversion from kilograms of water to
        liters of water is implicit.

        """

        if manure_type is ManureType.SOLID:
            return

        water_amount_in_l = manure_application.total_manure_mass * (1 - manure_application.dry_matter_fraction)

        water_amount_in_mm = self.field_data.convert_liters_to_millimeters(
            water_amount_in_l, self.field_data.field_size
        )
        self.field_data.manure_water += water_amount_in_mm

    def _record_nutrient_application_error(
        self,
        application_depth: float,
        surface_remainder_fraction: Optional[float],
        error_name: str,
        year: int,
        day: int,
    ) -> None:
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
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_nutrient_application_error.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "year": year,
            "day": day,
        }
        if surface_remainder_fraction is not None:
            error_message = (
                f"Invalid application depth ({application_depth}) and surface remainder fraction "
                f"({surface_remainder_fraction}). Defaulting to application depth of 0.0 mm and a "
                f"surface remainder fraction of 1.0."
            )
        else:
            error_message = (
                f"Invalid application depth ({application_depth}) is lower than the bottom depth of "
                f"the soil profile, setting the application depth to be at the bottom of the soil "
                f"profile."
            )
        self.om.add_error(error_name, error_message, info_map)

    # </editor-fold>

    # <editor-fold desc="--- Scheduling Methods ---">
    def _check_crop_planting_schedule(self, time: RufasTime) -> None:
        """
        Checks the list of PlantingEvents, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.

        """
        self.planting_events, todays_planting_events = self._filter_events(self.planting_events, time)
        for event in todays_planting_events:
            self._plant_crop(event.crop_reference, event.use_heat_scheduled_harvest, time)

    def _check_fertilizer_application_schedule(self, time: RufasTime) -> None:
        """
        Checks list of FertilizerEvents, and removes all that occur on the current day from the list.

        Parameters
        ----------
        time : RufasTime
            RufasTime object containing the current year and day of the simulation.

        """
        self.fertilizer_events, todays_fertilizer_events = self._filter_events(self.fertilizer_events, time)
        for event in todays_fertilizer_events:
            self._execute_fertilizer_application(
                event.mix_name,
                event.nitrogen_mass,
                event.phosphorus_mass,
                event.potassium_mass,
                event.depth,
                event.surface_remainder_fraction,
                event.year,
                event.day,
            )

    def _check_tillage_schedule(self, time: RufasTime) -> None:
        """
        Checks the list of Events, and all that are scheduled to happen are passed on to another method to be
        executed.

        Parameters
        ----------
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.
        """
        self.tillage_events, todays_events = self._filter_events(self.tillage_events, time)
        for event in todays_events:
            self.tiller.till_soil(
                event.tillage_depth,
                event.incorporation_fraction,
                event.mixing_fraction,
                event.implement,
                time.current_calendar_year,
                time.current_julian_day,
            )

    def check_manure_application_schedule(self, time: RufasTime) -> list[ManureEventNutrientRequest]:
        """Checks list of ManureEvents, sends all that occur today to another method to be executed.

        Parameters
        ----------
        time : RufasTime
            RufasTime containing the current year and day of the simulation.

        Returns
        -------
        list[ManureEventNutrientRequest]
            A list of the ManureEvents with their corresponding NutrientRequests that are scheduled to occur
            on the current day.
        """
        self.manure_events, todays_manure_events = self._filter_events(self.manure_events, time)
        manure_requests: list[ManureEventNutrientRequest] = []
        for event in todays_manure_events:
            manure_request = self._create_manure_request(event)
            manure_requests.append(ManureEventNutrientRequest(self.field_data.name, event, manure_request))
        return manure_requests

    def _create_manure_request(self, event: ManureEvent) -> NutrientRequest | None:
        """
        Creates a NutrientRequest object from the attributes of a ManureEvent.

        Parameters
        ----------
        event : ManureEvent
            ManureEvent object containing the attributes needed to create a NutrientRequest.

        Returns
        -------
        NutrientRequest | None
            Object containing the nutrient requests of the manure event or None if no nitrogen or phosphorus
            is requested.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._create_manure_request.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "year": event.year,
            "day": event.day,
        }
        if event.nitrogen_mass == event.phosphorus_mass == 0.0:
            log_message = "Tried to apply manure with no nitrogen or phosphorus requested."
            self.om.add_warning("Manure Application Warning", log_message, info_map)
            return None

        use_supplemental_manure = event.manure_supplement_method in [
            ManureSupplementMethod.MANURE,
            ManureSupplementMethod.SYNTHETIC_FERTILIZER_AND_MANURE,
        ]

        return NutrientRequest(
            nitrogen=event.nitrogen_mass,
            phosphorus=event.phosphorus_mass,
            manure_type=event.manure_type,
            use_supplemental_manure=use_supplemental_manure,
        )

    def _check_crop_harvest_schedule(
        self, time: RufasTime, current_conditions: CurrentDayConditions
    ) -> list[HarvestedCrop]:
        """
        Checks for all crops for potential harvests that may happen on the current day.

        Parameters
        ----------
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.
        current_conditions : CurrentDayConditions
            CurrentDayConditions object containing the current weather conditions of the simulated day.

        Returns
        -------
        list[HarvestedCrop]
            A list of harvested crops.

        Notes
        -----
        This method checks for scheduled harvests, i.e. checks all the remaining HarvestEvents. It calls the method that
        checks if crops should be harvested based on their heat fraction.

        """
        self.harvest_events, todays_harvest_events = self._filter_events(self.harvest_events, time)
        harvested_crops = []
        for event in todays_harvest_events:
            crops: list[HarvestedCrop] = self._harvest_crop(
                event.crop_reference, event.operation, time, current_conditions
            )
            harvested_crops.extend(crops)

        heat_scheduled_harvested_crops = self._harvest_heat_scheduled_crops(current_conditions.rainfall, time)

        harvested_crops.extend(heat_scheduled_harvested_crops)
        return harvested_crops

    def _harvest_heat_scheduled_crops(self, rainfall: float, time: RufasTime) -> list[HarvestedCrop]:
        """
        Checks if any of the active plants in the field are harvested based on their heat schedule, and if so harvests
        them if they meet the heat threshold.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall on the current day (mm).
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.

        Returns
        -------
        list[HarvestedCrop]
            Harvested crops.

        References
        ----------
        SWAT Theoretical documentation section 5:1.1.1 (Heat Scheduling)

        """
        harvested_crops = []
        for crop in self.crops:
            if crop.should_harvest_based_on_heat():
                harvested_crop: HarvestedCrop = crop.manage_crop_harvest(
                    HarvestOperation.HARVEST_ONLY,
                    self.field_data.name,
                    self.field_data.field_size,
                    time,
                    self.soil.data,
                )
                self.soil.carbon_cycling.residue_partition.add_residue_to_pools(rainfall)
                if harvested_crop:
                    harvested_crops.append(harvested_crop)
        return harvested_crops

    @staticmethod
    def _filter_events(
        all_events: Sequence[BaseFieldManagementEvent], time: RufasTime
    ) -> tuple[Sequence[BaseFieldManagementEvent], Sequence[BaseFieldManagementEvent]]:
        """
        Filters out all events from a list that occur on the current day, and creates a new list with all the events
        that were filtered out.

        Parameters
        ----------
        all_events : List[BaseFieldManagementEvent]
            List of all Events that will occur over the run of the simulation in this field.
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.

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
            elif event.date_occurs > time.current_date.date():
                remaining_events.append(event)
        return remaining_events, todays_events

    # </editor-fold>

    # <editor-fold desc="--- Crop Management Methods ---">
    def _plant_crop(self, crop_reference: str, use_heat_scheduled_harvesting: bool, time: RufasTime) -> None:
        """
        Plants a crop in the field by creating a new Crop instance and adding it to the field's list of current crops.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be planted.
        use_heat_scheduled_harvesting : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        time : RufasTime
            RufasTime object containing the current year and day of the simulation.

        Notes
        -----
        The crop reference may contain a reference to a supported crop that already has attributes defined for it, or a
        reference to a custom crop that has user-defined attributes.
        The harvest method is overwritten for the crop created because that is specified directly by the user, and the
        crop id is set so that the HarvestEvents will be able to identify the correct crop in the field's list of active
        crops.

        """
        crop = Crop.create_crop(crop_reference, use_heat_scheduled_harvesting, time)
        bottom_soil_layer = len(self.soil.data.soil_layers) - 1
        bottom_layer_depth = self.soil.data.soil_layers[bottom_soil_layer].bottom_depth
        crop.update_crop_max_root_depth(bottom_layer_depth)
        self.crops.append(crop)

        self._record_planting(
            use_heat_scheduled_harvesting,
            crop.data.name,
            time.current_calendar_year,
            time.current_julian_day,
        )

    def _record_planting(
        self,
        heat_scheduled_harvest: bool,
        crop_configuration: str,
        year: int,
        day: int,
    ) -> None:
        """
        Records a planting event to the OutputManager.

        Parameters
        ----------
        heat_scheduled_harvest : bool
            Indicates if this crop should be harvested based on the fraction of potential heat units it has accumulated.
        crop_configuration : str
            Name of the crop configuration being planted.
        year : int
            Year in which this crop planting occurs.
        day : int
            Julian day on which this crop planting occurs.

        """
        units = {
            "crop": MeasurementUnits.UNITLESS,
            "heat_scheduled_harvest": MeasurementUnits.UNITLESS,
            "year": MeasurementUnits.CALENDAR_YEAR,
            "day": MeasurementUnits.ORDINAL_DAY,
            "field_size": MeasurementUnits.HECTARE,
            "average_clay_percent": MeasurementUnits.PERCENT,
            "field_name": MeasurementUnits.UNITLESS,
        }
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_planting.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "units": units,
        }
        value = {
            "crop": crop_configuration,
            "heat_scheduled_harvest": heat_scheduled_harvest,
            "year": year,
            "day": day,
            "field_size": self.field_data.field_size,
            "average_clay_percent": self.soil.data.average_clay_percent,
            "field_name": self.field_data.name,
        }
        self.om.add_variable("crop_planting", value, info_map)

    def _harvest_crop(
        self,
        crop_reference: str,
        harvest_operation: HarvestOperation,
        time: RufasTime,
        current_conditions: CurrentDayConditions,
    ) -> list[HarvestedCrop]:
        """
        Performs the specified crop operation on the specified crop.

        Parameters
        ----------
        crop_reference : str
            Name used to get the specifications for the crop to be harvested.
        harvest_operation : HarvestOperation
            Harvest operation to be performed on the referenced crop.
        time : RufasTime
            RufasTime object containing the current day and year of the simulation.
        current_conditions : CurrentDayConditions
            Object containing the conditions of the current simulated day.

        Returns
        -------
        list[HarvestedCrop]
            Harvested crops.

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

        info_map = {
            "class": self.__class__.__name__,
            "function": self._harvest_crop.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "day": time.current_julian_day,
            "year": time.current_calendar_year,
        }
        if len(crops_to_be_harvested) > 1:
            self.om.add_warning(
                "harvest_warning",
                "Multiple crops to be harvested by single HarvestEvent.",
                info_map,
            )
        elif len(crops_to_be_harvested) < 1:
            self.om.add_warning(
                "harvest_warning",
                "No crop found to be harvested by a HarvestEvent.",
                info_map,
            )

        harvested_crops = []
        for crop in crops_to_be_harvested:
            harvested_crop: HarvestedCrop = crop.manage_crop_harvest(
                harvest_operation,
                self.field_data.name,
                self.field_data.field_size,
                time,
                self.soil.data,
            )
            self.soil.carbon_cycling.residue_partition.add_residue_to_pools(current_conditions.rainfall)
            if harvested_crop:
                harvested_crops.append(harvested_crop)
        return harvested_crops

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

    def _assess_dormancy(self, daylength: float | None, rainfall: float) -> None:
        """
        Transition all crops to dormancy if they are capable of going dormant.

        Parameters
        ----------
        daylength : float
            Length of time from sunup to sundown on the current day (hours).
        rainfall : float
            Amount of rain that fell on the current day (mm).
        """
        for crop in self.crops:
            crop.assess_dormancy(
                daylength, self.field_data.dormancy_threshold_daylength, rainfall, self.soil.data, self.soil
            )

    # </editor-fold>

    # <editor-fold desc="--- Field-level Methods ---">
    def _execute_daily_processes(self, current_conditions: CurrentDayConditions, time: RufasTime) -> None:
        """Executes all daily updates on this field's soil and crop objects.

        Parameters
        ----------
        current_conditions : CurrentDayConditions
            Object containing the environment conditions on this day.
        time : RufasTime
            RufasTime object containing the current year and day of the simulation.

        Notes
        -----
        This method is designed to make it easier to change the order of process execution, which is desirable because
        it will allow subject-matter experts to more easily experiment with different orders.

        """
        self.soil.snow.update_snow(current_day_conditions=current_conditions, day=time.current_julian_day)

        total_plant_cover = self.field_data.current_residue + self._determine_total_above_ground_biomass()
        self.soil.soil_temp.daily_soil_temperature_update(
            current_conditions.incoming_light,
            current_conditions.mean_air_temperature,
            current_conditions.min_air_temperature,
            current_conditions.max_air_temperature,
            total_plant_cover,
            self.soil.data.snow_content,
            current_conditions.annual_mean_air_temperature,
        )

        self._cycle_water(current_conditions, time)

        for crop in self.crops:
            crop.perform_daily_crop_update(current_conditions, self.field_data, self.soil.data, time)

    def _cycle_water(self, current_conditions: CurrentDayConditions, time: RufasTime) -> None:
        """
        Allow water to cycle through the field.

        Parameters
        ----------
        current_conditions : CurrentDayConditions
            A CurrentDayConditions object containing a collection of today's weather variables needed for field
            processes.
        time : RufasTime
            A RufasTime object containing the current year and day of the simulation.

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
        manure_water = self._get_manure_water()
        watering_amount = self._determine_watering_amount(
            rainfall=current_conditions.rainfall,
            manure_water=manure_water,
            year=time.current_simulation_year,
            day=time.current_julian_day,
            irrigation=current_conditions.irrigation,
        )
        total_water = current_conditions.rainfall + watering_amount + manure_water
        precipitation_reaching_soil = self._handle_water_in_crop_canopies(total_water)
        water_reaching_soil = precipitation_reaching_soil + self.soil.data.snow_melt_amount

        full_evapotranspirative_demand = self._determine_potential_evapotranspiration(
            current_conditions.incoming_light,
            current_conditions.max_air_temperature,
            current_conditions.min_air_temperature,
            current_conditions.mean_air_temperature,
        )
        self.field_data.max_evapotranspiration = full_evapotranspirative_demand

        remaining_evapotranspirative_demand = self._evaporate_from_crop_canopies(full_evapotranspirative_demand)

        self.soil.percolation.percolate(self.field_data.seasonal_high_water_table)
        self.soil.infiltration.infiltrate(water_reaching_soil)
        self.soil.percolation.percolate_infiltrated_water()

        self.soil.soil_erosion.erode(
            self.field_data.field_size,
            0.02,
            self.field_data.current_residue,
            total_water,
        )
        self.soil.phosphorus_cycling.cycle_phosphorus(
            water_reaching_soil,
            self.soil.data.accumulated_runoff,
            self.field_data.field_size,
            current_conditions.mean_air_temperature,
        )
        self.soil.carbon_cycling.cycle_carbon(
            water_reaching_soil,
            current_conditions.mean_air_temperature,
            self.field_data.field_size,
        )
        self.soil.nitrogen_cycling.cycle_nitrogen(self.field_data.field_size)

        weighted_transpiration_total = 0.0
        weights_sum = 0.0
        for crop in self.crops:
            crop.set_maximum_transpiration(remaining_evapotranspirative_demand)
            field_proportion = crop.data.field_proportion
            weighted_transpiration_total += crop.data.max_transpiration * field_proportion
            weights_sum += field_proportion

        if weights_sum == 0.0:
            weighted_average_transpiration = 0.0
        else:
            weighted_average_transpiration = weighted_transpiration_total / weights_sum

        above_ground_biomass = self._determine_total_above_ground_biomass()

        soil_evaporation_and_sublimation_amount = self._determine_soil_evaporation_and_sublimation_adjusted(
            above_ground_biomass,
            self.soil.data.soil_layers[0].plant_residue,
            self.soil.data.snow_content,
            remaining_evapotranspirative_demand,
            weighted_average_transpiration,
        )

        pre_sublimation_snow_content = self.soil.data.snow_content
        self.soil.snow.sublimate(soil_evaporation_and_sublimation_amount)
        remaining_evapotranspirative_demand -= self.soil.data.water_sublimated
        max_soil_evaporation = self._determine_maximum_soil_evaporation(
            soil_evaporation_and_sublimation_amount, pre_sublimation_snow_content
        )
        self.soil.evaporation.evaporate(max_soil_evaporation)
        remaining_evapotranspirative_demand -= self.soil.data.water_evaporated

        actual_evaporation = full_evapotranspirative_demand - remaining_evapotranspirative_demand

        for crop in self.crops:
            crop.cycle_water_for_crop(actual_evaporation, full_evapotranspirative_demand, self.soil.data)

    def _determine_watering_amount(
        self, rainfall: float, manure_water: float, year: int, day: int, irrigation: float
    ) -> float:
        """
        Manages watering of the field.

        Parameters
        ----------
        rainfall : float
            Amount of rainfall that occurs on this day (mm).
        manure_water : float
            Amount of water added to the field via manure application (mm).
        year : int
            Year in which this watering occurs.
        day : int
            Julian day on which this watering occurs.
        irrigation : float
            The amount of hard-coded irrigation in the weather data (mm).

        Returns
        -------
        float
            Amount of water used to irrigate the field on this day (mm).

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
            self.field_data.current_water_deficit -= manure_water
            self.field_data.current_water_deficit = max(0.0, self.field_data.current_water_deficit)

            if self.field_data.days_into_watering_interval == self.field_data.watering_interval:
                self.field_data.days_into_watering_interval = 0
                water_applied_this_interval: float = self.field_data.current_water_deficit
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

    def _get_manure_water(self) -> float:
        """
        Grabs water from a manure application and records it, if any.

        Returns
        -------
        float
            Amount of water applied to the field via manure on the current day (mm).

        """
        manure_water: float = self.field_data.manure_water

        info_map = {
            "class": self.__class__.__name__,
            "function": self._get_manure_water.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "units": MeasurementUnits.MILLIMETERS,
        }
        self.om.add_variable("manure_water", manure_water, info_map)

        self.field_data.manure_water = 0.0

        return manure_water

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

        for crop in self.crops:
            precipitation_reaching_soil = crop.handle_water_in_canopy(precipitation_reaching_soil)

        return precipitation_reaching_soil

    def _evaporate_from_crop_canopies(self, evapotranspirative_demand: float) -> float:
        """
        Evaporates water from crops' canopies and reduces evapotranspirative demand accordingly.

        Parameters
        ----------
        evapotranspirative_demand : float
            Evapotranspirative demand on the field on the current day (mm)

        Returns
        -------
        float
            Evapotranspirative demand after evaporating water from crops' canopies (mm)
        """
        remaining_evapotranspirative_demand = evapotranspirative_demand

        for crop in self.crops:
            amount_evaporated = crop.evaporate_from_canopy(remaining_evapotranspirative_demand)
            remaining_evapotranspirative_demand -= amount_evaporated
            if remaining_evapotranspirative_demand == 0.0:
                break

        return remaining_evapotranspirative_demand

    def _determine_total_above_ground_biomass(self) -> float:
        """Calculate the total amount of above-ground biomass still on the plant(s) in the field (kg / ha)"""
        total_above_ground_biomass = 0.0
        for crop in self.crops:
            total_above_ground_biomass += crop.data.above_ground_biomass
        return total_above_ground_biomass

    @staticmethod
    def _determine_potential_evapotranspiration(
        extraterrestrial_radiation: float,
        max_air_temp: float,
        min_air_temp: float,
        avg_air_temp: float,
    ) -> float:
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
        potential_evapotranspiration = (
            0.0023 * extraterrestrial_radiation * ((max_air_temp - min_air_temp) ** 0.5) * (avg_air_temp + 17.8)
        ) / latent_heat_vaporization
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
    def _determine_soil_evaporation_and_sublimation_adjusted(
        above_ground_biomass: float,
        residue: float,
        snow_water_content: float,
        potential_evapotranspiration_adjusted: float,
        transpiration: float,
    ) -> float:
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
        adjusted_soil_evaporation_sublimation = (
            max_soil_evaporation_sublimation * potential_evapotranspiration_adjusted
        ) / (max_soil_evaporation_sublimation + transpiration)
        actual_soil_evaporation_sublimation = min(
            max_soil_evaporation_sublimation, adjusted_soil_evaporation_sublimation
        )
        return actual_soil_evaporation_sublimation

    @staticmethod
    def _determine_maximum_soil_evaporation(soil_evaporation_adj: float, snow_water_content: float) -> float:
        """
        Calculates the maximum amount of evaporation from soil in a given day.

        Parameters
        ----------
        soil_evaporation_adj : float
            Maximum soil evaporation adjusted for plant water use on a given day (mm).
        snow_water_content : float
            Amount of water in the snow pack on a given day prior to accounting for sublimation (mm).

        Returns
        -------
        float
            Maximum soil water evaporation on a given day (mm).

        References
        ----------
        SWAT Theoretical documentation 2:2.3.3.1

        """
        if soil_evaporation_adj < snow_water_content:
            return 0  # 2:2.3.10
        else:
            return soil_evaporation_adj - snow_water_content  # 2:2.3.15

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
        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_field_watering.__name__,
            "suffix": f"field='{self.field_data.name}'",
            "year": year,
            "day": day,
            "field_size": self.field_data.field_size,
            "units": MeasurementUnits.MILLIMETERS,
        }
        self.om.add_variable("field_watering", watering_amount, info_map)

    # </editor-fold>
