import math
from typing import Callable, Dict, List

import numpy as np

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.ration.amino_acid import AminoAcidCalculator, EssentialAminoAcidRequirements
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.user_constants import UserConstants

om = OutputManager()


class AnimalRequirements:
    """
    Stores the information for the calculated requirements of animals to
    be used in the ration formulation.
    """

    def __init__(self) -> None:
        """
        Initializes a requirements object with default values of specific
        requirements at 0.

        Notes
        -----
        NEmaint_requirement = Net energy for maintenance requirement (Mcal)

        NEa_requirement = Net energy for activity requirement (Mcal)

        NEg_requirement = Net energy for growth requirement (Mcal)

        NEpreg_requirement = Net energy requirement for pregnancy (Mcal)

        NEl_requirement = Net energy requirement for lactation (Mcal)

        MP_requirement = Metabolizable protein requirement for growth (g)

        Ca_requirement = Calcium requirement (g)

        P_requirement = Phosphorus requirement (g)

        DMIest_requirement = dry matter intake estimation (kg)

        avg_BW = average body weight in pen (kg)

        avg_milk = average milk production per animal (kg/day)

        avg_CP_milk = average crude protein content of milk (%)

        """

        # Net energy for maintenance requirement (Mcal)
        self.NEmaint_requirement = 0
        # Net energy for activity requirement (Mcal)
        self.NEa_requirement = 0
        # Net energy for growth requirement (Mcal)
        self.NEg_requirement = 0
        # Net energy requirement for pregnancy (Mcal)
        self.NEpreg_requirement = 0
        # Net energy requirement for lactation (Mcal)
        self.NEl_requirement = 0
        # Metabolizable protein requirement for growth (g)
        self.MP_requirement = 0
        # Calcium requirement (g)
        self.Ca_requirement = 0
        # Phosphorus requirement (g)
        self.P_requirement = 0
        self.P_requirement_process = 0
        # dry matter intake estimation (kg)
        self.DMIest_requirement = 0
        # average body weight in pen
        self.avg_BW = 0
        # average milk production (kg/day)
        self.avg_milk = 0
        # average crude protein content of milk (%)
        self.avg_CP_milk = 0

        self.avg_milk_production_reduction = None

        self.avg_essential_amino_acid_requirement: EssentialAminoAcidRequirements = EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        )

    def calc_pen_requirements(
        self,
        NEmaint_requirement_list: List[float],
        NEa_requirement_list: List[float],
        NEg_requirement_list: List[float],
        NEpreg_requirement_list: List[float],
        NEl_requirement_list: List[float],
        MP_requirement_list: List[float],
        Ca_requirement_list: List[float],
        P_requirement_list: List[float],
        P_requirement_process_list: List[float],
        DMIest_requirement_list: List[float],
        BW: List[float],
        milk: List[float],
        CP_milk: List[float],
        milk_production_reduction: List[float],
        essential_amino_acid_requirement_list: List[EssentialAminoAcidRequirements],
        calc_method: str = "mean",
    ) -> None:
        """
        This functions sets the average (or median or #th percentile) pen requirements. Each input parameter is a list
        of floats generated in ration_driver.set_requirements

        Parameters
        ----------
        NEmaint_requirement_list: List[float]
            List of net energy for maintenance requirement (Mcal) for all animals in pen
        NEa_requirement_list: List[float]
            List of Net energy for activity requirement (Mcal) for all animals in pen
        NEg_requirement_list: List[float]
            List of Net energy for growth requirement (Mcal) for all animals in pen
        NEpreg_requirement_list: List[float]
            List of Net energy requirement for pregnancy (Mcal) for all animals in pen
        NEl_requirement_list: List[float]
            List of Net energy requirement for lactation (Mcal) for all animals in pen
        MP_requirement_list: List[float]
            List of Metabolizable protein requirement for growth (g) for all animals in pen
        Ca_requirement_list: List[float]
            List of Calcium requirement (g) for all animals in pen
        P_requirement_list: List[float]
            List of Phosphorus requirement (g) for all animals in pen, as calculated using NASEM or NRC equations
        P_requirement_process_list: List[float]
            List of Phosphorus requirement (g) for all animals in pen, as calculated in phosphorus_rqmts
        DMIest_requirement_list: List[float]
            List of dry matter intake estimation (kg) for all animals in pen
        BW: List[float]
            List of body weight (kg) for all animals in the pen for all animals in pen
        milk: List[float]
            List of milk production of the animals in the pen (kg)
        CP_milk: List[float]
            List of milk crude protein content of the animals in the pen (%)
        milk_production_reduction: List[float]
            list of milk_production_reduction values for all animals in the pen (kg)
        calc_method: str
            The summary statistic to be used (e.g. mean, median, etc)
        essential_amino_acid_requirement_list: List[EssentialAminoAcidRequirements]
            List of essential amino acid requirements (g).
        """

        attr_names_to_args_map: Dict[str, List[float | EssentialAminoAcidRequirements]] = {
            "NEmaint_requirement": NEmaint_requirement_list,
            "NEa_requirement": NEa_requirement_list,
            "NEg_requirement": NEg_requirement_list,
            "NEpreg_requirement": NEpreg_requirement_list,
            "NEl_requirement": NEl_requirement_list,
            "MP_requirement": MP_requirement_list,
            "Ca_requirement": Ca_requirement_list,
            "P_requirement": P_requirement_list,
            "P_requirement_process": P_requirement_process_list,
            "DMIest_requirement": DMIest_requirement_list,
            "avg_BW": BW,
            "avg_milk": milk,
            "avg_CP_milk": CP_milk,
            "avg_milk_production_reduction": milk_production_reduction,
            "avg_essential_amino_acid_requirement": essential_amino_acid_requirement_list,
        }

        calc_method_to_function_map: dict[str, Callable[..., float]] = {
            "mean": np.mean,
            "median": np.median,
            "percentile": np.percentile,
        }

        default_percentile = 90
        stats_args = [default_percentile] if calc_method == "percentile" else []

        for attribute_name, arg in attr_names_to_args_map.items():
            if attribute_name == "avg_essential_amino_acid_requirement":
                setattr(
                    self,
                    attribute_name,
                    EssentialAminoAcidRequirements(
                        histidine=calc_method_to_function_map[calc_method](
                            [eaa_req.histidine for eaa_req in arg], *stats_args
                        ),
                        isoleucine=calc_method_to_function_map[calc_method](
                            [eaa_req.isoleucine for eaa_req in arg], *stats_args
                        ),
                        leucine=calc_method_to_function_map[calc_method](
                            [eaa_req.leucine for eaa_req in arg], *stats_args
                        ),
                        lysine=calc_method_to_function_map[calc_method](
                            [eaa_req.lysine for eaa_req in arg], *stats_args
                        ),
                        methionine=calc_method_to_function_map[calc_method](
                            [eaa_req.methionine for eaa_req in arg], *stats_args
                        ),
                        phenylalanine=calc_method_to_function_map[calc_method](
                            [eaa_req.phenylalanine for eaa_req in arg], *stats_args
                        ),
                        threonine=calc_method_to_function_map[calc_method](
                            [eaa_req.threonine for eaa_req in arg], *stats_args
                        ),
                        thryptophan=calc_method_to_function_map[calc_method](
                            [eaa_req.thryptophan for eaa_req in arg], *stats_args
                        ),
                        valine=calc_method_to_function_map[calc_method](
                            [eaa_req.valine for eaa_req in arg], *stats_args
                        ),
                    ),
                )

            else:
                setattr(
                    self,
                    attribute_name,
                    calc_method_to_function_map[calc_method](arg, *stats_args),
                )

    def set_requirements(self, pen, animal_grouping_scenario, recalc: bool) -> None:
        """
        Calculates the average requirements utilizing cow_requirements.py and an
        input pen to generate the average requirements across a pen. It then
        populates the corresponding class variables.

        Parameters
        ----------
        pen : Pen
            Instance of an object of class Pen

        animal_grouping_scenario : AnimalGroupingScenario
            a grouping scenario fixed for current simulation, specified in AnimalManager

        recalc : boolean
            True if requirements need to be recalculated since grouping
        """
        requirements_lists: dict[str, list[float | EssentialAminoAcidRequirements]] = {
            "NEmaint_requirement": [],
            "NEa_requirement": [],
            "NEg_requirement": [],
            "NEpreg_requirement": [],
            "NEl_requirement": [],
            "MP_requirement": [],
            "Ca_requirement": [],
            "P_requirement": [],
            "P_requirement_process": [],
            "DMIest_requirement": [],
            "BW": [],
            "milk": [0],
            "milk_production_reduction": [0],
            "CP_milk": [0],
            "essential_amino_acid_requirement": [],
        }
        if recalc:
            requirements_lists = self.recalculate_requirements(pen, animal_grouping_scenario, requirements_lists)
        else:
            requirements_lists = self.use_existing_requirements(pen, animal_grouping_scenario, requirements_lists)

        self.calc_pen_requirements(
            requirements_lists["NEmaint_requirement"],
            requirements_lists["NEa_requirement"],
            requirements_lists["NEg_requirement"],
            requirements_lists["NEpreg_requirement"],
            requirements_lists["NEl_requirement"],
            requirements_lists["MP_requirement"],
            requirements_lists["Ca_requirement"],
            requirements_lists["P_requirement"],
            requirements_lists["P_requirement_process"],
            requirements_lists["DMIest_requirement"],
            requirements_lists["BW"],
            requirements_lists["milk"],
            requirements_lists["CP_milk"],
            requirements_lists["milk_production_reduction"],
            requirements_lists["essential_amino_acid_requirement"],
            "mean",
        )

        avg_nutrient_rqmts: dict[str, float | EssentialAminoAcidRequirements] = {
            "NEmaint_requirement": self.NEmaint_requirement,
            "NEa_requirement": self.NEa_requirement,
            "NEg_requirement": self.NEg_requirement,
            "NEpreg_requirement": self.NEpreg_requirement,
            "NEl_requirement": self.NEl_requirement,
            "MP_requirement": self.MP_requirement,
            "Ca_requirement": self.Ca_requirement,
            "P_req": self.P_requirement,
            "P_req_process": self.P_requirement_process,
            "DMIest_requirement": self.DMIest_requirement,
            "avg_BW": self.avg_BW,
            "avg_milk_production_reduction_pen": self.avg_milk_production_reduction,
            "avg_essential_amino_acid_requirement": self.avg_essential_amino_acid_requirement,
        }

        pen.set_avg_nutrient_rqmts(avg_nutrient_rqmts)

        pen.set_milk_avgs(self.avg_milk, self.avg_CP_milk, self.avg_milk_production_reduction)

    def recalculate_requirements(
        self,
        pen,
        animal_grouping_scenario,
        requirements_lists: Dict[str, List[float | EssentialAminoAcidRequirements]],
    ) -> Dict[str, List[float | EssentialAminoAcidRequirements]]:
        """
        Calculates requirements for every animal in a pen and appends each value to a list in a dictionary
         of requirements.

        Parameters
        ----------
        pen : Pen
            Instance of an object of class Pen

        animal_grouping_scenario : AnimalGroupingScenario
            the valid animal combinations inside the pen, an instance of the AnimalCombination Enum

        requirements_lists : Dict[str, List[float]]
            Dictionary of requirements for each animal

        Returns
        -------
        requirements_list : Dict[str, List[float]]
            Dictionary of lists of animal requirements for all animals

        """
        for animal_id in pen.animals_in_pen:
            animal = pen.animals_in_pen[animal_id]
            animal_type = animal_grouping_scenario.get_animal_type(animal)
            if animal_type in [AnimalType.HEIFER_I]:
                req = self.calc_rqmts(
                    body_weight=animal.body_weight,
                    mature_body_weight=animal.mature_body_weight,
                    day_of_pregnancy=None,
                    animal_type=animal_type,
                    body_condition_score_5=3,
                    previous_temperature=15,
                    average_daily_gain_heifer=animal.daily_growth,
                )
            elif animal_type in [
                AnimalType.HEIFER_II,
                AnimalType.HEIFER_III,
                AnimalType.DRY_COW,
            ]:
                req = self.calc_rqmts(
                    body_weight=animal.body_weight,
                    mature_body_weight=animal.mature_body_weight,
                    day_of_pregnancy=animal.days_in_preg,
                    animal_type=animal_type,
                    body_condition_score_5=3,
                    previous_temperature=15,
                    average_daily_gain_heifer=animal.daily_growth,
                )
            elif animal_type in [AnimalType.LAC_COW]:
                req = self.calc_rqmts(
                    body_weight=animal.body_weight,
                    mature_body_weight=animal.mature_body_weight,
                    day_of_pregnancy=animal.days_in_preg,
                    animal_type=animal_type,
                    parity=animal.calves,
                    calving_interval=animal.CI,
                    milk_true_protein=animal.mPrt,
                    milk_fat=animal.fat_percent,
                    milk_lactose=animal.lactose_milk,
                    milk_production=animal.estimated_daily_milk_produced,
                    days_in_milk=animal.days_in_milk,
                    lactating=animal.milking,
                )

            animal.NEmaint_requirement = req["NEmaint_requirement"]
            animal.NEg_requirement = req["NEg_requirement"]
            animal.NEpreg_requirement = req["NEpreg_requirement"]
            animal.NEl_requirement = req["NEl_requirement"]
            animal.MP_requirement = req["MP_requirement"]
            animal.Ca_requirement = req["Ca_requirement"]
            animal.P_requirement = req["P_requirement"]
            animal.DMIest_requirement = req["DMIest_requirement"]
            animal.essential_amino_acid_requirement = req["essential_amino_acid_requirement"]
            # these animal class variables are only used for grouping purposes
            if animal_type in [AnimalType.LAC_COW]:
                animal.DNED_requirement = (
                    req["NEmaint_requirement"] + req["NEl_requirement"]
                ) / animal.DMIest_requirement
                animal.DMDP_requirement = (req["MP_requirement"]) / animal.DMIest_requirement

                # calculating the activity requirement for energy
                animal.calc_daily_walking_dist(pen.vertical_dist_to_parlor, pen.horizontal_dist_to_parlor)
                NEa_val = self.energy_activity_rqmts(
                    animal.body_weight,
                    pen.housing_type,
                    (math.sqrt(animal.DVD**2 + animal.DHD**2)),
                )
                requirements_lists["milk"].append(animal.estimated_daily_milk_produced)
                requirements_lists["milk_production_reduction"].append(animal.milk_production_reduction)
                requirements_lists["CP_milk"].append(animal.CP_milk)
            else:
                NEa_val = 0

            requirements_lists["NEmaint_requirement"].append(req["NEmaint_requirement"])
            requirements_lists["NEa_requirement"].append(NEa_val)
            requirements_lists["NEg_requirement"].append(req["NEg_requirement"])
            requirements_lists["NEpreg_requirement"].append(req["NEpreg_requirement"])
            requirements_lists["NEl_requirement"].append(req["NEl_requirement"])
            requirements_lists["MP_requirement"].append(req["MP_requirement"])
            requirements_lists["Ca_requirement"].append(req["Ca_requirement"])
            requirements_lists["P_requirement"].append(req["P_requirement"])
            requirements_lists["P_requirement_process"].append(animal.p_req)
            requirements_lists["DMIest_requirement"].append(req["DMIest_requirement"])
            requirements_lists["BW"].append(animal.body_weight)
            requirements_lists["essential_amino_acid_requirement"].append(animal.essential_amino_acid_requirement)
        return requirements_lists

    def use_existing_requirements(
        self,
        pen,
        animal_grouping_scenario,
        requirements_lists: Dict[str, List[float | EssentialAminoAcidRequirements]],
    ) -> Dict[str, List[float | EssentialAminoAcidRequirements]]:
        """
        Finds previous set of requirements for every animal in a pen and appends each value to a list in a dictionary
         of requirements.
        In the case of net energy for activity, this must be recalculated for lactating animals.

        Parameters
        ----------
        pen : Pen
            Instance of an object of class Pen

        animal_grouping_scenario : AnimalGroupingScenario
            the valid animal combinations inside the pen, an instance of the AnimalCombination Enum

        requirements_lists : Dict[str, List[float]]
            Dictionary of requirements for each animal

        Returns
        -------
        requirements_list : Dict[str, List[float]]
            Dictionary of lists of animal requirements for all animals in pen

        """
        for animal_id in pen.animals_in_pen:
            animal = pen.animals_in_pen[animal_id]
            animal_type = animal_grouping_scenario.get_animal_type(animal)
            if animal_type in [AnimalType.LAC_COW]:
                animal.calc_daily_walking_dist(pen.vertical_dist_to_parlor, pen.horizontal_dist_to_parlor)
                NEa_val = self.energy_activity_rqmts(
                    animal.body_weight,
                    pen.housing_type,
                    (math.sqrt(animal.DVD**2 + animal.DHD**2)),
                )
                requirements_lists["milk"].append(animal.estimated_daily_milk_produced)
                requirements_lists["milk_production_reduction"].append(animal.milk_production_reduction)
                requirements_lists["CP_milk"].append(animal.CP_milk)
            else:
                NEa_val = 0

            requirements_lists["NEmaint_requirement"].append(animal.NEmaint_requirement)
            requirements_lists["NEa_requirement"].append(NEa_val)
            requirements_lists["NEg_requirement"].append(animal.NEg_requirement)
            requirements_lists["NEpreg_requirement"].append(animal.NEpreg_requirement)
            requirements_lists["NEl_requirement"].append(animal.NEl_requirement)
            requirements_lists["MP_requirement"].append(animal.MP_requirement)
            requirements_lists["Ca_requirement"].append(animal.Ca_requirement)
            requirements_lists["P_requirement"].append(animal.P_requirement)
            requirements_lists["P_requirement_process"].append(animal.p_req)
            requirements_lists["DMIest_requirement"].append(animal.DMIest_requirement)
            requirements_lists["BW"].append(animal.body_weight)
            requirements_lists["essential_amino_acid_requirement"].append(animal.essential_amino_acid_requirement)
        return requirements_lists

    def calc_rqmts(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int,
        animal_type: AnimalType,
        parity: int | None = 0,
        calving_interval: int | None = None,
        milk_true_protein: float | None = 0.0,
        milk_fat: float | None = 0.0,
        milk_lactose: float | None = 0.0,
        milk_production: float | None = 0.0,
        days_in_milk: int | None = None,
        lactating: bool | None = False,
        body_condition_score_5: int | None = 3,
        previous_temperature: float | None = None,
        average_daily_gain_heifer: float | None = None,
        NDF_conc: float | None = 0.3,
        TDN_conc: float | None = 0.7,
        net_energy_diet_concentration: float | None = 1.0,
        days_born: float | None = None,
    ) -> Dict[str, float | EssentialAminoAcidRequirements]:
        """
        Calculates the dietary requirements of a single animal.

        The energy requirements calculated according to NRC (2001) or NASEM (2021) are values that are used
        to generate the constraints or RHS of the nonlinear program for diet optimization.
        Each calculation has a reference to the respective calculation in the pseudocode (both Cow and Heifer).
        (Note that arguments that are only for a single animal class are instantiated
        at None however the respective parameters must be set when calling said
        animal class)
        Parameters
        ----------
        body_weight: float
            Body weight (kg)
        mature_body_weight: float
            Mature body weight(kg)
        animal_type: AnimalType
            A type or subtype of animal specified in AnimalType enum
        day_of_pregnancy: str, optional
            Day of pregnancy (d) (except Heifer Is)
        # parameters for just cow requirements)
        parity: int, optional
            Number of parity
        calving_interval: int, optional
            Calving interval (d)
        milk_true_protein: float, optional
            Milk true protein content  (% of milk)
        milk_fat: float, optional
            Milk fat content (% of milk)
        milk_lactose: float, optional
            Milk lactose content (% of milk)
        milk_production: float, optional
            Milk production (kg)
        days_in_milk: int, optional
            Days in milk
        lactating: bool, optional
            Boolean value which is true for lactating cows and false for dry cows
        # parameters for just heifer requirements
        body_condition_score_5: int, optional
            Body Condition Score (1-5 basis)
        previous_temperature: float, optional
            Average daily temperature of last month, °C
        average_daily_gain_heifer: float, optional
            Average daily gain of a heifer
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.
        TDN_conc:
            Concentration (percent value) of Total Digestible Nutrients in previously fed ration.
        net_energy_diet_concentration : float
            Metabolizable energy density of formulated ration
        days_born : float
            number of days since birth

        Returns
        -------
        Dict[str, float]
            dictionary of requirement values, see individual functions for each key value pair
        """
        essential_amino_acid_requirement: EssentialAminoAcidRequirements = EssentialAminoAcidRequirements(
            histidine=0.0,
            isoleucine=0.0,
            leucine=0.0,
            lysine=0.0,
            methionine=0.0,
            phenylalanine=0.0,
            threonine=0.0,
            thryptophan=0.0,
            valine=0.0,
        )
        if Animal.config["nutrient_standard"] == "NRC":
            (
                net_energy_maintenance,
                conceptus_weight,
                calf_birth_weight,
            ) = self.calculate_NRC_energy_maintenance_requirements(
                body_weight,
                mature_body_weight,
                day_of_pregnancy,
                body_condition_score_5,
                previous_temperature,
                animal_type,
            )
            (
                net_energy_growth,
                average_daily_gain,
                equivalent_shrunk_body_weight,
            ) = self.calculate_NRC_energy_growth_requirements(
                body_weight,
                mature_body_weight,
                conceptus_weight,
                animal_type,
                parity,
                calving_interval,
                average_daily_gain_heifer,
            )
            net_energy_pregnancy = self.calculate_NRC_energy_pregnancy_requirements(day_of_pregnancy, calf_birth_weight)
            net_energy_lactation = self.calculate_NRC_energy_lactation_requirements(
                animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
            )
            dry_matter_intake_estimate = self.calculate_NRC_DMI(
                animal_type,
                body_weight,
                day_of_pregnancy,
                days_in_milk,
                milk_production,
                milk_fat,
                net_energy_diet_concentration,
                days_born,
            )
            metabolizable_protein_requirement = self.calculate_NRC_protein_requirements(
                body_weight,
                conceptus_weight,
                day_of_pregnancy,
                animal_type,
                milk_production,
                milk_true_protein,
                calf_birth_weight,
                net_energy_growth,
                average_daily_gain,
                equivalent_shrunk_body_weight,
                dry_matter_intake_estimate,
                TDN_conc,
            )
            calcium_requirement = self.calculate_NRC_calcium_requirements(
                body_weight,
                mature_body_weight,
                day_of_pregnancy,
                animal_type,
                average_daily_gain,
                milk_production,
            )
            phosphorus_requirement = self.calculate_NRC_phosphorus_requirements(
                body_weight,
                mature_body_weight,
                day_of_pregnancy,
                milk_production,
                animal_type,
                average_daily_gain,
                dry_matter_intake_estimate,
            )

        elif Animal.config["nutrient_standard"] == "NASEM":
            net_energy_lactation = self.calculate_NASEM_energy_lactation_requirements(
                animal_type, milk_fat, milk_true_protein, milk_lactose, milk_production
            )
            dry_matter_intake_estimate = self.calculate_NASEM_DMI(
                body_weight,
                mature_body_weight,
                days_in_milk,
                lactating,
                net_energy_lactation,
                parity,
                body_condition_score_5,
                NDF_conc,
            )
            (
                net_energy_maintenance,
                gravid_uterine_weight,
                uterine_weight,
            ) = self.calculate_NASEM_energy_maintenance_requirements(
                body_weight, mature_body_weight, day_of_pregnancy, days_in_milk
            )
            (
                net_energy_growth,
                average_daily_gain,
                frame_weight_gain,
            ) = self.calculate_NASEM_energy_growth_requirements(
                body_weight,
                mature_body_weight,
                average_daily_gain_heifer,
                animal_type,
                parity,
                calving_interval,
            )
            (
                net_energy_pregnancy,
                gravid_uterine_weight_gain,
            ) = self.calculate_NASEM_energy_pregnancy_requirements(
                lactating,
                day_of_pregnancy,
                days_in_milk,
                gravid_uterine_weight,
                uterine_weight,
            )
            metabolizable_protein_requirement = self.calculate_NASEM_protein_requirements(
                lactating,
                body_weight,
                frame_weight_gain,
                gravid_uterine_weight_gain,
                dry_matter_intake_estimate,
                milk_true_protein,
                milk_production,
                NDF_conc,
            )
            AA_calculator = AminoAcidCalculator()
            essential_amino_acid_requirement = AA_calculator.calculate_essential_amino_acid_requirements(
                animal_type,
                lactating,
                body_weight,
                frame_weight_gain,
                gravid_uterine_weight_gain,
                dry_matter_intake_estimate,
                milk_true_protein,
                milk_production,
                NDF_conc,
            )
            calcium_requirement = self.calculate_NASEM_calcium_requirements(
                body_weight,
                mature_body_weight,
                day_of_pregnancy,
                average_daily_gain,
                dry_matter_intake_estimate,
                milk_true_protein,
                milk_production,
                parity,
            )
            phosphorus_requirement = self.calculate_NASEM_phosphorus_requirements(
                body_weight,
                mature_body_weight,
                animal_type,
                day_of_pregnancy,
                average_daily_gain,
                dry_matter_intake_estimate,
                milk_true_protein,
                milk_production,
                parity,
            )
        else:
            nutrient_standard_error = f"Nutrient Standard {Animal.config['nutrient_standard']} not supported"
            info_map = {"function": self.calc_rqmts}
            om.add_error("nutrient_standard_error", nutrient_standard_error, info_map)
            raise ValueError(nutrient_standard_error)

        if Animal.config["ration"]["phosphorus_requirement_buffer"] > 0:
            phosphorus_requirement = phosphorus_requirement * (
                1 + (Animal.config["ration"]["phosphorus_requirement_buffer"] * GeneralConstants.PERCENTAGE_TO_FRACTION)
            )
        # Requirements summary dictionary
        return {
            "NEmaint_requirement": net_energy_maintenance,
            "NEg_requirement": net_energy_growth,
            "NEpreg_requirement": net_energy_pregnancy,
            "NEl_requirement": net_energy_lactation,
            "MP_requirement": metabolizable_protein_requirement,
            "Ca_requirement": calcium_requirement,
            "P_requirement": phosphorus_requirement,
            "DMIest_requirement": dry_matter_intake_estimate,
            "essential_amino_acid_requirement": essential_amino_acid_requirement,
        }

    def calculate_NRC_energy_maintenance_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        body_condition_score_5: int,
        previous_temperature: float | None,
        animal_type: AnimalType,
    ) -> tuple[float, float, float]:
        """Calculates energy requirement for maintenance, conceptus weight, and calf birth weight

        Calculates the estimated energy requirements for maintenance in megacalories per day,
        as well as conceptus weight (kg) and calf birth weight (kg), according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int
            Day of pregnancy (days)
        body_condition_score_5 : int
            Body condition score (score from 1 to 5)
        previous_temperature : float
            Adjustment for previous temperature
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum

        Returns
        -------
        net_energy_maintenance : float
            Net energy requirement for maintenance (mcal/day)
        conceptus_weight : float
            Conceptus weight (kg)
        calf_birth_weight : float
            Calf birth weight (kg)

        Notes
        -----
        Energy requirements for activity are not included within calculations for maintenance.

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 2 "Energy",pp. 18-25, 2001.

        """
        calf_birth_weight = mature_body_weight * 0.06275 if day_of_pregnancy else 0.0
        conceptus_weight = 0.0
        if day_of_pregnancy and day_of_pregnancy > 190:
            conceptus_weight = (18 + (day_of_pregnancy - 190) * 0.665) * (calf_birth_weight / 45)
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            net_energy_maintenance = 0.08 * (body_weight - conceptus_weight) ** 0.75
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            body_condition_score_9 = (body_condition_score_5 - 1) * 2 + 1
            net_energy_maintenance = (body_weight - conceptus_weight) ** (0.75) * (
                0.086 * (0.8 + (body_condition_score_9 - 1) * 0.05)
            ) + 0.0007 * (20 - previous_temperature)
        return net_energy_maintenance, conceptus_weight, calf_birth_weight

    def calculate_NASEM_energy_maintenance_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        days_in_milk: int | None,
    ) -> tuple[float, float, float]:
        """Calculates energy requirement for maintenance and two measures of uterine weight

        The estimated energy requirements for maintenance are calculated in megacalories per day,
        as well as gravid uterine weight and uterine weight in kg, according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        day_of_pregnancy : int
            Day of pregnancy (days)
        days_in_milk : int
            Days in milk (lactation)

        Returns
        -------
        net_energy_maintenance : float
            Net energy requirement for maintenance (mcal/day)
        gravid_uterine_weight : float
            Gravid uterine weight (kg))
        uterine_weight : float
            Uterine weight (kg))

        Notes
        -----
        # NASEM (2021) does not adjust energy requirements for environmental temperature as it assumes
        # that confinement conditions already provide comfort temperature to the animals.
        # This is something to consider and update for the grazing module
        # Instead of calculating calf_birth_weight, NASEM (2021) also contains standards calf_birth_weight and
        # mature_body_weight (tabulated values) for selected breeds (eg., Holstein)
        # Instead of estimating conceptus_weight, gain in pregnancy tissues is estimated:
        # (gravid_uterine_weight and uterine_weight).
        # day_of_pregnancy (Day of pregnancy) was kept instead of DGest (Day ofgestation) as it is in NASEM (2021) book.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 29, 2021.
        """
        if day_of_pregnancy is None:
            net_energy_maintenance = 0.10 * body_weight**0.75
            gravid_uterine_weight = 0.0
            uterine_weight = 0.0
        else:
            calf_birth_weight = mature_body_weight * 0.06275
            gravid_uterine_weight = (calf_birth_weight * 1.825) * math.exp(
                -(0.0243 - (0.0000245 * day_of_pregnancy)) * (280 - day_of_pregnancy)
            )
            if days_in_milk is None:
                days_in_milk = 0
            uterine_weight = ((calf_birth_weight * 0.2288 - 0.204) * math.exp(-0.2 * days_in_milk)) + 0.204
            net_energy_maintenance = 0.10 * (body_weight - gravid_uterine_weight - uterine_weight) ** 0.75
        return net_energy_maintenance, gravid_uterine_weight, uterine_weight

    def calculate_NRC_energy_growth_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        conceptus_weight: float,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
        average_daily_gain_heifer: float | None,
    ) -> tuple[float, float, float]:
        """Calculates energy requirement for growth and associated weight gain parameters.

        The estimated energy requirements for growth in megacalories per day,
        and average daily gain and estimate of shrunk body weight, in kilograms are calculated according to NRC (2001).

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        mature_body_weight : float
            Mature body weight (kg)
        conceptus_weight : float
            Conceptus weight (kg)
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum
        parity : int
            Parity number (lactation 1, 2.. n)
        calving_interval : int
            Calving interval (days)
        average_daily_gain_heifer : float
            Average daily gain (grams per day)

        Returns
        -------
        net_energy_growth : float
            Net energy requirement for growth (Mcal/d)
        average_daily_gain : float
            Average daily gain (grams per day)
        equivalent_shrunk_body_weight : float
            Equivalent shrunk body weight (kilograms)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
        Chapter 11 "Growth", pp. 234-243, 2001.
        """
        # Activity requirements
        # ---------------------
        # Activity requirements must be calculated after grouping and thus is in a
        # separate function
        # Growth requirements
        # ---------------------
        # [A.Cow.A.7]-[A.Heifer.A.8]
        # Mature shrunk body weight (kg)
        MSBW = 0.96 * mature_body_weight
        # [A.Cow.A.8]-[A.Heifer.A.9]
        # Shrunk body weight (kg)
        SBW = 0.96 * body_weight
        # [A.Cow.A.9]-[A.Heifer.A.10]
        # Empty body weight (kg)
        # EBW = 0.891 * SBW
        # [A.Cow.A.10]-[A.Heifer.A.11]
        # Equivalent shrunk body weight (kg)
        equivalent_shrunk_body_weight = (SBW - conceptus_weight) * (478 / MSBW)
        # [A.Cow.A.11]
        # Average Daily Gain (kg)
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            if parity == 1 and calving_interval != 0:
                average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
            elif parity == 2 and calving_interval != 0:
                average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
            else:
                average_daily_gain = 0.0
        # [A.Heifer.A.12]
        # Average Daily Gain (kg)
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            average_daily_gain = max(average_daily_gain_heifer, 0.0)
        # [A.Cow.A.12]-[A.Heifer.A.13]
        # Equivalent empty weight gain (kg)
        EQEBG = 0.956 * average_daily_gain
        # [A.Cow.A.13]-[A.Heifer.A.14]
        # Equivalent shrunk body weight (kg)
        EQEBW = 0.891 * equivalent_shrunk_body_weight
        # [A.Cow.A.14]-[A.Heifer.A.15]
        # Net energy for growth requirement (Mcal)
        net_energy_growth = 0.0635 * EQEBW**0.75 * EQEBG**1.097
        return net_energy_growth, average_daily_gain, equivalent_shrunk_body_weight

    def calculate_NASEM_energy_growth_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        average_daily_gain_heifer: float | None,
        animal_type: AnimalType,
        parity: int,
        calving_interval: int | None,
    ) -> tuple[float, float, float]:
        """Calculates energy requirement for growth, and also growth metrics

        Calculates the estimated energy requirements requirements for growth in megacalories per day,
        and associated growth metrics, according to NASEM (2021).

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        average_daily_gain_heifer : float
            Average daily gain (grams per day)
        animal_type : AnimalType
            A type or subtype of animal specified in AnimalType enum
        parity : int
            Parity number (lactation 1, 2.. n)
        calving_interval : int
            Calving interval (days)

        Returns
        -------
        net_energy_growth : float
            Net energy requirement for frame growth (Mcal/d)
        average_daily_gain : float
            Average daily gain (grams per day)
        frame_weight_gain : float
            Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)

        Notes
        -----
        # In NASEM (2021), body frame gain (fat + protein) corresponds to the true growth and it is part
        # of the calculation which is further partitioned to body reserves or condition gain (or loss),
        # and pregnancy-associated gain (considered a pregnancy requirement).

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 32-35, 2021.

        """
        MSBW = 0.96 * mature_body_weight
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            if parity == 1 and calving_interval != 0:
                average_daily_gain = ((0.92 - 0.82) * MSBW) / calving_interval
            elif parity == 2 and calving_interval != 0:
                average_daily_gain = ((1 - 0.92) * MSBW) / calving_interval
            else:
                average_daily_gain = 0.0
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            average_daily_gain = max(average_daily_gain_heifer, 0.0)
        else:
            average_daily_gain = 0.0
        EBG = 0.85 * average_daily_gain
        if average_daily_gain == 0:
            average_daily_gain = 0.00001  # fix to avoid divide by 0 error
        FatADG = (0.067 + 0.375 * (body_weight / mature_body_weight)) * EBG / average_daily_gain
        ProtADG = (0.201 - 0.081 * (body_weight / mature_body_weight)) * EBG / average_daily_gain
        frame_weight_gain = FatADG + ProtADG
        REFADG = (9.4 * FatADG + 5.55 * ProtADG) * average_daily_gain
        # MEFrameADG = REFADG / 0.4  # Possible future use for this calc, see docstring notes
        net_energy_growth = REFADG / 0.61
        return net_energy_growth, average_daily_gain, frame_weight_gain

    def calculate_NRC_energy_pregnancy_requirements(
        self, day_of_pregnancy: int | None, calf_birth_weight: float
    ) -> float:
        """Calculates energy requirement for pregnancy according to NRC (2001).

        Calculates the estimated energy requirements for pregnancy in megacalories per day

        Parameters
        ----------
        day_of_pregnancy : int
            Day of pregnancy (days)
        calf_birth_weight : float
            Calf birth weight (kilograms)

        Returns
        -------
        net_energy_pregnancy : float
            Net energy requirement for pregnancy (Mcal/d)

        Notes
        -----
        # day_of_pregnancy are counted from 190 day_of_pregnancy once pregnancy is confirmed. Otherwise,
        this nutritional requirement is assumed to be zero.

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 2 "Energy", pp. 21-22, 2001.

        """
        # Pregnancy requirement
        # ---------------------
        # [A.Cow.A.15]-[A.Heifer.A.16]
        # Metabolizable energy requirement for pregnancy (Mcal)
        if day_of_pregnancy is None:
            MEpreg = 0.0
        elif day_of_pregnancy > 190:
            MEpreg = (2 * 0.00159 * day_of_pregnancy - 0.0352) * (calf_birth_weight / (45 * 0.14))
        else:
            MEpreg = 0.0
        # [A.Cow.A.16]-[A.Heifer.A.17]
        # Net energy requirement for pregnancy (Mcal)
        net_energy_pregnancy = MEpreg * 0.64
        return net_energy_pregnancy

    def calculate_NASEM_energy_pregnancy_requirements(
        self,
        lactating: bool,
        day_of_pregnancy: int | None,
        days_in_milk: int | None,
        gravid_uterine_weight: float,
        uterine_weight: float,
    ) -> tuple[float, float]:
        """Calculates energy requirement for pregnancy and gravid uterine weight gain

        Calculates the estimated energy requirements requirements for pregnancy in megacalories per day,
        according to NASEM (2021).

        Parameters
        ----------
        lactating : bool
            Physiological condition
        day_of_pregnancy : int
            Day of pregnancy
        days_in_milk : int
            Days in milk (lactation, days)
        gravid_uterine_weight : float
            Gravid uterine weight (kilograms)
        uterine_weight : float
            Uterine weight (kilograms)

        Returns
        -------
        net_energy_pregnancy : float
            Net energy requirement for pregnancy (Mcal/d)
        gravid_uterine_weight_gain : float
            Daily energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)

        Notes
        -----
        # Assumptions: tissue contains 0.882 Mcal of energy / kg; an ME to gestation energy efficiency of 0.14;
        # and ME to net_energy_lactation efficiency of 0.66.MEpreg = Metabolizable energy requirement for pregnancy,
            Mcal net_energy_lactation/day
        # day_of_pregnancy are counted from day 12 of pregnancy once it was confirmed and goes until day 280
            day_of_pregnancy.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 31-32, 2021.

        """

        if lactating:
            gravid_uterine_weight_gain = -0.2 * days_in_milk * (uterine_weight - 0.204)
        elif day_of_pregnancy is None:
            gravid_uterine_weight_gain = 0.0
        else:
            gravid_uterine_weight_gain = (0.0243 - (0.0000245 * day_of_pregnancy)) * gravid_uterine_weight
        if gravid_uterine_weight_gain > 0:
            net_energy_pregnancy = gravid_uterine_weight_gain * (0.882 / 0.14) * 0.66
        else:
            net_energy_pregnancy = gravid_uterine_weight_gain * (0.882 / 0.14)
        return net_energy_pregnancy, gravid_uterine_weight_gain

    def calculate_NRC_energy_lactation_requirements(
        self,
        animal_type: AnimalType,
        milk_fat: float,
        milk_true_protein: float,
        milk_lactose: float,
        milk_production: float,
    ) -> float:
        """Calculates energy requirement for lactation according to NRC (2001).

        Calculates the estimated energy requirements for lactation in megacalories per day

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_fat : float
            Fat contents in milk (%)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_lactose : float
            Lactose contents in milk (%)
        milk_production: float
            Milk production (kg/d)

        Returns
        -------
        net_energy_lactation : float
            Net energy requirement for lactation (Mcal/d)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 2 "Energy", pp. 19, 2001.

        """

        # Lactation requirement
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.A.17]
            # Milk energy (Mcal/kg of milk production)
            milk_energy_Mcal_per_kg = 0.0929 * milk_fat + (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
            # [A.Cow.A.18]
            # Net energy requirement for lactation (Mcal)
            net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
        else:
            net_energy_lactation = 0.0
        return net_energy_lactation

    def calculate_NASEM_energy_lactation_requirements(
        self,
        animal_type: AnimalType,
        milk_fat: float,
        milk_true_protein: float,
        milk_lactose: float,
        milk_production: float,
    ) -> float:
        """Calculates energy requirement for lactation according to NASEM (2021).

        Calculates the estimated energy requirements for lactation in megacalories per day

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_fat : float
            Fat contents in milk (%)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_lactose : float
            Lactose contents in milk (%)
        milk_production: float
            Milk yield (kg/d)

        Returns
        -------
        net_energy_lactation : float
            Net energy requirement for lactation (Mcal/d)

        Notes
        -----
        Same calculations as done in the NRC (2001). Requirements are based on milk yield and composition.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 30, 2021.

        """
        if animal_type in [AnimalType.LAC_COW]:
            milk_energy_Mcal_per_kg = 0.0929 * milk_fat + (0.0547 / 0.93) * milk_true_protein + 0.0395 * milk_lactose
            net_energy_lactation = milk_energy_Mcal_per_kg * milk_production
        else:
            net_energy_lactation = 0.0
        return net_energy_lactation

    def calculate_NRC_protein_requirements(
        self,
        body_weight: float,
        conceptus_weight: float,
        day_of_pregnancy: int | None,
        animal_type: AnimalType,
        milk_production: float,
        milk_true_protein: float,
        calf_birth_weight: float,
        net_energy_growth: float,
        average_daily_gain: float,
        equivalent_shrunk_body_weight: float,
        dry_matter_intake_estimate: float,
        TDN_conc: float | None = 0.7,
    ) -> float:
        """Protein requirement for maintenance according to NRC (2001).

        Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        conceptus_weight : float
            Conceptus weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        milk_production: float
            Milk yield (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        calf_birth_weight : float
            Calf birth weight
        net_energy_growth : float
            Net energy requirement for growth (Mcal/d)
        average_daily_gain : float
            Average daily gain (grams per day)
        equivalent_shrunk_body_weight : float
            Equivalent shrunk body weight (kilograms)
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
        TDN_conc:
            Concentration (percent value) of Total Digestible Nutrients in previously fed ration.

        Returns
        -------
        metabolizable_protein_requirement : float
            Metabolizable protein requirement (grams per day)

        Notes
        -----
        MP_bactria: Bacteria metabolizable protein production, g
        TDN: Total digestible nutrients
        MPm: Metabolizable protein requirement for maintenance, g
        NPg: Net protein requirement for growth, g
        EffMP_NPg: Efficiency of converting metabolizable protein to net protein
        MPg: Metabolizable protein requirement for growth, g
        MPpreg: Metabolizable protein requirement for pregnancy, g
        MPlact: Metabolizable protein requirement for lactation, g

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition."
            National Academic Press, Chapter 5 "Protein and Amino acids",pp. 67-69. 2001;

        """

        # B: PROTEIN REQUIREMENTS:
        # divided into 4 components: maintenance, growth, pregnancy, and lactation
        # --------------------------------------------
        # Maintenance Requirement
        # ---------------------
        # [A.Cow.B.1]-[A.Heifer.B.1]
        # Metabolizable protein requirement for maintenance (g)

        MP_bactria_estimate = dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * TDN_conc * 0.13

        MPm = (
            0.3 * (body_weight - conceptus_weight) ** 0.6
            + 4.1 * (body_weight - conceptus_weight) ** 0.5
            + (
                dry_matter_intake_estimate * GeneralConstants.KG_TO_GRAMS * 0.03
                - 0.5 * (MP_bactria_estimate / 0.68 - MP_bactria_estimate)
            )
            + 0.4 * 11.8 * dry_matter_intake_estimate / 0.67
        )
        # Growth Requirement
        # ---------------------
        # [A.Cow.B.2]-[A.Heifer.B.2]
        # Net protein requirement for growth (g)
        if average_daily_gain == 0:
            NPg = 0.0
        else:
            NPg = average_daily_gain * (268 - 29.4 * (net_energy_growth / average_daily_gain))
        # [A.Cow.B.3]-[A.Heifer.B.3]
        # Efficiency of converting metabolizable protein to net protein
        if equivalent_shrunk_body_weight <= 478:
            EffMP_NPg = (83.4 - 0.114 * equivalent_shrunk_body_weight) / 100
        else:
            EffMP_NPg = 0.28908
        # [A.Cow.B.4]-[A.Heifer.B.4]
        # Metabolizable protein requirement for growth (g)
        MPg = NPg / EffMP_NPg
        # Pregnancy Requirement
        # ---------------------
        # [A.Cow.B.5]-[A.Heifer.B.5]
        # Metabolizable protein requirement for pregnancy (g)
        if day_of_pregnancy is None:
            MPpreg = 0.0
        elif day_of_pregnancy > 190:
            MPpreg = (0.69 * day_of_pregnancy - 69.2) * (calf_birth_weight / (45 * 0.33))
        else:
            MPpreg = 0.0
        # Lactation Requirement
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.B.6]
            MPlact = milk_production * (milk_true_protein / 100) * (GeneralConstants.KG_TO_GRAMS / 0.67)
        # Total Protein Requirement  (g)
        # ---------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.B.7]
            metabolizable_protein_requirement = MPm + MPg + MPpreg + MPlact
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            # [A.Heifer.B.6]
            metabolizable_protein_requirement = MPm + MPg + MPpreg
        return metabolizable_protein_requirement

    def calculate_NASEM_protein_requirements(
        self,
        lactating: bool,
        body_weight: float,
        frame_weight_gain: float,
        gravid_uterine_weight_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        NDF_conc: float,
    ) -> float:
        """Calculates Protein requirement for maintenance according to NASEM (2021).

        Calculates the estimated total metabolizable protein requirement (MP) in kilograms per day

        Parameters
        ----------
        lactating : bool
            Physiological condition
        body_weight : float
            Body weight (kilograms)
        frame_weight_gain : float
            Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)
        gravid_uterine_weight_gain : float
            Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production: float
            Milk yield (kg/d)
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.


        Returns
        -------
        metabolizable_protein_requirement : float
            Total metabolizable protein requirement (grams per day)

        Notes
        -----
        As in the NRC (2021), the protein requirement is also divided into four components: maintenance, growth,
        pregnancy, and lactation (all of them on a metabolizable protein basis (MP, g/d).
        The MP is defined as the sum of rumen undegraded protein (RUP + microbial protein (MCP).
        MP requirements for maintenance includes: scurf + endogenous urinary loss + metabolic fecal protein.
        Current versions of RuFaS code for both NRC and NASEM do not split MP into physiological functions.

        NPscurf: Net protein requirement for scurf, g
        NPEndUrin: Net protein requirement for endogenous urinary excretion, g
        CPMFP: Crude protein in metabolic fecal protein, g
        NPMFP: Net protein requirement for metabolic fecal protein, g
        NPGrowth: Net protein requirement for body frame weight gain, g
        NPGest: Net protein requirement for pregnancy, g
        NPMilk: Net protein in milk, or milk true protein yield, g
        TargetEffMP: Proposed target efficiencies of converting metabolizable protein to export proteins and body gain.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 6 "Protein", pp. 69-104, 2021.
        """
        NPscurf: float = 0.20 * body_weight ** (0.60) * 0.85
        NPEndUrin: float = 53 * UserConstants.NITROGEN_TO_PROTEIN * body_weight * 0.001
        CPMFP: float = (11.62 + 0.134 * NDF_conc) * dry_matter_intake_estimate
        NPMFP: float = CPMFP * 0.73
        NPGrowth: float = frame_weight_gain * 0.11 * 0.86
        NPGest: float = gravid_uterine_weight_gain * 125
        NPMilk: float = (milk_true_protein / 100) * milk_production * GeneralConstants.KG_TO_GRAMS
        TargetEffMP: float = 0.69
        if lactating:
            metabolizable_protein_requirement: float = (
                ((NPscurf + NPMFP + NPMilk + NPGrowth) / TargetEffMP) + (NPGest / 0.33) + NPEndUrin
            )
        else:
            metabolizable_protein_requirement = (
                (NPscurf + NPMFP) / TargetEffMP + (NPGest / 0.33) + (NPGrowth / 0.40) + NPEndUrin
            )
        return metabolizable_protein_requirement

    def calculate_NRC_calcium_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        animal_type: AnimalType,
        average_daily_gain: float,
        milk_production: float,
    ) -> float:
        """Calculates total Calcium requirement according to NRC (2001).

        Calculates the estimated the total calcium requirement (Ca) in grams per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        average_daily_gain : float
            Average daily gain (grams per day)
        milk_production: float
            Milk yield (kg/d)

        Returns
        -------
        calcium_requirement : float
            Calcium requirement (grams per day)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 106-109. 2001.


        """

        # C: MINERAL REQUIREMENTS
        # Calcium and Phosphorus are the only requirements tracked currently
        # --------------------------------------------
        # Calcium Requirements
        # ----------------------
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.C.1]
            # Calcium maintenance requirement (g)
            Ca_maint = 0.031 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [AnimalType.DRY_COW]:
            Ca_maint = 0.0154 * body_weight + 0.08 * (body_weight / 100)
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            # [A.Heifer.C.1]
            # Calcium maintenance requirement (g)
            Ca_maint = 0.0154 * body_weight + 0.08 * (body_weight / 100)
        # [A.Cow.C.2]-[A.Heifer.C.2]
        # Calcium growth requirement (g)
        Ca_growth = 9.83 * mature_body_weight**0.22 * body_weight ** (-0.22) * (average_daily_gain / 0.96)
        # [A.Cow.C.3]-[A.Heifer.C.3]
        # Calcium pregnancy requirement (g)
        if day_of_pregnancy is None:
            Ca_preg = 0.0
        elif day_of_pregnancy > 190:
            Ca_preg = 0.02456 * math.exp(
                (0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy
            ) - 0.02456 * math.exp((0.05581 - 0.00007 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
        else:
            Ca_preg = 0.0
        if animal_type in [AnimalType.LAC_COW]:
            # [A.Cow.C.4]
            # Calcium lactation requirement (g)
            Ca_lact = 1.22 * milk_production
            # [A.Cow.C.5]
            # Total calcium requirement (g)
            calcium_requirement: float = Ca_maint + Ca_growth + Ca_preg + Ca_lact
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            # [A.Heifer.C.4]
            # Total calcium requirement (g)
            calcium_requirement = Ca_maint + Ca_growth + Ca_preg
        return calcium_requirement

    def calculate_NASEM_calcium_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        parity: int,
    ) -> float:
        """Calculates total Calcium requirement according to NASEM (2021).

        Calculates the estimated the total calcium requirement (Ca) in grams per day.

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        average_daily_gain : float
            Average daily gain (grams per day)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production : float
            Milk yield (kg/d)
        parity : int
            Parity number (lactation 1, 2.. n)

        Returns
        -------
        calcium_requirement : float
            Calcium requirement (grams per day)

        Notes
        -----
        NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 7 "Minerals" pp. 106-110, 2021.
        """
        Ca_Maint: float = 0.90 * dry_matter_intake_estimate
        if parity <= 2:
            Ca_Growth: float = ((9.83 * mature_body_weight**-0.22) * body_weight**-0.22) * average_daily_gain
        else:
            Ca_Growth = 0.0
        if day_of_pregnancy is None:
            Ca_Preg: float = 0.0
        else:
            Ca_Preg = 0.02456 * math.exp(
                (0.05581 - 0.00007 * day_of_pregnancy) * day_of_pregnancy
            ) - 0.02456 * math.exp((0.05581 - 0.00007 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1)) * (
                body_weight / 715
            )
        Ca_Lact: float = (0.295 + 0.239 * milk_true_protein) * milk_production
        calcium_requirement: float = Ca_Maint + Ca_Growth + Ca_Preg + Ca_Lact
        return max(calcium_requirement, AnimalModuleConstants.MINIMUM_CALCIUM)

    def calculate_NRC_phosphorus_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        day_of_pregnancy: int | None,
        milk_production: float,
        animal_type: AnimalType,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
    ) -> float:
        """Calculates total Phosphorus requirement according to NRC (2001).

        Calculates the estimated the total phosphorus requirement (P) in grams per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        milk_production: float
            Milk yield (kg/d)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        average_daily_gain : float
            Average daily gain (grams per day)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg/d)

        Returns
        -------
        phosphorus_requirement : float
            Phosphorus requirement (grams per day)

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 6 "Minerals",pp. 109-118. 2001.
        """
        P_growth: float = (1.2 + 4.635 * mature_body_weight**0.22 * body_weight ** (-0.22)) * (
            average_daily_gain / 0.96
        )
        if day_of_pregnancy is None:
            P_preg: float = 0.0
        elif day_of_pregnancy > 190:
            P_preg = 0.02743 * math.exp(
                (0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy
            ) - 0.02743 * math.exp((0.05527 - 0.000075 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
        else:
            P_preg = 0.0
        if animal_type in [AnimalType.LAC_COW]:
            P_maint: float = 1 * dry_matter_intake_estimate + 0.002 * body_weight
            P_lact: float = 0.9 * milk_production
            phosphorus_requirement: float = P_growth + P_preg + P_lact + P_maint
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            P_maint = 0.8 * dry_matter_intake_estimate + 0.002 * body_weight
            phosphorus_requirement = P_growth + P_preg + P_maint
        return phosphorus_requirement

    def calculate_NASEM_phosphorus_requirements(
        self,
        body_weight: float,
        mature_body_weight: float,
        animal_type: AnimalType,
        day_of_pregnancy: int | None,
        average_daily_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float | None,
        milk_production: float | None,
        parity: int,
    ) -> float:
        """Calculates total Phosphorus requirement according to NASEM (2021).

        Calculates the estimated the total phosphorus requirement (P) in grams per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        day_of_pregnancy : int
            Day of pregnancy (days)
        average_daily_gain : float
            Average daily gain (grams per day)
        dry_matter_intake_estimate : float
            Estimated dry matter intake (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production: float
            Milk yield (kg/d)
        parity : int
            Parity number (lactation 1, 2.. n)

        Returns
        -------
        phosphorus_requirement : float
            Phosphorus requirement (grams per day)

        Notes
        -----
        NASEM (2021) calculation for both Ca and P requirements consider milk production variables.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 7 "Minerals" pp. 112, 2021.

        """
        if animal_type in [AnimalType.LAC_COW]:
            P_Maint: float = 1.0 * dry_matter_intake_estimate + 0.0006 * body_weight
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
            AnimalType.DRY_COW,
        ]:
            P_Maint = 0.8 * dry_matter_intake_estimate + 0.0006 * body_weight
        else:
            P_Maint = 0.0
        if parity <= 2:
            P_Growth: float = (1.2 + 4.635 * mature_body_weight**0.22 * body_weight**-0.22) * average_daily_gain
        else:
            P_Growth = 0.0
        if day_of_pregnancy is None or day_of_pregnancy < 190:
            P_Preg: float = 0.0
        else:
            P_Preg = (
                (
                    0.02743 * math.exp((0.05527 - 0.000075 * day_of_pregnancy) * day_of_pregnancy)
                    - 0.02743 * math.exp((0.05527 - 0.000075 * (day_of_pregnancy - 1)) * (day_of_pregnancy - 1))
                )
                * body_weight
                / 715
            )
        if milk_true_protein is None or milk_production is None:
            P_Lact: float = 0.0
        else:
            P_Lact = milk_production * (0.49 + 0.13 * milk_true_protein)
        phosphorus_requirement: float = P_Maint + P_Growth + P_Preg + P_Lact
        return max(phosphorus_requirement, AnimalModuleConstants.MINIMUM_PHOSPHORUS)

    def calculate_NRC_DMI(
        self,
        animal_type: AnimalType,
        body_weight: float,
        day_of_pregnancy: int,
        days_in_milk: int | None,
        milk_production: float,
        milk_fat: float,
        net_energy_diet_concentration: float,
        days_born: float,
    ) -> float:
        """Calculates dry matter intake according to NRC (2001).

        Calculates the estimated total dry matter intake in kilograms per day

        Parameters
        ----------
        animal_type : AnimalType
            A type or subtype of animal specified in the AnimalType enum
        body_weight : float
            Body weight (kilograms)
        day_of_pregnancy : int
            Day of pregnancy (days)
        days_in_milk : int
            Days in milk (days)
        milk_production : float
            Milk yield (kg/d)
        milk_fat : float
            Fat contents in milk (%)
        net_energy_diet_concentration : float
            Metabolizable energy density of formulated ration
        days_born : float
            number of days since birth

        Returns
        -------
        dry_matter_intake_estimate : float
            Dry matter intake (kilograms per day)

        Notes
        -----
        The sum of dry matter intake of each feed is assumed to be less than
        dry matter intake estimation (Sum of Feed < dry_matter_intake_estimate).

        References
        ----------
        .. [1] National Research Council, "Nutrient Requirements of Dairy Cattle, 7th edition." National Academic Press,
            Chapter 1 "Dry Matter Intake",
            pp. 4; and pp. 325, 2001 (Equations 1 and 2), and pp. 326 for heifers

        """
        if net_energy_diet_concentration < 1.0:
            DivFact = 0.95
        else:
            DivFact = net_energy_diet_concentration

        if animal_type in [AnimalType.LAC_COW]:
            fat_corrected_milk_kg = (0.4 * milk_production) + (15 * milk_fat * (milk_production / 100))
            dry_matter_intake_estimate: float = (0.372 * fat_corrected_milk_kg + 0.0968 * body_weight**0.75) * (
                1 - math.exp(-0.192 * ((days_in_milk / 7) + 3.67))
            )
        elif animal_type in [AnimalType.DRY_COW]:
            dry_matter_intake_estimate = ((1.97 - 0.75 * math.exp(0.16 * (day_of_pregnancy - 280))) / 100) * body_weight
        else:
            if days_born and days_born > 365:
                value_to_use = 0.1128
            else:
                value_to_use = 0.0869
            dry_matter_intake_estimate = (
                body_weight**0.75 * (0.2435 * DivFact - 0.0466 * DivFact**2 - value_to_use) / DivFact
            )
            if day_of_pregnancy and day_of_pregnancy >= 210:
                adjustment_factor = 1 + ((210 - day_of_pregnancy) * 0.0025)
                dry_matter_intake_estimate -= adjustment_factor
        return max(
            dry_matter_intake_estimate,
            AnimalModuleConstants.MINIMUM_DAILY_DMI_RATIO * body_weight,
            AnimalModuleConstants.MINIMUM_DMI,
        )

    def calculate_NASEM_DMI(
        self,
        body_weight: float,
        mature_body_weight: float,
        days_in_milk: int | None,
        lactating: bool,
        net_energy_lactation: float,
        parity: int,
        body_condition_score_5: int,
        NDF_conc: float,
    ) -> float:
        """Calculates dry matter intake according to NASEM (2021).

        Calculates the estimated total dry matter intake in kilograms per day

        Parameters
        ----------
        body_weight : float
            Body weight (kilograms)
        mature_body_weight : float
            Mature body weight (kilograms)
        days_in_milk : int
            Days in milk (days)
        lactating : bool
            Physiological condition (conditional)
        net_energy_lactation : float
            Net energy for lactation
        parity : int
            Parity number
        body_condition_score_5 : int
            Body condition score (score; scale from 1 to 5)
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.

        Returns
        -------
        dry_matter_intake_estimate: float
            Dry matter intake (kilograms per day)

        Notes
        -----
        The sum of dry matter intake of each feed is assumed to be less than
        dry matter intake estimation (Sum of Feed < DMIest).
        There are additional equation in NASEM (2021) book including neutral detergent concentrations in the diet
        for both lactating (page 12) and growing animals (page 14). [1]

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 2 "Dry matter intake" pp. 7-20, 2021.
        """
        if lactating:
            parity_adjustment_factor = 0
            if parity > 1:
                parity_adjustment_factor = 1
            dry_matter_intake_estimate = (
                (3.7 + parity_adjustment_factor * 5.7)
                + 0.305 * net_energy_lactation
                + 0.022 * body_weight
                + (-0.689 - 1.87 * parity_adjustment_factor) * body_condition_score_5
            ) * (1 - (0.212 + parity_adjustment_factor * 0.136) * math.exp(-0.053 * days_in_milk))
        else:
            dry_matter_intake_estimate = (
                0.0226 * mature_body_weight * (1 - math.exp(-1.47 * (body_weight / mature_body_weight)))
            ) - (
                0.082
                * (
                    NDF_conc
                    - (
                        23.1
                        + 56 * (body_weight / mature_body_weight)
                        - 30.6 * (body_weight / mature_body_weight) ** 2.0
                    )
                )
            )
        return max(
            dry_matter_intake_estimate,
            AnimalModuleConstants.MINIMUM_DAILY_DMI_RATIO * body_weight,
            AnimalModuleConstants.MINIMUM_DMI,
        )

    def energy_activity_rqmts(self, body_weight: float, housing: str, distance: float) -> float:
        """
        Calculates the net energy for activity requirement portion of the energy
        requirements for animals. This is separate because it must be calculated after
        grouping due to pen input args and cannot be used individually on an animal. The estimated energy requirements
         for activity in megacalories per day are calculated following either NRC or NASEM guidelines

        Parameters
        ----------
        body_weight : float
            Body weight (kg)
        housing : str
            Housing type (Barn or Grazing)
        distance : float
            Distance walked in meters.

        Returns
        -------
        net_energy_activity : float
            Net energy requirement for activity (mcal/day)

        Notes
        -----
        Note that both NRC and NASEM calculations use distance walked in kilometers,
            hence the unit conversion in the code itself.

        Activity requirement (net_energy_activity) is proportional to body weight and daily walking distance.
        Grazing system and hilly topography will cost additional energy.
            Grazing is not implemented yet in the current version of code.

        References
        ----------
        .. [1] The National Academies of Sciences, Engineering, and Medicine "Nutrient Requirements of Dairy Cattle,
            8th edition."
            National Academic Press, Chapter 3 "Energy", pp. 30-31, 2021.

        """
        distance_km = distance * GeneralConstants.M_TO_KM
        nutrient_standard = Animal.config["nutrient_standard"]
        if nutrient_standard == "NRC":
            # Activity requirements
            # ---------------------
            # [A.Cow.A.4]-[A.Heifer.A.5]
            # Net energy for activity requirement caused by grazing system (Mcal)
            if housing == "Grazing":
                net_energy_activity1: float = 0.0012 * body_weight
            else:
                net_energy_activity1 = 0.0
            # [A.Cow.A.6]-[A.Heifer.A.7]
            # Total net energy for activity requirement (Mcal)
            net_energy_activity: float = distance_km * 0.00045 * body_weight + net_energy_activity1
            return net_energy_activity
        elif nutrient_standard == "NASEM":
            if housing == "Barn":
                net_energy_activity = distance_km * 0.00035 * body_weight
            elif housing == "Grazing":
                nonpasturekgDMI: float = 1.0
                net_energy_activity = distance_km * body_weight * 0.75 * (600 - 12 * nonpasturekgDMI) / 600

            else:
                net_energy_activity = 0.0
            return net_energy_activity
        else:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.energy_activity_rqmts.__name__,
            }
            om.add_error(
                "Unavailable nutrient standard.",
                f"The nutrient standard '{nutrient_standard}' does not exist.",
                info_map,
            )
            raise ValueError("Unavailable nutrient standard.")
