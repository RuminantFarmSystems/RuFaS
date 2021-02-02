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


def manure_calculations(ration_formulation, feed, BW, DIM, mPrt,
                        milk_prod, p_feces_excrt, p_urine, methane_model, mFat, ME_intake):
    """
    Calculates inputs for manure module with information from the
    ration formulation. Equations referenced are from pseudocode.

    Args:
        milk_prod: milk production, kg
        ration_formulation: dictionary which stores the calculated ration
        feed: instance of the Feed class
        BW: body weight, kg
        DIM: days in milk, d
        mPrt: milk protein, % of milk (from animal input)
        p_feces_excrt: amount of P excreted by an animal (g)
        p_urine: amount of P required for urine production (g)
        methane_model: methane model used for methane emission calculations
        mFat: milk fat, % of milk
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
    starch = 26  # Temporary placeholder (as %)
    amount, conc = ration_report(ration_formulation, feed.available_feeds)
    DMI = amount['dm']
    Ash_diet_content = amount['ash']
    ASH = conc["ash"]
    DM = conc['dm']
    ADF = conc['ADF']
    CP = conc['CP']
    LIG = conc['lignin']
    NDF = conc['NDF']
    K_conc = conc['potassium']
    EE = conc["EE"]

    # Calculating gross energy concentration (Moraes et al. 2014)
    soluble_residue = (100 - ASH) - NDF - CP - EE
    GE_conc = 0.263 * CP + 0.522 * EE + 0.198 * NDF + 0.160 * soluble_residue

    # Faecal water, kg (Eq 1.2)
    F_water = 1.987 * DMI + 0.348 * ADF - 0.412 * CP - 0.074 * DM - 0.0057 * DIM

    # Faecal dry matter, kg (Eq 1.3)
    F_DM = -0.576 + 0.370 * DMI - 0.075 * CP + 0.059 * ADF

    # Total urine, kg (Eq 1.4)
    U_E = -7.742 + 0.388 * DMI + 0.726 * CP + 2.066 * mPrt

    # Amount of manure, kg (Eq 1.1)
    Mkg = F_water + F_DM + U_E

    # Total solids, kg/d [A.3C.A.2]
    TSd = -0.576 + 0.370 * DMI + 0.059 * ADF - 0.075 * CP

    # Faecal nitrogen, g (Eq 2.2)
    F_N = (-0.0368 +
           0.0096 * DMI + 0.0022 * CP +
           0.0034 * LIG -
           0.000043 * BW) * 1000

    # Urine nitrogen, g (Eq 2.3)
    U_N = (-0.2837 +
           0.0068 * DMI + 0.0155 * CP +
           0.00013 * DIM +
           0.000092 * BW) * 1000

    # Nitrogen in liquid and solid manure, g (Eq 2.1)
    MN = F_N + U_N

    # Organic matter intake, kg
    OMI = DMI - Ash_diet_content

    # Degradable volatile solids, g (Eq 3.1)
    VSd = (-1.017 + 0.364 * OMI + 0.029 * NDF - 0.023 * CP) * 1000

    # Non-degradable volatile solids, g (Eq 4.1)
    VSnd = (-0.184 + 0.038 * OMI + 0.007 * NDF - 0.001 * CP) * 1000

    # Urea concentration, mol/L (Eq 5.1)
    U = (-1.16 + 0.86 * (U_N / U_E)) / 28

    # Total ammoniacal nitrogen concentration in the manure slurry,
    # mol/L (Eq 6.1)
    TAN_s = (-162.4 * U * U + 96.4 * U) / 100

    # Amount of potassium excreted, g/day [A.3C.C.1]
    K = 1.822 * milk_prod + 2688.88 * (mPrt / 100) + 156.93 * DMI * (K_conc / 100) - 91.755

    # Methane Emissions
    if methane_model == "Mutian":  # Mutian
        CH4 = - 126 + 11.3 * DMI + 2.30 * NDF + 28.8 * mFat + 0.148 * BW
    elif methane_model == "Mills":  # Mills
        CH4 = 45.98 * math.exp(- ((- 0.0011 * starch / ADF) + 0.0045) * ME_intake)
    elif methane_model == "IPCC":   # IPCC
        CH4 = (0.065 * (GE_conc / 100) * DMI) / 0.05565

    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(milk_prod, Mkg, p_feces_excrt, p_urine)

    return p_excrt, \
           {"U": U,
            "TAN_s": TAN_s,
            "MN": MN,
            "Mkg": Mkg,
            "TSd": TSd,
            "VSd": VSd,
            "VSnd": VSnd,
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac,
            "K_manure": K,
            "CH4_manure": CH4
            }
