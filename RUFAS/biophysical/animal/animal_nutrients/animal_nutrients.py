from __future__ import annotations

import math

from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.general_constants import GeneralConstants

CALVES_AND_HEIFERS = [AnimalType.CALF, AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III]
HEIFERS_AND_COWS = [AnimalType.DRY_COW, AnimalType.LAC_COW, AnimalType.HEIFER_II, AnimalType.HEIFER_II]


class AnimalNutrients:

    @staticmethod
    def perform_daily_phosphorus_update(
        animal_status: NutrientProperties, general_properties: GeneralProperties
    ) -> NutrientProperties:
        """Manages animal's daily phosphorus update."""
        dry_matter_intake = AnimalNutrients._get_dry_matter_intake()
        phosphorus_status = AnimalNutrients._calculate_phosphorus_requirements(
            general_properties, animal_status, dry_matter_intake
        )
        phosphorus_status = AnimalNutrients._calculate_total_animal_phosphorus(phosphorus_status)

        return phosphorus_status

    @staticmethod
    def _get_dry_matter_intake() -> float:
        """Get ration data for animal dry matter intake."""
        # Not sure where ration will be or how it will be tied to a particular animal (currently done by pen)
        # But assuming it's not an attribute of the animal, we will need this info from ration.
        return 0.0

    @staticmethod
    def _calculate_total_animal_phosphorus(phosphorus_status: NutrientProperties) -> NutrientProperties:
        """Calculates the total phosphorus for the animal.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1G.A.1, A.1G.A.2, A.1G.A.3.

        Notes
        -----
        - Change in body P reserves (g), must be <= 0

        """
        phosphorus_status.phosphorus_excess_in_diet = max(
            phosphorus_status.phosphorus_intake - phosphorus_status.phosphorus_requirement, 0
        )
        previous_phosphorus_reserves = phosphorus_status.phosphorus_reserves
        if phosphorus_status.phosphorus_intake < phosphorus_status.phosphorus_requirement:
            phosphorus_status.phosphorus_reserves = (
                phosphorus_status.phosphorus_intake
                - phosphorus_status.phosphorus_requirement
                + phosphorus_status.phosphorus_reserves
            )
        elif (
            phosphorus_status.phosphorus_intake >= phosphorus_status.phosphorus_requirement
            and phosphorus_status.phosphorus_reserves < 0
        ):
            phosphorus_status.phosphorus_reserves = (
                0.7 * phosphorus_status.phosphorus_excess_in_diet + phosphorus_status.phosphorus_reserves
            )
        else:
            phosphorus_status.phosphorus_reserves = 0.0
        phosphorus_status.total_phosphorus_in_animal = (
            phosphorus_status.total_phosphorus_in_animal
            + phosphorus_status.phosphorus_for_gestation
            + phosphorus_status.phosphorus_for_growth
            + (phosphorus_status.phosphorus_reserves - previous_phosphorus_reserves)
        )

        return phosphorus_status

    @staticmethod
    def _calculate_phosphorus_requirements(
        general_properties: GeneralProperties, phosphorus_status: NutrientProperties, dry_matter_intake: float
    ) -> NutrientProperties:
        """Calculates animal's phosophorus requirements"""
        phosphorus_status.phosphorus_endogenous_loss = AnimalNutrients._calculate_phosphorus_endogenous_loss(
            general_properties, dry_matter_intake
        )
        urine_production_phosphorus = 0.000002 * general_properties.body_weight * GeneralConstants.KG_TO_GRAMS
        phosphorus_status.phosphorus_for_growth = AnimalNutrients._calculate_phosphorus_for_growth(general_properties)
        phosphorus_status.phosphorus_for_gestation = AnimalNutrients._calculate_gestational_phosphorus(
            general_properties
        )
        phosphorus_status.phosphorus_for_gestation_required_for_calf += phosphorus_status.phosphorus_for_gestation
        milk_phosphorus = AnimalNutrients._calculate_milk_phosphorus(general_properties)
        absorbed_phosphorus = AnimalNutrients._calculate_absorbed_phosphorus(
            general_properties, phosphorus_status, milk_phosphorus, urine_production_phosphorus
        )
        phosphorus_status.phosphorus_requirement = AnimalNutrients._calculate_animal_phosphorus_requirement(
            general_properties, phosphorus_status, absorbed_phosphorus
        )

        return phosphorus_status

    @staticmethod
    def _calculate_phosphorus_endogenous_loss(
        general_properties: GeneralProperties, dry_matter_intake: float
    ) -> float:
        """Calculates phosphorus required for endogenous loss based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A-D.E.1, A.1EF.E.1.
        """
        if AnimalNutrients._is_calf_or_heifer(general_properties.animal_type):
            return 0.0008 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.001 * dry_matter_intake * GeneralConstants.KG_TO_GRAMS

    @staticmethod
    def _calculate_phosphorus_for_growth(general_properties: GeneralProperties) -> float:
        """Calculates phosphorus retained for growth based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1A-F.E.3.
        """
        if (
            AnimalNutrients._is_calf_or_heifer(general_properties.animal_type)
            or general_properties.body_weight < general_properties.mature_body_weight
        ):
            return (
                (
                    0.0012
                    + 0.004635
                    * (general_properties.mature_body_weight**0.22)
                    * (general_properties.body_weight ** (-0.22))
                )
                * general_properties.daily_growth
                / 0.96
                * GeneralConstants.KG_TO_GRAMS
            )
        else:
            return 0.0

    @staticmethod
    def _calculate_gestational_phosphorus(general_properties: GeneralProperties) -> float:
        """Calculates an animal's gestational phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1C-F.E.4.
        """
        if general_properties.days_in_preg >= 190:
            exp_1 = (0.05527 - 0.000075 * general_properties.days_in_preg) * general_properties.days_in_preg
            exp_2 = (0.05527 - 0.000075 * (general_properties.days_in_preg - 1)) * (general_properties.days_in_preg - 1)
            return (0.00002743 * math.exp(exp_1) - 0.00002743 * math.exp(exp_2)) * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    @staticmethod
    def _calculate_milk_phosphorus(general_properties: GeneralProperties) -> float:
        """Calculates an animal's milk phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1E.E.5.
        """
        if general_properties.is_milking:
            return 0.0009 * general_properties.daily_milk_produced * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    @staticmethod
    def _calculate_absorbed_phosphorus(
        general_properties: GeneralProperties,
        phosphorus_status: NutrientProperties,
        milk_phosphorus: float,
        urine_production_phosphorus: float,
    ) -> float:
        """Calculates absorbed phosphorus based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1EF.E.6, A.1A-F.E.6.
        """
        if general_properties.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW]:
            return (
                urine_production_phosphorus
                + phosphorus_status.phosphorus_endogenous_loss
                + phosphorus_status.phosphorus_for_growth
                + phosphorus_status.phosphorus_for_gestation
                + milk_phosphorus
            )
        elif general_properties.animal_type in [AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            return (
                urine_production_phosphorus
                + phosphorus_status.phosphorus_endogenous_loss
                + phosphorus_status.phosphorus_for_growth
                + phosphorus_status.phosphorus_for_gestation
            )
        else:
            return (
                urine_production_phosphorus
                + phosphorus_status.phosphorus_endogenous_loss
                + phosphorus_status.phosphorus_for_growth
            )

    @staticmethod
    def _calculate_animal_phosphorus_requirement(
        general_properties: GeneralProperties, phosphorus_status: NutrientProperties, absorbed_phosphorus: float
    ) -> float:
        """Calculates an animal's phosphorus requirement by animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A.E.7, A.1B-D.E.7, A.1EF.E.7.
        """
        if general_properties.animal_type in [AnimalType.DRY_COW, AnimalType.LAC_COW] and general_properties.is_milking:
            return absorbed_phosphorus / (
                1.86696
                - 5.01238 * phosphorus_status.ration_phosphorus_concentration
                + 5.12286 * phosphorus_status.ration_phosphorus_concentration**2
            )
        elif general_properties.animal_type == AnimalType.CALF:
            return absorbed_phosphorus / 0.90
        else:
            return absorbed_phosphorus / 0.664

    @staticmethod
    def _is_calf_or_heifer(animal_type: AnimalType) -> bool:
        return animal_type in CALVES_AND_HEIFERS
