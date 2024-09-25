from typing import Any

from RUFAS.biophysical.animal.animal_properties.digestive_system_properties import DigestiveSystemProperties
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.digestive_system.enteric_methane_calculator import EntericMethaneCalculator
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.input_manager import InputManager


class DigestiveSystem:
    @classmethod
    def initialize_class_variables(cls) -> None:
        im = InputManager()

    @staticmethod
    def daily_routine(general_properties: GeneralProperties,
                      digestive_properties: DigestiveSystemProperties,
                      animal_phosphorus_property: AnimalPhosphorusProperties,
                      milk_production_properties: MilkProductionProperties) -> tuple[
        float, float, AnimalManureExcretions]:
        if general_properties.animal_type == AnimalType.CALF:
            methane_emission = EntericMethaneCalculator.calf_methane("holder", general_properties.body_weight,
                                                                     )
            return methane_emission, ManureExcretionCalculator.calf_manure()
        is_lactating = GeneralProperties.is_milking

    pass
