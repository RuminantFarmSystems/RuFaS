from RUFAS.biophysical.animal.animal_properties.general_properties import Breed, Sex
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType

LAC_COW_PROPERTIES = {
    "animal_type": AnimalType.LAC_COW,
    "birth_date": "2020-01-01",
    "birth_weight": 40.0,
    "body_weight": 600.0,
    "breed": Breed.HO,
    "culled": False,
    "days_born": 900,
    "days_in_preg": 100,
    "events": AnimalEvents(),
    "days_in_milk": 150,
    "dry_off_day_of_pregnancy": 180,
    "daily_milk_produced": 30.0,
    "future_cull_date": 1000,
    "future_death_date": 1100,
    "sex": Sex.FEMALE,
    "id": 1,
    "mature_body_weight": 700.0,
    "nutrients": ["protein", "fat"],
    "sold": False,
    "sold_at_day": 0,
    "wean_weight": 90.0,
}
