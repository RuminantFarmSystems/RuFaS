from typing import List
import numpy as np

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow

# from RUFAS.routines.animal.pen import Pen
# from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions

# from RUFAS.routines.animal import AnimalManager

om = OutputManager()


class AnimalReporter:
    def report_daily_animal_population(animal_manager) -> None:
        """
        Adds daily totals for animal types to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager

        """
        info_map = {
            "class": "AnimalManager",
            "function": "daily_updates",
        }
        om.add_variable("sim_day", animal_manager.simulation_day, info_map)
        om.add_variable(
            "num_animals",
            len(animal_manager.calves)
            + len(animal_manager.heiferIs)
            + len(animal_manager.heiferIIs)
            + len(animal_manager.heiferIIIs)
            + len(animal_manager.cows),
            info_map,
        )
        om.add_variable("num_calves", len(animal_manager.calves), info_map)
        om.add_variable("num_heiferIs", len(animal_manager.heiferIs), info_map)
        om.add_variable("num_heiferIIs", len(animal_manager.heiferIIs), info_map)
        om.add_variable("num_heiferIIIs", len(animal_manager.heiferIIIs), info_map)
        om.add_variable(
            "num_lactating_cows",
            len([cow for cow in animal_manager.cows if cow.is_lactating]),
            info_map,
        )
        om.add_variable(
            "num_dry_cows",
            len([cow for cow in animal_manager.cows if not cow.is_lactating]),
            info_map,
        )

    def report_milk(pen, simulation_day) -> None:
        """
        Adds milk information for all cows in pen to output manager.

        Parameters
        ----------
        pen : Pen
            Individual Pen.
        simulation_day : int
            Day of simulation.

        """
        info_map = {
            "class": "cow",
            "function": "milking_update",
        }

        for animal in pen.animals_in_pen:
            milk_data_update = {}
            milk_data_update["days_in_milk"] = animal.days_in_milk
            milk_data_update["estimated_daily_milk_produced"] = animal.estimated_daily_milk_produced
            milk_data_update["milk_protein"] = animal.mPrt
            milk_data_update["milk_fat"] = animal.fat_percent
            milk_data_update["milk_lactose"] = animal.lactose_milk
            milk_data_update["lactating"] = animal.milking
            milk_data_update["parity"] = animal.calves
            milk_data_update["cow_id"] = animal.id
            milk_data_update["pen_id"] = animal.pen_history[-1].pen
            milk_data_update["simulation_day"] = simulation_day

            om.add_variable("milk_data_at_milk_update", milk_data_update, info_map)

    def report_ration_interval_data(animal_manager, feed) -> None:
        """
        For each pen, adds ration per animal and other supply reports, to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of class AnimalManager.

        feed : Feed
            Instance of class Feed.

        """
        for pen in animal_manager.all_pens:
            nutrient_amount = pen.ration_nutrient_amount
            nutrient_conc = pen.ration_nutrient_conc
            ration_per_animal = pen.ration_per_animal.copy()
            del ration_per_animal["status"]
            del ration_per_animal["objective"]
            ration_per_animal["dry_matter_intake_total"] = sum(
                [ration_per_animal[key] for key in ration_per_animal.keys()]
            )
            ration_report = {}
            ration_report["nutrient_amount"] = nutrient_amount
            ration_report["nutrient_conc"] = nutrient_conc

            info_map = {
                "class": "AnimalManager",
                "function": "_calc_ration_at_interval",
                "number_animals_in_pen": len(pen.animals_in_pen),
            }
            om.add_variable(
                f"ration_nutrient_amount_pen_{pen.id}_{pen.animal_combination.name}",
                nutrient_amount,
                info_map,
            )
            om.add_variable(
                f"MEdiet_pen_{pen.id}_{pen.animal_combination.name}",
                pen.MEdiet,
                info_map,
            )
            om.add_variable(
                f"avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}",
                pen.avg_nutrient_rqmts,
                info_map,
            )
            om.add_variable(
                f"ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_per_animal,
                info_map,
            )
            if pen.animal_combination != pen.AnimalCombination.CALF:
                ration_supply_report = RationReporter.report_ration_supply(
                    pen.ration_per_animal,
                    feed.available_feeds,
                    ration_report,
                    pen.avg_nutrient_rqmts["avg_BW"],
                )
                om.add_variable(
                    f"ration_supply_report_for_pen_{pen.id}_{pen.animal_combination.name}",
                    ration_supply_report,
                    info_map,
                )

    def report_daily_ration(animal_manager) -> None:
        """
        Adds ration totals as fed to each pen to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager class.

        """
        info_map = {
            "class": "AnimalReporter",
            "function": "report_daily_ration",
        }
        for pen in animal_manager.all_pens:
            ration_per_animal = pen.ration_per_animal.copy()
            del ration_per_animal["status"]
            del ration_per_animal["objective"]
            ration_total = {}
            ration_total["dry_matter_intake_total"] = 0
            for key in ration_per_animal.keys():
                if key != "status" and key != "objective":
                    ration_total[key] = pen.ration_per_animal[key] * len(pen.animals_in_pen)
                    ration_total["dry_matter_intake_total"] += ration_total[key]
            om.add_variable(
                f"ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_total,
                info_map,
            )

    def report_animal_module_manure(
        manure_excretions_output_data: dict[str, dict[str | AnimalManureExcretions]],
    ) -> None:
        """
        Generate detailed report of manure properties in the Animal Module.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of Animalmanager class.
        manure_excretions_output_data : dict[str, dict[str | AnimalManureExcretions]]
            Dictionary mapping prefixes to animal manure data.

        """
        for output_data_dict in manure_excretions_output_data.values():
            for manure_property, manure_value in output_data_dict["manure"].items():
                info_map = {
                    "class": "AnimalManager",
                    "function": "daily_updates",
                }
                om.add_variable(
                    f'{output_data_dict["prefix"]}_{str(manure_property)}',
                    manure_value,
                    info_map=info_map,
                )

    def report_pen_manure(pen) -> None:
        """
        Adds pen manure data to output manager.

        Parameters
        ----------
        pen : Pen
            Current pen.
        """
        info_map = {
            "class": "pen",
            "function": "calc_manure",
            "pen_id": pen.id,
            "pen_animal_combination": pen.animal_combination._name_,
        }
        om.add_variable("pen_manure_data", pen.manure, info_map)

    def report_pen_manure_properties(pen) -> None:
        info_map = {"class": "pen", "function": "calc_total_manure"}
        for manure_property, manure_value in pen.manure.items():
            om.add_variable(f"pen_{pen.id}_daily_{str(manure_property)}", manure_value, info_map=info_map)

    def report_life_cycle_manager_data(life_cycle_manager, sim_day: int) -> None:
        """
        Adds daily life cycle data to output manager.

        life_cycle_manager : LifeCycleManager
            Active instance of LifeCycleManager.
        sim_day : int
            Day of simulation.
        """
        info_map = {"class": "LifeCycleManager", "function": "daily_update"}
        # om.add_variable("calf_num", life_cycle_manager.calf_num, info_map)
        # om.add_variable("heiferI_num", life_cycle_manager.heiferI_num, info_map)
        # om.add_variable("heiferII_num", life_cycle_manager.heiferII_num, info_map)
        # om.add_variable("heiferIII_num", life_cycle_manager.heiferII_num, info_map)
        # om.add_variable("cow_num", life_cycle_manager.cow_num, info_map)
        om.add_variable("sold_heifer_num", life_cycle_manager.sold_heifer_num, info_map)
        om.add_variable("bought_heifer_num", life_cycle_manager.bought_heifer_num, info_map)
        om.add_variable("culled_heifer_num", life_cycle_manager.culled_heifer_num, info_map)
        om.add_variable("culled_cow_num", life_cycle_manager.culled_cow_num, info_map)
        om.add_variable("GnRH_injection_num_h", life_cycle_manager.GnRH_injection_num_h, info_map)
        om.add_variable("GnRH_injection_num", life_cycle_manager.GnRH_injection_num, info_map)
        om.add_variable("PGF_injection_num", life_cycle_manager.PGF_injection_num, info_map)
        om.add_variable("PGF_injection_num_h", life_cycle_manager.PGF_injection_num_h, info_map)
        om.add_variable("ai_num", life_cycle_manager.ai_num, info_map)
        om.add_variable("preg_check_num", life_cycle_manager.preg_check_num, info_map)
        om.add_variable("preg_check_num_h", life_cycle_manager.preg_check_num_h, info_map)
        om.add_variable("sold_calf_num", life_cycle_manager.sold_calf_num, info_map)
        om.add_variable("daily_milk_production", life_cycle_manager.daily_milk_production, info_map)
        om.add_variable("open_cow_num", life_cycle_manager.open_cow_num, info_map)
        om.add_variable("vwp_cow_num", life_cycle_manager.vwp_cow_num, info_map)
        om.add_variable("preg_cow_num", life_cycle_manager.preg_cow_num, info_map)
        om.add_variable("milking_cow_num", life_cycle_manager.milking_cow_num, info_map)
        om.add_variable("dry_cow_num", life_cycle_manager.dry_cow_num, info_map)
        om.add_variable("avg_days_in_milk", life_cycle_manager.avg_days_in_milk, info_map)
        om.add_variable("avg_days_in_preg", life_cycle_manager.avg_days_in_preg, info_map)
        om.add_variable("avg_cow_body_weight", life_cycle_manager.avg_cow_body_weight, info_map)
        om.add_variable("avg_parity_num", life_cycle_manager.avg_parity_num, info_map)
        om.add_variable("avg_calving_interval", life_cycle_manager.avg_calving_interval, info_map)
        om.add_variable("avg_breeding_to_preg_time", life_cycle_manager.avg_breeding_to_preg_time, info_map)
        om.add_variable("avg_heifer_culling_age", life_cycle_manager.avg_heifer_culling_age, info_map)
        om.add_variable("avg_cow_culling_age", life_cycle_manager.avg_cow_culling_age, info_map)
        om.add_variable("avg_mature_body_weight", life_cycle_manager.avg_mature_body_weight, info_map)
        om.add_variable("sim_day", sim_day, info_map)
        parity_1 = life_cycle_manager.num_cow_for_parity["1"]
        parity_2 = life_cycle_manager.num_cow_for_parity["2"]
        parity_3 = life_cycle_manager.num_cow_for_parity["3"]
        parity_greater_than_3 = life_cycle_manager.num_cow_for_parity["greater_than_3"]
        om.add_variable("num_cow_for_parity_1", parity_1, info_map)
        om.add_variable("num_cow_for_parity_2", parity_2, info_map)
        om.add_variable("num_cow_for_parity_3", parity_3, info_map)
        om.add_variable("num_cow_for_parity_greater_than_3", parity_greater_than_3, info_map)
        calving_to_preg_time_1 = life_cycle_manager.avg_calving_to_preg_time["1"]
        calving_to_preg_time_2 = life_cycle_manager.avg_calving_to_preg_time["2"]
        calving_to_preg_time_3 = life_cycle_manager.avg_calving_to_preg_time["3"]
        calving_to_preg_time_greater_than_3 = life_cycle_manager.avg_calving_to_preg_time["greater_than_3"]
        om.add_variable("calving_to_preg_time_1", calving_to_preg_time_1, info_map)
        om.add_variable("calving_to_preg_time_2", calving_to_preg_time_2, info_map)
        om.add_variable("calving_to_preg_time_3", calving_to_preg_time_3, info_map)
        om.add_variable("calving_to_preg_time_greater_than_3", calving_to_preg_time_greater_than_3, info_map)
        avg_age_for_calving_1 = life_cycle_manager.avg_age_for_calving["1"]
        avg_age_for_calving_2 = life_cycle_manager.avg_age_for_calving["2"]
        avg_age_for_calving_3 = life_cycle_manager.avg_age_for_calving["3"]
        avg_age_for_calving_greater_than_3 = life_cycle_manager.avg_age_for_calving["greater_than_3"]
        om.add_variable("avg_age_for_calving_1", avg_age_for_calving_1, info_map)
        om.add_variable("avg_age_for_calving_2", avg_age_for_calving_2, info_map)
        om.add_variable("avg_age_for_calving_3", avg_age_for_calving_3, info_map)
        om.add_variable("avg_age_for_calving_greater_than_3", avg_age_for_calving_greater_than_3, info_map)
        om.add_variable("cull_reason_stats", life_cycle_manager.cull_reason_stats, info_map)

    def report_sold_animal_information(sold_animals: List[HeiferII | HeiferIII | Cow]) -> None:
        """
        Adds a dictionary of sold animal information to the output manager.

        Parameters
        ----------
        sold_animals : List[HeiferII|HeiferIII|Cow]
            List of sold animal objects.

        """
        info_map = {
            "class": "LifeCycleManager",
            "function": "daily_update",
        }
        sold_report = {
            "animal_id": [],
            "animal_type": [],
            "body_weight": [],
            "cull_reason": [],
            "days_in_milk": [],
            "parity": [],
        }
        for animal in sold_animals:
            sold_report["animal_id"].append(animal.id)
            sold_report["animal_type"].append(animal.__class__.__name__)
            sold_report["body_weight"].append(animal.body_weight)
            if hasattr(animal, "cull_reason"):
                sold_report["cull_reason"].append(animal.cull_reason)
            else:
                sold_report["cull_reason"].append("cull_reason_not_set")
            if hasattr(animal, "days_in_milk"):
                sold_report["days_in_milk"].append(animal.days_in_milk)
            else:
                sold_report["days_in_milk"].append("NA")
            if hasattr(animal, "calves"):
                sold_report["parity"].append(animal.calves)
            else:
                sold_report["parity"].append("NA")
        om.add_variable("sold_report", sold_report, info_map)

    def report_305d_milk(animal_manager):
        """
        Adds herd mean of latest_milk_production_305days to output manager,
        though only for lactating cows with nonzero values.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of Animalmanager class.

        """
        info_map = {
            "class": "cow",
            "function": "update_milk_production_history",
        }
        milk_history_list = [cow.latest_milk_production_305days for cow in animal_manager.cows if cow.is_lactating]
        nonzero_milk_history_list = [x for x in milk_history_list if x != 0.0]
        milk_production_305days_herd_mean = ""
        if nonzero_milk_history_list:
            milk_production_305days_herd_mean = np.mean(nonzero_milk_history_list)
        om.add_variable("milk_production_305days_herd_mean", milk_production_305days_herd_mean, info_map)
