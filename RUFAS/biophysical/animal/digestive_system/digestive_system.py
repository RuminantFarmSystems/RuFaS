from typing import Any

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator

from RUFAS.output_manager import OutputManager


class DigestiveSystem:
    """
    This class serves as an entry point for the animal digestive systems.
    """

    def process_digestion(
            self,
            general_properties: GeneralProperties,
            animal_nutrient_property: NutrientProperties,
            milk_production_properties: MilkProductionProperties,
    ) -> tuple[dict[str, float], AnimalManureExcretions]:
        """
        Handles an animal's daily digest updates.

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        animal_nutrient_property: AnimalGrowthProperties
            Animal properties that are related to animal nutrients.
        milk_production_properties: MilkProductionProperties
            Animal properties that are related to animal milk production.

        Returns
        -------
        tuple[dict[str, float], AnimalManureExcretions]
            A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

        """
        om = OutputManager()
        statistics = {}
        if general_properties.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calculate_calf_methane(
                AnimalConfig.methane_model,
                general_properties.body_weight,
            )
            phosphorus, excretion = ManureExcretionCalculator.calculate_calf_manure(
                general_properties.body_weight,
                animal_nutrient_property.fecal_phosphorus,
                animal_nutrient_property.urine_phosphorus_required,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
            )
            statistics["methane_emission"] = methane_emission
            statistics["phosphorus_excreted"] = phosphorus
            return statistics, excretion

        elif general_properties.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            methane_emission = EntericMethaneCalculator.calculate_heifer_methane(
                AnimalConfig.methane_model,
                general_properties.nutrients["dm"],
                general_properties.nutrient_concentrations,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_heifer_manure(
                general_properties.body_weight,
                animal_nutrient_property.fecal_phosphorus,
                animal_nutrient_property.urine_phosphorus_required,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
            )
            statistics["methane_emission"] = methane_emission
            statistics["phosphorus_excreted"] = phosphorus
            return statistics, excretion

        elif general_properties.animal_type.is_cow:
            methane_emission = EntericMethaneCalculator.calculate_cow_methane(
                general_properties.is_milking,
                general_properties.body_weight,
                milk_production_properties.fat_content,
                general_properties.metabolizable_energy_intake,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
                AnimalConfig.methane_mitigation_method,
                AnimalConfig.methane_mitigation_additive_amount,
                AnimalConfig.methane_model,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_cow_manure(
                general_properties.is_milking,
                general_properties.body_weight,
                general_properties.days_in_milk,
                milk_production_properties.crude_protein_content,
                general_properties.daily_milk_produced,
                animal_nutrient_property.fecal_phosphorus,
                animal_nutrient_property.urine_phosphorus_required,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
            )
            statistics["methane_emission"] = methane_emission
            statistics["phosphorus_excreted"] = phosphorus
            return statistics, excretion
        else:
            supported_animal: list[str] = ["Calf", "HeiferI", "HeiferI", "HeiferII", "HeiferIII", "DryCow", "LacCow"]
            info_map = {
                "class": DigestiveSystem.__name__,
                "function": DigestiveSystem.process_digestion.__name__,
            }
            om.add_error(
                "Unsupported animal type",
                f"Supported animal types are {supported_animal}. Got {general_properties.animal_type}",
                info_map,
            )
            raise TypeError("Unsupported animal types")
