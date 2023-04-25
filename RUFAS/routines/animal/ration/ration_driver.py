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
from typing import Dict, List, Set, Any, Union
import collections
import math
import statistics as stat
from RUFAS.routines.animal.ration.user_defined_ration import user_defined_ration_values as user_defined_ration_values
udrv = user_defined_ration_values()
from RUFAS.routines.animal.ration.user_defined_ration import ration_to_use as ration_to_use

def optimization(pen, requirements, available_feeds, animal_type, cow_type, user_defined_ration_select=False, ration_percents = None):
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
    #print('optimization_attempt')
    while i < 1:
        try:
            solution = NLP.optimize(user_defined_ration_select, ration_percents)
            # TODO here we need to add a way to check why this is failing to optimize and
            # certainly happening at the minimize step, but we must  quantify which requirements aren't being met
        except:
            i -= 1
        finally:
            i += 1
            count += 1
        # this case should not be called, but is in place to not crash the
        # simulation if bounds error is not resolved
        #print(count)
        if count > 30:
            solution = None
            mock_solution = user_defined_solution(pen, requirements.DMIest)
            ration_vals = NLP.get_ration_vals_null(mock_solution)
            #print('nullvals')
            return solution, ration_vals

    # retrieving MEact from diet
    if solution == None:
        ration_vals = None
    else:
        ration_vals = NLP.get_ration_vals(solution.x)
    return solution, ration_vals


def user_defined_solution(pen, DMIest):
    """
    Returns a "solution" in format of the output from the optimization function
    Simply takes the percentage values and multiplies them by estimated DMI to retrieve the calculated  ration
    Each ration is represented in the NLP process as the sum of three values, here we simplify it by reporting two values as 0.0

    Parameters
    ----------
    Pen: object of pen class
    
    DMIest: float

    Returns
    -------
    solution: list[float,]
        list of values in order of feeds available for a given animal_type
    """
    ration_percents = ration_to_use(pen.animal_combination)
    solution = []
    for rationkey in ration_percents.keys():
        value = ration_percents[rationkey]*DMIest
        solution.append(value)
        solution.append(0.0)
        solution.append(0.0)
    return solution


