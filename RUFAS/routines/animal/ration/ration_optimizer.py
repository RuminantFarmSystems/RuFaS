"""
RUFAS: Ruminant Farm Systems Model
File name: ration_NLP.py
Description: Calculates the ration for animals using a Non-Linear
    programming method utilizing the scipy package. The NLP is formulated using
    constraint functions. Note NLP (Non-linear Program) will be used throughout
    descriptions for functions in this file.
Author(s):
    Chris VanKerkhove, cjv47@cornell.edu
    Joseph Waddell, jw2574@cornell.edu
"""
import numpy as np
import random
from scipy.optimize import minimize
from typing import Dict, List, Tuple

from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.ration.user_defined_ration import UserDefinedRationManager as UserDefinedRationManager
udrm = UserDefinedRationManager()

from RUFAS.routines.animal.ration.ration_config import RationConfig

import numpy.typing as npt
from typing import Callable, List
from RUFAS.output_manager import OutputManager
om = OutputManager()

class RationOptimizer:
    """
    Nonlinear programming methods to optimize a ration by comparing feed supply and animal requirements
    
    Constraints are defined here as the animal requirements subtracted from the feed supply (for a given 
        attempted 'solution') 
    The difference is then used in scipy.minimize to ensure that the attempted supply meets the requirements
    If supply meets requirements, then the solution is a 'success'
    
    Unmet requirements are checked here to report to users
    
    """
    def __init__(self):
        """initializes RationOptimizer object"""
        self.cow_cons = []
        self.heifer_cons = []
        self.constraint_functions = []

    def set_constraints(self, arguments):
        # establishing the constraints of the NLP
        self.constraint_functions = [
            self.total_energy,
            self.NEmact_constraint,
            self.NEl_constraint,
            self.NEgact_constraint,
            self.calcium_constraint,
            self.phosphorus_constraint,
            self.protein_constraint,
            self.NDF_constraint_lower,
            self.NDF_constraint_upper,
            self.forage_NDF_constraint,
            self.fat_constraint,
            self.DMI_constraint_upper,
            self.DMI_constraint_lower
        ]
        
        self.cow_cons = [{'type': 'ineq', 'fun': func} for func in self.constraint_functions]
        """ constraints for lactating cows """
        self.cow_cons=[{'type': 'ineq', 'fun': func, 'args': arguments} for func in self.constraint_functions]

        self.heifer_cons = [cons for cons in self.cow_cons if cons['fun'] not in [self.total_energy, self.NEl_constraint, self.DMI_constraint_lower]]
        """constraints for animals that are not lactating cows """


    @staticmethod
    def list_reconfig(list):
        """
        Helper function that takes an input of a list and returns that list with
        each value occuring a total of 3 times consecutively. This method is
        required for matching the decision variables to one of the three energy
        constraint.

        Args:
            list: A list of values
        """
        list_reconfig = []
        for i in list:
            list_reconfig.append(i)
            list_reconfig.append(i)
            list_reconfig.append(i)
        return list_reconfig


    def objective(self, x, ration_config):
        """
        Sets up the objective function in the optimize function for the non-linear
        program. Whenever the paramert x is used, it refers to the "decision vetor
        of the NLP" which means it is a list of solutions where each value in the
        list corresponds to the amount of a given feed (kg) in the formulated diet.
        The goal of this NLP is to minimize the cost of all feeds while satisfying
        all "constraints", which just means the diet fulfills the average nutrient
        requirements in the pen.

        Args:
            x: The decision vector of the NLP
        """
        # return sum(np.multiply(x, ration_config['price']))
        return sum(np.multiply(x, ration_config.price))


    def total_energy(self, x, ration_config):
        """
        Sets up the RHS multipliers for the maintenance and activity requirements
        satisfied by the feed. Each equation has a reference to the respective
        calculation in the pseudo code. 
        The global variables are a temporary measure until the completion of the ration refactor

        Args:
            x: The decision vector of the NLP
        """
        # global MEact
        # global TDNact
        # global DEact
        dry_matter_intake = sum(x)
        # Dietary TDN content, kg
        TotalTDN = sum(np.multiply(x, ration_config.TDN))
        TotalTDN = np.multiply(TotalTDN, 0.01)
        # [A.Cow.E.1]-[A.Heifer.E.1]
        # TDN concentration, %
        if dry_matter_intake != 0:
            TDNconc = (TotalTDN / dry_matter_intake) * 100
        else:
            TDNconc = 0
        somatic_BW = ration_config.BW * 0.96
        # [A.Cow.E.2]-[A.Heifer.E.2]
        # The amount of intake needed to meet the maintenance requirement, dimensionless
        if TotalTDN < (0.035 * ration_config.BW ** 0.75):
            DMI_to_maint = 1
        else:
            DMI_to_maint = (TotalTDN / (0.035 * somatic_BW ** 0.75))
        # [A.Cow.E.3]-[A.Heifer.E.3]
        # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
        if TDNconc < 60:
            Discount = 1
        else:
            Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
        ration_config.Discount = Discount
        # [A.Cow.E.4]-[A.Heifer.E.4]
        # Actual TDN content of feed i, %
        ration_config.TDNact = np.multiply(ration_config.TDN, Discount)
        # [A.Cow.E.5]-[A.Heifer.E.5]
        # Actual digestible energy of feed i, Mcal/kg
        DEact = np.multiply(ration_config.DE, Discount)
        ration_config.DEact = DEact
        # [A.Cow.E.6]-[A.Heifer.E.6]
        # Actual metabolizable energy of feed i, Mcal/kg
        MEact = []
        for i in range(len(DEact)):
            if ration_config.type[i] == 'Mineral':
                MEact.append(0)
            elif ration_config.is_fat[i] == 1:
                MEact.append(ration_config.DE[i])
            elif ration_config.EE[i] >= 3:
                MEact.append(1.01 * DEact[i] - 0.45 + 0.0046 * (ration_config.EE[i] - 3))
            else:
                MEact.append(1.01 * DEact[i] - 0.45)
        ration_config.MEact = MEact
        # [A.Cow.E.8]-[A.Heifer.E.8]
        # Actual net energy for maintenance of feed i, Mcal/kg
        NEm_act = []
        for i in range(len(MEact)):
            if ration_config.is_fat[i] == 1:
                NEm_act.append(0.8 * MEact[i])
            else:
                NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i] ** 2 + 0.0105 * MEact[i] ** 3 - 1.12)
        ration_config.NEm_act = NEm_act

        # Actual net energy for lactation of feed i, Mcal/kg
        NElact = []
        # [A.Cow.E.7]-[A.Heifer.E.7]
        for i in range(len(MEact)):
            if ration_config.type[i] == 'Mineral':
                NElact.append(0)
            elif ration_config.is_fat[i] == 1:
                NElact.append(0.8 * DEact[i])
            elif ration_config.EE[i] >= 3:
                NElact.append(0.703 * MEact[i] - 0.19 + ((0.097 * MEact[i] + 0.19) / 97) * (ration_config.EE[i] - 3))
            else:
                NElact.append(0.703 * MEact[i] - 0.19)
        ration_config.NElact = NElact

        # Actual net energy for growth of feed i, Mcal/kg
        NEgact = []
        # [A.Cow.E.9]-[A.Heifer.E.9]
        for i in range(len(MEact)):
            if ration_config.type[i] == 'Mineral':
                NEgact.append(0)
            elif ration_config.is_fat[i] == 1:
                NEgact.append(0.55 * MEact[i])
            else:
                NEgact.append(1.42 * MEact[i] - 0.174 * MEact[i] ** 2 + 0.0122 * MEact[i] ** 3 - 1.65)
        ration_config.NEgact = NEgact

        NEl_constraint= sum(np.multiply(x, ration_config.NElact)) 
        NEm_act_constraint = (sum(np.multiply(x, ration_config.NEm_act)))
        NEg_constraint = sum(np.multiply(x, ration_config.NEgact))

        all_req = ration_config.NEl + ration_config.NEg + ration_config.NEmaint + ration_config.NEa + ration_config.NEpreg
        return max(NEm_act_constraint, NEl_constraint, NEg_constraint) - all_req
    

    def NEmact_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for the maintenance and activity requirements
        satisfied by the feed. Each equation has a reference to the respective
        calculation in the pseudo code. The global variables defined in the begining
        of this function are used in future functions.

        Args:
            x: The decision vector of the NLP
        """
        # global MEact
        # global TDNact
        # global DEact
        # DMI calculated by the NLP
        dry_matter_intake = sum(x)
        # Dietary TDN content, kg
        TotalTDN = sum(np.multiply(x, ration_config.TDN))
        TotalTDN = np.multiply(TotalTDN, 0.01)
        # [A.Cow.E.1]-[A.Heifer.E.1]
        # TDN concentration, %
        if dry_matter_intake != 0:
            TDNconc = (TotalTDN / dry_matter_intake) * 100
        else:
            TDNconc = 0
        SBW = ration_config.BW * 0.96
        # [A.Cow.E.2]-[A.Heifer.E.2]
        # The amount of intake needed to meet the maintenance requirement, dimensionless
        if TotalTDN < (0.035 * ration_config.BW ** 0.75):
            DMI_to_maint = 1
        else:
            DMI_to_maint = (TotalTDN / (0.035 * SBW ** 0.75))
        # [A.Cow.E.3]-[A.Heifer.E.3]
        # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
        if TDNconc < 60:
            ration_config.Discount = 1
        else:
            ration_config.Discount = (TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))) / TDNconc
        # [A.Cow.E.4]-[A.Heifer.E.4]
        # Actual TDN content of feed i, %
        ration_config.TDNact = np.multiply(ration_config.TDN, ration_config.Discount)
        # [A.Cow.E.5]-[A.Heifer.E.5]
        # Actual digestible energy of feed i, Mcal/kg
        DEact = np.multiply(ration_config.DE, ration_config.Discount)
        ration_config.DEact = DEact 
        # [A.Cow.E.6]-[A.Heifer.E.6]
        # Actual metabolizable energy of feed i, Mcal/kg
        if not ration_config.MEact:
            MEact = []
            for i in range(len(DEact)):
                if ration_config.type[i] == 'Mineral':
                    MEact.append(0)
                elif ration_config.is_fat[i] == 1:
                    MEact.append(ration_config.DE[i])
                elif ration_config.EE[i] >= 3:
                    MEact.append(1.01 * DEact[i] - 0.45 + 0.0046 * (ration_config.EE[i] - 3))
                else:
                    MEact.append(1.01 * DEact[i] - 0.45)
            ration_config.MEact = MEact
        # [A.Cow.E.8]-[A.Heifer.E.8]
        # Actual net energy for maintenance of feed i, Mcal/kg
        if not ration_config.NEm_act:
            NEm_act = []
            for i in range(len(MEact)):
                if ration_config.is_fat[i] == 1:
                    NEm_act.append(0.8 * MEact[i])
                else:
                    NEm_act.append(1.37 * MEact[i] - 0.138 * MEact[i] ** 2 + 0.0105 * MEact[i] ** 3 - 1.12)
            ration_config.NEm_act = NEm_act
        # returning the NEm_act constraint in the NLP
        return (sum(np.multiply(x, ration_config.NEm_act)) - (ration_config.NEmaint + ration_config.NEa))


    def NEl_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for the lactation and pregnancy requirements
        satisfied by each feed. Each calculation has a reference to the respective
        calculation in the pseudocode. Note to eliminate code repetition the global
        variable MEact is used (calculated in NEmact_constraint).

        Args:
            x: The decision vector of the NLP
        """
        # Actual net energy for lactation of feed i, Mcal/kg
        if not ration_config.NElact:
            NElact = []
            # [A.Cow.E.7]-[A.Heifer.E.7]
            for i in range(len(ration_config.MEact)):
                if ration_config.type[i] == 'Mineral':
                    NElact.append(0)
                elif ration_config.is_fat[i] == 1:
                    NElact.append(0.8 * ration_config.DEact[i])
                elif ration_config.EE[i] >= 3:
                    NElact.append(0.703 * ration_config.MEact[i] - 0.19 + ((0.097 * ration_config.MEact[i] + 0.19) / 97) * (ration_config.EE[i] - 3))
                else:
                    NElact.append(0.703 * ration_config.MEact[i] - 0.19)
            ration_config.NElact = NElact
            # returning the NElact constraint in the NLP
        return sum(np.multiply(x, ration_config.NElact)) - (ration_config.NEpreg + ration_config.NEl)


    def NEgact_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for the growth requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Note to eliminate code repetition the global variable MEact is
        used (calculated in NEmact_constraint).

        Args:
            x: The decision vector of the NLP
        """
        # Actual net energy for growth of feed i, Mcal/kg
        if not ration_config.NEgact:
            NEgact = []
            # [A.Cow.E.9]-[A.Heifer.E.9]
            for i in range(len(ration_config.MEact)):
                if ration_config.type[i] == 'Mineral':
                    NEgact.append(0)
                elif ration_config.is_fat[i] == 1:
                    NEgact.append(0.55 * ration_config.MEact[i])
                else:
                    NEgact.append(1.42 * ration_config.MEact[i] - 0.174 * ration_config.MEact[i] ** 2 + 0.0122 * ration_config.MEact[i] ** 3 - 1.65)
            ration_config.NEgact = NEgact
        # returning the NEgact constraint in the NLP
        return sum(np.multiply(x, ration_config.NEgact)) - ration_config.NEg


    def calcium_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for the calcium requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Note the calculated calcium requirement 'C_req' is in grams and
        x is in kg thus the divide by 1000.

        Args:
            x: The decision vector of the NLP
        """
        # Ca digestibility of feed i (proportion of Ca)
        ration_config.dCa = []
        for i in range(len(ration_config.type)):
            if ration_config.type[i] == 'Forage':
                ration_config.dCa.append(.3)
            elif ration_config.type[i] == 'Conc':
                ration_config.dCa.append(.6)
            elif ration_config.type[i] == 'Mineral':
                ration_config.dCa.append(.95)
            else:
                ration_config.dCa.append(0)
        # [A.Cow.E.16]-[A.Heifer.E.16]
        return (sum(np.multiply(x, np.multiply(np.multiply(ration_config.calcium, 0.01), ration_config.dCa))) - (ration_config.C_req / 1000))


    def phosphorus_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for the phosphorus requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Becasue the maintenance requirement contains non-linearity
        properties, that requirement will be calculated in this function. Note the
        calculated phosphorus requirement 'P_req' is in grams and x is in kg thus
        the divide by 1000.

        Args:
            x: The decision vector of the NLP
        """
        # P digestibility of feed i (proportion of P)
        ration_config.dP = []
        for i in range(len(ration_config.type)):
            if ration_config.type[i] == 'Forage':
                ration_config.dP.append(.64)
            elif ration_config.type[i] == 'Conc':
                ration_config.dP.append(.70)
            elif ration_config.type[i] == 'Mineral':
                ration_config.dP.append(0.80)
            else:
                ration_config.dP.append(0)
        return sum(np.multiply(x, np.multiply(np.multiply(ration_config.phosphorus, 0.01), ration_config.dP))) - ((ration_config.P_req) / 1000)


    def protein_constraint(self, x, ration_config):
        """
        Sets up the protein requirement constraint in the NLP. Because part of the
        maintenance requirement for protein contains non-linearity properties, that
        requirement will be calculated in this function. Each calculation has a
        reference to the respective calculation in the pseudocode.

        Args:
            x: The decision vector of the NLP.
        """
        DMI = sum(x)
        # Boolean values to identify if feed is a concentrate
        ration_config.is_conc = []
        for i in range(len(ration_config.type)):
            if ration_config.type[i] == 'Conc':
                ration_config.is_conc.append(1)
            else:
                ration_config.is_conc.append(0)
        # Dietary concentrate percentage (% of DM)
        if DMI != 0:
            PercentConc = (sum(np.multiply(x, ration_config.is_conc)) / DMI) * 100
        else:
            PercentConc = 0
        # [A.Cow.E.10]-[A.Heifer.E.10]
        # Protein passage rate of feed i (%/h)
        Kp = []
        for i in range(len(ration_config.type)):
            if ration_config.type[i] == 'Conc':
                Kp.append(2.904 + 1.375 * (DMI / ration_config.BW) * 100 - 0.02 * PercentConc)
            elif ration_config.type[i] == 'Forage' and ration_config.is_wetforage[i] == 0:
                Kp.append(3.362 + 0.479 * (DMI / ration_config.BW) * 100 - 0.017 * ration_config.NDF[i] - 0.007 * PercentConc)
            elif ration_config.is_wetforage[i] == 1:
                Kp.append(3.054 + 0.614 * (DMI / ration_config.BW) * 100)
            else:
                Kp.append(0)
        # [A.Cow.E.11]-[A.Heifer.E.11]
        # Rumen degradable protein of feed i (% of DM)
        RDP = []
        for i in range(len(ration_config.Kd)):
            if Kp[i] > -ration_config.Kd[i]:
                RDP.append((ration_config.Kd[i] / (ration_config.Kd[i] + Kp[i])) * (ration_config.N_B[i] / 100) * ration_config.CP[i] + (ration_config.N_A[i] / 100) * ration_config.CP[i])
            else:
                RDP.append(0)
        ration_config.RDP = RDP
        # [A.Cow.E.12]-[A.Cow.E.12]
        # Rumen undegradable protein of feed i (% of DM)
        RUP = []
        for i in range(len(ration_config.CP)):
            RUP.append(ration_config.CP[i] - ration_config.RDP[i])
        ration_config.RUP = RUP
        # Dietary actual TDN (kg)
        ration_config.TDNact_diet = sum(np.multiply(x, np.multiply(ration_config.TDNact, 0.01)))
        # Dietary RDP (kg)
        ration_config.RDP_diet = sum(np.multiply(x, np.multiply(ration_config.RDP, 0.01)))
        # [A.Cow.E.13]-[A.Cow.E.13]
        # Metabolizable bacterial protein production (g)
        ration_config.MPbact = 0.64 * min(1000 * .13 * ration_config.TDNact_diet, 1000 * 0.85 * ration_config.RDP_diet)
        # [A.Cow.E.14]-[A.Heifer.E.14]
        # Dietary RUP (kg)
        ration_config.RUP_diet = sum(np.multiply(x, np.multiply(np.multiply(ration_config.RUP, 0.01), np.multiply(ration_config.dRUP, 0.01))))
        # [A.Cow.E.15]
        # Total metabolizable protein supply
        ration_config.MP_supply = ration_config.MPbact + ration_config.RUP_diet + 0.4 * 11.8 * DMI

        return (ration_config.MP_supply - (ration_config.MP_req / 1000))


    def NDF_constraint_lower(self, x, ration_config):
        """
        Sets up the RHS multipliers for each feed to instill an overall NDF percent
        constraint. This is a lower bound constraint on overall NDF percent.

        Args:
            x: The decision vector of the NLP
        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(x)
        if DMI != 0:
            return (sum(np.multiply(x, ration_config.NDF)) / DMI) - 25


    def NDF_constraint_upper(self, x, ration_config):
        """
        Sets up the RHS multipliers for each feed to instill an overall NDF percent
        constraint. This is an upper bound constraint on overall NDF percent.

        Args:
            x: The decision vector of the NLP
        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(x)
        if DMI != 0:
            return (-(sum(np.multiply(x, ration_config.NDF)) / DMI) + 45)


    def forage_NDF_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for only FORAGES to instill a NDF percent across
        forages constraint. This is a lower bound constraint on NDF percent across
        forages.

        Args:
            x: The decision vector of the NLP
        """
        # From E/D: OTHER REQUIREMENTS
        is_forage = []
        for i in range(len(ration_config.type)):
            if ration_config.type[i] == 'Forage':
                is_forage.append(1)
            else:
                is_forage.append(0)
        ration_config.is_forage = is_forage
        DMI = sum(x)
        if DMI != 0:
            return (sum(np.multiply(x, np.multiply(ration_config.NDF, ration_config.is_forage))) / DMI) - 15


    def fat_constraint(self, x, ration_config):
        """
        Sets up the RHS multipliers for each feed to instill an overall fat percent
        constraint. This is an upper bound constraint on over fat percent.

        Args:
            x: The decision vector of the NLP
        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(x)
        if DMI != 0:
            return -(sum(np.multiply(x, ration_config.EE)) / DMI) + 7


    def DMI_constraint_lower(self, x, ration_config):
        """
        Constraint in place to make sure the sum of all the feeds in the ration is
        greater than the DMI_est + 20% calculated in the requirements

        Args:
            x: The decision vector of the NLP
        """
        return (sum(x)) - (ration_config.DMIest*(1-AnimalModuleConstants.DMI_CONSTRAINT_PERCENT))


    def DMI_constraint_upper(self, x, ration_config):
        """
        Constraint in place to make sure the sum of all the feeds in the ration is
        less than the DMI_est + 20% calculated in the requirements.

        Args:
            x: The decision vector of the NLP
        """
        return -(sum(x)) + (ration_config.DMIest*(1+AnimalModuleConstants.DMI_CONSTRAINT_PERCENT))

    def energy_req_limit_constraint(self, x, ration_config):
        """
        Constraint that limits each feed to only satisfying a single energy constraint
        (NEmact, NEgact, or NEl).

        Args:
            x: The decision vector of the NLP
        """
        n = len(ration_config.price) / 3
        list = []
        for i in range(int(n)):
            a = i * 3
            list.append(x[a] * x[a + 1])
            list.append(x[a] * x[a + 2])
            list.append(x[a + 1] * x[a + 2])
        return -sum(list)

    def get_ration_vals(self, x, ration_config):
        """
        Function that calculates and retrieves ration values used throughout the
        ration.

        Args:
            x: the decision vector of the NLP (should be a completed ration)
        """
        #ration vals (subject to adding other ration vals)
        ME_tot = sum(np.multiply(x, ration_config.MEact))
        ration_vals = {'ME_tot': ME_tot}
        return ration_vals

    @classmethod
    def make_user_bounds(cls, ration_percents: Dict, DMIest: float) -> List[Tuple[float, float]]:
        """
        Calculates user bounds for optimize function

        Uses udrm object to get tolerance, e.g. the +/- percentage allowed around those.
        Returns a list of each key/value pair three times, but divided by three
            This return in triplicate is necessary for the scipy.minimize function,
            which requires the decision vector in this shape
        
        Parameters
        ----------
        ration_percents: Dict
            keys are feed IDs, values are percent of DMI
        DMIest: float
            average estimated DMI for pen
        Returns
        -------
        List
            List of each bound, divided by three and reported in triplicate for scipy.minimize function
        """
        tribounds = []
        udr_tolerance = udrm.tolerance
        ration_key_list = sorted([int(key) for key in ration_percents.keys()])
        for key in ration_key_list:
            target_lower = ration_percents[str(key)] / \
                100 * (1 - udr_tolerance) * (DMIest * 1.1 + 0.0001)
            target_upper = ration_percents[str(key)] / \
                100 * (1 + udr_tolerance) * (DMIest * 1.1 + 0.0001)
            targetbounds = (max(0.0, (target_lower)/3), (target_upper)/3)
            tribounds.append(targetbounds)
            tribounds.append(targetbounds)
            tribounds.append(targetbounds)
        return tribounds


    def optimize(self, animal_combination, available_feeds: Dict, ration_config) -> None:
        """
        Calls the objective function and constraint functions and formulates
        the inputs for the minimization function. Returns the optimized solution
        as a dictionary with feed keys corresponding to their ration (kg).

        Parameters
        ----------
        animal_combination : Pen.AnimalCombination
            The animal combination to optimize the ration for.
        available_feeds: Dict 
            a DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py
        ration_config: 
        
        Returns
        -------
        OptimizeResult object from scipy package

        """
        arguments = (ration_config,)
        self.set_constraints(arguments = arguments)
        n = len(ration_config.price)
        x0 = [1]
        for i in range(n-1):
            x0.append(random.random() * 10)
        # OPTIMIZE:
        # establishing the bounds of the NLP

        # Dividing limit by 3 for tri-decision variables for farm grown feeds
        if udrm.udr_or_not:
            bnds = self.make_user_bounds(UserDefinedRationManager.ration_to_use(animal_combination, available_feeds), ration_config.DMIest)
            x0 = [np.mean(bnd) for bnd in bnds]
        else:    
            bnds = []
            bnds = [(0, (lim / 3) + 0.0001) for lim in ration_config.limit]
        if udrm.udr_or_not:
            if str(animal_combination) in ['AnimalCombination.LAC_COW']:
                usermod = minimize(self.objective, x0, method='SLSQP', bounds=bnds, constraints=self.cow_cons, args = arguments)
            else:
                usermod = minimize(self.objective, x0, method='SLSQP', bounds=bnds, constraints=self.heifer_cons, args = arguments)
            return usermod
        # TODO: Put AnimalCombination enum in a separate file and import it here to avoid circular import
        elif str(animal_combination) in ['AnimalCombination.LAC_COW']:
            return minimize(self.objective, x0, method='SLSQP', bounds=bnds, constraints=self.cow_cons, args = arguments)
        elif str(animal_combination) in ['AnimalCombination.GROWING', 'AnimalCombination.CLOSE_UP',
                                        'AnimalCombination.GROWING_AND_CLOSE_UP']:
            return minimize(self.objective, x0, method='SLSQP', bounds=bnds, constraints=self.heifer_cons, args = arguments)
        else:
            raise ValueError("Invalid animal combination: " + str(animal_combination))


    def attempt_optimization(self, requirements, available_feeds, animal_combination):
        """
        Function that sets up the nutrients and requirements lists into structured
        inputs for the non-linear program and calls the optimization function.

        Args:
            requirements: object of class Requirements
            available_feeds: object of class AvailableFeeds
            animal_combination: one of the animal combinations specified in the AnimalCombination enum
        """
        price = self.list_reconfig(available_feeds['price'])
        TDN = self.list_reconfig(available_feeds['TDN'])
        DE = self.list_reconfig(available_feeds['DE'])
        EE = self.list_reconfig(available_feeds['EE'])
        is_fat = self.list_reconfig(available_feeds['is_fat'])
        calcium = self.list_reconfig(available_feeds['calcium'])
        phosphorus = self.list_reconfig(available_feeds['phosphorus'])
        NDF = self.list_reconfig(available_feeds['NDF'])
        feed_type = self.list_reconfig(available_feeds['type'])
        is_wetforage = self.list_reconfig(available_feeds['is_wetforage'])
        Kd = self.list_reconfig(available_feeds['Kd'])
        N_A = self.list_reconfig(available_feeds['N_A'])
        N_B = self.list_reconfig(available_feeds['N_B'])
        CP = self.list_reconfig(available_feeds['CP'])
        dRUP = self.list_reconfig(available_feeds['dRUP'])
        # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
        if str(animal_combination) in ['AnimalCombination.LAC_COW']:
            limit = self.list_reconfig(available_feeds['lactating_cow_limit'])
            lactating = True
        else:
            limit = self.list_reconfig(available_feeds['dry_cow_limit'])
            lactating = False
        ration_config = RationConfig(price, requirements.NEmaint, requirements.NEa, requirements.NEpreg,
                        requirements.NEl, requirements.NEg, requirements.MP_req,
                        requirements.Ca_req, requirements.P_req,
                        TDN, DE, EE, is_fat, requirements.avg_BW, calcium, phosphorus, NDF,
                        feed_type, is_wetforage, Kd, N_A, N_B, CP, dRUP, limit, lactating,
                        DMIest_=requirements.DMIest)
        # try block for catching scipy SLSQP error
        i = 0
        count = 0
        while i < 1:
            try:
                solution = self.optimize(animal_combination, available_feeds, ration_config)
            except Exception as e:
                i -= 1
                info_map = {"class": "RationOptimizer", 
                            "function": self.attempt_optimization.__name__,
                            }
                om.add_error('SLSQP error', 'whoops', info_map)
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
            ration_config = None
        else:
            ration_vals = self.get_ration_vals(solution.x, ration_config)
        return solution, ration_vals, ration_config


    def is_constraint_violated(self, solution_x: npt.NDArray, constraint: dict[str, Callable], ration_config) -> bool:
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
            result = constraint['fun'](solution_x, ration_config)
            if constraint['type'] == 'ineq' and result < 0:
                return True
            elif constraint['type'] == 'eq' and not np.isclose(result, 0):
                return True
            else:
                return False


    def find_failed_constraints(self, solution_x: npt.NDArray, constraints: List[dict[str,Callable]], ration_config) -> List[dict[str,Callable]]:
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
            return list(filter(lambda c: self.is_constraint_violated(solution_x, c, ration_config), constraints))

