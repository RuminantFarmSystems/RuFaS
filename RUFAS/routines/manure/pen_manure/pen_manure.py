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
        manure_urea: manure_urea concentration in the manure, g/L.
        manure_urine: amount of urine, kg.
        manure_urine_ammoniacal_nitrogen: ammoniacal nitrogen concentration in the urine, g/L.
        manure_total_ammoniacal_nitrogen: total ammoniacal nitrogen concentration in the manure slurry, g/L.
        manure_nitrogen: nitrogen in liquid and solid manure, kg.
        manure_mass: amount of manure, kg.
        manure_volume: volume of manure, m^3.
        manure_total_solids: total solids, kg.
        manure_degradable_volatile_solids: degradable volatile solids, kg.
        manure_non_degradable_volatile_solids: non-degradable volatile solids, kg.
        manure_inorganic_phosphorus_fraction: water extractable inorganic manure_phosphorus fraction,
        unitless.
        manure_organic_phosphorus_fraction: water extractable organic manure_phosphorus fraction, unitless.
        manure_phosphorus: manure phosphorus excretion for manure module input, kg.
        manure_phosphorus_fraction: phosphorus fraction of manure, unitless.
        manure_potassium: potassium in manure, kg.
        manure_methane: methane emission, g/day.

    """
    manure_urea: float = 0.0
    manure_urine: float = 0.0
    manure_urine_ammoniacal_nitrogen: float = 0.0
    manure_total_ammoniacal_nitrogen: float = 0.0
    manure_nitrogen: float = 0.0
    manure_mass: float = 0.0
    manure_volume: float = field(init=False)
    manure_total_solids: float = 0.0
    manure_degradable_volatile_solids: float = 0.0
    manure_non_degradable_volatile_solids: float = 0.0
    manure_inorganic_phosphorus_fraction: float = 0.0
    manure_organic_phosphorus_fraction: float = 0.0
    manure_phosphorus: float = 0.0
    manure_phosphorus_fraction: float = 0.0
    manure_potassium: float = 0.0
    manure_methane: float = 0.0

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
                manure_urea=animal_manure['U'] / num_animals,
                manure_urine=animal_manure['Urine'] / num_animals,
                manure_urine_ammoniacal_nitrogen=animal_manure['TAN_s'] * ManureConstants.URINE_TAN_FACTOR / num_animals,
                manure_total_ammoniacal_nitrogen=animal_manure['TAN_s'],
                manure_nitrogen=animal_manure['MN'],
                manure_mass=animal_manure['Mkg'],
                manure_total_solids=animal_manure['TSd'],
                manure_degradable_volatile_solids=animal_manure['VSd'],
                manure_non_degradable_volatile_solids=animal_manure['VSnd'],
                manure_inorganic_phosphorus_fraction=animal_manure['WIP_frac'] / num_animals,
                manure_organic_phosphorus_fraction=animal_manure['WOP_frac'] / num_animals,
                manure_phosphorus=animal_manure['p_excrt_manure'],
                manure_phosphorus_fraction=animal_manure['p_frac'] / num_animals,
                manure_potassium=animal_manure['K_manure'],
                manure_methane=animal_manure['CH4_manure']
        )
