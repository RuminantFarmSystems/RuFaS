from RUFAS.input_manager import InputManager


class AnimalConfig:
    wean_day: int
    heifer_breed_start_day: int  # previously breeding_start_day_h
    heifer_prefresh_day: int  # previously prefresh_day
    heifer_reproduction_cull_day: int  # previously heifer_repro_cull_time

    heifer_reproduction_program: str
    heifer_reproduction_sub_program: str

    cow_reproduction_program: str
    cow_presynch_method: str
    cow_tai_method: str
    cow_resynch_method: str

    @classmethod
    def initialize_animal_config(cls) -> None:
        im = InputManager()
        animal_config_data = im.get_data("animal.animal_config")

        cls.wean_day = animal_config_data["farm_level"]["calf"]["wean_day"]
        cls.heifer_breed_start_day = animal_config_data["management_decisions"]["breeding_start_day_h"]
        cls.heifer_prefresh_day = animal_config_data["farm_level"]["repro"]["prefresh_day"]
        cls.heifer_reproduction_cull_day = animal_config_data["management_decisions"]["heifer_repro_cull_time"]

        cls.heifer_reproduction_program = animal_config_data["management_decisions"]["heifer_repro_method"]
        cls.heifer_reproduction_sub_program = animal_config_data["farm_level"]["repro"]["heifers"]["repro_sub_protocol"]

        cls.cow_reproduction_program = animal_config_data["management_decisions"]["cow_repro_method"]
        cls.cow_presynch_method = animal_config_data["farm_level"]["repro"]["cows"]["presynch_program"]
        cls.cow_tai_method = animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program"]
        cls.cow_resynch_method = animal_config_data["farm_level"]["repro"]["cows"]["resynch_program"]
