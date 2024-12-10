from numpy import abs

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_requirements import (
    EnergyNutritionRequirements,
    EnergyNutritionSupply,
)
from RUFAS.biophysical.animal.nutrients.energy_supply_calculator import EnergySupplyCalculator
from RUFAS.data_structures.feed_storage_to_animal_module_connection import Feed
from RUFAS.general_constants import GeneralConstants


class EnergyNutritionEvaluator:
    """Checks if energy and nutrients supplied in a ration satisfy the demand for an individual animal."""

    @classmethod
    def evaluate_energy_nutrition_supply(
        cls,
        ration: dict[int, float],
        available_feeds: list[Feed],
        requirements: EnergyNutritionRequirements,
        body_weight: float,
    ) -> bool:
        """True if energy and nutrition supplied satisfy the requirements, false otherwise."""
        energy_nutrition_supply = EnergySupplyCalculator.calculate_energy_nutrient_supply(
            available_feeds, ration, body_weight  # TODO: confirm this is average body weight when formulating for a pen
        )  # but an individual body weight when checking for an individual animal

        energy_nutrition_checkers = [
            cls._check_total_energy_supplied,
            cls._check_activity_maintenance_energy_supplied,
            cls._check_lactation_energy_supplied,
            cls._check_growth_energy_supplied,
            cls._check_calcium_supplied,
            cls._check_phosphorus_supplied,
            cls._check_protein_supplied,
            cls._check_neutral_detergent_fiber_supplied,
            cls._check_fat_content,
            cls._check_dry_matter_intake,
        ]
        results = []
        for checker in energy_nutrition_checkers:
            result = checker(requirements, energy_nutrition_supply)
            results.append(result)

        return all(results)

    @classmethod
    def _check_total_energy_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that total energy supplied meets total demand."""
        energy_supplied: float = max(supply.metabolizable, supply.lactation, supply.lactation)

        total_energy_requirement = sum(
            [
                requirements.lactation,
                requirements.growth,
                requirements.maintenance,
                requirements.activity,
                requirements.pregnancy,
            ]
        )

        is_requirement_satisfied = energy_supplied >= total_energy_requirement
        return is_requirement_satisfied

    @classmethod
    def _check_activity_maintenance_energy_supplied(
        requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply
    ) -> bool:
        """Checks that energy supplied for maintenance and activity meets demand."""
        energy_requirement = requirements.activity + requirements.maintenance

        is_requirement_satisfied = supply.maintenance >= energy_requirement
        return is_requirement_satisfied

    @classmethod
    def _check_lactation_energy_supplied(
        requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply
    ) -> bool:
        """Checks that energy supplied for lactation meets requirement for lactation and pregnancy."""
        energy_requirement = requirements.lactation + requirements.pregnancy

        is_requirement_satisfied = supply.lactation >= energy_requirement
        return is_requirement_satisfied

    @classmethod
    def _check_growth_energy_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that energy supplied for growth meets the requirement."""
        is_requirement_satisfied = supply.growth >= requirements.growth
        return is_requirement_satisfied

    @classmethod
    def _check_calcium_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that calcium supplied meets the requirement."""
        is_requirement_satisfied = supply.calcium >= requirements.calcium
        return is_requirement_satisfied

    @classmethod
    def _check_phosphorus_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that phosphorus supplied meets the requirement."""
        requirement = max(requirements.phosphorus, requirements.alternative_phosphorus)  # TODO: add in other P req

        is_requirement_satisfied = supply.phosphorus >= requirement
        return is_requirement_satisfied

    @classmethod
    def _check_protein_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that protein supplied meets the requirement and does not exceed the upper threshold."""
        upper_protein_limit = requirements.protein * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR

        is_requirement_satisfied = requirements.protein <= supply.protein <= upper_protein_limit
        return is_requirement_satisfied

    @classmethod
    def _check_neutral_detergent_fiber_supplied(_: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that neutral detergent fiber (NDF) supplied is between the fixed upper and lower bounds."""
        ndf_percentage = supply.ndf_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        is_supply_acceptable = AnimalModuleConstants.MINIMUM_NDF <= ndf_percentage <= AnimalModuleConstants.MAXIMUM_NDF
        return is_supply_acceptable

    @classmethod
    def _check_fat_content(_: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that the fat content supplied meets the requirement."""
        fat_percentage = supply.ndf_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        is_requirement_satisfied = fat_percentage >= AnimalModuleConstants.MINIMUM_FAT
        return is_requirement_satisfied

    @classmethod
    def _check_dry_matter_intake(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that the dry matter supplied meets the requirement."""
        dry_matter_fractional_difference = abs(requirements.dry_matter - supply.dry_matter)

        is_requirement_satisfied = dry_matter_fractional_difference <= AnimalModuleConstants.DMI_CONSTRAINT_PERCENT
        return is_requirement_satisfied
