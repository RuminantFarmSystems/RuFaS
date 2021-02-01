"""
RUFAS: Ruminant Farm Systems Model
File name: dry_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from .general_manure import phosphorus_excreted
from RUFAS.routines.animal.ration.ration_driver import ration_report


def manure_calculations(ration_formulation, feed, BW, milk_prod, p_feces_excrt,
                        p_urine):
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation. Equations referenced are from pseudocode.

    Args:
        ration_formulation: dictionary which stores the calculated ration
        feed: instance of the Feed class
        BW: body weight, kg
        milk_prod: milk production, kg
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
            K: potassium in manure, g/day



    Further calculations to account for entire diet:
    DMI: dry matter intake, kg
    DM: dietary dry matter, % of diet
    CP: dietary crude protein, % of DM
    """
    amount, conc = ration_report(ration_formulation, feed.available_feeds)
    DMI = amount['dm']
    CP = conc['CP']
    K_conc = conc['potassium']

    # Amount of manure, kg [A.3D.A.1]
    Mkg = 0.022 * BW + 21.844

    # Total solids, kg/d [A.3D.A.2]
    TSd = 0.178 * DMI + 2.733

    # Nitrogen in liquid and solid manure , g [A.3D.B.1]
    MN = 12.747 * DMI + 1606.290 * CP/100 - 117.5

    # Amount of potassium excreted, g/day [A.3D.B.3]
    K = 1000 * DMI * K_conc / 100
    
    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(milk_prod, Mkg, p_feces_excrt, p_urine)
    
    return p_excrt, \
           {"U": 0.340,  # TODO: Implement with correct equation
            "TAN_s": 0.14,  # TODO: Implement with correct equation
            "MN": MN,
            "Mkg": Mkg,
            "TSd": TSd,
            "VSd": 7087.413,  # TODO: Implement with correct equation
            "VSnd": 859.390,  # TODO: Implement with correct equation
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac,
            "K": K,
            "CH4": 0
            }
