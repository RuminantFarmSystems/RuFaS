from typing import Any

from RUFAS.biophysical.animal.animal_properties.animal_statistics import AnimalStatistics
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.animal_properties.nutrient_properties import NutrientProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.input_manager import InputManager


class DigestiveSystem:
    METHANE_MODEL: str
    METHANE_MITIGATION_METHOD: str
    METHANE_MITIGATION_ADDITIVE_AMOUNT: float

    @classmethod
    def initialize_animal_methane_variables(cls) -> None:
        """This function retrieves the user input data from the InputManager and initializes the class constants."""
        im = InputManager()
        animal_config: dict[str, Any] = im.get_data("animal.animal_config")
        cls.METHANE_MODEL = animal_config["methane_model"]
        cls.METHANE_MITIGATION_METHOD = animal_config["methane_mitigation"]["methane_mitigation_method"]
        cls.METHANE_MITIGATION_ADDITIVE_AMOUNT = (animal_config)["methane_mitigation"][
            "methane_mitigation_additive_amount"
        ]

    @staticmethod
    def process_digestion(
        general_properties: GeneralProperties,
        animal_nutrient_property: NutrientProperties,
        milk_production_properties: MilkProductionProperties,
        statistics: AnimalStatistics
    ) -> tuple[AnimalStatistics, AnimalManureExcretions]:
        """
        Handles an animal's daily digest updates.

        Parameters
        ----------
        statistics: AnimalStatistics
            Animal properties that are used for animal statistics.
        general_properties: GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        animal_nutrient_property: AnimalGrowthProperties
            Animal properties that are related to animal nutrients.
        milk_production_properties: ReproductionProperties
            Animal properties that are related to animal milk production.

        Returns
        -------
        tuple[AnimalStatistics, AnimalManureExcretions]
            An updated AnimalStatistics class.
            A dictionary that contains the manure excretion values as specified
            in the AnimalManureExcretions class definition.

        """
        if general_properties.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calculate_calf_methane(
                DigestiveSystem.METHANE_MODEL,
                general_properties.body_weight,
            )
            phosphorus, excretion = ManureExcretionCalculator.calculate_calf_manure(
                general_properties.body_weight,
                animal_nutrient_property.fecal_phosphorus,
                animal_nutrient_property.urine_phosphorus_required,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
            )
            statistics.methane_emission = methane_emission
            statistics.phosphorus_excreted = phosphorus
            return statistics, excretion

        elif general_properties.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            methane_emission = EntericMethaneCalculator.calculate_heifer_methane(
                DigestiveSystem.METHANE_MODEL,
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
            statistics.methane_emission = methane_emission
            statistics.phosphorus_excreted = phosphorus
            return statistics, excretion

        else:
            methane_emission = EntericMethaneCalculator.calculate_cow_methane(
                general_properties.is_milking,
                general_properties.body_weight,
                milk_production_properties.fat_content,
                general_properties.metabolizable_energy_intake,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
                DigestiveSystem.METHANE_MITIGATION_METHOD,
                DigestiveSystem.METHANE_MITIGATION_ADDITIVE_AMOUNT,
                DigestiveSystem.METHANE_MODEL,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_cow_manure(
                general_properties.is_milking,
                general_properties.body_weight,
                general_properties.days_in_milk,
                milk_production_properties.crude_protein_content,
                milk_production_properties.daily_milk_production,
                animal_nutrient_property.fecal_phosphorus,
                animal_nutrient_property.urine_phosphorus_required,
                general_properties.nutrients,
                general_properties.nutrient_concentrations,
            )
            statistics.methane_emission = methane_emission
            statistics.phosphorus_excreted = phosphorus
            return statistics, excretion
