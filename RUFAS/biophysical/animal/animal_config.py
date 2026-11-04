from datetime import date, timedelta
from typing import Any

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import (
    BeefPostWeaningDestination,
    FinishingSystem,
    RemovalRiskParityGroup,
    StockerDietSystem,
)
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    CowReproductionProtocol,
    CowPreSynchSubProtocol,
    CowTAISubProtocol,
    CowReSynchSubProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
    BeefReproductionProtocol,
)
from RUFAS.data_validator import DataValidator
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

_MONTHS_IN_YEAR: int = 12
"""Calendar months per year, for calving-month validation."""

_NON_LEAP_REFERENCE_YEAR: int = 2001
"""Arbitrary non-leap year used to convert between calendar month and day-of-year.

The simulation calendar is 365 days (GeneralConstants.YEAR_LENGTH), so a
non-leap reference year keeps the month boundaries consistent with it.
"""


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
    user_defined_male_calf_rate : float
        Proportion of male calves, (unitless).
    keep_dairy_female_rate : float
        Rate at which dairy female calves are kept, used when ``calf_retention_method`` is
        ``"rate"`` (unitless).
    calf_retention_method : str
        Method used to decide female-calf retention: ``"rate"`` (keep each live female
        calf with probability ``keep_dairy_female_rate``) or ``"count"`` (keep a target
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
    annual_death_probability : float
        Annual probability that a cow in the whole cow herd dies during a given year, (unitless).
    parity_death_distribution : dict[RemovalRiskParityGroup, float]
        Fractions of all cow deaths that come from the 1st, 2nd, and 3rd+ parity groups, (unitless).
    annual_sale_probability : float
        Annual probability that a cow in the whole cow herd is sold during a given year, (unitless).
    parity_sale_distribution : dict[RemovalRiskParityGroup, float]
        Fractions of all cow sales that come from the 1st, 2nd, and 3rd+ parity groups, (unitless).
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
    beef_breeding_season_start_day : int
        Day-of-year on which the beef breeding season opens (1–365).
    beef_breeding_season_length : int
        Length of the breeding season in days; default is 63 (standard 9-week season).
    beef_weaning_age_days : int
        Target weaning age for beef calves in days; default is the USDA average of 207 days.
    beef_weaning_weight_kg : float | None
        Target weaning weight in kg. When set, weaning is triggered by age OR weight (whichever
        comes first). None means age is the sole trigger.
    beef_creep_feeding_enabled : bool
        Whether nursing calves receive supplemental creep feed in addition to dam's milk.
    beef_post_weaning_destination : BeefPostWeaningDestination
        Fate of weaned calves: SELL, REPLACEMENT_HEIFER, DIRECT_TO_FEEDLOT, or STOCKER.
    beef_mature_cow_weight_kg : float
        Expected mature body weight for cows in this herd (kg); used to set replacement heifer
        development targets.
    beef_natural_service_bull_ratio : int
        Number of cows per bull for natural-service mating; NRC reference range is 20–30:1.
    beef_cow_cull_rate_annual : float
        Annual culling rate for mature beef cows (fraction); default is 0.175 (USDA average).
    beef_reproduction_program : BeefReproductionProtocol
        Reproduction protocol used for the beef cow-calf herd;
        default is NATURAL_SERVICE_SEASONAL.
    tbv_fat_variance : float
        Variance of the true breeding value (TBV) for fat yield in the herd, (kg^2). Defaults to the CDCB
        national average.
    tbv_protein_variance : float
        Variance of the true breeding value (TBV) for protein yield in the herd, (kg^2). Defaults to the CDCB
        national average.
    tbv_correlation : float
        Correlation between the fat and protein true breeding values, (unitless). Defaults to the CDCB
        national average.
    permanent_environment_fat_variance : float
        Variance of the permanent environmental effect on fat yield in the herd, (kg^2). Defaults to the CDCB
        national average.
    permanent_environment_protein_variance : float
        Variance of the permanent environmental effect on protein yield in the herd, (kg^2). Defaults to the
        CDCB national average.
    permanent_environment_correlation : float
        Correlation between the fat and protein permanent environmental effects, (unitless). Defaults to the
        CDCB national average.
    temporary_environment_fat_variance : float
        Variance of the temporary environmental effect on fat yield in the herd, (kg^2). Defaults to the CDCB
        national average.
    temporary_environment_protein_variance : float
        Variance of the temporary environmental effect on protein yield in the herd, (kg^2). Defaults to the
        CDCB national average.
    temporary_environment_correlation : float
        Correlation between the fat and protein temporary environmental effects, (unitless). Defaults to the
        CDCB national average.

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

    user_defined_male_calf_rate: float = 0.1
    selective_repro_strategy: bool = False
    ranking_method: str = "genetic"
    genetic_selection_index_weights: dict[str, float] = {
        "fat": 0.318,
        "protein": 0.13,
    }
    heiferII_semen_allocation_proportions: dict[str, float] = {
        "sexed_dairy": 0.5,
        "conventional_dairy": 0.5,
        "beef": 0.0,
    }
    cow_semen_allocation_proportions: dict[str, float] = {
        "sexed_dairy": 0.2,
        "conventional_dairy": 0.5,
        "beef": 0.3,
    }
    keep_dairy_female_rate: float = 1
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

    annual_death_probability: float = 0.05
    parity_death_distribution: dict[RemovalRiskParityGroup, float] = {
        RemovalRiskParityGroup.ONE: 0.2,
        RemovalRiskParityGroup.TWO: 0.3,
        RemovalRiskParityGroup.THREE_PLUS: 0.5,
    }
    annual_sale_probability: float = 0.32
    parity_sale_distribution: dict[RemovalRiskParityGroup, float] = {
        RemovalRiskParityGroup.ONE: 0.2,
        RemovalRiskParityGroup.TWO: 0.3,
        RemovalRiskParityGroup.THREE_PLUS: 0.5,
    }

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
    tbv_fat_variance: float = 25.8
    tbv_protein_variance: float = 13.4
    tbv_correlation: float = 0.59
    permanent_environment_fat_variance: float = 38.8
    permanent_environment_protein_variance: float = 20.1
    permanent_environment_correlation: float = 0.95
    temporary_environment_fat_variance: float = 64.5
    temporary_environment_protein_variance: float = 33.4
    temporary_environment_correlation: float = 0.78

    # ── FEEDLOT PARAMETERS (defaults; overridden by initialize_animal_config) ─
    feedlot_entry_weight: float = 320.0

    feedlot_slaughter_weight: float = 580.0
    feedlot_max_days_on_feed: int = 220
    feedlot_target_adg: float = 1.5
    feedlot_implant_adg_factor: float = 1.0
    feedlot_mud_condition: str = "none"
    feedlot_ndf_minimum_pct: float = 10.0
    finishing_system: FinishingSystem = FinishingSystem.GRAIN_FED

    # ── STOCKER / BACKGROUNDING PARAMETERS (defaults; overridden by initialize_animal_config) ─
    stocker_entry_weight: float = AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG
    stocker_exit_weight: float = AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG
    stocker_max_days: int = AnimalModuleConstants.STOCKER_MAX_DAYS
    stocker_target_adg: float = AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D
    stocker_diet_system: StockerDietSystem = StockerDietSystem.PASTURE
    stocker_limit_feed_pct: float = AnimalModuleConstants.STOCKER_DEFAULT_LIMIT_FEED_PCT

    enable_compensatory_gain: bool = False

    # ── ENVIRONMENTAL STRESS (farm-wide; applies to feedlot and stocker alike) ─
    # UPSTREAM-COLLISION: RuminantFarmSystems/RuFaS PR #3241 removes ~172
    # lines from this file (streamline_animal_culling_inputs). Reconcile
    # at sync: this field is farm-wide, parsed at the top level of the
    # animal config rather than from a sub-block.
    relative_humidity_pct: float | None = None

    # ── COW-CALF PARAMETERS (defaults; overridden by initialize_animal_config) ─
    beef_breeding_season_start_day: int = 90
    beef_breeding_season_length: int = AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
    beef_weaning_age_days: int = AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
    beef_weaning_weight_kg: float | None = None
    beef_creep_feeding_enabled: bool = False
    beef_post_weaning_destination: BeefPostWeaningDestination = BeefPostWeaningDestination.SELL
    beef_mature_cow_weight_kg: float = AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
    beef_natural_service_bull_ratio: int = 25
    beef_cow_cull_rate_annual: float = AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE
    beef_conception_rate_multiplier: float = 1.0
    beef_reproduction_program: BeefReproductionProtocol = BeefReproductionProtocol.NATURAL_SERVICE_SEASONAL

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

        cls.user_defined_male_calf_rate = animal_config_data["farm_level"]["calf"]["user_defined_male_calf_rate"]
        cls.selective_repro_strategy = animal_config_data["farm_level"]["repro"]["selective_repro_strategy"]
        cls.ranking_method = animal_config_data["farm_level"]["repro"]["ranking_method"]
        cls.genetic_selection_index_weights["fat"] = animal_config_data["farm_level"]["repro"][
            "genetic_selection_index_weights"
        ]["fat"]
        cls.genetic_selection_index_weights["protein"] = animal_config_data["farm_level"]["repro"][
            "genetic_selection_index_weights"
        ]["protein"]
        cls.heiferII_semen_allocation_proportions["sexed_dairy"] = animal_config_data["farm_level"]["repro"]["heifers"][
            "semen_allocation_proportions"
        ]["sexed_dairy"]
        cls.heiferII_semen_allocation_proportions["conventional_dairy"] = animal_config_data["farm_level"]["repro"][
            "heifers"
        ]["semen_allocation_proportions"]["conventional_dairy"]
        cls.heiferII_semen_allocation_proportions["beef"] = animal_config_data["farm_level"]["repro"]["heifers"][
            "semen_allocation_proportions"
        ]["beef"]
        cls.cow_semen_allocation_proportions["sexed_dairy"] = animal_config_data["farm_level"]["repro"]["cows"][
            "semen_allocation_proportions"
        ]["sexed_dairy"]
        cls.cow_semen_allocation_proportions["conventional_dairy"] = animal_config_data["farm_level"]["repro"]["cows"][
            "semen_allocation_proportions"
        ]["conventional_dairy"]
        cls.cow_semen_allocation_proportions["beef"] = animal_config_data["farm_level"]["repro"]["cows"][
            "semen_allocation_proportions"
        ]["beef"]
        cls.keep_dairy_female_rate = animal_config_data["farm_level"]["calf"]["keep_dairy_female_rate"]
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

        culling_data = animal_config_data["from_literature"]["culling"]
        cls.annual_death_probability = culling_data["annual_death_prob"]
        cls.parity_death_distribution[RemovalRiskParityGroup.ONE] = culling_data["parity_death_dist"][0]
        cls.parity_death_distribution[RemovalRiskParityGroup.TWO] = culling_data["parity_death_dist"][1]
        cls.parity_death_distribution[RemovalRiskParityGroup.THREE_PLUS] = culling_data["parity_death_dist"][2]
        cls.annual_sale_probability = culling_data["annual_sale_prob"]
        cls.parity_sale_distribution[RemovalRiskParityGroup.ONE] = culling_data["parity_sale_dist"][0]
        cls.parity_sale_distribution[RemovalRiskParityGroup.TWO] = culling_data["parity_sale_dist"][1]
        cls.parity_sale_distribution[RemovalRiskParityGroup.THREE_PLUS] = culling_data["parity_sale_dist"][2]

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

        genetics_data = animal_data["genetics"]
        cls.tbv_fat_variance = genetics_data["tbv_fat_variance"]
        cls.tbv_protein_variance = genetics_data["tbv_protein_variance"]
        cls.tbv_correlation = genetics_data["tbv_correlation"]
        cls.permanent_environment_fat_variance = genetics_data["permanent_environment_fat_variance"]
        cls.permanent_environment_protein_variance = genetics_data["permanent_environment_protein_variance"]
        cls.permanent_environment_correlation = genetics_data["permanent_environment_correlation"]
        cls.temporary_environment_fat_variance = genetics_data["temporary_environment_fat_variance"]
        cls.temporary_environment_protein_variance = genetics_data["temporary_environment_protein_variance"]
        cls.temporary_environment_correlation = genetics_data["temporary_environment_correlation"]

        # ── FEEDLOT PARAMETERS ───────────────────────────────────────────────
        feedlot_cfg: dict[str, Any] = animal_config_data.get("feedlot", {})
        cls.feedlot_entry_weight = float(feedlot_cfg.get("entry_weight", 320.0))
        cls.feedlot_slaughter_weight = float(feedlot_cfg.get("slaughter_weight", 580.0))
        cls.feedlot_max_days_on_feed = int(feedlot_cfg.get("max_days_on_feed", 220))
        cls.feedlot_target_adg = float(feedlot_cfg.get("target_adg", 1.5))
        cls.feedlot_implant_adg_factor = float(feedlot_cfg.get("implant_adg_factor", 1.0))
        cls.feedlot_mud_condition = str(feedlot_cfg.get("mud_condition", "none"))
        cls.feedlot_ndf_minimum_pct = float(feedlot_cfg.get("ndf_minimum_pct", 10.0))
        cls._initialize_feedlot_finishing_system(feedlot_cfg)

        # ── COW-CALF PARAMETERS ──────────────────────────────────────────────
        cls._initialize_beef_cow_calf_config(animal_config_data)

        # ── STOCKER / BACKGROUNDING PARAMETERS ───────────────────────────────
        stocker_cfg: dict[str, Any] = animal_config_data.get("stocker", {}) or {}
        cls._initialize_beef_stocker_config(stocker_cfg)

        # ── ENVIRONMENTAL STRESS ─────────────────────────────────
        cls._initialize_relative_humidity(animal_config_data)

    @classmethod
    def _initialize_relative_humidity(cls, animal_config_data: dict[str, Any]) -> None:
        """Initialize the relative_humidity_pct ClassVar from the animal config block.

        Parameters
        ----------
        animal_config_data : dict[str, Any]
            The raw ``animal_config`` dict. A missing or None value keeps the
            None default, which disables heat stress entirely.

        """
        DataValidator._validate_relative_humidity(animal_config_data)
        cls.relative_humidity_pct = (
            float(humidity) if (humidity := animal_config_data.get("relative_humidity_pct")) is not None else None
        )

    @classmethod
    def _initialize_feedlot_finishing_system(cls, feedlot_cfg: dict[str, Any]) -> None:
        """Initialize the finishing_system ClassVar from the ``feedlot`` config block.

        Parameters
        ----------
        feedlot_cfg : dict[str, Any]
            The raw ``feedlot`` sub-dict from ``animal_config`` (may be empty).
            A missing or None value keeps the GRAIN_FED default.

        """
        DataValidator._validate_feedlot_finishing_system(feedlot_cfg)
        cls.finishing_system = (
            FinishingSystem(str(raw))
            if (raw := feedlot_cfg.get("finishing_system")) is not None
            else FinishingSystem.GRAIN_FED
        )

    @classmethod
    def _initialize_beef_cow_calf_config(cls, animal_config_data: dict[str, Any]) -> None:
        """Initialize cow-calf ClassVars from the ``beef_cow_calf`` config block.

        Parameters
        ----------
        animal_config_data : dict[str, Any]
            The parsed ``animal_config`` sub-dict from InputManager.
        """
        beef_cfg_raw: Any = animal_config_data.get("beef_cow_calf", {})
        if beef_cfg_raw is None:
            beef_cfg: dict[str, Any] = {}
        elif not isinstance(beef_cfg_raw, dict):
            raise ValueError("animal_config.beef_cow_calf must be a dictionary when provided")
        else:
            beef_cfg = beef_cfg_raw
        merged_beef_cfg = cls._merge_beef_defaults(beef_cfg)
        DataValidator.validate_beef_cow_calf_config(merged_beef_cfg)
        cls._assign_beef_config_fields(beef_cfg, merged_beef_cfg)
        cls._parse_beef_enum_fields(beef_cfg)

    @classmethod
    def _initialize_beef_stocker_config(cls, stocker_cfg: dict[str, Any]) -> None:
        """Initialize stocker ClassVars from the ``stocker`` config block.

        Parameters
        ----------
        stocker_cfg : dict[str, Any]
            The raw ``stocker`` sub-dict from ``animal_config`` (may be empty).
            Unknown keys are silently ignored; missing keys keep class defaults.
        """
        DataValidator.validate_beef_stocker_config(stocker_cfg)
        cls.stocker_entry_weight = (
            float(entry_weight)
            if (entry_weight := stocker_cfg.get("entry_weight")) is not None
            else AnimalModuleConstants.STOCKER_MIN_ENTRY_WEIGHT_KG
        )
        cls.stocker_exit_weight = (
            float(exit_weight)
            if (exit_weight := stocker_cfg.get("exit_weight")) is not None
            else AnimalModuleConstants.STOCKER_TARGET_EXIT_WEIGHT_KG
        )
        cls.stocker_max_days = (
            int(max_days)
            if (max_days := stocker_cfg.get("max_days")) is not None
            else AnimalModuleConstants.STOCKER_MAX_DAYS
        )
        cls.stocker_target_adg = (
            float(target_adg)
            if (target_adg := stocker_cfg.get("target_adg")) is not None
            else AnimalModuleConstants.STOCKER_TARGET_ADG_KG_D
        )
        cls.stocker_diet_system = (
            StockerDietSystem(str(raw))
            if (raw := stocker_cfg.get("stocker_diet_system")) is not None
            else StockerDietSystem.PASTURE
        )
        cls.stocker_limit_feed_pct = (
            float(limit_feed_pct)
            if (limit_feed_pct := stocker_cfg.get("limit_feed_pct")) is not None
            else AnimalModuleConstants.STOCKER_DEFAULT_LIMIT_FEED_PCT
        )
        cls.enable_compensatory_gain = (
            bool(enable_cg) if (enable_cg := stocker_cfg.get("enable_compensatory_gain")) is not None else False
        )

    @classmethod
    def _merge_beef_defaults(cls, beef_cfg: dict[str, Any]) -> dict[str, Any]:
        """Return a merged config dict with defaults substituted for missing/None values.

        Parameters
        ----------
        beef_cfg : dict[str, Any]
            The raw ``beef_cow_calf`` sub-dict (may be empty).

        Returns
        -------
        dict[str, Any]
            Complete config with all required numeric fields present.
        """
        return {
            "mature_cow_weight_kg": (
                beef_cfg["mature_cow_weight_kg"]
                if beef_cfg.get("mature_cow_weight_kg") is not None
                else AnimalModuleConstants.BEEF_DEFAULT_MATURE_COW_WEIGHT_KG
            ),
            "weaning_age_days": (
                beef_cfg["weaning_age_days"]
                if beef_cfg.get("weaning_age_days") is not None
                else AnimalModuleConstants.BEEF_DEFAULT_WEANING_AGE_DAYS
            ),
            "breeding_season_length": (
                beef_cfg["breeding_season_length"]
                if beef_cfg.get("breeding_season_length") is not None
                else AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS
            ),
            "natural_service_bull_ratio": (
                beef_cfg["natural_service_bull_ratio"]
                if beef_cfg.get("natural_service_bull_ratio") is not None
                else AnimalModuleConstants.BEEF_DEFAULT_NATURAL_SERVICE_BULL_RATIO
            ),
            "cow_cull_rate_annual": (
                beef_cfg["cow_cull_rate_annual"]
                if beef_cfg.get("cow_cull_rate_annual") is not None
                else AnimalModuleConstants.BEEF_ANNUAL_CULL_RATE
            ),
            "breeding_season_start_day": (
                beef_cfg["breeding_season_start_day"]
                if beef_cfg.get("breeding_season_start_day") is not None
                else AnimalModuleConstants.BEEF_DEFAULT_BREEDING_SEASON_START_DAY
            ),
            "weaning_weight_kg": beef_cfg.get("weaning_weight_kg"),
            "conception_rate_multiplier": (
                beef_cfg["conception_rate_multiplier"]
                if beef_cfg.get("conception_rate_multiplier") is not None
                else 1.0
            ),
        }

    @classmethod
    def _assign_beef_config_fields(cls, beef_cfg: dict[str, Any], merged: dict[str, Any]) -> None:
        """Assign validated numeric and boolean ClassVars from the merged config.

        Parameters
        ----------
        beef_cfg : dict[str, Any]
            Raw ``beef_cow_calf`` sub-dict for optional fields.
        merged : dict[str, Any]
            Merged config with defaults applied (output of ``_merge_beef_defaults``).
        """
        cls.beef_breeding_season_length = int(merged["breeding_season_length"])
        cls.beef_weaning_age_days = int(merged["weaning_age_days"])
        cls.beef_mature_cow_weight_kg = float(merged["mature_cow_weight_kg"])
        cls.beef_natural_service_bull_ratio = int(merged["natural_service_bull_ratio"])
        cls.beef_cow_cull_rate_annual = float(merged["cow_cull_rate_annual"])
        cls.beef_breeding_season_start_day = int(merged["breeding_season_start_day"])
        cls.beef_weaning_weight_kg = (
            float(merged["weaning_weight_kg"]) if merged["weaning_weight_kg"] is not None else None
        )
        cls.beef_creep_feeding_enabled = bool(beef_cfg.get("creep_feeding_enabled") or False)
        cls.beef_conception_rate_multiplier = float(merged["conception_rate_multiplier"])

    @classmethod
    def get_beef_calving_month(cls) -> int:
        """Return the calving month implied by the breeding season start day.

        Returns
        -------
        int
            Calendar month (1-12) in which the calving season opens, derived as
            ``beef_breeding_season_start_day + BEEF_GESTATION_LENGTH_DAYS``
            wrapped into a single year.

        Notes
        -----
        Nothing is stored for the calving month; only
        ``beef_breeding_season_start_day`` is held, so the two cannot
        desynchronise.

        Month-to-day is one-to-many. The setter maps month M to the first
        day of M, so month -> day -> month round-trips losslessly, while
        day -> month -> day snaps to the month start. Expected behaviour for
        a coarsening accessor.

        """
        calving_day = cls.beef_breeding_season_start_day + AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
        return cls._month_of_year_day(((calving_day - 1) % GeneralConstants.YEAR_LENGTH) + 1)

    @classmethod
    def set_beef_calving_month(cls, month: int) -> None:
        """Set the calving month by moving the breeding season start day.

        Parameters
        ----------
        month : int
            Calendar month (1-12) in which the calving season should open.

        Raises
        ------
        ValueError
            If ``month`` is outside 1-12.

        Notes
        -----
        Writes only ``beef_breeding_season_start_day``; nothing of its own is
        retained, so the two values cannot desynchronise.

        Month-to-day is one-to-many. The setter maps month M to the first
        day of M, so month -> day -> month round-trips losslessly, while
        day -> month -> day snaps to the month start. Expected behaviour for
        a coarsening accessor.

        """
        if not isinstance(month, int) or month < 1 or month > _MONTHS_IN_YEAR:
            raise ValueError(f"calving_month must be an integer in 1-12, got {month}")
        calving_day = cls._first_year_day_of_month(month)
        breeding_day = calving_day - AnimalModuleConstants.BEEF_GESTATION_LENGTH_DAYS
        cls.beef_breeding_season_start_day = ((breeding_day - 1) % GeneralConstants.YEAR_LENGTH) + 1

    @staticmethod
    def _first_year_day_of_month(month: int) -> int:
        """Return the 1-based day of a non-leap year on which ``month`` begins."""
        return date(_NON_LEAP_REFERENCE_YEAR, month, 1).timetuple().tm_yday

    @staticmethod
    def _month_of_year_day(year_day: int) -> int:
        """Return the 1-based calendar month containing ``year_day`` in a non-leap year."""
        reference = date(_NON_LEAP_REFERENCE_YEAR, 1, 1) + timedelta(days=year_day - 1)
        return reference.month

    @classmethod
    def _parse_beef_enum_fields(cls, beef_cfg: dict[str, Any]) -> None:
        """Parse and validate post-weaning destination and reproduction program enums.

        Parameters
        ----------
        beef_cfg : dict[str, Any]
            Raw ``beef_cow_calf`` sub-dict.
        """
        destination_str = str(beef_cfg.get("post_weaning_destination") or BeefPostWeaningDestination.SELL.value)
        try:
            cls.beef_post_weaning_destination = BeefPostWeaningDestination(destination_str)
        except ValueError:
            valid = sorted(d.value for d in BeefPostWeaningDestination)
            raise ValueError(
                f"Invalid beef post-weaning destination '{destination_str}'. Expected one of: {valid}."
            ) from None
        reproduction_program_str = str(
            beef_cfg.get("reproduction_program", BeefReproductionProtocol.NATURAL_SERVICE_SEASONAL.value)
        )
        try:
            cls.beef_reproduction_program = BeefReproductionProtocol(reproduction_program_str)
        except ValueError:
            valid = sorted(p.value for p in BeefReproductionProtocol)
            raise ValueError(
                f"Invalid beef reproduction program '{reproduction_program_str}'. Expected one of: {valid}."
            ) from None
