################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: ration_driver.py
Description: Main file in the ration formulation process that connects all
    other files such as requirements files and non-linear program files and
    also connects with the Feed and Animal modules to bring in relevant values.
"""
################################################################################
#from RUFAS.routines.feed.feed import Feed
#from RUFAS.routines.animal.animal_management import AnimalManagement
from RUFAS.routines.animal.ration import cow_requirements
from RUFAS.routines.animal.ration import lactating_cow_ration_NLP as NLP
import statistics as stat
import math
import random


def ration_formulation(requirements, available_feeds):
    #TODO do a real values
    BW = 600
    SBW = 600*0.96
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
    x0 = [0]*int(len(price))
    solution = NLP.optimize(x0)
    count = 0
    while not solution.success and count < 30:
        solution = NLP.optimize()
        #print(x0)
        #print('X: ')
        #print(NLP.objective(solution.x))
        #print(rounded)
        #print(solution.success)
        rounded = [round(num, 2) for num in solution.x]
        print('X: ')
        print(rounded)
        count += 1
        print('Con_1')
        print(NLP.NEmact_constraint(solution.x))
        print('Con_2')
        print(NLP.NEl_constraint(solution.x))
        print('Con_3')
        print(NLP.NEgact_constraint(solution.x))
        print('Con_4')
        print(NLP.calcium_constraint(solution.x))
        print('Con_5')
        print(NLP.phosphorus_constraint(solution.x))
        print('Con_6')
        print(NLP.protien_constraint(solution.x))
        print('Con_7')
        print(NLP.NDF_constraint_1(solution.x))
        print('Con_8')
        print(NLP.NDF_constraint_2(solution.x))
        print('Con_9')
        print(NLP.forage_NDF_constraint(solution.x))
        print('Con_10')
        print(NLP.fat_constraint(solution.x))
        print('Con_11')
        print(NLP.DMI_constraint(solution.x))

        print('Con_12')
        print(NLP.energy_req_limit_constraint(solution.x))

    rounded = [round(num, 2) for num in solution.x]
    print(solution.success)
    print(rounded)
    print('Break')



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
        input pen to generate the average requirements across pens. It then
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
        #TODO find where these values come from. Confirm other values
        fat_milk = 3

        # iterating through each animal in the pen and calculating requirements
        for animal in pen.animals_in_pen:
            req = cow_requirements.calculate_requirements(animal.body_weight, animal.mature_body_weight,
                            animal.days_in_preg, pen.housing_type,(math.sqrt((animal.DVD)**2 + (animal.DHD)**2)),
                            animal.calves, animal.CI, animal.mPrt, fat_milk,
                            animal.lactose_milk,animal.estimated_daily_milk_produced_lst[0],
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

        for key in available_feeds:
            feed_id.append(available_feeds[key]['feed_id'])
            price.append(random.random() * 5)
            TDN.append(available_feeds[key]['TDN'])
            DE.append(available_feeds[key]['DE'])
            EE.append(available_feeds[key]['EE'])
            is_fat.append(available_feeds[key]['is_fat'])
            calcium.append(available_feeds[key]['calcium'])
            phosphorus.append(available_feeds[key]['phosphorus'])
            NDF.append(available_feeds[key]['NDF'])
            type.append(available_feeds[key]['type'])
            is_wetforage.append(available_feeds[key]['is_wetforage'])
            Kd.append(available_feeds[key]['Kd'])
            N_A.append(available_feeds[key]['N_A'])
            N_B.append(available_feeds[key]['N_B'])
            CP.append(available_feeds[key]['CP'])
            dRUP.append(available_feeds[key]['dRUP'])
            limit.append(available_feeds[key]['limit'])

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



'''
    available_feeds = {'2': {'feed_id': 2, 'type': 'Conc', 'DM': 86.9, 'CP': 6.5, 'NDICP': 2.3, 'ADICP': 1.8, 'EE': 2.9, 'NDF': 36.8, 'ADF': 28.7, 'lignin': 14.9, 'ash': 6.1, 'non_fiber_carb': 50, 'PAF': 1, 'TDN': 58.36, 'N_A': 29.6, 'N_B': 35.4, 'N_C': 35, 'Kd': 5.3, 'dRUP': 50, 'calcium': 0.28, 'phosphorus': 0.13, 'magnesium': 0.13, 'potassium': 2.6, 'sodium': 0.02, 'chlorine': 0.03, 'sulfur': 0.04, 'DE': 2.53, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '24': {'feed_id': 24, 'type': 'Conc', 'DM': 89.4, 'CP': 23.8, 'NDICP': 3.6, 'ADICP': 1.4, 'EE': 3.5, 'NDF': 35.5, 'ADF': 12.1, 'lignin': 2, 'ash': 6.8, 'non_fiber_carb': 34, 'PAF': 1, 'TDN': 74.07, 'N_A': 48, 'N_B': 43.2, 'N_C': 8.8, 'Kd': 7.7, 'dRUP': 85, 'calcium': 0.07, 'phosphorus': 1, 'magnesium': 0.42, 'potassium': 1.46, 'sodium': 0.13, 'chlorine': 0.2, 'sulfur': 0.44, 'DE': 3.43, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '36': {'feed_id': 36, 'type': 'Forage', 'DM': 35.1, 'CP': 8.8, 'NDICP': 1.3, 'ADICP': 0.8, 'EE': 3.2, 'NDF': 45, 'ADF': 28.1, 'lignin': 2.6, 'ash': 4.3, 'non_fiber_carb': 40, 'PAF': 0.94, 'TDN': 68.82, 'N_A': 51.3, 'N_B': 30.2, 'N_C': 18.5, 'Kd': 4.4, 'dRUP': 70, 'calcium': 0.28, 'phosphorus': 0.26, 'magnesium': 0.17, 'potassium': 1.2, 'sodium': 0.01, 'chlorine': 0.29, 'sulfur': 0.14, 'DE': 2.99, 'is_fat': 0, 'is_wetforage': 1, 'units': 'kg', 'limit': 100}, '38': {'feed_id': 38, 'type': 'Conc', 'DM': 90.1, 'CP': 23.5, 'NDICP': 2.4, 'ADICP': 1.9, 'EE': 19.3, 'NDF': 50.3, 'ADF': 40.1, 'lignin': 12.9, 'ash': 4.2, 'non_fiber_carb': 5.1, 'PAF': 1, 'TDN': 77.22, 'N_A': 45.4, 'N_B': 46.7, 'N_C': 7.9, 'Kd': 15.7, 'dRUP': 80, 'calcium': 0.17, 'phosphorus': 0.6, 'magnesium': 0.37, 'potassium': 1.13, 'sodium': 0.02, 'chlorine': 0.06, 'sulfur': 0.23, 'DE': 3.55, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '91': {'feed_id': 91, 'type': 'Forage', 'DM': 39.1, 'CP': 20, 'NDICP': 2.9, 'ADICP': 1.6, 'EE': 3.1, 'NDF': 45.7, 'ADF': 37, 'lignin': 8.1, 'ash': 10.4, 'non_fiber_carb': 23.7, 'PAF': 1, 'TDN': 56.57, 'N_A': 57.3, 'N_B': 33, 'N_C': 9.9, 'Kd': 11.1, 'dRUP': 65, 'calcium': 1.34, 'phosphorus': 0.32, 'magnesium': 0.27, 'potassium': 2.87, 'sodium': 0.06, 'chlorine': 0.62, 'sulfur': 0.24, 'DE': 2.62, 'is_fat': 0, 'is_wetforage': 1, 'units': 'kg', 'limit': 100}, '102': {'feed_id': 102, 'type': 'Forage', 'DM': 91.9, 'CP': 9.1, 'NDICP': 1.3, 'ADICP': 0.6, 'EE': 2.2, 'NDF': 58, 'ADF': 36.4, 'lignin': 6.5, 'ash': 8.5, 'non_fiber_carb': 23.5, 'PAF': 1, 'TDN': 55.91, 'N_A': 35, 'N_B': 53.1, 'N_C': 11.9, 'Kd': 4.3, 'dRUP': 70, 'calcium': 0.37, 'phosphorus': 0.22, 'magnesium': 0.17, 'potassium': 2.01, 'sodium': 0.33, 'chlorine': 1.08, 'sulfur': 0.14, 'DE': 2.46, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}, '137': {'feed_id': 137, 'type': 'Mineral', 'DM': 97, 'CP': 0, 'NDICP': 0, 'ADICP': 0, 'EE': 0, 'NDF': 0, 'ADF': 0, 'lignin': 0, 'ash': 0, 'non_fiber_carb': 0, 'PAF': 0, 'TDN': 0, 'N_A': 0, 'N_B': 0, 'N_C': 0, 'Kd': 0, 'dRUP': 0, 'calcium': 16.4, 'phosphorus': 21.6, 'magnesium': 0, 'potassium': 0, 'sodium': 0, 'chlorine': 0, 'sulfur': 1.22, 'DE': 0, 'is_fat': 0, 'is_wetforage': 0, 'units': 'kg', 'limit': 100}}
'''
