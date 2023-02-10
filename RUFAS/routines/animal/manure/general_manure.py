from typing import Final
from typing import Literal
from typing import Tuple
from typing import TypedDict

from RUFAS.general_constants import GeneralConstants


class AnimalManureExcretions(TypedDict):
    """A TypedDict class that specifies the structure of the dictionary of animal manure excretion values.

    """
    urea: float
    """Concentration of urea in manure, mol/L."""

    urine: float
    """Amount of urine in manure, g."""

    total_ammoniacal_nitrogen: float
    """Concentration of total ammoniacal nitrogen in the manure slurry, mol/L."""

    nitrogen: float
    """Amount of nitrogen in manure, g."""

    manure_mass: float
    """Amount of manure, kg."""

    total_solids: float
    """Amount of total solids, kg."""

    degradable_volatile_solids: float
    """Amount of degradable volatile solids, g."""

    non_degradable_volatile_solids: float
    """Amount of non-degradable volatile solids, g."""

    inorganic_phosphorus_fraction: float
    """Fraction of water extractable inorganic phosphorus, unitless."""

    organic_phosphorus_fraction: float
    """Fraction of water extractable organic phosphorus, unitless."""

    phosphorus: float
    """Amount of phosphorus excreted in manure, g."""

    phosphorus_fraction: float
    """Fraction of phosphorus in manure, unitless."""

    potassium: float
    """Amount of potassium in manure, g."""

    methane: float
    """Amount of methane emissions, g/day."""


def calculate_phosphorus_excretion_values(daily_milk_production: float,
                                          total_manure_excreted: float,
                                          fecal_phosphorus: float,
                                          urine_phosphorus_required: float) \
        -> Tuple[float, float, float, float, float]:
    """Calculates a set of phosphorus excretion values produced by a given animal.

    Parameters
    ----------
    daily_milk_production : float
        Amount of daily milk produced by the animal, kg.
        This parameter should be set to 0 if this function is called for a non-cow animal.
    total_manure_excreted : float
        Amount of manure excreted by the animal, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the animal, g.
    float
        Fraction of extractable inorganic phosphorus, unitless.
    float
        Fraction of water extractable organic phosphorus, unitless.
    float
        Amount of manure phosphorus excreted, g.
    float
        Fraction of phosphorus in the manure, unitless.

    """
    # P fraction of manure (A.3.A.1)
    manure_phosphorus_fraction = (fecal_phosphorus + urine_phosphorus_required) / (
            total_manure_excreted * GeneralConstants.KG_TO_GRAMS)

    # Water extractable Inorganic P (WIP) fraction - fraction of manure
    # compromised of inorganic water extractable P (A.3.A.2)
    inorganic_phosphorus_fraction = 0.50 * manure_phosphorus_fraction

    # Water extractable Organic P (WOP) fraction - fraction of maure
    # compromised of organic water extractable P (A.3.A.3)
    organic_phosphorus_fraction = 0.05 * manure_phosphorus_fraction

    # amount of P in milk per animal (g) (A.3E.B.1)
    phosphorus_in_milk = 0.0009 * daily_milk_production * GeneralConstants.KG_TO_GRAMS

    # manure P excretion for manure module input (g) (A.3.B.2)
    manure_phosphorus_excreted = fecal_phosphorus + urine_phosphorus_required

    # amount of P excreted by an animal (g) (A.3.B.3)
    total_phosphorus_excreted = phosphorus_in_milk + fecal_phosphorus + urine_phosphorus_required

    return (total_phosphorus_excreted, inorganic_phosphorus_fraction, organic_phosphorus_fraction,
            manure_phosphorus_excreted, manure_phosphorus_fraction)
