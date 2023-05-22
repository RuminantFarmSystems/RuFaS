"""
RUFAS: Ruminant Farm Systems Model
File name: user_defined_ration.py
Description: Tools for accessing and providing user-defined ration  variables
    Main class used to read JSON as singleton, return ration percentages where needed
Author: Joseph C. Waddell, jw2574@cornell.edu
"""

from typing import Any, Dict, List, Union
import json

def generate_user_feed_json(ration_percentage_filename = 'input/userdefinedration/user_defined_ration_input_percentages.json',
                            reference_filename = 'input/feed/purchased_feed.json',
                            new_feed_filename = 'input/feed/user_defined_ration_feed.json')->None:
    """
    This will use the user_defined_ration file to generate the feed input json
    It reads in the input file, compares it to the purchased_feed file, and prints a new user_defined_ration_feed file

    Returns nothing, BUT the feed JSON needs to have the PRICES manually adjusted. placeholdervalues of 0.9999 
        used for any not found in the reference JSON

    Parameters
    ----------
    ration_percentage_filename: str

    reference_filename: str

    new_feed_filename: str

    """
    import json
    with open(ration_percentage_filename, 'r') as f:
        rationall = json.load(f)
        key_list = list(rationall.keys())
    ration_calf = rationall[key_list[0]]

    ration_all_heifers = rationall[key_list[1]]
    ration_cow_lactating = rationall[key_list[2]]
    ration_cow_dry = rationall[key_list[3]]
    with open(reference_filename, 'r') as f:
        ff = json.load(f)
        key_list = list(ff.keys())

    new_calf_feeds = [int(i) for i in ration_calf]
    new_growing_feeds = [int(i) for i in ration_all_heifers]
    new_close_up_feeds = [int(i) for i in ration_cow_dry]
    new_lac_cow_feeds = [int(i) for i in ration_cow_lactating]

    ff['calf_feeds']=new_calf_feeds
    ff['growing_feeds']=new_growing_feeds
    ff['close_up_feeds']=new_close_up_feeds
    ff['lac_cow_feeds']=new_lac_cow_feeds

    with open(new_feed_filename, 'w') as file:
        json.dump(ff, file)
    with open(new_feed_filename, 'r') as f:
        fff = json.load(f)
    fff['purchased_feeds_costs']

    feedslisted = list(fff['purchased_feeds_costs'].keys())

    newlist = new_lac_cow_feeds + new_calf_feeds + new_close_up_feeds \
        + new_growing_feeds
    setlist = set(newlist)
    newsetted = list(setlist)
    newsetted.sort()
    newsetted = [str(i) for i in newsetted]
    difflist = list(set(newsetted).difference(feedslisted))
    difflist.sort()
    newpricesdict = {}
    for i in newsetted:
        print(i)
        if i in fff['purchased_feeds_costs'].keys():
            price = fff['purchased_feeds_costs'][str(i)]
            print(fff['purchased_feeds_costs'][str(i)])
        else: 
            price = 0.9999
        newpricesdict[i] = price
    fff['purchased_feeds_costs'] = newpricesdict
    purchased_feeds_keynames = list(newpricesdict.keys())
    fff['purchased_feeds'] = [int(i) for i in purchased_feeds_keynames]
    with open(new_feed_filename, 'w') as file:
        json.dump(fff, file, indent=3)


class user_defined_ration_values(object):
    """
    Reads in the user_defined_ration JSON and collects variables and dicts to use later
    """

    # check the setup JSON
    # if user-defined-ration is NOT selected, initialize as NULL
    
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(user_defined_ration_values, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if user_defined_ration_values.__instance is None:
            user_defined_ration_values.__instance = self
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
 
            self.udr_or_not = False
            

def ration_to_use(pen_animal_combo):
    """
    Function outputs the correct dictionary from the user_defined_ration_values class
    
    Parameters
    ----------
    pen_animal_combo

    Returns
    -------
    ration_percents: Dict
        dictionary of feed ids and their associated percentage of DMI 
    """
    udrv = user_defined_ration_values()
    # print('udrv.udr_or_not' + str(udrv.udr_or_not))
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
    return ration_percents
