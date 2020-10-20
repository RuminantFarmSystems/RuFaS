"""
RUFAS: Ruminant Farm Systems Model
File name: dry_cow_ration.py
Description: Calculates the ration for dry cows.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""


def optimize():
    """
    Sets up the arguments for the linear programming optimization.

    Returns: a TEMPORARY PLACE HOlDER for the ration formulation
    """
    return {'Corn_grain': 0.0, 'Cotton_seed': 6.0651063,
            'Legume_hay': 13.669348, 'Roasted_soybean': 2.4089406,
            'Rye_hay': 0.0, 'status': 'Optimal', 'objective': 4.536948317}


def calculate_rqmts():
    """
    TEMPORARY PLACEHOLDER
    Calculate the dietary requirements of the animals. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:

    Returns:
        dict: a dictionary that represents the dietary requirements of the
            cows, where the left hand side is nutrients_list and the right hand
            side is calculated in this method
        DMIest: dry matter intake estimation, kg
        DBW: Body weight change (delta body weight = DBW), kg
    """
    nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807},
                      'RU': {'op': '>=', 'val': 0},
                      'ME_DM': {'op': '>=', 'val': 57.238188330372566},
                      'RDP_DM': {'op': '>=', 'val': 2.0347001114951313},
                      'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    return nutrient_rqmts
