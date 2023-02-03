"""
RUFAS: Ruminant Farm Systems Model
File name: calf_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""

from .general_manure import phosphorus_excreted


def manure_calculations(bw, p_feces_excrt, p_urine):
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation. Equations referenced are from pseudocode.

    Args:
        bw: body weight, kg
        p_feces_excrt: amount of P excreted by an animal (g)
        p_urine: amount of P required for urine production (g)

    Returns:
        p_excrt: amount of P excreted by animal, g
        and a dictionary containing the following values
            U: urea concentration, mol/L
            Urine: # TODO: Add description
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
            K: potassium in manure, g/day

    """
    # Amount of manure, kg [A.3A.A.1]
    manure = 0.0567 * bw

    # Total solids, kg/day [A.3A.A.2]
    total_solids = 0.0093 * bw

    # Methane Emissions [A.3A.C.1]
    methane_emis = (0.013 * (bw ** 0.75) * 4.184) / 0.05565

    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(0, manure, p_feces_excrt, p_urine)

    return p_excrt, \
           {"U": 0.340,  # TODO: Implement with correct equation
            "Urine": 2,
            "TAN_s": 0.14,  # TODO: Implement with correct equation
            "MN": 532.407,  # TODO: Implement with correct equation
            "Mkg": manure,
            "TSd": total_solids,
            "VSd": 7087.413,  # TODO: Implement with correct equation
            "VSnd": 859.390,  # TODO: Implement with correct equation
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac,
            "K_manure": 0,
            "CH4_manure": methane_emis
            }
