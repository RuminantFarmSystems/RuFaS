import numpy
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

from RUFAS.classes import Config, Feed, Weather, Time
from RUFAS.routines.animal.animal_management import AnimalManagement

class ExampleAnimalSA:
    def __init__(self):
        self.animal_management_json = None
        self.main_input_dict = None
        self.animal_path = None
        self.config_dict = None
        self.feed_path = None
        self.manure_management_path = None
        self.weather_path = None
        self.config_instance = None
        self.feed_instance = None
        self.weather_instance = None
        self.time_instance = None
        self.animal_management_dict = None
        self.animal_management_instance = None

    @staticmethod
    def objective_function(feed_dry_matter: float, feed_carbon: float, feed_phosphorus: float,
                           feed_nitrogen: float, feed_detergent_fiber: float,
                           animal_management_json: str = "input/animal_management.json",
                           animal_dir: str = "input/animal", feed_dir: str = "input/feed",
                           manure_dir: str = "input/manure",
                           ) -> Tuple[float | Any, float | Any]:

        # Setup a new instance of this class
        example_class = ExampleAnimalSA()
        example_class._setup_path_references(animal_management_json, animal_dir, feed_dir, manure_dir)
        example_class._setup_default_objects()

        # alter relevant values (these are just examples)
        example_class.feed_instance.DM = feed_dry_matter
        example_class.feed_instance.C = feed_carbon
        example_class.feed_instance.P = feed_phosphorus
        example_class.feed_instance.N = feed_nitrogen
        example_class.feed_instance.NDF = feed_detergent_fiber

        # initialize the class of interest, with altered configurations
        example_class.animal_management_instance = AnimalManagement(
            example_class.animal_management_dict, example_class.config_instance, example_class.feed_instance,
            example_class.weather_instance, example_class.time_instance
        )

        # run the method of interest
        example_class.animal_management_instance.daily_updates(
            example_class.feed_instance, example_class.weather_instance, example_class.time_instance
        )

        # collect and return the output values of interest
        number_of_pens = len(example_class.animal_management_instance.all_pens)
        total_phosphorus_requirements = sum(
            [pen.avg_p_req for pen in example_class.animal_management_instance.all_pens]
        )
        total_manure_mass = sum(
            [pen.manure["manure_mass"] for pen in example_class.animal_management_instance.all_pens]
        )
        mean_pen_phosphorus_requirements = total_phosphorus_requirements / number_of_pens
        mean_pen_manure_mass = total_manure_mass / number_of_pens

        return mean_pen_phosphorus_requirements, mean_pen_manure_mass

    @staticmethod
    def vectorized_objective_function(X: numpy.array,
                                      animal_management_json: str = "input/animal_management.json",
                                      animal_dir: str = "input/animal", feed_dir: str = "input/feed",
                                      manure_dir: str = "input/manure") -> numpy.array:
        rows, cols = X.shape
        n_outputs = 2  # length of output from objective_function()

        results = numpy.empty((rows, n_outputs))
        for i in range(rows):  # This loop is probably slowing things down - need faster way to vectorize
            dry_matter, carbon, phosphorus, nitrogen, fiber = X[i, :]
            results[i, ] = ExampleAnimalSA.objective_function(dry_matter, carbon, phosphorus, nitrogen, fiber,
                                                              animal_management_json=animal_management_json,
                                                              animal_dir=animal_dir, manure_dir=manure_dir)

        return results

    @staticmethod
    def make_data_dict_from_json(path: str) -> Dict:
        in_file = Path(path)
        with in_file.open("r") as f:
            data_dict = json.load(f)
            return data_dict

    def _setup_path_references(self, animal_management_json: str = "input/animal_management.json",
                               animal_dir: str = "input/animal", feed_dir: str = "input/feed",
                               manure_dir: str = "input/manure"):
        self.animal_management_json = animal_management_json
        self.main_input_dict = self.make_data_dict_from_json(self.animal_management_json)
        self.animal_path = animal_dir + "/" + self.main_input_dict["farm"]["animal"]
        self.config_dict = self.main_input_dict["config"]
        self.feed_path = feed_dir + "/" + self.main_input_dict["farm"]["feed"]
        self.manure_management_path = manure_dir + "/" + self.main_input_dict["farm"]["manure"]
        self.weather_path = self.main_input_dict["weather"]

    def _setup_default_objects(self):
        self.config_instance = Config(self.config_dict, self.weather_path)
        self.feed_instance = Feed(self.make_data_dict_from_json(self.feed_path))
        self.weather_instance = Weather(self.weather_path, self.config_instance)
        self.time_instance = Time(self.config_instance)

        self.animal_management_dict = self.make_data_dict_from_json(self.animal_path)  # this will get altered
        self.animal_management_dict["manure_management_scenarios"] = self.make_data_dict_from_json(
            self.manure_management_path)["manure_management_scenarios"]


if __name__ == '__main__':
    import time
    from model_evaluation.sensitivity_analysis.generalized_sensitivity import SensitivityAnalysis

    # example of objective function evaluation
    print(ExampleAnimalSA.objective_function(feed_dry_matter=100, feed_carbon=0.8, feed_phosphorus=0.012,
                                             feed_nitrogen=0.11, feed_detergent_fiber=0.001))
    # example of vectorized objective function
    input_matrix = numpy.array([[100, 0.8, 0.12, 0.11, 0.001],
                                [110, 0.8, 0.12, 0.11, 0.001],  # increase dry matter
                                [100, 0.7, 0.12, 0.11, 0.001],  # decrease carbon
                                [100, 0.7, 0.10, 0.08, 0.002]]) # multiple changes
    outs = ExampleAnimalSA.vectorized_objective_function(input_matrix)
    print(outs)

    # run SA
    par_names = ["feed_dry_matter", "feed_carbon", "feed_phosphorus", "feed_nitrogen", "feed_detergent_fiber"]
    par_bounds = [(0, 10000), (0, 1), (0, 1), (0, 1), (0, 1)]
    output_names = ["phosphorus_requirements", "manure_requirements"]
    SA = SensitivityAnalysis(fun=ExampleAnimalSA.vectorized_objective_function,
                             pars=par_names, bounds=par_bounds, outputs=output_names, sample_n=2**7,
                             n_cores=8, method="fast",
                             animal_management_json="input/animal_management.json",
                             animal_dir="input/animal", feed_dir="input/feed", manure_dir="input/manure")
    # SA.sample_parameter_space()
    # from SALib.sample import fast_sampler
    # SA.problem.sample(func=fast_sampler.sample, N=SA.sample_n)
    # SA.problem.evaluate(SA.objective_function, nprocs=4)
    # SA.problem.evaluate(SA.objective_function, *SA.additional_args, nprocs=4, **SA.additional_kwargs)

    start_time = time.time()
    SA.perform_sensitivity_analysis()
    end_time = time.time()
    print(f"elapsed time for {SA.problem.samples.shape[0]} samples: {end_time - start_time} seconds")
    print(SA.problem.analysis["ST"])
