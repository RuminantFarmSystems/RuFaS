# Meta data
from datetime import datetime
import json
import tomli_w
from pathlib import Path
from typing import Optional
import pickle

## NOTE these data are intentionally different from RUFAS to exemplify a test problem.

# Information about the user and use
META_DEFAULT = {
    "name": "Scenario A",  # string
    "author": {  # dict
        "name": "Clay Morrow",  # key label matches higher-level key label "name"
        "email": "25436787+morrowcj@users.noreply.github.com",
        "affiliation": "RUFAS",
    },
    "date": str(datetime.now().date()),  # current date
    "years_collected": [2018, 2020, 2021]  # simple list
}

# Model parameters, settings, etc.
CONFIG_DEFAULT = {
    "start": (2013, 1),  # tuples (year, day)
    "end": (2019, 365),
    "task_type": "SIMULATION_SINGLE_RUN",  # controlled by an ENUM
    "seed": 42,  # integer
    "exclude_info_maps": True,  # bool
    "sub-configs": [],  # optional argument [list]
}

# data
## animal data
ANIMAL_DEFAULT = {
    "pens": [  # list of dicts
        {
            "name": "first pen",
            "cow_names": ["bessy", "sally", "meridith", "billy"],  # sublist
            "nicknames": {"bessy": "sleepy", "sally": "softy",
                          "meridith": "m-dith", "billy": "jennifer"}  # subdict
        },
        {
            "name": "second pen",
            "cow_names": ["finn", "jake", "marcy", "betty", "simon"],
            # missing nicknames
        }
    ]
}


## quick function to construct crop schedule
def make_schedule(name: str, plant: int | list[int], harv: int | list[int]) -> dict:
    return {"crop": name, "plant_days": [plant], "harvest_days": [harv]}


## field data
FIELD_DEFAULT = {
    "rotation": {
        "pattern_start": (2015, 1),  # (year, day) that the pattern starts on.
        "pattern": [
            make_schedule("corn_silage", 127, 263),  # name, plant day, harvest day,
            make_schedule("alfalfa_silage", 89, [120, 150, 179, 210, 242]),
            make_schedule("my_corn", 130, 265)
        ],

    },
    "custom_crops": [
        {
            "id": "my_corn",  # referenced above in rotation.pattern
            "template": "corn_grain",
            "minimum_temperature": 8.5,
        }
    ]
}

DEFAULT_DATA = {
    "metadata": META_DEFAULT, "configuration": CONFIG_DEFAULT,
    "pool": {"animal": ANIMAL_DEFAULT, "field": FIELD_DEFAULT}
}

DEFAULT_DATA_PATH = "_internal/defaults.pkl" # relative to this file's parent dir


class UserInput:
    def __init__(self, data: Optional[dict] = None):
        if data is None:
            self._load_defaults()
        else:
            self.data = data

    def _load_defaults(self):
        """load default data from globals"""
        self.data = DEFAULT_DATA

    def load_data_file(self, path: str | Path):
        """load data from file"""
        path = Path(path)
        if path.suffix == ".pkl":
            with open(path, "rb") as f:
                self.data = pickle.load(f)
        elif path.suffix == ".json":
            with open(path, "r") as f:
                self.data = json.load(f)
        elif path.suffix == ".toml":
            with open(path, "rb") as f:
                self.data = tomli_w.load(f)
        else:
            raise Exception(f"Unsupported input format: {path.suffix}")

    def get_data(self):
        return self.data

    def wipe_data(self):
        self.data = None

    def write_data(self, path: str | Path = None, mkdir=True):
        if path is None:
            path = DEFAULT_DATA_PATH

        path = Path(path)

        if mkdir:
            path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix == ".pkl":
            with open(path, "wb") as f:
                pickle.dump(self.data, f)
        ## TODO: other formats would be supported (but need translation of unsupported types)
        elif path.suffix == ".json":
            with open(path, "w") as f:
                json.dump(self.data, f, indent=4)
        elif path.suffix == ".toml":
            with open(path, "wb") as f:
                tomli_w.dump(self.data, f, indent=2)
        else:
            raise Exception(f"Unsupported output format: {path.suffix}")
        # self.data = all_data

if __name__ == '__main__':
    UI = UserInput()
    UI._load_defaults()
    UI.write_data("_internal/defaults.pkl")
    UI.write_data("_internal/defaults.json")
    UI.write_data("_internal/defaults.toml")

    UI.wipe_data()
    UI.load_data_file("_internal/defaults.pkl")