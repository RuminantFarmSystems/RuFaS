"""
RUFAS: Ruminant Farm Systems Model
File name: ration_driver.py

Description: Main file in the ration formulation process that connects all
    other files such as requirements files and non-linear program files and
    also connects with the Feed and Animal modules to bring in relevant values.

Author(s): Chris VanKerkhove, cjv47@cornell.edu
           Joseph Waddell, jw2574@cornell.edu
"""
import collections
from typing import Set, Dict, List

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.ration import animal_requirements
from RUFAS.routines.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.routines.animal.ration.user_defined_ration import \
    UserDefinedRationManager as UserDefinedRationManager
from RUFAS.routines.animal.ration.ration_config import RationConfig
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants

import scipy

udrm = UserDefinedRationManager()
ration_optimizer = RationOptimizer()
om = OutputManager()


class RationManager:
    """
    Ration formulation is performed via collection and comparison of feed supply and animal requirements

    Calls to AnimalRequirements and AvailableFeeds (in this file until Feed refactor)
    collect the necessary information, which is then sent to RationOptimization
    Finally, RationReporter is a suite of methods used to send information to output manager
    (and other submodules of RuFaS)
    """

    @classmethod
    def formulate_ration(cls, pen, available_feeds, animal_grouping_scenario):
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
        if udrm.udr_or_not:
            ration, ration_vals = cls.get_user_defined_ration(req, pen, available_feeds, animal_grouping_scenario)
            return ration, ration_vals

        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds,
                                                                                     pen.animal_combination)
        # Reduction of milk production estimate process to achieve feasible solution
        num_reattempts = 0

        # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
        if pen.animal_combination.name in ['LAC_COW']:
            while not solution.success:
                num_reattempts += 1
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons,
                                                                              ration_config)
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                reduction = AnimalModuleConstants.MILK_REDUCTION_KG
                cls.reduce_milk_production(pen, reduction)

                req.set_requirements(pen, animal_grouping_scenario, True)
                solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds,
                                                                                             pen.animal_combination)
                info_map = {"class": "RationManager",
                            "function": cls.formulate_ration.__name__,
                            }
                sim_day = pen.animals_in_pen[0].body_weight_history[-1].simulation_day
                fail_summary = {'simulation day': sim_day,
                                'reattempt number': num_reattempts,
                                'constraints_failed_dict': constraints_failed_list,
                                'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                                'pen requirements': pen.avg_nutrient_rqmts}
                om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)

        if solution is not None:
            ration = cls.make_ration_from_solution(available_feeds, solution)
            return ration, ration_vals
        # safeguard if scipy SLSQP bounds error still occurs after many iterations
        # using previous cycles ration for this pen
        else:
            return pen.ration, ration_vals

    def calc_milk_average(pen) -> float:
        """
        Calculates average milk produced in a pen.

        Parameters
        ----------
        pen: an object of class Pen

        Returns
        -------
        float
            Average running milk
        """
        total_milk_in_pen = sum(animal.estimated_daily_milk_produced for animal in pen.animals_in_pen)
        starting_milk_average = total_milk_in_pen / len(pen.animals_in_pen)
        return starting_milk_average

    @classmethod
    def reduce_milk_production(cls, pen, reduction: float) -> None:
        """
        Reduces milk production for all animals in a pen.
        Only does so if post-reduction production would be above 1.0.
        Returns running total milk produced in the pen.

        Parameters
        ----------
        pen: an object of class Pen

        reduction: float
            The kg amount of lactation should be reduced in each loop, per animal

        """
        running_total_milk = 0.0
        for animal in pen.animals_in_pen:
            if animal.estimated_daily_milk_produced - reduction > 1.0:
                animal.estimated_daily_milk_produced -= reduction
                animal.milk_production_reduction -= reduction
            running_total_milk += animal.estimated_daily_milk_produced

    @classmethod
    def make_ration_from_solution(cls, available_feeds: Dict, solution: scipy.optimize.OptimizeResult) -> dict:
        """
        Generates ration dictionary from scipy result

        Parameters
        ----------
        available_feeds : an object of class AvailableFeeds
            a DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py

        solution : OptimizeResult object from scipy package

        Returns
        -------
        Dict

        """
        ration = {}
        for feed_id in range(len(available_feeds['feed_id'])):
            i = feed_id * 3
            num = solution.x[i]
            num += solution.x[i + 1]
            num += solution.x[i + 2]
            ration[available_feeds['feed_key'][feed_id]] = round(num, 6)
        ration['status'] = 'Optimal'
        ration_config = RationConfig()
        ration_config.price_list = RationOptimizer.triple_values_in_list(available_feeds['price'])
        ration['objective'] = ration_optimizer.objective(solution.x, ration_config)
        return ration

    @classmethod
    def make_solution_from_fixed_ration(cls, ration: Dict) -> List:
        """
        makes solution object from returned fixed ration for use in get_ration_vals function in ration_optimizer.py
        Simply puts the value in triplicate, and multiplies by the MEact defined in  ration_config

        Parameters
        ----------
        ration: Dict

        Returns
        -------
        List

        """
        excluded_keys = {'status', 'objective'}
        solution_from_ration = []
        for key in ration.keys():
            if key not in excluded_keys:
                solution_from_ration.append(ration[key]/3)
                solution_from_ration.append(ration[key]/3)
                solution_from_ration.append(ration[key]/3)
        return solution_from_ration

    @classmethod
    def get_user_defined_ration(cls, req: animal_requirements, pen, available_feeds, animal_grouping_scenario) \
            -> tuple[Dict[str, float], Dict[str, float]]: # noqa
        """
        Function that links the ration_driver file with the calc_ration function in
        pen.py. Returns a dictionary of the rations by feed and status of the NLP
        optimization.

        There are multiple outcomes here.
        1: User has defined a lactation reduction percent of 0.0, and tolerance of 0.0, thus the fixed ration is used.
        2: Optimization is a success, and optimized solution (within the tolerance bounds) is used.
        3: Optimization fails
            3a: If lactation reduction is set to 0.0, no reattempt is made
            3b: Optimization reattempted until lactation reduction threshold is reached.
                (e.g. milk_reduction_maximum)

        Parameters
        ----------
        req : an object of class Requirements

        pen : an object of class Pen

        available_feeds : an object of class AvailableFeeds

        animal_grouping_scenario : AnimalCombination
            the valid animal combinations inside this pen, an instance of the AnimalCombination Enum

        Returns
        -------
        ration : Dict

        ration_vals : Dict

        """
        info_map = {"class": "RationManager",
                    "function": cls.get_user_defined_ration.__name__,
                    }
        ration_percents = UserDefinedRationManager.ration_to_use(pen.animal_combination, available_feeds)
        fixed_ration = False
        num_reattempts = 0
        constraints_failed_list = []

        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds,
                                                                                     pen.animal_combination)
        if pen.animal_combination.name in ['LAC_COW']:
            failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons,
                                                                          ration_config)
        else:
            failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.heifer_cons,
                                                                          ration_config)

        if failed_constraints is not None:
            for constr in failed_constraints:
                constraints_failed_list.append(constr["fun"].__name__)
            fail_summary = {'simulation day': pen.animals_in_pen[0].body_weight_history[-1].simulation_day,
                            'reattempt number': num_reattempts,
                            'constraints_failed_dict': constraints_failed_list,
                            'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                            'pen requirements': pen.avg_nutrient_rqmts}
            om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)

        if udrm.milk_reduction_maximum == 0.0 and udrm.tolerance == 0.0 and not solution.success:
            ration = UserDefinedRationManager.make_ration_from_user_values(ration_percents, available_feeds, req)
            ration_vals = ration_optimizer.get_ration_vals(cls.make_solution_from_fixed_ration(ration), ration_config)
            return ration, ration_vals

        if pen.animal_combination.name not in ['LAC_COW'] and not solution.success:
            fixed_ration = True

        if pen.animal_combination.name in ['LAC_COW'] and solution is not None:
            running_milk_reduction = 0.0
            while not solution.success:
                running_average_milk = cls.calc_milk_average(pen)
                reduction = AnimalModuleConstants.MILK_REDUCTION_KG
                if udrm.milk_reduction_maximum == 0.0 or \
                    running_milk_reduction + reduction > udrm.milk_reduction_maximum or\
                        running_average_milk - reduction < 1.0:
                    fixed_ration = True
                    solution.success = True
                    break

                num_reattempts += 1
                running_milk_reduction += reduction
                cls.reduce_milk_production(pen, reduction)
                running_average_milk = cls.calc_milk_average(pen)

                req.set_requirements(pen, animal_grouping_scenario, True)
                solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds,
                                                                                             pen.animal_combination)
                failed_constraints = []
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons,
                                                                              ration_config)
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                    fail_summary = {'simulation day': pen.animals_in_pen[0].body_weight_history[-1].simulation_day,
                                    'reattempt number': num_reattempts,
                                    'constraints_failed_dict': constraints_failed_list,
                                    'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                                    'pen requirements': pen.avg_nutrient_rqmts}
                    om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)

        if fixed_ration:
            ration = UserDefinedRationManager.make_ration_from_user_values(ration_percents, available_feeds, req)
            ration_vals = ration_optimizer.get_ration_vals(cls.make_solution_from_fixed_ration(ration), ration_config)
        else:
            ration = cls.make_ration_from_solution(available_feeds, solution)
            ration_vals = ration_optimizer.get_ration_vals(solution.x, ration_config)
        return ration, ration_vals


class RationReporter:
    """
    Calculates and collects information about a formulated ration.
    """
    def __init__(cls):
        cls.nutrient_amount = []
        cls.nutrient_conc = []

    @classmethod
    def report_ration(cls, ration, available_feeds): # noqa

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
