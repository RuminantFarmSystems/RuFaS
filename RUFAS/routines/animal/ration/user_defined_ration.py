"""
User-defined ration logic

General workflow is as follows:
User should first modify the following file:
input/userdefinedration/userdefinedration_test.json
This file contains a dictionary where the key value pairs are the feed ID and their associated desired percent of the suplied ration
User will note that there are a few other values they can change.
One is the amount of tolerance of those percentages allowed in the optmization step. 
The idea here is that a user may want 30% of the ration to be feed X, but is OK within some tolerance of those percentages.
    Because these are percentages of the percent tolerance, not raw +/- values, a tolerance of 0.033 would allow any value from 29-30.9
NOTE: We need to think about how to handle cases in which the solution drop below the total DMI: e.g. not meeting the minimum DMI because the target percentages were too high, and optmization lowered the totals - and they don't sum to 100.

Once this is defined, the user must ensure that the main input JSON is "pointing" to the 'input/feed/user_defined_ration_feed.json'
This file is supplied, but will be rewritten to update the ration items found in the user_defined_ration_input_percentages file supplied.
NOTE: price values will need to be manually adjusted, as values not found in the reference_filename aren't supplied, and instead filled with 0.99999

Now the user must note that inside the "animal": "animal_user_input_ration.json"
    Inside this JSON make sure that the ['ration']['user_input'] == True"ration": {"user_input": true,...
    
Once this prep has been done, run RuFaS as normal. 

"""

from typing import Any, Dict, List, Union
from RUFAS.util import Utility
import json

#from RUFAS.routines.animal.ration import ration_driver as ration_driver
#available_feeds = ration_driver.AvailableFeeds()

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

    # ff['calf_feeds']
    # ff['growing_feeds']
    # ff['close_up_feeds']
    # ff['lac_cow_feeds']

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

    Attributes
    ----------
    something_somethingelse : Dict[str, Any]
        Contains variables 
    
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
            self.heifer_ration: Dict[str, Any]  = heifer_ration
            self.lactating_cow_ration: Dict[str, Any]  = lactating_cow_ration
            self.dry_cow_ration: Dict[str, Any]  = dry_cow_ration
            self.ration_all: Dict[str, Any]  = ration_all
            self.close_up_ration: Dict[str, Any] = close_up_ration

            self.tolerance = ration_all['tolerance']
            self.milk_reduction_percent = ration_all['milk_reduction_percent']
            
            self.udr_or_not = True # TODO: retrieve this value from the animal_management config
            
udrv = user_defined_ration_values()

def ration_to_use(pen_animal_combo):
    """
    Function outputs the correct dictionary from the user_defined_ration_values class
    
    Parameters
    ----------
    animal_type: str
        animal type e.g. 'calf', 'heifer', 'cow'
    lactating: bool
        state of whether a cow is actively lactating or not 

    Returns
    -------
    ration_percents: Dict
        dictionary of feed ids and their associated percentage of DMI 
    """
    group = pen_animal_combo.name 
    if group == 'LAC_COW':
        ration_percents = udrv.lactating_cow_ration
    # elif pen.classes
    elif group == 'GROWING':
        ration_percents = udrv.heifer_ration
    elif group == 'CLOSE_UP':
        ration_percents = udrv.close_up_ration
    else: 
        ration_percents = udrv.calf_ration
    return ration_percents
