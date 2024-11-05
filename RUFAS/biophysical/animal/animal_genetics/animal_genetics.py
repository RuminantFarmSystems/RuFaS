from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.time import Time


class AnimalGenetics:
    def __init__(self) -> None:
        # read and save a lookup table for top-semen and net-merit percentile
        pass

    def assign_net_merit_value_to_animals_entering_herd(self, birth_date: str) -> float:
        pass
        return 0.0

    def assign_net_merit_value_to_newborn_calf(self, time: Time, breed: Breed, dam_net_merit_value: float) -> float:
        pass
        return 0.0
