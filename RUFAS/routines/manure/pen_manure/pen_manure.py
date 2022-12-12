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
        urea: urea concentration in the manure, g/L.
        urine: amount of urine, kg.
        urine_ammoniacal_nitrogen: ammoniacal nitrogen concentration in the urine, g/L.
        total_ammoniacal_nitrogen: total ammoniacal nitrogen concentration in the manure slurry, g/L.
        manure_nitrogen: nitrogen in liquid and solid manure, kg.
        manure_mass: amount of manure, kg.
        manure_volume: volume of manure, m^3.
        TS: total solids, kg.
        VSd: degradable volatile solids, kg.
        VSnd: non-degradable volatile solids, kg.
        WIP_frac: water extractable inorganic manure_phosphorus fraction, dimensionless.
        WOP_frac: water extractable organic manure_phosphorus fraction, dimensionless.
        manure_phosphorus: manure phosphorus excretion for manure module input, kg.
        P_frac: phosphorus fraction of manure.
        K: potassium in manure, kg.
        CH4: methane emission, g/day.

    """
    urea: float = 0.0
    urine: float = 0.0
    urine_ammoniacal_nitrogen: float = 0.0
    total_ammoniacal_nitrogen: float = 0.0
    manure_nitrogen: float = 0.0
    manure_mass: float = 0.0
    manure_volume: float = field(init=False)
    TS: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    manure_phosphorus: float = 0.0
    P_frac: float = 0.0
    K: float = 0.0
    CH4: float = 0.0

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
                urine_ammoniacal_nitrogen=animal_manure['TAN_s'] * ManureConstants.URINE_TAN_FACTOR / num_animals,
                total_ammoniacal_nitrogen=animal_manure['TAN_s'],
                manure_nitrogen=animal_manure['MN'],
                manure_mass=animal_manure['Mkg'],
                TS=animal_manure['TSd'],
                VSd=animal_manure['VSd'],
                VSnd=animal_manure['VSnd'],
                WIP_frac=animal_manure['WIP_frac'] / num_animals,
                WOP_frac=animal_manure['WOP_frac'] / num_animals,
                manure_phosphorus=animal_manure['p_excrt_manure'],
                P_frac=animal_manure['p_frac'] / num_animals,
                K=animal_manure['K_manure'],
                CH4=animal_manure['CH4_manure']
        )
