################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: dry_cow_manure_excretion.py
Description: Determines manure excretion with information from the ration
    formulation, outputs used by the manure module.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################


def manure_calculations():
    """
    TEMPORARY PLACEHOLDER
    Calculates inputs for manure module with information from the
    ration formulation.

    Returns: dictionary containing the following values
        U: urea concentration, mol/L
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry,
            mol/L
        MN: nitrogen in liquid and solid manure, g
        Mkg: amount of manure, kg
        VSd: degradable volatile solids, g
        VSnd: non-degradable volatile solids, g
    """
    return {"U": 0.340,
            "TAN_s": 0.14,
            "MN": 532.407,
            "Mkg": 70.792,
            "VSd": 7087.413,
            "VSnd": 859.390}
