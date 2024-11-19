from RUFAS.biophysical.animal.animal import Animal
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.pen_statistics import PenStatistics
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.enums import AnimalCombination


class Pen:
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
        self.pen_statistics = PenStatistics()
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

        self.animals_in_pen = {}
        self.animal_types_in_pen = set()

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
        self.ration_nutrient_concentration = {
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
        self.MEdiet = 0.0

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

    @property
    def needs_ration_formulation(self) -> bool:
        """
        Returns whether pen needs a ration formulated.

        This is currently written to cover the case in which a ration was not formulated due to the pen being empty,
         but was populated in subsequent days.

        Returns
        -------
        bool
            True if pen needs ration formulation.
        """
        return not self.ration and self.is_populated

    @property
    def animal_types_in_pen(self) -> set[AnimalType]:
        animal_types = set([animal.type for animal in self.animals_in_pen.values()])
        return animal_types

    @property
    def number_of_lactating_cows_in_pen(self) -> int:
        return len([animal for animal in self.animals_in_pen.values() if animal.animal_type == AnimalType.LAC_COW])

    def remove_animals_by_ids(self, animal_ids: list[int]) -> None:
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

    def update_animals(self, new_animals: list[Animal], animal_combination: AnimalCombination) -> None:
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
        # self.update_classes_in_pen()

    def add_new_animals(self, new_animals: list[Animal]) -> None:
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

    def calculate_daily_walking_dist(self) -> None:
        """
        Sets the daily walking distance for the cows in the pen (if any).
        """
        animal_types_in_pen = self.animal_types_in_pen
        if AnimalType.LAC_COW in animal_types_in_pen or AnimalType.DRY_COW in animal_types_in_pen:
            for animal in list(self.animals_in_pen.values()):
                if animal.animal_type.is_cow:
                    animal.calculate_daily_walking_dist(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    @property
    def average_growth(self) -> float:
        if not self.is_populated:
            return 0
        total_growth = sum([animal.growth.daily_growth for animal in self.animals_in_pen.values()])
        return total_growth / len(self.animals_in_pen)

    @property
    def total_manure_excretion(self) -> AnimalManureExcretions:
        total_manure_excretion = AnimalManureExcretions(
            urea=0.0,
            urine=0.0,
            manure_total_ammoniacal_nitrogen=0.0,
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
        for animal in self.animals_in_pen.values():
            animal_manure = animal.digestive_system.manure_excretion
            for (key, value) in animal_manure.items():
                total_manure_excretion[key] += value
        return total_manure_excretion

    def get_manure_data(self) -> PenManureData:
        """Packages manure data from this pen."""
        return PenManureData(
            id=self.id,
            num_animals=len(self.animals_in_pen),
            classes_in_pen=self.animal_types_in_pen,
            animal_combination=self.animal_combination,
            housing_type=self.housing_type,
            pen_type=self.pen_type,
            bedding_type=self.bedding_type,
            manure_handler=self.manure_handling,
            manure_separator=self.manure_separator,
            manure_separator_after_digestion=self.manure_separator_after_digestion,
            manure_treatment=self.manure_storage,
            manure=self.total_manure_excretion,
            num_lactating_cows=self.number_of_lactating_cows_in_pen,
            num_stalls=self.num_stalls,
        )