from typing import Any

from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.input_manager import InputManager


class DigestiveSystem:

    @classmethod
    def initialize_animal_growth_variables(cls) -> None:
        """This function retrieves the user input data from the InputManager and initializes the class constants."""
        im = InputManager()
        animal_config: dict[str, Any] = im.get_data("animal.animal_config")
        cls.methane_model = animal_config["methane_model"]
        cls.methane_mitigation_method = animal_config["methane_mitigation"]["methane_mitigation_method"]
        cls.methane_mitigation_additive_amount = (
            animal_config)["methane_mitigation"]["methane_mitigation_additive_amount"]

    @staticmethod
    def daily_routine(general_properties: GeneralProperties,
                      animal_nutrient_property: NutrientProperties,
                      milk_production_properties: MilkProductionProperties) \
        -> tuple[float, float, AnimalManureExcretions]:
        """
        Handles an animal's daily digest updates.

        Parameters
        ----------
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        animal_nutrient_property: AnimalGrowthProperties
            Animal properties that are related to animal nutrients.
        milk_production_properties: ReproductionProperties
            Animal properties that are related to animal milk production.

        Returns
        -------
        tuple[float, float, AnimalManureExcretions]
            

        """
        if general_properties.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calf_methane(DigestiveSystem.methane_model,
                                                                     general_properties.body_weight,
                                                                     )
            phosphorus, excretion = \
                ManureExcretionCalculator.calf_manure(general_properties.body_weight,
                                                      animal_nutrient_property.fecal_phosphorus,
                                                      animal_nutrient_property.urine_phosphorus_required,
                                                      general_properties.nutrients,
                                                      general_properties.nutrient_concentrations)
            return methane_emission, phosphorus, excretion

        if general_properties.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            methane_emission = EntericMethaneCalculator.heifer_methane(DigestiveSystem.methane_model,
                                                                       general_properties.nutrients["dm"],
                                                                       general_properties.nutrient_concentrations)

            phosphorus, excretion = (
                ManureExcretionCalculator.heifer_manure(general_properties.body_weight,
                                                        animal_nutrient_property.fecal_phosphorus,
                                                        animal_nutrient_property.urine_phosphorus_required,
                                                        general_properties.nutrients,
                                                        general_properties.nutrient_concentrations
                                                        ))
            return methane_emission, phosphorus, excretion

        if general_properties.animal_type in (AnimalType.DRY_COW, AnimalType.LAC_COW):
            methane_emission = EntericMethaneCalculator.cow_methane(general_properties.is_milking,
                                                                    general_properties.body_weight,
                                                                    milk_production_properties.fat_content,
                                                                    general_properties.metabolizable_energy_intake,
                                                                    general_properties.nutrients,
                                                                    general_properties.nutrient_concentrations,
                                                                    DigestiveSystem.methane_mitigation_method,
                                                                    DigestiveSystem.methane_mitigation_additive_amount,
                                                                    DigestiveSystem.methane_model)

            phosphorus, excretion = (
                ManureExcretionCalculator.cow_manure(general_properties.is_milking,
                                                     general_properties.body_weight,
                                                     general_properties.days_in_milk,
                                                     milk_production_properties.crude_protein_content,
                                                     milk_production_properties.daily_milk_production,
                                                     animal_nutrient_property.fecal_phosphorus,
                                                     animal_nutrient_property.urine_phosphorus_required,
                                                     general_properties.nutrients,
                                                     general_properties.nutrient_concentrations
                                                     ))
            return methane_emission, phosphorus, excretion
