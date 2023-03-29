import os

import numpy
import json
from pathlib import Path
from typing import Dict

from RUFAS.routines import daily_animal_routine
from RUFAS.classes import Config, Feed, Weather, Time
from RUFAS.routines.animal.animal_management import AnimalManagement


def make_data_dict_from_json(path: str = "../../input/animal/animal_management.json") -> Dict:
    in_file = Path(path)
    with in_file.open("r") as f:
        data_dict = json.load(f)
        return data_dict


main_input_dict = make_data_dict_from_json("input/animal_management.json")
animal_path = "input/animal/" + main_input_dict["farm"]["animal"]
config_dict = main_input_dict["config"]
feed_path = "input/feed/" + main_input_dict["farm"]["feed"]
manure_management_path = "input/manure/" + main_input_dict["farm"]["manure"]
weather_path = main_input_dict["weather"]

# --- objects needed to create AnimalManagement instance ---
# Config
config_instance = Config(config_dict, weather_path)
# Feed
feed_instance = Feed(make_data_dict_from_json(feed_path))
# Weather
weather_instance = Weather(weather_path, config_instance)
# Time
time_instance = Time(config_instance)
#

# --- create Animal Management Instance
animal_mgt_data = make_data_dict_from_json(animal_path)  # this will get altered
# add manure_management (done in State, for some reason??)
animal_mgt_data["manure_management_scenarios"] = make_data_dict_from_json(manure_management_path)[
    "manure_management_scenarios"]
animal_mgt_instance = AnimalManagement(animal_mgt_data, config_instance, feed_instance,
                                       weather_instance, time_instance)
# TODO: this isn't working because animal_mgt_data does not have a "manure_management_scenarios" key.
#   See State().__init__ to see how variables are initialized.
