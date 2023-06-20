"""
RUFAS: Ruminant Farm Systems Model
File name: user_defined_ration.py
Description: Tools for accessing and providing user-defined ration  variables
    Main class used to read JSON as singleton, return ration percentages where needed
Author: Joseph C. Waddell, jw2574@cornell.edu
"""

from typing import Any, Dict
import json

class UserDefinedRationManager(object):
    """
    Reads in the user_defined_ration JSON and collects variables as Dicts.
    Methods return rations and change keys in the dict as needed.
    """

    # check the setup JSON
    # if user-defined-ration is NOT selected, initialize as NULL
    
    __instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UserDefinedRationManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if UserDefinedRationManager.__instance is None:
            UserDefinedRationManager.__instance = self
            
            self.udr_or_not = None

            self.lactating_cow_ration = []
            self.heifer_ration = []
            self.calf_ration = []
            self.close_up_ration = []

            self.tolerance = []
            self.milk_reduction_percent = []

    def feed_quality_fix(ration_percents: Dict, available_feeds: Dict) -> Dict:
        """
        This checks the keys in the ration_percents dictionary and checks
         against the AvailableFeeds dictionary. If a given key is not found in the 
         latter, 2 is added to the key. This is because there is a 'quality' change
         in the Feed module that changes keys that vary in quality. Said functionality may be deprecated, hence this quick solution. 
        
        Parameters
        ----------
        ration_percents: Dict
            dictionary of feed ids and their associated percentage of DMI 
        available_feeds: available feeds dictionary from the Feed class object

        Returns
        -------
        ration_percents: Dict
            dictionary of feed ids and their associated percentage of DMI 

        """
        key_list = list(ration_percents.keys())
        for key in key_list:
            if int(key) not in available_feeds['feed_id']:
                new_key = str(int(key)+2)
                ration_percents[new_key] = ration_percents[key]
                del ration_percents[key]
        return ration_percents
    

    def ration_to_use(pen_animal_combo, available_feeds: Dict) -> Dict:
        """
        Function outputs the correct dictionary from the UserDefinedRationManager class
        
        Parameters
        ----------
        pen_animal_combo : Pen.AnimalCombination
            AnimalCombination in the given pen
        available_feeds : Dict
            available feeds dictionary from the Feed class object

        Returns
        -------
        ration_percents : Dict
            dictionary of feed ids and their associated percentage of DMI 
        """
        udrv = UserDefinedRationManager()
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
        return UserDefinedRationManager.feed_quality_fix(ration_percents, available_feeds)


    def make_ration_from_user_values(ration_percents: Dict, available_feeds, req) -> Dict:
        """
        Generate ration dict from user ration percents input
        
        Parameters
        ----------
        ration_percents : Dict
            dictionary of feed ids and their associated percentage of DMI 
        
        available_feeds : Dict
            available feeds dictionary from the Feed class object
        
        req : an object of class Requirements        
        
        Returns
        -------
        Dict
            dictionary of formulated ration
        
        """
        ration = {}
        for feed_id in range(len(available_feeds['feed_id'])):
            if available_feeds['feed_key'][feed_id] in ration_percents:
                ingredient_percentage = ration_percents[available_feeds['feed_key'][feed_id]]
                ingredient_as_proportion = ingredient_percentage/100*req.DMIest
                ration[available_feeds['feed_key'][feed_id]] = round(ingredient_as_proportion, 6)
            else:
                ration[available_feeds['feed_key'][feed_id]] = 0.0
        ration['status'] = 'Optimal'
        ration['objective'] = 0.0 # setting as optimal
        return ration