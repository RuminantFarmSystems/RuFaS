################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: growing_heifer_manure_excretion.py
Description: Determines manure excretion with information from the
    ration formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
from .general_manure import phosphorus_excreted


def manure_calculations(BW, p_intake):
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation.

    Args:
        BW: body weight of animal, kg
        p_intake: amount of P in the formulated ration, g

    Returns: dictionary containing the following values
        U: urea concentration, mol/L
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry,
            mol/L
        MN: nitrogen in liquid and solid manure, g
        Mkg: amount of manure, kg
        VSd: degradable volatile solids, g
        VSnd: non-degradable volatile solids, g
        p_excrt: amount of P excreted by animal, g
        WIP_frac: water extractable inorganic P fraction
        WOP_frac: water extractable organic P fraction
    """
    total_manure = 70.792
    p_excrt, WIP_frac, WOP_frac = \
        phosphorus_excreted(BW, 0, p_intake, total_manure)
    return {"U": 0.340,
            "TAN_s": 0.14,
            "MN": 532.407,
            "Mkg": total_manure,
            "VSd": 7087.413,
            "VSnd": 859.390,
            "p_excrt": p_excrt,
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac
            }
