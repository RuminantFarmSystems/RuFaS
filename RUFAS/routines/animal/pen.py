from __future__ import annotations

import copy
from typing import List, Dict, Union, Any, Tuple

from RUFAS.units import MeasurementUnits
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.manure.general_manure import (
    AnimalManureExcretions,
    add_animal_manure_excretions,
    get_default_animal_manure_excretions,
)
from RUFAS.routines.animal.ration.animal_requirements import AnimalRequirements
from ...shared_structures.animal_combinations import AnimalCombination
from ...shared_structures.pen_manure_data import PenManureData

om = OutputManager()

req = AnimalRequirements()


class Pen:
    """
    Manages a pen's operation. Stores the characteristics of the pen and the
    animals that are housed in it any point in the simulation. This class also
    keeps track of some key characteristics of the average animal in the pen.

    Attributes
    -------------
    pen_id : int
        The pen's unique pen ID.
        Obtained from the input file.

    vertical_dist_to_milking_parlor : float
        The vertical distance to milking parlor, measured in kilometers.
        Obtained from the input file.

    horizontal_dist_to_milking_parlor : float
        The horizontal distance to milking parlor, measured in kilometers.
        Obtained from the input file.

    number_of_stalls : int
        The number of stalls.
        Obtained from the input file.

    housing_type : string
        The housing type of the pen.
        Obtained from the input file.

    bedding_type : string
        The bedding type of the pen.
        Obtained from the input file.

    pen_type : string
        The pen type (freestall or tiestall).
        Obtained from the input file.

    manure_handling : string
        The manure handling method used to clean the pen.

    manure_separator : string
        The type of manure separator that processes manure excreted in the pen.

    manure_separator_after_digestion : string
        The type of manure separator that processes manure from the pen after it's been in a digestor.

    manure_storage : string
        The type of manure storage receptacle that stores manure excreted in the pen.

    avg_p_intake : float
        The average phosphorus intake of the animals in the pen.

    avg_p_req : float
        The average phosphorus requirements of the animals in the pen.

    avg_p_animal : float
        The average phosphorus content/mass of the animals in the pen.

    animals_in_pen : dictionary
        A dictionary of all animals in this pen that maps animal id to animal object.

    classes_in_pen : set
        The set (no repeats) of all the classes to which the animals in the pen belong.

    avg_DBW : float
        The average daily change in (delta) body weight of the animals in the pen.
        Used for ration formulation.

    avg_BW : float
        The average body weight of the animals in the pen.
        Used for ration formulation.

    avg_DMIest : float
        The average dry matter intake estimation of the animals in the pen.
        Used for ration formulation

    avg_nutrient_rqmts : dict
        Contains the average nutrient requirements of the animals in the pen.
        Used for ration formulation

    avg_milk : float
        The average milk production of the animals in the pen.
        Used for (lactating cow) ration formulation

    avg_CP_milk : float
        The average milk crude protein content of the animals in the pen.
        Used for (lactating cow) ration formulation

    ration : dict
        Contains the ration for all the animals in the pen.

    ration_nutrient_amount : dict
        Contains the total amount of different nutrients in the current ration.

    ration_nutrient_conc : dict
        Contains the concentration of different nutrients in the current ration.

    dry_matter_intake : float
        The dry matter intake value of the animals in the pen.

    avg_growth : float
        The average growth of the animals in the pen.

    MEdiet : float
        The metabolizable energy concentration of the diet fed to the pen.

    _manure_dict_template : dict
        The dictionary template for the manure attributes (manure, calf_total, etc)

    manure : dict
        Contains the total manure excretion of all animals in the pen.

    calf_total : dict
        Contains the total manure excretion of the calves in the pen.

    heifer_total : dict
        Contains the total manure excretion of the heifers in the pen.

    dry_total : dict
        Contains the total manure excretion of the dry cows in the pen.

    lactating_total : dict
        Contains the total manure excretion of the lactating cows in the pen.

    animal_combination : AnimalCombination
        Represents the valid animal type combinations in the pen.
    """

    def __init__(
        self,
        pen_id: int,
        pen_name: str,
        vertical_dist_to_milking_parlor: float,
        horizontal_dist_to_milking_parlor: float,
        number_of_stalls: int,
        housing_type: str,
        bedding_type: str,
        pen_type: str,
        manure_handling: str,
        manure_separator: str,
        manure_separator_after_digestion: str,
        manure_storage: str,
        animal_combination: AnimalCombination,
        max_stocking_density: float,
    ) -> None:
        """
        Initializes a pen with the given arguments.

        Parameters
        ----------
            pen_id : int
                the unique id number of the pen
            vertical_dist_to_milking_parlor : float
                vertical distance to milking parlor, km
            horizontal_dist_to_milking_parlor: float
                horizontal distance to milking parlor, km
            number_of_stalls : int
                number of stalls in the pen
            housing_type : str
                housing type of the pen
            bedding_type : str
                bedding type of the pen
            pen_type : str
                freestall or tiestall
            manure_handling : str
                the manure handling method used to clean the pen
            manure_separator : str
                the manure separator that processes manure excreted in this pen
            manure_separator_after_digestion : str
                the second manure separator that processes manure excreted in this pen post-digestor
            manure_storage : str
                the manure storage receptacle that stores manure excreted in this pen
            animal_combination : AnimalCombination
                the valid animal combinations inside this pen, an instance of the AnimalCombination Enum
            max_stocking_density : float
                maximum stocking density allowed for pen
        """
        self.id = pen_id

        self.max_stocking_density = max_stocking_density

        self.vertical_dist_to_parlor = vertical_dist_to_milking_parlor
        self.horizontal_dist_to_parlor = horizontal_dist_to_milking_parlor
        self.num_stalls = number_of_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type
        self.pen_name = pen_name

        self.manure_handling = manure_handling
        self.manure_separator = manure_separator
        self.manure_separator_after_digestion = manure_separator_after_digestion
        self.manure_storage = manure_storage
        self.avg_p_intake = 0.0
        self.avg_p_req = 0.0
        self.avg_p_animal = 0.0

        self.animals_in_pen = {}

        self.classes_in_pen = set()

        self.avg_BW = 0.0
        self.avg_DMIest = 0.0
        self.avg_DBW = 0.0

        self.avg_nutrient_rqmts = {}
        self.avg_milk = 0.0
        self.avg_CP_milk = 0.0

        self.ration = {}
        self.ration_per_animal = {}
        self.ration_nutrient_amount = {
            "dm": 0.0,
            "CP": 0.0,
            "ADF": 0.0,
            "NDF": 0.0,
            "lignin": 0.0,
            "ash": 0.0,
            "phosphorus": 0.0,
            "potassium": 0.0,
            "N": 0.0,
        }
        self.ration_nutrient_conc = {
            "dm": 0.0,
            "CP": 0.0,
            "ADF": 0.0,
            "NDF": 0.0,
            "lignin": 0.0,
            "ash": 0.0,
            "phosphorus": 0.0,
            "potassium": 0.0,
            "N": 0.0,
        }
        self.dry_matter_intake = 0.0

        self.avg_growth = 0.0

        self.MEdiet = 0.0
        self.avg_milk_production_reduction = 0.0

        # template for manure, calf_total, etc.
        self._manure_dict_template = AnimalManureExcretions(
            urea=0.0,
            urine=0.0,
            total_ammoniacal_nitrogen_concentration=0.0,
            urine_nitrogen=0.0,
            manure_nitrogen=0.0,
            manure_mass=0.0,
            total_solids=0.0,
            degradable_volatile_solids=0.0,
            non_degradable_volatile_solids=0.0,
            inorganic_phosphorus_fraction=0.0,
            organic_phosphorus_fraction=0.0,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=0.0,
            phosphorus_fraction=0.0,
            potassium=0.0,
            enteric_methane_g=0.0,
        )

        # manure attributes are initialized in the reset_manure method
        self.manure = None
        self.calf_total = None
        self.heifer_total = None
        self.dry_total = None
        self.lactating_total = None

        self.reset_manure()

        # set of all the ids for the feeds allocated for this pen object
        self.allocated_feeds = set()

        # the animal_combinations in this pen, utilizes the AnimalCombination Enum
        self.animal_combination = animal_combination

    @property
    def current_stocking_density(self) -> float:
        """
        Returns the current stocking density of the pen.

        Returns
        -------
        float
            the current stocking density of the pen.

        """

        return len(self.animals_in_pen) / self.num_stalls

    @property
    def is_populated(self) -> bool:
        """
        Returns whether the pen is populated.

        Returns
        -------
        bool
            True if the pen is populated, False otherwise.

        """
        return len(self.animals_in_pen) > 0

    def set_avg_nutrient_rqmts(self, avg_nutrient_rqmts: Dict[str, float]) -> None:
        """
        Sets the pen's average nutrient requirements

        Parameters
        ----------
        avg_nutrient_rqmts: Dict[str, float]
            The new average nutrient requirements
        """
        self.avg_nutrient_rqmts = {key: value for (key, value) in avg_nutrient_rqmts.items()}

    def set_milk_avgs(self, avg_milk: float, avg_CP_milk: float, avg_milk_production_reduction: float) -> None:
        """
        Sets the pen's average milk and average CP milk.

        Parameters
        ----------
        avg_milk: float
            The new average nutrient requirements
        avg_CP_milk: float
            The new average CP milk
        """
        self.avg_milk = avg_milk
        self.avg_CP_milk = avg_CP_milk
        self.avg_milk_production_reduction = avg_milk_production_reduction

    def add_new_animals(self, new_animals: List[Union[Calf, Cow, HeiferI, HeiferII, HeiferIII]]) -> None:
        """
        Adds all animals in new_animals to the pen.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen

        """
        for animal in new_animals:
            self.animals_in_pen[animal.id] = animal

    def update_animal_combination(self, animal_combination: AnimalCombination) -> None:
        """
        Sets the pen's animal combination to animal_combination

        Parameters
        ----------
        animal_combination: AnimalCombination
            the new AnimalCombination
        """
        self.animal_combination = animal_combination

    # TODO: Remove this functionality once pen has been fully switched to AnimalCombination enum GitHub Issue #1208
    def update_classes_in_pen(self) -> None:
        """
        Updates the classes contained within the pen
        """
        self.classes_in_pen = set()
        for animal in list(self.animals_in_pen.values()):
            life_cycle_stage = type(animal).__name__
            self.classes_in_pen.add(life_cycle_stage)

    def update_animals(self, new_animals: List[Any], animal_combination: AnimalCombination) -> None:
        """
        Calls functions that will add new animals to the pen and update associated attributes.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen
        animal_combination: AnimalCombination
            an AnimalCombination Enum representing the type of the new animals
        """

        self.add_new_animals(new_animals)
        self.calc_daily_walking_dist()
        self.update_animal_combination(animal_combination)
        self.update_classes_in_pen()

    def manure_sums(
        self, manure: Dict[float, int], curr_manure: AnimalManureExcretions, animal_dict: Dict[float, int]
    ) -> Tuple[Dict[float, int], Dict[float, int]]:
        """
        Accumulator helper function for calc_manure.
        The function finds sums of manure components for each
        animal in the pen and the total manure for each animal type.

        Parameters
        ----------
        manure: Dict[float, int]
            A dictionary that contains the the accumulated manure excretion values for all animals
        curr_manure: AnimalManureExcretions
            A dictionary that contains the manure excretion values used to update the manure and animal dictionaries
            in the AnimalManureExcretions class definition.
        animal_dict: Dict[float, int]
            A dictionary that contains the manure excretion values for specific animals in the pen

        Returns
        -------
        Tuple[Dict[float, int], Dict[float, int]]
            A tuple containing the updated manure dictionary and the updated animal dictionary.
        """

        for key in manure.keys():
            manure[key] += curr_manure[key]
            animal_dict[key] += curr_manure[key]
        return manure, animal_dict

    def calc_manure(self, feed, methane_model: str):  # noqa
        """
        Calculates the manure excretion of the animals in the pen.

        Parameters
        ----------
        feed: Feed
            An object of the Feed class containing information about the feed.
        methane_model : str
            Methane model used for calculations.
        """

        for animal in list(self.animals_in_pen.values()):
            if type(animal).__name__ == "Cow":
                animal.calc_manure_excretion(feed, methane_model, self.MEdiet)
            else:
                animal.calc_manure_excretion(feed, methane_model)

        manure = {}
        calf_total = {}
        heifer_total = {}
        dry_total = {}
        lactating_total = {}

        # obtain keys of manure composition calculations
        animals = list(self.animals_in_pen.values())
        first_animal_manure = animals[0].manure_excretion
        for key in first_animal_manure.keys():
            manure[key] = 0
            calf_total[key] = 0
            heifer_total[key] = 0
            dry_total[key] = 0
            lactating_total[key] = 0

        # find sums of manure components for each animal in the pen for
        # total manure in pen and total manure by animal type
        for animal in animals:
            curr_manure = animal.manure_excretion
            if type(animal) == Calf:  # noqa
                manure, calf_total = self.manure_sums(manure, curr_manure, calf_total)
            elif type(animal) in [HeiferI, HeiferII, HeiferIII]:  # noqa
                manure, heifer_total = self.manure_sums(manure, curr_manure, heifer_total)
            elif type(animal) == Cow and not animal.milking:  # noqa
                manure, dry_total = self.manure_sums(manure, curr_manure, dry_total)
            elif type(animal) == Cow and animal.milking:  # noqa
                manure, lactating_total = self.manure_sums(manure, curr_manure, lactating_total)

        self.manure = manure
        self.calf_total = calf_total
        self.heifer_total = heifer_total
        self.dry_total = dry_total
        self.lactating_total = lactating_total

    def _copy_manure_template(self):
        return copy.deepcopy(self._manure_dict_template)

    def reset_manure(self):
        self.manure = self._copy_manure_template()
        self.calf_total = self._copy_manure_template()
        self.heifer_total = self._copy_manure_template()
        self.dry_total = self._copy_manure_template()
        self.lactating_total = self._copy_manure_template()

    def calc_avg_growth(self):
        """
        Calculates the average growth of the animals in the pen.
        """

        if not self.is_populated:
            return

        total_growth = 0
        for animal in list(self.animals_in_pen.values()):
            total_growth += animal.daily_growth
        self.avg_growth = total_growth / len(self.animals_in_pen)

    # TODO: Fix this to use AnimalType enum GitHub Issue #1209
    def calc_daily_walking_dist(self):
        """
        Sets the daily walking distance for the cows in the pen (if any).
        """
        if "Cow" in self.classes_in_pen:
            for animal in list(self.animals_in_pen.values()):
                if type(animal).__name__ == "Cow":
                    animal.calc_daily_walking_dist(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    def call_p_rqmts(self):
        """
        Calls each animal's method to calculate phosphorus requirements.
        """
        # since each animal in the pen receives the same ration
        if len(self.animals_in_pen) > 0:
            DMI = self.ration_nutrient_amount["dm"]

            total_p_req = 0
            for animal in list(self.animals_in_pen.values()):
                animal.phosphorus_rqmts(DMI)
                total_p_req += animal.p_req
            self.avg_p_req = total_p_req / len(self.animals_in_pen)

    def daily_p_update(self):
        """
        Calls each animal's method to calculate daily phosphorus update.
        """
        if len(self.animals_in_pen) > 0:
            total_p_animal = 0
            for animal in list(self.animals_in_pen.values()):
                animal.daily_p_update()
                total_p_animal += animal.p_animal
            # TODO: Add warning if total_p_animal < 0 GitHub Issue #1212
            total_p_animal = max(total_p_animal, 0)
            self.avg_p_animal = total_p_animal / len(self.animals_in_pen)

    def remove_animals_by_ids(self, animal_ids: List[int]) -> None:
        """
        Removes animals from the pen by their ids.

        Notes
        -----
        Because this method takes O(n) time, it is recommended that the caller of this method
        should prepare a list of animal ids to be removed from the pen first, and then call this
        method with that list once.

        Parameters
        ----------
        animal_ids : List[int]
            List of animals that match the given ids to be removed from the pen.

        """
        if not animal_ids:
            return
        animal_ids = set(animal_ids)
        self.animals_in_pen = {
            animal_id: animal for animal_id, animal in self.animals_in_pen.items() if animal_id not in animal_ids
        }

    def clear(self):
        """
        Clears the pen attributes for re-allocation.
        """
        # All other attributes are kept the same so that if a pen becomes empty
        # and animals are to be added to it, there are previous initial values
        # that are non-zero.
        self.animals_in_pen = {}
        self.avg_p_animal = 0

    def subset_class_feeds(self, feed):
        """
        Subsets the feed_ids list to appropriately include the feeds necessary for that pen object,
        based on the animal type(s) that are currently in the pen.

        Args:
            feed: an object of the Feed class
        """

        self.allocated_feeds = feed.input_feed_combinations[self.animal_combination]

    @staticmethod
    def _get_prefix_and_default_manure_excretion(
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow, is_lactating_cow=False
    ) -> Tuple[str, AnimalManureExcretions]:
        """
        Get the prefix and default manure value for a given animal.

        Parameters
        ----------
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow
            The animal instance for which to get the prefix and manure.
        is_lactating_cow: bool, optional
            True if the animal is a lactating cow, False otherwise. Default is set to False.

        Returns
        -------
        Tuple[str, AnimalManureExcretions]
            A tuple containing the prefix and default manure value for the animal.

        Raises
        ------
        ValueError
            If prefix for animal type is not found.

        """
        animal_type_to_prefix = {
            "Calf": "daily_aggregate_calf",
            "HeiferI": "daily_aggregate_heifer",
            "HeiferII": "daily_aggregate_heifer",
            "HeiferIII": "daily_aggregate_heifer",
            "Cow": "daily_aggregate_dry_cow",
        }
        prefix = animal_type_to_prefix.get(animal.__class__.__name__, None)
        if prefix is None:
            raise ValueError(f"Unrecognized animal type: {type(animal)}")
        if is_lactating_cow:
            prefix = "daily_aggregate_lactating_cow"
        manure = get_default_animal_manure_excretions()
        return prefix, manure

    def _calc_animal_manure_excretion(
        self,
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow,
        methane_model: str,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
    ) -> Tuple[str, AnimalManureExcretions]:
        """
        Calculate the manure excretion for a given animal and return the prefix and excretions.

        Parameters
        ----------
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow
            The animal instance for which to calculate manure excretion.
        feed: Feed
            An object of the Feed class containing information about the feed.
        methane_model: str
            Methane model used for calculations.
        methane_mitigation_method: str
            Methane mitigation method used.
        methane_mitigation_additive_amount: float
            Amount of methane mitigation additive, mg/kg dry matter intake (DMI).

        Returns
        -------
        Tuple[str, AnimalManureExcretions]
            A tuple containing the prefix and calculated manure excretion for the animal.

        """
        is_cow = animal.__class__.__name__ == "Cow"
        is_lactating_cow = is_cow and animal.is_lactating
        if is_cow:
            animal.calc_manure_excretion(
                methane_model,
                methane_mitigation_method,
                methane_mitigation_additive_amount,
                self.MEdiet,
                nutrient_amount=self.ration_nutrient_amount,
                nutrient_conc=self.ration_nutrient_conc,
            )
        else:
            animal.calc_manure_excretion(
                methane_model, nutrient_amount=self.ration_nutrient_amount, nutrient_conc=self.ration_nutrient_conc
            )
        return self._get_prefix_and_default_manure_excretion(animal, is_lactating_cow)

    @staticmethod
    def _update_animal_manure_excretion_data(
        manure_excretions_output_data: dict[str, dict[str, str | AnimalManureExcretions]],
        prefix: str,
        manure: AnimalManureExcretions,
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow,
    ) -> None:
        """
        Update the manure excretion dictionaries and the `self.manure` variable.

        Parameters
        ----------
        manure_excretions_output_data: dict[str, dict[str, str | AnimalManureExcretions]]
            Dictionary mapping prefixes to animal manure data.
        prefix: str
            Prefix related to the animal type.
        manure: AnimalManureExcretions
            Manure excretions data for the animal.
        animal: Calf | HeiferI | HeiferII | HeiferIII | Cow
            The animal instance for which to update the manure excretion data.

        Returns
        -------
        None

        """
        if prefix not in manure_excretions_output_data:
            manure_excretions_output_data[prefix] = {"prefix": prefix, "manure": manure}

        manure_excretions_output_data[prefix]["manure"] = add_animal_manure_excretions(
            manure_excretions_output_data[prefix]["manure"], animal.manure_excretion
        )

    def calc_total_manure(
        self,
        methane_model: str,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
        manure_excretions_output_data: dict[str, dict[str | AnimalManureExcretions]],
    ) -> None:
        """
        Calculate the total manure excreted by all animals in the pen.

        Parameters
        ----------
        feed: Feed
            An object of the Feed class that stores the feed information managed by the farm
        methane_model: str
            Methane model used for methane emission calculations, including "Mutian", "Mills", "IPCC".
        methane_mitigation_method: str
            Methane mitigation method used to reduce enteric methane emissions, including "3-NOP", "Monensin",
            "Essential Oils", and "Seaweed".
        methane_mitigation_additive_amount: float
            The amount of methane mitigation feed additive that is added, mg/kg dry matter intake (DMI).
            The recommended dose for 3-NOP is between 40 and 100 mg/kg DMI, while that for monensin is
            between 16 and 36 mg/kg DMI.
        manure_excretions_output_data : dict[str, dict[str | AnimalManureExcretions]]
            Dictionary mapping prefixes to animal manure data.

        Returns
        -------
        None

        """
        if not self.is_populated:
            return

        self.manure = get_default_animal_manure_excretions()

        for animal in list(self.animals_in_pen.values()):
            prefix, manure = self._calc_animal_manure_excretion(
                animal,
                methane_model,
                methane_mitigation_method,
                methane_mitigation_additive_amount,
            )
            self._update_animal_manure_excretion_data(manure_excretions_output_data, prefix, manure, animal)
            self.manure = add_animal_manure_excretions(self.manure, animal.manure_excretion)

    def _set_animal_nutrient_values(
        self, animal, animal_grouping_scenario, feed, temp, phosphorus_concentration
    ) -> None:
        """
        Set the nutrient values for the animal.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            The animal to set the nutrient values for.
        animal_grouping_scenario
        feed
        temp
        phosphorus_concentration : float

        Returns
        -------
        None

        """
        animal_type = animal_grouping_scenario.get_animal_type(animal)
        if animal_type in [AnimalType.LAC_COW, AnimalType.DRY_COW]:
            req = AnimalRequirements()
            requirements = req.calc_rqmts(
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
                previous_temperature=temp,
            )
            animal.NEmaint_requirement = requirements["NEmaint_requirement"]
            animal.NEg_requirement = requirements["NEg_requirement"]
            animal.NEpreg_requirement = requirements["NEpreg_requirement"]
            animal.NEl_requirement = requirements["NEl_requirement"]
            animal.MP_requirement = requirements["MP_requirement"]
            animal.Ca_requirement = requirements["Ca_requirement"]
            animal.P_requirement = requirements["P_requirement"]
            animal.DMIest_requirement = requirements["DMIest_requirement"]
            animal.DNED_requirement = (
                requirements["NEmaint_requirement"] + requirements["NEl_requirement"]
            ) / animal.DMIest_requirement
            animal.DMPD_requirement = (requirements["MP_requirement"]) / animal.DMIest_requirement

            animal.calc_daily_walking_dist(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

        if animal_type in [AnimalType.CALF]:
            if self.avg_nutrient_rqmts:
                animal.nutrient_rqmts = self.avg_nutrient_rqmts
            else:
                animal.calc_nutrient_rqmts(feed, temp)
        elif animal_type in [
            AnimalType.HEIFER_I,
            AnimalType.HEIFER_II,
            AnimalType.HEIFER_III,
        ]:
            if self.avg_nutrient_rqmts:
                animal.nutrient_rqmts = self.avg_nutrient_rqmts
            else:
                animal.set_nutrient_rqmts(temp, animal_grouping_scenario)
        else:
            if self.avg_nutrient_rqmts:
                animal.nutrient_rqmts = self.avg_nutrient_rqmts
            else:
                animal.set_nutrient_rqmts(animal_grouping_scenario)

        if phosphorus_concentration != -1:
            animal.p_animal = animal.body_weight * phosphorus_concentration

        animal.dry_matter_intake = self.dry_matter_intake
        animal.set_ration(self.ration_per_animal, self.ration_nutrient_amount["dm"])

        # animal.p_intake = self.avg_p_intake
        animal.set_p_intake(
            self.ration_nutrient_amount["phosphorus"],
            self.ration_nutrient_conc["phosphorus"],
        )

    def _calc_new_ration(self, num_animals: int):
        """
        Calculate the new ration for the pen based on the number of animals in the pen.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        ration : Dict[str, Union[float, str]]
            The new ration for the pen.

        """

        ration = {}
        for key in self.ration_per_animal:
            if key == "status":
                ration[key] = self.ration_per_animal[key]
            else:  # feeds and price
                ration[key] = self.ration_per_animal[key] * num_animals
        return ration

    # Population-related methods
    def add_animal(
        self,
        animal,
        animal_grouping_scenario,
        feed,
        temp,
        phosphorus_concentration: float,
    ) -> None:
        """
        Add an animal to the pen and adjust the ration accordingly.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            The animal to be added to the pen.
        animal_grouping_scenario
        feed
        temp
        phosphorus_concentration : float

        Returns
        -------
        None

        """

        self._set_animal_nutrient_values(animal, animal_grouping_scenario, feed, temp, phosphorus_concentration)
        self.animals_in_pen[animal.id] = animal
        self.ration = self._calc_new_ration(len(self.animals_in_pen))

    def remove_animal(self, animal_id: int) -> None:
        """
        Remove an animal from the pen by its id and adjust the ration accordingly.

        Parameters
        ----------
        animal_id : int
            The id of the animal to be removed from the pen.

        Returns
        -------
        None

        """
        del self.animals_in_pen[animal_id]
        self.ration = self._calc_new_ration(len(self.animals_in_pen))

    def _count_lactating_cows(self) -> int:
        """Returns the count of lactating cows currently held in this pen."""
        if self.animal_combination is not AnimalCombination.LAC_COW:
            return 0
        num_lac_cows = 0
        for animal in self.animals_in_pen.values():
            if type(animal) is Cow:
                num_lac_cows += 1
        return num_lac_cows

    def get_manure_data(self) -> PenManureData:
        """Packages manure data from this pen."""
        return PenManureData(
            id=self.id,
            num_animals=len(self.animals_in_pen),
            classes_in_pen=self.classes_in_pen,
            animal_combination=self.animal_combination,
            housing_type=self.housing_type,
            pen_type=self.pen_type,
            bedding_type=self.bedding_type,
            manure_handler=self.manure_handling,
            manure_separator=self.manure_separator,
            manure_separator_after_digestion=self.manure_separator_after_digestion,
            manure_treatment=self.manure_storage,
            manure=self.manure,
            num_lactating_cows=self._count_lactating_cows(),
            num_stalls=self.num_stalls,
        )
