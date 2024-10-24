from typing import Any

import numpy as np

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.reproduction_properties import ReproductionProperties
from RUFAS.biophysical.animal.animal_properties.growth_properties import GrowthProperties


class Growth:
    """
    Handles updating the body weight growth related animal attributes.

    Attributes
    ----------
    WEAN_DAY: int
        Class constant that indicates the user-defined wean day for calves.
    TARGET_HEIFER_PREGNANT_DAY: int
        Class constant that indicates the user-defined target pregnant day for heifers.
    """

    WEAN_DAY: int
    TARGET_HEIFER_PREGNANT_DAY: int

    @classmethod
    def initialize_animal_growth_variables(cls) -> None:
        """
        This function retrieves the user input data from the InputManager and initializes the class constants.
        """
        im = InputManager()
        animal_config: dict[str, dict[str, Any]] = im.get_data("animal.animal_config.farm_level")
        cls.WEAN_DAY = animal_config["calf"]["wean_day"]
        cls.TARGET_HEIFER_PREGNANT_DAY = animal_config["bodyweight"]["target_heifer_preg_day"]

    @staticmethod
    def evaluate_body_weight_change(
        general_properties: GeneralProperties,
        animal_growth_properties: GrowthProperties,
        reproduction_properties: ReproductionProperties,
        time: Time,
    ) -> tuple[GrowthProperties, ReproductionProperties, GeneralProperties]:
        """
        Handles an animal's daily growth updates.

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        animal_growth_properties: GrowthProperties
            Animal properties that are related to body weight growth.
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        time : Time
            Time instance containing the current time of the simulation.

        Returns
        -------
        tuple[AnimalGrowthProperties, ReproductionProperties, GeneralProperties]
            The updated animal growth properties, reproduction properties, and the general properties of the animal
            after the growth-related routines for the current day.
        """
        is_non_pregnant_heifer = not general_properties.is_pregnant and (
            general_properties.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II)
        )
        is_pregnant_heifer = general_properties.is_pregnant and (
            general_properties.animal_type in (AnimalType.HEIFER_II, AnimalType.HEIFER_III)
        )

        if general_properties.animal_type == AnimalType.CALF:
            animal_growth_properties.daily_growth = Growth.calculate_calf_body_weight_change(general_properties)
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif is_non_pregnant_heifer:
            animal_growth_properties.daily_growth = Growth.calculate_non_pregnant_heifer_body_weight_change(
                general_properties
            )
            general_properties.body_weight += animal_growth_properties.daily_growth

        elif is_pregnant_heifer:
            if general_properties.body_weight < general_properties.mature_body_weight:
                (animal_growth_properties.daily_growth, reproduction_properties.conceptus_weight) = (
                    Growth.calculate_pregnant_heifer_body_weight_change(
                        reproduction_properties, general_properties
                    )
                )
                general_properties.body_weight += animal_growth_properties.daily_growth
            else:
                general_properties.body_weight = general_properties.mature_body_weight
                general_properties.events.add_event(
                    general_properties.days_born, time.simulation_day, animal_constants.MATURE_BODY_WEIGHT_REGULAR
                )

        elif general_properties.animal_type.is_cow:
            (
                animal_growth_properties.daily_growth,
                reproduction_properties.conceptus_weight,
                animal_growth_properties.tissue_changed,
            ) = Growth.calculate_cow_body_weight_change(
                animal_growth_properties, reproduction_properties, general_properties
            )
            general_properties.body_weight += animal_growth_properties.daily_growth
        else:
            om = OutputManager()
            om.add_error(
                "Unexpected Animal Type",
                f"{general_properties.animal_type} is not a valid animal type.",
                {
                    "class": Growth.__class__.__name__,
                    "function": Growth.evaluate_body_weight_change.__name__,
                },
            )

        return animal_growth_properties, reproduction_properties, general_properties

    @staticmethod
    def calculate_calf_body_weight_change(general_properties: GeneralProperties) -> float:
        """
        Calculates the body weight change for calves.

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        float
            The daily body weight growth for calves (kg).
        """
        return general_properties.birth_weight / Growth.WEAN_DAY

    @staticmethod
    def calculate_non_pregnant_heifer_body_weight_change(general_properties: GeneralProperties) -> float:
        """
        Calculates the body weight change for non-pregnant heifers.

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        float
            The daily body weight growth for non-pregnant heifers (kg).

        References
        ----------
        Life cycle pseudocode @[A.1A.C.6] in pseudocode, which are from Fox et al. 1999 and NRC 2001.

        Notes
        -----
        For animals over 55% of their mature body weight, the equation results in a negative return.
        Therefore, when the result is negative, the minimum BW change constant is returned instead.
        """
        divisor = max(1, abs(Growth.TARGET_HEIFER_PREGNANT_DAY - general_properties.days_born))
        return max(
            (0.55 * 0.96 * general_properties.mature_body_weight - 0.96 * general_properties.body_weight) / divisor,
            AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE,
        )

    @staticmethod
    def calculate_pregnant_heifer_body_weight_change(
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float]:
        """
        Calculates the body weight change for pregnant heifers.

        Parameters
        ----------
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        tuple[float, float]
            The daily body weight growth for pregnant heifers (kg), and the updated conceptus weight (kg).

        References
        ----------
        Life cycle pseudocode @[A.1A.C.9]
        """
        target_average_daily_growth_pregnant_heifer = Growth._calculate_pregnant_heifer_target_daily_growth(
            reproduction_properties, general_properties
        )

        (conceptus_growth, reproduction_properties.conceptus_weight) = (
            Growth._calculate_pregnant_heifer_conceptus_growth(reproduction_properties, general_properties)
        )

        return (
            target_average_daily_growth_pregnant_heifer + conceptus_growth,
            reproduction_properties.conceptus_weight,
        )

    @staticmethod
    def calculate_cow_body_weight_change(
        animal_growth_properties: GrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float, float]:
        """
        Calculates the body weight change for cows.

        Parameters
        ----------
        animal_growth_properties: GrowthProperties
            Animal properties that are related to body weight growth.
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        tuple[float, float, float]
            The daily body weight growth for pregnant heifers (kg), the updated conceptus weight (kg), and the updated
            tissue changed (kg).

        References
        ----------
        Life cycle pseudocode @[A.1A.C.56/57/58]
        """
        (conceptus_growth, reproduction_properties.conceptus_weight, animal_growth_properties.tissue_changed) = (
            Growth._calculate_cow_conceptus_growth(
                animal_growth_properties, reproduction_properties, general_properties
            )
        )

        target_adg_cow = Growth._calculate_cow_target_daily_growth(reproduction_properties, general_properties)

        (body_weight_tissue, animal_growth_properties.tissue_changed) = (
            Growth._calculate_cow_body_weight_tissue_change(
                animal_growth_properties, reproduction_properties, general_properties
            )
        )

        return (
            target_adg_cow + conceptus_growth + body_weight_tissue,
            reproduction_properties.conceptus_weight,
            animal_growth_properties.tissue_changed,
        )

    @staticmethod
    def _calculate_pregnant_heifer_conceptus_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> tuple[float, float]:
        """
        Calculates the conceptus growth for pregnant heifers.

        Parameters
        ----------
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        tuple[float, float]
            The conceptus growth for pregnant heifers (kg), and the updated conceptus weight (kg).
        """
        updated_conceptus_weight = reproduction_properties.conceptus_weight
        if general_properties.days_in_preg == reproduction_properties.gestation_length:
            conceptus_growth = -reproduction_properties.conceptus_weight
            updated_conceptus_weight = 0

        elif general_properties.days_in_preg > 50:
            conceptus_total_weight = (
                0.0148 * reproduction_properties.gestation_length - 2.408
            ) * reproduction_properties.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (reproduction_properties.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (general_properties.days_in_preg - 50) ** 2
            updated_conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0
        return conceptus_growth, updated_conceptus_weight

    @staticmethod
    def _calculate_cow_conceptus_growth(
        animal_growth_properties: GrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float, float]:
        """
        Calculates the conceptus growth for cows.

        Parameters
        ----------
        animal_growth_properties: GrowthProperties
            Animal properties that are related to body weight growth.
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        tuple[float, float, float]
            The conceptus growth for pregnant heifers (kg), the updated conceptus weight (kg), and the updated
            tissue changed (kg).
        """
        updated_tissue_change = (
            0.0
            if general_properties.days_in_preg == reproduction_properties.gestation_length
            else animal_growth_properties.tissue_changed
        )

        conceptus_growth, updated_conceptus_weight = Growth._calculate_pregnant_heifer_conceptus_growth(
            reproduction_properties, general_properties
        )

        return conceptus_growth, updated_conceptus_weight, updated_tissue_change

    @staticmethod
    def _calculate_pregnant_heifer_target_daily_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> float:
        """
        Calculates the target daily growth for pregnant heifers.

        Parameters
        ----------
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        float
            The daily growth rate for pregnant heifers (kg).
        """
        divisor = max(1, abs(reproduction_properties.gestation_length - general_properties.days_in_preg))
        return (0.82 * 0.96 * general_properties.mature_body_weight - 0.96 * general_properties.body_weight) / divisor

    @staticmethod
    def _calculate_cow_target_daily_growth(
        reproduction_properties: ReproductionProperties, general_properties: GeneralProperties
    ) -> float:
        """
        Calculates the target daily growth for cows.

        Parameters
        ----------
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        float
            The daily growth rate for cows (kg).
        """
        if reproduction_properties.calves == 1:
            if general_properties.days_in_preg < 1:
                target_adg_cow = (
                    (0.92 - 0.82)
                    * 0.96
                    * general_properties.mature_body_weight
                    / reproduction_properties.calving_interval
                )
            else:
                target_adg_cow = (0.92 * general_properties.mature_body_weight - general_properties.body_weight) / (
                    reproduction_properties.gestation_length - general_properties.days_in_preg + 1
                )
        elif reproduction_properties.calves == 2:
            if general_properties.days_in_preg < 1:
                target_adg_cow = (
                    (1 - 0.92) * 0.96 * general_properties.mature_body_weight / reproduction_properties.calving_interval
                )
            else:
                target_adg_cow = (general_properties.mature_body_weight - general_properties.body_weight) / (
                    reproduction_properties.gestation_length - general_properties.days_in_preg + 1
                )
        else:
            target_adg_cow = 0
        return target_adg_cow

    @staticmethod
    def _calculate_cow_body_weight_tissue_change(
        animal_growth_properties: GrowthProperties,
        reproduction_properties: ReproductionProperties,
        general_properties: GeneralProperties,
    ) -> tuple[float, float]:
        """
        Calculates the body weight tissue growth for cows.

        Parameters
        ----------
        animal_growth_properties: GrowthProperties
            Animal properties that are related to body weight growth.
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        tuple[float, float]
            The body weight tissue growth for cows (kg), and the updated tissue changed (kg).
        """
        updated_tissue_changed = animal_growth_properties.tissue_changed
        if general_properties.is_milking:
            if reproduction_properties.calves == 1:
                body_weight_tissue = -20 / 65 * np.exp(1 - general_properties.days_in_milk / 65) + 20 / (
                    65**2
                ) * general_properties.days_in_milk * np.exp(1 - general_properties.days_in_milk / 65)
                if general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        20 * general_properties.days_in_milk / 65 * np.exp(1 - general_properties.days_in_milk / 65)
                    )
            else:
                body_weight_tissue = -40 / 70 * np.exp(1 - general_properties.days_in_milk / 70) + 40 / (
                    70**2
                ) * general_properties.days_in_milk * np.exp(1 - general_properties.days_in_milk / 70)
                if general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        40 * general_properties.days_in_milk / 70 * np.exp(1 - general_properties.days_in_milk / 70)
                    )
        else:
            body_weight_tissue = animal_growth_properties.tissue_changed / (
                reproduction_properties.gestation_length - general_properties.dry_off_day_of_pregnancy
            )
        return body_weight_tissue, updated_tissue_changed
