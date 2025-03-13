from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    CowReproductionProtocol,
    CowPreSynchSubProtocol,
    CowTAISubProtocol,
    CowReSynchSubProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
)
from RUFAS.input_manager import InputManager


class AnimalConfig:
    wean_day: int = 60
    wean_length: int = 7
    target_heifer_pregnant_day: int = 399
    heifer_breed_start_day: int = 380
    heifer_prefresh_day: int = 21
    calving_interval: int = 400
    dry_off_day_of_pregnancy: int = 218
    heifer_reproduction_cull_day: int = 500
    do_not_breed_time: int = 185
    cull_milk_production: int = 30

    semen_type: str = "conventional"
    male_calf_rate_conventional_semen: float = 0.53
    male_calf_rate_sexed_semen: float = 0.10
    keep_female_calf_rate: float = 1
    still_birth_rate: float = 0.065
    average_gestation_length: int = 276
    std_gestation_length: float = 6
    cow_times_milked_per_day: int = 3
    milk_fat_percent: float = 4
    true_protein_percent: float = 3.2

    heifer_reproduction_program: HeiferReproductionProtocol = HeiferReproductionProtocol("ED")
    heifer_reproduction_sub_program: HeiferTAISubProtocol | HeiferSynchEDSubProtocol = HeiferTAISubProtocol("5dCG2P")
    heifer_estrus_detection_rate: float = 0.9
    heifer_estrus_conception_rate: float = 0.6
    heifer_reproduction_sub_program_conception_rate: float = 0.6
    heifer_reproduction_sub_program_estrus_detection_rate: float = 0.9

    cow_reproduction_program: CowReproductionProtocol = CowReproductionProtocol("ED-TAI")
    cow_estrus_conception_rate: float = 0.6
    cow_presynch_method: CowPreSynchSubProtocol = CowPreSynchSubProtocol("Double OvSynch")
    cow_tai_method: CowTAISubProtocol = CowTAISubProtocol("OvSynch 56")
    cow_ovsynch_method: CowTAISubProtocol = CowTAISubProtocol("OvSynch 56")
    cow_resynch_method: CowReSynchSubProtocol = CowReSynchSubProtocol("TAIafterPD")
    cow_estrus_detection_rate: float = 0.5
    ovsynch_program_start_day: int = 64
    ovsynch_program_conception_rate: float = 0.6
    presynch_program_start_day: int = 50

    voluntary_waiting_period: int = 50

    birth_weight_avg_ho: float = 43.9
    birth_weight_std_ho: float = 1
    birth_weight_avg_je: float = 27.2
    birth_weight_std_je: float = 1
    average_mature_body_weight: float = 740.1
    std_mature_body_weight: float = 73.5

    conception_rate_decrease: float = 0.026
    should_decrease_conception_rate_in_rebreeding: bool = False
    should_decrease_conception_rate_by_parity: bool = False

    average_estrus_cycle_return: int = 23
    std_estrus_cycle_return: float = 6
    average_estrus_cycle_heifer: int = 21
    std_estrus_cycle_heifer: float = 2.5
    average_estrus_cycle_cow: int = 21
    std_estrus_cycle_cow: float = 4
    average_estrus_cycle_after_pgf: int = 5
    std_estrus_cycle_after_pgf: float = 2

    first_pregnancy_check_day: int = 32
    first_pregnancy_check_loss_rate: float = 0.02
    second_pregnancy_check_day: int = 60
    second_pregnancy_check_loss_rate: float = 0.096
    third_pregnancy_check_day: int = 200
    third_pregnancy_check_loss_rate: float = 0.017

    parity_death_probability: list[float] = [0.039, 0.056, 0.085, 0.117]
    death_day_probability: list[float] = [0, 0.18, 0.32, 0.42, 0.48, 0.54, 0.60, 0.65, 0.70, 0.77, 0.83, 0.89, 0.95, 1]

    parity_cull_probability: list[float] = [0.169, 0.233, 0.301, 0.408]
    cull_day_count: list[int] = [0, 5, 15, 45, 90, 135, 180, 225, 270, 330, 380, 430, 480, 530]
    feet_leg_cull_probability: float = 0.1633
    feet_leg_cull_day_probability: list[float] = [
        0,
        0.03,
        0.08,
        0.16,
        0.25,
        0.36,
        0.48,
        0.59,
        0.69,
        0.78,
        0.85,
        0.90,
        0.95,
        1,
    ]
    injury_cull_probability: float = 0.2883
    injury_cull_day_probability: list[float] = [
        0,
        0.08,
        0.18,
        0.28,
        0.38,
        0.47,
        0.56,
        0.64,
        0.71,
        0.78,
        0.85,
        0.90,
        0.95,
        1,
    ]
    mastitis_cull_probability: float = 0.2439
    mastitis_cull_day_probability: list[float] = [
        0,
        0.06,
        0.12,
        0.19,
        0.30,
        0.43,
        0.56,
        0.68,
        0.78,
        0.85,
        0.90,
        0.94,
        0.97,
        1,
    ]
    disease_cull_probability: float = 0.1391
    disease_cull_day_probability: list[float] = [
        0,
        0.04,
        0.12,
        0.24,
        0.34,
        0.42,
        0.50,
        0.57,
        0.64,
        0.72,
        0.81,
        0.89,
        0.95,
        1,
    ]
    udder_cull_probability: float = 0.0645
    udder_cull_day_probability: list[float] = [
        0,
        0.12,
        0.24,
        0.33,
        0.41,
        0.48,
        0.55,
        0.62,
        0.68,
        0.76,
        0.82,
        0.89,
        0.95,
        1,
    ]
    unknown_cull_probability: float = 0.1009
    unknown_cull_day_probability: list[float] = [
        0,
        0.05,
        0.11,
        0.18,
        0.27,
        0.37,
        0.45,
        0.54,
        0.62,
        0.70,
        0.77,
        0.84,
        0.92,
        1,
    ]

    methane_model: str = "IPCC"
    methane_mitigation_method: str = "None"
    methane_mitigation_additive_amount: float = 0.0

    milk_reduction_maximum: float

    @classmethod
    def initialize_animal_config(cls) -> None:
        im = InputManager()
        animal_data = im.get_data("animal")
        animal_config_data = animal_data["animal_config"]

        cls.wean_day = animal_config_data["farm_level"]["calf"]["wean_day"]
        cls.wean_length = animal_config_data["farm_level"]["calf"]["wean_length"]
        cls.target_heifer_pregnant_day = animal_config_data["farm_level"]["bodyweight"]["target_heifer_preg_day"]
        cls.heifer_breed_start_day = animal_config_data["management_decisions"]["breeding_start_day_h"]
        cls.heifer_prefresh_day = animal_config_data["farm_level"]["repro"]["prefresh_day"]
        cls.calving_interval = animal_config_data["farm_level"]["repro"]["calving_interval"]
        cls.dry_off_day_of_pregnancy = animal_config_data["management_decisions"]["days_in_preg_when_dry"]
        cls.heifer_reproduction_cull_day = animal_config_data["management_decisions"]["heifer_repro_cull_time"]
        cls.do_not_breed_time = animal_config_data["management_decisions"]["do_not_breed_time"]
        cls.cull_milk_production = animal_config_data["management_decisions"]["cull_milk_production"]

        cls.semen_type = animal_config_data["management_decisions"]["semen_type"]
        cls.male_calf_rate_conventional_semen = animal_config_data["farm_level"]["calf"][
            "male_calf_rate_conventional_semen"
        ]
        cls.male_calf_rate_sexed_semen = animal_config_data["farm_level"]["calf"]["male_calf_rate_sexed_semen"]
        cls.keep_female_calf_rate = animal_config_data["farm_level"]["calf"]["keep_female_calf_rate"]
        cls.still_birth_rate = animal_config_data["from_literature"]["life_cycle"]["still_birth_rate"]
        cls.average_gestation_length = animal_config_data["farm_level"]["repro"]["avg_gestation_len"]
        cls.std_gestation_length = animal_config_data["farm_level"]["repro"]["std_gestation_len"]
        cls.cow_times_milked_per_day = animal_config_data["management_decisions"]["cow_times_milked_per_day"]
        cls.milk_fat_percent = animal_config_data["management_decisions"]["milk_fat_percent"]
        cls.true_protein_percent = animal_config_data["management_decisions"]["milk_protein_percent"]

        cls.heifer_reproduction_program = HeiferReproductionProtocol(
            animal_config_data["management_decisions"]["heifer_repro_method"]
        )
        if cls.heifer_reproduction_program == HeiferReproductionProtocol.TAI:
            cls.heifer_reproduction_sub_program = HeiferTAISubProtocol(
                animal_config_data["farm_level"]["repro"]["heifers"]["repro_sub_protocol"]
            )
        elif cls.heifer_reproduction_program == HeiferReproductionProtocol.SynchED:
            cls.heifer_reproduction_sub_program = HeiferSynchEDSubProtocol(
                animal_config_data["farm_level"]["repro"]["heifers"]["repro_sub_protocol"]
            )
        else:
            cls.heifer_reproduction_sub_program = HeiferTAISubProtocol("5dCG2P")
        cls.heifer_estrus_detection_rate = animal_config_data["farm_level"]["repro"]["heifers"]["estrus_detection_rate"]
        cls.heifer_estrus_conception_rate = animal_config_data["farm_level"]["repro"]["heifers"][
            "estrus_conception_rate"
        ]
        cls.heifer_reproduction_sub_program_conception_rate = animal_config_data["farm_level"]["repro"]["heifers"][
            "repro_sub_properties"
        ]["conception_rate"]
        cls.heifer_reproduction_sub_program_estrus_detection_rate = animal_config_data["farm_level"]["repro"][
            "heifers"
        ]["repro_sub_properties"]["estrus_detection_rate"]

        cls.cow_reproduction_program = CowReproductionProtocol(
            animal_config_data["management_decisions"]["cow_repro_method"]
        )
        cls.cow_estrus_detection_rate = animal_config_data["farm_level"]["repro"]["cows"]["estrus_detection_rate"]
        cls.cow_estrus_conception_rate = animal_config_data["farm_level"]["repro"]["cows"]["ED_conception_rate"]
        cls.cow_presynch_method = CowPreSynchSubProtocol(
            animal_config_data["farm_level"]["repro"]["cows"]["presynch_program"]
        )
        cls.cow_tai_method = CowTAISubProtocol(animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program"])
        cls.cow_ovsynch_method = CowTAISubProtocol(animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program"])
        cls.cow_resynch_method = CowReSynchSubProtocol(
            animal_config_data["farm_level"]["repro"]["cows"]["resynch_program"]
        )
        cls.ovsynch_program_start_day = animal_config_data["farm_level"]["repro"]["cows"]["ovsynch_program_start_day"]
        cls.ovsynch_program_conception_rate = animal_config_data["farm_level"]["repro"]["cows"][
            "ovsynch_program_conception_rate"
        ]
        cls.presynch_program_start_day = animal_config_data["farm_level"]["repro"]["cows"]["presynch_program_start_day"]

        cls.voluntary_waiting_period = animal_config_data["farm_level"]["repro"]["voluntary_waiting_period"]

        cls.birth_weight_avg_ho = animal_config_data["farm_level"]["bodyweight"]["birth_weight_avg_ho"]
        cls.birth_weight_std_ho = animal_config_data["farm_level"]["bodyweight"]["birth_weight_std_ho"]
        cls.birth_weight_avg_je = animal_config_data["farm_level"]["bodyweight"]["birth_weight_avg_je"]
        cls.birth_weight_std_je = animal_config_data["farm_level"]["bodyweight"]["birth_weight_std_je"]
        cls.average_mature_body_weight = animal_config_data["farm_level"]["bodyweight"]["mature_body_weight_avg"]
        cls.std_mature_body_weight = animal_config_data["farm_level"]["bodyweight"]["mature_body_weight_std"]

        cls.conception_rate_decrease = animal_config_data["farm_level"]["repro"]["conception_rate_decrease"]
        cls.should_decrease_conception_rate_in_rebreeding = animal_config_data["farm_level"]["repro"][
            "decrease_conception_rate_in_rebreeding"
        ]
        cls.should_decrease_conception_rate_by_parity = animal_config_data["farm_level"]["repro"][
            "decrease_conception_rate_by_parity"
        ]

        cls.average_estrus_cycle_return = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_return"]
        cls.std_estrus_cycle_return = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_return"]
        cls.average_estrus_cycle_heifer = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_heifer"]
        cls.std_estrus_cycle_heifer = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_heifer"]
        cls.average_estrus_cycle_cow = animal_config_data["from_literature"]["repro"]["avg_estrus_cycle_cow"]
        cls.std_estrus_cycle_cow = animal_config_data["from_literature"]["repro"]["std_estrus_cycle_cow"]
        cls.average_estrus_cycle_after_pgf = animal_config_data["from_literature"]["repro"][
            "avg_estrus_cycle_after_pgf"
        ]
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
            "cull_day_prob"
        ]
        cls.injury_cull_probability = animal_config_data["from_literature"]["culling"]["injury_cull"]["probability"]
        cls.injury_cull_day_probability = animal_config_data["from_literature"]["culling"]["injury_cull"][
            "cull_day_prob"
        ]
        cls.mastitis_cull_probability = animal_config_data["from_literature"]["culling"]["mastitis_cull"]["probability"]
        cls.mastitis_cull_day_probability = animal_config_data["from_literature"]["culling"]["mastitis_cull"][
            "cull_day_prob"
        ]
        cls.disease_cull_probability = animal_config_data["from_literature"]["culling"]["disease_cull"]["probability"]
        cls.disease_cull_day_probability = animal_config_data["from_literature"]["culling"]["disease_cull"][
            "cull_day_prob"
        ]
        cls.udder_cull_probability = animal_config_data["from_literature"]["culling"]["udder_cull"]["probability"]
        cls.udder_cull_day_probability = animal_config_data["from_literature"]["culling"]["udder_cull"]["cull_day_prob"]
        cls.unknown_cull_probability = animal_config_data["from_literature"]["culling"]["unknown_cull"]["probability"]
        cls.unknown_cull_day_probability = animal_config_data["from_literature"]["culling"]["unknown_cull"][
            "cull_day_prob"
        ]

        cls.methane_model = animal_data["methane_model"]
        cls.methane_mitigation_method = animal_data["methane_mitigation"]["methane_mitigation_method"]
        cls.methane_mitigation_additive_amount = animal_data["methane_mitigation"]["methane_mitigation_additive_amount"]

        cls.milk_reduction_maximum = im.get_data("feed.user_defined_ration_percentages.milk_reduction_maximum")
