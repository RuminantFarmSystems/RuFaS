from typing import TypedDict

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.pen_manure_data import PenManureData


class HerdManagerOutput(TypedDict):
    pen_manure: PenManureData
    manure_excretion: AnimalManureExcretions