from typing import Any

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
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

    """

    CALF_DRY_MATTER_INTAKE = 3

    _om = OutputManager()
    ration_feeds: dict[AnimalCombination, list[RUFAS_ID]] | None
    user_defined_rations: dict[AnimalCombination, dict[RUFAS_ID, float]] | None
    tolerance: float | None = 0.0
    maximum_ration_reformulation_attempts: int

    @classmethod
    def set_ration_feeds(cls, ration_config: dict[str, Any]) -> None:
        """
        Maps the input feeds available for each ration to Animal combinations.

        Parameters
        ----------
        ration_config : dict[str, Any]
            Collection of animal requirements and feed supply information for ration formulation.

        """
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
            if abs(total_percentage_of_ration - 100.0) > tolerance:
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
    def get_user_defined_ration(
        cls,
        animal_combination: AnimalCombination,
        requirements: NutritionRequirements,
    ) -> dict[RUFAS_ID, float]:
        """
        Generate a ration for the given animal type scaled to the estimated dry matter intake requirement.

        Parameters
        ----------
        animal_combination : AnimalCombination
            The combination of animals in the pen.
        requirements : NutritionRequirements
            The nutrition requirements of an animal or average of a group of animals.

        Returns
        -------
        dict[RUFAS_ID, float]
            A mapping of feed RuFaS IDs to the amount of feed required in the ration (kg dry matter).

        """
        ration_formulation = cls.user_defined_rations[animal_combination]

        ration: dict[RUFAS_ID, float] = {
            rufas_id: (
                requirements.dry_matter * percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
                if animal_combination != AnimalCombination.CALF
                else cls.CALF_DRY_MATTER_INTAKE * percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
            )
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
