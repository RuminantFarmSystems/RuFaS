from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from RUFAS.biophysical.animal.animal import Animal

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.animal_enums import StockerDietSystem
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.intake_option import IntakeOption
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


class RationManager:
    """
    Handles the initialization and management of user-defined animal rations.

    Each ration formulation is represented as a dictionary, where the key is the
    RuFaS ID of a feed and the value is the percentage it contributes to the ration.

    Attributes
    ----------
    _om : OutputManager
        A private instance of OutputManager for use in this class.
    user_defined_rations : dict[AnimalCombination, dict[RUFAS_ID, float]]
        A mapping of animal groupings to their respective ration formulations.
    ration_feeds : dict[AnimalCombination, list[RUFAS_ID]]
        A mapping of animal groupings to the list of RuFaS feed IDs available to formulate their ration.
    tolerance : float
        Fraction +/- of target user defined ration value (as a fraction of dry matter intake estimate) allowable in
        ration formulation.
    maximum_ration_reformulation_attempts : int
        Maximum number of attempts to formulate a ration in a single ration interval for a single pen.
    intake_options : dict[AnimalCombination, IntakeOption]
        A mapping of animal groupings to their dry matter intake control options. Animal
        combinations absent from this mapping use the predict DMI option (default behavior).
    intake_values : dict[AnimalCombination, float | None]
        A mapping of animal groupings to their user-provided dry matter intake values. Values are
        None for animal combinations using the predict DMI option.

    """

    CALF_DRY_MATTER_INTAKE = 3

    _om = OutputManager()
    ration_feeds: dict[AnimalCombination, list[RUFAS_ID]] | None
    user_defined_rations: dict[AnimalCombination, dict[RUFAS_ID, float]] | None
    tolerance: float | None = 0.0
    maximum_ration_reformulation_attempts: int
    feedlot_starter_ration: dict[RUFAS_ID, float]
    feedlot_transition_ration: dict[RUFAS_ID, float]
    feedlot_finisher_ration: dict[RUFAS_ID, float]
    beef_lactating_pasture_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    beef_dry_gestating_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    beef_creep_feed_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    beef_replacement_heifer_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    # UPSTREAM-SYNC NOTE: RuminantFarmSystems/RuFaS PR #3248 (IntakeOption
    # enum) landed in the 2026-11 upstream sync. The stocker limit-feed cap is
    # still applied here; reconciling it as an IntakeOption member taking a
    # percentage of predicted DMI remains open.
    beef_stocker_pasture_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    beef_stocker_drylot_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    beef_stocker_limit_feed_ration: ClassVar[dict[RUFAS_ID, float]] = {}
    intake_options: dict[AnimalCombination, IntakeOption] = {}
    intake_values: dict[AnimalCombination, float | None] = {}

    @classmethod
    def set_ration_feeds(cls, ration_config: dict[str, Any]) -> None:
        """
        Maps the input feeds available for each ration to Animal combinations.

        Parameters
        ----------
        ration_config : dict[str, Any]
            Collection of animal requirements and feed supply information for ration formulation.

        Notes
        -----
        This method configures the automated ration formulation mode, so the dry matter intake
        options (only applicable to user-defined rations) are reset to the default predict DMI
        behavior.

        """
        next_ration_feeds: dict[AnimalCombination, list[RUFAS_ID]] = {
            animal_combination: [] for animal_combination in AnimalCombination
        }

        next_ration_feeds[AnimalCombination.CALF] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "calf"
            for feed in ration["feeds"]
        ]

        next_ration_feeds[AnimalCombination.GROWING] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "growing"
            for feed in ration["feeds"]
        ]

        next_ration_feeds[AnimalCombination.CLOSE_UP] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "close_up"
            for feed in ration["feeds"]
        ]

        next_ration_feeds[AnimalCombination.LAC_COW] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "lac_cow"
            for feed in ration["feeds"]
        ]

        feedlot_starter = {int(k): float(v) for k, v in ration_config.get("feedlot_starter_ration", {}).items()}
        feedlot_transition = {int(k): float(v) for k, v in ration_config.get("feedlot_transition_ration", {}).items()}
        feedlot_finisher = {int(k): float(v) for k, v in ration_config.get("feedlot_finisher_ration", {}).items()}

        for name, ration in (
            ("starter", feedlot_starter),
            ("transition", feedlot_transition),
            ("finisher", feedlot_finisher),
        ):
            if ration:
                cls._validate_ration_percentages(f"Feedlot {name}", ration)

        next_ration_feeds[AnimalCombination.FEEDLOT_FINISHING] = [
            int(f) for f in ration_config.get("feedlot_feeds", [])
        ]

        # Stage in local variables first — validate before modifying class state
        beef_lactating_pasture_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_lactating_pasture_ration") or {}).items()
        }
        beef_dry_gestating_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_dry_gestating_ration") or {}).items()
        }
        beef_creep_feed_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_creep_feed_ration") or {}).items()
        }
        beef_replacement_heifer_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_replacement_heifer_ration") or {}).items()
        }
        for name, ration in [
            ("beef_lactating_pasture", beef_lactating_pasture_ration),
            ("beef_dry_gestating", beef_dry_gestating_ration),
            ("beef_creep_feed", beef_creep_feed_ration),
            ("beef_replacement_heifer", beef_replacement_heifer_ration),
        ]:
            if ration:
                cls._validate_ration_percentages(f"Beef {name}", ration)

        beef_stocker_pasture_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_stocker_pasture_ration") or {}).items()
        }
        beef_stocker_drylot_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_stocker_drylot_ration") or {}).items()
        }
        beef_stocker_limit_feed_ration = {
            int(k): float(v) for k, v in (ration_config.get("beef_stocker_limit_feed_ration") or {}).items()
        }
        for name, ration in [
            ("beef_stocker_pasture", beef_stocker_pasture_ration),
            ("beef_stocker_drylot", beef_stocker_drylot_ration),
            ("beef_stocker_limit_feed", beef_stocker_limit_feed_ration),
        ]:
            if ration:
                cls._validate_ration_percentages(f"Beef {name}", ration)

        cls.intake_options = {}
        cls.intake_values = {}
        cls.ration_feeds = next_ration_feeds
        cls.feedlot_starter_ration = feedlot_starter
        cls.feedlot_transition_ration = feedlot_transition
        cls.feedlot_finisher_ration = feedlot_finisher
        cls.beef_lactating_pasture_ration = beef_lactating_pasture_ration
        cls.beef_dry_gestating_ration = beef_dry_gestating_ration
        cls.beef_creep_feed_ration = beef_creep_feed_ration
        cls.beef_replacement_heifer_ration = beef_replacement_heifer_ration
        cls.beef_stocker_pasture_ration = beef_stocker_pasture_ration
        cls.beef_stocker_drylot_ration = beef_stocker_drylot_ration
        cls.beef_stocker_limit_feed_ration = beef_stocker_limit_feed_ration

    @staticmethod
    def _validate_ration_percentages(name: str, ration: dict[int, float]) -> None:
        """Raise ValueError if ``ration`` has negative, non-finite, or non-100% percentages.

        Parameters
        ----------
        name : str
            Human-readable ration label used in error messages.
        ration : dict[int, float]
            Feed-ID to percentage mapping to validate.
        """
        negative = [pct for pct in ration.values() if pct < 0.0]
        if negative:
            raise ValueError(f"{name} ration percentages must be non-negative, got: {negative}")
        total_pct = sum(ration.values())
        if not math.isfinite(total_pct):
            raise ValueError(f"{name} ration contains non-finite values")
        if abs(total_pct - 100.0) > 1e-2:
            raise ValueError(f"{name} ration percentages must sum to 100.0%, got {total_pct}%")

    @classmethod
    def get_feedlot_phase_ration(
        cls,
        step_up_phase: str,
        requirements: NutritionRequirements,
    ) -> dict[RUFAS_ID, float]:
        """
        Return feed quantities (kg DM) for the current step-up diet phase.

        Parameters
        ----------
        step_up_phase : str
            'starter', 'transition', or 'finisher'.  Unknown values fall back
            to the finisher ration.
        requirements : NutritionRequirements
            Current nutrition requirements; ``dry_matter`` provides the DMI target.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of feed RUFAS ID to kg DM allocation for this day.

        """
        phase_ration_map: dict[str, dict[RUFAS_ID, float]] = {
            "starter": cls.feedlot_starter_ration,
            "transition": cls.feedlot_transition_ration,
            "finisher": cls.feedlot_finisher_ration,
        }
        ration_pct = phase_ration_map.get(step_up_phase, cls.feedlot_finisher_ration)
        return {feed_id: requirements.dry_matter * pct / 100.0 for feed_id, pct in ration_pct.items()}

    @classmethod
    def get_beef_seasonal_ration(cls, animal: Animal) -> dict[RUFAS_ID, float]:
        """Returns the seasonal ration dict for a beef cow-calf animal based on its current state.

        Parameters
        ----------
        animal : Animal
            The beef animal whose ration is being selected.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of feed RUFAS ID to percentage of ration.

        Raises
        ------
        ValueError
            If the animal type has no beef seasonal ration mapping.

        """
        if animal.animal_type == AnimalType.BEEF_HEIFER_REPLACEMENT:
            return cls.beef_replacement_heifer_ration.copy()
        if animal.animal_type == AnimalType.BEEF_COW and animal.calf_at_side is not None:
            return cls.beef_lactating_pasture_ration.copy()
        if animal.animal_type in (AnimalType.BEEF_COW, AnimalType.BEEF_BULL):
            return cls.beef_dry_gestating_ration.copy()
        if animal.animal_type == AnimalType.BEEF_CALF:
            return {}
        raise ValueError(f"No beef seasonal ration for animal_type {animal.animal_type}")

    @classmethod
    def get_beef_creep_feed_supplement(cls, animal: Animal) -> dict[RUFAS_ID, float]:
        """Returns creep feed dict for a nursing calf if creep feeding is enabled, else empty dict.

        Parameters
        ----------
        animal : Animal
            The beef animal (typically a nursing calf) for creep feed lookup.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of feed RUFAS ID to percentage, or empty dict if creep feeding disabled.

        """
        if animal.animal_type is not AnimalType.BEEF_CALF:
            return {}
        if not AnimalConfig.beef_creep_feeding_enabled:
            return {}
        return cls.beef_creep_feed_ration.copy()

    @classmethod
    def get_beef_stocker_ration(cls, animal: Animal) -> dict[RUFAS_ID, float]:
        """Return the stocker ration dict for the configured diet system.

        Parameters
        ----------
        animal : Animal
            The stocker animal (unused; kept for API symmetry with get_beef_seasonal_ration).

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of feed RUFAS ID to percentage for the active stocker diet system.

        Raises
        ------
        ValueError
            If AnimalConfig.stocker_diet_system is not a recognised StockerDietSystem member.

        """
        # UPSTREAM-SYNC NOTE: RuminantFarmSystems/RuFaS PR #3248 (IntakeOption
        # enum) landed in the 2026-11 upstream sync. The stocker limit-feed cap is
        # still applied here; reconciling it as an IntakeOption member taking a
        # percentage of predicted DMI remains open.
        system = AnimalConfig.stocker_diet_system
        if system is StockerDietSystem.PASTURE:
            return cls.beef_stocker_pasture_ration.copy()
        if system is StockerDietSystem.DRYLOT_FORAGE:
            return cls.beef_stocker_drylot_ration.copy()
        if system is StockerDietSystem.LIMIT_FEED:
            return cls.beef_stocker_limit_feed_ration.copy()
        raise ValueError(f"Unknown stocker_diet_system: {system!r}")

    @classmethod
    def get_ration_feeds(cls, animal_combination: AnimalCombination) -> list[RUFAS_ID]:
        """
        Generate a list of feed RuFaS IDs for the given animal combination that user defined to be used as the ration.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.

        Returns
        -------
        list[RUFAS_ID]
            A list of feed RuFaS IDs that user defined to be used as the feed for the given animal combination.

        """
        return cls.ration_feeds[animal_combination]

    @classmethod
    def set_user_defined_ration_tolerance(cls, feed_config: dict[str, Any]) -> None:
        """
        Collects the tolerance value for user defined rations.

        Parameters
        ----------
        feed_config : dict[str, Any]
            Collection of animal requirements and feed supply information for ration formulation.

        """
        cls.tolerance = feed_config["ration_formulation_parameters"]["user_defined_ration_tolerance"]

    @classmethod
    def set_user_defined_rations(cls, feed_config: dict[str, Any]) -> None:
        """
        Maps the input user-defined rations to Animal combinations.

        Parameters
        ----------
        ration_config : dict[str, Any]
            Collection of animal requirements and feed supply information for ration formulation.

        Raises
        ------
        ValueError
            If one or more invalid rations is found.

        """
        info_map: dict[str, object] = {"class": cls.__name__, "function": cls.set_user_defined_rations.__name__}

        cls.user_defined_rations = {animal_combination: {} for animal_combination in AnimalCombination}

        ration_config = feed_config["rations"]
        user_defined_ration_percentages = {ration["animal_combination"]: ration["feeds"] for ration in ration_config}
        tolerance = feed_config["ration_formulation_parameters"]["user_defined_ration_tolerance"]

        for combination in cls.user_defined_rations.keys():
            if combination.value not in user_defined_ration_percentages:
                continue
            cls.user_defined_rations[combination] = {
                feed["feed_type"]: feed["ration_percentage"]
                for feed in user_defined_ration_percentages[combination.value]
            }

        invalid_ration_found: bool = False
        for animal_combo, ration in cls.user_defined_rations.items():
            if not ration:
                continue
            total_percentage_of_ration = sum(ration.values())
            info_map["ration"] = ration
            info_map["animal_combination"] = animal_combo.value
            info_map["units"] = MeasurementUnits.PERCENT

            if abs(total_percentage_of_ration - 100.0) > tolerance * 100:
                error_msg = (
                    f"Invalid user-defined ration for {animal_combo.value}. "
                    f"Ration percentages sum to {total_percentage_of_ration}. "
                    "Simulation will be halted."
                )
                cls._om.add_error("invalid_user_defined_ration_found", error_msg, info_map)
                invalid_ration_found = True
            else:
                cls._om.add_variable("user_defined_ration", ration, info_map)

        if invalid_ration_found:
            raise ValueError("One or more invalid user-defined rations found.")

        cls.user_defined_rations[AnimalCombination.GROWING_AND_CLOSE_UP] = cls.user_defined_rations[
            AnimalCombination.CLOSE_UP
        ]
        cls._om.add_log(
            "growing_and_close_up_user_defined_rations",
            "Pens with growing and close-up cows will use the user-defined ration for close-up pens",
            info_map,
        )

    @classmethod
    def set_intake_options(cls, feed_config: dict[str, Any]) -> None:
        """
        Maps the input dry matter intake options and values to Animal combinations.

        Parameters
        ----------
        feed_config : dict[str, Any]
            Collection of animal requirements and feed supply information for ration formulation.

        Raises
        ------
        ValueError
            If a ration names an unknown animal combination or intake option, if an intake option
            other than predict DMI is missing an intake value, or if the DMI per X option is
            requested for an animal combination that does not support it.

        Notes
        -----
        An intake value supplied alongside the predict DMI option is not used, since dry matter
        intake is predicted in that case. A warning identifies the animal combination and the
        unused value rather than halting the simulation.

        """
        info_map: dict[str, object] = {"class": cls.__name__, "function": cls.set_intake_options.__name__}

        cls.intake_options = {animal_combination: IntakeOption.PREDICT_DMI for animal_combination in AnimalCombination}
        cls.intake_values = {animal_combination: None for animal_combination in AnimalCombination}

        for ration in feed_config["rations"]:
            combination = AnimalCombination(ration["animal_combination"])
            option = IntakeOption(ration.get("intake_option") or IntakeOption.PREDICT_DMI.value)
            intake_value = ration.get("intake_value") if option is not IntakeOption.PREDICT_DMI else None

            info_map["animal_combination"] = combination.value
            info_map["intake_value"] = intake_value
            info_map["units"] = MeasurementUnits.UNITLESS

            if option is IntakeOption.PREDICT_DMI and ration.get("intake_value") is not None:
                cls._om.add_warning(
                    "unused_intake_value_for_predict_dmi",
                    f"The {combination.value} ration provides an intake_value of "
                    f"{ration['intake_value']}, but its intake_option is '{option.value}', so dry matter intake "
                    "is predicted and the provided value is not used.",
                    info_map,
                )

            if option is not IntakeOption.PREDICT_DMI and (intake_value is None or intake_value <= 0):
                error_msg = (
                    f"Intake option '{option.value}' for {combination.value} requires an intake_value greater "
                    f"than 0, but got {intake_value}. Simulation will be halted."
                )
                cls._om.add_error("invalid_intake_value_for_intake_option", error_msg, info_map)
                raise ValueError(error_msg)
            if option is IntakeOption.SET_DMI_PER_X and combination not in (
                AnimalCombination.GROWING,
                AnimalCombination.LAC_COW,
            ):
                error_msg = (
                    f"Intake option '{option.value}' is only available for growing and lac_cow rations, "
                    f"but was requested for {combination.value}. Simulation will be halted."
                )
                cls._om.add_error("invalid_intake_option_for_animal_combination", error_msg, info_map)
                raise ValueError(error_msg)

            cls.intake_options[combination] = option
            cls.intake_values[combination] = intake_value
            cls._om.add_variable("dmi_intake_option", option.value, info_map)

        cls.intake_options[AnimalCombination.GROWING_AND_CLOSE_UP] = cls.intake_options[AnimalCombination.CLOSE_UP]
        cls.intake_values[AnimalCombination.GROWING_AND_CLOSE_UP] = cls.intake_values[AnimalCombination.CLOSE_UP]

    @classmethod
    def get_intake_option(cls, animal_combination: AnimalCombination | None) -> IntakeOption:
        """
        Returns the dry matter intake option configured for the given animal combination.

        Parameters
        ----------
        animal_combination : AnimalCombination | None
            The combination of animals in the pen, or None when no combination applies.

        Returns
        -------
        IntakeOption
            The configured intake option, or the predict DMI option when none is configured.

        """
        if animal_combination is None:
            return IntakeOption.PREDICT_DMI
        return cls.intake_options.get(animal_combination, IntakeOption.PREDICT_DMI)

    @classmethod
    def uses_dmi_input_option(cls, animal_combination: AnimalCombination | None) -> bool:
        """
        Returns True if the given animal combination uses a DMI input option (set DMI or DMI per X).

        Parameters
        ----------
        animal_combination : AnimalCombination | None
            The combination of animals in the pen, or None when no combination applies.

        Returns
        -------
        bool
            True if the animal combination uses a DMI input option, False otherwise.

        """
        return cls.get_intake_option(animal_combination) is not IntakeOption.PREDICT_DMI

    @classmethod
    def effective_dmi_constraint_fraction(cls, animal_combination: AnimalCombination | None) -> float:
        """
        Returns the effective DMI constraint fraction for the given animal combination.

        Parameters
        ----------
        animal_combination : AnimalCombination | None
            The combination of animals in the pen, or None when no combination applies.

        Returns
        -------
        float
            0.0 when a DMI input option is used, so the dry matter intake may only deviate from the
            user-provided target by the user-defined tolerance; the DMI_CONSTRAINT_FRACTION constant
            otherwise.

        """
        if cls.uses_dmi_input_option(animal_combination):
            return 0.0
        return AnimalModuleConstants.DMI_CONSTRAINT_FRACTION

    @classmethod
    def effective_dmi_requirement_boost(cls, animal_combination: AnimalCombination | None) -> float:
        """
        Returns the effective DMI requirement boost for the given animal combination.

        Parameters
        ----------
        animal_combination : AnimalCombination | None
            The combination of animals in the pen, or None when no combination applies.

        Returns
        -------
        float
            1.0 when a DMI input option is used, so the ingredient inclusion bounds are centered on
            the user-provided target; the DMI_REQUIREMENT_BOOST constant otherwise.

        """
        if cls.uses_dmi_input_option(animal_combination):
            return 1.0
        return AnimalModuleConstants.DMI_REQUIREMENT_BOOST

    @classmethod
    def effective_dmi_retry_increase_factor(cls, animal_combination: AnimalCombination | None) -> float:
        """
        Returns the effective DMI retry increase factor for the given animal combination.

        Parameters
        ----------
        animal_combination : AnimalCombination | None
            The combination of animals in the pen, or None when no combination applies.

        Returns
        -------
        float
            1.0 when a DMI input option is used, so formulation retries never adjust the
            user-provided target; the DMI_RETRY_INCREASE_FACTOR constant otherwise.

        """
        if cls.uses_dmi_input_option(animal_combination):
            return 1.0
        return AnimalModuleConstants.DMI_RETRY_INCREASE_FACTOR

    @classmethod
    def resolve_target_dmi(cls, animal_combination: AnimalCombination, pen: Any) -> float:
        """
        Resolves the target dry matter intake for a pen based on its dry matter intake option.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.
        pen : Any
            The Pen whose target dry matter intake is resolved. Typed as Any because Pen imports
            RationManager, so importing Pen here would create a circular import.

        Returns
        -------
        float
            The target dry matter intake (kg/animal/day). For the set DMI option this is the
            user-provided intake value, and for the DMI per X option it is the intake value
            multiplied by the pen's average milk production (lactating cows) or average daily gain
            (growing heifers). For the predict DMI option this is the pen's average predicted dry
            matter requirement, or the fixed calf dry matter intake for calf pens.

        Raises
        ------
        ValueError
            If a DMI input option is configured without an intake value.

        Notes
        -----
        If the DMI per X option is selected but the pen's X value (average milk production or
        average daily gain) is not positive, e.g. before the first daily growth update, the
        predicted dry matter requirement is used for that formulation and a warning is logged.

        """
        option = cls.get_intake_option(animal_combination)

        if option is IntakeOption.PREDICT_DMI:
            if animal_combination is AnimalCombination.CALF:
                return float(cls.CALF_DRY_MATTER_INTAKE)
            return float(pen.average_nutrition_requirements.dry_matter)

        intake_value = cls.intake_values.get(animal_combination)
        if intake_value is None:
            raise ValueError(f"Intake option '{option.value}' for {animal_combination.value} requires an intake_value.")

        if option is IntakeOption.SET_DMI:
            return intake_value

        if animal_combination is AnimalCombination.LAC_COW:
            x_value = pen.average_milk_production
            x_description = "average milk production"
        else:
            x_value = pen.average_growth
            x_description = "average daily gain"
        if x_value <= 0.0:
            cls._om.add_warning(
                "dmi_per_x_value_unavailable",
                f"The {option.value} option for {animal_combination.value} could not be applied because the pen's "
                f"{x_description} is not positive ({x_value}). The predicted dry matter requirement is used for "
                "this ration formulation instead.",
                {
                    "class": cls.__name__,
                    "function": cls.resolve_target_dmi.__name__,
                    "animal_combination": animal_combination.value,
                    "units": MeasurementUnits.KILOGRAMS,
                },
            )
            return float(pen.average_nutrition_requirements.dry_matter)
        return float(intake_value * x_value)

    @classmethod
    def get_user_defined_ration(
        cls,
        animal_combination: AnimalCombination,
        target_dry_matter_intake: float,
    ) -> dict[RUFAS_ID, float]:
        """
        Generate a ration for the given animal type scaled to the target dry matter intake.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.
        target_dry_matter_intake : float
            The dry matter intake the ration is scaled to (kg/animal/day), as resolved by
            resolve_target_dmi.

        Returns
        -------
        dict[RUFAS_ID, float]
            A mapping of feed RuFaS IDs to the amount of feed required in the ration (kg dry matter).

        """
        ration_formulation = cls.user_defined_rations[animal_combination]

        ration: dict[RUFAS_ID, float] = {
            rufas_id: target_dry_matter_intake * percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
            for rufas_id, percentage in ration_formulation.items()
        }

        return ration

    @classmethod
    def get_user_defined_ration_feeds(cls, animal_combination: AnimalCombination) -> list[RUFAS_ID]:
        """
        Generate a list of feed RuFaS IDs for the given animal combination that user defined to be used as the ration.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.

        Returns
        -------
        list[RUFAS_ID]
            A list of feed RuFaS IDs that user defined to be used as the feed for the given animal combination.

        """
        ration_formulation = cls.user_defined_rations[animal_combination]
        return list(ration_formulation.keys())
