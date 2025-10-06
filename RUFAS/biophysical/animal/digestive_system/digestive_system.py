from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.digestive_system import DigestiveSystemInputs
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.general_constants import GeneralConstants

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
        self.enteric_methane_emission: float = 0.0

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
        supported_animals: list[AnimalType] = [
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

        fecal_phosphorus, urine_phosphorus_required = self._calculate_base_manure(
            digestive_system_inputs.body_weight,
            digestive_system_inputs.phosphorus_intake,
            digestive_system_inputs.phosphorus_requirement,
            digestive_system_inputs.phosphorus_reserves,
            digestive_system_inputs.phosphorus_endogenous_loss,
        )
        if digestive_system_inputs.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calculate_calf_methane(
                AnimalConfig.methane_model["calves"],
                digestive_system_inputs.body_weight,
            )
            phosphorus, excretion = ManureExcretionCalculator.calculate_calf_manure(
                digestive_system_inputs.body_weight,
                fecal_phosphorus,
                urine_phosphorus_required,
                digestive_system_inputs.nutrients,
            )
            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion

        elif digestive_system_inputs.animal_type in (AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III):
            if digestive_system_inputs.animal_type == AnimalType.HEIFER_I:
                model_selection = "heiferIs"
            elif digestive_system_inputs.animal_type == AnimalType.HEIFER_II:
                model_selection = "heiferIIs"
            else:
                model_selection = "heiferIIIs"

            methane_emission = EntericMethaneCalculator.calculate_heifer_methane(
                AnimalConfig.methane_model[model_selection],
                digestive_system_inputs.nutrients,
            )

            phosphorus, excretion = ManureExcretionCalculator.calculate_heifer_manure(
                digestive_system_inputs.body_weight,
                fecal_phosphorus,
                urine_phosphorus_required,
                digestive_system_inputs.nutrients,
            )
            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion

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
                fecal_phosphorus,
                urine_phosphorus_required,
                digestive_system_inputs.nutrients,
            )

            self.enteric_methane_emission = methane_emission
            self.phosphorus_excreted = phosphorus
            self.manure_excretion = excretion

        else:
            om.add_error(
                "Unexpected execution path in process_digestion evaluating animal type",
                f"Supported animal types are {supported_animals}. Got {digestive_system_inputs.animal_type}",
                info_map,
            )
            raise RuntimeError(
                f"Unexpected execution path in process_digestion. Animal type: {digestive_system_inputs.animal_type}"
            )

    def _calculate_base_manure(
        self,
        body_weight: float,
        phosphorus_intake: float,
        phosphorus_requirement: float,
        phosphorus_reserves: float,
        phosphorus_endogenous_loss: float,
    ) -> tuple[float, float]:
        """
        Calculates the base manure production in terms of phosphorus for an animal.

        The function determines the amount of phosphorus excreted via urine and feces
        based on the animal's body weight, phosphorus intake, requirements, reserves,
        and endogenous loss.

        Parameters
        ----------
        body_weight : float
            The body weight of the animal (kg).
        phosphorus_intake : float
            The amount of phosphorus consumed by the animal (g).
        phosphorus_requirement : float
            The required phosphorus intake for the animal's physiological needs (g).
        phosphorus_reserves : float
            The phosphorus reserves in the animal's body (g).
            Can be negative indicating a deficit.
        phosphorus_endogenous_loss : float
            The endogenous loss of phosphorus (g).

        Returns
        -------
        tuple[float, float]
            A tuple containing two values:
            - The amount of phosphorus excreted in urine (g).
            - The amount of phosphorus excreted in feces (g).
        """

        # amount of P required for urine production (g) (A.1G.B.1)
        urine_phosphorus_required = 0.000002 * body_weight * GeneralConstants.KG_TO_GRAMS

        # excess P in the diet (g) (A.1G.A.1)
        phosphorus_excess_in_diet = max(phosphorus_intake - phosphorus_requirement, 0)

        # amount of P excreted by an animal (g) (A.1G.B.2)
        if phosphorus_reserves == 0 and phosphorus_intake >= phosphorus_requirement:
            fecal_phosphorus = phosphorus_intake - phosphorus_requirement + phosphorus_reserves
        elif (
            phosphorus_reserves < 0
            and phosphorus_intake >= phosphorus_requirement
            and phosphorus_excess_in_diet >= (-1) * phosphorus_reserves / 0.7
        ):
            fecal_phosphorus = (
                phosphorus_intake - phosphorus_requirement + phosphorus_endogenous_loss + phosphorus_reserves / 0.7
            )

        else:
            fecal_phosphorus = phosphorus_endogenous_loss

        return fecal_phosphorus, urine_phosphorus_required
