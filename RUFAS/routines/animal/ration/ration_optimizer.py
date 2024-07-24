import random
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import numpy.typing as npt
from scipy.optimize import OptimizeResult, minimize

from RUFAS.enums import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.animal_typed_dicts import AvailableFeedsTypedDict
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements
from RUFAS.routines.animal.ration.ration_config import RationConfig
from RUFAS.routines.animal.ration.user_defined_ration import (
    UserDefinedRationManager as UserDefinedRationManager,
)

om = OutputManager()
udrm = UserDefinedRationManager()


class RationOptimizer:
    """
    Nonlinear programming methods to optimize a ration by comparing feed supply and animal requirements

    Constraints are defined here as the animal requirements subtracted from the feed supply (for a given
        attempted 'solution')
    The difference is then used in scipy.minimize to ensure that the attempted supply meets the requirements
    If supply meets requirements, then the solution is a 'success'

    Unmet requirements are checked here to report to users

    """

    def __init__(self) -> None:
        """initializes RationOptimizer object"""

        self.constraint_functions: List[Callable[[Any, Any], float]] = []
        self.cow_constraints: List[Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str] | str] = []
        self.heifer_constraints: List[Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str] | str] = []

    def set_constraints(self, arguments: Tuple[RationConfig]) -> None:
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
            self.DMI_constraint_lower,
        ]

        self.cow_constraints = [{"type": "ineq", "fun": func, "args": arguments} for func in self.constraint_functions]

        self.heifer_constraints = [
            cons for cons in self.cow_constraints if cons["fun"] not in [self.total_energy, self.NEl_constraint]
        ]

    @staticmethod
    def objective(decision_vector: npt.NDArray[np.float64], ration_config: RationConfig) -> float:
        """
        Sets up the objective function in the optimize function for the non-linear
        program. Whenever the paramert x is used, it refers to the "decision vetor
        of the NLP" which means it is a list of solutions where each value in the
        list corresponds to the amount of a given feed (kg) in the formulated diet.
        The goal of this NLP is to minimize the cost of all feeds while satisfying
        all "constraints", which just means the diet fulfills the average nutrient
        requirements in the pen.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        return float(sum(np.multiply(decision_vector, ration_config.price_list)))

    # fmt: off
    @staticmethod
    def total_energy(  # noqa
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        # fmt: on
        """
        Sets up the RHS multipliers for the sum of the lactation, pregnancy, maintenance, and activity requirements
        satisfied by the feed. Each equation has a reference to the respective
        calculation in the pseudo code.
        The global variables are a temporary measure until the completion of the ration refactor

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        dry_matter_intake = sum(decision_vector)
        # Dietary TDN content, kg
        TotalTDN = sum(np.multiply(decision_vector, ration_config.TDN_list))
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
        if TotalTDN < (0.035 * ration_config.BW**0.75):
            DMI_to_maint = 1
        else:
            DMI_to_maint = TotalTDN / (0.035 * somatic_BW**0.75)
        # [A.Cow.E.3]-[A.Heifer.E.3]
        # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
        if TDNconc < 60:
            Discount = 1.0
        else:
            Discount = (
                TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))
            ) / TDNconc
        ration_config.Discount = Discount
        # [A.Cow.E.4]-[A.Heifer.E.4]
        # Actual TDN content of feed i, %
        ration_config.TDNact_list = np.multiply(ration_config.TDN_list, Discount)
        # [A.Cow.E.5]-[A.Heifer.E.5]
        # Actual digestible energy of feed i, Mcal/kg
        ration_config.DEact_list = np.multiply(ration_config.DE_list, Discount)
        # [A.Cow.E.6]-[A.Heifer.E.6]
        # Actual metabolizable energy of feed i, Mcal/kg
        ration_config.MEact_list = []
        for i in range(len(ration_config.DEact_list)):
            if ration_config.feed_type_list[i] == "Mineral":
                ration_config.MEact_list.append(0.0)
            elif ration_config.is_fat_list[i] is True:
                ration_config.MEact_list.append(ration_config.DE_list[i])
            elif ration_config.EE_list[i] >= 3:
                ration_config.MEact_list.append(
                    1.01 * ration_config.DEact_list[i]
                    - 0.45
                    + 0.0046 * (ration_config.EE_list[i] - 3)
                )
            else:
                ration_config.MEact_list.append(
                    1.01 * ration_config.DEact_list[i] - 0.45
                )
        # [A.Cow.E.8]-[A.Heifer.E.8]
        # Actual net energy for maintenance of feed i, Mcal/kg
        ration_config.NEm_act_list = []
        for i in range(len(ration_config.MEact_list)):
            if ration_config.is_fat_list[i] is True:
                ration_config.NEm_act_list.append(0.8 * ration_config.MEact_list[i])
            else:
                ration_config.NEm_act_list.append(
                    1.37 * ration_config.MEact_list[i]
                    - 0.138 * ration_config.MEact_list[i] ** 2
                    + 0.0105 * ration_config.MEact_list[i] ** 3
                    - 1.12
                )

        # Actual net energy for lactation of feed i, Mcal/kg
        ration_config.NElact_list = []
        # [A.Cow.E.7]-[A.Heifer.E.7]
        for i in range(len(ration_config.MEact_list)):
            if ration_config.feed_type_list[i] == "Mineral":
                ration_config.NElact_list.append(0)
            elif ration_config.is_fat_list[i] is True:
                ration_config.NElact_list.append(0.8 * ration_config.DEact_list[i])
            elif ration_config.EE_list[i] >= 3:
                ration_config.NElact_list.append(
                    0.703 * ration_config.MEact_list[i]
                    - 0.19
                    + ((0.097 * ration_config.MEact_list[i] + 0.19) / 97)
                    * (ration_config.EE_list[i] - 3)
                )
            else:
                ration_config.NElact_list.append(
                    0.703 * ration_config.MEact_list[i] - 0.19
                )

        # Actual net energy for growth of feed i, Mcal/kg
        ration_config.NEgact_list = []
        # [A.Cow.E.9]-[A.Heifer.E.9]
        for i in range(len(ration_config.MEact_list)):
            if ration_config.feed_type_list[i] == "Mineral":
                ration_config.NEgact_list.append(0)
            elif ration_config.is_fat_list[i] is True:
                ration_config.NEgact_list.append(0.55 * ration_config.MEact_list[i])
            else:
                ration_config.NEgact_list.append(
                    1.42 * ration_config.MEact_list[i]
                    - 0.174 * ration_config.MEact_list[i] ** 2
                    + 0.0122 * ration_config.MEact_list[i] ** 3
                    - 1.65
                )

        NEl_constraint = sum(np.multiply(decision_vector, ration_config.NElact_list))
        NEm_act_constraint = sum(
            np.multiply(decision_vector, ration_config.NEm_act_list)
        )
        NEg_constraint = sum(np.multiply(decision_vector, ration_config.NEgact_list))

        all_req = (
            ration_config.NEl_requirement
            + ration_config.NEg_requirement
            + ration_config.NEmaint_requirement
            + ration_config.NEa_requirement
            + ration_config.NEpreg_requirement
        )
        return float(max(NEm_act_constraint, NEl_constraint, NEg_constraint) - all_req)

    # fmt: off
    @staticmethod
    def NEmact_constraint(  # noqa
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        # fmt: on
        """
        Sets up the RHS multipliers for the maintenance and activity requirements
        satisfied by the feed. Each equation has a reference to the respective
        calculation in the pseudo code. The global variables defined in the begining
        of this function are used in future functions.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # DMI calculated by the NLP
        dry_matter_intake = sum(decision_vector)
        # Dietary TDN content, kg
        TotalTDN = sum(np.multiply(decision_vector, ration_config.TDN_list))
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
        if TotalTDN < (0.035 * ration_config.BW**0.75):
            DMI_to_maint = 1
        else:
            DMI_to_maint = TotalTDN / (0.035 * SBW**0.75)
        # [A.Cow.E.3]-[A.Heifer.E.3]
        # TDN discount, TDN digestibility decrease caused by DMI and TDNconc
        if TDNconc < 60:
            ration_config.Discount = 1.0
        else:
            ration_config.Discount = (
                TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))
            ) / TDNconc
        # [A.Cow.E.4]-[A.Heifer.E.4]
        # Actual TDN content of feed i, %
        ration_config.TDNact_list = np.multiply(
            ration_config.TDN_list, ration_config.Discount
        )
        # [A.Cow.E.5]-[A.Heifer.E.5]
        # Actual digestible energy of feed i, Mcal/kg
        ration_config.DEact_list = np.multiply(
            ration_config.DE_list, ration_config.Discount
        )
        # [A.Cow.E.6]-[A.Heifer.E.6]
        # Actual metabolizable energy of feed i, Mcal/kg
        if hasattr(ration_config, "MEact_list"):
            ration_config.MEact_list = []
            for i in range(len(ration_config.DEact_list)):
                if ration_config.feed_type_list[i] == "Mineral":
                    ration_config.MEact_list.append(0.0)
                elif ration_config.is_fat_list[i] is True:
                    ration_config.MEact_list.append(ration_config.DE_list[i])
                elif ration_config.EE_list[i] >= 3:
                    ration_config.MEact_list.append(
                        1.01 * ration_config.DEact_list[i]
                        - 0.45
                        + 0.0046 * (ration_config.EE_list[i] - 3)
                    )
                else:
                    ration_config.MEact_list.append(
                        1.01 * ration_config.DEact_list[i] - 0.45
                    )
        # [A.Cow.E.8]-[A.Heifer.E.8]
        # Actual net energy for maintenance of feed i, Mcal/kg
        if not ration_config.NEm_act_list:
            ration_config.NEm_act_list = []
            for i in range(len(ration_config.MEact_list)):
                if ration_config.is_fat_list[i] is True:
                    ration_config.NEm_act_list.append(0.8 * ration_config.MEact_list[i])
                else:
                    ration_config.NEm_act_list.append(
                        1.37 * ration_config.MEact_list[i]
                        - 0.138 * ration_config.MEact_list[i] ** 2
                        + 0.0105 * ration_config.MEact_list[i] ** 3
                        - 1.12
                    )
        # returning the NEm_act constraint in the NLP
        return float(sum(np.multiply(decision_vector, ration_config.NEm_act_list)) - (
            ration_config.NEmaint_requirement + ration_config.NEa_requirement
        ))

    @staticmethod
    def NEl_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for the lactation and pregnancy requirements
        satisfied by each feed. Each calculation has a reference to the respective
        calculation in the pseudocode. Note to eliminate code repetition the global
        variable MEact is used (calculated in NEmact_constraint).

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # Actual net energy for lactation of feed i, Mcal/kg
        if not ration_config.NElact_list:
            ration_config.NElact_list = []
            # [A.Cow.E.7]-[A.Heifer.E.7]
            for i in range(len(ration_config.MEact_list)):
                if ration_config.feed_type_list[i] == "Mineral":
                    ration_config.NElact_list.append(0)
                elif ration_config.is_fat_list[i] is True:
                    ration_config.NElact_list.append(0.8 * ration_config.DEact_list[i])
                elif ration_config.EE_list[i] >= 3:
                    ration_config.NElact_list.append(
                        0.703 * ration_config.MEact_list[i]
                        - 0.19
                        + ((0.097 * ration_config.MEact_list[i] + 0.19) / 97)
                        * (ration_config.EE_list[i] - 3)
                    )
                else:
                    ration_config.NElact_list.append(
                        0.703 * ration_config.MEact_list[i] - 0.19
                    )
            # returning the NElact constraint in the NLP
        return float(sum(np.multiply(decision_vector, ration_config.NElact_list)) - (
            ration_config.NEpreg_requirement + ration_config.NEl_requirement
        ))

    @staticmethod
    def NEgact_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for the growth requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Note to eliminate code repetition the global variable MEact is
        used (calculated in NEmact_constraint).

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # Actual net energy for growth of feed i, Mcal/kg
        if not ration_config.NEgact_list:
            ration_config.NEgact_list = []
            # [A.Cow.E.9]-[A.Heifer.E.9]
            for i in range(len(ration_config.MEact_list)):
                if ration_config.feed_type_list[i] == "Mineral":
                    ration_config.NEgact_list.append(0.0)
                elif ration_config.is_fat_list[i] is True:
                    ration_config.NEgact_list.append(0.55 * ration_config.MEact_list[i])
                else:
                    ration_config.NEgact_list.append(
                        1.42 * ration_config.MEact_list[i]
                        - 0.174 * ration_config.MEact_list[i] ** 2
                        + 0.0122 * ration_config.MEact_list[i] ** 3
                        - 1.65
                    )
        # returning the NEgact constraint in the NLP
        return float(
            sum(np.multiply(decision_vector, ration_config.NEgact_list))
            - ration_config.NEg_requirement
        )

    @staticmethod
    def calcium_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for the calcium requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Note the calculated calcium requirement 'C_req' is in grams and
        x is in kg thus the divide by 1000.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # Ca digestibility of feed i (proportion of Ca)
        ration_config.dCa_list = []
        for i in range(len(ration_config.feed_type_list)):
            if ration_config.feed_type_list[i] == "Forage":
                ration_config.dCa_list.append(0.3)
            elif ration_config.feed_type_list[i] == "Conc":
                ration_config.dCa_list.append(0.6)
            elif ration_config.feed_type_list[i] == "Mineral":
                ration_config.dCa_list.append(0.95)
            else:
                ration_config.dCa_list.append(0.0)
        # [A.Cow.E.16]-[A.Heifer.E.16]
        return float(sum(
            np.multiply(
                decision_vector,
                np.multiply(
                    np.multiply(ration_config.calcium_list, 0.01),
                    ration_config.dCa_list,
                ),
            )
        ) - (ration_config.C_requirement / 1000))

    @staticmethod
    def phosphorus_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for the phosphorus requirements satisfied by each
        feed. Each calculation has a reference to the respective calculation in the
        pseudocode. Note the calculated phosphorus requirement 'P_requirement' is in grams and the formualted ration is
        reported in kg.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # P digestibility of feed i (proportion of P)
        ration_config.dP_list = []
        for i in range(len(ration_config.feed_type_list)):
            if ration_config.feed_type_list[i] == "Forage":
                ration_config.dP_list.append(0.64)
            elif ration_config.feed_type_list[i] == "Conc":
                ration_config.dP_list.append(0.70)
            elif ration_config.feed_type_list[i] == "Mineral":
                ration_config.dP_list.append(0.80)
            else:
                ration_config.dP_list.append(0.0)
        return float(sum(
            np.multiply(
                decision_vector,
                np.multiply(
                    np.multiply(ration_config.phosphorus_list, 0.01),
                    ration_config.dP_list,
                ),
            )
        ) - (ration_config.P_requirement * GeneralConstants.GRAMS_TO_KG))

    # fmt: off
    @staticmethod
    def protein_constraint(  # noqa
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        # fmt: on
        """
        Sets up the protein requirement constraint in the NLP. Because part of the
        maintenance requirement for protein contains non-linearity properties, that
        requirement will be calculated in this function. Each calculation has a
        reference to the respective calculation in the pseudocode.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        DMI = sum(decision_vector)
        # Boolean values to identify if feed is a concentrate
        ration_config.is_conc_list = []
        for i in range(len(ration_config.feed_type_list)):
            if ration_config.feed_type_list[i] == "Conc":
                ration_config.is_conc_list.append(1)
            else:
                ration_config.is_conc_list.append(0)
        # Dietary concentrate percentage (% of DM)
        if DMI != 0:
            PercentConc = (
                sum(np.multiply(decision_vector, ration_config.is_conc_list)) / DMI
            ) * 100
        else:
            PercentConc = 0
        # [A.Cow.E.10]-[A.Heifer.E.10]
        # Protein passage rate of feed i (%/h)
        Kp = []
        for i in range(len(ration_config.feed_type_list)):
            if ration_config.feed_type_list[i] == "Conc":
                Kp.append(
                    2.904 + 1.375 * (DMI / ration_config.BW) * 100 - 0.02 * PercentConc
                )
            elif (
                ration_config.feed_type_list[i] == "Forage"
                and ration_config.is_wetforage_list[i] is False
            ):
                Kp.append(
                    3.362
                    + 0.479 * (DMI / ration_config.BW) * 100
                    - 0.017 * ration_config.NDF_list[i]
                    - 0.007 * PercentConc
                )
            elif ration_config.is_wetforage_list[i] is True:
                Kp.append(3.054 + 0.614 * (DMI / ration_config.BW) * 100)
            else:
                Kp.append(0)
        # [A.Cow.E.11]-[A.Heifer.E.11]
        # Rumen degradable protein of feed i (% of DM)
        ration_config.RDP_list = []
        for i in range(len(ration_config.Kd_list)):
            if Kp[i] > -ration_config.Kd_list[i]:
                ration_config.RDP_list.append(
                    (ration_config.Kd_list[i] / (ration_config.Kd_list[i] + Kp[i]))
                    * (ration_config.N_B_list[i] / 100)
                    * ration_config.CP_list[i]
                    + (ration_config.N_A_list[i] / 100) * ration_config.CP_list[i]
                )
            else:
                ration_config.RDP_list.append(0)
        # [A.Cow.E.12]-[A.Cow.E.12]
        # Rumen undegradable protein of feed i (% of DM)
        ration_config.RUP_list = []
        for i in range(len(ration_config.CP_list)):
            ration_config.RUP_list.append(
                ration_config.CP_list[i] - ration_config.RDP_list[i]
            )
        # Dietary actual TDN (kg)
        ration_config.TDNact_diet = sum(
            np.multiply(decision_vector, np.multiply(ration_config.TDNact_list, 0.01))
        )
        # Dietary RDP (kg)
        ration_config.RDP_diet = sum(
            np.multiply(decision_vector, np.multiply(ration_config.RDP_list, 0.01))
        )
        # [A.Cow.E.13]-[A.Cow.E.13]
        # Metabolizable bacterial protein production (g)
        ration_config.MPbact = float(0.64 * min(
            1000 * 0.13 * ration_config.TDNact_diet,
            1000 * 0.85 * ration_config.RDP_diet,
        ))
        # [A.Cow.E.14]-[A.Heifer.E.14]
        # Dietary RUP (kg)
        ration_config.RUP_diet = sum(
            np.multiply(
                decision_vector,
                np.multiply(
                    np.multiply(ration_config.RUP_list, 0.01),
                    np.multiply(ration_config.dRUP_list, 0.01),
                ),
            )
        )
        # [A.Cow.E.15]
        # Total metabolizable protein supply
        ration_config.MP_supply = (
            ration_config.MPbact + ration_config.RUP_diet + 0.4 * 11.8 * DMI
        )
        return ration_config.MP_supply - (ration_config.MP_requirement / 1000)

    @staticmethod
    def NDF_constraint_lower(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for each feed to instill an overall NDF percent
        constraint. This is a lower bound constraint on overall NDF percent.
        To avoid division by 0 error, returns -1 (fail state) in cases where DMI is equivalent to 0.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(decision_vector)
        if DMI != 0:
            return float((
                sum(np.multiply(decision_vector, ration_config.NDF_list)) / DMI
            ) - 25)
        else:
            return -1.0

    @staticmethod
    def NDF_constraint_upper(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for each feed to instill an overall NDF percent
        constraint. This is an upper bound constraint on overall NDF percent.
        To avoid division by 0 error, returns -1 (fail state) in cases where DMI is equivalent to 0.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(decision_vector)
        if DMI != 0:
            return float((
                -(sum(np.multiply(decision_vector, ration_config.NDF_list)) / DMI) + 45
            ))
        else:
            return -1.0

    @staticmethod
    def forage_NDF_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for only FORAGES to instill a NDF percent across
        forages constraint. This is a lower bound constraint on NDF percent across
        forages.
        To avoid division by 0 error, returns -1 (fail state) in cases where DMI is equivalent to 0.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        # From E/D: OTHER REQUIREMENTS
        ration_config.is_forage_list = []
        for i in range(len(ration_config.feed_type_list)):
            if ration_config.feed_type_list[i] == "Forage":
                ration_config.is_forage_list.append(1)
            else:
                ration_config.is_forage_list.append(0)
        DMI = sum(decision_vector)
        if DMI != 0:
            return (float(
                sum(
                    np.multiply(
                        decision_vector,
                        np.multiply(
                            ration_config.NDF_list, ration_config.is_forage_list
                        ),
                    )
                )
                / DMI
            ) - 15)
        else:
            return -1.0

    @staticmethod
    def fat_constraint(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Sets up the RHS multipliers for each feed to instill an overall fat percent
        constraint. This is an upper bound constraint on over fat percent.
        To avoid division by 0 error, returns -1 (fail state) in cases where DMI is equivalent to 0.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        # From E/D: OTHER REQUIREMENTS
        DMI = sum(decision_vector)
        if DMI != 0:
            return float(-(sum(np.multiply(decision_vector, ration_config.EE_list)) / DMI) + 7)
        else:
            return -1.0

    @staticmethod
    def DMI_constraint_lower(
        decision_vector: npt.NDArray[np.float64], ration_config: RationConfig
    ) -> float:
        """
        Constraint in place to make sure the sum of all the feeds in the ration is
        greater than the DMI_est + 20% calculated in the requirements

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        return float((sum(decision_vector)) - (
            ration_config.DMIest_requirement
            * (1 - AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)
        ))

    @staticmethod
    def DMI_constraint_upper(
        decision_vector: npt.NDArray[np.float64] | List[float], ration_config: RationConfig
    ) -> float:
        """
        Constraint in place to make sure the sum of all the feeds in the ration is
        less than the DMI_est + 20% calculated in the requirements.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float

        """
        return float(-(sum(decision_vector)) + (
            ration_config.DMIest_requirement
            * (1 + AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)
        ))

    @staticmethod
    def get_ration_vals(
        decision_vector: npt.NDArray[np.float64] | List[float], ration_config: RationConfig
    ) -> Dict[str, float]:
        """
        Function that calculates and retrieves ration values used throughout the
        ration.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        Dict[str, float]

        """
        ME_total = sum(np.multiply(decision_vector, ration_config.MEact_list))
        ration_vals = {"ME_total": ME_total}
        return ration_vals

    @staticmethod
    def make_user_bounds(
        ration_percents: Dict[str, float], DMIest: float
    ) -> List[Tuple[float, float]]:
        """
        Calculates user bounds for optimize function

        Uses udrm object to get tolerance, e.g. the +/- percentage allowed around those.
        Returns a list of each key/value pair three times, but divided by three
            This return in triplicate is necessary for the scipy.minimize function,
            which requires the decision vector in this shape
        Parameters
        ----------
        ration_percents: Dict[str, float]
            keys are feed IDs, values are percent of DMI
        DMIest: float
            average estimated DMI for pen

        Returns
        -------
        List
            List of each bound, divided by three and reported in triplicate for scipy.minimize function
        """
        bounds = []
        udr_tolerance = udrm.tolerance
        ration_key_list = sorted([int(key) for key in ration_percents.keys()])
        for key in ration_key_list:
            target_lower = (
                ration_percents[str(key)]
                / 100
                * (1 - udr_tolerance)
                * (DMIest * 1.1 + 0.0001)
            )
            target_upper = (
                ration_percents[str(key)]
                / 100
                * (1 + udr_tolerance)
                * (DMIest * 1.1 + 0.0001)
            )
            targetbounds = (max(0.0, target_lower), target_upper)
            bounds.append(targetbounds)
        return bounds

    def optimize(
        self, animal_combination: AnimalCombination,
        ration_config: RationConfig,
        previous_ration: Dict[str, float | str] | None = None
    ) -> OptimizeResult:
        """
        Calls the objective function and constraint functions and formulates
        the inputs for the minimization function. Returns the optimized solution
        as a dictionary with feed keys corresponding to their ration (kg).

        Parameters
        ----------
        animal_combination : AnimalCombination
            enum of 'AnimalCombination', e.g. The animal combination to optimize the ration for.
        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization
        previous_ration : Dict[str, float | str] | None
            Ration from previous month, if applicable.

        Returns
        -------
        OptimizeResult object from scipy package

        Raises
        ------
        ValueError
            If the animal combination is invalid.

        """
        arguments = (ration_config,)
        self.set_constraints(arguments=arguments)
        if previous_ration and not udrm.is_udr:
            x0 = []
            prev_ration = previous_ration.copy()
            for key, value in prev_ration.items():
                if key not in ["status", "objective"]:
                    x0.append(value)
        else:
            n = len(ration_config.price_list)
            x0 = [1] + [random.random() * 10 for _ in range(n - 1)]
        # Dividing limit by 3 for tri-decision variables for farm grown feeds
        if udrm.is_udr:
            bnds = self.make_user_bounds(
                UserDefinedRationManager.ration_to_use(animal_combination),
                ration_config.DMIest_requirement,
            )
            x0 = [np.mean(bnd) for bnd in bnds]
        else:
            bnds = []
            bnds = [(0, lim + 0.0001) for lim in ration_config.feed_limit_list]

        if str(animal_combination) in ["AnimalCombination.LAC_COW"]:
            return minimize(
                self.objective,
                x0,
                method="SLSQP",
                bounds=bnds,
                constraints=self.cow_constraints,
                args=arguments,
            )
        elif str(animal_combination) in [
            "AnimalCombination.GROWING",
            "AnimalCombination.CLOSE_UP",
            "AnimalCombination.GROWING_AND_CLOSE_UP",
        ]:
            return minimize(
                self.objective,
                x0,
                method="SLSQP",
                bounds=bnds,
                constraints=self.heifer_constraints,
                args=arguments,
            )
        else:
            raise ValueError("Invalid animal combination: " + str(animal_combination))

    def attempt_optimization(
        self,
        requirements: AnimalRequirements,
        available_feeds: AvailableFeedsTypedDict,
        animal_combination: AnimalCombination,
        previous_ration: Dict[str, float | str] | None = None
    ) -> Tuple[OptimizeResult | None, Dict[str, float] | None, RationConfig]:
        """
        Function that sets up the nutrients and requirements lists into structured
        inputs for the non-linear program and calls the optimization function.

        Parameters
        ----------
        requirements: AnimalRequirements
            Summary of requirements for a group of animals.
        available_feeds : Dict
            A DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py
        animal_combination : AnimalCombination
            Enum of 'AnimalCombination', e.g. The animal combination to optimize the ration for.
        previous_ration : Dict[str, float | str] | None
            Ration from previous month, if applicable.

        Returns
        -------
        OptimizeResult
            Scipy object with information regarding the minimization attempt.

        Dict[str, float]

        RationConfig
            RationCofig object.

        """
        price_list = available_feeds["price"]
        TDN_list = available_feeds["TDN"]
        DE_list = available_feeds["DE"]
        EE_list = available_feeds["EE"]
        is_fat_list = available_feeds["is_fat"]
        calcium_list = available_feeds["calcium"]
        phosphorus_list = available_feeds["phosphorus"]
        NDF_list = available_feeds["NDF"]
        feed_type_list = available_feeds["feed_type"]
        is_wetforage_list = available_feeds["is_wetforage"]
        Kd_list = available_feeds["Kd"]
        N_A_list = available_feeds["N_A"]
        N_B_list = available_feeds["N_B"]
        CP_list = available_feeds["CP"]
        dRUP_list = available_feeds["dRUP"]
        # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
        # GitHub Issue # 793
        if str(animal_combination) in ["AnimalCombination.LAC_COW"]:
            feed_limit_list = available_feeds["lactating_cow_limit"]
            lactating = True
        else:
            feed_limit_list = available_feeds["dry_cow_limit"]
            lactating = False
        ration_config = RationConfig(
            price_list,
            requirements.NEmaint_requirement,
            requirements.NEa_requirement,
            requirements.NEpreg_requirement,
            requirements.NEl_requirement,
            requirements.NEg_requirement,
            requirements.MP_requirement,
            requirements.Ca_requirement,
            requirements.P_requirement,
            TDN_list,
            DE_list,
            EE_list,
            is_fat_list,
            requirements.avg_BW,
            calcium_list,
            phosphorus_list,
            NDF_list,
            feed_type_list,
            is_wetforage_list,
            Kd_list,
            N_A_list,
            N_B_list,
            CP_list,
            dRUP_list,
            feed_limit_list,
            lactating,
            DMIest__requirement=requirements.DMIest_requirement,
        )
        # try block for catching scipy SLSQP error
        i = 0
        count = 0
        while i < 1:
            try:
                solution = self.optimize(
                    animal_combination, ration_config, previous_ration
                )
            except Exception as e:  # noqa
                i -= 1
                info_map = {
                    "class": "RationOptimizer",
                    "function": self.attempt_optimization.__name__,
                }
                om.add_error(
                    "SLSQP error", "Ration optimization unable to resolve.", info_map
                )
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
            ration_vals = self.get_ration_vals(solution.x, ration_config)
        return solution, ration_vals, ration_config

    @staticmethod
    def is_constraint_violated(
        solution_x: npt.NDArray[np.float64],
        constraint: Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str],
        ration_config: RationConfig
    ) -> bool:
        """
        Helper function to check a solution dictionary to see if a given constraint
            in a list of constraints was met.

        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x array from minimize function used in ration_NLP.py
        constraint: dict[str, Any]
            constraint function as defined in ration_NLP.py
        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        bool
            True if the constraint method was not met.
        """
        result = constraint["fun"](solution_x, ration_config)
        if constraint["type"] == "ineq" and result < 0:
            return True
        elif constraint["type"] == "eq" and not np.isclose(result, 0):
            return True
        else:
            return False

    @staticmethod
    def find_failed_constraints(
        solution_x: npt.NDArray[np.float64],
        constraints: List[Dict[str, Callable[[Any, Any], float]]],
        ration_config: RationConfig
    ) -> List[Dict[str, Callable[[Any, Any], float]]]:
        """
        Returns list of constraints that were not met during optmization step.

        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x is from minimize function used in ration_NLP.py,
                solution obj itself is returned as  <dict class 'scipy.optimize._optimize.OptimizeResult'>

        constraints: List[dict[str, Callable]]
            list of constraint functions as defined in ration_NLP.py

        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        List[dict[str,Callable]]
            the same type of list as the constraints themselves
                just filtered such that the ones that failed are returned
        """
        return list(
            filter(
                lambda c: RationOptimizer.is_constraint_violated(
                    solution_x, c, ration_config
                ),
                constraints,
            )
        )
