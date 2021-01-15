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
import statistics as stat
import math


def optimization(requirements, available_feeds, BW, animal_type, cow_type):
    """
    Function that sets up the nutrients and requirements lists into structured
    inputs for the non-linear program and calls the optimization function.

    Args:
        requirements: object of class Requirements
        available_feeds: object of class AvailableFeeds
        BW: Average Body weight of the input pen
        animal_type: string representation of the animal
        cow_type: Boolean which is True if cow is lactating, False otherwise
    """
    price = NLP.list_reconfig(available_feeds.price)
    TDN = NLP.list_reconfig(available_feeds.TDN)
    DE = NLP.list_reconfig(available_feeds.DE)
    EE = NLP.list_reconfig(available_feeds.EE)
    is_fat = NLP.list_reconfig(available_feeds.is_fat)
    calcium = NLP.list_reconfig(available_feeds.calcium)
    phosphorus = NLP.list_reconfig(available_feeds.phosphorus)
    NDF = NLP.list_reconfig(available_feeds.NDF)
    feed_type = NLP.list_reconfig(available_feeds.type)
    is_wetforage = NLP.list_reconfig(available_feeds.is_wetforage)
    Kd = NLP.list_reconfig(available_feeds.Kd)
    N_A = NLP.list_reconfig(available_feeds.N_A)
    N_B = NLP.list_reconfig(available_feeds.N_B)
    CP = NLP.list_reconfig(available_feeds.CP)
    dRUP = NLP.list_reconfig(available_feeds.dRUP)
    if cow_type:
        limit = NLP.list_reconfig(available_feeds.lactating_cow_limit)
    else:
        limit = NLP.list_reconfig(available_feeds.dry_cow_limit)
    NLP.set_globals(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                    requirements.NEl, requirements.NEg, requirements.MP_req,
                    requirements.Ca_req, requirements.P_req,
                    TDN, DE, EE, is_fat, BW, calcium, phosphorus, NDF,
                    feed_type, is_wetforage, Kd, N_A, N_B, CP, dRUP, limit, cow_type,
                    animal_type_ = animal_type,
                    DMIest_ = requirements.DMIest)
    #try block for catching scipy SLSQP error
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
    #this case should not be called, but is in place to not crash the
    #simulation if bounds error is not resolved
        if count > 30:
            solution = None

    return solution


def ration_formulation(pen, available_feeds, animal_type, cow_type):
    """
    Function that links the ration_driver file with the calc_ration function in
    pen.py. Returns a dictionary of the rations by feed and status of the NLP
    optimization.

    Args:
        pen: an object of class Pen
        available_feeds: an object of class AvailableFeeds
        animal_type: string representation of the type of animal (cow, heifer)
        cow_type: Boolean which is True if cow is lactating, False otherwise
    """
    # creating instance of class requirements
    req = Requirements()
    req.set_requirements(pen, animal_type, False)
    BW = pen.avg_BW
    solution = optimization(req, available_feeds, BW, animal_type, cow_type)
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
            # recalculating requirements after reduction
            req.set_requirements(pen, animal_type, True)
            solution = optimization(req, available_feeds, BW, animal_type, cow_type)
            #in case of scipy error
            if solution == None:
                break

    if solution != None:
        ration = {}
        for feed_id in range(len(available_feeds.feed_id)):
            i = feed_id * 3
            num = solution.x[i]
            num += solution.x[i + 1]
            num += solution.x[i + 2]
            ration[available_feeds.feed_key[feed_id]] = round(num, 6)
        ration['status'] = 'Optimal'
        ration['objective'] = NLP.objective(solution.x)
        return ration
    #safeguard if scipy SLSQP bounds error still occurs after many iterations
    #using previous cycles ration for this pen
    else:
        return pen.ration / len(pen.animals_in_pen)


