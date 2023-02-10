"""
RUFAS: Ruminant Farm Systems Model
File name: pen_manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.manure.constants.manure_constants import ManureConstants


@dataclass
class PenManure:
    """A class that represents the manure data extracted from the animal module.

    """
    urea: float = 0.0
    """float: Concentration of urea in manure, g/L."""

    urine: float = 0.0
    """Amount of urine in manure, kg."""

    urine_ammoniacal_nitrogen: float = 0.0
    """Concentration of ammoniacal nitrogen concentration in urine, g/L."""

    total_ammoniacal_nitrogen: float = 0.0
    """Concentration of total ammoniacal nitrogen in manure slurry, g/L."""

    nitrogen: float = 0.0
    """Amount of nitrogen in manure, kg."""

    manure_mass: float = 0.0
    """Amount of manure, kg."""

    manure_volume: float = field(init=False)
    """Volume of manure, m^3."""

    total_solids: float = 0.0
    """Amount of total solids, kg."""

    degradable_volatile_solids: float = 0.0
    """Amount of degradable volatile solids, kg."""

    non_degradable_volatile_solids: float = 0.0
    """Amount of non-degradable volatile solids, kg."""

    inorganic_phosphorus_fraction: float = 0.0
    """Fraction of water extractable inorganic phosphorus, unitless."""

    organic_phosphorus_fraction: float = 0.0
    """Fraction of water extractable organic phosphorus, unitless."""

    phosphorus: float = 0.0
    """Amount of phosphorus excreted in manure, kg."""

    phosphorus_fraction: float = 0.0
    """Fraction of phosphorus in manure, unitless."""

    potassium: float = 0.0
    """Amount of potassium in manure, kg."""

    methane: float = 0.0
    """Amount of methane emission, g/day."""

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""
        self.manure_volume = self.manure_mass / ManureConstants.MANURE_DENSITY

    @classmethod
    def get_instance(cls, animal_manure: AnimalManureExcretions, num_animals: int) -> PenManure:
        """Returns a PenManure object based on the information given in the manure data.

        Parameters
        ----------
        animal_manure : AnimalManureExcretions
            The manure data extracted from the animal module.
        num_animals : int
            The number of animals in the pen.


        Returns
        -------
        PenManure
            A PenManure object.

        """
        return cls(
                urea=animal_manure['urea'] / num_animals,
                urine=animal_manure['urine'] / num_animals,
                urine_ammoniacal_nitrogen=(
                        animal_manure['total_ammoniacal_nitrogen'] * ManureConstants.URINE_TAN_FACTOR / num_animals),
                total_ammoniacal_nitrogen=animal_manure['total_ammoniacal_nitrogen'],
                nitrogen=animal_manure['nitrogen'],
                manure_mass=animal_manure['manure_mass'],
                total_solids=animal_manure['total_solids'],
                degradable_volatile_solids=animal_manure['degradable_volatile_solids'],
                non_degradable_volatile_solids=animal_manure['non_degradable_volatile_solids'],
                inorganic_phosphorus_fraction=animal_manure['inorganic_phosphorus_fraction'] / num_animals,
                organic_phosphorus_fraction=animal_manure['organic_phosphorus_fraction'] / num_animals,
                phosphorus=animal_manure['phosphorus'],
                phosphorus_fraction=animal_manure['phosphorus_fraction'] / num_animals,
                potassium=animal_manure['potassium'],
                methane=animal_manure['methane']
        )
