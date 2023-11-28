import numpy
import json
from pathlib import Path
from typing import Dict, Tuple, Any

from RUFAS.config import Config
from RUFAS.routines.feed import Feed
from RUFAS.weather import Weather
from RUFAS.time import Time
from RUFAS.routines.animal.animal_manager import AnimalManager

"""
This module is an example of how to apply the SensitivityAnalysis module (generalized_sensitivity.py) to RuFas
components.

Here are the basic steps needed to apply SA:
1) First, decide which component(s) of the model on which you would like to conduct SA. For this example, I chose to
evaluate the effects of feed composition on phosphorus requirements and manure production (for a given set of animals)
over the course of a single day. Within RuFaS, `AnimalManager.daily_updates()` simulates the animals over the course
of a day, so this will be the basis for our objective function.
2) Then, ensure that the method of interest can be called from an objective function that meets the requirements of the
SAlib.
    * These requirements are that the function must take a :math:`N \\times P` numpy array `X` as its first argument and
    must return a :math`N \\times K` numpy array as output. Here, :math:`P` is the number of input parameters, :math:`K`
    is the number of responses, and :math:`N` is the number of samples. The model will be run :math:`N` times, once for
    each row of `X`.
    * In this example, an objective function was created by wrapping `AnimalManager.daily_updates()` (and its setup
    methods) into a function (`@staticmethod`) that accepts the parameters of interest as arguments (as floats) and
    returns the outputs of interest (as a tuple). The objective function is then 'vectorized' into the desired format.
3) Then we pass our objective function to the `SensitivityAnalysis` module to perform SA.

The features of this example are contained within a class for simplicity, but the same principles could be implemented
in basic (functional) scripts. To view the example in practice, execute this program from the root MASM directory:

```
python Example-animal_management_SA.wrapper.py
```

Note that the specific structure of this module (and any for conducting SA) was largely determined by how the source
`AnimalManager` module is written. If modules had a more consistent structure (in the future), it would be much
easier to apply SA universally. For now, though, users will need to design their own objective functions based on how
their module functions is designed. It should also be noted that objective functions of the form in this module are
perfectly suited for both model validation and mathematical optimization, in addition to SA. This means that writing
such objective functions will be broadly useful beyond SA.
"""


