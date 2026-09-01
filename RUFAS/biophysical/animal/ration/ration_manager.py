from typing import Any, TYPE_CHECKING

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.intake_option import IntakeOption
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

if TYPE_CHECKING:
    from RUFAS.biophysical.animal.pen import Pen


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
    intake_options : dict[AnimalCombination, IntakeOption] | None
        A mapping of animal groupings to their dry matter intake control options. When None, the
        predict DMI option (default behavior) is used for every animal combination.
    intake_values : dict[AnimalCombination, float | None] | None
        A mapping of animal groupings to their user-provided dry matter intake values. Values are
        None for animal combinations using the predict DMI option.

    """

    CALF_DRY_MATTER_INTAKE = 3

    _om = OutputManager()
    ration_feeds: dict[AnimalCombination, list[RUFAS_ID]] | None
    user_defined_rations: dict[AnimalCombination, dict[RUFAS_ID, float]] | None
    tolerance: float | None = 0.0
    maximum_ration_reformulation_attempts: int
    intake_options: dict[AnimalCombination, IntakeOption] | None = None
    intake_values: dict[AnimalCombination, float | None] | None = None

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
        cls.intake_options = None
        cls.intake_values = None
        cls.ration_feeds = {animal_combination: [] for animal_combination in AnimalCombination}

        cls.ration_feeds[AnimalCombination.CALF] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "calf"
            for feed in ration["feeds"]
        ]

        cls.ration_feeds[AnimalCombination.GROWING] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "growing"
            for feed in ration["feeds"]
        ]

        cls.ration_feeds[AnimalCombination.CLOSE_UP] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "close_up"
            for feed in ration["feeds"]
        ]

        cls.ration_feeds[AnimalCombination.LAC_COW] = [
            feed["feed_type"]
            for ration in ration_config["rations"]
            if ration["animal_combination"] == "lac_cow"
            for feed in ration["feeds"]
        ]

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
            If an intake option other than predict DMI is missing an intake value, or if the
            DMI per X option is requested for an animal combination that does not support it.

        """
        info_map: dict[str, object] = {"class": cls.__name__, "function": cls.set_intake_options.__name__}

        cls.intake_options = {animal_combination: IntakeOption.PREDICT_DMI for animal_combination in AnimalCombination}
        cls.intake_values = {animal_combination: None for animal_combination in AnimalCombination}

        combinations_by_value = {
            animal_combination.value: animal_combination for animal_combination in AnimalCombination
        }
        for ration in feed_config["rations"]:
            combination = combinations_by_value.get(ration["animal_combination"])
            if combination is None:
                continue
            option = IntakeOption(ration.get("intake_option") or IntakeOption.PREDICT_DMI.value)
            intake_value = ration.get("intake_value") if option is not IntakeOption.PREDICT_DMI else None

            info_map["animal_combination"] = combination.value
            info_map["intake_value"] = intake_value
            info_map["units"] = MeasurementUnits.UNITLESS

            if option is not IntakeOption.PREDICT_DMI and intake_value is None:
                error_msg = (
                    f"Intake option '{option.value}' for {combination.value} requires an intake_value. "
                    "Simulation will be halted."
                )
                cls._om.add_error("missing_intake_value_for_intake_option", error_msg, info_map)
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
        if animal_combination is None or cls.intake_options is None:
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
    def resolve_target_dmi(cls, animal_combination: AnimalCombination, pen: "Pen") -> float:
        """
        Resolves the target dry matter intake for a pen based on its dry matter intake option.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.
        pen : Pen
            The pen whose target dry matter intake is resolved.

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

        """
        option = cls.get_intake_option(animal_combination)

        if option is IntakeOption.PREDICT_DMI:
            if animal_combination is AnimalCombination.CALF:
                return float(cls.CALF_DRY_MATTER_INTAKE)
            return pen.average_nutrition_requirements.dry_matter

        intake_value = cls.intake_values[animal_combination] if cls.intake_values is not None else None
        if intake_value is None:
            raise ValueError(f"Intake option '{option.value}' for {animal_combination.value} requires an intake_value.")

        if option is IntakeOption.SET_DMI:
            return intake_value

        x_value = pen.average_milk_production if animal_combination is AnimalCombination.LAC_COW else pen.average_growth
        return intake_value * x_value

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
