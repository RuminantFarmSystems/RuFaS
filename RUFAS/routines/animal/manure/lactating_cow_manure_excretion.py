"""
RUFAS: Ruminant Farm Systems Model
File name: lactating_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from .general_manure import phosphorus_excreted
from RUFAS.routines.animal.ration.ration_driver import ration_report
import math


def manure_calculations(ration_formulation, feed, bw, days_milk, milk_protein,
                        milk_prod, p_feces_excrt, p_urine, methane_model, milk_fat, ME_intake):
    """
    Calculates inputs for manure module with information from the
    ration formulation. Equations referenced are from pseudocode.

    Args:
        milk_prod: milk production, kg
        ration_formulation: dictionary which stores the calculated ration
        feed: instance of the Feed class
        bw: body weight, kg
        days_milk: days in milk, d
        milk_protein: milk protein, % of milk (from animal input)
        p_feces_excrt: amount of P excreted by an animal (g)
        p_urine: amount of P required for urine production (g)
        methane_model: methane model used for methane emission calculations
        milk_fat: milk fat, % of milk
        ME_intake: metabolizable energy intake, Mcal/kg DM

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
    """
    amount, conc = ration_report(ration_formulation, feed.available_feeds)
    dm_intake = amount['dm']
    Ash_diet_content = amount['ash']
    ASH_conc = conc["ash"]
    DM_conc = conc['dm']
    ADF_conc = conc['ADF']
    CP_conc = conc['CP']
    lignin_conc = conc['lignin']
    NDF_conc = conc['NDF']
    K_conc = conc['potassium']
    EE_conc = conc["EE"]
    starch_conc = conc['starch']

    # Faecal water, kg [A.3C.A.1]
    fecal_water = 1.987 * dm_intake + 0.348 * ADF_conc - 0.412 * CP_conc - 0.074 * DM_conc - 0.0057 * days_milk

    # Total Solids, kg [A.3C.A.2]
    total_solids = -0.576 + 0.370 * dm_intake - 0.075 * CP_conc + 0.059 * ADF_conc

    # Total urine, kg [A.3C.A.3]
    urine = -7.742 + 0.388 * dm_intake + 0.726 * CP_conc + 2.066 * milk_protein

    # Amount of manure, kg [A.3C.A.4]
    manure = fecal_water + total_solids + urine

    # Faecal nitrogen, g [A.3C.B.1]
    N_feces = (-0.0368 +
               0.0096 * dm_intake + 0.0022 * CP_conc +
               0.0034 * lignin_conc -
               0.000043 * bw)

    # Urine nitrogen, g [A.3C.B.2]
    N_urine = (-0.2837 +
               0.0068 * dm_intake + 0.0155 * CP_conc +
               0.00013 * days_milk +
               0.000092 * bw)

    # Nitrogen in liquid and solid manure, g [A.3C.B.3]
    N_manure = N_feces + N_urine

    # Organic matter intake, kg
    OM_intake = dm_intake - Ash_diet_content

    # Degradable volatile solids, g [A.3C.A.5]
    degradable_volatile_solids = (-1.017 + 0.364 * OM_intake + 0.029 * NDF_conc - 0.023 * CP_conc) * 1000

    # Non-degradable volatile solids, g [A.3C.A.6]
    nondegradable_volatile_solids = (-0.184 + 0.038 * OM_intake + 0.007 * NDF_conc - 0.001 * CP_conc) * 1000

    # Urea concentration, mol/L (Eq 5.1)
    U = (-1.16 + 0.86 * (N_urine / urine)) / 28

    # Total ammoniacal nitrogen concentration in the manure slurry,
    # mol/L (Eq 6.1)
    TAN_s = (-162.4 * U * U + 96.4 * U) / 100

    # Amount of potassium excreted, g/day [A.3C.C.1]
    K_manure = 1.822 * milk_prod + 2688.88 * (milk_protein / 100) + 156.93 * dm_intake * (K_conc / 100) - 91.755

    # Methane Emissions
    if methane_model == "Mutian":  # [A.3E.C.1]
        methane_emis = - 126 + 11.3 * dm_intake + 2.30 * NDF_conc + 28.8 * milk_fat + 0.148 * bw
    elif methane_model == "Mills":  # [A.3E.C.2]
        methane_emis = (45.98 - 45.98 * math.exp(- ((- 0.0011 * starch_conc / ADF_conc) + 0.0045)
                                                 * ME_intake * 4.184)) / 0.05565
    elif methane_model == "IPCC":  # IPCC
        # Calculating gross energy concentration (Moraes et al. 2014)
        soluble_residue = (100 - ASH_conc) - NDF_conc - CP_conc - EE_conc
        gross_energy_conc = 0.263 * CP_conc + 0.522 * EE_conc + 0.198 * NDF_conc + 0.160 * soluble_residue  # [A.3E.C.3]

        methane_emis = (0.065 * gross_energy_conc * dm_intake) / 0.05565  # [A.3E.C.4]

    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(milk_prod, manure, p_feces_excrt, p_urine)

    return p_excrt, \
           {"U": U,
            "TAN_s": TAN_s,
            "MN": N_manure,
            "Mkg": manure,
            "TSd": total_solids,
            "VSd": degradable_volatile_solids,
            "VSnd": nondegradable_volatile_solids,
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac,
            "K_manure": K_manure,
            "CH4_manure": methane_emis
            }
