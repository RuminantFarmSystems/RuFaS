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

        Notes:
        - Calculation of amount of P in diet greater than animal requirements (A.1G.A.1).
        - Change in body P reserves (g), must be <= 0 (A.1G.A.2).
        - Calculate total P in the animal (A.1G.A.3).
        """
        animal_status.phosphorus_excess = max(animal_status.phosphorus_intake - animal_status.phosphorus_requirement, 0)
        previous_phosphorus_reserves = animal_status.phosphorus_reserves

        if animal_status.phosphorus_intake < animal_status.phosphorus_requirement:
            animal_status.phosphorus_reserves = animal_status.phosphorus_intake \
                - animal_status.phosphorus_requirement + animal_status.phosphorus_reserves
        elif animal_status.phosphorus_intake >= animal_status.phosphorus_requirement and \
                animal_status.phosphorus_reserves < 0:
            animal_status.phosphorus_reserves = 0.7 * animal_status.phosphorus_excess \
                + animal_status.phosphorus_reserves
        else:
            animal_status.phosphorus_reserves = 0

        animal_status.total_phosphorus = animal_status.total_phosphorus + animal_status.gestational_phosphorus \
            + animal_status.phosphorus_retained_for_growth + (animal_status.phosphorus_reserves
                                                              - previous_phosphorus_reserves)

    def calculate_phosphorus_requirements(self, animal_status: AnimalPhosphorusStatus, dry_matter_intake: float
                                          ) -> None:
        """Calculates animal's phosophorus requirements"""
        self._calculate_endogenous_loss_phosphorus(animal_status, dry_matter_intake)
        urine_production_phosphorus = 0.000002 * animal_status.body_weight * GeneralConstants.KG_TO_GRAMS
        self._calculate_phosphorus_retained_for_growth(animal_status)
        self._calculate_gestational_phosphorus(animal_status)
        milk_phosphorus = self._calculate_milk_phosphorus(animal_status)
        absorbed_phosphorus = self._calculate_absorbed_phosphorus(animal_status, milk_phosphorus,
                                                                  urine_production_phosphorus)
        self._calculate_animal_phosphorus_requirement(animal_status, absorbed_phosphorus)

    def _calculate_endogenous_loss_phosphorus(self, animal_status: AnimalPhosphorusStatus, dry_matter_intake: float
                                              ) -> None:
        """Calculates phosphorus required for endogenous loss based on animal type.

        Notes
        -----
        Calculation of the amount of P required for endogenous losses (g).
        - If animal is a CALF, HEIFER_I, HEIFER_II, or HEIFER_III -> (A.1A-D.E.1).
        - If animal is a DRY_COW or LAC_COW -> (A.1EF.E.1).
        """
        if animal_status.animal_type in CALVES_AND_HEIFERS:
            animal_status.endogenous_loss_phosphorus = 0.0008 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS
        else:
            animal_status.endogenous_loss_phosphorus = 0.001 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS

    def _calculate_phosphorus_retained_for_growth(animal_status: AnimalPhosphorusStatus) -> None:
        """Calculates phosphorus retained for growth based on animal type.

        Notes
        -----
        Calculation of the absorbed P retained for growth (g) (A.1A-F.E.3).
        """
        if animal_status.animal_type in CALVES_AND_HEIFERS or animal_status.body_weight < \
           animal_status.mature_body_weight:
            animal_status.phosphorus_retained_for_growth = (
                (0.0012 + 0.004635 * (animal_status.mature_body_weight**0.22) * (animal_status.body_weight ** (-0.22)))
                * animal_status.daily_growth
                / 0.96
                * GeneralConstants.KG_TO_GRAMS
            )
        else:
            animal_status.phosphorus_retained_for_growth = 0

    def _calculate_gestational_phosphorus(animal_status: AnimalPhosphorusStatus) -> None:
        """Calculates an animal's gestational phosphorus.

        Notes
        -----
        Calculation of absorbed P retained for fetal growth (g) (A.1C-F.E.4).
        """
        if animal_status.days_in_preg >= 190:
            exp_1 = (0.05527 - 0.000075 * animal_status.days_in_preg) * animal_status.days_in_preg
            exp_2 = (0.05527 - 0.000075 * (animal_status.days_in_preg - 1)) * (animal_status.days_in_preg - 1)
            animal_status.gestational_phosphorus = (0.00002743 * math.exp(exp_1) - 0.00002743
                                                    * math.exp(exp_2)) * GeneralConstants.KG_TO_GRAMS
            animal_status.gestational_phosphorus_for_calf += animal_status.gestational_phosphorus
        else:
            animal_status.gestational_phosphorus = 0

    def _calculate_milk_phosphorus(animal_status: AnimalPhosphorusStatus) -> float:
        """Calculates an animal's milk phosphorus.

        Notes
        -----
        Calculation of the amount of P in milk per animal (g) (A.1E.E.5).
        """
        if animal_status.milking:
            return 0.0009 * animal_status.estimated_daily_milk_produced * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    def _calculate_absorbed_phosphorus(animal_status: AnimalPhosphorusStatus, milk_phosphorus: float,
                                       urine_production_phosphorus: float) -> float:
        """Calculates absorbed phosphorus based on animal type.

        Notes
        -----
        Calculation of absorbed P required by the animal (g).
        - Cows: (A.1EF.E.6).
        - Calves, HeiferIs, HeiferIIs, HeiferIIIs: (A.1A-F.E.6).
        """
        if animal_status.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW]:
            return urine_production_phosphorus + animal_status.endogenous_loss_phosphorus \
                + animal_status.phosphorus_retained_for_growth + animal_status.gestational_phosphorus + milk_phosphorus
        elif animal_status.animal_type in [AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            return urine_production_phosphorus + animal_status.endogenous_loss_phosphorus \
                + animal_status.phosphorus_retained_for_growth + animal_status.gestational_phosphorus
        else:
            return urine_production_phosphorus + animal_status.endogenous_loss_phosphorus \
                + animal_status.phosphorus_retained_for_growth

    def _calculate_animal_phosphorus_requirement(animal_status: AnimalPhosphorusStatus,
                                                 absorbed_phosphorus: float) -> None:
        """Calculates an animal's phosphorus requirement by animal type.

        Notes
        -----
        Calculates the requirement of P from the ration (g).
        - Calves: (A.1A.E.7).
        - HeiferIs, HeiferIIs, HeiferIIIs: (A.1B-D.E.7).
        - Cows: (A.1EF.E.7).
        """
        if animal_status.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW]:
            if animal_status.milking:
                animal_status.phosphorus_requirement = (
                    absorbed_phosphorus / (1.86696 - 5.01238 * animal_status.ration_phosphorus_concentration + 5.12286
                                           * animal_status.ration_phosphorus_concentration**2)
                )
        elif animal_status.animal_type == AnimalType.CALF:
            animal_status.phosphorus_requirement = absorbed_phosphorus / 0.90
        else:
            animal_status.phosphorus_requirement = absorbed_phosphorus / 0.664
