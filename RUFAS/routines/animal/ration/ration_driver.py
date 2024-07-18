import collections
from typing import Set, Dict, List, Tuple, Literal

from RUFAS.units import MeasurementUnits
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.ration import animal_requirements
from RUFAS.routines.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.routines.animal.ration.user_defined_ration import (
    UserDefinedRationManager as UserDefinedRationManager,
)
from RUFAS.routines.animal.ration.ration_config import RationConfig
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.animal_typed_dicts import AvailableFeedsTypedDict, FeedInfoTypedDict
from RUFAS.general_constants import GeneralConstants

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
    def formulate_ration(
        cls, pen, available_feeds: AvailableFeedsTypedDict, animal_grouping_scenario
    ) -> Tuple[Dict[str, float | str], Dict[str, float]]:
        """
        Function that links the ration_driver file with the calc_ration function in
        animal_manager.py. Returns a dictionary of the rations by feed and status of the NLP
        optimization.

        Parameters
        ----------
        pen : Pen
            An object of class Pen.
        available_feeds : AvailableFeedsTypedDict
            An object of class AvailableFeeds.
        animal_grouping_scenario : AnimalGroupingScenario enum
            A grouping scenario of animals used in the current simulation,
            specified in AnimalGroupingScenario enum and AnimalManager class.

        Returns
        -------
        Dict[str, float]
            Formulated ration.
        Dict[str, float]
            Summary of ration content.
        """

        # creating instance of class requirements
        req = animal_requirements.AnimalRequirements()
        # Use grouping scenario to find the type of each animal in pen
        req.set_requirements(pen, animal_grouping_scenario, False)
        if udrm.is_udr:
            ration, ration_vals = cls.get_user_defined_ration(req, pen, available_feeds, animal_grouping_scenario)
            return ration, ration_vals

        if hasattr(pen, "ration_per_animal"):
            previous_ration = pen.ration_per_animal
        else:
            previous_ration = None
        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(
            req, available_feeds, pen.animal_combination, previous_ration
        )
        # Reduction of milk production estimate process to achieve feasible solution
        num_reattempts: int = 0

        # TODO: Put AnimalCombination enum in a separate file and use it here instead of hardcoding the names
        # GitHub Issue #793
        if pen.animal_combination.name in ["LAC_COW"]:
            while not solution.success:
                num_reattempts += 1
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(
                    solution.x, ration_optimizer.cow_constraints, ration_config
                )
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                reduction = AnimalModuleConstants.MILK_REDUCTION_KG
                cls.reduce_milk_production(pen, reduction)
                req.set_requirements(pen, animal_grouping_scenario, True)
                (
                    solution,
                    ration_vals,
                    ration_config,
                ) = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination, previous_ration)
                info_map = {
                    "class": "RationManager",
                    "function": cls.formulate_ration.__name__,
                }
                animal_list = list(pen.animals_in_pen.values())
                sim_day = animal_list[0].body_weight_history[-1].simulation_day
                fail_summary = {
                    "simulation day": sim_day,
                    "reattempt number": num_reattempts,
                    "constraints_failed_dict": constraints_failed_list,
                    "ration_attempted": cls.make_ration_from_solution(available_feeds, solution),
                    "pen requirements": pen.avg_nutrient_rqmts,
                }
                fail_summary_units = {
                    "simulation_day": MeasurementUnits.SIMULATION_DAY,
                    "reattempt number": MeasurementUnits.UNITLESS,
                    "constraints_failed_dict": MeasurementUnits.UNITLESS,
                    "ration_attempted": MeasurementUnits.UNITLESS,
                    "pen requirements": {
                        "NEmaint_requirement": MeasurementUnits.MEGACALORIES,
                        "NEa_requirement": MeasurementUnits.MEGACALORIES,
                        "NEg_requirement": MeasurementUnits.MEGACALORIES,
                        "NEpreg_requirement": MeasurementUnits.MEGACALORIES,
                        "NEl_requirement": MeasurementUnits.MEGACALORIES,
                        "MP_requirement": MeasurementUnits.GRAMS,
                        "Ca_requirement": MeasurementUnits.GRAMS,
                        "P_req": MeasurementUnits.GRAMS,
                        "DMIest_requirement": MeasurementUnits.KILOGRAMS,
                        "avg_BW": MeasurementUnits.KILOGRAMS,
                        "avg_milk_production_reduction_pen": MeasurementUnits.KILOGRAMS,
                    },
                }
                om.add_variable(
                    f"failed_constraint_summary_for_pen_{pen.id}",
                    fail_summary,
                    dict(info_map, **{"units": fail_summary_units}),
                )
                # TODO remove if statement below before, replace with error
                if num_reattempts > 20:
                    print(fail_summary)
                    print(pen.animal_combination.name)

        if solution is not None:
            ration = cls.make_ration_from_solution(available_feeds, solution)
            return ration, ration_vals
        # safeguard if scipy SLSQP bounds error still occurs after many iterations
        # using previous cycles ration for this pen
        else:
            return pen.ration, ration_vals

    @staticmethod
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
        total_milk_in_pen = sum(animal.estimated_daily_milk_produced for animal in list(pen.animals_in_pen.values()))
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
        for animal in list(pen.animals_in_pen.values()):
            if animal.estimated_daily_milk_produced - reduction > 1.0:
                animal.estimated_daily_milk_produced -= reduction
                animal.milk_production_reduction -= reduction
            running_total_milk += animal.estimated_daily_milk_produced

    @classmethod
    def make_ration_from_solution(
        cls, available_feeds: AvailableFeedsTypedDict, solution: scipy.optimize.OptimizeResult
    ) -> Dict[str, float | str]:
        """
        Generates ration dictionary from scipy result

        Parameters
        ----------
        available_feeds : Dict[str, Dict[str, List[str] | List[int] | List[float]]]
            A DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py

        solution : OptimizeResult
            Object from scipy package.

        Returns
        -------
        Dict[str, float]
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed per animal.

        """
        ration: Dict[str, float | str] = {}
        for feed_id in range(len(available_feeds["feed_id"])):
            i = feed_id * 3
            num = solution.x[i]
            num += solution.x[i + 1]
            num += solution.x[i + 2]
            ration[available_feeds["feed_key"][feed_id]] = round(num, 6)
        ration["status"] = "Optimal"
        ration_config = RationConfig()
        ration_config.price_list = RationOptimizer.triple_values_in_list(available_feeds["price"])
        ration["objective"] = ration_optimizer.objective(solution.x, ration_config)
        return ration

    @classmethod
    def make_solution_from_fixed_ration(cls, ration: Dict[str, float]) -> List[float]:
        """
        makes solution object from returned fixed ration for use in get_ration_vals function in ration_optimizer.py
        Simply puts the value in triplicate, and multiplies by the MEact defined in  ration_config

        Parameters
        ----------
        ration : Dict[str, float]
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed per animal.

        Returns
        -------
        List[float]
            List of kg fed per animal, in triplicate, to match scipy.OptimizeResult object.

        """
        excluded_keys = {"status", "objective"}
        solution_from_ration = []
        for key in ration.keys():
            if key not in excluded_keys:
                solution_from_ration.append(ration[key] / 3)
                solution_from_ration.append(ration[key] / 3)
                solution_from_ration.append(ration[key] / 3)
        return solution_from_ration

    @classmethod
    def get_user_defined_ration(  # noqa
        cls,
        req: animal_requirements.AnimalRequirements,
        pen,
        available_feeds: AvailableFeedsTypedDict,
        animal_grouping_scenario,
    ) -> tuple[Dict[str, float], Dict[str, float]]:
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
        ration : Dict[str, float]
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed.
        ration_vals : Dict[str, float]

        """
        info_map = {
            "class": "RationManager",
            "function": cls.get_user_defined_ration.__name__,
        }
        ration_percents = UserDefinedRationManager.ration_to_use(pen.animal_combination)
        fixed_ration = False
        num_reattempts = 0
        constraints_failed_list = []

        if hasattr(pen, "ration_per_animal"):
            previous_ration = pen.ration_per_animal
        else:
            previous_ration = None
        solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(
            req, available_feeds, pen.animal_combination, previous_ration
        )
        if pen.animal_combination.name in ["LAC_COW"]:
            failed_constraints = ration_optimizer.find_failed_constraints(
                solution.x, ration_optimizer.cow_constraints, ration_config
            )
        else:
            failed_constraints = ration_optimizer.find_failed_constraints(
                solution.x, ration_optimizer.heifer_constraints, ration_config
            )
        fail_summary_units = {
            "simulation_day": MeasurementUnits.SIMULATION_DAY,
            "reattempt number": MeasurementUnits.UNITLESS,
            "constraints_failed_dict": MeasurementUnits.UNITLESS,
            "ration_attempted": MeasurementUnits.UNITLESS,
            "pen requirements": {
                "NEmaint_requirement": MeasurementUnits.MEGACALORIES,
                "NEa_requirement": MeasurementUnits.MEGACALORIES,
                "NEg_requirement": MeasurementUnits.MEGACALORIES,
                "NEpreg_requirement": MeasurementUnits.MEGACALORIES,
                "NEl_requirement": MeasurementUnits.MEGACALORIES,
                "MP_requirement": MeasurementUnits.GRAMS,
                "Ca_requirement": MeasurementUnits.GRAMS,
                "P_req": MeasurementUnits.GRAMS,
                "DMIest_requirement": MeasurementUnits.KILOGRAMS,
                "avg_BW": MeasurementUnits.KILOGRAMS,
                "avg_milk_production_reduction_pen": MeasurementUnits.KILOGRAMS,
            },
        }
        if failed_constraints is not None:
            for constr in failed_constraints:
                constraints_failed_list.append(constr["fun"].__name__)
            animal_list = list(pen.animals_in_pen.values())
            fail_summary = {
                "simulation day": animal_list[0].body_weight_history[-1].simulation_day,
                "reattempt number": num_reattempts,
                "constraints_failed_dict": constraints_failed_list,
                "ration_attempted": cls.make_ration_from_solution(available_feeds, solution),
                "pen requirements": pen.avg_nutrient_rqmts,
            }
            om.add_variable(
                f"failed_constraint_summary_for_pen_{pen.id}",
                fail_summary,
                dict(info_map, **{"units": fail_summary_units}),
            )

        if udrm.milk_reduction_maximum == 0.0 and udrm.tolerance == 0.0 and not solution.success:
            ration = UserDefinedRationManager.make_ration_from_user_values(ration_percents, available_feeds, req)
            ration_vals = ration_optimizer.get_ration_vals(cls.make_solution_from_fixed_ration(ration), ration_config)
            return ration, ration_vals

        if pen.animal_combination.name not in ["LAC_COW"] and not solution.success:
            fixed_ration = True

        if pen.animal_combination.name in ["LAC_COW"] and solution is not None:
            running_milk_reduction = 0.0
            while not solution.success:
                running_average_milk = cls.calc_milk_average(pen)
                reduction = AnimalModuleConstants.MILK_REDUCTION_KG
                if (
                    udrm.milk_reduction_maximum == 0.0
                    or running_milk_reduction + reduction > udrm.milk_reduction_maximum
                    or running_average_milk - reduction < 1.0
                ):
                    fixed_ration = True
                    solution.success = True
                    break

                num_reattempts += 1
                running_milk_reduction += reduction
                cls.reduce_milk_production(pen, reduction)
                running_average_milk = cls.calc_milk_average(pen)

                req.set_requirements(pen, animal_grouping_scenario, True)
                (
                    solution,
                    ration_vals,
                    ration_config,
                ) = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination, previous_ration)
                failed_constraints = []
                constraints_failed_list = []
                failed_constraints = ration_optimizer.find_failed_constraints(
                    solution.x, ration_optimizer.cow_constraints, ration_config
                )
                if failed_constraints:
                    for constr in failed_constraints:
                        constraints_failed_list.append(constr["fun"].__name__)
                    fail_summary = {
                        "simulation day": animal_list[0].body_weight_history[-1].simulation_day,
                        "reattempt number": num_reattempts,
                        "constraints_failed_dict": constraints_failed_list,
                        "ration_attempted": cls.make_ration_from_solution(available_feeds, solution),
                        "pen requirements": pen.avg_nutrient_rqmts,
                    }
                    om.add_variable(
                        f"failed_constraint_summary_for_pen_{pen.id}",
                        fail_summary,
                        dict(info_map, **{"units": fail_summary_units}),
                    )

        if fixed_ration:
            ration = UserDefinedRationManager.make_ration_from_user_values(ration_percents, available_feeds, req)
            ration_vals = ration_optimizer.get_ration_vals(cls.make_solution_from_fixed_ration(ration), ration_config)
        else:
            ration = cls.make_ration_from_solution(available_feeds, solution)
            ration_vals = ration_optimizer.get_ration_vals(solution.x, ration_config)
        return ration, ration_vals


class RationReporter:
    """
    Reports information about a formulated ration.
    """

    # fmt: off
    @classmethod
    def report_ration(  # noqa
        cls, ration: Dict[str, float | str],
        available_feeds: Dict[str, Dict[str, float]]
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        # fmt: on
        """
        Calculates information in the ration about nutrient information including
        nutrient amounts and concentrations. Returns a dictionary of nutrient amounts
        and nutrient calculations respectively. Psuedocode for these calculations
        are located in Ration Class Variables in Animal Module Pseduocode.

        Parameters
        ----------
        ration : Dict
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed.
        available_feeds : Dict
            Available feeds dictionary from the Feed class object.


        Returns
        -------
        Tuple[Dict, Dict]
            Tuple of two dictionaries: one of nutrient amounts, the other of nutrient concentration (as a percentage
              of fed dry matter).
        """
        nutrient_amount: Dict[str, float] = {
            "dm": 0,
            "as_fed": 0,
            "CP": 0,
            "ADF": 0,
            "NDF": 0,
            "lignin": 0,
            "ash": 0,
            "phosphorus": 0,
            "potassium": 0,
            "N": 0,
            "EE": 0,
            "starch": 0,
            "TDN": 0,
            "DE": 0,
            "calcium": 0,
        }

        nutrient_conc: Dict[str, float] = {}
        ration = ration.copy()
        for non_numeric_key in ["status", "objective"]:
            if non_numeric_key in ration:
                del ration[non_numeric_key]
        nutrients = [
            "DM",
            "CP",
            "ADF",
            "NDF",
            "lignin",
            "ash",
            "phosphorus",
            "potassium",
            "N",
            "EE",
            "starch",
            "TDN",
            "DE",
            "calcium",
        ]

        for key, val in ration.items():
            nutrient_amount["dm"] += val
            for nutr in nutrients:
                # all values on a 100% dry matter basis
                if nutr == "DM":
                    if available_feeds[key][nutr]:
                        nutrient_amount["as_fed"] += val / (
                            available_feeds[key][nutr] * GeneralConstants.PERCENTAGE_TO_FRACTION
                        )
                elif nutr == "N":
                    # [A.2.A.2]
                    if key[:3] in ["172", "181", "202", "216"]:
                        denom = 6.38
                    # [A.2.A.1]
                    else:
                        denom = 6.25
                    nutrient_amount[nutr] += (
                        available_feeds[key]["CP"] / (denom * GeneralConstants.FRACTION_TO_PERCENTAGE)
                    ) * val
                else:
                    if nutr == "DE":
                        if available_feeds[key]["DE"] != -1:
                            nutrient_amount[nutr] += val * (
                                available_feeds[key]["DE"]
                            )
                        else:
                            nutrient_amount[nutr] += val * (
                                available_feeds[key]["DE_Base"]
                            )
                    else:
                        nutrient_amount[nutr] += val * (
                            available_feeds[key][nutr] * GeneralConstants.PERCENTAGE_TO_FRACTION
                        )

        dm_amount = nutrient_amount["dm"]
        if dm_amount == 0:
            dm_amount = 1
        for nutr in nutrients:
            if nutr == "DM":
                if nutrient_amount["as_fed"]:
                    nutrient_conc["dm"] = (
                        (dm_amount / nutrient_amount["as_fed"]) * GeneralConstants.FRACTION_TO_PERCENTAGE
                    )
                else:
                    nutrient_conc["dm"] = 0.0
            else:
                # all values on a 100% dry matter basis
                nutrient_conc[nutr] = (nutrient_amount[nutr] / dm_amount) * GeneralConstants.FRACTION_TO_PERCENTAGE
        return nutrient_amount, nutrient_conc

    @classmethod
    def report_ration_supply(
        cls,
        ration: Dict[str, float],
        available_feeds: AvailableFeedsTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float,
    ) -> Dict[str, float]:
        """
        Nutrient and energy supply of a formulated ration
        Different from the report_ration method, since this takes into account digestibility and other factors

        Parameters
        ----------
        ration : Dict[str, float]
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed.
        available_feeds : Dict
            available feeds dictionary from the Feed class object.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.


        Returns
        -------
        Dict[str, float]
            Dictionary of nutrients and energy supplied by a formulated ration.

        """
        ration_ = ration.copy()
        for non_numeric_key in ["status", "objective"]:
            if non_numeric_key in ration_:
                del ration_[non_numeric_key]

        supply_report = {
            "ME": 0.0,
            "DE": 0.0,
            "NE_maintenance_and_activity": 0.0,
            "NE_lactation": 0.0,
            "NE_growth": 0.0,
            "calcium": 0.0,
            "phosphorus": 0.0,
            "fat": 0.0,
            "fat_percentage": 0.0,
            "forage_NDF": 0.0,
        }

        for key, kg_fed in ration_.items():
            for item in supply_report:
                supply_report[item] += eval(
                    "RationReporter.get_"
                    + item
                    + "(kg_fed, available_feeds[key], ration_report, body_weight)"
                )
        supply_report["forage_NDF_percent"] = supply_report["forage_NDF"] / sum(
            ration_.values()
        )
        supply_report[
            "metabolizable_protein"
        ] = RationReporter.get_metabolizable_protein(
            ration_, available_feeds, ration_report, body_weight
        )

        return supply_report

    @staticmethod
    def get_TDN_discount(ration_report: Dict[str, Dict[str, float]], body_weight: float) -> float:
        """
        Crucial step to take into account Total digestible nutrient (TDN)
         digesitbility (% of DM).
        Initial step in net energy (NE) and metabolizable energy (ME) calculations.


        Parameters
        ----------
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Total digestible nutrient (% of DM) discount, which is TDN digestibility decrease that is a result of
             TDN amount relative to TDN concentration.

        Notes
        -----
        See the following pseudocode for all equations
        [A.Cow.E.3]-[A.Heifer.E.3]

        """
        TDNtotal: float = ration_report["nutrient_amount"]["TDN"]
        TDNconc: float = ration_report["nutrient_conc"]["TDN"]
        somatic_body_weight = body_weight * 0.96
        if body_weight == 0.0 or TDNtotal == 0.0:
            return 0.0
        if TDNtotal < (0.035 * body_weight**0.75):
            DMI_to_maint = 1.0
        else:
            DMI_to_maint = TDNtotal / (0.035 * somatic_body_weight**0.75)
        if TDNconc < 60:
            Discount = 1.0
        else:
            Discount = (
                TDNconc - ((0.18 * TDNconc - 10.3) * (DMI_to_maint - 1))
            ) / TDNconc
        return Discount

    @staticmethod
    def get_DE(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns actual digestible energy of feed item, Mcal/kg
        Calculation is performed on a per feed item basis

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            actual digestible energy of feed item, Mcal/kg.

        """
        de_key: Literal["DE_Base", "DE"] = "DE_Base" if feed_item_info["DE"] == -1 else "DE"
        DE_act = feed_item_info[de_key] * RationReporter.get_TDN_discount(
            ration_report, body_weight
        )
        return DE_act

    @staticmethod
    def get_ME(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns metabolizable energy of feed item.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            metabolizable energy of feed i, Mcal/kg.

        """
        DE_act = RationReporter.get_DE(
            kg_fed, feed_item_info, ration_report, body_weight
        )

        if feed_item_info["feed_type"] == "Mineral":
            ME_item = 0.0
        elif feed_item_info["is_fat"] is True:
            ME_item = float(
                feed_item_info["DE"]
                if feed_item_info["DE"] != -1
                else feed_item_info["DE_Base"]
            )
        elif feed_item_info["EE"] >= 3:
            ME_item = 1.01 * DE_act - 0.45 + 0.0046 * (feed_item_info["EE"] - 3)
        else:
            ME_item = 1.01 * DE_act - 0.45
        return ME_item

    @staticmethod
    def get_NE_maintenance_and_activity(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns net energy of feed item available for maintenance requirements.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Net energy of feed i, Mcal/kg.

        """
        ME_item = RationReporter.get_ME(
            kg_fed, feed_item_info, ration_report, body_weight
        )
        if feed_item_info["is_fat"] is True:
            NEm_item = 0.8 * ME_item
        else:
            NEm_item = (
                1.37 * ME_item - 0.138 * ME_item**2 + 0.0105 * ME_item**3 - 1.12
            )
        return NEm_item * kg_fed

    @staticmethod
    def get_NE_lactation(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns net energy of feed item available for lactation requirements.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Net energy of feed i, Mcal/kg.

        """
        DE_act = RationReporter.get_DE(
            kg_fed, feed_item_info, ration_report, body_weight
        )
        ME_item = RationReporter.get_ME(
            kg_fed, feed_item_info, ration_report, body_weight
        )
        if feed_item_info["feed_type"] == "Mineral":
            NE_lactation_item = 0.0
        elif feed_item_info["is_fat"] is True:
            NE_lactation_item = 0.8 * DE_act
        elif feed_item_info["EE"] >= 3.0:
            NE_lactation_item = (
                0.703 * ME_item
                - 0.19
                + ((0.097 * ME_item + 0.19) / 97) * (feed_item_info["EE"] - 3)
            )
        else:
            NE_lactation_item = 0.703 * ME_item - 0.19
        return NE_lactation_item * kg_fed

    @staticmethod
    def get_NE_growth(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns net energy of feed item available for growth requirements.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Net energy of feed i, Mcal/kg.

        """
        ME_item = RationReporter.get_ME(
            kg_fed, feed_item_info, ration_report, body_weight
        )
        if feed_item_info["feed_type"] == "Mineral":
            NE_growth = 0.0
        elif feed_item_info["is_fat"] is True:
            NE_growth = 0.55 * ME_item
        else:
            NE_growth = (
                1.42 * ME_item - 0.174 * ME_item**2 + 0.0122 * ME_item**3 - 1.65
            )
        return NE_growth * kg_fed

    @staticmethod
    def get_calcium(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns calcium supply of feed item.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Calcium supply of feed item, g.

        """
        if feed_item_info["feed_type"] == "Forage":
            dCa = 0.3
        elif feed_item_info["feed_type"] == "Conc":
            dCa = 0.6
        elif feed_item_info["feed_type"] == "Mineral":
            dCa = 0.95
        else:
            dCa = 0.0
        calcium_item = kg_fed * feed_item_info["calcium"] * 0.01 * dCa
        return calcium_item

    @staticmethod
    def get_phosphorus(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns phosphorus supply of feed item.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Phosphorus supply, g.

        """
        if feed_item_info["feed_type"] == "Forage":
            dP = 0.64
        elif feed_item_info["feed_type"] == "Conc":
            dP = 0.70
        elif feed_item_info["feed_type"] == "Mineral":
            dP = 0.80
        else:
            dP = 0.0
        return dP * feed_item_info["phosphorus"] * 0.01 * kg_fed

    @staticmethod
    def get_fat(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns fat supply of feed item.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Fat supply of feed item, g.

        """
        fat_item = feed_item_info["EE"] * kg_fed
        return fat_item

    @staticmethod
    def get_fat_percentage(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns fat content percentage of feed item.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Dry matter fat percentage of feed item.

        """
        fat_item_percentage = (feed_item_info["EE"] * kg_fed) / ration_report[
            "nutrient_amount"
        ]["dm"]
        return fat_item_percentage

    @staticmethod
    def get_forage_NDF(
        kg_fed: float,
        feed_item_info: FeedInfoTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns forage neutral detergent fiber content of feed item, g.

        Parameters
        ----------
        kg_fed : float
            Kilograms of feed item in ration.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, Dict[str, float]]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Forage neutral detergent fiber content of feed item, g.

        """
        if feed_item_info["feed_type"] == "Forage":
            forage_NDF_item = feed_item_info["NDF"] * kg_fed
        else:
            forage_NDF_item = 0.0
        return forage_NDF_item

    @staticmethod
    def get_metabolizable_protein(
        ration: Dict[str, float],
        available_feeds: AvailableFeedsTypedDict,
        ration_report: Dict[str, Dict[str, float]],
        body_weight: float
    ) -> float:
        """
        Returns metabolizable protein supply  of feed item, g.

        Parameters
        ----------
        ration : Dict[str, float]
            Dictionary of formulated ration, with keys as feed IDs, values as kg fed.
        available_feeds : Dict
            available feeds dictionary from the Feed class object.
        feed_item_info : Dict
            Dictionary of nutrient and energy information of feed item.
        ration_report : Dict[str, float]
            Dictionary of nutrient amount and concentrations.
        body_weight : float
            Animal body weight in kg.

        Returns
        -------
        float
            Metabolizable protein supply of feed item, g.
        """
        TDNtotal = ration_report["nutrient_amount"]["TDN"]

        DMI_estimate = sum(ration.values())
        is_conc = []
        for item in ration:
            if available_feeds[item]["feed_type"] == "Conc":
                is_conc.append(ration[item])
        DMI_conc_percentage = sum(is_conc) / DMI_estimate * GeneralConstants.FRACTION_TO_PERCENTAGE
        Kp = []
        RUP_list = []
        RDP_list = []
        dRUP_diet = []
        counter = 0
        for key, kg_fed in ration.items():
            feed_item_info = available_feeds[key]

            # KP calcs
            if feed_item_info["feed_type"] == "Conc":
                Kp.append(
                    2.904
                    + 1.375 * (DMI_estimate / body_weight) * 100
                    - 0.02 * DMI_conc_percentage
                )
            elif (
                feed_item_info["feed_type"] == "Forage"
                and feed_item_info["is_wetforage"] is False
            ):
                Kp.append(
                    3.362
                    + 0.479 * (DMI_estimate / body_weight) * 100
                    - 0.017 * feed_item_info["NDF"]
                    - 0.007 * DMI_conc_percentage
                )
            elif feed_item_info["is_wetforage"] is True:
                Kp.append(3.054 + 0.614 * (DMI_estimate / body_weight) * 100)
            else:
                Kp.append(0)

            # RDP calcs
            if Kp[counter] > -feed_item_info["Kd"]:
                RDP_list.append(
                    (
                        feed_item_info["Kd"]
                        / (feed_item_info["Kd"] + Kp[counter])
                        * (feed_item_info["N_B"] / 100)
                        * feed_item_info["CP"]
                        + (feed_item_info["N_A"] / 100) * feed_item_info["CP"]
                    )
                )
            else:
                RDP_list.append(0)

            # RUP calcs
            RUP_list.append((feed_item_info["CP"] - RDP_list[counter]))
            dRUP_diet.append(feed_item_info["dRUP"])

            counter += 1

        RDP_diet = []
        RUP_diet = []
        for i, kg_fed in enumerate(ration.values()):
            RDP_diet.append(GeneralConstants.KG_TO_GRAMS * RDP_list[i] * kg_fed * GeneralConstants.PERCENTAGE_TO_FRACTION)
            RUP_diet.append(GeneralConstants.KG_TO_GRAMS * kg_fed * RUP_list[i] * GeneralConstants.PERCENTAGE_TO_FRACTION * 
                            dRUP_diet[i] * GeneralConstants.PERCENTAGE_TO_FRACTION)

        TDN_total_actual = TDNtotal * RationReporter.get_TDN_discount(
            ration_report, body_weight
        )

        # MP bact calcs
        MP_bact = 0.64 * min(
            GeneralConstants.KG_TO_GRAMS * 0.13 * TDN_total_actual, 0.85 * sum(RDP_diet)
        )

        MP_supply = MP_bact + sum(RUP_diet) + 0.4 * 11.8 * DMI_estimate
        return float(MP_supply)


class AvailableFeeds:
    """
    Stores the information of the feeds available at the end of a ration interval
    to be used in the non-linear program ration formulation.
    """

    def __init__(self) -> None:
        # id of the feed in the feed database
        self.feed_id: List[int] = []
        # list to keep track of dictionary keys
        self.feed_key: List[int] = []
        # price of the feed ($/KG)
        self.price: List[float] = []
        # Total digestible nutrient (% of DM)
        self.TDN: List[float] = []
        # Digestible energy (Mcal/kg)
        self.DE: List[float] = []
        # Ether extract, crude fat (% of DM)
        self.EE: List[float] = []
        # If the feed is fat supplement or not (yes = 1; no = 0)
        self.is_fat: List[int] = []
        # Calcium content (% of DM)
        self.calcium: List[float] = []
        # Phosphorus content (% of DM)
        self.phosphorus: List[float] = []
        # Neutral detergent fiber (% of DM)
        self.NDF: List[float] = []
        # Feed type (Forage, Concentrate, or Mineral)
        self.feed_type: List[str] = []
        # If the feed is wet forage or not (yes = 1; no = 0)
        self.is_wetforage: List[int] = []
        # Rumen protein degradation rate (%/h)
        self.Kd: List[float] = []
        # Fraction A of protein, degraded immediately in rumen (% of CP)
        self.N_A: List[float] = []
        # Fraction B of protein, potentially degradable protein, require time to
        # generally degrade in rumen (% of CP)
        self.N_B: List[float] = []
        # Crude protein (% of DM)
        self.CP: List[float] = []
        # RUP degradability (% of RUP)
        self.dRUP: List[float] = []
        # lactating cows feed limits
        self.lactating_cow_limit: List[float] = []
        # dry cow feed limits
        self.dry_cow_limit: List[float] = []
        # lactating cows feed limits
        self.lactating_cow_minimum: List[float] = []
        # dry cow feed limits
        self.dry_cow_minimum: List[float] = []
        # heiferIII limits
        self.heiferIII_limit: List[float] = []
        # heiferII limit
        self.heiferII_limit: List[float] = []
        # heiferI limit
        self.heiferI_limit: List[float] = []
        # calf limit
        self.calf_limit: List[float] = []
        # key = feed_id, val = index of that feed_id in self.feed_id list
        self._feed_id_to_list_idx_dict: Dict[int, int] = {}

    def feed_nutrients(self, feed) -> None:
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
            self.feed_id.append(feed["rufas_id"])
            self.price.append(feed_costs[str(key)])
            self.TDN.append(feed["TDN"])
            if feed["DE"] != -1:
                self.DE.append(feed["DE"])
            else:
                self.DE.append(feed["DE_Base"])
            self.EE.append(feed["EE"])
            self.is_fat.append(feed["is_fat"])
            self.calcium.append(feed["calcium"])
            self.phosphorus.append(feed["phosphorus"])
            self.NDF.append(feed["NDF"])
            self.feed_type.append(feed["feed_type"])
            self.is_wetforage.append(feed["is_wetforage"])
            self.Kd.append(feed["Kd"])
            self.N_A.append(feed["N_A"])
            self.N_B.append(feed["N_B"])
            self.CP.append(feed["CP"])
            self.dRUP.append(feed["dRUP"])
            if isinstance(feed["limit"], dict):
                self.lactating_cow_limit.append(feed["limit"]["lactating_cows"])
                self.dry_cow_limit.append(feed["limit"]["dry_cows"])
            else:
                self.lactating_cow_limit.append(feed["limit"])
                self.dry_cow_limit.append(feed["limit"])
            if isinstance(feed["lower_limit"], dict):
                self.lactating_cow_limit.append(feed["lower_limit"]["lactating_cows"])
                self.dry_cow_limit.append(feed["lower_limit"]["dry_cows"])
            else:
                self.lactating_cow_minimum.append(feed["lower_limit"])
                self.dry_cow_minimum.append(feed["lower_limit"])

    def get_feed_data_from_feed_ids(self, feed_ids: Set[int]):
        """
        Returns a subset of data from all the available feeds based on the
        given set of feed ids.

        Parameters
        ----------
        feed_ids : Set[int]
            A set of feed ids.

        Returns
        -------
        Dict
            A dictionary that contains a subset of data from all the available feeds based on the given set of feed ids.

        Raises
        ------
        KeyError
            If the feed id is not found in the feed id list.

        """
        # An explanation of code seen below can be found in Basecamp with the following path:
        # RuFaS > Docs & Files > Animal Module > Ration Driver Logic

        if not self._feed_id_to_list_idx_dict:
            self._feed_id_to_list_idx_dict = {fid: i for i, fid in enumerate(self.feed_id)}

        excluded_keys = ["_feed_id_to_list_idx_dict"]
        result = collections.defaultdict(list)
        for key, vals in self.__dict__.items():
            if key in excluded_keys:
                continue
            if not vals:
                result[key] = []
                continue
            for feed_id in sorted(list(feed_ids)):
                # Get the list index of the feed_id in self.feed_id list.
                try:
                    idx = self._feed_id_to_list_idx_dict[int(feed_id)]
                    result[key].append(vals[idx])
                except KeyError:
                    info_map = {
                        "class": self.__class__.__name__,
                        "function": self.get_feed_data_from_feed_ids.__name__,
                    }
                    om.add_error(
                        "KeyError",
                        f"Feed ID {feed_id} not found in AvailableFeeds. "
                        f"Check that price was set in purchased_feeds in input feed json, "
                        f"and that it is included in the specified NRC or NASEM csv.",
                        info_map,
                    )
                    raise
        return result
