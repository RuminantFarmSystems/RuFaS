from dataclasses import dataclass

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions


@dataclass
class DigestiveSystemOutputs:
    methane_emission: float
    phosphorus_excreted: float
    manure_excretion: AnimalManureExcretions