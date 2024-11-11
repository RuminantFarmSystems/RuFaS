from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.digestive_system_outputs import DigestiveSystemOutputs
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.digestive_system_inputs import DigestiveSystemInputs
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator

from RUFAS.output_manager import OutputManager


class DigestiveSystem:
    """
    This class serves as an entry point for the animal digestive systems.
    """

    def process_digestion(self, digestive_system_inputs: DigestiveSystemInputs) -> DigestiveSystemOutputs:
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
        if digestive_system_inputs.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calculate_calf_methane(
                AnimalConfig.methane_model,
                digestive_system_inputs.body_weight,
            )
            phosphorus, excretion = ManureExcretionCalculator.calculate_calf_manure(
                digestive_system_inputs.body_weight,
                digestive_system_inputs.fecal_phosphorus,
                digestive_system_inputs.urine_phosphorus_required,
                digestive_system_inputs.nutrients,
                digestive_system_inputs.nutrient_concentrations,
            )

            return DigestiveSystemOutputs(
                methane_emission=methane_emission,
                phosphorus_excreted=phosphorus,
                manure_excretion=excretion)

        elif digestive_system_inputs.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            methane_emission = EntericMethaneCalculator.calculate_heifer_methane(
                AnimalConfig.methane_model,
                digestive_system_inputs.nutrients["dm"],
                digestive_system_inputs.nutrient_concentrations,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_heifer_manure(
                digestive_system_inputs.body_weight,
                digestive_system_inputs.fecal_phosphorus,
                digestive_system_inputs.urine_phosphorus_required,
                digestive_system_inputs.nutrients,
                digestive_system_inputs.nutrient_concentrations,
            )

            return DigestiveSystemOutputs(
                methane_emission=methane_emission,
                phosphorus_excreted=phosphorus,
                manure_excretion=excretion)

        elif digestive_system_inputs.animal_type.is_cow:
            methane_emission = EntericMethaneCalculator.calculate_cow_methane(
                digestive_system_inputs.is_milking,
                digestive_system_inputs.body_weight,
                digestive_system_inputs.fat_content,
                digestive_system_inputs.metabolizable_energy_intake,
                digestive_system_inputs.nutrients,
                digestive_system_inputs.nutrient_concentrations,
                AnimalConfig.methane_mitigation_method,
                AnimalConfig.methane_mitigation_additive_amount,
                AnimalConfig.methane_model,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_cow_manure(
                digestive_system_inputs.is_milking,
                digestive_system_inputs.body_weight,
                digestive_system_inputs.days_in_milk,
                digestive_system_inputs.crude_protein_content,
                digestive_system_inputs.daily_milk_produced,
                digestive_system_inputs.fecal_phosphorus,
                digestive_system_inputs.urine_phosphorus_required,
                digestive_system_inputs.nutrients,
                digestive_system_inputs.nutrient_concentrations,
            )

            return DigestiveSystemOutputs(
                methane_emission=methane_emission,
                phosphorus_excreted=phosphorus,
                manure_excretion=excretion)
        else:
            supported_animal: list[str] = ["Calf", "HeiferI", "HeiferI", "HeiferII", "HeiferIII", "DryCow", "LacCow"]
            info_map = {
                "class": DigestiveSystem.__name__,
                "function": DigestiveSystem.process_digestion.__name__,
            }
            om.add_error(
                "Unsupported animal type",
                f"Supported animal types are {supported_animal}. Got {digestive_system_inputs.animal_type}",
                info_map,
            )
            raise TypeError("Unsupported animal types")
