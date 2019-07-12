################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: calf_ration.py
Description: Calculates the ration for calves.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################

def optimize(feed, rqmts):
    """
    TEMPORARY PLACEHOLDER
    Sets up the arguments for the linear programming optimization.

    Args:
        feed : instance of the Feed class
        rqmts : dict which represents the dietary requirements of the cows

    Returns:
    """
    pass

def calculate_rqmts():
    """
    TEMPORARY PLACEHOLDER
    Calculate the dietary requirements of the animals. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:

    Returns:
        dict : a dictionary that represents the dietary requirements of the cows,
            where the left hand side is nutrients_list and the right hand side is
            calculated in this method
        DMIest: dry matter intake estimation, kg
        DBW: Body weight change (delta body weight = DBW), kg
    """
    nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    DMIest = 27.620363504458798 
    DBW = -0.4125
    return nutrient_rqmts, DMIest, DBW