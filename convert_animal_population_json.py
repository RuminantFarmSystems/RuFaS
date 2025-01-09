import json

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

animal_population_json_path = "input/data/animal/animal_population.json"

with open(animal_population_json_path) as f:
    animal_population = json.load(f)
    f.close()
print(animal_population.keys())

# for calf in animal_population["calves"]:
#     calf["animal_type"] = AnimalType.CALF.value
# for heiferI in animal_population["heiferIs"]:
#     heiferI["animal_type"] = AnimalType.HEIFER_I.value
# for heiferII in animal_population["heiferIIs"]:
#     heiferII["animal_type"] = AnimalType.HEIFER_II.value
# for heiferIII in animal_population["heiferIIIs"]:
#     heiferIII["animal_type"] = AnimalType.HEIFER_III.value
# for cow in animal_population["cows"]:
#     cow["animal_type"] = AnimalType.LAC_COW.value if cow["days_in_milk"] > 0 else AnimalType.DRY_COW.value
# for cow in animal_population["replacement"]:
#     cow["animal_type"] = AnimalType.HEIFER_III.value

for cow in animal_population["replacement"]:
    cow["heifer_reproduction_program"] = cow["repro_program"]
    cow["heifer_reproduction_sub_protocol"] = cow["repro_sub_protocol"]
    # cow["cow_reproduction_program"] = cow["repro_program"]
    # cow["cow_reproduction_sub_protocol"] = cow["repro_sub_protocol"]
    assert "heifer_reproduction_program" in cow.keys()
    assert "heifer_reproduction_sub_protocol" in cow.keys()
    # assert "cow_reproduction_program" in cow.keys()
    # assert "cow_reproduction_sub_protocol" in cow.keys()

for animal in (
        animal_population["calves"] +
        animal_population["heiferIs"] +
        animal_population["heiferIIs"] +
        animal_population["heiferIIIs"] +
        animal_population["cows"] +
        animal_population["replacement"]
):
    assert "animal_type" in animal.keys()
with open(animal_population_json_path, "w") as f:
    json.dump(animal_population, f, separators=(',', ':'))
