import numpy as np

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.growth import GrowthInputs, GrowthOutputs
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class Growth:
    """
    Handles updating the body weight growth related animal attributes.

    Attributes
    ----------
    daily_growth: float
        The body weight of the animal (kg).
    tissue_changed: float
        Body weight change due to tissue mobilization (kg).
    """

    daily_growth: float = 0.0
    tissue_changed: float = 0.0
    body_weight_history: list[BodyWeightHistory] = []

    def __init__(
        self,
        daily_growth: float = 0.0,
        tissue_changed: float = 0.0,
        body_weight_history: list[BodyWeightHistory] = None,
    ) -> None:
        self.daily_growth = daily_growth if daily_growth else 0.0
        self.tissue_changed = tissue_changed if tissue_changed else 0.0
        self.body_weight_history = body_weight_history if body_weight_history else []

    def evaluate_body_weight_change(
        self,
        growth_inputs: GrowthInputs,
        time: RufasTime,
    ) -> GrowthOutputs:
        """
        Handles an animal's daily growth updates.

        Notes
        -----
        Calf growth - [AN.BWT.1]
        Non-preg heifer growth - [AN.BWT.2]
        Preg heifer growth -  [AN.BWT.3]
        1st & 2nd parity cow growth - [AN.BWT.4]
        Parity 3+ cow growth - [AN.BWT.5]

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        animal_growth_properties: GrowthProperties
            Animal properties that are related to body weight growth.
        reproduction_properties: ReproductionProperties
            Animal properties that are related to animal reproduction.
        time : RufasTime
            RufasTime instance containing the current time of the simulation.

        Returns
        -------
        tuple[AnimalGrowthProperties, ReproductionProperties, GeneralProperties]
            The updated animal growth properties, reproduction properties, and the general properties of the animal
            after the growth-related routines for the current day.
        """
        growth_outputs = GrowthOutputs(
            body_weight=growth_inputs.body_weight,
            conceptus_weight=growth_inputs.conceptus_weight,
            events=AnimalEvents(),
        )

        is_non_pregnant_heifer = not growth_inputs.is_pregnant and (
            growth_inputs.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III)
        )
        is_pregnant_heifer = growth_inputs.is_pregnant and (
            growth_inputs.animal_type in (AnimalType.HEIFER_II, AnimalType.HEIFER_III)
        )
        supported_animal_types = (
            AnimalType.CALF,
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.LAC_COW,
            AnimalType.DRY_COW,
        )
        if growth_inputs.animal_type not in supported_animal_types:
            om = OutputManager()
            om.add_error(
                "Unexpected Animal Type",
                f"{growth_inputs.animal_type} is not a valid animal type.",
                {
                    "class": Growth.__class__.__name__,
                    "function": Growth.evaluate_body_weight_change.__name__,
                },
            )
            raise ValueError(f"{growth_inputs.animal_type} is not a valid animal type.")
        if growth_inputs.animal_type == AnimalType.CALF:
            self.daily_growth = self.calculate_calf_body_weight_change(growth_inputs)
            growth_outputs.body_weight += self.daily_growth

        elif is_non_pregnant_heifer:
            self.daily_growth = self.calculate_non_pregnant_heifer_body_weight_change(growth_inputs)
            growth_outputs.body_weight += self.daily_growth

        elif is_pregnant_heifer:
            if growth_inputs.body_weight < growth_inputs.mature_body_weight:
                self.daily_growth, growth_outputs.conceptus_weight = self.calculate_pregnant_heifer_body_weight_change(
                    growth_inputs
                )
                growth_outputs.body_weight += self.daily_growth
            else:
                growth_outputs.body_weight = growth_inputs.mature_body_weight
                growth_outputs.events.add_event(
                    growth_inputs.days_born, time.simulation_day, animal_constants.MATURE_BODY_WEIGHT_REGULAR
                )

        elif growth_inputs.animal_type.is_cow:
            (
                self.daily_growth,
                growth_outputs.conceptus_weight,
                self.tissue_changed,
            ) = self.calculate_cow_body_weight_change(growth_inputs)
            growth_outputs.body_weight += self.daily_growth
        else:
            om = OutputManager()
            om.add_error(
                "Unexpected execution path in process_digestion evaluating animal type",
                f"Supported animal types are {supported_animal_types}. Got {growth_inputs.animal_type}",
                {
                    "class": Growth.__class__.__name__,
                    "function": Growth.evaluate_body_weight_change.__name__,
                },
            )
            raise RuntimeError(
                f"Unexpected execution path in process_digestion. Animal type: {growth_inputs.animal_type}"
            )

        self.body_weight_history.append(
            BodyWeightHistory(
                simulation_day=time.simulation_day,
                days_born=growth_inputs.days_born,
                body_weight=growth_outputs.body_weight,
            )
        )
        return growth_outputs

    def calculate_calf_body_weight_change(self, growth_inputs: GrowthInputs) -> float:
        """
        Calculates the body weight change for calves.

        Notes
        ------
        [AN.BWT.7]


        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        float
            The daily body weight growth for calves (kg).
        """
        return growth_inputs.birth_weight / AnimalConfig.wean_day

    def calculate_non_pregnant_heifer_body_weight_change(self, growth_inputs: GrowthInputs) -> float:
        """
        Calculates the body weight change of heifers due to growth.

        Notes
        ------
        [AN.BWT.8]
        [AN.BWT.9]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

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
        divisor = abs(AnimalConfig.target_heifer_pregnant_day - growth_inputs.days_born)
        if divisor == 0:
            divisor = 1
        return max(
            (0.55 * 0.96 * growth_inputs.mature_body_weight - 0.96 * growth_inputs.body_weight) / divisor,
            AnimalModuleConstants.MINIMUM_HEIFER_DAILY_GROWTH_RATE,
        )

    def calculate_pregnant_heifer_body_weight_change(self, growth_inputs: GrowthInputs) -> tuple[float, float]:
        """
        Calculates the body weight change for pregnant heifers.

        Notes
        -----
        [AN.BWT.3]
        [AN.BWT.9]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        tuple[float, float]
            The daily body weight growth for pregnant heifers (kg), and the updated conceptus weight (kg).


        """
        target_average_daily_growth_pregnant_heifer = self._calculate_pregnant_heifer_target_daily_growth(growth_inputs)

        conceptus_growth, updated_conceptus_weight = self._calculate_pregnant_heifer_conceptus_growth(growth_inputs)

        return (
            target_average_daily_growth_pregnant_heifer + conceptus_growth,
            updated_conceptus_weight,
        )

    def calculate_cow_body_weight_change(self, growth_inputs: GrowthInputs) -> tuple[float, float, float]:
        """
        Calculates the body weight change for cows.

        Notes
        -----
        [AN.BWT.4]
        [AN.BWT.5]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        tuple[float, float, float]
            The daily body weight growth for pregnant heifers (kg), the updated conceptus weight (kg), and the updated
            tissue changed (kg).

        """
        conceptus_growth, updated_conceptus_weight, self.tissue_changed = self._calculate_cow_conceptus_growth(
            growth_inputs
        )

        target_adg_cow = self._calculate_cow_target_daily_growth(growth_inputs)

        body_weight_tissue, self.tissue_changed = self._calculate_cow_body_weight_tissue_change(growth_inputs)

        return (
            target_adg_cow + conceptus_growth + body_weight_tissue,
            updated_conceptus_weight,
            self.tissue_changed,
        )

    def _calculate_pregnant_heifer_conceptus_growth(self, growth_inputs: GrowthInputs) -> tuple[float, float]:
        """
        Calculates the conceptus growth for pregnant heifers.

        Notes
        --------
        Total conceptus weight - [AN.BWT.14]
        conceptus parameter - [AN.BWT.15]
        Conceptus growth - [AN.BWT.16]
        Conceptus weight change at parturition - [AN.BWT.17]


        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        tuple[float, float]
            The conceptus growth for pregnant heifers (kg), and the updated conceptus weight (kg).
        """
        updated_conceptus_weight = growth_inputs.conceptus_weight
        if growth_inputs.days_in_pregnancy == growth_inputs.gestation_length:
            conceptus_growth = -growth_inputs.conceptus_weight
            updated_conceptus_weight = 0

        elif growth_inputs.days_in_pregnancy > 50:
            conceptus_total_weight = (0.0148 * growth_inputs.gestation_length - 2.408) * growth_inputs.calf_birth_weight
            conceptus_param = conceptus_total_weight ** (1 / 3) / (growth_inputs.gestation_length - 50)
            conceptus_growth = 3 * conceptus_param**3 * (growth_inputs.days_in_pregnancy - 50) ** 2
            updated_conceptus_weight += conceptus_growth
        else:
            conceptus_growth = 0
        return conceptus_growth, updated_conceptus_weight

    def _calculate_cow_conceptus_growth(self, growth_inputs: GrowthInputs) -> tuple[float, float, float]:
        """
        Calculates the conceptus growth for cows.

        Notes
        -------
        Total conceptus weight - [AN.BWT.14]
        conceptus parameter - [AN.BWT.15]
        Conceptus growth - [AN.BWT.16]
        Conceptus weight change at parturition - [AN.BWT.17]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        tuple[float, float, float]
            The conceptus growth for pregnant heifers (kg), the updated conceptus weight (kg), and the updated
            tissue changed (kg).
        """
        updated_tissue_change = (
            0.0 if growth_inputs.days_in_pregnancy == growth_inputs.gestation_length else self.tissue_changed
        )

        conceptus_growth, updated_conceptus_weight = self._calculate_pregnant_heifer_conceptus_growth(growth_inputs)

        return conceptus_growth, updated_conceptus_weight, updated_tissue_change

    def _calculate_pregnant_heifer_target_daily_growth(self, growth_inputs: GrowthInputs) -> float:
        """
        Calculates the target daily growth for pregnant heifers.

        Notes
        ----------
        [AN.BWT.9]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        float
            The daily growth rate for pregnant heifers (kg).
        """
        divisor = abs(growth_inputs.gestation_length - growth_inputs.days_in_pregnancy)
        if divisor == 0:
            divisor = 1
        return (0.82 * 0.96 * growth_inputs.mature_body_weight - 0.96 * growth_inputs.body_weight) / divisor

    def _calculate_cow_target_daily_growth(self, growth_inputs: GrowthInputs) -> float:
        """
        Calculates the target daily growth for cows.

        Notes
        ---------
        [AN.BWT.10]
        [AN.BWT.11]
        [AN.BWT.12]
        [AN.BWT.13]


        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        float
            The daily growth rate for cows (kg).
        """
        if growth_inputs.calves == 1:
            if growth_inputs.days_in_pregnancy < 1:
                target_adg_cow = (
                    (0.92 - 0.82) * 0.96 * growth_inputs.mature_body_weight / growth_inputs.calving_interval
                )
            else:
                target_adg_cow = (0.92 * growth_inputs.mature_body_weight - growth_inputs.body_weight) / (
                    growth_inputs.gestation_length - growth_inputs.days_in_pregnancy + 1
                )
        elif growth_inputs.calves == 2:
            if growth_inputs.days_in_pregnancy < 1:
                target_adg_cow = (1 - 0.92) * 0.96 * growth_inputs.mature_body_weight / growth_inputs.calving_interval
            else:
                target_adg_cow = (growth_inputs.mature_body_weight - growth_inputs.body_weight) / (
                    growth_inputs.gestation_length - growth_inputs.days_in_pregnancy + 1
                )
        else:
            target_adg_cow = 0
        return target_adg_cow

    def _calculate_cow_body_weight_tissue_change(self, growth_inputs: GrowthInputs) -> tuple[float, float]:
        """
        Calculates the body weight tissue growth for cows.

        Notes
        --------
        [AN.BWT.18]
        [AN.BWT.19]
        [AN.BWT.20]

        Parameters
        ----------
        growth_inputs: GrowthInputs
            Animal properties related to body weight growth.

        Returns
        -------
        tuple[float, float]
            The body weight tissue growth for cows (kg), and the updated tissue changed (kg).
        """
        updated_tissue_changed = self.tissue_changed
        if growth_inputs.is_milking:
            if growth_inputs.calves == 1:
                body_weight_tissue = -20 / 65 * np.exp(1 - growth_inputs.days_in_milk / 65) + 20 / (
                    65**2
                ) * growth_inputs.days_in_milk * np.exp(1 - growth_inputs.days_in_milk / 65)

                if growth_inputs.days_in_pregnancy == AnimalConfig.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        20 * growth_inputs.days_in_milk / 65 * np.exp(1 - growth_inputs.days_in_milk / 65)
                    )
            else:
                body_weight_tissue = -40 / 70 * np.exp(1 - growth_inputs.days_in_milk / 70) + 40 / (
                    70**2
                ) * growth_inputs.days_in_milk * np.exp(1 - growth_inputs.days_in_milk / 70)

                if growth_inputs.days_in_pregnancy == AnimalConfig.dry_off_day_of_pregnancy - 1:
                    updated_tissue_changed = (
                        40 * growth_inputs.days_in_milk / 70 * np.exp(1 - growth_inputs.days_in_milk / 70)
                    )
        else:
            body_weight_tissue = self.tissue_changed / (
                growth_inputs.gestation_length - AnimalConfig.dry_off_day_of_pregnancy
            )
        return body_weight_tissue, updated_tissue_changed
