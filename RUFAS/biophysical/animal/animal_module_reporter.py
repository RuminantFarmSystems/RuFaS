import sys
from dataclasses import asdict
from typing import Any, Dict, List

import numpy as np

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulationStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionStatistics
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.enums import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits

om = OutputManager()


class AnimalModuleReporter:

    _om = OutputManager()

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
    def report_daily_animal_population(cls, herd_statistics: HerdStatistics, simulation_day: int) -> None:
        """
        Adds daily totals for animal types to OutputManager.

        Parameters
        ----------
        herd_statistics : HerdStatistics
            The HerdStatistics object containing the statistics for the animals in the herd.
        simulation_day : int
            The current simulation day.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_animal_population.__name__,
            "data_origin": [("AnimalManager", "daily_updates")],
        }
        om.add_variable("sim_day", simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}))
        om.add_variable(
            "num_animals",
            herd_statistics.calf_num
            + herd_statistics.heiferI_num
            + herd_statistics.heiferII_num
            + herd_statistics.heiferII_num
            + herd_statistics.cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable("num_calves", herd_statistics.calf_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_heiferIs", herd_statistics.heiferI_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "num_heiferIIs", herd_statistics.heiferII_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "num_heiferIIIs",
            herd_statistics.heiferIII_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_lactating_cows",
            herd_statistics.milking_cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_dry_cows",
            herd_statistics.dry_cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_total", herd_statistics.cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )

    @classmethod
    def report_milk(cls, milk_reports: list[MilkProductionStatistics], simulation_day: int) -> None:
        """
        Adds milk information for all cows in pen to output manager.

        Parameters
        ----------
        milk_reports : list[MilkProductionStatistics]
            A list of MilkProductionStatistics for each lactating cow in the herd.
        simulation_day : int
            Day of simulation.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_milk.__name__,
            "data_origin": [("MilkProduction", "perform_daily_milking_update")],
            "units": MilkProductionStatistics.UNITS,
        }

        for milk_stats in milk_reports:
            milk_data_update: dict[str, int | float] = asdict(milk_stats)
            milk_data_update["lactating"] = milk_stats.is_milking
            milk_data_update["simulation_day"] = simulation_day
            om.add_variable("milk_data_at_milk_update", milk_data_update, info_map)

    @classmethod
    def report_ration_interval_data(cls, pen: Pen, simulation_day: int) -> None:
        """
        For each pen, adds ration per animal and other supply reports, to output manager.

        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.

        """

        if pen.is_populated is False:
            return

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_interval_data.__name__,
            "number_animals_in_pen": len(pen.animals_in_pen),
            "simulation_day": simulation_day,
            "units": MeasurementUnits.ANIMALS,
        }
        cls._om.add_variable(
            f"number_animals_in_pen_{pen.id}_{pen.animal_combination.name}", len(pen.animals_in_pen), info_map
        )
        cls._report_ration_per_animal(pen, simulation_day)
        cls._report_nutrient_amounts(pen, simulation_day)
        cls._report_me_diet(pen, simulation_day)

        if pen.animal_combination != AnimalCombination.CALF:
            cls._report_average_nutrient_requirements(pen, simulation_day)
            cls._report_average_nutrient_evaluation_results(pen, simulation_day)

    @classmethod
    def _report_ration_per_animal(cls, pen: Pen, simulation_day: int) -> dict[int, float]:
        """
        For each pen, adds the average ration per animal to the OutputManager.

        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.

        Returns
        -------
        dict[int, float]
            Map of RuFaS Feed IDs to amounts of that feed in the ration (kg dry matter).

        """
        total_dry_matter = pen.average_nutrition_supply.dry_matter

        ration_amounts_with_str_keys = {str(key): amount for key, amount in pen.ration.items()}
        ration_amounts_with_str_keys["dry_matter_intake_total"] = total_dry_matter

        units = {key: MeasurementUnits.KILOGRAMS for key in ration_amounts_with_str_keys.keys()}

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_interval_data.__name__,
            "number_animals_in_pen": len(pen.animals_in_pen.keys()),
            "simulation_day": simulation_day,
            "units": units,
        }

        cls._om.add_variable(
            f"ration_per_animal_for_pen_{pen.id}_{pen.animal_combination.name}", ration_amounts_with_str_keys, info_map
        )

        return pen.ration

    @classmethod
    def _report_nutrient_amounts(cls, pen: Pen, simulation_day: int) -> None:
        """Reports the amounts of nutrients in the ration."""
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
            "fat": MeasurementUnits.GRAMS,
            "fat_percentage": MeasurementUnits.PERCENT,
            "forage_ndf": MeasurementUnits.KILOGRAMS,
            "forage_ndf_percent": MeasurementUnits.PERCENT_OF_DRY_MATTER,
            "ME": MeasurementUnits.MEGACALORIES,
            "NE_maintenance_and_activity": MeasurementUnits.MEGACALORIES,
            "NE_lactation": MeasurementUnits.MEGACALORIES,
            "NE_growth": MeasurementUnits.MEGACALORIES,
            "metabolizable_protein": MeasurementUnits.GRAMS,
        }
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_interval_data.__name__,
            "number_animals_in_pen": len(pen.animals_in_pen.keys()),
            "simulation_day": simulation_day,
            "units": nutrient_amount_units,
        }

        fat_grams = pen.average_nutrition_supply.fat_supply * GeneralConstants.KG_TO_GRAMS
        nutrient_amounts = {
            "dm": pen.average_nutrition_supply.dry_matter,
            "CP": pen.average_nutrition_supply.crude_protein,
            "ADF": pen.average_nutrition_supply.adf_supply,
            "NDF": pen.average_nutrition_supply.ndf_supply,
            "lignin": pen.average_nutrition_supply.lignin_supply,
            "ash": pen.average_nutrition_supply.ash_supply,
            "phosphorus": pen.average_nutrition_supply.phosphorus * GeneralConstants.GRAMS_TO_KG,
            "potassium": pen.average_nutrition_supply.potassium_supply,
            "N": pen.average_nutrition_supply.nitrogen_supply,
            "as_fed": pen.average_nutrition_supply.wet_matter,
            "EE": pen.average_nutrition_supply.fat_supply,
            "starch": pen.average_nutrition_supply.starch_supply,
            "TDN": pen.average_nutrition_supply.tdn_supply,
            "DE": pen.average_nutrition_supply.digestible_energy_supply,
            "calcium": pen.average_nutrition_supply.calcium * GeneralConstants.GRAMS_TO_KG,
            "fat": fat_grams,
            "fat_percentage": pen.average_nutrition_supply.fat_percentage,
            "forage_ndf": pen.average_nutrition_supply.forage_ndf_supply,
            "forage_ndf_percent": pen.average_nutrition_supply.forage_ndf_percentage,
            "ME": pen.average_nutrition_supply.metabolizable_energy,
            "NE_maintenance_and_activity": pen.average_nutrition_supply.maintenance_energy,
            "NE_lactation": pen.average_nutrition_supply.lactation_energy,
            "NE_growth": pen.average_nutrition_supply.growth_energy,
            "metabolizable_protein": pen.average_nutrition_supply.metabolizable_protein,
        }

        cls._om.add_variable(
            f"ration_nutrient_amount_pen_{pen.id}_{pen.animal_combination.name}", nutrient_amounts, info_map
        )

    @classmethod
    def _report_average_nutrient_requirements(cls, pen: Pen, simulation_day: int) -> None:
        """
        Adds the average ration per animal of a pen to the OutputManager.

        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.

        """
        units = {
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
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_interval_data.__name__,
            "number_animals_in_pen": len(pen.animals_in_pen),
            "simulation_day": simulation_day,
            "units": units,
        }

        avg_requirements = {
            "NEmaint_requirement": pen.average_nutrition_requirements.maintenance_energy,
            "NEa_requirement": pen.average_nutrition_requirements.activity_energy,
            "NEg_requirement": pen.average_nutrition_requirements.growth_energy,
            "NEpreg_requirement": pen.average_nutrition_requirements.pregnancy_energy,
            "NEl_requirement": pen.average_nutrition_requirements.lactation_energy,
            "MP_requirement": pen.average_nutrition_requirements.metabolizable_protein,
            "Ca_requirement": pen.average_nutrition_requirements.calcium,
            "P_req": pen.average_nutrition_requirements.phosphorus,
            "P_req_process": pen.average_nutrition_requirements.process_based_phosphorus,
            "DMIest_requirement": pen.average_nutrition_requirements.dry_matter,
            "avg_BW": pen.average_body_weight,
            "avg_milk_production_reduction_pen": pen.average_milk_production_reduction,
            "avg_essential_amino_acid_requirement": pen.average_nutrition_requirements.essential_amino_acids,
        }

        cls._om.add_variable(f"avg_rqmts_pen_{pen.id}_{pen.animal_combination.name}", avg_requirements, info_map)

    @classmethod
    def _report_average_nutrient_evaluation_results(cls, pen: Pen, simulation_day: int) -> None:
        """
        Reports the average nutrient evaluation results for a pen.
        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._report_average_nutrient_evaluation_results.__name__,
            "simulation_day": simulation_day,
        }

        nutrient_evaluation_units = {
            "total_energy_difference": MeasurementUnits.MEGACALORIES,
            "maintenance_energy_difference": MeasurementUnits.MEGACALORIES,
            "lactation_energy_difference": MeasurementUnits.MEGACALORIES,
            "growth_energy_difference": MeasurementUnits.MEGACALORIES,
            "metabolizable_protein_difference": MeasurementUnits.GRAMS,
            "calcium_difference": MeasurementUnits.GRAMS,
            "phosphorus_difference": MeasurementUnits.GRAMS,
            "dry_matter_difference": MeasurementUnits.KILOGRAMS,
            "ndf_percent_difference": MeasurementUnits.PERCENT,
            "forage_ndf_percent_difference": MeasurementUnits.PERCENT,
            "fat_percent_difference": MeasurementUnits.PERCENT,
        }
        info_map["units"] = nutrient_evaluation_units

        nutrient_evaluation_results = {
            "total_energy_difference": pen.average_nutrition_evaluation.total_energy,
            "maintenance_energy_difference": pen.average_nutrition_evaluation.maintenance_energy,
            "lactation_energy_difference": pen.average_nutrition_evaluation.lactation_energy,
            "growth_energy_difference": pen.average_nutrition_evaluation.growth_energy,
            "metabolizable_protein_difference": pen.average_nutrition_evaluation.metabolizable_protein,
            "calcium_difference": pen.average_nutrition_evaluation.calcium,
            "phosphorus_difference": pen.average_nutrition_evaluation.phosphorus,
            "dry_matter_difference": pen.average_nutrition_evaluation.dry_matter,
            "ndf_percent_difference": pen.average_nutrition_evaluation.ndf_percent,
            "forage_ndf_percent_difference": pen.average_nutrition_evaluation.forage_ndf_percent,
            "fat_percent_difference": pen.average_nutrition_evaluation.fat_percent,
        }
        cls._om.add_variable(
            f"avg_eval_results_pen_{pen.id}_{pen.animal_combination.name}", nutrient_evaluation_results, info_map
        )

        info_map["units"] = {
            "is_valid_heifer_ration": MeasurementUnits.UNITLESS,
            "is_valid_cow_ration": MeasurementUnits.UNITLESS,
            "total_energy_acceptable": MeasurementUnits.UNITLESS,
            "maintenance_energy_acceptable": MeasurementUnits.UNITLESS,
            "lactation_energy_acceptable": MeasurementUnits.UNITLESS,
            "growth_energy_acceptable": MeasurementUnits.UNITLESS,
            "metabolizable_protein_acceptable": MeasurementUnits.UNITLESS,
            "calcium_acceptable": MeasurementUnits.UNITLESS,
            "phosphorus_acceptable": MeasurementUnits.UNITLESS,
            "dry_matter_acceptable": MeasurementUnits.UNITLESS,
            "ndf_percent_acceptable": MeasurementUnits.UNITLESS,
            "forage_ndf_percent_acceptable": MeasurementUnits.UNITLESS,
            "fat_percent_acceptable": MeasurementUnits.UNITLESS,
        }

        cls._om.add_variable(
            f"avg_eval_report_pen_{pen.id}_{pen.animal_combination.name}",
            pen.average_nutrition_evaluation.report,
            info_map,
        )

    @classmethod
    def _report_me_diet(cls, pen: Pen, simulation_day: int) -> None:
        """
        Report the total metabolizable energy of a pen's average ration to the Output Manager as "MEdiet".

        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.

        """
        units = MeasurementUnits.MEGACALORIES
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_interval_data.__name__,
            "number_animals_in_pen": len(pen.animals_in_pen.values()),
            "simulation_day": simulation_day,
            "units": units,
        }

        cls._om.add_variable(
            f"MEdiet_pen_{pen.id}_{pen.animal_combination.name}",
            pen.average_nutrition_supply.metabolizable_energy,
            info_map,
        )

    @classmethod
    def report_daily_ration(cls, herd_manager, simulation_day: int) -> None:
        """
        Adds ration totals as fed to each pen to output manager.

        Parameters
        ----------
        herd_manager : HerdManager
            Instance of HerdManager class.
        simulation_day : int

        """
        ration_across_pens: dict[str, float] = {}
        for pen in herd_manager.all_pens:
            pen_ration = cls._report_daily_ration_per_pen(pen, simulation_day, herd_manager)
            for key, amount in pen_ration.items():
                if key not in ration_across_pens.keys():
                    ration_across_pens[key] = 0.0
                ration_across_pens[key] += amount

        units = {key: MeasurementUnits.KILOGRAMS for key in ration_across_pens.keys()}
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_ration.__name__,
            "simulation_day": simulation_day,
            "units": units,
        }
        om.add_variable("ration_daily_feed_total_across_pens", ration_across_pens, info_map)
        AnimalModuleReporter.report_daily_feed_emissions(ration_across_pens, "ALL", "", herd_manager, simulation_day)

    @classmethod
    def _report_daily_ration_per_pen(cls, pen: Pen, simulation_day: int, herd_manager) -> dict[str, float]:
        """
        Calculates and reports the total amounts of feed fed to animals in a pen in a given day.

        Parameters
        ----------
        pen : Pen
            Pen object.
        simulation_day : int
            Day of simulation.
        herd_manager : HerdManager
            Herd Manager object.

        Returns
        -------
        dict[str, float]
            Maps the RuFaS Feed ID (as a string) to the total amount of that feed used for the given pen, as well as the
            total amounts of all feeds and byproducts used for the given pen (kg dry matter).

        """
        animal_count = len(pen.animals_in_pen.values())

        ration_per_pen = {str(rufas_id): amount * animal_count for rufas_id, amount in pen.ration.items()}
        ration_per_pen["dry_matter_intake_total"] = sum([total_feed for total_feed in ration_per_pen.values()])
        ration_per_pen["byproducts_total"] = pen.average_nutrition_supply.byproduct_supply * animal_count

        units = {key: MeasurementUnits.KILOGRAMS for key in ration_per_pen.keys()}
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_ration.__name__,
            "simulation_day": simulation_day,
            "units": units,
        }

        AnimalModuleReporter.report_daily_feed_emissions(
            ration_per_pen, pen.id, pen.animal_combination.name, herd_manager, simulation_day
        )

        cls._om.add_variable(
            f"ration_daily_feed_totals_for_pen_{pen.id}_{pen.animal_combination.name}", ration_per_pen, info_map
        )

        return ration_per_pen

    @classmethod
    def report_daily_feed_emissions(
        cls,
        ration_total: dict[str, float],
        pen_id: int | str,
        pen_animal_name: str,
        animal_manager,
        simulation_day: int,
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
                simulation_day,
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
    def report_enteric_methane_emission(cls, enteric_methane_emission_by_pen: dict[str, float]) -> None:
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_enteric_methane_emission.__name__,
            "data_origin": [("HerdManager", "daily_routines")],
        }
        for pen_id_combination, enteric_methane_emission in enteric_methane_emission_by_pen.items():
            om.add_variable(
                f"enteric_methane_emission_for_{pen_id_combination}",
                enteric_methane_emission,
                dict(info_map, **{"units": MeasurementUnits.GRAMS}),
            )

    @classmethod
    def report_manure_streams(cls, manure_streams: dict[str, ManureStream], simulation_day: int) -> None:
        """
        Report Animal Module manure stream data to Output Manager.

        Parameters
        ----------
        manure_streams : dict[str, ManureStream]
            A dictionary of manure stream data, where the key is the formatted stream name
            and the value is the ManureStream object.
        simulation_day : int
            The simulation day.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_manure_streams.__name__,
            "data_origin": [("HerdManager", "daily_routines")],
            "simulation_day": simulation_day,
        }

        for stream_name, manure_stream in manure_streams.items():
            if isinstance(manure_stream, ManureStream):
                manure_stream_dict = asdict(manure_stream)
                manure_stream_dict["total_volatile_solids"] = manure_stream.total_volatile_solids
                manure_stream_dict["mass"] = manure_stream.mass
            else:
                om.add_error(
                    "Manure Stream Type Error",
                    "This function requires either a ManureStream instance or a dictionary.",
                    info_map,
                )
                raise ValueError("Manure stream must be a dictionary or a ManureStream instance to properly report it.")

            if manure_stream_dict.keys() != ManureStream.MANURE_STREAM_UNITS.keys():
                om.add_error(
                    "Manure Stream Keys Error",
                    f"Expected keys: {set(ManureStream.MANURE_STREAM_UNITS.keys())}, "
                    f"received: {set(manure_stream_dict.keys())}.",
                    info_map,
                )
                raise ValueError(
                    "Manure Stream must contain the same keys as manure_stream_units to properly report it."
                )

            for key, value in manure_stream_dict.items():
                if key != "pen_manure_data":
                    om.add_variable(
                        f"{key}_{stream_name}", value, {**info_map, "units": ManureStream.MANURE_STREAM_UNITS[key]}
                    )

    @classmethod
    def report_manure_excretions(
        cls, manure_excretions: dict[str, AnimalManureExcretions], simulation_day: int
    ) -> None:
        """
        Report pen AnimalManureExcretions to Output Manager.

        Parameters
        ----------
        manure_excretions : dict[str, AnimalManureExcretions]
            A dictionary of manure excretion data, where the key is the formatted base name
            and the value is the AnimalManureExcretions object.
        simulation_day : int
            The simulation day.

        """
        pen_manure_data_units = {
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
        }
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_manure_excretions.__name__,
            "data_origin": [("HerdManager", "daily_routines")],
            "simulation_day": simulation_day,
        }
        for base_name, manure_excretion in manure_excretions.items():
            for manure_property, manure_value in asdict(manure_excretion).items():
                om.add_variable(
                    f"{base_name}_{str(manure_property)}",
                    manure_value,
                    dict(info_map, **{"units": pen_manure_data_units[manure_property]}),
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
            "data_origin": [("Pen", "total_manure_excretion")],
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
        for manure_property, manure_value in asdict(pen.total_manure_excretion).items():
            reference_variable = f"{classname}.{funcname}.pen_0_daily_{str(manure_property)}"
            variable_to_add = f"{classname}.{funcname}.pen_{pen.id}_daily_{str(manure_property)}"
            AnimalModuleReporter.data_padder(
                reference_variable, variable_to_add, 0, simulation_day, info_map, manure_value_units[manure_property]
            )
            om.add_variable(
                f"pen_{pen.id}_daily_{str(manure_property)}",
                manure_value,
                dict(info_map, **{"units": manure_value_units[manure_property]}),
            )

    @classmethod
    def report_herd_statistics_data(cls, herd_statistics: HerdStatistics, simulation_day: int) -> None:
        """
        Adds daily herd statistics data to OutputManager.

        Parameters
        ----------
        herd_statistics : HerdStatistics
            The HerdStatistics object containing the daily herd statistics data.
        simulation_day : int
            Day of simulation.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_herd_statistics_data.__name__,
            "data_origin": [("HerdManager", "daily_update")],
        }
        om.add_variable(
            "sold_heiferIII_oversupply_num",
            herd_statistics.sold_heiferIII_oversupply_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "bought_heifer_num",
            herd_statistics.bought_heifer_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "sold_heiferII_num",
            herd_statistics.sold_heiferII_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "cow_herd_exit_num",
            herd_statistics.cow_herd_exit_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "sold_cow_num", herd_statistics.sold_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "GnRH_injection_num_h",
            herd_statistics.GnRH_injection_num_h,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "GnRH_injection_num",
            herd_statistics.GnRH_injection_num,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "PGF_injection_num",
            herd_statistics.PGF_injection_num,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "PGF_injection_num_h",
            herd_statistics.PGF_injection_num_h,
            dict(info_map, **{"units": MeasurementUnits.INJECTIONS}),
        )
        om.add_variable(
            "ai_num",
            herd_statistics.ai_num,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "ai_num_h",
            herd_statistics.ai_num_h,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "preg_check_num",
            herd_statistics.preg_check_num,
            dict(info_map, **{"units": MeasurementUnits.PREGNANCY_CHECKS}),
        )
        om.add_variable(
            "preg_check_num_h",
            herd_statistics.preg_check_num_h,
            dict(info_map, **{"units": MeasurementUnits.PREGNANCY_CHECKS}),
        )
        om.add_variable(
            "num_heiferII_in_ed_period",
            herd_statistics.ed_period_h,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cow_in_ed_period",
            herd_statistics.ed_period,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "sold_calf_num",
            herd_statistics.sold_calf_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "daily_milk_production",
            herd_statistics.daily_milk_production,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_fat_percent",
            herd_statistics.herd_milk_fat_percent,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        om.add_variable(
            "herd_milk_fat_kg",
            herd_statistics.herd_milk_fat_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_protein_kg",
            herd_statistics.herd_milk_protein_kg,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS_PER_DAY}),
        )
        om.add_variable(
            "herd_milk_protein_percent",
            herd_statistics.herd_milk_protein_percent,
            dict(info_map, **{"units": MeasurementUnits.PERCENT}),
        )
        om.add_variable(
            "open_cow_num", herd_statistics.open_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "vwp_cow_num", herd_statistics.vwp_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "preg_cow_num", herd_statistics.preg_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "milking_cow_num",
            herd_statistics.milking_cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "dry_cow_num", herd_statistics.dry_cow_num, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
        )
        om.add_variable(
            "avg_days_in_milk",
            herd_statistics.avg_days_in_milk,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_days_in_preg",
            herd_statistics.avg_days_in_preg,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_cow_body_weight",
            herd_statistics.avg_cow_body_weight,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        om.add_variable(
            "avg_parity_num",
            herd_statistics.avg_parity_num,
            dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
        )
        om.add_variable(
            "avg_calving_interval",
            herd_statistics.avg_calving_interval,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_breeding_to_preg_time",
            herd_statistics.avg_breeding_to_preg_time,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_heifer_culling_age",
            herd_statistics.avg_heifer_culling_age,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_cow_culling_age",
            herd_statistics.avg_cow_culling_age,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        om.add_variable(
            "avg_mature_body_weight",
            herd_statistics.avg_mature_body_weight,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )
        om.add_variable("simulation_day", simulation_day, dict(info_map, **{"units": MeasurementUnits.DAYS}))
        parity_1 = herd_statistics.num_cow_for_parity["1"]
        parity_2 = herd_statistics.num_cow_for_parity["2"]
        parity_3 = herd_statistics.num_cow_for_parity["3"]
        parity_4 = herd_statistics.num_cow_for_parity["4"]
        parity_5 = herd_statistics.num_cow_for_parity["5"]
        parity_greater_than_3 = herd_statistics.num_cow_for_parity["greater_than_3"]
        om.add_variable("num_cow_for_parity_1", parity_1, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_2", parity_2, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_3", parity_3, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_4", parity_4, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_5", parity_5, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_cow_for_parity_greater_than_3",
            parity_greater_than_3,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        calving_to_preg_time_1 = herd_statistics.avg_calving_to_preg_time["1"]
        calving_to_preg_time_2 = herd_statistics.avg_calving_to_preg_time["2"]
        calving_to_preg_time_3 = herd_statistics.avg_calving_to_preg_time["3"]
        calving_to_preg_time_greater_than_3 = herd_statistics.avg_calving_to_preg_time["greater_than_3"]
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
        avg_age_for_calving_1 = herd_statistics.avg_age_for_calving["1"]
        avg_age_for_calving_2 = herd_statistics.avg_age_for_calving["2"]
        avg_age_for_calving_3 = herd_statistics.avg_age_for_calving["3"]
        avg_age_for_calving_greater_than_3 = herd_statistics.avg_age_for_calving["greater_than_3"]
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
            herd_statistics.cull_reason_stats,
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
    def report_sold_animal_information(cls, herd_statistics: HerdStatistics) -> None:
        """
        Adds a dictionary of sold animal information to the output manager.

        Parameters
        ----------
        herd_statistics : HerdStatistics
            The HerdStatistics object containing sold animal information.

        """
        sold_animals = (
            herd_statistics.sold_calves_info
            + herd_statistics.sold_heiferIIs_info
            + herd_statistics.sold_heiferIIIs_info
            + list(
                filter(
                    lambda cow: cow["cull_reason"] != animal_constants.DEATH_CULL,
                    herd_statistics.sold_and_died_cows_info,
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
        cls, sold_animals: list[SoldAnimalTypedDict], report_name: str, total_days: int
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
        daily_sell: Dict[int, List[SoldAnimalTypedDict]] = {}

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
        for day in range(total_days):
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
    def report_305d_milk(cls, average_herd_305_days_milk_production: float) -> None:
        """
        Adds herd mean of latest_milk_production_305days to output manager,
        though only for lactating cows with nonzero values.

        Parameters
        ----------
        average_herd_305_days_milk_production : float
            The herd average total past 305-day milk production.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_305d_milk.__name__,
            "data_origin": [("MilkProduction", "perform_daily_milking_update")],
        }
        om.add_variable(
            "milk_production_305days_herd_mean",
            average_herd_305_days_milk_production,
            dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
        )

    @classmethod
    def report_daily_reports(cls, herd_manager, simulation_day: int) -> None:
        """
        Calls all reporter methods that should happen at the end of each day.

        Parameters
        ----------
        animal_manager : AnimalManager
            Instance of AnimalManager class.
        available_feeds : Dict[str, Dict[str, Any]]
            Available feeds dictionary from the Feed class object.
        """
        AnimalModuleReporter.report_daily_ration(herd_manager, simulation_day)
        AnimalModuleReporter.report_daily_pen_total(simulation_day, herd_manager.all_pens)
        for pen in herd_manager.all_pens:
            AnimalModuleReporter.report_pen_manure_properties(pen, simulation_day)

    @classmethod
    def report_end_of_simulation(
        cls,
        herd_statistics: HerdStatistics,
        herd_reproduction_statistics: HerdReproductionStatistics,
        time: RufasTime,
        heiferII_events_by_id: dict[str, str],
        cow_events_by_id: dict[str, str],
    ) -> None:
        """
        Calls all reporter methods that should happen at the end of the simulation.

        Parameters
        ----------
        herd_statistics : HerdStatistics
            Instance of HerdStatistics class.
        herd_reproduction_statistics : HerdReproductionStatistics
            Instance of HerdReproductionStatistics class.
        time : RufasTime
            The RufasTime object with the current time information.
        heiferII_events_by_id : dict[str, str]
            The dictionary of HeiferII events.
        cow_events_by_id : dict[str, str]
            The dictionary of Cow events.
        """
        AnimalModuleReporter.report_sold_animal_information(herd_statistics)
        if herd_statistics.sold_calves_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_calves_info,
                "sold_calves",
                time.simulation_day,
            )
        if herd_statistics.sold_heiferIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_heiferIIs_info, "heiferII", time.simulation_day
            )
        if herd_statistics.sold_heiferIIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_heiferIIIs_info, "heiferIII", time.simulation_day
            )
        if herd_statistics.sold_and_died_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_and_died_cows_info,
                "sold_and_died_cows",
                time.simulation_day,
            )
        if herd_statistics.sold_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_cows_info,
                "sold_cows",
                time.simulation_day,
            )
        AnimalModuleReporter._record_animal_events(heiferII_events_by_id, time.simulation_day)
        AnimalModuleReporter._record_animal_events(cow_events_by_id, time.simulation_day)
        AnimalModuleReporter._record_heiferIIs_conception_rate(herd_reproduction_statistics)
        AnimalModuleReporter._record_cows_conception_rate(herd_reproduction_statistics)

    @classmethod
    def _record_animal_events(cls, animal_events_by_id: dict[str, str], simulation_day: int) -> None:
        """
        Record the events of the animals.

        Parameters
        ----------
        animal_events_by_id : dict[str, str]
            A dictionary of animal events, where the key is a string containing the animal id and the animal type,
            and the value is the string representation of the events of the animal.
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
        for prefix, animal_events in animal_events_by_id.items():
            om.add_variable(
                f"{prefix}_day_{simulation_day}",
                animal_events,
                dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
            )

    @classmethod
    def _record_heiferIIs_conception_rate(cls, herd_reproduction_statistics: HerdReproductionStatistics) -> None:
        """
        Record the conception rate of heiferIIs.
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._record_heiferIIs_conception_rate.__name__,
        }
        om.add_variable(
            "heiferII_total_num_ai_performed",
            herd_reproduction_statistics.heifer_num_ai_performed,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_total_num_successful_conceptions",
            herd_reproduction_statistics.heifer_num_successful_conceptions,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        om.add_variable(
            "heiferII_overall_conception_rate",
            herd_reproduction_statistics.heifer_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_ED",
            herd_reproduction_statistics.heifer_num_ai_performed_in_ED,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_ED",
            herd_reproduction_statistics.heifer_num_successful_conceptions_in_ED,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        om.add_variable(
            "heiferII_ED_conception_rate",
            herd_reproduction_statistics.heifer_ED_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_TAI",
            herd_reproduction_statistics.heifer_num_ai_performed_in_TAI,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_TAI",
            herd_reproduction_statistics.heifer_num_successful_conceptions_in_TAI,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        om.add_variable(
            "heiferII_TAI_conception_rate",
            herd_reproduction_statistics.heifer_TAI_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_SynchED",
            herd_reproduction_statistics.heifer_num_ai_performed_in_SynchED,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_SynchED",
            herd_reproduction_statistics.heifer_num_successful_conceptions_in_SynchED,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        om.add_variable(
            "heiferII_SynchED_conception_rate",
            herd_reproduction_statistics.heifer_SynchED_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    @classmethod
    def _record_cows_conception_rate(cls, herd_reproduction_statistics: HerdReproductionStatistics) -> None:
        """Record the conception rate of cows."""

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter._record_cows_conception_rate.__name__,
        }
        om.add_variable(
            "cow_total_num_ai_performed",
            herd_reproduction_statistics.cow_num_ai_performed,
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "cow_total_num_successful_conceptions",
            herd_reproduction_statistics.cow_num_successful_conceptions,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        om.add_variable(
            "cow_overall_conception_rate",
            herd_reproduction_statistics.cow_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    @classmethod
    def report_animal_population_statistics(cls, prefix: str, herd_summary: AnimalPopulationStatistics) -> None:
        """Reports the herd summary statistics for the starting animal population."""
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_animal_population_statistics.__name__,
        }
        units = {
            "breed": MeasurementUnits.UNITLESS,
            "number_of_calves": MeasurementUnits.ANIMALS,
            "number_of_heiferIs": MeasurementUnits.ANIMALS,
            "number_of_heiferIIs": MeasurementUnits.ANIMALS,
            "number_of_heiferIIIs": MeasurementUnits.ANIMALS,
            "number_of_cows": MeasurementUnits.ANIMALS,
            "number_of_replacement_heiferIIIS": MeasurementUnits.ANIMALS,
            "number_of_lactating_cows": MeasurementUnits.ANIMALS,
            "number_of_dry_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_1_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_2_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_3_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_4_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_5_cows": MeasurementUnits.ANIMALS,
            "number_of_parity_4_and_more_cows": MeasurementUnits.ANIMALS,
            "average_calf_age": MeasurementUnits.DAYS,
            "average_heiferI_age": MeasurementUnits.DAYS,
            "average_heiferII_age": MeasurementUnits.DAYS,
            "average_heiferIII_age": MeasurementUnits.DAYS,
            "average_cow_age": MeasurementUnits.DAYS,
            "average_replacement_age": MeasurementUnits.DAYS,
            "average_calf_body_weight": MeasurementUnits.KILOGRAMS,
            "average_heiferI_body_weight": MeasurementUnits.KILOGRAMS,
            "average_heiferII_body_weight": MeasurementUnits.KILOGRAMS,
            "average_heiferIII_body_weight": MeasurementUnits.KILOGRAMS,
            "average_cow_body_weight": MeasurementUnits.KILOGRAMS,
            "average_replacement_body_weight": MeasurementUnits.KILOGRAMS,
            "average_cow_days_in_pregnancy": MeasurementUnits.DAYS,
            "average_cow_days_in_milk": MeasurementUnits.DAYS,
            "average_cow_parity": MeasurementUnits.UNITLESS,
            "average_cow_calving_interval": MeasurementUnits.DAYS,
        }
        for variable_name, value in herd_summary.__dict__.items():
            if isinstance(value, dict):
                for sub_variable_name, sub_value in value.items():
                    om.add_variable(
                        f"{prefix}_{sub_variable_name}",
                        sub_value,
                        dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
                    )
            else:
                om.add_variable(f"{prefix}_{variable_name}", value, dict(info_map, **{"units": units[variable_name]}))

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
