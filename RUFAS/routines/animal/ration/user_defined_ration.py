"""
RUFAS: Ruminant Farm Systems Model
File name: user_defined_ration.py
Description: Tools for accessing and providing user-defined ration  variables
    Main class used to read JSON as singleton, return ration percentages where needed
Author: Joseph C. Waddell, jw2574@cornell.edu
"""

from typing import Dict


class UserDefinedRationManager(object):
    """
    Reads in the user_defined_ration JSON and collects variables as Dicts.
    Methods return rations and change keys in the dict as needed.
    """

    __instance = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(UserDefinedRationManager, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        if UserDefinedRationManager.__instance is None:
            UserDefinedRationManager.__instance = self

            self.udr_or_not = None

            self.calf_ration = []
            self.growing_ration = []
            self.close_up_ration = []
            self.lactating_cow_ration = []

            self.tolerance = []
            self.milk_reduction_maximum = []

    def ration_to_use(animal_combination, available_feeds: Dict) -> Dict:
        """
        Function outputs the dictionary for a given animal combination from the UserDefinedRationManager class

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
        udrm = UserDefinedRationManager()
        animal_type = animal_combination.name
        if animal_type == "LAC_COW":
            ration_percents = udrm.lactating_cow_ration
        # elif pen.classes
        elif animal_type == "GROWING":
            ration_percents = udrm.growing_ration
        elif animal_type == "CLOSE_UP":
            ration_percents = udrm.close_up_ration
        else:
            ration_percents = udrm.calf_ration
        return ration_percents

    def make_ration_from_user_values(ration_percents: Dict, available_feeds, req) -> Dict:
        """
        Generate ration dict from user ration percents input,
        scaled to their estimated dry matter intake (DMI)

        Parameters
        ----------
        ration_percents : Dict
            dictionary of feed ids and their desired percentages of estimated DMI

        available_feeds : Dict
            available feeds dictionary from the Feed class object

        req : an object of class Requirements

        Returns
        -------
        Dict
            dictionary of formulated ration

        """
        ration = {}
        for feed_id in range(len(available_feeds["feed_id"])):
            if available_feeds["feed_key"][feed_id] in ration_percents:
                ingredient_percentage = ration_percents[available_feeds["feed_key"][feed_id]]
                ingredient_as_proportion = ingredient_percentage / 100 * req.DMIest_requirement
                ration[available_feeds["feed_key"][feed_id]] = round(ingredient_as_proportion, 6)
            else:
                ration[available_feeds["feed_key"][feed_id]] = 0.0
        ration["status"] = "Optimal"
        ration["objective"] = 0.0
        return ration
