"""
User-defined ration logic

"""

from typing import Any, Dict, List, Union
from RUFAS.util import Utility
import json

#from RUFAS.routines.animal.ration import ration_driver as ration_driver
#available_feeds = ration_driver.AvailableFeeds()

def generate_user_feed_json(ration_percentage_filename = 'input/userdefinedration/userdefinedration_test.json',
                            reference_filename = 'input/feed/purchased_feed.json',
                            new_feed_filename = 'input/feed/user_defined_ration_feed.json')->None:
    """
    This will use the user_defined_ration file to generate the feed input json
    It reads in the input file, compares it to the purchased_feed file, and prints a new user_defined_ration_feed file

    Returns nothing, BUT the feed JSON needs to have the PRICES manually adjusted. placeholdervalues of 0.9999 
        used for any not found in the reference JSON

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

    ff['calf_feeds']
    ff['growing_feeds']
    ff['close_up_feeds']
    ff['lac_cow_feeds']

    new_calf_feeds = [int(i) for i in ration_calf]
    new_growing_feeds = [int(i) for i in ration_all_heifers]
    new_close_up_feeds = [int(i) for i in ration_cow_dry]
    new_lac_cow_feeds = [int(i) for i in ration_cow_lactating]

    ff['calf_feeds']=new_calf_feeds
    ff['growing_feeds']=new_growing_feeds
    ff['close_up_feeds']=new_close_up_feeds
    ff['lac_cow_feeds']=new_lac_cow_feeds

    # fftoprint = json.dumps(ff, sort_keys=True, indent=4)

    with open(new_feed_filename, 'w') as file:
        json.dump(ff, file)
    with open(new_feed_filename, 'r') as f:
        fff = json.load(f)
    fff['purchased_feeds_costs']

    feedslisted = list(fff['purchased_feeds_costs'].keys())
    feedsprices = list(fff['purchased_feeds_costs'].values())

    newlist = new_lac_cow_feeds + new_calf_feeds + new_close_up_feeds \
        + new_growing_feeds
    setlist = set(newlist)
    newsetted = list(setlist)
    newsetted.sort()
    newsetted = [str(i) for i in newsetted]
    # [newsetted not in feedslisted for newsetted in newsetted]
    difflist = list(set(newsetted).difference(feedslisted))
    difflist.sort()

    dummyprices = [1 for i in difflist]
    len(feedslisted)
    len(difflist)
    len(newsetted)
    len(dummyprices)

    newpricesdict = {}
    for i in newsetted:
        print(i)
        if i in fff['purchased_feeds_costs'].keys():
            price = fff['purchased_feeds_costs'][str(i)]
            print(fff['purchased_feeds_costs'][str(i)])
        else: 
            price = 0.9999
            # print(0.9999)
        newpricesdict[i] = price
    # len(newpricesdict)
    fff['purchased_feeds_costs'] = newpricesdict
    purchased_feeds_keynames = list(newpricesdict.keys())
    fff['purchased_feeds'] = [int(i) for i in purchased_feeds_keynames]
    with open(new_feed_filename, 'w') as file:
        json.dump(fff, file, indent=3)
    # with open(new_feed_filename, 'r') as f:
    #     fff = json.load(f)


def triple_ration_formatting(ration):
    triple_ration_formatted = []
    for key, value in ration.keys():
        triple_ration_formatted.append=value
        triple_ration_formatted.append=0.0
        triple_ration_formatted.append=0.0
    return triple_ration_formatted


# def ration_formatting(ration_all, ration_percentages, DMIest):
#     ration = {}
#     for feed_id in range(len(available_feeds['feed_id'])):
#         print(feed_id)
#         print(available_feeds['feed_key'][feed_id])
#         if available_feeds['feed_key'][feed_id] in ration:
#             ingredient_percentage = ration[available_feeds['feed_key'][feed_id]]
#             ingredient_as_proportion = ingredient_percentage/100*DMIest
#             ration[available_feeds['feed_key'][feed_id]] = round(ingredient_as_proportion, 6)
#         else:
#             ration[available_feeds['feed_key'][feed_id]] = 0.0
#     ration['status'] = 'Optimal'
#     ration['objective'] = 0.0 # JCW THIS IS FAST FIX # NLP.objective(solution.x)
#     return ration


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
            heifer_ration = ration_all['all_heifers']
            calf_ration = ration_all['calf']

            self.calf_ration = calf_ration
            self.heifer_ration = heifer_ration
            self.lactating_cow_ration = lactating_cow_ration
            self.dry_cow_ration = dry_cow_ration
            self.ration_all = ration_all



            self.variables_pool: Dict[str, Any] = {}
            self.warnings_pool: Dict[str, Any] = {}
            self.errors_pool: Dict[str, Any] = {}
            self.logs_pool: Dict[str, Any] = {}

udrv = user_defined_ration_values()

def ration_to_use(animal_type, lactating):
    ration_calf = udrv.calf_ration
    ration_all_heifers = udrv.heifer_ration
    ration_cow_lactating = udrv.lactating_cow_ration
    ration_cow_dry = udrv.lactating_cow_ration
    if animal_type == 'cow':
        if lactating:
            rationtouse = ration_cow_lactating
        else:
            rationtouse = ration_cow_dry
    elif animal_type == 'heifer':
        rationtouse = ration_all_heifers
    else: 
        rationtouse = ration_calf
    return rationtouse


def userbounds(animal_type = 'cow', lactating = True, DMIest = 0.0):
    # TODO use the util.py read_json_file method instead
    with open('input/userdefinedration/user_defined_ration_input_percentages.json', 'r') as f:
        rationall = json.load(f)
    ration_calf = rationall['calf']
    ration_all_heifers = rationall['all_heifers']
    ration_cow_lactating = rationall['cow_lactating']
    ration_cow_dry = rationall['cow_dry']
    if animal_type == 'cow':
        if lactating:
            rationtouse = ration_cow_lactating
        else:
            rationtouse = ration_cow_dry
    elif animal_type == 'heifer':
        rationtouse = ration_all_heifers
        chancho_debug = False
        if chancho_debug:
            print('heiferfound')
            print(ration_all_heifers)
    else: 
        rationtouse = ration_calf
    
    values2= []
    # IT"S FAILING HERE
    for key, value in rationall.items():
        for i in value.keys():
            values2.append(int(i))
    uniqueset=set(values2) # TODO fix tortured logic 
    uniqueset2 = [i for i in uniqueset]
    uniqueset2.sort()
    uniqueset2 = [str(i) for i in uniqueset2]
    
    tribounds = []
    wiggleroom = 0.15
    print('foundrations3')
    if DMIest == 0.0: DMIest = 1.0
    for key in uniqueset2:
        if key in rationtouse.keys():
            target = rationtouse[key]/100*(DMIest) # change from percent to decimal percent
            # target = rationtouse[key]
            tribounds.append((target-target*wiggleroom,target+target*wiggleroom))
            tribounds.append((target-target*wiggleroom,target+target*wiggleroom))
            tribounds.append((target-target*wiggleroom,target+target*wiggleroom))
        else:
            tribounds.append((0,0.0001))
            tribounds.append((0,0.0001))
            tribounds.append((0,0.0001))
    return tribounds