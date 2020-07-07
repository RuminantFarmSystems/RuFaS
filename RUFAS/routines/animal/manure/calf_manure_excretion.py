"""
RUFAS: Ruminant Farm Systems Model
File name: calf_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""

from .general_manure import phosphorus_excreted


def manure_calculations(BW, p_feces_excrt, p_urine):
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation.

    Args:
        BW: body weight, kg
        p_feces_excrt: amount of P excreted by an animal (g)
        p_urine: amount of P required for urine production (g)

    Returns:
        p_excrt: amount of P excreted by animal, g
        and a dictionary containing the following values
            U: urea concentration, mol/L
            TAN_s: total ammoniacal nitrogen concentration in the manure slurry,
                mol/L
            MN: nitrogen in liquid and solid manure, g
            Mkg: amount of manure, kg
            VSd: degradable volatile solids, g
            VSnd: non-degradable volatile solids, g
            WIP_frac: water extractable inorganic P fraction
            WOP_frac: water extractable organic P fraction
            p_excrt_manure: manure P excretion for manure module input (g)
            p_frac: P fraction of manure
    """
    # Amount of manure, kg [A.3A.A.1]
    Mkg = 0.0567 * BW
    
    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(0, Mkg, p_feces_excrt, p_urine)
    return p_excrt, \
           {"U": 0.340, #TODO: Implement with correct equation
            "TAN_s": 0.14, #TODO: Implement with correct equation
            "MN": 532.407, #TODO: Implement with correct equation
            "Mkg": Mkg,
            "VSd": 7087.413, #TODO: Implement with correct equation
            "VSnd": 859.390, #TODO: Implement with correct equation
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac
            }