class ExampleAnimalSA:
    """Object for running an example SA on the AnimalManagement module

    Attributes
    ----------
    animal_management_json : str
        path to a default animal management input json file
    main_input_dict : dict
        a dictionary object containing data parsed from `animal_management.json`
    animal_path : str
        path to a default animal input json file
    config_dict : dict
        a dictionary object created from the "config" subset of `main_input_dict`
    feed_path : str
        path to the feed input json file
    manure_management_path : str
        path to the manure management input json file
    weather_path : str
        path to the weather csv file
    config_instance : Config
        an instance of the Config class
    feed_instance : Feed
        an instance of the Feed class
    weather_instance : Weather
        an instance of the Weather class
    time_instance : Time
        an instance of the Time class
    animal_management_dict : dict
        a dictionary containing the full animal management data necessary to create an AnimalManagement instance
    animal_management_instance : AnimalManager
        an instance of the AnimalManagement class; the main object containing the method of interest.
    """
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
        """The non-vectorized objective function for this example.

        This function calculates the average phosphorus requirements and manure production for a pen of animals, based
        on the composition of the feed.

        # TODO: @JoeWaddell, would you please double check my descriptions/units for the parameters and return values:
        Parameters
        ----------
        feed_dry_matter : float
            The dry matter content of the feed (kg)
        feed_carbon : float
            Carbon available in the feed (fraction of total)
        feed_phosphorus : float
            Phosphorus available in the feed (fraction of total)
        feed_nitrogen : float
            Nitrogen available in the feed (fraction of total)
        feed_detergent_fiber : float
            Neutral detergent fiber present in the feed (fraction of total)
        animal_management_json : str
            path to a default animal management input json file
        animal_dir : str
            directory in which to search for the animal json file
        feed_dir : str
            directory in which to search for the feed json file
        manure_dir : str
            directory in which to search for the manure json file

        Returns
        -------
        results : tuple
            phosphorus_requirements : float
                average per-pen phosphorus requirements for the day
            manure_production : float
                average per-pen manure produced during the day

        Notes
        -----
        The `feed_[x]` parameters are those on which we wish to conduct SA. The other arguments should remain constant
        throughout the SA and, therefore, will not be included in `X` (see `vectorized_objective_function()`).

        This function works by first creating default objects (from input files) and then modifying those
        objects based on the parameter values.
        """

        # Set up a new instance of this class
        example_class = ExampleAnimalSA()
        example_class._perform_initial_setup(animal_management_json, animal_dir, feed_dir, manure_dir)
        example_class._setup_main_object()

        # alter relevant values (these are just examples)
        example_class.feed_instance.DM = feed_dry_matter
        example_class.feed_instance.C = feed_carbon
        example_class.feed_instance.P = feed_phosphorus
        example_class.feed_instance.N = feed_nitrogen
        example_class.feed_instance.NDF = feed_detergent_fiber

        # initialize the class of interest, with altered configurations
        example_class.animal_management_instance = AnimalManager(
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
        """Vectorized wrapper for `objective_function()`

        Parameters
        ----------
        X : numpy.array
            An :math:`N \\times P` matrix of input values over which the `objective_function()` should be applied.
            Columns correspond to `feed_dry_matter`, `feed_carbon`, `feed_phosphorus`, `feed_nitrogen`, and
            `feed_detergent_fiber`, respectively.
        animal_management_json : str
            path to a default animal management input json file
        animal_dir : str
            directory in which to search for the animal json file
        feed_dir : str
            directory in which to search for the feed json file
        manure_dir : str
            directory in which to search for the manure json file

        Returns
        -------
        Y : numpy.array
            an :math:`N \\times 2` matrix of response values. Columns correspond to `phosphorus_requirements` and `
            manure_production`,
            respectively. Rows correspond to rows of `X`: the evaluation of X[i, ] corresponds to Y[i, ]
        """

        rows, cols = X.shape
        n_outputs = 2  # length of output from objective_function()

        results = numpy.empty((rows, n_outputs))
        for i in range(rows):  # This loop is probably slowing things down - need faster way to vectorize
            dry_matter, carbon, phosphorus, nitrogen, fiber = X[i, :]
            results[i, ] = ExampleAnimalSA.objective_function(dry_matter, carbon, phosphorus, nitrogen, fiber,
                                                              animal_management_json=animal_management_json,
                                                              animal_dir=animal_dir, manure_dir=manure_dir,
                                                              feed_dir=feed_dir)

        return results

    @staticmethod
    def make_data_dict_from_json(path: str) -> Dict:
        """helper function to convert a json file into a python dictionary

        Parameters
        ----------
        path : str
            path to the json file
        """
        in_file = Path(path)
        with in_file.open("r") as f:
            data_dict = json.load(f)
            return data_dict

    def _perform_initial_setup(self, animal_management_json: str = "input/animal_management.json",
                               animal_dir: str = "input/animal", feed_dir: str = "input/feed",
                               manure_dir: str = "input/manure"):
        """Executes the first setup steps; converts input files into dictionaries

        Parameters
        ----------
        animal_management_json : str
            path to a default animal management input json file
        animal_dir : str
            directory in which to search for the animal json file
        feed_dir : str
            directory in which to search for the feed json file
        manure_dir : str
            directory in which to search for the manure json file
        """
        self.animal_management_json = animal_management_json
        self.main_input_dict = self.make_data_dict_from_json(self.animal_management_json)
        self.animal_path = animal_dir + "/" + self.main_input_dict["farm"]["animal"]
        self.config_dict = self.main_input_dict["config"]
        self.feed_path = feed_dir + "/" + self.main_input_dict["farm"]["feed"]
        self.manure_management_path = manure_dir + "/" + self.main_input_dict["farm"]["manure"]
        self.weather_path = self.main_input_dict["weather"]

    def _setup_main_object(self):
        """Creates an instance the main AnimalManager class, after creating instances of the objects needed to
        initialize this class"""
        self.config_instance = Config(self.config_dict)
        self.feed_instance = Feed(self.make_data_dict_from_json(self.feed_path))
        self.weather_instance = Weather(self.weather_path, self.config_instance)
        self.time_instance = Time(self.config_instance)

        self.animal_management_dict = self.make_data_dict_from_json(self.animal_path)  # this will get altered
        self.animal_management_dict["manure_management_scenarios"] = self.make_data_dict_from_json(
            self.manure_management_path)["manure_management_scenarios"]


# --- Example in Practice ----
if __name__ == '__main__':
    import time
    from model_evaluation.sensitivity_analysis.generalized_sensitivity import SensitivityAnalysis

    # TODO: @JoeWaddell, I totally guessed on the values and ranges for these parameters.
    # example of objective function evaluation
    print(ExampleAnimalSA.objective_function(feed_dry_matter=100, feed_carbon=0.8, feed_phosphorus=0.012,
                                             feed_nitrogen=0.11, feed_detergent_fiber=0.001))
    # example of vectorized objective function evaluation
    input_matrix = numpy.array([[100, 0.8, 0.12, 0.11, 0.001],
                                [110, 0.8, 0.12, 0.11, 0.001],  # increase dry matter
                                [100, 0.7, 0.12, 0.11, 0.001],  # decrease carbon
                                [100, 0.7, 0.10, 0.08, 0.002]])  # multiple changes
    outs = ExampleAnimalSA.vectorized_objective_function(input_matrix)
    print(outs)

    # run SA
    par_names = ["feed_dry_matter", "feed_carbon", "feed_phosphorus", "feed_nitrogen", "feed_detergent_fiber"]
    par_bounds = [(0, 10000), (0, 1), (0, 1), (0, 1), (0, 1)]
    output_names = ["phosphorus_requirements", "manure_production"]
    SA = SensitivityAnalysis(fun=ExampleAnimalSA.vectorized_objective_function,
                             pars=par_names, bounds=par_bounds, outputs=output_names, sample_n=2**7,
                             n_cores=2, method="fast",
                             animal_management_json="input/animal_management.json",
                             animal_dir="input/animal", feed_dir="input/feed", manure_dir="input/manure")

    # results
    start_time = time.time()
    print("performing SA (expect benign warnings about parallelization) ...")
    SA.perform_sensitivity_analysis()  # note, verify CPU usage in Task Manager or Resource Monitor
    end_time = time.time()
    print(f"elapsed time for {SA.problem.samples.shape[0]} samples: {end_time - start_time} seconds")
    # Note: For the run on my work PC, using 2 cores, this took 1.36 seconds per sample (rows of `SA.problem.samples`)

    # Total effects of each parameter
    print(SA.problem.analysis["phosphorus_requirements"]["ST"])
    print(SA.problem.analysis["manure_production"]["ST"])

    # # ---- compare numpy.vectorize and our looped version in terms of speed
    # # our function
    # start = time.time()
    # ExampleAnimalSA.vectorized_objective_function(input_matrix)
    # end = time.time()
    # print(end - start) # approx. 7.5 seconds avg.
    #
    # # numpy vectorized function: MUCH slower
    # vfun = numpy.vectorize(ExampleAnimalSA.objective_function)
    # start = time.time()
    # dm, carb, phos, nitro, fiber = input_matrix.T
    # vfun(dm, carb, phos, nitro, fiber)
    # end = time.time()
    # print(end - start) # approx. 10 seconds avg.
