import json

from typing import Any


def update_birth_date(data_dict: dict[str, Any]) -> dict[str, Any]:
    data_dict.update(birth_date="")
    return data_dict


with open('input/data/animal/animal_population.json') as json_file:
    data: dict[str, list[dict[str, Any]]] = json.load(json_file)

data["calves"] = list(map(update_birth_date, data["calves"]))
data["heiferIs"] = list(map(update_birth_date, data["heiferIs"]))
data["heiferIIs"] = list(map(update_birth_date, data["heiferIIs"]))
data["heiferIIIs"] = list(map(update_birth_date, data["heiferIIIs"]))
data["cows"] = list(map(update_birth_date, data["cows"]))
data["replacement"] = list(map(update_birth_date, data["replacement"]))

with open('input/data/animal/animal_population2.json', "w") as outfile:
    json.dump(data, outfile)
