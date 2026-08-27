from typing import Any

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
from RUFAS.output_manager import OutputManager


class AnimalConfig:
    """
    AnimalConfig class that holds all the animal configuration parameters from user input.

    Attributes
    ----------
    wean_day : int
        The number of days after birth when a calf is weaned, (simulation day).
    wean_length : int
        The duration required for weaning, (simulation day).
    target_heifer_pregnant_day : int
        The target day for heifers to become pregnant, (simulation day).
    heifer_breed_start_day : int
        The day heifer breeding starts, (simulation day).
    heifer_prefresh_day : int
        The number of days for prefresh heifer preparation , (simulation day).
    calving_interval : int
        The targeted interval between calvings, (simulation day).
    dry_off_day_of_pregnancy : int
        The day of pregnancy when a cow is dried off, (simulation day).
    heifer_reproduction_cull_day : int
        Maximum day at which a heifer is culled if not pregnant, (simulation day).
    do_not_breed_time : int
        The duration after which breeding is stopped, (simulation day).
    semen_type : str
        Types of semen used for reproduction, e.g., "conventional", (unitless).
    male_calf_rate_conventional_semen : float
        Proportion of male calves when conventional semen is used, (unitless).
    male_calf_rate_sexed_semen : float
        Proportion of male calves when sexed semen is used, (unitless).
    keep_female_calf_rate : float
        Rate at which female calves are kept, used when ``calf_retention_method`` is
        ``"rate"`` (unitless).
    calf_retention_method : str
        Method used to decide female-calf retention: ``"rate"`` (keep each live female
        calf with probability ``keep_female_calf_rate``) or ``"count"`` (keep a target
        number of female calves per year, ``annual_keep_female_calf_num``).
    annual_keep_female_calf_num : int
        Target number of female calves to keep per year, used when
        ``calf_retention_method`` is ``"count"``, (head/year).
    still_birth_rate : float
        Probability of stillbirth occurring during calving, (unitless).
    average_gestation_length : int
        The average gestation length, (simulation day).
    std_gestation_length : float
        The standard deviation for gestation length, (simulation day).
    cow_times_milked_per_day : int
        Number of times a cow is milked per day, (unitless).
    milk_fat_percent : float
        Percentage of milk fat in cow's milk, (unitless).
    true_protein_percent : float
        Percentage of true protein in cow's milk, (unitless).
    heifer_reproduction_program : HeiferReproductionProtocol
        Heifer reproduction program used.
    heifer_reproduction_sub_program : HeiferTAISubProtocol | HeiferSynchEDSubProtocol
        Sub-program for heifer reproduction.
    heifer_estrus_detection_rate : float
        Probability of detecting estrus in heifers, (unitless).
    heifer_estrus_conception_rate : float
        Conception rate during detected estrus for heifers, (unitless).
    heifer_reproduction_sub_program_conception_rate : float
        Conception rate for the heifer sub-program, (unitless).
    heifer_reproduction_sub_program_estrus_detection_rate : float
        Estrus detection rate for the heifer sub-program, (unitless).
    cow_reproduction_program : CowReproductionProtocol
        Main reproduction program used for cows.
    cow_estrus_conception_rate : float
        Conception rate during detected estrus in cows, (unitless).
    cow_presynch_method : CowPreSynchSubProtocol
        Presynchronization method for cows.
    cow_tai_method : CowTAISubProtocol
        Timed artificial insemination (TAI) protocol for cows.
    cow_ovsynch_method : CowTAISubProtocol
        Ovsynch protocol for use in reproduction schedules.
    cow_resynch_method : CowReSynchSubProtocol
        Resynchronization protocol for cows.
    cow_estrus_detection_rate : float
        Probability of detecting estrus in cows.
    ovsynch_program_start_day : int
        The starting day for the Ovsynch program, (simulation day).
    ovsynch_program_conception_rate : float
        Conception rate associated with the Ovsynch program, (unitless).
    presynch_program_start_day : int
        The starting day for the presynchronization program, (simulation day).
    voluntary_waiting_period : int
        The voluntary waiting period before breeding is resumed after calving, (simulation day).
    birth_weight_avg_ho : float
        Average Holstein birth weight, (kg).
    birth_weight_std_ho : float
        Standard deviation for Holstein birth weight, (kg).
    birth_weight_avg_je : float
        Average Jersey birth weight, (kg).
    birth_weight_std_je : float
        Standard deviation for Jersey birth weight, (kg).
    average_mature_body_weight : float
        Average weight of a mature cow, (kg).
    std_mature_body_weight : float
        Standard deviation for mature cow body weight, (kg).
    conception_rate_decrease : float
        Proportional decrease in conception rate with each unsuccessful breeding attempt, (unitless).
    should_decrease_conception_rate_in_rebreeding : bool
        Whether to adjust conception rates for subsequent breeding cycles, (unitless).
    should_decrease_conception_rate_by_parity : bool
        Whether to adjust conception rates based on parity number, (unitless).
    average_estrus_cycle_return : int
        Average number of days before an estrus cycle returns, (simulation day).
    std_estrus_cycle_return : float
        Standard deviation for estrus cycle return time, (simulation day).
    average_estrus_cycle_heifer : int
        Average estrus cycle length for heifers, (simulation day).
    std_estrus_cycle_heifer : float
        Standard deviation for heifer estrus cycle length, (simulation day).
    average_estrus_cycle_cow : int
        Average estrus cycle length for cows, (simulation day).
    std_estrus_cycle_cow : float
        Standard deviation for cow estrus cycle length, (simulation day).
    average_estrus_cycle_after_pgf : int
        Average estrus cycle length after prostaglandin injection, (simulation day).
    std_estrus_cycle_after_pgf : float
        Standard deviation for estrus cycle length after prostaglandin injection, (simulation day).
    first_pregnancy_check_day : int
        First pregnancy check day post-breeding, (simulation day).
    first_pregnancy_check_loss_rate : float
        Pregnancy loss probability during the first pregnancy check, (unitless).
    second_pregnancy_check_day : int
        Second pregnancy check day post-breeding, (simulation day).
    second_pregnancy_check_loss_rate : float
        Pregnancy loss probability during the second pregnancy check, (unitless).
    third_pregnancy_check_day : int
        Third pregnancy check day post-breeding, (simulation day).
    third_pregnancy_check_loss_rate : float
        Pregnancy loss probability during the third pregnancy check, (unitless).
    parity_death_probability : list[float]
        Annual, parity-indexed probability that a cow dies during a given year, (unitless).
    parity_acute_sale_probability : list[float]
        Annual, parity-indexed probability that a cow is sold for an acute / involuntary
        reason during a given year, (unitless).
    methane_mitigation_method : str
        The mitigation method applied for methane reduction, e.g., "None", (unitless).
    methane_mitigation_additive_amount : float
        The dose of the additive selected by ``methane_mitigation_method``, taken from that
        method's per-additive input field, (mg/kg DMI).
    milk_reduction_maximum : float
        Maximum possible milk production reduction from a given cause, (kg).
    methane_model: dict[str, Any]
        Methane emission model selections for each animal category and production stage.
    average_phenotype : dict[str, dict[int, float]]
        Average genetic phenotype values used for genetic simulations.
    top_listing_semen : dict[str, dict[str, float]]
        Semen sire information used for genetic simulations and breeding selection.
    simulate_genetics : bool
        Whether genetic simulation functionality is enabled.

    """

    wean_day: int = 60
    wean_length: int = 7
    target_heifer_pregnant_day: int = 399
    heifer_breed_start_day: int = 380
    heifer_prefresh_day: int = 21
    calving_interval: int = 400
    dry_off_day_of_pregnancy: int = 218
    heifer_reproduction_cull_day: int = 500
    do_not_breed_time: int = 185
    calf_mortality_rate: float = 0.0
    heifer_mortality_rate: float = 0.0

    semen_type: str = "conventional"
    male_calf_rate_conventional_semen: float = 0.53
    male_calf_rate_sexed_semen: float = 0.10
    keep_female_calf_rate: float = 1
    calf_retention_method: str = "rate"
    annual_keep_female_calf_num: int = 0
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

    # Annual, parity-indexed probabilities that a cow dies (parity_death_probability) or is sold
    # for an acute / involuntary reason (parity_acute_sale_probability) during a given year. See
    # issue #2694: these were formerly evaluated once per lactation and are now evaluated annually.
    parity_death_probability: list[float] = [0.039, 0.056, 0.085, 0.117]
    parity_acute_sale_probability: list[float] = [0.169, 0.233, 0.301, 0.408]

    methane_model: dict[str, Any] = {
        "calves": "Pattanaik",
        "heiferIs": "IPCC",
        "heiferIIs": "IPCC",
        "heiferIIIs": "IPCC",
        "cow": {
            "dry cows": "IPCC",
            "lactating cows": "IPCC",
        },
    }
    methane_mitigation_method: str = "None"
    methane_mitigation_additive_amount: float = 0.0
    _METHANE_MITIGATION_DOSE_FIELDS: dict[str, str] = {
        "3-NOP": "3-NOP_additive_amount",
        "Monensin": "monensin_additive_amount",
        "Essential Oils": "essential_oils_additive_amount",
        "Seaweed": "seaweed_additive_amount",
    }

    milk_reduction_maximum: float

    average_phenotype: dict[str, dict[int, float]] = {}
    top_listing_semen: dict[str, dict[str, float]] = {}
    simulate_genetics: bool = False

    @classmethod
    def initialize_animal_config(cls) -> None:
        """Initialize the animal config from the input manager user input data."""
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
        cls.calf_mortality_rate = animal_config_data["management_decisions"]["calf_mortality_rate"]
        cls.heifer_mortality_rate = animal_config_data["management_decisions"]["heifer_mortality_rate"]

        cls.semen_type = animal_config_data["management_decisions"]["semen_type"]
        cls.male_calf_rate_conventional_semen = animal_config_data["farm_level"]["calf"][
            "male_calf_rate_conventional_semen"
        ]
        cls.male_calf_rate_sexed_semen = animal_config_data["farm_level"]["calf"]["male_calf_rate_sexed_semen"]
        cls.keep_female_calf_rate = animal_config_data["farm_level"]["calf"]["keep_female_calf_rate"]
        cls.calf_retention_method = animal_config_data["farm_level"]["calf"].get("calf_retention_method", "rate")
        cls.annual_keep_female_calf_num = int(
            animal_config_data["farm_level"]["calf"].get("annual_keep_female_calf_num", 0)
        )
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
        cls.parity_acute_sale_probability = animal_config_data["from_literature"]["culling"]["parity_acute_sale_prob"]

        cls.methane_model = animal_data["methane_model"]
        methane_mitigation_data = animal_data["methane_mitigation"]
        cls.methane_mitigation_method = methane_mitigation_data["methane_mitigation_method"]
        dose_field = cls._METHANE_MITIGATION_DOSE_FIELDS.get(cls.methane_mitigation_method)
        if dose_field is not None and dose_field not in methane_mitigation_data:
            OutputManager().add_warning(
                "Missing methane mitigation additive dose",
                f"The selected methane mitigation method '{cls.methane_mitigation_method}' takes its dose from "
                f"'{dose_field}', but that field is missing from the animal input. Defaulting the dose to 0, "
                "which applies no mitigation.",
                {
                    "class": cls.__name__,
                    "function": "initialize_animal_config",
                },
            )
        cls.methane_mitigation_additive_amount = methane_mitigation_data.get(dose_field, 0.0) if dose_field else 0.0

        cls.milk_reduction_maximum = im.get_data("feed.ration_formulation_parameters.milk_reduction_maximum")

        if cls.third_pregnancy_check_day >= cls.dry_off_day_of_pregnancy:
            om = OutputManager()
            om.add_warning(
                "3rd pregnancy check day >= Dry-off day",
                "Typically, the 3rd pregnancy check day should happen before the dry-off day."
                "The configured animal input has the 3rd pregnancy check day set to on or after the dry-off day."
                "This may cause the animal to be stuck in an unexpected state.",
                {
                    "class": AnimalConfig.__class__.__name__,
                    "function": "initialize_animal_config",
                },
            )

        average_phenotype = im.get_data("animal_mean_phenotype")
        cls.average_phenotype = {
            trait: dict(zip(average_phenotype["birth_year"], values))
            for trait, values in average_phenotype.items()
            if trait != "birth_year"
        }

        top_listing_semen = im.get_data("animal_top_listing_semen")
        cls.top_listing_semen = {
            trait: dict(zip(top_listing_semen["year_month"], values))
            for trait, values in top_listing_semen.items()
            if trait != "year_month"
        }
        cls.simulate_genetics = animal_data["herd_information"]["simulate_genetics"]
