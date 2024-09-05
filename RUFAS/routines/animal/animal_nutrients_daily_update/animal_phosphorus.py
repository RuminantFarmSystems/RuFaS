from __future__ import annotations
import math
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.animal_nutrients_daily_update.animal_phosphorus_status import AnimalPhosphorusStatus
from RUFAS.routines.animal.animal_types import AnimalType

CALVES_AND_HEIFERS = [AnimalType.CALF, AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III]
HEIFERS_AND_COWS = [AnimalType.DRY_COW, AnimalType.LAC_COW, AnimalType.HEIFER_II, AnimalType.HEIFER_II]


class AnimalPhosphorus:

    def perform_daily_phosphorus_update(self, animal_status: AnimalPhosphorusStatus) -> None:
        """Runs the daily phosphorus update for the animal.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1G.A.1, A.1G.A.2, A.1G.A.3.

        Notes
        -----
        - Change in body P reserves (g), must be <= 0

        """
        animal_status.phosphorus_excess_in_diet = max(
            animal_status.phosphorus_intake - animal_status.phosphorus_requirement, 0
        )
        previous_phosphorus_reserves = animal_status.phosphorus_reserves

        if animal_status.phosphorus_intake < animal_status.phosphorus_requirement:
            animal_status.phosphorus_reserves = (
                animal_status.phosphorus_intake
                - animal_status.phosphorus_requirement
                + animal_status.phosphorus_reserves
            )
        elif (
            animal_status.phosphorus_intake >= animal_status.phosphorus_requirement
            and animal_status.phosphorus_reserves < 0
        ):
            animal_status.phosphorus_reserves = (
                0.7 * animal_status.phosphorus_excess_in_diet + animal_status.phosphorus_reserves
            )
        else:
            animal_status.phosphorus_reserves = 0.0

        animal_status.total_phosphorus_in_animal = (
            animal_status.total_phosphorus_in_animal
            + animal_status.phosphorus_for_gestation
            + animal_status.phosphorus_for_growth
            + (animal_status.phosphorus_reserves - previous_phosphorus_reserves)
        )

    def calculate_phosphorus_requirements(
        self, animal_status: AnimalPhosphorusStatus, dry_matter_intake: float
    ) -> None:
        """Calculates animal's phosophorus requirements"""
        self._calculate_phosphorus_endogenous_loss(animal_status, dry_matter_intake)
        urine_production_phosphorus = 0.000002 * animal_status.body_weight * GeneralConstants.KG_TO_GRAMS
        self._calculate_phosphorus_for_growth(animal_status)
        self._calculate_gestational_phosphorus(animal_status)
        milk_phosphorus = self._calculate_milk_phosphorus(animal_status)
        absorbed_phosphorus = self._calculate_absorbed_phosphorus(
            animal_status, milk_phosphorus, urine_production_phosphorus
        )
        self._calculate_animal_phosphorus_requirement(animal_status, absorbed_phosphorus)

    def _calculate_phosphorus_endogenous_loss(
        self, animal_status: AnimalPhosphorusStatus, dry_matter_intake: float
    ) -> None:
        """Calculates phosphorus required for endogenous loss based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A-D.E.1, A.1EF.E.1.
        """
        if animal_status.animal_type in CALVES_AND_HEIFERS:
            animal_status.phosphorus_endogenous_loss = 0.0008 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS
        else:
            animal_status.phosphorus_endogenous_loss = 0.001 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS

    def _calculate_phosphorus_for_growth(self, animal_status: AnimalPhosphorusStatus) -> None:
        """Calculates phosphorus retained for growth based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1A-F.E.3.
        """
        if (
            animal_status.animal_type in CALVES_AND_HEIFERS
            or animal_status.body_weight < animal_status.mature_body_weight
        ):
            animal_status.phosphorus_for_growth = (
                (0.0012 + 0.004635 * (animal_status.mature_body_weight**0.22) * (animal_status.body_weight ** (-0.22)))
                * animal_status.daily_growth
                / 0.96
                * GeneralConstants.KG_TO_GRAMS
            )
        else:
            animal_status.phosphorus_for_growth = 0.0

    def _calculate_gestational_phosphorus(self, animal_status: AnimalPhosphorusStatus) -> None:
        """Calculates an animal's gestational phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1C-F.E.4.
        """
        if animal_status.days_in_preg >= 190:
            exp_1 = (0.05527 - 0.000075 * animal_status.days_in_preg) * animal_status.days_in_preg
            exp_2 = (0.05527 - 0.000075 * (animal_status.days_in_preg - 1)) * (animal_status.days_in_preg - 1)
            animal_status.phosphorus_for_gestation = (
                0.00002743 * math.exp(exp_1) - 0.00002743 * math.exp(exp_2)
            ) * GeneralConstants.KG_TO_GRAMS
            animal_status.phosphorus_for_gestation_required_for_calf += animal_status.phosphorus_for_gestation
        else:
            animal_status.phosphorus_for_gestation = 0.0

    def _calculate_milk_phosphorus(self, animal_status: AnimalPhosphorusStatus) -> float:
        """Calculates an animal's milk phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1E.E.5.
        """
        if animal_status.milking:
            return 0.0009 * animal_status.estimated_daily_milk_produced * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    def _calculate_absorbed_phosphorus(
        self, animal_status: AnimalPhosphorusStatus, milk_phosphorus: float, urine_production_phosphorus: float
    ) -> float:
        """Calculates absorbed phosphorus based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1EF.E.6, A.1A-F.E.6.
        """
        if animal_status.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW]:
            return (
                urine_production_phosphorus
                + animal_status.phosphorus_endogenous_loss
                + animal_status.phosphorus_for_growth
                + animal_status.phosphorus_for_gestation
                + milk_phosphorus
            )
        elif animal_status.animal_type in [AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            return (
                urine_production_phosphorus
                + animal_status.phosphorus_endogenous_loss
                + animal_status.phosphorus_for_growth
                + animal_status.phosphorus_for_gestation
            )
        else:
            return (
                urine_production_phosphorus
                + animal_status.phosphorus_endogenous_loss
                + animal_status.phosphorus_for_growth
            )

    def _calculate_animal_phosphorus_requirement(
        self, animal_status: AnimalPhosphorusStatus, absorbed_phosphorus: float
    ) -> None:
        """Calculates an animal's phosphorus requirement by animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A.E.7, A.1B-D.E.7, A.1EF.E.7.
        """
        if animal_status.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW]:
            if animal_status.milking:
                animal_status.phosphorus_requirement = absorbed_phosphorus / (
                    1.86696
                    - 5.01238 * animal_status.ration_phosphorus_concentration
                    + 5.12286 * animal_status.ration_phosphorus_concentration**2
                )
        elif animal_status.animal_type == AnimalType.CALF:
            animal_status.phosphorus_requirement = absorbed_phosphorus / 0.90
        else:
            animal_status.phosphorus_requirement = absorbed_phosphorus / 0.664
