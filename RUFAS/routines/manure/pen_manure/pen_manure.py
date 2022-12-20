"""
RUFAS: Ruminant Farm Systems Model
File name: pen_manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.manure.constants.manure_constants import ManureConstants


@dataclass
class PenManure:
    """A class that represents the manure data extracted from the animal module.

    Attributes:
        urea: manure urea concentration in the manure, g/L.
        urine: amount of urine, kg.
        urine_ammoniacal_nitrogen: ammoniacal nitrogen concentration in the urine, g/L.
        total_ammoniacal_nitrogen: total ammoniacal nitrogen concentration in the manure slurry, g/L.
        nitrogen: nitrogen in liquid and solid manure, kg.
        manure_mass: amount of manure, kg.
        manure_volume: volume of manure, m^3.
        total_solids: total solids, kg.
        degradable_volatile_solids: degradable volatile solids, kg.
        non_degradable_volatile_solids: non-degradable volatile solids, kg.
        inorganic_phosphorus_fraction: water extractable inorganic phosphorus fraction,
        unitless.
        organic_phosphorus_fraction: water extractable organic phosphorus fraction, unitless.
        phosphorus: manure phosphorus excretion for manure module input, kg.
        phosphorus_fraction: phosphorus fraction of manure, unitless.
        potassium: potassium in manure, kg.
        methane: methane emission, g/day.

    """
    urea: float = 0.0
    urine: float = 0.0
    urine_ammoniacal_nitrogen: float = 0.0
    total_ammoniacal_nitrogen: float = 0.0
    nitrogen: float = 0.0
    manure_mass: float = 0.0
    manure_volume: float = field(init=False)
    total_solids: float = 0.0
    degradable_volatile_solids: float = 0.0
    non_degradable_volatile_solids: float = 0.0
    inorganic_phosphorus_fraction: float = 0.0
    organic_phosphorus_fraction: float = 0.0
    phosphorus: float = 0.0
    phosphorus_fraction: float = 0.0
    potassium: float = 0.0
    methane: float = 0.0

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""
        self.manure_volume = self.manure_mass / ManureConstants.MANURE_DENSITY

    @classmethod
    def get_instance(cls, animal_manure, num_animals: int) -> PenManure:
        """Returns a PenManure object based on the information given in the manure data.

        Args:
            animal_manure: The manure data extracted from the animal module.
            num_animals: The number of animals in the pen.

        Returns:
            A PenManure object.

        """
        return cls(
                urea=animal_manure['U'] / num_animals,
                urine=animal_manure['Urine'] / num_animals,
                urine_ammoniacal_nitrogen=(
                        animal_manure['TAN_s'] * ManureConstants.URINE_TAN_FACTOR / num_animals),
                total_ammoniacal_nitrogen=animal_manure['TAN_s'],
                nitrogen=animal_manure['MN'],
                manure_mass=animal_manure['Mkg'],
                total_solids=animal_manure['TSd'],
                degradable_volatile_solids=animal_manure['VSd'],
                non_degradable_volatile_solids=animal_manure['VSnd'],
                inorganic_phosphorus_fraction=animal_manure['WIP_frac'] / num_animals,
                organic_phosphorus_fraction=animal_manure['WOP_frac'] / num_animals,
                phosphorus=animal_manure['p_excrt_manure'],
                phosphorus_fraction=animal_manure['p_frac'] / num_animals,
                potassium=animal_manure['K_manure'],
                methane=animal_manure['CH4_manure']
        )
