from typing import Dict, List, Any
import numpy as np
import sys

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.animal_combinations import AnimalCombination
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.feed import Feed

om = OutputManager()


class AnimalModuleReporter:
    @classmethod
    def data_padder(
        cls,
        reference_variable: str,
        full_variable_to_add: str,
        thing_to_add: Any,
        simulation_day: int,
        info_map: Dict[str, Any],
    ) -> None:
        """
        Parameters
        ----------
        reference_variable : str
            The "reference" variable name as found in om.variables_pool. In the case of a pen, this should be pen 0 (as it will always be instantiated at the start of the simulation).
        full_variable_to_add: str
            The variable name as found in om.variables_pool.
        thing_to_add : Any
            The variable data to pad the om.variables_pool with.
        simulation_day: int
            The day of the simulation.
        info_map: Dict[str, Any]
            The info_map to use when padding.

        """
        if simulation_day > 0 and reference_variable in om.variables_pool:
            if full_variable_to_add in om.variables_pool:
                current_output_length = len(list(om.variables_pool[full_variable_to_add].values())[0])
            else:
                current_output_length = 0
            length_difference = len(list(om.variables_pool[reference_variable].values())[0]) - current_output_length
            if length_difference > 1:
                short_variable_to_add = full_variable_to_add[full_variable_to_add.rfind(".") + 1 :]
                for _ in range(0, length_difference - 1):
                    om.add_variable(
                        short_variable_to_add,
                        thing_to_add,
                        info_map=info_map,
                    )


    @classmethod
    def report_daily_animal_population(cls, animal_manager) -> None:
        """
        Adds daily totals for animal types to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_animal_population.__name__,
            "data_origin": [("AnimalManager", "daily_updates")],
        }
        om.add_variable("sim_day", animal_manager.simulation_day, dict(info_map, **{"units": "simulation day"}))
        om.add_variable(
            "num_animals",
            len(animal_manager.calves)
            + len(animal_manager.heiferIs)
            + len(animal_manager.heiferIIs)
            + len(animal_manager.heiferIIIs)
            + len(animal_manager.cows),
            dict(info_map, **{"units": "animals"}),
        )
        om.add_variable("num_calves", len(animal_manager.calves), dict(info_map, **{"units": "animals"}))
        om.add_variable("num_heiferIs", len(animal_manager.heiferIs), dict(info_map, **{"units": "animals"}))
        om.add_variable("num_heiferIIs", len(animal_manager.heiferIIs), dict(info_map, **{"units": "animals"}))
        om.add_variable("num_heiferIIIs", len(animal_manager.heiferIIIs), dict(info_map, **{"units": "animals"}))
        om.add_variable(
            "num_lactating_cows",
            len([cow for cow in animal_manager.cows if cow.is_lactating]),
            dict(info_map, **{"units": "animals"}),
        )
        om.add_variable(
            "num_dry_cows",
            len([cow for cow in animal_manager.cows if not cow.is_lactating]),
            dict(info_map, **{"units": "animals"}),
        )
        om.add_variable("num_cows_total", len(animal_manager.cows), dict(info_map, **{"units": "animals"}))

    @classmethod
    def report_milk(cls, pen: Pen, simulation_day: int) -> None:
        """
        Adds milk information for all cows in pen to output manager.

        Parameters
        ----------
        pen : Pen
            Individual Pen.
        simulation_day : int
            Day of simulation.

        """
        units = {
            "days_in_milk": "days",
            "estimated_daily_milk_produced": "kg/day",
            "milk_protein": "kg/day",
            "milk_fat": "kg/day",
            "milk_lactose": "kg/day",
            "lactating": "unitless",
            "parity": "unitless",
            "cow_id": "unitless",
            "pen_id": "unitless",
            "simulation_day": "simulation day",
        }

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_milk.__name__,
            "data_origin": [("Cow", "milking_update")],
            "units": units,
        }

        for animal in list(pen.animals_in_pen.values()):
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

    @classmethod
    def report_ration_interval_data(cls, pen_list: List[Pen], feed: Feed, simulation_day: int) -> None:
        """
        For each pen, adds ration per animal and other supply reports, to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of class AnimalManager.
        feed : Feed
            Instance of class Feed.
        simulation_day : int
            Day of simulation.
        """

        for pen in pen_list:
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
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_ration_interval_data.__name__,
                "data_origin": [("AnimalManager", "_calc_ration_at_interval")],
                "number_animals_in_pen": len(pen.animals_in_pen),
                "simulation_day": simulation_day,
            }
            nutrient_amount_units = {
                "dm": "kg/animal",
                "CP": "percent of DM",
                "ADF": "percent of DM",
                "NDF": "percent of DM",
                "lignin": "percent of DM",
                "ash": "percent of DM",
                "phosphorus": "percent of DM",
                "potassium": "percent of DM",
                "N": "percent of DM",
            }
            classname = AnimalModuleReporter.__name__
            funcname = AnimalModuleReporter.report_ration_interval_data.__name__
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_nutrient_amount_pen_0_CALF",
                f"{classname}.{funcname}.ration_nutrient_amount_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
            )
            om.add_variable(
                f"ration_nutrient_amount_pen_{pen.id}_{pen.animal_combination.name}",
                nutrient_amount,
                dict(info_map, **{"units": nutrient_amount_units}),
            )
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.MEdiet_pen_0_CALF",
                f"{classname}.{funcname}.MEdiet_pen_{pen.id}_{pen.animal_combination.name}",
                0,
                simulation_day,
                info_map,
            )
            om.add_variable(
                f"MEdiet_pen_{pen.id}_{pen.animal_combination.name}",
                pen.MEdiet,
                dict(info_map, **{"units": "kg"}),
            )
            avg_nutrient_rqmts_units = {
                "NEmaint_requirement": "Mcal",
                "NEa_requirement": "Mcal",
                "NEg_requirement": "Mcal",
                "NEpreg_requirement": "Mcal",
                "NEl_requirement": "Mcal",
                "MP_requirement": "g",
                "Ca_requirement": "g",
                "P_req": "g",
                "DMIest_requirement": "kg",
                "avg_BW": "kg",
                "avg_milk_production_reduction_pen": "kg/animal",
            }
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.avg_rqmts_pen_0_CALF",
                f"{classname}.{funcname}.avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
            )
            om.add_variable(
                f"avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}",
                pen.avg_nutrient_rqmts,
                dict(info_map, **{"units": avg_nutrient_rqmts_units}),
            )
            ration_per_animal_units = {key: "kg" for key in ration_per_animal.keys()}
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_per_animal_for_pen_0_CALF",
                f"{classname}.{funcname}.ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
            )
            om.add_variable(
                f"ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_per_animal,
                dict(info_map, **{"units": ration_per_animal_units}),
            )
            if pen.animal_combination != AnimalCombination.CALF:
                ration_supply_report_units = {
                    "ME": "Mcal/kg",
                    "DE": "Mcal/kg",
                    "NE_maintenance_and_activity": "Mcal/kg",
                    "NE_lactation": "Mcal/kg",
                    "NE_growth": "Mcal/kg",
                    "calcium": "percent of DM",
                    "phosphorus": "percent of DM",
                    "fat": "g",
                    "fat_percentage": "percent",
                    "forage_NDF": "percent",
                }
                ration_supply_report = RationReporter.report_ration_supply(
                    pen.ration_per_animal,
                    feed.available_feeds,
                    ration_report,
                    pen.avg_nutrient_rqmts["avg_BW"],
                )
                AnimalModuleReporter.data_padder(
                    f"{classname}.{funcname}.ration_supply_report_for_pen_0_CALF",
                    f"{classname}.{funcname}.ration_supply_report_for_pen_{pen.id}_{pen.animal_combination.name}",
                    {},
                    simulation_day,
                    info_map,
                )
                om.add_variable(
                    f"ration_supply_report_for_pen_{pen.id}_{pen.animal_combination.name}",
                    ration_supply_report,
                    dict(info_map, **{"units": ration_supply_report_units}),
                )

    @classmethod
    def report_daily_ration(cls, animal_manager, available_feeds: Dict[str, Dict[str, Any]]) -> None:
        """
        Adds ration totals as fed to each pen to output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager class.
        available_feeds : Dict[str, Dict[str, Any]]
            Available feeds dictionary from the Feed class object.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_ration.__name__,
            "data_origin": [("AnimalModuleReporter", "report_daily_ration")],
        }
        for pen in animal_manager.all_pens:
            ration_per_animal = pen.ration_per_animal.copy()
            del ration_per_animal["status"]
            del ration_per_animal["objective"]
            ration_total = {}
            ration_total["dry_matter_intake_total"] = 0
            ration_total["byproducts_total"] = 0
            for key in ration_per_animal.keys():
                if key != "status" and key != "objective":
                    ration_total[key] = pen.ration_per_animal[key] * len(pen.animals_in_pen)
                    ration_total["dry_matter_intake_total"] += ration_total[key]
                    if available_feeds[key]["Fd_Category"] == "By-Product/Other":
                        ration_total["byproducts_total"] += ration_total[key]

            AnimalModuleReporter.report_daily_feed_emissions(
                ration_total, pen.id, pen.animal_combination.name, animal_manager
            )
            ration_total_units = {key: "kg" for key in ration_total.keys()}
            classname = AnimalModuleReporter.__name__
            funcname = AnimalModuleReporter.report_daily_ration.__name__
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_daily_feed_totals_for_pen_0_CALF",
                f"{classname}.{funcname}.ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                animal_manager.simulation_day,
                info_map,
            )
            om.add_variable(
                f"ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_total,
                dict(info_map, **{"units": ration_total_units}),
            )

    @classmethod
    def report_daily_feed_emissions(
        cls,
        ration_total: dict[str, float],
        pen_id: int,
        pen_animal_name: str,
        animal_manager,
    ) -> None:
        """
        Adds emissions totals from purchased feeds on a pen / feed basis.

        Parameters
        ----------
        ration_total : dict[str, float]
           Total amounts of dry matter per feed type fed to the pen.
        pen_id : int
            The unique number identifying a pen.
        pen_animal_name : str
            The name of the animal combination in a pen.
        animal_manager : AnimalManager
            The AnimalManager instance being reported.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_feed_emissions.__name__,
            "data_origin": [("FeedEmissionsEstimator", "create_daily_purchased_feed_emissions_report")],
        }
        daily_feed_emissions = animal_manager.feeds_emissions_estimator.create_daily_purchased_feed_emissions_report(
            ration_total
        )
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_daily_feed_emissions.__name__
        AnimalModuleReporter.data_padder(
            f"{classname}.{funcname}.pen_0_animal_CALF_feed_emissions",
            f"{classname}.{funcname}.pen_{pen_id}_animal_{pen_animal_name}_feed_emissions",
            {},
            animal_manager.simulation_day,
            info_map,
        )
        om.add_variable(
            f"pen_{pen_id}_animal_{pen_animal_name}_feed_emissions",
            daily_feed_emissions,
            dict(info_map, **{"units": "kg CO2 / kg DM"}),
        )

    @classmethod
    def report_animal_module_manure(
        cls,
        manure_excretions_output_data: dict[str, dict[str | AnimalManureExcretions]],
    ) -> None:
        """
        Generate detailed report of manure properties in the Animal Module.

        Parameters
        ----------
        manure_excretions_output_data : dict[str, dict[str | AnimalManureExcretions]]
            Dictionary mapping prefixes to animal manure data.

        """
        manure_value_units = {
            "urea": "g/L",
            "urine": "kg",
            "total_ammoniacal_nitrogen_concentration": "g/L",
            "urine_nitrogen": "kg",
            "manure_nitrogen": "kg",
            "manure_mass": "kg",
            "total_solids": "kg",
            "degradable_volatile_solids": "kg",
            "non_degradable_volatile_solids": "kg",
            "inorganic_phosphorus_fraction": "unitless",
            "organic_phosphorus_fraction": "unitless",
            "non_water_inorganic_phosphorus_fraction": "unitless",
            "non_water_organic_phosphorus_fraction": "unitless",
            "phosphorus": "g",
            "phosphorus_fraction": "unitless",
            "potassium": "g",
            "enteric_methane_g": "g/day",
        }
        for output_data_dict in manure_excretions_output_data.values():
            for manure_property, manure_value in output_data_dict["manure"].items():
                info_map = {
                    "class": AnimalModuleReporter.__name__,
                    "function": AnimalModuleReporter.report_animal_module_manure.__name__,
                    "data_origin": [("AnimalManager", "daily_updates")],
                }
                om.add_variable(
                    f'{output_data_dict["prefix"]}_{str(manure_property)}',
                    manure_value,
                    dict(info_map, **{"units": manure_value_units}),
                )

    @classmethod
    def report_pen_manure(cls, pen: Pen) -> None:
        """
        Adds pen manure data to output manager.

        Parameters
        ----------
        pen : Pen
            Current pen.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_pen_manure.__name__,
            "data_origin": [("Pen", "calc_manure")],
            "pen_id": pen.id,
            "pen_animal_combination": pen.animal_combination._name_,
            "units": {
                "urea": "g/L",
                "urine": "kg",
                "total_ammoniacal_nitrogen_concentration": "g/L",
                "urine_nitrogen": "kg",
                "manure_nitrogen": "kg",
                "manure_mass": "kg",
                "total_solids": "kg",
                "degradable_volatile_solids": "kg",
                "non_degradable_volatile_solids": "kg",
                "inorganic_phosphorus_fraction": "unitless",
                "organic_phosphorus_fraction": "unitless",
                "non_water_inorganic_phosphorus_fraction": "unitless",
                "non_water_organic_phosphorus_fraction": "unitless",
                "phosphorus": "g",
                "phosphorus_fraction": "unitless",
                "potassium": "g",
                "enteric_methane_g": "g/day",
            },
        }
        om.add_variable("pen_manure_data", pen.manure, info_map)

    @classmethod
    def report_pen_manure_properties(cls, pen: Pen, simulation_day: int) -> None:
        """
        Adds pen manure properties to output manager.

        Parameters
        ----------
        pen : Pen
            Current pen.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_pen_manure_properties.__name__,
            "data_origin": [("Pen", "calc_total_manure")],
        }
        manure_value_units = {
            "urea": "g/L",
            "urine": "kg",
            "total_ammoniacal_nitrogen_concentration": "g/L",
            "urine_nitrogen": "kg",
            "manure_nitrogen": "kg",
            "manure_mass": "kg",
            "total_solids": "kg",
            "degradable_volatile_solids": "kg",
            "non_degradable_volatile_solids": "kg",
            "inorganic_phosphorus_fraction": "unitless",
            "organic_phosphorus_fraction": "unitless",
            "non_water_inorganic_phosphorus_fraction": "unitless",
            "non_water_organic_phosphorus_fraction": "unitless",
            "phosphorus": "g",
            "phosphorus_fraction": "unitless",
            "potassium": "g",
            "enteric_methane_g": "g/day",
        }
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_pen_manure_properties.__name__
        for manure_property, manure_value in pen.manure.items():
            reference_variable = f"{classname}.{funcname}.pen_0_daily_{str(manure_property)}"
            variable_to_add = f"{classname}.{funcname}.pen_{pen.id}_daily_{str(manure_property)}"
            AnimalModuleReporter.data_padder(reference_variable, variable_to_add, 0, simulation_day, info_map)
            om.add_variable(
                f"pen_{pen.id}_daily_{str(manure_property)}",
                manure_value,
                dict(info_map, **{"units": manure_value_units}),
            )

    @classmethod
    def report_life_cycle_manager_data(cls, life_cycle_manager: LifeCycleManager, sim_day: int) -> None:
        """
        Adds daily life cycle data to output manager.

        life_cycle_manager : LifeCycleManager
            Active instance of LifeCycleManager.
        sim_day : int
            Day of simulation.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_life_cycle_manager_data.__name__,
            "data_origin": [("LifeCycleManager", "daily_update")],
        }
        om.add_variable(
            "sold_heiferIII_oversupply_num",
            life_cycle_manager.sold_heiferIII_oversupply_num,
            dict(info_map, **{"units": "animals"}),
        )
        om.add_variable(
            "bought_heifer_num", life_cycle_manager.bought_heifer_num, dict(info_map, **{"units": "animals"})
        )
        om.add_variable(
            "sold_heiferII_num", life_cycle_manager.sold_heiferII_num, dict(info_map, **{"units": "animals"})
        )
        om.add_variable(
            "cow_herd_exit_num", life_cycle_manager.cow_herd_exit_num, dict(info_map, **{"units": "animals"})
        )
        om.add_variable("sold_cow_num", life_cycle_manager.sold_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable(
            "GnRH_injection_num_h", life_cycle_manager.GnRH_injection_num_h, dict(info_map, **{"units": "injections"})
        )
        om.add_variable(
            "GnRH_injection_num", life_cycle_manager.GnRH_injection_num, dict(info_map, **{"units": "injections"})
        )
        om.add_variable(
            "PGF_injection_num", life_cycle_manager.PGF_injection_num, dict(info_map, **{"units": "injections"})
        )
        om.add_variable(
            "PGF_injection_num_h", life_cycle_manager.PGF_injection_num_h, dict(info_map, **{"units": "injections"})
        )
        om.add_variable("ai_num", life_cycle_manager.ai_num, dict(info_map, **{"units": "AIs"}))
        om.add_variable("preg_check_num", life_cycle_manager.preg_check_num, dict(info_map, **{"units": "preg checks"}))
        om.add_variable(
            "preg_check_num_h", life_cycle_manager.preg_check_num_h, dict(info_map, **{"units": "preg checks"})
        )
        om.add_variable("sold_calf_num", life_cycle_manager.sold_calf_num, dict(info_map, **{"units": "animals"}))
        om.add_variable(
            "daily_milk_production", life_cycle_manager.daily_milk_production, dict(info_map, **{"units": "kg/day"})
        )
        om.add_variable(
            "dry_cows_daily_milk_production",
            life_cycle_manager.dry_cows_daily_milk_production,
            dict(info_map, **{"units": "kg/day"}),
        )
        om.add_variable(
            "herd_milk_fat_percent", life_cycle_manager.herd_milk_fat_percent, dict(info_map, **{"units": "unitless"})
        )
        om.add_variable("herd_milk_fat_kg", life_cycle_manager.herd_milk_fat_kg, dict(info_map, **{"units": "kg/day"}))
        om.add_variable(
            "dry_cows_milk_fat_kg", life_cycle_manager.dry_cows_milk_fat_kg, dict(info_map, **{"units": "kg/day"})
        )
        om.add_variable(
            "herd_milk_protein_kg", life_cycle_manager.herd_milk_protein_kg, dict(info_map, **{"units": "kg/day"})
        )
        om.add_variable(
            "herd_milk_protein_percent",
            life_cycle_manager.herd_milk_protein_percent,
            dict(info_map, **{"units": "unitless"}),
        )
        om.add_variable(
            "dry_cows_milk_protein_kg",
            life_cycle_manager.dry_cows_milk_protein_kg,
            dict(info_map, **{"units": "kg/day"}),
        )
        om.add_variable("open_cow_num", life_cycle_manager.open_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable("vwp_cow_num", life_cycle_manager.vwp_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable("preg_cow_num", life_cycle_manager.preg_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable("milking_cow_num", life_cycle_manager.milking_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable("dry_cow_num", life_cycle_manager.dry_cow_num, dict(info_map, **{"units": "animals"}))
        om.add_variable("avg_days_in_milk", life_cycle_manager.avg_days_in_milk, dict(info_map, **{"units": "days"}))
        om.add_variable("avg_days_in_preg", life_cycle_manager.avg_days_in_preg, dict(info_map, **{"units": "days"}))
        om.add_variable(
            "avg_cow_body_weight", life_cycle_manager.avg_cow_body_weight, dict(info_map, **{"units": "kg"})
        )
        om.add_variable("avg_parity_num", life_cycle_manager.avg_parity_num, dict(info_map, **{"units": "unitless"}))
        om.add_variable(
            "avg_calving_interval", life_cycle_manager.avg_calving_interval, dict(info_map, **{"units": "days"})
        )
        om.add_variable(
            "avg_breeding_to_preg_time",
            life_cycle_manager.avg_breeding_to_preg_time,
            dict(info_map, **{"units": "days"}),
        )
        om.add_variable(
            "avg_heifer_culling_age",
            life_cycle_manager.avg_heifer_culling_age,
            dict(info_map, **{"units": "days"}),
        )
        om.add_variable(
            "avg_cow_culling_age", life_cycle_manager.avg_cow_culling_age, dict(info_map, **{"units": "days"})
        )
        om.add_variable(
            "avg_mature_body_weight",
            life_cycle_manager.avg_mature_body_weight,
            dict(info_map, **{"units": "kg"}),
        )
        om.add_variable("sim_day", sim_day, dict(info_map, **{"units": "days"}))
        parity_1 = life_cycle_manager.num_cow_for_parity["1"]
        parity_2 = life_cycle_manager.num_cow_for_parity["2"]
        parity_3 = life_cycle_manager.num_cow_for_parity["3"]
        parity_greater_than_3 = life_cycle_manager.num_cow_for_parity["greater_than_3"]
        om.add_variable("num_cow_for_parity_1", parity_1, dict(info_map, **{"units": "animals"}))
        om.add_variable("num_cow_for_parity_2", parity_2, dict(info_map, **{"units": "animals"}))
        om.add_variable("num_cow_for_parity_3", parity_3, dict(info_map, **{"units": "animals"}))
        om.add_variable(
            "num_cow_for_parity_greater_than_3", parity_greater_than_3, dict(info_map, **{"units": "animals"})
        )
        calving_to_preg_time_1 = life_cycle_manager.avg_calving_to_preg_time["1"]
        calving_to_preg_time_2 = life_cycle_manager.avg_calving_to_preg_time["2"]
        calving_to_preg_time_3 = life_cycle_manager.avg_calving_to_preg_time["3"]
        calving_to_preg_time_greater_than_3 = life_cycle_manager.avg_calving_to_preg_time["greater_than_3"]
        om.add_variable("calving_to_preg_time_1", calving_to_preg_time_1, dict(info_map, **{"units": "days"}))
        om.add_variable("calving_to_preg_time_2", calving_to_preg_time_2, dict(info_map, **{"units": "days"}))
        om.add_variable("calving_to_preg_time_3", calving_to_preg_time_3, dict(info_map, **{"units": "days"}))
        om.add_variable(
            "calving_to_preg_time_greater_than_3",
            calving_to_preg_time_greater_than_3,
            dict(info_map, **{"units": "days"}),
        )
        avg_age_for_calving_1 = life_cycle_manager.avg_age_for_calving["1"]
        avg_age_for_calving_2 = life_cycle_manager.avg_age_for_calving["2"]
        avg_age_for_calving_3 = life_cycle_manager.avg_age_for_calving["3"]
        avg_age_for_calving_greater_than_3 = life_cycle_manager.avg_age_for_calving["greater_than_3"]
        om.add_variable("avg_age_for_calving_1", avg_age_for_calving_1, dict(info_map, **{"units": "days"}))
        om.add_variable("avg_age_for_calving_2", avg_age_for_calving_2, dict(info_map, **{"units": "days"}))
        om.add_variable("avg_age_for_calving_3", avg_age_for_calving_3, dict(info_map, **{"units": "days"}))
        om.add_variable(
            "avg_age_for_calving_greater_than_3",
            avg_age_for_calving_greater_than_3,
            dict(info_map, **{"units": "days"}),
        )
        cull_reason_stats_units = {
            animal_constants.DEATH_CULL: "unitless",
            animal_constants.LOW_PROD_CULL: "unitless",
            animal_constants.LAMENESS_CULL: "unitless",
            animal_constants.INJURY_CULL: "unitless",
            animal_constants.MASTITIS_CULL: "unitless",
            animal_constants.DISEASE_CULL: "unitless",
            animal_constants.UDDER_CULL: "unitless",
            animal_constants.UNKNOWN_CULL: "unitless",
        }
        om.add_variable(
            "cull_reason_stats",
            life_cycle_manager.cull_reason_stats,
            dict(info_map, **{"units": cull_reason_stats_units}),
        )

    @classmethod
    def report_daily_pen_total(cls, simulation_day: int, pen_list: List[Pen]) -> None:
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_daily_pen_total.__name__
        info_map = {
            "class": classname,
            "function": funcname,
        }
        for pen in pen_list:
            variable_to_add = f"{classname}.{funcname}.number_of_animals_in_pen_{pen.id}_{pen.animal_combination.name}"
            reference_variable = f"{classname}.{funcname}.number_of_animals_in_pen_0_CALF"
            AnimalModuleReporter.data_padder(reference_variable, variable_to_add, 0, simulation_day, info_map)
            om.add_variable(
                f"number_of_animals_in_pen_{pen.id}_{pen.animal_combination.name}",
                len(pen.animals_in_pen),
                info_map,
            )

    @classmethod
    def report_sold_animal_information(cls, animal_manager) -> None:
        """
        Adds a dictionary of sold animal information to the output manager.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of Class AnimalManager.

        """
        sold_animals = (
            animal_manager.life_cycle_manager.sold_calves
            + animal_manager.life_cycle_manager.sold_heiferIIs
            + animal_manager.life_cycle_manager.sold_heiferIIIs
            + list(
                filter(
                    lambda cow: cow.cull_reason != animal_constants.DEATH_CULL,
                    animal_manager.life_cycle_manager.sold_and_died_cows,
                )
            )
        )

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_sold_animal_information.__name__,
        }
        for animal in sold_animals:
            om.add_variable("animal_id", animal.id, dict(info_map, **{"units": "unitless"}))
            om.add_variable("animal_type", animal.__class__.__name__, dict(info_map, **{"units": "unitless"}))
            om.add_variable("body_weight", animal.body_weight, dict(info_map, **{"units": "kg"}))

            if hasattr(animal, "sold_at_day"):
                om.add_variable("sold_day", animal.sold_at_day, dict(info_map, **{"units": "simulation day"}))
            else:
                om.add_variable("sold_day", "NA", dict(info_map, **{"units": "simulation day"}))

            if hasattr(animal, "cull_reason"):
                om.add_variable("cull_reason", animal.cull_reason, dict(info_map, **{"units": "unitless"}))
            else:
                om.add_variable("cull_reason", "NA", dict(info_map, **{"units": "unitless"}))

            if hasattr(animal, "days_in_milk"):
                om.add_variable("days_in_milk", animal.days_in_milk, dict(info_map, **{"units": "days"}))
            else:
                om.add_variable("days_in_milk", "NA", dict(info_map, **{"units": "days"}))

            if hasattr(animal, "calves"):
                om.add_variable("parity", animal.calves, dict(info_map, **{"units": "unitless"}))
            else:
                om.add_variable("parity", "NA", dict(info_map, **{"units": "unitless"}))

    @classmethod
    def report_sold_animal_information_sort_by_sell_day(cls, sold_animals, report_name: str, total_days: int) -> None:
        """
        Adds a dictionary of sold animal information to the output manager on daily basis.

        Parameters
        ----------
        sold_animals : list[object]
            List of sold animals.
        report_name : str
            The string to be appended to the variable being reported to the OM.
        total_days : int
            The total number of days in the simulation
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day.__name__,
        }

        sold_at_day_min: int = sys.maxsize
        sold_at_day_max: int = 0
        daily_sell: Dict[int, List[object]] = {}

        for animal in sold_animals:
            if animal.sold_at_day < sold_at_day_min:
                sold_at_day_min = animal.sold_at_day
            if animal.sold_at_day > sold_at_day_max:
                sold_at_day_max = animal.sold_at_day
            if daily_sell.get(animal.sold_at_day):
                daily_sell[animal.sold_at_day].append(animal)
            else:
                daily_sell[animal.sold_at_day] = [animal]

        om.add_variable(
            f"{report_name}_first_sell_event", sold_at_day_min, dict(info_map, **{"units": "simulation day"})
        )
        om.add_variable(
            f"{report_name}_last_sell_event", sold_at_day_max, dict(info_map, **{"units": "simulation day"})
        )
        for day in range(1, total_days + 1):
            if daily_sell.get(day):
                sold_count = len(daily_sell[day])
                sold_weight = sum(sold_animal.body_weight for sold_animal in daily_sell[day])
                om.add_variable(f"{report_name}_sold_count", sold_count, dict(info_map, **{"units": "animals"}))
                om.add_variable(f"{report_name}_sold_weight", sold_weight, dict(info_map, **{"units": "kg"}))
            else:
                om.add_variable(f"{report_name}_sold_count", 0, dict(info_map, **{"units": "animals"}))
                om.add_variable(f"{report_name}_sold_weight", 0, dict(info_map, **{"units": "kg"}))

    @classmethod
    def report_305d_milk(cls, animal_manager) -> None:
        """
        Adds herd mean of latest_milk_production_305days to output manager,
        though only for lactating cows with nonzero values.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of Animalmanager class.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_305d_milk.__name__,
            "data_origin": [("Cow", "update_milk_production_history")],
        }
        milk_history_list = [cow.latest_milk_production_305days for cow in animal_manager.cows if cow.is_lactating]
        nonzero_milk_history_list = [x for x in milk_history_list if x != 0.0]
        milk_production_305days_herd_mean = ""
        if nonzero_milk_history_list:
            milk_production_305days_herd_mean = np.mean(nonzero_milk_history_list)
        om.add_variable(
            "milk_production_305days_herd_mean",
            milk_production_305days_herd_mean,
            dict(info_map, **{"units": "kg"}),
        )

    @classmethod
    def report_daily_reports(cls, animal_manager, available_feeds: Dict[str, Dict[str, Any]]) -> None:
        """
        Calls all reporter methods that should happen at the end of each day.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager class.
        available_feeds : Dict[str, Dict[str, Any]]
            Available feeds dictionary from the Feed class object.
        """
        AnimalModuleReporter.report_daily_animal_population(animal_manager)
        AnimalModuleReporter.report_life_cycle_manager_data(
            animal_manager.life_cycle_manager, animal_manager.simulation_day
        )
        AnimalModuleReporter.report_daily_ration(animal_manager, available_feeds)
        AnimalModuleReporter.report_daily_pen_total(animal_manager.simulation_day, animal_manager.all_pens)
        AnimalModuleReporter.report_305d_milk(animal_manager)
        for pen in animal_manager.all_pens:
            AnimalModuleReporter.report_pen_manure_properties(pen, animal_manager.simulation_day)
            if pen.animal_combination.name == "LAC_COW":
                AnimalModuleReporter.report_milk(pen, animal_manager.simulation_day)

    @classmethod
    def report_end_of_simulation(cls, animal_manager, total_days: int) -> None:
        """
        Calls all reporter methods that should happen at the end of the simulation.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager class.
        total_days : int
            The total number of days in the simulation
        """
        AnimalModuleReporter.report_sold_animal_information(animal_manager)
        AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
            animal_manager.life_cycle_manager.sold_calves,
            "sold_calves",
            total_days,
        )
        AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
            animal_manager.life_cycle_manager.sold_heiferIIs, "heiferII", total_days
        )
        AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
            animal_manager.life_cycle_manager.sold_heiferIIIs, "heiferIII", total_days
        )
        AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
            animal_manager.life_cycle_manager.sold_and_died_cows,
            "sold_and_died_cows",
            total_days,
        )
        AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
            animal_manager.life_cycle_manager.sold_cows,
            "sold_cows",
            total_days,
        )
