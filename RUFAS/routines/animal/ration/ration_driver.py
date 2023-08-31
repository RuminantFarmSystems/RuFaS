"""
RUFAS: Ruminant Farm Systems Model
File name: ration_driver.py

Description: Main file in the ration formulation process that connects all
    other files such as requirements files and non-linear program files and
    also connects with the Feed and Animal modules to bring in relevant values.

Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
import collections
import math
from typing import Callable
from typing import List
import numpy as np
import numpy.typing as npt
from typing import Set
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.ration import animal_requirements
from RUFAS.routines.animal.ration import ration_NLP as NLP

om = OutputManager()

class RationManager:
    pass

def optimization(requirements, available_feeds, animal_combination):
    """
    Function that sets up the nutrients and requirements lists into structured
    inputs for the non-linear program and calls the optimization function.

    Args:
        requirements: object of class Requirements
        available_feeds: object of class AvailableFeeds
        animal_combination: one of the animal combinations specified in the AnimalCombination enum
    """
    price = NLP.list_reconfig(available_feeds['price'])
    TDN = NLP.list_reconfig(available_feeds['TDN'])
    DE = NLP.list_reconfig(available_feeds['DE'])
    EE = NLP.list_reconfig(available_feeds['EE'])
    is_fat = NLP.list_reconfig(available_feeds['is_fat'])
    calcium = NLP.list_reconfig(available_feeds['calcium'])
    phosphorus = NLP.list_reconfig(available_feeds['phosphorus'])
    NDF = NLP.list_reconfig(available_feeds['NDF'])
    feed_type = NLP.list_reconfig(available_feeds['type'])
    is_wetforage = NLP.list_reconfig(available_feeds['is_wetforage'])
    Kd = NLP.list_reconfig(available_feeds['Kd'])
    N_A = NLP.list_reconfig(available_feeds['N_A'])
    N_B = NLP.list_reconfig(available_feeds['N_B'])
    CP = NLP.list_reconfig(available_feeds['CP'])
    dRUP = NLP.list_reconfig(available_feeds['dRUP'])
    # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
    if str(animal_combination) in ['AnimalCombination.LAC_COW']:
        limit = NLP.list_reconfig(available_feeds['lactating_cow_limit'])
        cow_type = True
    else:
        limit = NLP.list_reconfig(available_feeds['dry_cow_limit'])
        cow_type = False
    NLP.set_globals(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                    requirements.NEl, requirements.NEg, requirements.MP_req,
                    requirements.Ca_req, requirements.P_req,
                    TDN, DE, EE, is_fat, requirements.avg_BW, calcium, phosphorus, NDF,
                    feed_type, is_wetforage, Kd, N_A, N_B, CP, dRUP, limit, cow_type,
                    DMIest_=requirements.DMIest)
    # try block for catching scipy SLSQP error
    i = 0
    count = 0
    while i < 1:
        try:
            solution = NLP.optimize(animal_combination)
        except:
            i -= 1
        finally:
            i += 1
            count += 1
        # this case should not be called, but is in place to not crash the
        # simulation if bounds error is not resolved
        if count > 30:
            solution = None
            break

    # retrieving MEact from diet
    if solution is None:
        ration_vals = None
    else:
        ration_vals = NLP.get_ration_vals(solution.x)
    return solution, ration_vals


def is_constraint_violated(solution_x: npt.NDArray, constraint: dict[str, Callable]) -> bool:
        """
        Helper function to check a solution dictionary to see if a given constraint 
            in a list of constraints was met.
        
        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x array from minimize function used in ration_NLP.py
        constraint: dict[str, Any]
            constraint function as defined in ration_NLP.py

        """
        result = constraint['fun'](solution_x)
        if constraint['type'] == 'ineq' and result < 0:
            return True
        elif constraint['type'] == 'eq' and not np.isclose(result, 0):
            return True
        else:
            return False


def find_failed_constraints(solution_x: npt.NDArray, constraints: List[dict[str,Callable]]) -> List[dict[str,Callable]]:
        """
        Returns list of constraints that were not met during optmization step.
        
        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x is from minimize function used in ration_NLP.py, 
                solution obj itself is returned as  <dict class 'scipy.optimize._optimize.OptimizeResult'>

        constraints: List[dict[str, Callable]]
            list of constraint functions as defined in ration_NLP.py

        Returns
        -------
        List[dict[str,Callable]]
            the same type of list as the constraints themselves
                just filtered such that the ones that failed are returned
        """
        return list(filter(lambda c: is_constraint_violated(solution_x, c), constraints))


def ration_formulation(pen, available_feeds, animal_grouping_scenario):
    """
    Function that links the ration_driver file with the calc_ration function in
    animal_manager.py. Returns a dictionary of the rations by feed and status of the NLP
    optimization.

    Args:
        pen: an object of class Pen
        available_feeds: an object of class AvailableFeeds
        animal_grouping_scenario: A grouping scenario of animals used in the current simulation, specified in
            AnimalGroupingScenario enum and AnimalManager class

    """

    # creating instance of class requirements
    req = animal_requirements.AnimalRequirements()
    # Use grouping scenario to find the type of each animal in pen
    req.set_requirements(pen, animal_grouping_scenario, False)

    solution, ration_vals = optimization(req, available_feeds, pen.animal_combination)
    # Reduction of milk production estimate process to achieve feasible solution
    num_reattempts = 0
    failed_list = []

    # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
    if pen.animal_combination.name in ['LAC_COW']:
        while not solution.success:
            num_reattempts += 1
            failed_constraints = find_failed_constraints(solution.x, NLP.cow_cons)
            if failed_constraints:
                for constr in failed_constraints:
                    failed_list.append(constr["fun"].__name__)
            # These values for reduction are not from pseudocode, but the values below
            # are based on fastest case runtime testing
            # TODO: continue testing for more efficient reductions: see Issues #569, 577, 589
            # NEl_con = NLP.NEl_constraint(solution.x)
            # if NEl_con < -0.5:
            #     reduction = 3 * (-NEl_con)
            # else:
            #     reduction = 1.5
            reduction = 0.25
            for animal in pen.animals_in_pen:
                animal.estimated_daily_milk_produced -= reduction
                animal.milk_production_reduction -= reduction
            # recalculating requirements after reduction
            req.set_requirements(pen, animal_grouping_scenario, True)
            solution, ration_vals = optimization(req, available_feeds, pen.animal_combination)
            info_map = {"class": "no_caller_class",
                "function": pen.__init__.__name__,
                }

    if solution is not None:
        if failed_list != []:
            fail_summary = [num_reattempts, failed_list]
            om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)
        ration = {}
        for feed_id in range(len(available_feeds['feed_id'])):
            i = feed_id * 3
            num = solution.x[i]
            num += solution.x[i + 1]
            num += solution.x[i + 2]
            ration[available_feeds['feed_key'][feed_id]] = round(num, 6)
        ration['status'] = 'Optimal'
        ration['objective'] = NLP.objective(solution.x)
        return ration, ration_vals
    # safeguard if scipy SLSQP bounds error still occurs after many iterations
    # using previous cycles ration for this pen
    else:
        return pen.ration, ration_vals

class RationReport:
    pass

def ration_report(ration, available_feeds):
    """
    Calculates information in the ration about nutrient information including
    nutrient amounts and concentrations. Returns a dictionary of nutrient amounts
    and nutrient calculations respectively. Psuedocode for these calculations
    are located in Ration Class Variables in Animal Module Pseduocode

    Args:
        ration: a dictionary of the calculated ration
        available_feeds: available feeds dictionary from the Feed class object
    """
    nutrient_amount = {'dm': 0, 'as_fed': 0, 'CP': 0, 'ADF': 0, 'NDF': 0,
                       'lignin': 0, 'ash': 0, 'phosphorus': 0, 'potassium': 0,
                       'N': 0, "EE": 0, "starch": 0}
    nutrient_conc = {}
    ration = ration.copy()
    for non_numeric_key in ['status', 'objective']:
        if non_numeric_key in ration:
            del ration[non_numeric_key]
    nutrients = ['DM', 'CP', 'ADF', 'NDF', 'lignin', 'ash', 'phosphorus',
                 'potassium', 'N', 'EE', 'starch']

    # feed nutrient amounts
    for key, val in ration.items():
        nutrient_amount['dm'] += val
        for nutr in nutrients:
            # all values on a 100% dry matter basis
            if nutr == 'DM':
                nutrient_amount['as_fed'] += val * (available_feeds[key][nutr] / 100)
            elif nutr == 'N':
                # [A.2.A.2]
                if key[:3] in ['121', '122', '155', '157']:
                    denom = 6.38
                # [A.2.A.1]
                else:
                    denom = 6.25
                nutrient_amount[nutr] += (available_feeds[key]['CP'] / (denom * 100)) * val
            else:
                nutrient_amount[nutr] += val * (available_feeds[key][nutr] / 100)

    # feed nutrient concentrations
    dm_amount = nutrient_amount['dm']
    if dm_amount == 0:
        dm_amount = 1
    for nutr in nutrients:
        if nutr == 'DM':
            nutrient_conc['dm'] = (nutrient_amount['as_fed'] / dm_amount) * 100
        else:
            # all values on a 100% dry matter basis
            nutrient_conc[nutr] = (nutrient_amount[nutr] / dm_amount) * 100
    return nutrient_amount, nutrient_conc


class AvailableFeeds:
    """
    Stores the information of the feeds available at the end of a ration interval
    to be used in the non-linear program ration formulation.
    """

    def __init__(self):
        # id of the feed in the feed database
        self.feed_id = []
        # list to keep track of dictionary keys
        self.feed_key = []
        # price of the feed ($/KG)
        self.price = []
        # Total digestible nutrient (% of DM)
        self.TDN = []
        # Digestible energy (Mcal/kg)
        self.DE = []
        # Ether extract, crude fat (% of DM)
        self.EE = []
        # If the feed is fat supplement or not (yes = 1; no = 0)
        self.is_fat = []
        # Calcium content (% of DM)
        self.calcium = []
        # Phosphorus content (% of DM)
        self.phosphorus = []
        # Neutral detergent fiber (% of DM)
        self.NDF = []
        # Feed type (Forage, Concentrate, or Mineral)
        self.type = []
        # If the feed is wet forage or not (yes = 1; no = 0)
        self.is_wetforage = []
        # Rumen protein degradation rate (%/h)
        self.Kd = []
        # Fraction A of protein, degraded immediately in rumen (% of CP)
        self.N_A = []
        # Fraction B of protein, potentially degradable protein, require time to
        # generally degrade in rumen (% of CP)
        self.N_B = []
        # Crude protein (% of DM)
        self.CP = []
        # RUP degradability (% of RUP)
        self.dRUP = []
        # lactating cows feed limits
        self.lactating_cow_limit = []
        # dry cow feed limits
        self.dry_cow_limit = []
        # heiferIII limits
        self.heiferIII_limit = []
        # heiferII limit
        self.heiferII_limit = []
        # heiferI limit
        self.heiferI_limit = []
        # calf limit
        self.calf_limit = []
        # key = feed_id, val = index of that feed_id in self.feed_id list
        self._feed_id_to_list_idx_dict = {}
        # key = feed_id, val = index of that feed_id in self.feed_id list
        self._feed_id_to_list_idx_dict = {}

    def feed_nutrients(self, feed):
        """
        Class function that manipulates the available feeds nutrient information
        into list (valid for input in the non-linear program) and populates the
        corresponding class variables.

        Args:
            feed: an instance of the Feed class object
        """
        # available feeds dictionary from the feed module
        available_feeds = feed.available_feeds
        # dictionary of feed costs
        feed_costs = feed.feed_costs

        for key, feed in available_feeds.items():
            self.feed_key.append(key)
            self.feed_id.append(feed['feed_id'])
            self.price.append(feed_costs[str(key)])
            self.TDN.append(feed['TDN'])
            self.DE.append(feed['DE'])
            self.EE.append(feed['EE'])
            self.is_fat.append(feed['is_fat'])
            self.calcium.append(feed['calcium'])
            self.phosphorus.append(feed['phosphorus'])
            self.NDF.append(feed['NDF'])
            self.type.append(feed['type'])
            self.is_wetforage.append(feed['is_wetforage'])
            self.Kd.append(feed['Kd'])
            self.N_A.append(feed['N_A'])
            self.N_B.append(feed['N_B'])
            self.CP.append(feed['CP'])
            self.dRUP.append(feed['dRUP'])
            if isinstance(feed['limit'], dict):
                self.lactating_cow_limit.append(feed['limit']['lactating_cows'])
                self.dry_cow_limit.append(feed['limit']['dry_cows'])

            else:
                self.lactating_cow_limit.append(feed['limit'])
                self.dry_cow_limit.append(feed['limit'])

    def get_feed_data_from_feed_ids(self, feed_ids: Set[int]):
        """
        Returns a subset of data from all the available feeds based on the
        given set of feed ids.

        Args
        ----
        feed_ids: a set of feed ids

        Returns
        -------
        A dictionary that contains a subset of data from all the available feeds based on the
        given set of feed ids
        """
        # An explanation of code seen below can be found in Basecamp with the following path:
        # RuFaS > Docs & Files > Animal Module > Ration Driver Logic

        if not self._feed_id_to_list_idx_dict:
            self._feed_id_to_list_idx_dict = {fid: i for i, fid in enumerate(self.feed_id)}

        excluded_keys = ['_feed_id_to_list_idx_dict']
        result = collections.defaultdict(list)
        for key, vals in self.__dict__.items():
            if key in excluded_keys:
                continue
            if not vals:
                result[key] = []
                continue
            for feed_id in sorted(list(feed_ids)):
                # Get the list index of the feed_id in self.feed_id list.
                idx = self._feed_id_to_list_idx_dict[int(feed_id)]
                result[key].append(vals[idx])
        return result
