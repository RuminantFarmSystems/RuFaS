from RUFAS.input_manager import InputManager


class AnimalConfig:
    wean_day: int
    heifer_breed_start_day: int  # previously breeding_start_day_h
    heifer_prefresh_day: int  # previously prefresh_day
    heifer_reproduction_cull_day: int  # previously heifer_repro_cull_time

    semen_type: str
    average_gestation_length: int
    std_gestation_length: float

    heifer_reproduction_program: str
    heifer_reproduction_sub_program: str
    heifer_estrus_detection_rate: float
    heifer_estrus_conception_rate: float
    heifer_reproduction_sub_program_conception_rate: float
    heifer_reproduction_sub_program_estrus_detection_rate: float


    cow_reproduction_program: str
    cow_estrus_conception_rate: float
    cow_presynch_method: str
    cow_tai_method: str
    cow_ovsynch_method: str
    cow_resynch_method: str
    cow_estrus_detection_rate: float
    ovsynch_program_start_day: int
    ovsynch_program_conception_rate: float
    presynch_program_start_day: int

    voluntary_waiting_period: int

    birth_weight_avg_ho: float
    birth_weight_std_ho: float
    birth_weight_avg_je: float
    birth_weight_std_je: float

    conception_rate_decrease: float
    should_decrease_conception_rate_in_rebreeding: bool
    should_decrease_conception_rate_by_parity: bool

    average_estrus_cycle_return: int
    std_estrus_cycle_return: float
    average_estrus_cycle_heifer: int
    std_estrus_cycle_heifer: float
    average_estrus_cycle_cow: int
    std_estrus_cycle_cow: float
    average_estrus_cycle_after_pgf: int
    std_estrus_cycle_after_pgf: float

    first_pregnancy_check_day: int
    first_pregnancy_check_loss_rate: float
    second_pregnancy_check_day: int
    second_pregnancy_check_loss_rate: float
    third_pregnancy_check_day: int
    third_pregnancy_check_loss_rate: float

    parity_death_probability: list[float]
    death_day_probability: list[float]

    parity_cull_probability: list[float]
    cull_day_count: list[int]
    feet_leg_cull_probability: float
    feet_leg_cull_day_probability: list[float]
    injury_cull_probability: float
    injury_cull_day_probability: list[float]
    mastitis_cull_probability: float
    mastitis_cull_day_probability: list[float]
    disease_cull_probability: float
    disease_cull_day_probability: list[float]
    udder_cull_probability: float
    udder_cull_day_probability: list[float]
    unknown_cull_probability: float
    unknown_cull_day_probability: list[float]

    @classmethod
    def initialize_animal_config(cls) -> None:
        im = InputManager()
        animal_config_data = im.get_data("animal.animal_config")

        cls.wean_day = animal_config_data["farm_level"]["calf"]["wean_day"]
        cls.heifer_breed_start_day = animal_config_data["management_decisions"]["breeding_start_day_h"]
        cls.heifer_prefresh_day = animal_config_data["farm_level"]["repro"]["prefresh_day"]
        cls.heifer_reproduction_cull_day = animal_config_data["management_decisions"]["heifer_repro_cull_time"]

        cls.semen_type = animal_config_data["management_decisions"]["semen_type"]
        cls.average_gestation_length = animal_config_data["farm_level"]["repro"]["avg_gestation_len"]
        cls.std_gestation_length = animal_config_data["farm_level"]["repro"]["std_gestation_len"]

        cls.heifer_reproduction_program = animal_config_data["management_decisions"]["heifer_repro_method"]
        cls.heifer_reproduction_sub_program = animal_config_data["farm_level"]["repro"]["heifers"]["repro_sub_protocol"]
        cls.heifer_estrus_detection_rate = animal_config_data["farm_level"]["repro"]["heifers"]["estrus_detection_rate"]
        cls.heifer_estrus_conception_rate = animal_config_data["farm_level"]["repro"]["heifers"][
            "estrus_conception_rate"]
        cls.heifer_reproduction_sub_program_conception_rate = animal_config_data["farm_level"]["repro"]["heifers"][
            "repro_sub_properties"]["conception_rate"]
        cls.heifer_reproduction_sub_program_estrus_detection_rate = animal_config_data["farm_level"]["repro"][
            "heifers"]["repro_sub_properties"]["estrus_detection_rate"]

        cls.cow_reproduction_program = animal_config_data["management_decisions"]["cow_repro_method"]
        cls.cow_estrus_detection_rate = animal_config_data["farm_level"]["repro"]["cows"]["estrus_detection_rate"]
        cls.cow_estrus_conception_rate = animal_config_data["farm_level"]["repro"]["cows"]["ED_conception_rate"]
        cls.cow_presynch_method = animal_config_data["farm_level"]["repro"]["cows"]["presynch_program"]
        cls.cow_tai_method = animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program"]
        cls.cow_ovsynch_method = animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program"]
        cls.cow_resynch_method = animal_config_data["farm_level"]["repro"]["cows"]["resynch_program"]
        cls.ovsynch_program_start_day = animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program_start_day"]
        cls.ovsynch_program_conception_rate = animal_config_data["farm_level"]["repro"]["cows"][
            "ovsynch_program_conception_rate"]
        cls.ovsynch_program_start_day = animal_config_data["farm_level"]["repro"]["cows"]["presynch_program_start_day"]

        cls.voluntary_waiting_period = animal_config_data["farm_level"]["repro"]["voluntary_waiting_period"]

        cls.birth_weight_avg_ho = animal_config_data["farm_level"]["bodyweight"]["birth_weight_avg_ho"]
        cls.birth_weight_std_ho = animal_config_data["farm_level"]["bodyweight"]["birth_weight_std_ho"]
        cls.birth_weight_avg_je = animal_config_data["farm_level"]["bodyweight"]["birth_weight_avg_je"]
        cls.birth_weight_std_je = animal_config_data["farm_level"]["bodyweight"]["birth_weight_std_je"]

        cls.conception_rate_decrease = animal_config_data["farm_level"]["repro"]["conception_rate_decrease"]
        cls.should_decrease_conception_rate_in_rebreeding = animal_config_data["farm_level"]["repro"][
            "decrease_conception_rate_in_rebreeding"]
        cls.should_decrease_conception_rate_by_parity = animal_config_data["farm_level"]["repro"][
            "decrease_conception_rate_by_parity"]

        cls.average_estrus_cycle_return = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_return"]
        cls.std_estrus_cycle_return = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_return"]
        cls.average_estrus_cycle_heifer = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_heifer"]
        cls.std_estrus_cycle_heifer = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_heifer"]
        cls.average_estrus_cycle_cow = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_cow"]
        cls.std_estrus_cycle_cow = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_cow"]
        cls.average_estrus_cycle_after_pgf = animal_config_data["from_literature"]["repro"][
            "avg_estrus_cycle_after_pgf"]
        cls.std_estrus_cycle_after_pgf = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_after_pgf"]

        cls.first_pregnancy_check_day = animal_config_data["from_literature"]["repro"]["preg_check_day_1"]
        cls.first_pregnancy_check_loss_rate = animal_config_data["from_literature"]["repro"]["preg_loss_rate_1"]
        cls.second_pregnancy_check_day = animal_config_data["from_literature"]["repro"]["preg_check_day_2"]
        cls.second_pregnancy_check_loss_rate = animal_config_data["from_literature"]["repro"]["preg_loss_rate_2"]
        cls.third_pregnancy_check_day = animal_config_data["from_literature"]["repro"]["preg_check_day_3"]
        cls.third_pregnancy_check_loss_rate = animal_config_data["from_literature"]["repro"]["preg_loss_rate_3"]

        cls.parity_death_probability = animal_config_data["from_literature"]["culling"]["parity_death_prob"]
        cls.death_day_probability = animal_config_data["from_literature"]["culling"]["death_day_prob"]

        cls.parity_cull_probability = animal_config_data["from_literature"]["culling"]["parity_cull_prob"]
        cls.cull_day_count = animal_config_data["from_literature"]["culling"]["cull_day_count"]
        cls.feet_leg_cull_probability = animal_config_data["from_literature"]["culling"]["feet_leg_cull"]["probability"]
        cls.feet_leg_cull_day_probability = animal_config_data["from_literature"]["culling"]["feet_leg_cull"][
            "cull_day_prob"]
        cls.injury_cull_probability = animal_config_data["from_literature"]["culling"]["injury_cull"]["probability"]
        cls.injury_cull_day_probability = animal_config_data["from_literature"]["culling"]["injury_cull"][
            "cull_day_prob"]
        cls.mastitis_cull_probability = animal_config_data["from_literature"]["culling"]["mastitis_cull"]["probability"]
        cls.mastitis_cull_day_probability = animal_config_data["from_literature"]["culling"]["mastitis_cull"][
            "cull_day_prob"]
        cls.disease_cull_probability = animal_config_data["from_literature"]["culling"]["disease_cull"]["probability"]
        cls.disease_cull_day_probability = animal_config_data["from_literature"]["culling"]["disease_cull"][
            "cull_day_prob"]
        cls.udder_cull_probability = animal_config_data["from_literature"]["culling"]["udder_cull"]["probability"]
        cls.udder_cull_day_probability = animal_config_data["from_literature"]["culling"]["udder_cull"][
            "cull_day_prob"]
        cls.unknown_cull_probability = animal_config_data["from_literature"]["culling"]["unknown_cull"]["probability"]
        cls.unknown_cull_day_probability = animal_config_data["from_literature"]["culling"]["unknown_cull"][
            "cull_day_prob"]
