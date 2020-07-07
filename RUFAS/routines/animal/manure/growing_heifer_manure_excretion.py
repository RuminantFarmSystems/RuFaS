"""
RUFAS: Ruminant Farm Systems Model
File name: growing_heifer_manure_excretion.py
Description: Determines manure excretion with information from the
    ration formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
from RUFAS.routines.feed.feed import FeedNames, Nutrients
from .general_manure import phosphorus_excreted


def manure_calculations(ration_formulation, feed, BW, p_feces_excrt, p_urine):
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation.

    Args:
        ration_formulation: dictionary which stores the calculated ration
        feed: instance of the Feed class
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
    DMI = 0
    total_diet = 0  # in kg
    CP_diet_content = 0
    for key in ration_formulation:
        # not every key in the ration_formulation dictionary refers to a feed
        if key in feed.managed_feed_names:
            # percentages of the DM of each nutrient
            managed_feed = FeedNames[key]
            nutrients = feed.values(managed_feed)
            DM_feed_content = 0.01 * nutrients[Nutrients.DM.name]
            CP_feed_content = 0.01 * nutrients[Nutrients.CP_DM.name]

            # kg of each nutrient
            DM_feed_amount = ration_formulation[key]
            CP_feed_amount = CP_feed_content * DM_feed_amount

            # add to running sums
            as_fed_feed_amount = DM_feed_amount / DM_feed_content
            total_diet += as_fed_feed_amount
            DMI += DM_feed_amount
            CP_diet_content += CP_feed_amount

    # to find total percentages
    CP = CP_diet_content / DMI * 100

    # Amount of manure, kg [A.3B.A.1]
    Mkg = 3.886 * DMI - 0.029 * BW + 5.641
    
    # nitrogen in liquid and solid manure, g [A.3D.B.1]
    MN = 78.390 * DMI * CP / 100 + 51.35

    p_excrt, WIP_frac, WOP_frac, p_excrt_manure, p_frac = \
        phosphorus_excreted(0, Mkg, p_feces_excrt, p_urine)
    return p_excrt, \
           {"U": 0.340, #TODO: Implement with correct equation
            "TAN_s": 0.14, #TODO: Implement with correct equation
            "MN": MN,
            "Mkg": Mkg,
            "VSd": 7087.413, #TODO: Implement with correct equation
            "VSnd": 859.390, #TODO: Implement with correct equation
            "WIP_frac": WIP_frac,
            "WOP_frac": WOP_frac,
            "p_excrt_manure": p_excrt_manure,
            "p_frac": p_frac
            }
