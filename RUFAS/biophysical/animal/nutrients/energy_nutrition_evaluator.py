
from RUFAS.biophysical.animal.data_types.nutrition_requirements import EnergyNutritionRequirements, EnergyNutritionSupply
from RUFAS.biophysical.animal.nutrients.energy_supply_calculator import EnergySupplyCalculator
from RUFAS.data_structures.feed_storage_to_animal_module_connection import Feed


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
        )                                         # but an individual body weight when checking for an individual animal

        total_energy_satisfactory = cls._check_total_energy_supplied(requirements, energy_nutrition_supply)
        
        pass

    @classmethod
    def _check_total_energy_supplied(requirements: EnergyNutritionRequirements, supply: EnergyNutritionSupply) -> bool:
        """Checks that total energy supplied meets total demand."""
        energy_supplied: float = max(supply.metabolizable, supply.lactation, supply.lactation)

        total_energy_requirement = sum([
            requirements.lactation,
            requirements.growth,
            requirements.maintenance,
            requirements.activity,
            requirements.pregnancy,
        ])

        is_requirement_satisfied = energy_supplied >= total_energy_requirement
        return is_requirement_satisfied
