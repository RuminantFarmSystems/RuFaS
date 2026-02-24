import sys
from dataclasses import asdict
from typing import Any

from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulationStatistics
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict, StillbornCalfTypedDict
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionStatistics
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionSupply,
    NutritionRequirements,
    NutritionEvaluationResults,
)
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.animal import animal_constants
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
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
        info_map: dict[str, Any],
        units: dict[str, MeasurementUnits] | MeasurementUnits,
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
            (e.g., the one following the call of data_padder).

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
            + herd_statistics.heiferIII_num
            + herd_statistics.cow_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        for animal_type, deaths in herd_statistics.animals_deaths_by_stage.items():
            om.add_variable(f"{animal_type}_deaths", deaths, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
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
            updated_milk_data: dict[str, int | float] = asdict(milk_stats)
            updated_milk_data["is_milking"] = milk_stats.is_milking
            updated_milk_data["estimated_daily_milk_produced"] = milk_stats.estimated_daily_milk_produced
            updated_milk_data["milk_protein"] = milk_stats.milk_protein
            updated_milk_data["milk_fat"] = milk_stats.milk_fat
            updated_milk_data["milk_lactose"] = milk_stats.milk_lactose
            updated_milk_data["parity"] = milk_stats.parity
            updated_milk_data["cow_id"] = milk_stats.cow_id
            updated_milk_data["pen_id"] = milk_stats.pen_id
            updated_milk_data["simulation_day"] = simulation_day
            om.add_variable("milk_data_at_milk_update", updated_milk_data, info_map)

    @classmethod
    def report_ration_per_animal(
        cls,
        pen_base_name: str,
        ration_per_animal: dict[RUFAS_ID, float],
        total_dry_matter: float,
        num_animals: int,
        simulation_day: int,
    ) -> None:
        """
        Reports the ration consumption per animal along with additional simulation details.

        Parameters
        ----------
        pen_base_name : str
            The base name of the pen for which the ration report is created.
        ration_per_animal : dict[RUFAS_ID, float]
            A dictionary mapping animal identifiers (RUFAS_ID) to the amount of ration consumption
            per animal in kilograms.
        total_dry_matter : float
            The total dry matter intake for all animals in the pen.
        num_animals : int
            The number of animals present in the pen during the simulation.
        simulation_day : int
            The current simulation day when the ration report is generated.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_ration_per_animal.__name__,
            "simulation_day": simulation_day,
            "number_animals_in_pen": num_animals,
        }

        ration_amounts_with_str_keys = {str(key): amount for key, amount in ration_per_animal.items()}
        ration_amounts_with_str_keys["dry_matter_intake_total"] = total_dry_matter

        units = {key: MeasurementUnits.KILOGRAMS for key in ration_amounts_with_str_keys.keys()}
        om.add_variable(
            f"ration_per_animal_for_{pen_base_name}", ration_amounts_with_str_keys, {**info_map, "units": units}
        )

    @classmethod
    def report_nutrient_amounts(
        cls, pen_base_name: str, average_nutrition_supply: NutritionSupply, num_animals: int, simulation_day: int
    ) -> None:
        """Reports the amounts of nutrients in the ration."""
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_nutrient_amounts.__name__,
            "simulation_day": simulation_day,
            "units": NutritionSupply.UNITS,
            "number_animals_in_pen": num_animals,
        }

        nutrient_amounts = {
            "dm": average_nutrition_supply.dry_matter,
            "CP": average_nutrition_supply.crude_protein,
            "ADF": average_nutrition_supply.adf_supply,
            "NDF": average_nutrition_supply.ndf_supply,
            "lignin": average_nutrition_supply.lignin_supply,
            "ash": average_nutrition_supply.ash_supply,
            "phosphorus": average_nutrition_supply.phosphorus * GeneralConstants.GRAMS_TO_KG,
            "potassium": average_nutrition_supply.potassium_supply,
            "N": average_nutrition_supply.nitrogen_supply,
            "as_fed": average_nutrition_supply.wet_matter,
            "EE": average_nutrition_supply.fat_supply,
            "starch": average_nutrition_supply.starch_supply,
            "TDN": average_nutrition_supply.tdn_supply,
            "DE": average_nutrition_supply.digestible_energy_supply,
            "calcium": average_nutrition_supply.calcium * GeneralConstants.GRAMS_TO_KG,
            "fat": average_nutrition_supply.fat_supply * GeneralConstants.KG_TO_GRAMS,
            "fat_percentage": average_nutrition_supply.fat_percentage,
            "forage_ndf": average_nutrition_supply.forage_ndf_supply,
            "forage_ndf_percent": average_nutrition_supply.forage_ndf_percentage,
            "ME": average_nutrition_supply.metabolizable_energy,
            "NE_maintenance_and_activity": average_nutrition_supply.maintenance_energy,
            "NE_lactation": average_nutrition_supply.lactation_energy,
            "NE_growth": average_nutrition_supply.growth_energy,
            "metabolizable_protein": average_nutrition_supply.metabolizable_protein,
        }
        om.add_variable(f"ration_nutrient_amount_for_{pen_base_name}", nutrient_amounts, info_map)

    @classmethod
    def report_average_nutrient_requirements(
        cls,
        pen_base_name: str,
        average_nutrition_requirements: NutritionRequirements,
        average_body_weight: float,
        average_milk_production_reduction: float,
        num_animals: int,
        simulation_day: int,
    ) -> None:
        """
        Reports the average nutrient requirements for a pen of animals over a simulation period.

        Parameters
        ----------
        pen_base_name : str
            The identifier for the pen in which the group of animals resides.
        average_nutrition_requirements : NutritionRequirements
            The average nutrient requirements for the pen, encapsulated in a NutritionRequirements object.
        average_body_weight : float
            The average body weight of the animals in the pen.
        average_milk_production_reduction : float
            The average milk production reduction for these animals.
        num_animals : int
            The number of animals present in the pen.
        simulation_day : int
            The current day in the simulation for which data is being reported.

        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_average_nutrient_requirements.__name__,
            "number_animals_in_pen": num_animals,
            "simulation_day": simulation_day,
            "units": NutritionRequirements.UNITS,
        }

        avg_requirements = {
            "NEmaint_requirement": average_nutrition_requirements.maintenance_energy,
            "NEa_requirement": average_nutrition_requirements.activity_energy,
            "NEg_requirement": average_nutrition_requirements.growth_energy,
            "NEpreg_requirement": average_nutrition_requirements.pregnancy_energy,
            "NEl_requirement": average_nutrition_requirements.lactation_energy,
            "MP_requirement": average_nutrition_requirements.metabolizable_protein,
            "Ca_requirement": average_nutrition_requirements.calcium,
            "P_req": average_nutrition_requirements.phosphorus,
            "P_req_process": average_nutrition_requirements.process_based_phosphorus,
            "DMIest_requirement": average_nutrition_requirements.dry_matter,
            "avg_BW": average_body_weight,
            "avg_milk_production_reduction_pen": average_milk_production_reduction,
            "avg_essential_amino_acid_requirement": average_nutrition_requirements.essential_amino_acids,
        }

        om.add_variable(f"avg_rqmts_for_{pen_base_name}", avg_requirements, info_map)

    @classmethod
    def report_average_nutrient_evaluation_results(
        cls, pen_base_name: str, average_nutrition_evaluation: NutritionEvaluationResults, simulation_day: int
    ) -> None:
        """
        Reports the average nutritional evaluation results for a specific pen and simulation day.

        Parameters
        ----------
        pen_base_name : str
            The base name of the pen for which the nutrient evaluation data is reported.
        average_nutrition_evaluation : NutritionEvaluationResults
            Contains the average values of nutrient evaluation differences for various metrics
            such as energy, protein, and minerals.
        simulation_day : int
            Represents the simulation day for which the nutrient evaluation report is generated.
        """
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_average_nutrient_evaluation_results.__name__,
            "simulation_day": simulation_day,
        }

        nutrient_evaluation_results = {
            "total_energy_difference": average_nutrition_evaluation.total_energy,
            "maintenance_energy_difference": average_nutrition_evaluation.maintenance_energy,
            "lactation_energy_difference": average_nutrition_evaluation.lactation_energy,
            "growth_energy_difference": average_nutrition_evaluation.growth_energy,
            "metabolizable_protein_difference": average_nutrition_evaluation.metabolizable_protein,
            "calcium_difference": average_nutrition_evaluation.calcium,
            "phosphorus_difference": average_nutrition_evaluation.phosphorus,
            "dry_matter_difference": average_nutrition_evaluation.dry_matter,
            "ndf_percent_difference": average_nutrition_evaluation.ndf_percent,
            "forage_ndf_percent_difference": average_nutrition_evaluation.forage_ndf_percent,
            "fat_percent_difference": average_nutrition_evaluation.fat_percent,
        }
        om.add_variable(
            f"avg_eval_results_for_{pen_base_name}",
            nutrient_evaluation_results,
            {**info_map, "units": NutritionEvaluationResults.UNITS},
        )

        om.add_variable(
            f"avg_eval_report_for_{pen_base_name}",
            average_nutrition_evaluation.report,
            {**info_map, "units": NutritionEvaluationResults.REPORT_UNITS},
        )

    @classmethod
    def report_me_diet(
        cls, pen_base_name: str, metabolizable_energy: float, num_animals: int, simulation_day: int
    ) -> None:
        """
        Reports the metabolizable energy of the diet for a specified pen.

        Parameters
        ----------
        pen_base_name : str
            The base name of the pen for which the metabolizable energy is reported.
        metabolizable_energy : float
            The value of the metabolizable energy in the given units.
        num_animals : int
            The number of animals present in the pen.
        simulation_day : int
            The specific day in the simulation when this data is captured.

        """
        units = MeasurementUnits.MEGACALORIES
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_me_diet.__name__,
            "number_animals_in_pen": num_animals,
            "simulation_day": simulation_day,
            "units": units,
        }

        om.add_variable(
            f"MEdiet_for_{pen_base_name}",
            metabolizable_energy,
            info_map,
        )

    @classmethod
    def report_daily_herd_total_ration(cls, herd_total_ration: dict[str, float], simulation_day: int) -> None:
        """
        Adds the daily total ration of the herd to the OutputManager.

        Parameters
        ----------
        herd_total_ration : dict[str, float]
            The total ration of the herd.
        simulation_day : int
            The day of simulation.
        """
        units = {key: MeasurementUnits.KILOGRAMS for key in herd_total_ration.keys()}
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_herd_total_ration.__name__,
            "simulation_day": simulation_day,
            "units": units,
        }
        om.add_variable("ration_daily_feed_total_across_pens", herd_total_ration, info_map)

    @classmethod
    def report_daily_ration_per_pen(
        cls, pen_id: str, pen_animal_name: str, pen_ration: dict[str, float], simulation_day: int
    ) -> None:
        """
        Calculates and reports the total amounts of feed fed to animals in a pen in a given day.

        Parameters
        ----------
        pen_id : str
            ID of the pen.
        pen_animal_name : str
            Name of the animal combination in the pen.
        pen_ration : dict[str, float]
            Dictionary of feed types and total amounts fed to animals in the pen.
        simulation_day : int
            Day of simulation.
        """
        units = {key: MeasurementUnits.KILOGRAMS for key in pen_ration.keys()}
        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_daily_ration_per_pen.__name__,
            "simulation_day": simulation_day,
            "units": units,
        }

        om.add_variable(f"ration_daily_feed_totals_for_pen_{pen_id}_{pen_animal_name}", pen_ration, info_map)

    @classmethod
    def report_enteric_methane_emission(cls, enteric_methane_emission_by_pen: dict[str, float]) -> None:
        """Reports the amount of daily emission by pen."""
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
        MANURE_STREAM_UNITS = {
            "total_bedding_mass": MeasurementUnits.KILOGRAMS,
            "total_bedding_volume": MeasurementUnits.CUBIC_METERS,
            **ManureStream.MANURE_STREAM_UNITS,
        }

        for stream_name, manure_stream in manure_streams.items():
            if isinstance(manure_stream, ManureStream):
                manure_stream_dict = asdict(manure_stream)
                manure_stream_dict["total_volatile_solids"] = manure_stream.total_volatile_solids
                manure_stream_dict["mass"] = manure_stream.mass
                if manure_stream.pen_manure_data is None:
                    raise ValueError(f"No PenManureData for {stream_name}: pen_manure_data must be present.")
                manure_stream_dict["total_bedding_mass"] = manure_stream.pen_manure_data.total_bedding_mass
                manure_stream_dict["total_bedding_volume"] = manure_stream.pen_manure_data.total_bedding_volume
            else:
                om.add_error(
                    "Manure Stream Type Error",
                    "This function requires either a ManureStream instance or a dictionary.",
                    info_map,
                )
                raise ValueError("Manure stream must be a dictionary or a ManureStream instance to properly report it.")

            if manure_stream_dict.keys() != MANURE_STREAM_UNITS.keys():
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
                    om.add_variable(f"{key}_{stream_name}", value, {**info_map, "units": MANURE_STREAM_UNITS[key]})

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
            "class": (class_name := AnimalModuleReporter.__name__),
            "function": (function_name := AnimalModuleReporter.report_manure_excretions.__name__),
            "data_origin": [("HerdManager", "daily_routines")],
            "simulation_day": simulation_day,
        }
        for base_name, manure_excretion in manure_excretions.items():
            for manure_property, manure_value in asdict(manure_excretion).items():
                reference_variable = f"{class_name}.{function_name}.CALF_PEN_0_{str(manure_property)}"
                variable_to_add = f"{class_name}.{function_name}.{base_name}_{str(manure_property)}"
                AnimalModuleReporter.data_padder(
                    reference_variable,
                    variable_to_add,
                    0,
                    simulation_day,
                    info_map,
                    pen_manure_data_units[manure_property],
                )
                om.add_variable(
                    f"{base_name}_{str(manure_property)}",
                    manure_value,
                    dict(info_map, **{"units": pen_manure_data_units[manure_property]}),
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
            "born_calf_num",
            herd_statistics.born_calf_num,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "stillborn_calf_num",
            herd_statistics.stillborn_calf_num,
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
        parity_greater_than_5 = herd_statistics.num_cow_for_parity["greater_than_5"]
        om.add_variable("num_cow_for_parity_1", parity_1, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_2", parity_2, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_3", parity_3, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_4", parity_4, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_cow_for_parity_5", parity_5, dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_cow_for_parity_greater_than_5",
            parity_greater_than_5,
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        calving_to_preg_time_1 = herd_statistics.avg_calving_to_preg_time["1"]
        calving_to_preg_time_2 = herd_statistics.avg_calving_to_preg_time["2"]
        calving_to_preg_time_3 = herd_statistics.avg_calving_to_preg_time["3"]
        calving_to_preg_time_4 = herd_statistics.avg_calving_to_preg_time["4"]
        calving_to_preg_time_5 = herd_statistics.avg_calving_to_preg_time["5"]
        calving_to_preg_time_greater_than_5 = herd_statistics.avg_calving_to_preg_time["greater_than_5"]
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
            "calving_to_preg_time_4", calving_to_preg_time_4, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "calving_to_preg_time_5", calving_to_preg_time_5, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "calving_to_preg_time_greater_than_5",
            calving_to_preg_time_greater_than_5,
            dict(info_map, **{"units": MeasurementUnits.DAYS}),
        )
        avg_age_for_calving_1 = herd_statistics.avg_age_for_calving["1"]
        avg_age_for_calving_2 = herd_statistics.avg_age_for_calving["2"]
        avg_age_for_calving_3 = herd_statistics.avg_age_for_calving["3"]
        avg_age_for_calving_4 = herd_statistics.avg_age_for_calving["4"]
        avg_age_for_calving_5 = herd_statistics.avg_age_for_calving["5"]
        avg_age_for_calving_greater_than_5 = herd_statistics.avg_age_for_calving["greater_than_5"]
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
            "avg_age_for_calving_4", avg_age_for_calving_4, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "avg_age_for_calving_5", avg_age_for_calving_5, dict(info_map, **{"units": MeasurementUnits.DAYS})
        )
        om.add_variable(
            "avg_age_for_calving_greater_than_5",
            avg_age_for_calving_greater_than_5,
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
    def report_daily_pen_total(
        cls, pen_id: str, pen_animal_name: str, number_of_animals_in_pen: int, simulation_day: int
    ) -> None:
        """
        Reports the pen total animal numbers.

        Parameters
        ----------
        pen_id : str
            The pen ID.
        pen_animal_name : str
            The pen animal name.
        number_of_animals_in_pen : int
            The number of animals in the pen.
        simulation_day : int
            The current simulation day.
        """
        info_map = {
            "class": (class_name := AnimalModuleReporter.__name__),
            "function": (function_name := AnimalModuleReporter.report_daily_pen_total.__name__),
            "units": MeasurementUnits.ANIMALS,
            "simulation_day": simulation_day,
        }
        variable_to_add = f"{class_name}.{function_name}.number_of_animals_in_pen_{pen_id}_{pen_animal_name}"
        reference_variable = f"{class_name}.{function_name}.number_of_animals_in_pen_0_CALF"
        AnimalModuleReporter.data_padder(
            reference_variable, variable_to_add, 0, simulation_day, info_map, MeasurementUnits.ANIMALS
        )
        om.add_variable(
            f"number_of_animals_in_pen_{pen_id}_{pen_animal_name}",
            number_of_animals_in_pen,
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
    def report_stillborn_calves_information(
        cls, stillborn_calves: list[StillbornCalfTypedDict] | list[dict[str, int]], report_name: str, total_days: int
    ) -> None:
        """
        Adds a dictionary of sold animal information to the output manager on daily basis.

        Parameters
        ----------
        stillborn_calves : list[StillbornCalfTypedDict]
            List of stillborn calves.
        report_name : str
            The string to be appended to the variable being reported to the OM.
        total_days : int
            The total number of days in the simulation
        """

        info_map = {
            "class": AnimalModuleReporter.__name__,
            "function": AnimalModuleReporter.report_stillborn_calves_information.__name__,
        }

        stillborn_at_day_min: int = sys.maxsize
        stillborn_at_day_max: int = 0
        daily_stillborn: dict[int, list[StillbornCalfTypedDict]] = {}

        for animal in stillborn_calves:
            if animal["stillborn_day"] < stillborn_at_day_min:
                stillborn_at_day_min = animal["stillborn_day"]
            if animal["stillborn_day"] > stillborn_at_day_max:
                stillborn_at_day_max = animal["stillborn_day"]
            if daily_stillborn.get(animal["stillborn_day"]):
                daily_stillborn[animal["stillborn_day"]].append(animal)
            else:
                daily_stillborn[animal["stillborn_day"]] = [animal]

        om.add_variable(
            f"{report_name}_first_stillborn_event",
            stillborn_at_day_min,
            dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}),
        )
        om.add_variable(
            f"{report_name}_last_stillborn_event",
            stillborn_at_day_max,
            dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}),
        )
        for day in range(total_days + 1):
            if daily_stillborn.get(day):
                stillborn_count = len(daily_stillborn[day])
                birth_weight = sum(stillborn_calf["birth_weight"] for stillborn_calf in daily_stillborn[day])
                om.add_variable(
                    f"{report_name}_stillborn_count",
                    stillborn_count,
                    dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
                )
                om.add_variable(
                    f"{report_name}_stillborn_birth_weight",
                    birth_weight,
                    dict(info_map, **{"units": MeasurementUnits.KILOGRAMS}),
                )
            else:
                om.add_variable(
                    f"{report_name}_stillborn_count", 0, dict(info_map, **{"units": MeasurementUnits.ANIMALS})
                )
                om.add_variable(
                    f"{report_name}_stillborn_birth_weight", 0, dict(info_map, **{"units": MeasurementUnits.KILOGRAMS})
                )

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
        daily_sell: dict[int, list[SoldAnimalTypedDict]] = {}

        for animal in sold_animals:
            if sold_at_day := animal.get("sold_at_day"):
                if sold_at_day < sold_at_day_min:
                    sold_at_day_min = sold_at_day
                if sold_at_day > sold_at_day_max:
                    sold_at_day_max = sold_at_day
                if daily_sell.get(sold_at_day):
                    daily_sell[sold_at_day].append(animal)
                else:
                    daily_sell[sold_at_day] = [animal]

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
        for day in range(total_days + 1):
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
        Adds herd mean of latest_milk_production_305days to the output manager,
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
        empty_sold_animals: list[SoldAnimalTypedDict] = [{"sold_at_day": 0, "body_weight": 0}]
        AnimalModuleReporter.report_sold_animal_information(herd_statistics)
        if herd_statistics.sold_calves_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_calves_info,
                "sold_calves",
                time.simulation_day,
            )
        else:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                empty_sold_animals,
                "sold_calves",
                time.simulation_day,
            )
        if herd_statistics.sold_heiferIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_heiferIIs_info, "heiferII", time.simulation_day
            )
        else:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                empty_sold_animals,
                "heiferII",
                time.simulation_day,
            )
        if herd_statistics.sold_heiferIIIs_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_heiferIIIs_info, "heiferIII", time.simulation_day
            )
        else:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                empty_sold_animals,
                "heiferIII",
                time.simulation_day,
            )
        if herd_statistics.sold_and_died_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_and_died_cows_info,
                "sold_and_died_cows",
                time.simulation_day,
            )
        else:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                empty_sold_animals,
                "sold_and_died_cows",
                time.simulation_day,
            )
        if herd_statistics.sold_cows_info:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                herd_statistics.sold_cows_info,
                "sold_cows",
                time.simulation_day,
            )
        else:
            AnimalModuleReporter.report_sold_animal_information_sort_by_sell_day(
                empty_sold_animals,
                "sold_cows",
                time.simulation_day,
            )

        if herd_statistics.stillborn_calf_info:
            AnimalModuleReporter.report_stillborn_calves_information(
                herd_statistics.stillborn_calf_info, "stillborn_calves", time.simulation_day
            )
        else:
            AnimalModuleReporter.report_stillborn_calves_information(
                [{"stillborn_day": 0, "birth_weight": 0}], "stillborn_calves", time.simulation_day
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
            "number_of_parity_6_or_more_cows": MeasurementUnits.ANIMALS,
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
