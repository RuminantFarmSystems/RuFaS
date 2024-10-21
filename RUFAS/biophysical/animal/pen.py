from RUFAS.biophysical.animal.data_types.pen_statistics import PenStatistics
from RUFAS.enums import AnimalCombination


class Pen:
    def __init__(self,
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
                 max_stocking_density: float) -> None:
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
        self.MEdiet = 0.0

        # set of all the ids for the feeds allocated for this pen object
        self.allocated_feeds = set()

        # the animal_combinations in this pen, utilizes the AnimalCombination Enum
        self.animal_combination = animal_combination
