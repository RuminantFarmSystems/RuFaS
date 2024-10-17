from typing import Any, Optional

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.purchased_feed_emissions_estimator import PurchasedFeedEmissionsEstimator

om = OutputManager()


class HerdManager:
    def __init__(
        self,
        data: Dict[str, Any],
        feed: Feed,
        weather: Weather,
        time: Time,
        feed_emissions_estimator: PurchasedFeedEmissionsEstimator = None,
    ) -> None:
        """
        Initializes the pens and animals in the simulation with data from the
        JSON file by calling init_pens() and init_animals(). Creates instance
        of LifeCycleManager class and sets up the animal environment.

        Parameters
        ----------
        data : Dict[str, Any]
            dictionary with animal information from the input JSON file
        feed : Feed
            instance of the Feed class
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class
        feed_emissions_estimator : PurchasedFeedEmissionsEstimator, default=None
            Instance of the PurchasedFeedEmissionsEstimator class.

        """
        self.im = InputManager()
        config_data: dict[str, Any] = self.im.get_data("config")
        AnimalConfig.initialize_animal_config()

        # how do we set lactation curve
        AnimalBase.setup_lactation_curve_parameters(time)

        # if False, there are no animals being simulated on the farm
        self.simulate_animals = config_data.get("simulate_animals", True)

        # list of all the animals in the simulation
        self.calves: list[Animal] = []
        self.heiferIs: list[Animal] = []
        self.heiferIIs: list[Animal] = []
        self.heiferIIIs: list[Animal] = []
        self.cows: list[Animal] = []
        self.heifers_sold: list[Animal] = []
        self.cows_culled: list[Animal] = []

        # list of all the pens on the farm
        self.all_pens: list[Pen] = []

        # dictionary: key is animal ID, value is the pen ID that animal is in
        self.animal_to_pen_id_map = {}

        # alternative option: AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW
        self.set_animal_grouping_scenario(AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW)

        # dictionary for keeping track of what animal types each pen is holding
        # (value of the dictionaries are lists of pen objects)
        self.pens_by_animal_combination = {
            AnimalCombination.CALF: [],
            AnimalCombination.GROWING: [],
            AnimalCombination.CLOSE_UP: [],
            AnimalCombination.GROWING_AND_CLOSE_UP: [],
            AnimalCombination.LAC_COW: [],
        }

        # these variables are the P concentrations of each class of animal. They
        # are calculated daily and are used when an animal is added to the
        # herd, whether by birth or replacement herd purchase. They are calculated
        # in _update_phosphorus_concentrations() and are calculated by dividing the total P in the animals
        # of the class by the total body weight of the animals, on a per-animal basis
        self.p_conc = {"calf": 0, "heiferI": 0, "heiferII": 0, "heiferIII": 0, "cow": 0}

        self.phosphorus_concentration_by_animal_class = {
            animal_type: 0.0 for animal_type in [Calf, HeiferI, HeiferII, HeiferIII, Cow]
        }

        self.housing = data["housing"]
        self.pasture_concentrate = data["pasture_concentrate"]

        udrm = udr.UserDefinedRationManager()
        self.ration_user_input = data["ration"]["user_input"]
        udrm.use_user_defined_ration = self.ration_user_input

        # how often a ration is calculated, days
        self.formulation_interval = data["ration"]["formulation_interval"]

        self.init_pens(data["pen_information"], data["manure_management_scenarios"])

        if self.simulate_animals:
            self.init_animals(data["herd_information"])

            self.init_nutrient_rqmts(weather, time, feed)

            self.allocate_animals_to_pens()

        self._print_animal_num_warnings(data["herd_information"])

        self.feeds_emissions_estimator: Optional[PurchasedFeedEmissionsEstimator] = (
            feed_emissions_estimator or PurchasedFeedEmissionsEstimator()
        )
