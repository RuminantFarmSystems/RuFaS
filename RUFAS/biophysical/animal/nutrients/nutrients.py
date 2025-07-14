import math

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrients import NutrientsInputs
from RUFAS.general_constants import GeneralConstants


class Nutrients:
    phosphorus_excess_in_diet: float
    phosphorus_intake: float
    phosphorus_requirement: float
    phosphorus_reserves: float
    total_phosphorus_in_animal: float
    phosphorus_for_growth: float
    phosphorus_endogenous_loss: float
    ration_phosphorus_concentration: float
    phosphorus_for_gestation: float
    phosphorus_for_gestation_required_for_calf: float

    def __init__(self) -> None:
        self.phosphorus_excess_in_diet = 0.0
        self.phosphorus_intake = 0.0
        self.phosphorus_requirement = 0.0
        self.phosphorus_reserves = 0.0
        self.total_phosphorus_in_animal = 0.0
        self.phosphorus_for_growth = 0.0
        self.phosphorus_endogenous_loss = 0.0
        self.ration_phosphorus_concentration = 0.0
        self.phosphorus_for_gestation = 0.0
        self.phosphorus_for_gestation_required_for_calf = 0.0
        self._dry_matter_intake = 0.0

    def perform_daily_phosphorus_update(self, nutrients_inputs: NutrientsInputs) -> None:
        """Manages animal's daily phosphorus update."""
        self._calculate_phosphorus_requirements(nutrients_inputs)
        self._calculate_total_animal_phosphorus()

    def set_dry_matter_intake(self, dry_matter_intake: float) -> None:
        """Set the dry matter intake for the animal according to the provided ration."""
        self._dry_matter_intake = dry_matter_intake

    def set_phosphorus_intake(self, phosphorus_intake: float) -> None:
        """Set the phosphorus intake for the animal according to the provided ration."""
        self.phosphorus_intake = phosphorus_intake

    def _calculate_total_animal_phosphorus(self) -> None:
        """Calculates the total phosphorus for the animal.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1G.A.1, A.1G.A.2, A.1G.A.3.

        Notes
        -----
        - Change in body P reserves (g), must be <= 0

        """
        self.phosphorus_excess_in_diet = max(self.phosphorus_intake - self.phosphorus_requirement, 0)
        previous_phosphorus_reserves = self.phosphorus_reserves
        if self.phosphorus_intake < self.phosphorus_requirement:
            self.phosphorus_reserves = self.phosphorus_intake - self.phosphorus_requirement + self.phosphorus_reserves
        elif self.phosphorus_intake >= self.phosphorus_requirement and self.phosphorus_reserves < 0:
            self.phosphorus_reserves = 0.7 * self.phosphorus_excess_in_diet + self.phosphorus_reserves
        else:
            self.phosphorus_reserves = 0.0
        self.total_phosphorus_in_animal = (
            self.total_phosphorus_in_animal
            + self.phosphorus_for_gestation
            + self.phosphorus_for_growth
            + (self.phosphorus_reserves - previous_phosphorus_reserves)
        )

    def _calculate_phosphorus_requirements(self, nutrients_inputs: NutrientsInputs) -> None:
        """Calculates animal's phosphorus requirements"""
        self.phosphorus_endogenous_loss = self._calculate_phosphorus_endogenous_loss(nutrients_inputs)

        urine_production_phosphorus = 0.000002 * nutrients_inputs.body_weight * GeneralConstants.KG_TO_GRAMS

        self.phosphorus_for_growth = self._calculate_phosphorus_for_growth(nutrients_inputs)

        self.phosphorus_for_gestation = self._calculate_gestational_phosphorus(nutrients_inputs)

        self.phosphorus_for_gestation_required_for_calf += self.phosphorus_for_gestation

        milk_phosphorus = self._calculate_milk_phosphorus(nutrients_inputs)

        absorbed_phosphorus = self._calculate_absorbed_phosphorus(
            nutrients_inputs, milk_phosphorus, urine_production_phosphorus
        )
        self.phosphorus_requirement = self._calculate_animal_phosphorus_requirement(
            nutrients_inputs, absorbed_phosphorus
        )

    def _calculate_phosphorus_endogenous_loss(self, nutrients_inputs: NutrientsInputs) -> float:
        """Calculates phosphorus required for endogenous loss based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A-D.E.1, A.1EF.E.1.
        """
        if not nutrients_inputs.animal_type.is_cow:
            return 0.0008 * self._dry_matter_intake * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.001 * self._dry_matter_intake * GeneralConstants.KG_TO_GRAMS

    def _calculate_phosphorus_for_growth(self, nutrients_inputs: NutrientsInputs) -> float:
        """Calculates phosphorus retained for growth based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1A-F.E.3.
        """
        if (
            not nutrients_inputs.animal_type.is_cow
            or nutrients_inputs.body_weight < nutrients_inputs.mature_body_weight
        ):
            return (
                (
                    0.0012
                    + 0.004635 * (nutrients_inputs.mature_body_weight**0.22) * (nutrients_inputs.body_weight ** (-0.22))
                )
                * nutrients_inputs.daily_growth
                / 0.96
                * GeneralConstants.KG_TO_GRAMS
            )
        else:
            return 0.0

    def _calculate_gestational_phosphorus(self, nutrients_inputs: NutrientsInputs) -> float:
        """Calculates an animal's gestational phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1C-F.E.4.
        """
        if nutrients_inputs.days_in_pregnancy >= 190:
            exp_1 = (0.05527 - 0.000075 * nutrients_inputs.days_in_pregnancy) * nutrients_inputs.days_in_pregnancy
            exp_2 = (0.05527 - 0.000075 * (nutrients_inputs.days_in_pregnancy - 1)) * (
                nutrients_inputs.days_in_pregnancy - 1
            )
            return (0.00002743 * math.exp(exp_1) - 0.00002743 * math.exp(exp_2)) * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    def _calculate_milk_phosphorus(self, nutrients_inputs: NutrientsInputs) -> float:
        """Calculates an animal's milk phosphorus.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation section A.1E.E.5.
        """
        if nutrients_inputs.is_milking:
            return 0.0009 * nutrients_inputs.daily_milk_produced * GeneralConstants.KG_TO_GRAMS
        else:
            return 0.0

    def _calculate_absorbed_phosphorus(
        self,
        nutrients_inputs: NutrientsInputs,
        milk_phosphorus: float,
        urine_production_phosphorus: float,
    ) -> float:
        """Calculates absorbed phosphorus based on animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1EF.E.6, A.1A-F.E.6.
        """
        if nutrients_inputs.animal_type.is_cow:
            return (
                urine_production_phosphorus
                + self.phosphorus_endogenous_loss
                + self.phosphorus_for_growth
                + self.phosphorus_for_gestation
                + milk_phosphorus
            )
        elif nutrients_inputs.animal_type in [AnimalType.HEIFER_II, AnimalType.HEIFER_III]:
            return (
                urine_production_phosphorus
                + self.phosphorus_endogenous_loss
                + self.phosphorus_for_growth
                + self.phosphorus_for_gestation
            )
        else:
            return urine_production_phosphorus + self.phosphorus_endogenous_loss + self.phosphorus_for_growth

    def _calculate_animal_phosphorus_requirement(
        self, nutrients_inputs: NutrientsInputs, absorbed_phosphorus: float
    ) -> float:
        """Calculates an animal's phosphorus requirement by animal type.

        References
        ----------
        RuFaS Phosphorus Animal Module documentation sections A.1A.E.7, A.1B-D.E.7, A.1EF.E.7.
        """
        if nutrients_inputs.animal_type.is_cow and nutrients_inputs.is_milking:
            return absorbed_phosphorus / (
                1.86696
                - 5.01238 * self.ration_phosphorus_concentration
                + 5.12286 * self.ration_phosphorus_concentration**2
            )
        elif nutrients_inputs.animal_type == AnimalType.CALF:
            return absorbed_phosphorus / 0.90
        else:
            return absorbed_phosphorus / 0.664
