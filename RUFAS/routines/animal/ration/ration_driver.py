################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: ration_driver.py
Description: Main file in the ration formulation process that connects all
    other files such as requirements files and non-linear program files and
    also connects with the Feed and Animal modules to bring in relevant values.
"""
################################################################################
from RUFAS.routines.animal.ration import cow_requirements
from RUFAS.routines.animal.ration import lactating_cow_ration_NLP as NLP
import statistics as stat
import math
import random

def optimization(pen, requirements, available_feeds, BW, SBW):
    price = NLP.list_reconfig(available_feeds.price)
    TDN = NLP.list_reconfig(available_feeds.TDN)
    DE = NLP.list_reconfig(available_feeds.DE)
    EE = NLP.list_reconfig(available_feeds.EE)
    is_fat = NLP.list_reconfig(available_feeds.is_fat)
    calcium = NLP.list_reconfig(available_feeds.calcium)
    phosphorus = NLP.list_reconfig(available_feeds.phosphorus)
    NDF = NLP.list_reconfig(available_feeds.NDF)
    type = NLP.list_reconfig(available_feeds.type)
    is_wetforage = NLP.list_reconfig(available_feeds.is_wetforage)
    Kd = NLP.list_reconfig(available_feeds.Kd)
    N_A = NLP.list_reconfig(available_feeds.N_A)
    N_B = NLP.list_reconfig(available_feeds.N_B)
    CP = NLP.list_reconfig(available_feeds.CP)
    dRUP = NLP.list_reconfig(available_feeds.dRUP)
    NLP.set_globals(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                            requirements.NEl, requirements.NEg, requirements.MP_req,
                            requirements.Ca_req, requirements.P_req, requirements.DMIest,
                            TDN, DE, EE, is_fat, BW, SBW, calcium, phosphorus, NDF,
                            type, is_wetforage, Kd, N_A, N_B, CP, dRUP)
    solution = NLP.optimize()
    #print(solution.success)
    '''
    print(solution.success)
    print('Con_2: ')
    print(NLP.NEl_constraint(solution.x))

    constraints = {'Con_1': NLP.NEmact_constraint(solution.x), 'Con_2': NLP.NEl_constraint(solution.x),
    'Con_3': NLP.NEgact_constraint(solution.x), 'Con_4': NLP.calcium_constraint(solution.x),
    'Con_5': NLP.phosphorus_constraint(solution.x), 'Con_6': NLP.protien_constraint(solution.x),
    'Con_7': NLP.NDF_constraint_1(solution.x), 'Con_8': NLP.NDF_constraint_2(solution.x),
    'Con_9': NLP.forage_NDF_constraint(solution.x), 'Con_10': NLP.fat_constraint(solution.x),
    'Con_11': NLP.DMI_constraint(solution.x) }

    for key, val in constraints.items():
        if val < -0.001:
            print(key)
            print(val)
    '''

    return solution

def ration_formulation(pen, available_feeds):
    """
    Function that links the ration_driver file with the calc_ration function in
    pen.py. Returns a dictionary of the rations by feed and status of the NLP
    optimization.

    Args:
        pen: an object of class Pen
        available_feeds: an object of class AvailableFeeds
    """
    #print('Pen' + str(pen.id))
    req = Requirements()
    req.pen_requirements(pen)
    BW = pen.avg_BW
    solution = optimization(pen, req, available_feeds, BW, BW*0.953)
    #Reduction of milk production estimate process to achieve feasible solution
    while not solution.success:
        #TODO: Time analysis for hardcoded reduction values
        #print(NLP.NEl_constraint(solution.x))
        NEl_con = NLP.NEl_constraint(solution.x)
        if NEl_con < -0.5:
            reduction = 3*(-NEl_con)
        else:
            reduction = 1

        for animal in pen.animals_in_pen:
            animal.estimated_daily_milk_produced -= reduction
            #TODO: Code below is useful for time analysis
            #if animal.estimated_daily_milk_produced < 0:
            #    print('negative')
        req.pen_requirements(pen)
        solution = optimization(pen, req, available_feeds, BW, BW*0.953)

    ration = {}
    for id in range(len(available_feeds.feed_id)):
        i = id*3
        num = solution.x[i]
        num += solution.x[i+1]
        num += solution.x[i+2]
        ration[available_feeds.feed_key[id]] = round(num, 2)
    ration['status'] = 'Optimal'
    ration['objective'] = NLP.objective(solution.x)
    return ration

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

    def pen_requirements(self, pen):
        """
        Calculates the average requirements utilizing cow_requirements.py and an
        input pen to generate the average requirements across a pen. It then
        populates the corresponding class variables.

        Args:
            pen: an instance of an object of class Pen
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

        # iterating through each animal in the pen and calculating requirements
        for animal in pen.animals_in_pen:
            req = cow_requirements.calculate_requirements(animal.body_weight, animal.mature_body_weight,
                            animal.days_in_preg, pen.housing_type,(math.sqrt((animal.DVD)**2 + (animal.DHD)**2)),
                            animal.calves, animal.CI, animal.mPrt, animal.fat_percent,
                            animal.lactose_milk,animal.estimated_daily_milk_produced,
                            animal.days_in_milk)
            NEmaint.append(req['NEmaint'])
            NEa.append(req['NEa'])
            NEg.append(req['NEg'])
            NEpreg.append(req['NEpreg'])
            NEl.append(req['NEl'])
            MP_req.append(req['MP_req'])
            Ca_req.append(req['Ca_req'])
            P_req.append(req['P_req'])
            DMIest.append(req['DMIest'])
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

    def feed_nutrients(self, feed):
        """
        Class function that manipulates the avaialable feeds nutrient information
        into list (valid for input in the non-linear program) and populates the
        corresponding class variables.

        Args:
            feed: an instance of the Feed class object
        """
        available_feeds = feed.available_feeds
        feed_key = []
        feed_id = []
        ##TODO find where price comes from
        price = []
        TDN = []
        DE = []
        EE = []
        is_fat = []
        calcium = []
        phosphorus = []
        NDF = []
        type = []
        is_wetforage = []
        Kd = []
        N_A = []
        N_B = []
        CP = []
        dRUP = []
        limit = []

        for key, feed in available_feeds.items():
            feed_key.append(key)
            feed_id.append(feed['feed_id'])
            price.append(random.random() * 1)
            TDN.append(feed['TDN'])
            DE.append(feed['DE'])
            EE.append(feed['EE'])
            is_fat.append(feed['is_fat'])
            calcium.append(feed['calcium'])
            phosphorus.append(feed['phosphorus'])
            NDF.append(feed['NDF'])
            type.append(feed['type'])
            is_wetforage.append(feed['is_wetforage'])
            Kd.append(feed['Kd'])
            N_A.append(feed['N_A'])
            N_B.append(feed['N_B'])
            CP.append(feed['CP'])
            dRUP.append(feed['dRUP'])
            limit.append(feed['limit'])

        self.feed_key = feed_key
        self.feed_id = feed_id
        self.price = price
        self.TDN = TDN
        self.DE = DE
        self.EE = EE
        self.is_fat = is_fat
        self.calcium = calcium
        self.phosphorus = phosphorus
        self.NDF = NDF
        self.type = type
        self.is_wetforage = is_wetforage
        self.Kd = Kd
        self.N_A = N_A
        self.N_B = N_B
        self.CP = CP
        self.dRUP = dRUP
        self.limit = limit
