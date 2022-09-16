"""
RUFAS: Ruminant Farm Systems Model
File name: manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations

from dataclasses import dataclass

from RUFAS.routines.manure.constants.constants import ManureManagementConstants as Constants


@dataclass
class Manure:
    """A class that represents the manure data extracted from the animal module.

    Attributes:
        U: urea concentration, g/L.
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry, g/L.
        MN: nitrogen in liquid and solid manure, kg.
        Mkg: amount of manure, kg.
        TSd: total solids, g.
        VSd: degradable volatile solids, kg.
        VSnd: non-degradable volatile solids, kg.
        WIP_frac: water extractable inorganic P fraction, unitless.
        WOP_frac: water extractable organic P fraction, unitless.
        p_excrt_manure: manure P excretion for manure module input, kg.
        p_frac: P fraction of manure.
        K_manure: potassium in manure, kg/day.
        CH4_manure: methane emission, g/day.

    """

    U: float = 0.0
    TAN_s: float = 0.0
    MN: float = 0.0
    Mkg: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    p_excrt_manure: float = 0.0
    p_frac: float = 0.0
    K_manure: float = 0.0
    CH4_manure: float = 0.0

    def __post_init__(self):
        """Performs any necessary unit conversion after initialization."""

        self.U *= Constants.UREA_MOLAR_MASS  # mol/L x g/mol = g/L
        self.TAN_s *= Constants.TAN_MOLAR_MASS  # mol/L x g/mol = g/L
        self.MN *= Constants.GRAMS_TO_KG  # kg
        # self.TSd *= Constants.GRAMS_TO_KG  # kg
        self.VSd *= Constants.GRAMS_TO_KG  # kg
        self.VSnd *= Constants.GRAMS_TO_KG  # kg
        self.p_excrt_manure *= Constants.GRAMS_TO_KG  # kg
        self.K_manure *= Constants.GRAMS_TO_KG  # kg
