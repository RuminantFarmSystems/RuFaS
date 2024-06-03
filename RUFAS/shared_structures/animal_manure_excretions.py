from typing import TypedDict


class AnimalManureExcretions(TypedDict):
    """
    A TypedDict class that specifies the structure of the dictionary of animal manure excretion values.

    Attributes
    ----------
    urea: float
        Concentration of urea in manure (g/L).
    urine: float
        Amount of urine excreted (kg).
    total_ammoniacal_nitrogen_concentration: float
        Concentration of total ammoniacal manure_nitrogen in the manure slurry (g/L).
    urine_nitrogen: float
        Amount of nitrogen in urine (kg).
    manure_nitrogen: float
        Amount of nitrogen in manure (kg).
    manure_mass: float
        Amount of manure (kg).
    total_solids: float
        Amount of total solids (kg).
    degradable_volatile_solids: float
        Amount of degradable volatile solids (kg).
    non_degradable_volatile_solids: float
        Amount of non-degradable volatile solids (kg).
    inorganic_phosphorus_fraction: float
        Fraction of water extractable inorganic phosphorus (unitless).
    organic_phosphorus_fraction: float
        Fraction of water extractable organic phosphorus (unitless).
    non_water_inorganic_phosphorus_fraction: float
        Fraction of non-water extractable inorganic phosphorus (unitless).
    non_water_organic_phosphorus_fraction: float
        Fraction of non-water extractable organic phosphorus (unitless).
    phosphorus: float
        Amount of phosphorus excreted in manure (g).
    phosphorus_fraction: float
        Fraction of phosphorus in manure (unitless).
    potassium: float
        Amount of potassium in manure (g).
    enteric_methane_g: float
        Amount of methane emissions (g/day).

    """

    urea: float
    urine: float
    total_ammoniacal_nitrogen_concentration: float
    urine_nitrogen: float
    manure_nitrogen: float
    manure_mass: float
    total_solids: float
    degradable_volatile_solids: float
    non_degradable_volatile_solids: float
    inorganic_phosphorus_fraction: float
    organic_phosphorus_fraction: float
    non_water_inorganic_phosphorus_fraction: float
    non_water_organic_phosphorus_fraction: float
    phosphorus: float
    phosphorus_fraction: float
    potassium: float
    enteric_methane_g: float
