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

        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination)
        # Reduction of milk production estimate process to achieve feasible solution
        num_reattempts = 0

        # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
        if pen.animal_combination.name in ['LAC_COW']:
            while not solution.success:
                num_reattempts += 1
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons, ration_config)
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                # TODO: continue testing for more efficient reductions: see Issues #569, 577, 589
                reduction = 0.5
                cls.reduce_milk_production(pen, reduction)

                req.set_requirements(pen, animal_grouping_scenario, True)
                solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination)
                info_map = {"class": "RationManager", 
                            "function": cls.formulate_ration.__name__,
                            }
                sim_day = pen.animals_in_pen[0].body_weight_history[-1].simulation_day
                fail_summary = {'simulation day' : sim_day,
                            'reattempt number' : num_reattempts,
                            'constraints_failed_dict': constraints_failed_list, 
                            'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                            'pen requirements' : pen.avg_nutrient_rqmts}
                om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)

        if solution is not None:
            ration = cls.make_ration_from_solution(available_feeds, solution)
            return ration, ration_vals
        # safeguard if scipy SLSQP bounds error still occurs after many iterations
        # using previous cycles ration for this pen
        else:
            return pen.ration, ration_vals

    @classmethod
    def calc_milk_average(cls, pen) -> float:
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
        ration_config.price = RationOptimizer.list_reconfig(available_feeds['price'])
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
        -> tuple[Dict[str, float], Dict[str, float]]:
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

        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination)
        if str(pen.animal_combination) in ['AnimalCombination.LAC_COW']:
            failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons, ration_config)
        else:
            failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.heifer_cons, ration_config)
        
        if failed_constraints is not None:
            for constr in failed_constraints:
                constraints_failed_list.append(constr["fun"].__name__)
            # TODO: is there a better way to get the simulation day?
            fail_summary = {'simulation day' : pen.animals_in_pen[0].body_weight_history[-1].simulation_day,
                        'reattempt number' : num_reattempts,
                        'constraints_failed_dict': constraints_failed_list, 
                        'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                        'pen requirements' : pen.avg_nutrient_rqmts}
            om.add_variable(f'failed_constraint_summary_for_pen_{pen.id}', fail_summary, info_map)
        
        if udrm.milk_reduction_maximum == 0.0 and udrm.tolerance == 0.0 and not solution.success:
            ration = UserDefinedRationManager.make_ration_from_user_values(ration_percents, available_feeds, req)
            ration_vals = ration_optimizer.get_ration_vals(cls.make_solution_from_fixed_ration(ration), ration_config)
            return ration, ration_vals

        if str(pen.animal_combination) not in ['AnimalCombination.LAC_COW'] and not solution.success:
            fixed_ration = True

        if str(pen.animal_combination) in ['AnimalCombination.LAC_COW'] and solution is not None:
            running_milk_reduction = 0.0
            while not solution.success:
                running_average_milk = cls.calc_milk_average(pen)
                reduction = 0.25
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
                solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination)
                failed_constraints = []
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(solution.x, ration_optimizer.cow_cons, ration_config)
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                    # TODO: is there a better way to get the simulation day?
                    fail_summary = {'simulation day' : pen.animals_in_pen[0].body_weight_history[-1].simulation_day,
                        'reattempt number' : num_reattempts,
                        'constraints_failed_dict': constraints_failed_list, 
                        'ration_attempted': cls.make_ration_from_solution(available_feeds, solution),
                        'pen requirements' : pen.avg_nutrient_rqmts}
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

    """
    def __init__(cls):
        cls.nutrient_amount = []
        cls.nutrient_conc = []
    
    @classmethod
    def report_ration(cls, ration, available_feeds):

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
                        'N': 0, "EE": 0, "starch": 0, "TDN": 0, "DE" : 0, "calcium":0}
        nutrient_conc = {}
        ration = ration.copy()
        for non_numeric_key in ['status', 'objective']:
            if non_numeric_key in ration:
                del ration[non_numeric_key]
        nutrients = ['DM', 'CP', 'ADF', 'NDF', 'lignin', 'ash', 'phosphorus',
                    'potassium', 'N', 'EE', 'starch', 'TDN', 'DE', 'calcium']

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


    @classmethod
    def ration_supply(cls, ration, available_feeds, ration_report, body_weight):
        ration = ration.copy()
        for non_numeric_key in ['status', 'objective']:
            if non_numeric_key in ration:
                del ration[non_numeric_key]

        supply_report = {
            'ME': 0.0,
            'DE': 0.0,
            'NE_maintenance_and_activity': 0.0,
            'NE_lactation': 0.0,
            'NE_growth': 0.0,
            'Calcium': 0.0,
            'Phosphorus': 0.0,
            'Forage_NDF': 0.0,
            'Forage_NDF_percent': 0.0,
            'Fat': 0.0,
            'Fat_percentage': 0.0
        }

        DMI = sum(ration.values())

        for key, val in ration.items():
            for item in supply_report:
                feed_item_info = available_feeds[key]
                supply_report[item] += eval('cls.get_' + item + '(val, feed_item_info, ration_report, body_weight)')

        supply_report['Forage_NDF_percent'] = supply_report['Forage_NDF'] / DMI

        supply_report['Metabolizable_protein'] = \
            cls.get_Metabolizable_protein(ration, available_feeds, ration_report, body_weight)

        return supply_report


    @classmethod
    def get_TDN_discount(cls, ration_report, body_weight):
        """
        Crucial step to take into account TDN digesitbility decreate from DMI and TDN
        Initial step in NE/ME calcs
        """
        TDNtotal = ration_report['nutrient_amount']['TDN']
        TDNconc = ration_report['nutrient_conc']['TDN']
        somatic_body_weight = body_weight * 0.96
        if body_weight == 0.0 or TDNtotal == 0.0:
            return 0.0
        if TDNtotal < (0.035 * body_weight ** 0.75):
            DMI_to_maint = 1
        else:
            DMI_to_maint = (TDNtotal / (0.035 * somatic_body_weight ** 0.75))
        # [A.Cow.E.3]-[A.Heifer.E.3]
        # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
        if TDNconc < 60:
            Discount = 1
        else:
            Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
        return Discount

    @classmethod
    def get_DE(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        DE_act = feed_item_info['DE'] * cls.get_TDN_discount(ration_report, body_weight)
        return DE_act

    @classmethod
    def get_ME(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        DE_act =cls.get_DE(val, feed_item_info, ration_report, body_weight)

        if feed_item_info['type'] == 'Mineral':
            ME_item = 0.0
        elif feed_item_info['is_fat'] == 1:
            ME_item = feed_item_info['DE']
        elif feed_item_info['EE'] >= 3:
            ME_item = 1.01 * DE_act - 0.45 + 0.0046 * (feed_item_info['EE'] - 3)
        else:
            ME_item = 1.01 * DE_act - 0.45
        return ME_item
        
    @classmethod
    def get_NE_maintenance_and_activity(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        ME_item = cls.get_ME(val, feed_item_info, ration_report, body_weight)
        # turn ME into NEm
        if feed_item_info['is_fat'] == 1:
            NEm_item = (0.8 * ME_item)
        else:
            NEm_item = 1.37 * ME_item - 0.138 * ME_item ** 2 + 0.0105 * ME_item ** 3 - 1.12
        return NEm_item * val

    @classmethod
    def get_NE_lactation(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        DE_act = cls.get_DE(val, feed_item_info, ration_report, body_weight)
        ME_item = cls.get_ME(val, feed_item_info, ration_report, body_weight)
        if feed_item_info['type'] == 'Mineral':
            NE_lactation_item = 0.0
        elif feed_item_info['is_fat'] == 1:
            NE_lactation_item = 0.8 * DE_act
        elif feed_item_info['EE'] >= 3:
            NE_lactation_item = 0.703 * ME_item - 0.19 + ((0.097 * ME_item + 0.19) / 97) * (feed_item_info['EE'] - 3)
        else:
            NE_lactation_item = 0.703 * ME_item - 0.19
        return NE_lactation_item * val

    @classmethod
    def get_NE_growth(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        ME_item = cls.get_ME(val, feed_item_info, ration_report, body_weight)
        if feed_item_info['type'] == 'Mineral':
            NE_growth = 0.0
        elif feed_item_info['is_fat'] == 1:
            NE_growth = 0.55 * ME_item
        else:
            NE_growth = 1.42 * ME_item - 0.174 * ME_item ** 2 + 0.0122 * ME_item ** 3 - 1.65
        return NE_growth * val

    @classmethod
    def get_Calcium(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        if feed_item_info['type'] == 'Forage':
            dCa = 0.3
        elif feed_item_info['type'] == 'Conc':
            dCa = 0.6
        elif feed_item_info['type'] == 'Mineral':
            dCa = 0.95
        else:
            dCa = 0.0
        calcium_item = val * feed_item_info['calcium'] * 0.01 * dCa
        return calcium_item


    @classmethod
    def get_Phosphorus(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        if feed_item_info['type'] == 'Forage':
            dP = 0.64
        elif feed_item_info['type'] == 'Conc':
            dP = 0.70
        elif feed_item_info['type'] == 'Mineral':
            dP = 0.80
        else:
            dP = 0.0
        return dP * feed_item_info['phosphorus'] * 0.01 * val

    @classmethod
    def get_Metabolizable_protein(cls, ration, available_feeds, ration_report, body_weight):
        """
        
        """
        TDNconc = ration_report['nutrient_conc']['TDN']
        TDNtotal = ration_report['nutrient_amount']['TDN']

        DMI_estimate = sum(ration.values())
        is_conc = []
        for item in ration:
            if available_feeds[item]['type'] == 'Conc':
                is_conc.append(ration[item])
        DMI_conc_percentage = sum(is_conc) / DMI_estimate * 100
        Kp = []
        RUP_list = []
        RDP_list = []
        dRUP_diet = []
        counter = 0
        for key, val in ration.items():
            feed_item_info = available_feeds[key]

            # KP calcs
            if feed_item_info['type'] == 'Conc':
                Kp.append(2.904 + 1.375 * (DMI_estimate / body_weight) * 100 - 0.02 * DMI_conc_percentage)
            elif feed_item_info['type'] == 'Forage' and feed_item_info['is_wetforage'] == 0:
                Kp.append(3.362 + 0.479 * (DMI_estimate / body_weight) * 100 - 0.017 * feed_item_info['NDF'] - 0.007 * DMI_conc_percentage)
            elif feed_item_info['is_wetforage'] == 1:
                Kp.append(3.054 + 0.614 * (DMI_estimate / body_weight) * 100)
            else:
                Kp.append(0)

            # RDP calcs
            if Kp[counter] > -feed_item_info['Kd']:
                RDP_list.append( (feed_item_info['Kd'] / (feed_item_info['Kd'] + Kp[counter]) * (feed_item_info['N_B'] / 100) * feed_item_info['CP'] + (feed_item_info['N_A'] / 100) * feed_item_info['CP']) ) 
            else:
                RDP_list.append(0)

            # RUP calcs
            RUP_list.append((feed_item_info['CP'] - RDP_list[counter]))
            dRUP_diet.append(feed_item_info['dRUP'])

            counter+=1

        RDP_diet = []
        RUP_diet = []
        for i, val in enumerate(ration.values()):
            RDP_diet.append(RDP_list[i] * val * 0.01)
            RUP_diet.append(val * RUP_list[i] * dRUP_diet[i])

        TDN_total_actual = TDNtotal * cls.get_TDN_discount(ration_report, body_weight)

        # MP bact calcs
        MP_bact = 0.64 * min(1000 * 0.13 * TDN_total_actual, 1000 * 0.85 * sum(RDP_diet))

        MP_supply = MP_bact + sum(RUP_diet)*0.0001 + 0.4 * 11.8 * DMI_estimate
        return MP_supply

    @classmethod
    def get_Forage_NDF(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        if feed_item_info['type'] == 'Forage':
            forage_NDF_item = feed_item_info['NDF'] * val
        else:
            forage_NDF_item = 0.0
        return forage_NDF_item

    @classmethod
    def get_Forage_NDF_percent(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        if feed_item_info['type'] == 'Forage':
            forage_NDF_percent_item = val / ration_report['nutrient_amount']['dm']
        else:
            forage_NDF_percent_item = 0.0
        return forage_NDF_percent_item


    @classmethod
    def get_Fat(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        fat_item = feed_item_info['EE'] * val
        return fat_item

    @classmethod
    def get_Fat_percentage(cls, val, feed_item_info, ration_report, body_weight):
        """
        
        """
        fat_item_percentage = (feed_item_info['EE'] * val) / ration_report['nutrient_amount']['dm']
        return fat_item_percentage





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
