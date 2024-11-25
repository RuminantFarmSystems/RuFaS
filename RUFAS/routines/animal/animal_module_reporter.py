import sys
from typing import Any, Dict, List, Sequence

import numpy as np

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.enums import AnimalCombination
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.feed import Feed
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits

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
        units: Dict[str, MeasurementUnits] | MeasurementUnits,
    ) -> None:
        """
        Pads a variable in OutputManager for entries that it "missed" relative to another variable.

        This is meant to be used prior to the addition of a variable to OutputManager, only in the cases where there
        may be a mismatch in variable lengths.
        A common case would be when a variable is stored in OutputManager by pen, and additional pens are created
        during the simulation.

        This method checks the length of a reference variable (in the previous example, Pen 0) in OutputManager and the
        variable of interest (in the previous example, a newly created Pen 15), and if there is a
        mismatch greater than one, it makes the number of calls to OutputManager necessary to ensure the length of the
        variable to add is one less than the reference variable using "blank" data.

        Parameters
        ----------
        reference_variable : str
            The "reference" variable name as found in om.variables_pool. In the case of a pen, this should be pen 0 (as
            it will always be instantiated at the start of the simulation).
        full_variable_to_add: str
            The variable name as found in om.variables_pool.
        thing_to_add : Any
            The variable data to pad the om.variables_pool with.
        simulation_day: int
            The day of the simulation.
        info_map: Dict[str, Any]
            The info_map to use when padding.
        units: Dict[str, str] | str
            Units for the variable being added, in the format provided in the main call to add_variable,
            (e.g. the one following the call of data_padder).

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
                        info_map=dict(info_map, **{"units": units}),
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
        om.add_variable(
            "sim_day", animal_manager.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY})
        )
        om.add_variable(
            "num_animals",
            len(animal_manager.calves)
            + len(animal_manager.heiferIs)
            + len(animal_manager.heiferIIs)
            + len(animal_manager.heiferIIIs)
            + len(animal_manager.cows),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable("num_calves", len(animal_manager.calves), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_heiferIs", len(animal_manager.heiferIs), dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "num_heiferIIs", len(animal_manager.heiferIIs), dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "num_heiferIIIs",
            len(animal_manager.heiferIIIs),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_lactating_cows",
            len([cow for cow in animal_manager.cows if cow.is_lactating]),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_dry_cows",
            len([cow for cow in animal_manager.cows if not cow.is_lactating]),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_total", len(animal_manager.cows), dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )

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
            "days_in_milk": MeasurementUnits.DAYS,
            "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY,
            "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY,
            "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY,
            "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY,
            "lactating": MeasurementUnits.UNITLESS,
            "parity": MeasurementUnits.UNITLESS,
            "cow_id": MeasurementUnits.UNITLESS,
            "pen_id": MeasurementUnits.UNITLESS,
            "simulation_day": MeasurementUnits.SIMULATION_DAY,
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
            milk_data_update["pen_id"] = animal.pen_history[-1]["pen"]
            milk_data_update["simulation_day"] = simulation_day

            om.add_variable("milk_data_at_milk_update", milk_data_update, info_map)

    @classmethod
    def report_ration_interval_data(cls, pen: Pen, feed: Feed, simulation_day: int) -> None:
        """
        For each pen, adds ration per animal and other supply reports, to output manager.

        Parameters
        ----------
        pen : Pen
            Pen object.
        feed : Feed
            Instance of class Feed.
        simulation_day : int
            Day of simulation.
        """

        if pen.is_populated:
            nutrient_amount = pen.ration_nutrient_amount
            nutrient_conc = pen.ration_nutrient_conc
            ration_per_animal = pen.ration_per_animal.copy()
            for non_numeric_key in ["status", "objective"]:
                if non_numeric_key in ration_per_animal:
                    del ration_per_animal[non_numeric_key]
            ration_per_animal["dry_matter_intake_total"] = sum(
                [ration_per_animal[key] for key in ration_per_animal.keys()]
            )
            ration_report = {}
            ration_report["nutrient_amount"] = nutrient_amount
            ration_report["nutrient_conc"] = nutrient_conc

            info_map = {
                "class": AnimalModuleReporter.__name__,
                "function": AnimalModuleReporter.report_ration_interval_data.__name__,
                "data_origin": [("AnimalManager", "_handle_pen_ration")],
                "number_animals_in_pen": len(pen.animals_in_pen),
                "simulation_day": simulation_day,
            }
            nutrient_amount_units = {
                "dm": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "CP": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "ADF": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "NDF": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "lignin": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "ash": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "phosphorus": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "potassium": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "N": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "as_fed": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "EE": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "starch": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "TDN": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "DE": MeasurementUnits.MEGACALORIES,
                "calcium": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
            }
            classname = AnimalModuleReporter.__name__
            funcname = AnimalModuleReporter.report_ration_interval_data.__name__
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_nutrient_amount_pen_0_CALF",
                f"{classname}.{funcname}.ration_nutrient_amount_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
                nutrient_amount_units,
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
                MeasurementUnits.KILOGRAMS,
            )
            om.add_variable(
                f"MEdiet_pen_{pen.id}_{pen.animal_combination.name}",
                pen.MEdiet,
                dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
            )
            avg_nutrient_rqmts_units = {
                "NEmaint_requirement": MeasurementUnits.MEGACALORIES,
                "NEa_requirement": MeasurementUnits.MEGACALORIES,
                "NEg_requirement": MeasurementUnits.MEGACALORIES,
                "NEpreg_requirement": MeasurementUnits.MEGACALORIES,
                "NEl_requirement": MeasurementUnits.MEGACALORIES,
                "MP_requirement": MeasurementUnits.GRAMS,
                "Ca_requirement": MeasurementUnits.GRAMS,
                "P_req": MeasurementUnits.GRAMS,
                "P_req_process": MeasurementUnits.GRAMS,
                "DMIest_requirement": MeasurementUnits.KILOGRAMS,
                "avg_BW": MeasurementUnits.KILOGRAMS,
                "avg_milk_production_reduction_pen": MeasurementUnits.KILOGRAMS_PER_ANIMAL,
                "avg_essential_amino_acid_requirement": MeasurementUnits.GRAMS_PER_DAY,
            }
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.avg_rqmts_pen_0_CALF",
                f"{classname}.{funcname}.avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
                avg_nutrient_rqmts_units,
            )
            om.add_variable(
                f"avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}",
                pen.avg_nutrient_rqmts,
                dict(info_map, **{"units": avg_nutrient_rqmts_units}),
            )
            ration_per_animal_units = {key: MeasurementUnits.KILOGRAMS for key in ration_per_animal.keys()}
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_per_animal_for_pen_0_CALF",
                f"{classname}.{funcname}.ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                simulation_day,
                info_map,
                ration_per_animal_units,
            )
            om.add_variable(
                f"ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_per_animal,
                dict(info_map, **{"units": ration_per_animal_units}),
            )
            if pen.animal_combination != AnimalCombination.CALF:
                ration_supply_report_units = {
                    "ME": MeasurementUnits.MEGACALORIES_PER_KILOGRAM,
                    "DE": MeasurementUnits.MEGACALORIES_PER_KILOGRAM,
                    "NE_maintenance_and_activity": MeasurementUnits.MEGACALORIES_PER_KILOGRAM,
                    "NE_lactation": MeasurementUnits.MEGACALORIES_PER_KILOGRAM,
                    "NE_growth": MeasurementUnits.MEGACALORIES_PER_KILOGRAM,
                    "calcium": MeasurementUnits.PERCENT_OF_DRY_MATTER,
                    "phosphorus": MeasurementUnits.PERCENT_OF_DRY_MATTER,
                    "fat": MeasurementUnits.GRAMS,
                    "fat_percentage": MeasurementUnits.PERCENT,
                    "forage_NDF": MeasurementUnits.PERCENT,
                    "forage_NDF_percent": MeasurementUnits.PERCENT_OF_DRY_MATTER,
                    "metabolizable_protein": MeasurementUnits.GRAMS,
                }
                if pen.ration_per_animal:
                    ration_supply_report = RationReporter.report_ration_supply(
                        pen.ration_per_animal, feed.available_feeds, ration_report, pen.avg_nutrient_rqmts["avg_BW"]
                    )
                else:
                    ration_supply_report = {}
                AnimalModuleReporter.data_padder(
                    f"{classname}.{funcname}.ration_supply_report_for_pen_0_CALF",
                    f"{classname}.{funcname}.ration_supply_report_for_pen_{pen.id}_{pen.animal_combination.name}",
                    {},
                    simulation_day,
                    info_map,
                    ration_supply_report_units,
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
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_daily_ration.__name__
        info_map = {
            "class": classname,
            "function": funcname,
            "data_origin": [(classname, funcname)],
        }
        non_numeric_keys = ["status", "objective"]
        ration_across_pens = {"dry_matter_intake_total": 0, "byproducts_total": 0}
        for pen in animal_manager.all_pens:
            ration_per_pen = {"dry_matter_intake_total": 0, "byproducts_total": 0}
            for key in pen.ration_per_animal.keys():
                if key in non_numeric_keys:
                    continue
                ration_per_pen[key] = pen.ration_per_animal[key] * len(pen.animals_in_pen)
                ration_per_pen["dry_matter_intake_total"] += ration_per_pen[key]
                if available_feeds[key]["Fd_Category"] == "By-Product/Other":
                    ration_per_pen["byproducts_total"] += ration_per_pen[key]

                if key in ration_across_pens:
                    ration_across_pens[key] += ration_per_pen[key]
                else:
                    ration_across_pens[key] = ration_per_pen[key]

            AnimalModuleReporter.report_daily_feed_emissions(
                ration_per_pen, pen.id, pen.animal_combination.name, animal_manager
            )
            units = {key: MeasurementUnits.KILOGRAMS for key in ration_per_pen.keys()}
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.ration_daily_feed_totals_for_pen_0_CALF",
                f"{classname}.{funcname}.ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}",
                {},
                animal_manager.simulation_day,
                info_map,
                units,
            )
            om.add_variable(
                f"ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}",
                ration_per_pen,
                dict(info_map, **{"units": units}),
            )
        units = {key: MeasurementUnits.KILOGRAMS for key in ration_across_pens.keys()}
        om.add_variable(
            "ration_daily_feed_total_across_pens",
            ration_across_pens,
            dict(info_map, **{"units": units}),
        )
        AnimalModuleReporter.report_daily_feed_emissions(ration_across_pens, "ALL", "", animal_manager)

    @classmethod
    def report_daily_feed_emissions(
        cls,
        ration_total: dict[str, float],
        pen_id: int | str,
        pen_animal_name: str,
        animal_manager,
    ) -> None:
        """
        Adds emissions totals from purchased feeds on a pen / feed basis.

        Parameters
        ----------
        ration_total : dict[str, float]
           Total amounts of dry matter per feed type fed to the pen.
        pen_id : int | str
            The unique number identifying a pen. Use `ALL` when the given ration is the sum of mulitple pens' rations.
        pen_animal_name : str
            The name of the animal combination in a pen.
        animal_manager : AnimalManager
            The AnimalManager instance being reported.

        """
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_daily_feed_emissions.__name__
        info_map = {
            "class": classname,
            "function": funcname,
        }
        daily_purchased_feed_emissions = (
            animal_manager.feeds_emissions_estimator.create_daily_purchased_feed_emissions_report(ration_total)
        )
        daily_land_use_change_feed_emissions = (
            animal_manager.feeds_emissions_estimator.create_daily_land_use_change_feed_emissions_report(ration_total)
        )
        if pen_id == "ALL":
            info_map["data_origin"] = [("FeedEmissionsEstimator", "create_daily_purchased_feed_emissions_report")]
            om.add_variable(
                "purchased_feed_emissions_across_pens",
                daily_purchased_feed_emissions,
                dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ}),
            )
            info_map["data_origin"] = [("FeedEmissionsEstimator", "create_daily_land_use_change_feed_emissions_report")]
            om.add_variable(
                "land_use_change_feed_emissions_across_pens",
                daily_land_use_change_feed_emissions,
                dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ}),
            )
        else:
            AnimalModuleReporter.data_padder(
                f"{classname}.{funcname}.pen_0_animal_CALF_feed_emissions",
                f"{classname}.{funcname}.pen_{pen_id}_animal_{pen_animal_name}_feed_emissions",
                {},
                animal_manager.simulation_day,
                info_map,
                MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ,
            )
            info_map["data_origin"] = [("FeedEmissionsEstimator", "create_daily_purchased_feed_emissions_report")]
            om.add_variable(
                f"purchased_feed_emissions_Pen_{pen_id}_animal_{pen_animal_name}_",
                daily_purchased_feed_emissions,
                dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ}),
            )
            info_map["data_origin"] = [("FeedEmissionsEstimator", "create_daily_land_use_change_feed_emissions_report")]
            om.add_variable(
                f"land_use_change_feed_emissions_Pen_{pen_id}_animal_{pen_animal_name}_",
                daily_land_use_change_feed_emissions,
                dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_CARBON_DIOXIDE_EQ}),
            )

    @classmethod
    def report_animal_module_manure(
        cls,
        manure_excretions_output_data: dict[str, dict[str, str | AnimalManureExcretions]],
    ) -> None:
        """
        Generate detailed report of manure properties in the Animal Module.

        Parameters
        ----------
        manure_excretions_output_data : dict[str, dict[str, str | AnimalManureExcretions]]
            Dictionary mapping prefixes to animal manure data.

        """
        manure_value_units = {
            "urea": MeasurementUnits.GRAMS_PER_LITER,
            "urine": MeasurementUnits.KILOGRAMS,
            "urine_nitrogen": MeasurementUnits.KILOGRAMS,
            "manure_nitrogen": MeasurementUnits.KILOGRAMS,
            "manure_total_ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
            "manure_mass": MeasurementUnits.KILOGRAMS,
            "total_solids": MeasurementUnits.KILOGRAMS,
            "degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "inorganic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "organic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "non_water_inorganic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "non_water_organic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "phosphorus": MeasurementUnits.GRAMS,
            "phosphorus_fraction": MeasurementUnits.UNITLESS,
            "potassium": MeasurementUnits.GRAMS,
            "enteric_methane_g": MeasurementUnits.GRAMS_PER_DAY,
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
                    dict(info_map, **{"units": manure_value_units[manure_property]}),
                )

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
            "urea": MeasurementUnits.GRAMS_PER_LITER,
            "urine": MeasurementUnits.KILOGRAMS,
            "manure_total_ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
            "urine_nitrogen": MeasurementUnits.KILOGRAMS,
            "manure_nitrogen": MeasurementUnits.KILOGRAMS,
            "manure_mass": MeasurementUnits.KILOGRAMS,
            "total_solids": MeasurementUnits.KILOGRAMS,
            "degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "inorganic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "organic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "non_water_inorganic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "non_water_organic_phosphorus_fraction": MeasurementUnits.UNITLESS,
            "phosphorus": MeasurementUnits.GRAMS,
            "phosphorus_fraction": MeasurementUnits.UNITLESS,
            "potassium": MeasurementUnits.GRAMS,
            "enteric_methane_g": MeasurementUnits.GRAMS_PER_DAY,
        }
        classname = AnimalModuleReporter.__name__
        funcname = AnimalModuleReporter.report_pen_manure_properties.__name__
        for manure_property, manure_value in pen.manure.items():
            reference_variable = f"{classname}.{funcname}.pen_0_daily_{str(manure_property)}"
            variable_to_add = f"{classname}.{funcname}.pen_{pen.id}_daily_{str(manure_property)}"
            AnimalModuleReporter.data_padder(
                reference_variable, variable_to_add, 0, simulation_day, info_map, manure_value_units
            )
            om.add_variable(
                f"pen_{pen.id}_daily_{str(manure_property)}",
                manure_value,
                dict(info_map, **{"units": manure_value_units[manure_property]}),
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
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "bought_heifer_num",
            life_cycle_manager.bought_heifer_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "sold_heiferII_num",
            life_cycle_manager.sold_heiferII_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "cow_herd_exit_num",
            life_cycle_manager.cow_herd_exit_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "sold_cow_num", life_cycle_manager.sold_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "GnRH_injection_num_h",
            life_cycle_manager.GnRH_injection_num_h,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "GnRH_injection_num",
            life_cycle_manager.GnRH_injection_num,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "PGF_injection_num",
            life_cycle_manager.PGF_injection_num,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "PGF_injection_num_h",
            life_cycle_manager.PGF_injection_num_h,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "ai_num",
            life_cycle_manager.ai_num,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "preg_check_num",
            life_cycle_manager.preg_check_num,
            dict(info_map, **{"units": MeasurementUnits.PREGNANCY_CHECKS}),
        )
        om.add_variable(
            "preg_check_num_h",
            life_cycle_manager.preg_check_num_h,
            dict(info_map, **{"units": MeasurementUnits.PREGNANCY_CHECKS}),
        )
        om.add_variable(
            "sold_calf_num",
            life_cycle_manager.sold_calf_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "daily_milk_production",
            life_cycle_manager.daily_milk_production,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "dry_cows_daily_milk_production",
            life_cycle_manager.dry_cows_daily_milk_production,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_fat_percent",
            life_cycle_manager.herd_milk_fat_percent,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        om.add_variable(
            "herd_milk_fat_kg",
            life_cycle_manager.herd_milk_fat_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "dry_cows_milk_fat_kg",
            life_cycle_manager.dry_cows_milk_fat_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_protein_kg",
            life_cycle_manager.herd_milk_protein_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_protein_percent",
            life_cycle_manager.herd_milk_protein_percent,
            dict(info_map, **{"units": MeasurementUnits.PERCENT}),
        )
        om.add_variable(
            "dry_cows_milk_protein_kg",
            life_cycle_manager.dry_cows_milk_protein_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "open_cow_num", life_cycle_manager.open_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "vwp_cow_num", life_cycle_manager.vwp_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "preg_cow_num", life_cycle_manager.preg_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "milking_cow_num",
            life_cycle_manager.milking_cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "dry_cow_num", life_cycle_manager.dry_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "avg_days_in_milk",
            life_cycle_manager.avg_days_in_milk,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_days_in_preg",
            life_cycle_manager.avg_days_in_preg,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_cow_body_weight",
            life_cycle_manager.avg_cow_body_weight,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        om.add_variable(
            "avg_parity_num",
            life_cycle_manager.avg_parity_num,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        om.add_variable(
            "avg_calving_interval",
            life_cycle_manager.avg_calving_interval,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_breeding_to_preg_time",
            life_cycle_manager.avg_breeding_to_preg_time,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_heifer_culling_age",
            life_cycle_manager.avg_heifer_culling_age,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_cow_culling_age",
            life_cycle_manager.avg_cow_culling_age,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_mature_body_weight",
            life_cycle_manager.avg_mature_body_weight,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        om.add_variable("sim_day", sim_day, dict(info_map, **{"units": MeasurementUnits.DAYS}))
        parity_1 = life_cycle_manager.num_cow_for_parity["1"]
        parity_2 = life_cycle_manager.num_cow_for_parity["2"]
        parity_3 = life_cycle_manager.num_cow_for_parity["3"]
        parity_greater_than_3 = life_cycle_manager.num_cow_for_parity["greater_than_3"]
        om.add_variable("num_cow_for_parity_1", parity_1, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_2", parity_2, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_3", parity_3, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_cow_for_parity_greater_than_3",
            parity_greater_than_3,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        calving_to_preg_time_1 = life_cycle_manager.avg_calving_to_preg_time["1"]
        calving_to_preg_time_2 = life_cycle_manager.avg_calving_to_preg_time["2"]
        calving_to_preg_time_3 = life_cycle_manager.avg_calving_to_preg_time["3"]
        calving_to_preg_time_greater_than_3 = life_cycle_manager.avg_calving_to_preg_time["greater_than_3"]
        om.add_variable(
            "calving_to_preg_time_1", calving_to_preg_time_1, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "calving_to_preg_time_2", calving_to_preg_time_2, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "calving_to_preg_time_3", calving_to_preg_time_3, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "calving_to_preg_time_greater_than_3",
            calving_to_preg_time_greater_than_3,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        avg_age_for_calving_1 = life_cycle_manager.avg_age_for_calving["1"]
        avg_age_for_calving_2 = life_cycle_manager.avg_age_for_calving["2"]
        avg_age_for_calving_3 = life_cycle_manager.avg_age_for_calving["3"]
        avg_age_for_calving_greater_than_3 = life_cycle_manager.avg_age_for_calving["greater_than_3"]
        om.add_variable(
            "avg_age_for_calving_1", avg_age_for_calving_1, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "avg_age_for_calving_2", avg_age_for_calving_2, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "avg_age_for_calving_3", avg_age_for_calving_3, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "avg_age_for_calving_greater_than_3",
            avg_age_for_calving_greater_than_3,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        cull_reason_stats_units = {
            animal_constants.DEATH_CULL: MeasurementUnits.UNITLESS,
            animal_constants.LOW_PROD_CULL: MeasurementUnits.UNITLESS,
            animal_constants.LAMENESS_CULL: MeasurementUnits.UNITLESS,
            animal_constants.INJURY_CULL: MeasurementUnits.UNITLESS,
            animal_constants.MASTITIS_CULL: MeasurementUnits.UNITLESS,
            animal_constants.DISEASE_CULL: MeasurementUnits.UNITLESS,
            animal_constants.UDDER_CULL: MeasurementUnits.UNITLESS,
            animal_constants.UNKNOWN_CULL: MeasurementUnits.UNITLESS,
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
            "units": MeasurementUnits.ANIMALS,
            "simulation_day": simulation_day,
        }
        for pen in pen_list:
            variable_to_add = f"{classname}.{funcname}.number_of_animals_in_pen_{pen.id}_{pen.animal_combination.name}"
            reference_variable = f"{classname}.{funcname}.number_of_animals_in_pen_0_CALF"
            AnimalModuleReporter.data_padder(
                reference_variable, variable_to_add, 0, simulation_day, info_map, MeasurementUnits.ANIMALS
            )
            om.add_variable(
                f"number_of_animals_in_pen_{pen.id}_{pen.animal_combination.name}",
                len(pen.animals_in_pen),
                info_map,
            )

    @classmethod
    def report_sold_animal_information(cls, life_cycle_manager: LifeCycleManager) -> None:
        """
        Adds a dictionary of sold animal information to the output manager.

        Parameters
        ----------
        life_cycle_manager : LifeCycleManager
            Instance of Class LifeCycleManager.

        """
        sold_animals = (
            life_cycle_manager.sold_calves_info
            + life_cycle_manager.sold_heiferIIs_info
            + life_cycle_manager.sold_heiferIIIs_info
            + list(
                filter(
                    lambda cow: cow["cull_reason"] != animal_constants.DEATH_CULL,
                    life_cycle_manager.sold_and_died_cows_info,
                )
            )
        )

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_sold_animal_information.__name__,
        }
        for animal in sold_animals:
            om.add_variable("animal_id", animal["id"], dict(info_map, **{"units": MeasurementUnits.UNITLESS}))
            om.add_variable(
                "animal_type", animal["animal_type"], dict(info_map, **{"units": MeasurementUnits.UNITLESS})
            )
            om.add_variable(
                "body_weight", animal["body_weight"], dict(info_map, **{"units": MeasurementUnits.KILOGRAMS})
            )
            om.add_variable(
                "sold_day", animal["sold_at_day"], dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY})
            )

            om.add_variable(
                "cull_reason", animal["cull_reason"], dict(info_map, **{"units": MeasurementUnits.UNITLESS})
            )
            om.add_variable("days_in_milk", animal["days_in_milk"], dict(info_map, **{"units": MeasurementUnits.DAYS}))
            om.add_variable("parity", animal["parity"], dict(info_map, **{"units": MeasurementUnits.UNITLESS}))

    @classmethod
    def report_sold_animal_information_sort_by_sell_day(
        cls, sold_animals: Sequence[Calf | HeiferI | HeiferII | HeiferIII | Cow], report_name: str, total_days: int
    ) -> None:
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
            if animal["sold_at_day"] < sold_at_day_min:
                sold_at_day_min = animal["sold_at_day"]
            if animal["sold_at_day"] > sold_at_day_max:
                sold_at_day_max = animal["sold_at_day"]
            if daily_sell.get(animal["sold_at_day"]):
                daily_sell[animal["sold_at_day"]].append(animal)
            else:
                daily_sell[animal["sold_at_day"]] = [animal]

        om.add_variable(
            f"{report_name}_first_sell_event",
            sold_at_day_min,
            dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}),
        )
        om.add_variable(
            f"{report_name}_last_sell_event",
            sold_at_day_max,
            dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}),
        )
        for day in range(1, total_days + 1):
            if daily_sell.get(day):
                sold_count = len(daily_sell[day])
                sold_weight = sum(sold_animal["body_weight"] for sold_animal in daily_sell[day])
                om.add_variable(
                    f"{report_name}_sold_count", sold_count, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
                )
                om.add_variable(
                    f"{report_name}_sold_weight",
                    sold_weight,
                    dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
                )
            else:
                om.add_variable(f"{report_name}_sold_count", 0, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
                om.add_variable(
                    f"{report_name}_sold_weight", 0, dict(info_map, **{"units": MeasurementUnits.KILOGRAMS})
                )

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
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
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
    def report_end_of_simulation(
        cls, life_cycle_manager: LifeCycleManager, time: Time, heiferIIs: List[HeiferII], cows: List[Cow]
    ) -> None:
        """
        Calls all reporter methods that should happen at the end of the simulation.

        Parameters
        ----------
        life_cycle_manager : LifeCycleManager
            Instance of LifeCycleManager class.
        time : Time
            The Time object with the current time information.
        heiferIIs : List[HeiferII]
            The list of HeiferIIs.
        cows : List[Cow]
            The list of Cows
        """
        AnimalModuleReporter.report_sold_animal_information(life_cycle_manager)
        if life_cycle_manager.sold_calves_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                life_cycle_manager.sold_calves_info,
                "sold_calves",
                time.simulation_day,
            )
        if life_cycle_manager.sold_heiferIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                life_cycle_manager.sold_heiferIIs_info, "heiferII", time.simulation_day
            )
        if life_cycle_manager.sold_heiferIIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                life_cycle_manager.sold_heiferIIIs_info, "heiferIII", time.simulation_day
            )
        if life_cycle_manager.sold_and_died_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                life_cycle_manager.sold_and_died_cows_info,
                "sold_and_died_cows",
                time.simulation_day,
            )
        if life_cycle_manager.sold_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                life_cycle_manager.sold_cows_info,
                "sold_cows",
                time.simulation_day,
            )
        AnimalModuleReporter._record_animal_events(cows, time.simulation_day)
        AnimalModuleReporter._record_animal_events(heiferIIs, time.simulation_day)
        AnimalModuleReporter._record_heiferIIs_conception_rate()
        AnimalModuleReporter._record_cows_conception_rate()

    @classmethod
    def _record_animal_events(
        cls, animals: list[Calf | HeiferI | HeiferII | HeiferIII | Cow], simulation_day: int
    ) -> None:
        """
        Record the events of the animals.

        Parameters
        ----------
        animals : list[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            A list of animals.
        simulation_day : int
            The current simulation day.

        Returns
        -------
        None
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._record_animal_events.__name__,
        }
        for animal in animals:
            om.add_variable(
                f"{animal.__class__.__name__}_{animal.id}_day_{simulation_day}",
                animal.events,
                dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
            )

    @classmethod
    def _record_heiferIIs_conception_rate(cls) -> None:
        """
        Record the conception rate of heiferIIs.
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._record_heiferIIs_conception_rate.__name__,
        }
        om.add_variable(
            "heiferII_total_num_ai_performed",
            HeiferII.stats["num_ai_performed"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_total_num_successful_conceptions",
            HeiferII.stats["num_successful_conceptions"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        heiferII_overall_conception_rate = (
            (HeiferII.stats["num_successful_conceptions"] / HeiferII.stats["num_ai_performed"])
            if HeiferII.stats["num_ai_performed"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_overall_conception_rate",
            heiferII_overall_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_ED",
            HeiferII.stats["num_ai_performed_in_ED"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_ED",
            HeiferII.stats["num_successful_conceptions_in_ED"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        ed_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_ED"] / HeiferII.stats["num_ai_performed_in_ED"])
            if HeiferII.stats["num_ai_performed_in_ED"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_ED_conception_rate",
            ed_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_TAI",
            HeiferII.stats["num_ai_performed_in_TAI"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_TAI",
            HeiferII.stats["num_successful_conceptions_in_TAI"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        tai_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_TAI"] / HeiferII.stats["num_ai_performed_in_TAI"])
            if HeiferII.stats["num_ai_performed_in_TAI"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_TAI_conception_rate",
            tai_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_SynchED",
            HeiferII.stats["num_ai_performed_in_SynchED"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_SynchED",
            HeiferII.stats["num_successful_conceptions_in_SynchED"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        synch_ed_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_SynchED"] / HeiferII.stats["num_ai_performed_in_SynchED"])
            if HeiferII.stats["num_ai_performed_in_SynchED"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_SynchED_conception_rate",
            synch_ed_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    @classmethod
    def _record_cows_conception_rate(cls) -> None:
        """
        Record the conception rate of cows.
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._record_cows_conception_rate.__name__,
        }
        om.add_variable(
            "cow_total_num_ai_performed",
            Cow.stats["num_ai_performed"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "cow_total_num_successful_conceptions",
            Cow.stats["num_successful_conceptions"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        cow_overall_conception_rate = (
            (Cow.stats["num_successful_conceptions"] / Cow.stats["num_ai_performed"])
            if Cow.stats["num_ai_performed"] > 0
            else 0
        )
        om.add_variable(
            "cow_overall_conception_rate",
            cow_overall_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    @classmethod
    def report_total_disease_days(cls) -> None:
        """Adds total animal-days of disease to Output Manager."""
        pass

    @classmethod
    def report_disease_incidence(cls) -> None:
        """Adds disease-incidence data to Output Manager."""
        pass

    @classmethod
    def report_lost_milk_production(cls) -> None:
        """Reports lost milk production due to disease to Output Manager."""
        pass

    @classmethod
    def report_feed_efficiency_decreases(cls) -> None:
        """Reports feed efficiency decreases due to disease to Output Manager."""
        pass

    @classmethod
    def report_milk_co2_increases(cls) -> None:
        """Reports increases in milk kgCO2/kgMilk due to disease to Output Manager."""
        pass

    @classmethod
    def report_income_losses(cls) -> None:
        """Reports losses in income due to disease to Output Manager."""
        pass
