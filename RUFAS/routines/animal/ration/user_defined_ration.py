"""
RUFAS: Ruminant Farm Systems Model
File name: user_defined_ration.py
Description: Tools for accessing and providing user-defined ration  variables
    Main class used to read JSON as singleton, return ration percentages where needed
Author: Joseph C. Waddell, jw2574@cornell.edu
"""

from typing import Any, Dict, List, Union
import json

class UserDefinedRationValues(object):
    """
    Reads in the user_defined_ration JSON and collects variables and dicts to use later
    """

    # check the setup JSON
    # if user-defined-ration is NOT selected, initialize as NULL
    
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UserDefinedRationValues, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if UserDefinedRationValues.__instance is None:
            UserDefinedRationValues.__instance = self
            with open('input/userdefinedration/user_defined_ration_input_percentages.json', 'r') as f:
                ration_all = json.load(f)
            lactating_cow_ration = ration_all['cow_lactating']
            dry_cow_ration = ration_all['cow_dry']
            heifer_ration = ration_all['growing_heifers']
            calf_ration = ration_all['calf']
            close_up_ration = ration_all['close_up']
            self.calf_ration: Dict[str, Any] = calf_ration
            self.heifer_ration: Dict[str, Any] = heifer_ration
            self.lactating_cow_ration: Dict[str, Any] = lactating_cow_ration
            self.dry_cow_ration: Dict[str, Any] = dry_cow_ration
            self.ration_all: Dict[str, Any] = ration_all
            self.close_up_ration: Dict[str, Any] = close_up_ration
            self.tolerance = ration_all['tolerance']
            self.milk_reduction_percent = ration_all['milk_reduction_percent']
            self.udr_or_not = None
            

def ration_to_use(pen_animal_combo, available_feeds) -> Dict:
    """
    Function outputs the correct dictionary from the UserDefinedRationValues class
    
    Parameters
    ----------
    pen_animal_combo: Pen.AnimalCombination

    Returns
    -------
    ration_percents: Dict
        dictionary of feed ids and their associated percentage of DMI 
    """
    udrv = UserDefinedRationValues()
    group = pen_animal_combo.name 
    if group == 'LAC_COW':
        ration_percents = udrv.lactating_cow_ration
    # elif pen.classes
    elif group == 'GROWING':
        ration_percents = udrv.heifer_ration
    elif group == 'CLOSE_UP':
        ration_percents = udrv.dry_cow_ration
    else: 
        ration_percents = udrv.calf_ration
    return feed_quality_fix(ration_percents, available_feeds)


def feed_quality_fix(ration_percents, available_feeds):
    key_list = list(ration_percents.keys())
    for key in key_list:
        if int(key) not in available_feeds['feed_id']:
            new_key = str(int(key)+2)
            ration_percents[new_key] = ration_percents[key]
            del ration_percents[key]
    return ration_percents