def ration_report(ration, available_feeds):
    """
    Calculates information in the ration about nutrient information including
    nutrient amounts and concentrations. Returns a dictionary of nutrient amounts
    and nutrient calculations respectively.

    Args:
        ration: a dictionary of the calculated ration
        available_feeds: available feeds dictionary from the Feed class object
    """
    nutrient_amount = {'dm_amount': 0, 'as_fed_amount': 0, 'cp_amount': 0, 'adf_amount': 0,
                       'ndf_amount': 0, 'lignin_amount': 0, 'ash_amount': 0,
                       'P_amount': 0, 'K_amount': 0, 'N_amount': 0}
    nutrient_conc = {}
    ration = ration.copy()
    ration.pop('status')
    ration.pop('objective')
    for key, val in ration.items():
        # TODO: Code condensation
        nutrient_amount['dm_amount'] += val
        nutrient_amount['as_fed_amount'] += val / (available_feeds[key]['DM'] / 100)
        # all values on a 100% dry matter basis
        nutrient_amount['cp_amount'] += (available_feeds[key]['CP'] / 100) * val
        nutrient_amount['adf_amount'] += (available_feeds[key]['ADF'] / 100) * val
        nutrient_amount['ndf_amount'] += (available_feeds[key]['NDF'] / 100) * val
        nutrient_amount['lignin_amount'] += (available_feeds[key]['lignin'] / 100) \
                                            * val
        nutrient_amount['ash_amount'] += (available_feeds[key]['ash'] / 100) * val
        nutrient_amount['P_amount'] += (available_feeds[key]['phosphorus'] / 100) \
                                       * val
        nutrient_amount['K_amount'] += (available_feeds[key]['potassium'] / 100) \
                                       * val
        # [A.2.A.2]
        if key[:3] in ['121', '122', '155', '157']:
            denom = 6.38
        # [A.2.A.1]
        else:
            denom = 6.25
        nutrient_amount['N_amount'] += (available_feeds[key]['CP'] / (denom * 100)) * val
    dm_amount = nutrient_amount['dm_amount']
    nutrient_conc['dm_conc'] = dm_amount / nutrient_amount['as_fed_amount']
    # all values on a 100% dry matter basis
    nutrient_conc['cp_conc'] = (nutrient_amount['cp_amount'] / dm_amount) * 100
    nutrient_conc['adf_conc'] = (nutrient_amount['adf_amount'] / dm_amount) * 100
    nutrient_conc['ndf_conc'] = (nutrient_amount['ndf_amount'] / dm_amount) * 100
    nutrient_conc['lignin_conc'] = (nutrient_amount['lignin_amount'] / dm_amount) \
                                   * 100
    nutrient_conc['ash_conc'] = (nutrient_amount['ash_amount'] / dm_amount) * 100
    nutrient_conc['P_conc'] = (nutrient_amount['P_amount'] / dm_amount) * 100
    nutrient_conc['K_conc'] = (nutrient_amount['K_amount'] / dm_amount) * 100
    nutrient_conc['N_conc'] = (nutrient_amount['N_amount'] / dm_amount) * 100

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

        if recalc:
            # iterating through each animal in the pen and calculating requirements
            # temp parameter for heifer is hardcoded because heifer req should
            # never have to be recalculated
            for animal in pen.animals_in_pen:
                a_type = type(animal).__name__
                if a_type == 'HeiferI':
                    req = animal_requirements.calc_rqmts(animal.body_weight,
                        animal.mature_body_weight, None, animal_type = 'heifer',
                                                    BCS5 = 3, PrevTemp = 15,
                                              ADG_heifer = animal.daily_growth,
                                                     Age = animal.days_born
                                                      )
                elif a_type == 'HeiferII' or a_type == 'HeiferIII':
                    req = animal_requirements.calc_rqmts(animal.body_weight,
                        animal.mature_body_weight,  animal.days_in_preg,
                            animal_type = 'heifer', BCS5 = 3, PrevTemp = 15,
                                            ADG_heifer = animal.daily_growth,
                                                      Age = animal.days_born
                                                      )
                else:
                    req = animal_requirements.calc_rqmts(animal.body_weight,
                                    animal.mature_body_weight, animal.days_in_preg,
                                    'cow', animal.calves, animal.CI,
                                    animal.mPrt, animal.fat_percent, animal.lactose_milk,
                                    animal.estimated_daily_milk_produced,
                                    animal.days_in_milk, animal.milking
                                                  )

                animal.NEmaint = req['NEmaint']
                animal.NEg = req['NEg']
                animal.NEpreg = req['NEpreg']
                animal.NEl = req['NEl']
                animal.MP_req = req['MP_req']
                animal.Ca_req = req['Ca_req']
                animal.P_req = req['P_req']
                animal.DMIest = req['DMIest']
                #these animal class variables are only used for grouping purposes
                if animal_type == 'cow':
                    animal.DNED_req = (req['NEmaint'] + req['NEl']) / animal.DMIest
                    animal.DMDP_req = (req['MP_req']) / animal.DMIest

                    # calculating the activity requirement for energy
                    animal.calc_daily_walking_dist(pen.vertical_dist_to_parlor,
                                                   pen.horizontal_dist_to_parlor)
                    NEa_val = animal_requirements.energy_activity_rqmts(animal.body_weight,
                                                                     pen.housing_type,
                                                                     (math.sqrt(animal.DVD ** 2 + animal.DHD ** 2)))
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
