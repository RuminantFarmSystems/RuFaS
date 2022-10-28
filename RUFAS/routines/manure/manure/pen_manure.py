"""
RUFAS: Ruminant Farm Systems Model
File name: pen_manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations

from dataclasses import dataclass

from RUFAS.routines.manure.constants.constants import ManureManagementConstants as Constants


@dataclass
class PenManure:
    """A class that represents the manure data extracted from the animal module.

    Attributes:
        urea: urea concentration, g/L.
        TAN: total ammoniacal nitrogen concentration in the manure slurry, g/L.
        N: nitrogen in liquid and solid manure, kg.
        manure_mass: amount of manure, kg.
        TS: total solids, kg.
        VSd: degradable volatile solids, kg.
        VSnd: non-degradable volatile solids, kg.
        WIP_frac: water extractable inorganic P fraction, dimensionless.
        WOP_frac: water extractable organic P fraction, dimensionless.
        P: manure phosphorus excretion for manure module input, kg.
        P_frac: phosphorus fraction of manure.
        K: potassium in manure, kg.
        CH4: methane emission, g/day.

    """
    urea: float = 0.0
    TAN: float = 0.0
    N: float = 0.0
    manure_mass: float = 0.0
    TS: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    P: float = 0.0
    P_frac: float = 0.0
    K: float = 0.0
    CH4: float = 0.0

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""

        # The following calculations will need to agree with
        # how the animal module produces manure data
        # self.urea *= Constants.UREA_MOLAR_MASS  # mol/L x g/mol = g/L
        # self.TAN *= Constants.TAN_MOLAR_MASS  # mol/L x g/mol = g/L
        # self.N *= Constants.GRAMS_TO_KG  # kg
        # self.VSd *= Constants.GRAMS_TO_KG  # kg
        # self.VSnd *= Constants.GRAMS_TO_KG  # kg
        # self.P *= Constants.GRAMS_TO_KG  # kg
        # self.K *= Constants.GRAMS_TO_KG  # kg
        pass

    @staticmethod
    def get_instance(animal_manure, num_animals: int) -> PenManure:
        return PenManure(
                urea=animal_manure['U'] / num_animals,
                TAN=animal_manure['TAN_s'] / num_animals,
                N=animal_manure['MN'],
                manure_mass=animal_manure['Mkg'],
                TS=animal_manure['TSd'],
                VSd=animal_manure['VSd'],
                VSnd=animal_manure['VSnd'],
                WIP_frac=animal_manure['WIP_frac'] / num_animals,
                WOP_frac=animal_manure['WOP_frac'] / num_animals,
                P=animal_manure['p_excrt_manure'],
                P_frac=animal_manure['p_frac'] / num_animals,
                K=animal_manure['K_manure'],
                CH4=animal_manure['CH4_manure']
        )
