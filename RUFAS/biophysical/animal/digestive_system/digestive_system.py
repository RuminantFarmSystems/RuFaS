from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator

from RUFAS.output_manager import OutputManager


class DigestiveSystem:
    """
    This class serves as an entry point for the animal digestive systems.
    """

    manure_excretion: AnimalManureExcretions
    phosphorus_excreted: float
    enteric_methane_emission: float

    def __init__(self) -> None:
        self.manure_excretion = AnimalManureExcretions()
        self.phosphorus_excreted = 0.0
        self.enteric_methane_emission = 0.0

    def process_digestion(self, digestive_system_inputs: DigestiveSystemInputs) -> None:
        """
        Processes the digestion for different types of animals by calculating methane emission
        and manure excretion based on the provided digestive system inputs.

        Parameters
        ----------
        digestive_system_inputs : DigestiveSystemInputs
            Contains inputs related to the digestive system of the animal, including animal type,
            body weight, nutrient details, fecal phosphorus, and urine phosphorus requirements.

        Raises
        ------
        TypeError
            If the animal type in digestive_system_inputs is not supported, a TypeError is raised
            with information about supported animal types.
        """
        om = OutputManager()
        info_map = {
            "class": DigestiveSystem.__name__,
            "function": DigestiveSystem.process_digestion.__name__,
        }
        supported_animals: list[str] = [
            AnimalType.CALF,
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
            AnimalType.LAC_COW,
        ]
        if digestive_system_inputs.animal_type not in supported_animals:
            om.add_error(
                "Unsupported animal type",
                f"Supported animal types are {supported_animals}. Got {digestive_system_inputs.animal_type}",
                info_map,
            )
            raise TypeError("Unsupported animal types")

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
            )
            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion
            return

        elif digestive_system_inputs.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            methane_emission = EntericMethaneCalculator.calculate_heifer_methane(
                AnimalConfig.methane_model,
                digestive_system_inputs.nutrients,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_heifer_manure(
                digestive_system_inputs.body_weight,
                digestive_system_inputs.fecal_phosphorus,
                digestive_system_inputs.urine_phosphorus_required,
                digestive_system_inputs.nutrients,
            )
            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion
            return

        elif digestive_system_inputs.animal_type.is_cow:
            methane_emission = EntericMethaneCalculator.calculate_cow_methane(
                digestive_system_inputs.is_milking,
                digestive_system_inputs.body_weight,
                digestive_system_inputs.fat_content,
                digestive_system_inputs.metabolizable_energy_intake,
                digestive_system_inputs.nutrients,
                AnimalConfig.methane_mitigation_method,
                AnimalConfig.methane_mitigation_additive_amount,
                AnimalConfig.methane_model,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_cow_manure(
                digestive_system_inputs.is_milking,
                digestive_system_inputs.body_weight,
                digestive_system_inputs.days_in_milk,
                digestive_system_inputs.protein_content,
                digestive_system_inputs.daily_milk_produced,
                digestive_system_inputs.fecal_phosphorus,
                digestive_system_inputs.urine_phosphorus_required,
                digestive_system_inputs.nutrients,
            )

            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion
            return

        else:
            om.add_error(
                "Unexpected execution path in process_digestion evaluating animal type",
                f"Supported animal types are {supported_animals}. Got {digestive_system_inputs.animal_type}",
                info_map,
            )
            raise RuntimeError(
                f"Unexpected execution path in process_digestion. Animal type: {digestive_system_inputs.animal_type}"
            )