def user_defined_ration(req, pen, available_feeds, animal_type, cow_type, user_defined_ration_select):
    """
    Function that links the ration_driver file with the calc_ration function in
    pen.py. Returns a dictionary of the rations by feed and status of the NLP
    optimization.

    Args:
        pen: an object of class Pen
        feed: an object of class Feed
        available_feeds: an object of class AvailableFeeds
        animal_type: string
            representation of the type of animal (cow, heifer)
        cow_type: Boolean 
            True if cow is lactating, False otherwise
        user_defined_ration_select: Boolean of whether user input selected
    """
    ration_percents = ration_to_use(pen.animal_combination)
    solution, ration_vals = optimization(pen, req, available_feeds, animal_type, cow_type, user_defined_ration_select, ration_percents)
    # Reduction of milk production estimate process to achieve feasible solution
    if animal_type == 'cow':
        total_milk_in_pen = 0.0
        num_animals = 0
        for animal in pen.animals_in_pen:
            total_milk_in_pen += animal.estimated_daily_milk_produced
            num_animals += 1
        average_total_milk = total_milk_in_pen/num_animals
        # print('average_total_milk = '+ str(average_total_milk))
    fixed_ration = False
    if animal_type == 'cow' and solution is not None:
        while not solution.success:
            # TODO: JCW 24 Mar 2023 commented out below is the existing method, here we're simply reducing 1 at a time.
            # This values for reduction are not from pseudocode, but the vales below
            # are based on fastest case runtime testing
            # TODO: continue testing for more efficient reductions
            # NEl_con = NLP.NEl_constraint(solution.x)
            # if NEl_con < -0.5:
            #     reduction = 3 * (-NEl_con)
            # else:
            #     reduction = 1.5
            reduction = 1.0
            running_total_milk = 0.0
            for animal in pen.animals_in_pen:
                if animal.estimated_daily_milk_produced > 1.0:
                    animal.estimated_daily_milk_produced -= reduction
                    animal.milk_production_reduction -= reduction
                running_total_milk += animal.estimated_daily_milk_produced
            average_running_total_milk = running_total_milk / num_animals
            chanchodebug = False
            if chanchodebug:
                print('dropping milk!')
                print('reduction = '+ str(reduction))
                print('average_running_total_milk = '+ str(average_running_total_milk))
            # recalculating requirements after reduction
            req.set_requirements(pen, animal_type, True)
            solution, ration_vals = optimization(pen, req, available_feeds, animal_type, cow_type, user_defined_ration_select, ration_percents)
            if average_running_total_milk < udrv.milk_reduction_percent*average_total_milk or average_running_total_milk == 0.0:
                fixed_ration = True
                solution.success = True
                if chanchodebug:
                    print('dropped too much!')
                    print(solution)
                break

    if solution is not None and not fixed_ration:
        #print(solution)
        #print('solution is not None and not fixed_ration')
        # if not fixed_ration:
        ration = {}
        for feed_id in range(len(available_feeds['feed_id'])):
            i = feed_id * 3
            num = solution.x[i]
            num += solution.x[i + 1]
            num += solution.x[i + 2]
            ration[available_feeds['feed_key'][feed_id]] = round(num, 6)
        ration['status'] = 'Optimal'
        ration['objective'] = NLP.objective(solution.x)
    else:
        #print('fixed ration')
        ration = {}
        chanchodebug = False
        if chanchodebug:
            print(available_feeds['feed_id'])
            print(ration_percents)
        for feed_id in range(len(available_feeds['feed_id'])):
            if available_feeds['feed_key'][feed_id] in ration_percents:
                ingredient_percentage = ration_percents[available_feeds['feed_key'][feed_id]]
                ingredient_as_proportion = ingredient_percentage/100*req.DMIest
                ration[available_feeds['feed_key'][feed_id]] = round(ingredient_as_proportion, 6)
                if chanchodebug:
                    print('ingredient_as_proportion = ' + str(ingredient_as_proportion))
                    print('ingredient_as_proportion = ' + str(round(ingredient_as_proportion,6)))
            else:
                ration[available_feeds['feed_key'][feed_id]] = 0.0
        ration['status'] = 'Optimal'
        ration['objective'] = 0.0 # setting as optimal
    return ration, ration_vals


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
    # print('udrv.udr_or_not' + str(udrv.udr_or_not))
    user_defined_ration_select = udrv.udr_or_not
    if user_defined_ration_select:
        ration, ration_vals = user_defined_ration(req, pen, available_feeds, animal_type, cow_type,user_defined_ration_select)
        #print('\n \n \n returning UDR \n \n \n ')
        return ration, ration_vals

    solution, ration_vals = optimization(pen, req, available_feeds, animal_type, cow_type,)
    # Reduction of milk production estimate process to achieve feasible solution
    if animal_type == 'cow':
        while not solution.success:
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
            solution, ration_vals = optimization(pen, req, available_feeds, animal_type, cow_type)

    if solution != None:
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
                nutrient_amount[nutr] += (available_feeds[key]['CP'] /
                                          (denom * 100)) * val
            else:
                nutrient_amount[nutr] += val * (available_feeds[key][nutr] / 100)

    # feed nutrient concentrations
    dm_amount = nutrient_amount['dm']
    for nutr in nutrients:
        if nutr == 'DM':
            nutrient_conc['dm'] = (nutrient_amount['as_fed'] / dm_amount) \
                                  * 100
        else:
            # all values on a 100% dry matter basis
            nutrient_conc[nutr] = (nutrient_amount[nutr] / dm_amount) \
                                  * 100

    return nutrient_amount, nutrient_conc

def ration_net_energy_maintenance(ration, available_feeds):
    """
    Returns actual net energy for maintenance of feed i, Mcal for given ration total

    first calculates actual metabolizable energy of feed i, Mcal/kg

    Then from the metabolizable energy, calculates the maintenance for each feed

    """  
    MEact = []
    for key, val in ration.items():
        if available_feeds[key]['type'] == 'Mineral':
            MEact.append(0)
        elif available_feeds[key]['is_fat'] == 1:
            MEact.append(val*available_feeds[key]['DE'])
        elif available_feeds[key]['EE'] >= 3:
            MEact.append(val*(1.01 * available_feeds[key]['DE'] - 0.45 + 0.0046 * (available_feeds[key]['EE'] - 3)))
        else:
            MEact.append(val*(1.01 * available_feeds[key]['DE'] - 0.45))
    NEm_act = []
    i = 0
    for key, val in ration.items():
        if available_feeds[key]['is_fat'] == 1:
            NEm_act.append(0.8 * MEact[i])
        else:
            NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i] ** 2 + 0.0105 * MEact[i] ** 3 - 1.12)
        i+=1
    return sum(NEm_act)


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

        # setting average nutrient requirements pen class variable
        avg_nutrient_rqmts = {'NEmaint': self.NEmaint, 'NEa': self.NEa,
                              'NEg': self.NEg, 'NEpreg': self.NEpreg, 'NEl': self.NEl,
                              'MP_req': self.MP_req, 'Ca_req': self.Ca_req, 'P_req': self.P_req,
                              'DMIest': self.DMIest, 'avg_BW': self.avg_BW}

        pen.set_avg_nutrient_rqmts(avg_nutrient_rqmts)

        pen.set_milk_avgs(self.avg_milk, self.avg_CP_milk)


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
