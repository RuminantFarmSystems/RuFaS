from numpy import abs

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_requirements import (
    EnergyNutritionRequirements,
    EnergyNutritionSupply,
    EnergyNutritionEvaluation
)
from RUFAS.biophysical.animal.nutrients.energy_supply_calculator import EnergySupplyCalculator
from RUFAS.data_structures.feed_storage_to_animal_module_connection import Feed, RUFAS_ID
from RUFAS.general_constants import GeneralConstants


class EnergyNutritionEvaluator:
    """Checks if energy and nutrients supplied in a ration satisfy the demand for an individual animal."""

    @classmethod
    def evaluate_energy_nutrition_supply(
        cls,
        ration: dict[RUFAS_ID, float],
        available_feeds: list[Feed],
        requirements: EnergyNutritionRequirements,
        body_weight: float,
        is_cow: bool,
    ) -> tuple[bool, EnergyNutritionEvaluation]:
        """True if energy and nutrition supplied satisfy the requirements, false otherwise."""
        energy_nutrition_supply = EnergySupplyCalculator.calculate_energy_nutrient_supply(
            available_feeds, ration, body_weight  # TODO: confirm this is average body weight when formulating for a pen
        )  # but an individual body weight when checking for an individual animal

        heifer_energy_nutrition_checkers = {
            "maintenance": cls._check_activity_maintenance_energy_supplied,
            "growth": cls._check_growth_energy_supplied,
            "calcium": cls._check_calcium_supplied,
            "phosphorus": cls._check_phosphorus_supplied,
            "protein": cls._check_protein_supplied,
            "ndf": cls._check_neutral_detergent_fiber_supplied,
            "fat": cls._check_fat_content,
            "dry_matter": cls._check_dry_matter_intake,
        }
        cow_energy_nutrition_checkers = heifer_energy_nutrition_checkers + {
            "total_energy": cls._check_total_energy_supplied, "lactation": cls._check_lactation_energy_supplied
        }

        checkers = cow_energy_nutrition_checkers if is_cow else heifer_energy_nutrition_checkers
        results = {name: method(requirements, energy_nutrition_supply) for name, method in checkers.items()}

        evaluation = EnergyNutritionEvaluation(
            total_energy=results.get("total_energy"),
            maintenance=results["maintentance"],
            lactation=results.get("lactation"),
            growth=results["growth"],
            calcium=results["calcium"],
            phosphorus=results["phosphorus"],
            protein=results["protein"],
            ndf=results["ndf"],
            fat=results["fat"],
            dry_matter=results["dry_matter"],
        )

        if is_cow:
            return evaluation.is_valid_cow_ration, evaluation
        else:
            return evaluation.is_valid_heifer_ration, evaluation

    @classmethod
    def _check_total_energy_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that total energy supplied meets total demand."""
        energy_supplied: float = max(supply.maintenance, supply.lactation, supply.growth)

        total_energy_requirement = sum(
            [
                requirements.lactation,
                requirements.growth,
                requirements.maintenance,
                requirements.activity,
                requirements.pregnancy,
            ]
        )

        return energy_supplied - total_energy_requirement

    @classmethod
    def _check_activity_maintenance_energy_supplied(
        requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply
    ) -> float:
        """Checks that energy supplied for maintenance and activity meets demand."""
        energy_requirement = requirements.activity + requirements.maintenance

        return supply.maintenance - energy_requirement

    @classmethod
    def _check_lactation_energy_supplied(
        requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply
    ) -> float:
        """Checks that energy supplied for lactation meets requirement for lactation and pregnancy."""
        energy_requirement = requirements.lactation + requirements.pregnancy

        return supply.lactation - energy_requirement

    @classmethod
    def _check_growth_energy_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that energy supplied for growth meets the requirement."""
        return supply.growth - requirements.growth

    @classmethod
    def _check_calcium_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that calcium supplied meets the requirement."""
        return supply.calcium - requirements.calcium

    @classmethod
    def _check_phosphorus_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that phosphorus supplied meets the requirement."""
        requirement = max(requirements.phosphorus, requirements.alternative_phosphorus)  # TODO: add in other P req

        return supply.phosphorus - requirement

    @classmethod
    def _check_protein_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that protein supplied meets the requirement and does not exceed the upper threshold."""
        upper_protein_limit = requirements.protein * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR

        if supply.protein < requirements.protein:
            return supply.protein - requirements.protein
        elif supply.protein > upper_protein_limit:
            return supply.protein - upper_protein_limit
        else:
            return 0.0

    @classmethod
    def _check_neutral_detergent_fiber_supplied(_: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that neutral detergent fiber (NDF) supplied is between the fixed upper and lower bounds."""
        ndf_percentage = supply.ndf_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        if ndf_percentage < AnimalModuleConstants.MINIMUM_NDF:
            return ndf_percentage - AnimalModuleConstants.MINIMUM_NDF
        elif ndf_percentage > AnimalModuleConstants.MAXIMUM_NDF:
            return ndf_percentage - AnimalModuleConstants.MAXIMUM_NDF
        else:
            return 0.0

    @classmethod
    def _check_fat_content(_: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that the fat content supplied meets the requirement."""
        fat_percentage = supply.fat_content / supply.dry_matter * GeneralConstants.FRACTION_TO_PERCENTAGE

        return fat_percentage - AnimalModuleConstants.MINIMUM_FAT

    @classmethod
    def _check_dry_matter_intake(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> float:
        """Checks that the dry matter supplied meets the requirement."""
        lower_dry_matter_limit = requirements.dry_matter * (1.0 - AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)
        upper_dry_matter_limit = requirements.dry_matter * (1.0 + AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)

        if supply.dry_matter < lower_dry_matter_limit:
            return supply.dry_matter - lower_dry_matter_limit
        elif supply.dry_matter > upper_dry_matter_limit:
            return supply.dry_matter - upper_dry_matter_limit
        else:
            return 0.0
