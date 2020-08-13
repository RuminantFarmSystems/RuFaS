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
    """
    Function that sets up the nutrients and requirements lists into structured
    inputs for the non-linear program and calls the optimization function.

    Args:
        pen: object of class pen
        requirements: object of class Requirements
        available_feeds: object of class AvailableFeeds
        BW: Average Body weight of the input pen
        SBW: Average Shrunk Body weight of pen
    """
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
    limit = NLP.list_reconfig(available_feeds.lactating_cow_limit)
    NLP.set_globals(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                            requirements.NEl, requirements.NEg, requirements.MP_req,
                            requirements.Ca_req, requirements.P_req, requirements.DMIest,
                            TDN, DE, EE, is_fat, BW, SBW, calcium, phosphorus, NDF,
                            type, is_wetforage, Kd, N_A, N_B, CP, dRUP, limit)
    solution = NLP.optimize()
    #print(solution.success)
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
        ration[available_feeds.feed_key[id]] = round(num, 6)
    ration['status'] = 'Optimal'
    ration['objective'] = NLP.objective(solution.x)
    print(ration)
    return ration

def hardcoded_rat():
    return {'2': 0.75,
            '24': 5,
            '36': 2,
            '38': 4,
            '91': 5,
            '102': 3,
            '137': 0.32,
            'status': 'Optimal',
            'objective': 4.5}
def ration_report(ration, available_feeds):
    """
    """
    nutrient_amount = {'dm_amount': 0, 'cp_amount': 0, 'adf_amount': 0,
                        'ndf_amount': 0, 'lignin_amount': 0, 'ash_amount': 0,
                        'P_amount': 0, 'K_amount': 0, 'N_amount': 0}
    nutrient_conc = {}
    ration = ration.copy()
    ration.pop('status')
    ration.pop('objective')
    for key, val in ration.items():
        nutrient_amount['dm_amount'] += (available_feeds[key]['DM']/100) * val
        nutrient_amount['cp_amount'] += (available_feeds[key]['CP']/100) * val
        nutrient_amount['adf_amount'] += (available_feeds[key]['ADF']/100) * val
        nutrient_amount['ndf_amount'] += (available_feeds[key]['NDF']/100) * val
        nutrient_amount['lignin_amount'] +=(available_feeds[key]['lignin']/100)\
                                                                         * val
        nutrient_amount['ash_amount'] += (available_feeds[key]['ash']/100) * val
        nutrient_amount['P_amount'] += (available_feeds[key]['phosphorus']/100)\
                                                                          * val
        nutrient_amount['K_amount'] += (available_feeds[key]['potassium']/100)\
                                                                        *val
        # [A.2.A.1]
        if key[:3] in ['121', '122', '155', '157']:
            denom = 6.25
        # [A.2.A.2]
        else:
            denom = 6.38
        nutrient_amount['N_amount'] += (available_feeds[key]['CP'] / \
                                                        (denom*100)) * val
    dm_amount = nutrient_amount['dm_amount']
    # TODO: ask about DM conc
    nutrient_conc['dm_conc'] = 100
    nutrient_conc['cp_conc'] = (nutrient_amount['cp_amount'] / dm_amount) * 100
    nutrient_conc['adf_conc'] = (nutrient_amount['adf_amount']/dm_amount) * 100
    nutrient_conc['ndf_conc'] = (nutrient_amount['ndf_amount']/dm_amount) *100
    nutrient_conc['lignin_conc']=(nutrient_amount['lignin_amount']/dm_amount)\
                                                                        * 100
    nutrient_conc['ash_conc']=(nutrient_amount['ash_amount']/dm_amount) * 100
    nutrient_conc['P_conc']=(nutrient_amount['P_amount']/dm_amount)*100
    nutrient_conc['K_conc']=(nutrient_amount['K_amount']/dm_amount)*100
    nutrient_conc['N_conc'] = (nutrient_amount['N_amount']/dm_amount)*100

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
        Class function that manipulates the avaialable feeds nutrient information
        into list (valid for input in the non-linear program) and populates the
        corresponding class variables.

        Args:
            feed: an instance of the Feed class object
        """
        # available feeds dictionary from the feed module
        available_feeds = feed.available_feeds
        # dictionary of feed costs
        feed_costs = feed.feed_costs

        feed_key = []
        feed_id = []
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
        lactating_cow_limit = []
        dry_cow_limit = []
        heiferIII_limit = []
        heiferII_limit = []
        heiferI_limit = []
        calf_limit = []

        for key, feed in available_feeds.items():
            feed_key.append(key)
            feed_id.append(feed['feed_id'])
            price.append(feed_costs[str(key)])
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
            if isinstance(feed['limit'], dict):
                lactating_cow_limit.append(feed['limit']['lactating_cows'])
                dry_cow_limit.append(feed['limit']['dry_cows'])
                heiferIII_limit.append(feed['limit']['heiferIIIs'])
                heiferII_limit.append(feed['limit']['heiferIIs'])
                heiferI_limit.append(feed['limit']['heiferIs'])
                calf_limit.append(feed['limit']['calves'])
            else:
                lactating_cow_limit.append(feed['limit'])
                dry_cow_limit.append(feed['limit'])
                heiferIII_limit.append(feed['limit'])
                heiferII_limit.append(feed['limit'])
                heiferI_limit.append(feed['limit'])
                calf_limit.append(feed['limit'])

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
        self.lactating_cow_limit = lactating_cow_limit
        self.dry_cow_limit = dry_cow_limit
        self.heiferIII_limit = heiferIII_limit
        self.heiferII_limit = heiferII_limit
        self.heiferI_limit = heiferI_limit
        self.calf_limit = calf_limit
