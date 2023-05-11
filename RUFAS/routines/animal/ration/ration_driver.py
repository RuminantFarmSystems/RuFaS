"""
RUFAS: Ruminant Farm Systems Model
File name: ration_driver.py

Description: Main file in the ration formulation process that connects all
    other files such as requirements files and non-linear program files and
    also connects with the Feed and Animal modules to bring in relevant values.

Author(s): Chris VanKerkhove, cjv47@cornell.edu
"""
from RUFAS.routines.animal.ration import animal_requirements
from RUFAS.routines.animal.ration import ration_NLP as NLP
from typing import Dict, List, Set
import collections
import math
import statistics as stat
import numpy as np
from RUFAS.output_manager import OutputManager


om = OutputManager()


def optimization(requirements, available_feeds, animal_type, cow_type):
    """
    Function that sets up the nutrients and requirements lists into structured
    inputs for the non-linear program and calls the optimization function.

    Args:
        requirements: object of class Requirements
        available_feeds: object of class AvailableFeeds
        animal_type: string representation of the animal
        cow_type: Boolean which is True if cow is lactating, False otherwise
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
    if cow_type:
        limit = NLP.list_reconfig(available_feeds['lactating_cow_limit'])
    else:
        limit = NLP.list_reconfig(available_feeds['dry_cow_limit'])
    NLP.set_globals(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                    requirements.NEl, requirements.NEg, requirements.MP_req,
                    requirements.Ca_req, requirements.P_req,
                    TDN, DE, EE, is_fat, requirements.avg_BW, calcium, phosphorus, NDF,
                    feed_type, is_wetforage, Kd, N_A, N_B, CP, dRUP, limit, cow_type,
                    animal_type_=animal_type,
                    DMIest_=requirements.DMIest)
    # try block for catching scipy SLSQP error
    i = 0
    count = 0
    while i < 1:
        try:
            solution = NLP.optimize()
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
    if solution == None:
        ration_vals = None
    else:
        ration_vals = NLP.get_ration_vals(solution.x)
    return solution, ration_vals


def is_constraint_violated(solution, constraint) -> bool:
        result = constraint['fun'](solution)
        if constraint['type'] == 'ineq' and result < 0:
            return True
        elif constraint['type'] == 'eq' and not np.isclose(result, 0):
            return True
        else:
            return False


def find_failed_constraints(solution, constraints):
        return list(filter(lambda c: is_constraint_violated(solution, c), constraints))


def ration_formulation(pen, available_feeds, animal_type, cow_type):
    """
    Function that links the ration_driver file with the calc_ration function in
    pen.py. Returns a dictionary of the rations by feed and status of the NLP
    optimization.

    Args:
        pen: an object of class Pen
        feed: an object of class Feed
        available_feeds: an object of class AvailableFeeds
        animal_type: string representation of the type of animal (cow, heifer)
        cow_type: Boolean which is True if cow is lactating, False otherwise
    """

    # creating instance of class requirements
    req = Requirements()
    req.set_requirements(pen, animal_type, False)

    solution, ration_vals = optimization(req, available_feeds, animal_type, cow_type)
    # Reduction of milk production estimate process to achieve feasible solution
    num_reattempts = 0
    failed_list = []
    if animal_type == 'cow':
        while not solution.success:
            num_reattempts += 1
            # add step to check constraints
            failed_constraints = find_failed_constraints(solution.x, NLP.cow_cons)
            if failed_constraints:
                for constr in failed_constraints:
                    failed_list.append(constr["fun"].__name__)
            # This values for reduction are not from pseudocode, but the vales below
            # are based on fastest case runtime testing
            # TODO: continue testing for more efficient reductions
            NEl_con = NLP.NEl_constraint(solution.x)
            if NEl_con < -0.5:
                reduction = 3 * (-NEl_con)
            else:
                reduction = 1.5

            for animal in pen.animals_in_pen:
                animal.estimated_daily_milk_produced -= reduction
                animal.milk_production_reduction -= reduction
            # recalculating requirements after reduction
            req.set_requirements(pen, animal_type, True)
            solution, ration_vals = optimization(req, available_feeds, animal_type, cow_type)
    info_map = {"class": pen.__class__.__name__,
                "function": pen.__init__.__name__,
                }
    if solution != None:
        if failed_list != []:
            fail_summary = [num_reattempts, failed_list]
            om.add_variable(f'failed_constraints for pen {pen.id} ', fail_summary, info_map)
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
    ration.pop('status')
    ration.pop('objective')
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
    for nutr in nutrients:
        if nutr == 'DM':
            nutrient_conc['dm'] = (nutrient_amount['as_fed'] / dm_amount) * 100
        else:
            # all values on a 100% dry matter basis
            nutrient_conc[nutr] = (nutrient_amount[nutr] / dm_amount) * 100
    return nutrient_amount, nutrient_conc


class Requirements:
    """
    Stores the information for the calculated requirements of animals to
    be used in the the ration formulation.
    """

    def __init__(self):
        """
        Initializes a requirements object with default values of specific
        requirements at 0.
        """

        # Net energy for maintenance requirement (Mcal)
        self.NEmaint = 0
        # Net energy for activity requirement (Mcal)
        self.NEa = 0
        # Net energy for growth requirement (Mcal)
        self.NEg = 0
        # Net energy requirement for pregnancy (Mcal)
        self.NEpreg = 0
        # Net energy requirement for lactation (Mcal)
        self.NEl = 0
        # Metabolizable protein requirement for growth (g)
        self.MP_req = 0
        # Calcium requirement (g)
        self.Ca_req = 0
        # Phosphorus requirement (g)
        self.P_req = 0
        # dry matter intake estimation (kg)
        self.DMIest = 0
        # average body weigth in pen
        self.avg_BW = 0
        # TODO: add documentation for avg_milk and avg_CP_milk
        self.avg_milk = 0
        self.avg_CP_milk = 0

    def set_requirements(self, pen, animal_type, recalc):
        """
        Calculates the average requirements utilizing cow_requirements.py and an
        input pen to generate the average requirements across a pen. It then
        populates the corresponding class variables.

        Args:
            pen: an instance of an object of class Pen
            animal_type: string representation of the animal
            recalc: boolean to see if requirements need to be recalculated since grouping
        """
        NEmaint = []
        NEa = []
        NEg = []
        NEpreg = []
        NEl = []
        MP_req = []
        Ca_req = []
        P_req = []
        DMIest = []
        BW = []
        milk = [0]
        milk_production_reduction = [0]
        CP_milk = [0]

        if recalc:
            # iterating through each animal in the pen and calculating requirements
            # temp parameter for heifer is hardcoded because heifer req should
            # never have to be recalculated
            for animal in pen.animals_in_pen:
                a_type = type(animal).__name__
                if a_type == 'HeiferI':
                    req = animal_requirements.calc_rqmts(body_weight = animal.body_weight,
                                                         mature_body_weight = animal.mature_body_weight, day_of_pregnancy = None, animal_type='heifer',
                                                         body_condition_score_5=3, previous_temperature=15,
                                                         average_daily_gain_heifer=animal.daily_growth
                                                         )
                elif a_type == 'HeiferII' or a_type == 'HeiferIII':
                    req = animal_requirements.calc_rqmts(body_weight = animal.body_weight,
                                                         mature_body_weight = animal.mature_body_weight, day_of_pregnancy = animal.days_in_preg,
                                                         animal_type='heifer', body_condition_score_5=3, previous_temperature=15,
                                                         average_daily_gain_heifer=animal.daily_growth)
                else:
                    req = animal_requirements.calc_rqmts(body_weight = animal.body_weight,
                                                         mature_body_weight = animal.mature_body_weight, day_of_pregnancy = animal.days_in_preg,
                                                         animal_type = 'cow', parity = animal.calves, calving_interval = animal.CI,
                                                         milk_true_protein= animal.mPrt, milk_fat = animal.fat_percent, milk_lactose = animal.lactose_milk,
                                                         milk_production = animal.estimated_daily_milk_produced,
                                                         days_in_milk = animal.days_in_milk, lactating = animal.milking
                                                         )

                animal.NEmaint = req['NEmaint']
                animal.NEg = req['NEg']
                animal.NEpreg = req['NEpreg']
                animal.NEl = req['NEl']
                animal.MP_req = req['MP_req']
                animal.Ca_req = req['Ca_req']
                animal.P_req = req['P_req']
                animal.DMIest = req['DMIest']
                # these animal class variables are only used for grouping purposes
                if animal_type == 'cow':
                    animal.DNED_req = (req['NEmaint'] + req['NEl']) / animal.DMIest
                    animal.DMDP_req = (req['MP_req']) / animal.DMIest

                    # calculating the activity requirement for energy
                    animal.calc_daily_walking_dist(pen.vertical_dist_to_parlor,
                                                   pen.horizontal_dist_to_parlor)
                    NEa_val = animal_requirements.energy_activity_rqmts(animal.body_weight,
                                                                        pen.housing_type,
                                                                        (math.sqrt(animal.DVD ** 2 + animal.DHD ** 2)))
                    milk.append(animal.estimated_daily_milk_produced)
                    milk_production_reduction.append(animal.milk_production_reduction)
                    CP_milk.append(animal.CP_milk)
                else:
                    NEa_val = 0

                NEmaint.append(req['NEmaint'])
                NEa.append(NEa_val)
                NEg.append(req['NEg'])
                NEpreg.append(req['NEpreg'])
                NEl.append(req['NEl'])
                MP_req.append(req['MP_req'])
                Ca_req.append(req['Ca_req'])
                P_req.append(req['P_req'])
                DMIest.append(req['DMIest'])
                BW.append(animal.body_weight)
        else:
            # iterating through each animal in the pen and setting requirements
            for animal in pen.animals_in_pen:
                if animal_type == 'cow':
                    # calculating the activity requirement for energy
                    animal.calc_daily_walking_dist(pen.vertical_dist_to_parlor,
                                                   pen.horizontal_dist_to_parlor)
                    NEa_val = animal_requirements.energy_activity_rqmts(animal.body_weight,
                                                                        pen.housing_type,
                                                                        (math.sqrt(animal.DVD ** 2 + animal.DHD ** 2)))
                    milk.append(animal.estimated_daily_milk_produced)
                    milk_production_reduction.append(animal.milk_production_reduction)
                    CP_milk.append(animal.CP_milk)
                else:
                    NEa_val = 0

                NEmaint.append(animal.NEmaint)
                NEa.append(NEa_val)
                NEg.append(animal.NEg)
                NEpreg.append(animal.NEpreg)
                NEl.append(animal.NEl)
                MP_req.append(animal.MP_req)
                Ca_req.append(animal.Ca_req)
                P_req.append(animal.P_req)
                DMIest.append(animal.DMIest)
                BW.append(animal.body_weight)
                # milk.append(milk)
                # CP_milk.append(CP_milk)
        usethemean = True
        if usethemean == True:
            # populating the class variables as an average across cows for each requirement
            self.NEmaint = stat.mean(NEmaint)
            self.NEa = stat.mean(NEa)
            self.NEg = stat.mean(NEg)
            self.NEpreg = stat.mean(NEpreg)
            self.NEl = stat.mean(NEl)
            self.MP_req = stat.mean(MP_req)
            self.Ca_req = stat.mean(Ca_req)
            self.P_req = stat.mean(P_req)
            self.DMIest = stat.mean(DMIest)
            self.avg_BW = stat.mean(BW)
            self.avg_milk = stat.mean(milk)
            self.avg_CP_milk = stat.mean(CP_milk)
            self.avg_milk_production_reduction = stat.mean(milk_production_reduction)
        else:
            requirement_percentile = 80
            self.NEmaint = np.percentile(NEmaint, requirement_percentile)
            self.NEa = np.percentile(NEa, requirement_percentile)
            self.NEg = np.percentile(NEg, requirement_percentile)
            self.NEpreg = np.percentile(NEpreg, requirement_percentile)
            self.NEl = np.percentile(NEl, requirement_percentile)
            self.MP_req = np.percentile(MP_req, requirement_percentile)
            self.Ca_req = np.percentile(Ca_req, requirement_percentile)
            self.P_req = np.percentile(P_req, requirement_percentile)
            self.DMIest = np.percentile(DMIest, requirement_percentile)
            self.avg_BW = np.percentile(BW, requirement_percentile)
            self.avg_milk = np.percentile(milk, requirement_percentile)
            self.avg_CP_milk = np.percentile(CP_milk, requirement_percentile)
            self.avg_milk_production_reduction = np.percentile(milk_production_reduction, requirement_percentile)
            #print('worked')

        info_map = {"class": self.__class__.__name__,
                    "function": self.__init__.__name__,
                    }
        # setting average nutrient requirements pen class variable
        avg_nutrient_rqmts = {'NEmaint': self.NEmaint, 'NEa': self.NEa,
                              'NEg': self.NEg, 'NEpreg': self.NEpreg, 'NEl': self.NEl,
                              'MP_req': self.MP_req, 'Ca_req': self.Ca_req, 'P_req': self.P_req,
                              'DMIest': self.DMIest, 'avg_BW': self.avg_BW, 'avg_milk': self.avg_milk,
                              'avg_milk_production_reduction': self.avg_milk_production_reduction,
                              'cumulated_milk':sum(milk),
                              'num_animals':len(pen.animals_in_pen)}
        #print(avg_nutrient_rqmts)
        om.add_variable(f'avg_rqmts_for pen {pen.id} ', avg_nutrient_rqmts, info_map)

        pen.set_avg_nutrient_rqmts(avg_nutrient_rqmts)

        pen.set_milk_avgs(self.avg_milk, self.avg_CP_milk, self.avg_milk_production_reduction)


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
