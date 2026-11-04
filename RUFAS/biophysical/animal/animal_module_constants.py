from types import MappingProxyType

from RUFAS.biophysical.animal.data_types.animal_enums import Sex


class AnimalModuleConstants:
    """
    A class used to store constants related to the animal module.
    """

    DEFAULT_BODY_CONDITION_SCORE_5: float = 3.0
    """
    Score on a scale of 1-5 indicating how fit an animal is. This default is used because the score is neither set nor
    calculated in the Animal module.
    """

    DEFAULT_MAX_STOCKING_DENSITY: float = 1.2
    """The default maximum stocking density for a pen. This value is used when a pen is created dynamically during the
    simulation."""

    DEFAULT_NUM_STALLS: int = 100
    """The default number of stalls to be created in a new pen if no specific value is provided."""

    DEFAULT_NUM_STALLS_FOR_CALF_PEN: int = 110
    """The default number of stalls to be created in a calf pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_PEN: int = 800
    """The default number of stalls to be created in a growing pen."""

    DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN: int = 200
    """The default number of stalls to be created in a close-up pen."""

    DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN: int = 850
    """The default number of stalls to be created in a lactating cow pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN: int = 500
    """The default number of stalls to be created in a combined growing and close-up pen."""

    DEFAULT_DRY_MATTER_INTAKE: float = 10.0
    """Default dry matter intake of a ration when this value is not known for an animal (kg)."""

    DEFAULT_NET_ENERGY_DIET_CONCENTRATION: float = 1.0
    """Default metabolizable energy density of a ration when this value is not known for an animal."""

    DEFAULT_NDF_PERCENTAGE: float = 0.3
    """Percentage of neutral detergent fiber in a ration when this value is not known for an animal."""

    DEFAULT_TDN_PERCENTAGE: float = 0.7
    """Percentage of total digestible nutrition in a ration when this value is not known for an animal."""

    VERTICAL_DIST_TO_MILKING_PARLOR: float = 0.1
    """The default vertical distance from the animal pens to the milking parlor."""

    HORIZONTAL_DIST_TO_MILKING_PARLOR: float = 1.6
    """The default horizontal distance from the animal pens to the milking parlor."""

    DEFAULT_HOUSING_TYPE: str = "open air barn"
    """The default housing type for animals in the simulation."""

    DEFAULT_BEDDING_TYPE: str = "sawdust"
    """The default bedding material used in the pens."""

    DEFAULT_PEN_TYPE: str = "freestall"
    """The default type of pen to be created in the simulation."""

    DEFAULT_MANURE_HANDLER: str = "manual scraping"
    """The default method of manure handling used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_SEPARATOR: str = "screw press"
    """The default manure separator system used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_STORAGE: str = "slurry storage outdoor"
    """The default type of manure storage system used in those pens created dynamically during the simulation."""

    MAXMIMUM_MANURE_DRY_MATTER_CONTENT: float = 0.20
    """The maximum dry matter content for manure produced by all animal classe, fraction."""

    DAILY_MILK_VARIATION_MEAN: float = 0
    """Mean of the daily milk production variation from the estimated milk production, kg/day"""

    DAILY_MILK_VARIATION_STD_DEV: float = 1.0
    """Standard deviation of the daily milk production variation from the estimated milk production, kg/day"""

    MILK_CRUDE_PROTEIN: float = 3.2
    """Milk crude protein content, percentage."""

    MILK_LACTOSE: float = 4.85
    """Milk lactose content, percentage."""

    DMI_CONSTRAINT_FRACTION: float = 0.30
    """The +/- fraction of DMI estimated allowed for ration formulation."""

    DMI_REQUIREMENT_BOOST: float = 1.1
    """The fraction of the dry matter intake requirement used as the basis for
    the inclusion rate bounds in user defined ration formulation method."""

    DMI_RETRY_INCREASE_FACTOR: float = 1.1
    """Multiplier applied to the dry matter intake when a lactating-cow ration retry is warranted."""

    MINIMUM_DMI: float = 1.0
    """Minimum estimated DMI instituted for all animals, kg/day"""

    MINIMUM_DAILY_DMI_RATIO: float = 0.01
    """Minimum estimated DMI (kg/day), as a fraction of body_weight in kg"""

    MINIMUM_DMI_LACT: float = 6.06
    """Minimum pen-level DMI for lactating cows, calculated as an average across the
    literature, kg/day (Appuhamy 2014; Appuhamy 2018; Reed 2015; Nennich 2015)."""

    MINIMUM_DMI_DRY: float = 3.6
    """Minimum pen-level DMI for dry cows, calculated as an average across the
    literature, kg/day (Reed 2015; Nennich 2015)."""

    MINIMUM_DMI_HEIFER: float = 4.17
    """Minimum pen-level DMI for heifers, calculated as an average across the
    literature, kg/day (Reed 2015; Nennich 2015)."""

    MINIMUM_DMI_CALF: float = 2.38
    """Minimum pen-level DMI for calves, calculated as an average across the
    literature, kg/day (Nennich 2015)."""

    MINIMUM_DMI_LACT_FOR_MANURE_VS: float = 7.1
    """Minimum DMI for lactating cows in the dataset used to generate the equation,
    kg/day (Appuhamy 2018)."""

    MINIMUM_DMI_DRY_FOR_MANURE_VS: float = 7.1
    """Minimum DMI for dry cows in the dataset used to generate the equation,
    kg/day (Appuhamy 2018)."""

    MINIMUM_PHOSPHORUS: float = 0.0
    """Minimum phosphorus estimate, g/day"""

    MINIMUM_CALCIUM: float = 0.0
    """Minimum calcium estimate, g/day"""

    MINIMUM_RATION_NDF: float = 25.0
    """Minimum percentage of a pen's ration's dry matter that must be neutral detergent fiber (NDF) (percent)."""

    MAXIMUM_RATION_NDF: float = 45.0
    """Maximum percentage of a pen's ration's dry matter that must be NDF (percent)."""

    MINIMUM_RATION_FORAGE_NDF: float = 15.0
    """Minimum percentage of a pen's ration's dry matter that must be NDF from forages (percent)."""

    MAXIMUM_RATION_FAT: float = 7.0
    """Maximum percentage of a ration's dry matter that must be fat (percent)."""

    MILK_REDUCTION_KG: float = 0.25
    """Milk reduction amount for each failed ration optimization attempt, kg"""

    MINIMUM_HEIFER_DAILY_GROWTH_RATE: float = 0.5
    """Minimum daily growth for heifers, kg."""

    PROTEIN_UPPER_LIMIT_FACTOR: float = 1.5
    """Factor used to generate the upper limit for metabolizable protein content in ration formulation."""

    MINIMUM_AVG_PEN_MILK: float = 15
    """Minimum allowable average milk production, for a given pen, as used in ration formulation, kg/animal"""

    MINIMUM_TDN_DISCOUNT: float = 0.6
    """Minimum allowable TDN discount for use in energetic calculations, unitless."""

    EFF_OF_ME_USE: float = 0.66
    """Efficiency of metabolizable energy use, e.g. conversion rate of metabolizable energy to net energy, unitless."""

    # ── FEEDLOT CONSTANTS (NRC 2016 Beef) ────────────────────────────────────
    FEEDLOT_MIN_DMI_RATIO: float = 0.015
    """Minimum DMI as a fraction of body weight for yearling feedlot cattle (kg DMI / kg BW)."""

    STEP_UP_STARTER_END_DAY: int = 7
    """Days on feed at which the starter phase ends (days 1–7)."""

    STEP_UP_TRANSITION_END_DAY: int = 21
    """Days on feed at which the transition phase ends (days 8–21)."""

    RECEIVING_PERIOD_DAYS: int = 21
    """Length of the receiving period during which DMI is reduced post-arrival."""

    RECEIVING_DMI_FRACTION: float = 0.60
    """Fraction of normal DMI consumed during the receiving stress period."""

    MUD_NEm_MULTIPLIER_NONE: float = 1.00
    """NEm multiplier for no mud condition (NRC 2016 Ch. 11)."""

    MUD_NEm_MULTIPLIER_MILD: float = 1.08
    """NEm multiplier for mild mud condition — ankle-deep (NRC 2016 Ch. 11)."""

    MUD_NEm_MULTIPLIER_SEVERE: float = 1.30
    """NEm multiplier for severe mud condition — knee-deep (NRC 2016 Ch. 11)."""

    DEFAULT_IMPLANT_ADG_FACTOR: float = 1.0
    """ADG multiplier for growth implants (1.0 = no implant)."""

    BREED_NEm_MULTIPLIER: dict[str, float] = {
        # NRC 2016 Table 19-1 (BE factor) — all 31 breeds, plus "Crossbred" fallback.
        # British beef breeds = 1.0. High-milk dairy/dual-purpose = 1.2.
        # Bos indicus and composites (Brahman, Canchim, Gir, Guzerat, Sahiwal) = 0.9.
        # Bos indicus composites (Braford, Brangus, Santa Gertrudis) = 0.95.
        # Note: NRC 2016 changed Nellore from 0.9 (NRC 2000) to 1.0 — do NOT use 0.9.
        "Angus": 1.0,
        "Braford": 0.95,
        "Brahman": 0.9,
        "Brangus": 0.95,
        "Braunvieh": 1.2,
        "Canchim": 0.9,
        "Charolais": 1.0,
        "Chianina": 1.0,
        "Crossbred": 1.0,
        "Devon": 1.0,
        "Galloway": 1.0,
        "Gelbvieh": 1.0,
        "Gir": 0.9,
        "Guzerat": 0.9,
        "Hereford": 1.0,
        "Holstein": 1.2,
        "Jersey": 1.2,
        "Limousin": 1.0,
        "Longhorn": 1.0,
        "Maine Anjou": 1.0,
        "Nellore": 1.0,
        "Piedmontese": 1.0,
        "Pinzgauer": 1.0,
        "Polled Hereford": 1.0,
        "Red Poll": 1.0,
        "Sahiwal": 0.9,
        "Salers": 1.0,
        "Santa Gertrudis": 0.95,
        "Shorthorn": 1.0,
        "Simmental": 1.2,
        "South Devon": 1.0,
        "Tarentaise": 1.0,
    }
    """NRC 2016 Table 19-1 breed maintenance multipliers (BE factor)."""

    SEX_NEm_MULTIPLIER: dict[Sex, float] = {
        Sex.STEER: 1.00,
        Sex.FEMALE: 1.00,
        Sex.MALE: 1.15,
    }
    """NRC 2016 Table 19-1 sex maintenance multipliers. Bulls 15% higher; steers/heifers = 1.0."""

    SRW_CHOICE: int = 478
    """Standard reference weight (SBW, kg) for Small/Choice marbling grade — NRC 2016 Table 12-2 default."""

    DEFAULT_NUM_STALLS_FOR_FEEDLOT_PEN: int = 100
    """The default number of stalls to be created in a feedlot finishing pen."""

    FEEDLOT_HCW_DRESSING_PERCENTAGE: float = 0.62
    """NRC 2016 typical Choice-grade dressing percentage for hot carcass weight calculation."""

    # ── COW-CALF CONSTANTS (NRC 2016 Beef Ch.13, USDA surveys) ───────────────

    BEEF_GESTATION_LENGTH_DAYS: int = 283
    """NRC 2016 average beef gestation length (days)."""

    BEEF_CALF_CROP_WEANED_RATE: float = 0.855
    """USDA NASS average calf crop weaned per cow exposed (unitless)."""

    BEEF_STILLBIRTH_RATE: float = 0.035
    """3.5% stillbirth rate; 96.5% of calves born alive (USDA 2009a)."""

    BEEF_PREWEANING_SURVIVAL_RATE: float = 0.968
    """96.8% of live calves survive to weaning (USDA 2009a)."""

    BEEF_DEFAULT_WEANING_AGE_DAYS: int = 207
    """USDA NASS average weaning age for beef calves (days)."""

    BEEF_DEFAULT_WEANING_WEIGHT_KG: float = 240.0
    """USDA NASS average weaning weight for beef calves (kg)."""

    BEEF_PREWEANING_ADG_KG_D: float = 1.0
    """NRC 2016 reference average daily gain for nursing beef calves (kg/d)."""

    BEEF_CALF_BIRTH_WEIGHT_KG: float = 35.0
    """NRC 2016 reference average birth weight for beef calves (kg)."""

    BEEF_DEFAULT_MATURE_COW_WEIGHT_KG: float = 520.0
    """USDA NASS average mature beef cow weight at weaning (kg)."""

    BEEF_COW_FORAGE_DMI_PCT_BW: float = 0.0225
    """NRC 2016 Ch.10: forage DMI as fraction of BW for a cow in moderate condition (2.25%)."""

    BEEF_PREWEANING_CALF_DMI_PCT_BW: float = 0.0125
    """NRC 2016 approximate preweaning forage intake as fraction of BW (1.25%)."""

    BEEF_HEIFER_TARGET_BREEDING_PCT_MATURE: float = 0.60
    """NRC 2016: replacement heifers should reach 55–65% of mature weight by first breeding (midpoint 60%)."""

    BEEF_HEIFER_TARGET_CALVING_PCT_MATURE: float = 0.80
    """NRC 2016: replacement heifers should reach ~80% of mature weight by first calving."""

    BEEF_HEIFER_TARGET_ADG_KG_D: float = 0.675
    """NRC 2016: target ADG for replacement heifer development (midpoint of 0.45–0.90 kg/d range)."""

    BEEF_HEIFER_FIRST_CALVING_AGE_DAYS: int = 690
    """NRC 2016: target first calving age of 22–24 months; midpoint ~23 months = 690 days."""

    BEEF_ANNUAL_CULL_RATE: float = 0.175
    """USDA national average annual beef cow cull rate (midpoint of 15–20% range)."""

    BEEF_COW_MAX_AGE_DAYS: int = 5475
    """Conservative longevity ceiling of 15 years = 5475 days."""

    BEEF_POSTPARTUM_ANESTRUS_DAYS: int = 45
    """Minimum days postpartum before a cow resumes cycling (NRC 2016 Ch.13)."""

    BEEF_CONCEPTION_BASE_DAILY_PROB: float = 0.0404
    """Base daily conception probability calibrated to USDA 91.5% seasonal pregnancy rate at BCS=5, 25:1 bull ratio."""

    BEEF_CONCEPTION_BULL_RATIO_REFERENCE: float = 30.0
    """Bull-to-cow ratio above which bull coverage capacity constrains conception (NRC 2016 Ch.13)."""

    BEEF_CONCEPTION_BCS_DIVISOR: float = 4.0
    """BCS normalization divisor mapping the 1-9 scale to a [0, 1] factor (NRC 2016 Ch.13 qualitative guidance)."""

    BEEF_CONCEPTION_BCS_FLOOR: float = 0.5
    """Minimum BCS factor retained by severely thin cows; pragmatic floor, not a specific NRC 2016 equation."""

    BEEF_DEFAULT_BREEDING_SEASON_LENGTH_DAYS: int = 63
    """Standard 9-week (63-day) breeding season per NRC 2016 management reference."""

    BEEF_DEFAULT_NATURAL_SERVICE_BULL_RATIO: int = 25
    """Default bulls-per-cow ratio for natural service breeding (industry standard 25:1)."""

    BEEF_DEFAULT_BREEDING_SEASON_START_DAY: int = 90
    """Default Julian day on which the breeding season opens (approximately April 1)."""

    # ===== NAMED SCENARIO DEFAULTS =====
    # Starting points for the pre-built comparison scenarios. These are
    # management choices being compared, not measured biological values, and
    # carry no NRC 2016 or USDA citation.

    BEEF_SCENARIO_SPRING_CALVING_MONTH: int = 4
    """Calving month for the spring-calving scenario. A named-scenario default, not a measured value."""

    BEEF_SCENARIO_FALL_CALVING_MONTH: int = 10
    """Calving month for the fall-calving scenario. A named-scenario default, not a measured value."""

    BEEF_SCENARIO_EARLY_WEANING_AGE_DAYS: int = 150
    """
    Weaning age for the early-weaning scenario (days).

    Neither the source document nor the cited literature gives an
    early-weaning age in days — the source specifies only whole months
    (5). 150 is a round figure chosen for that reason, roughly two months
    ahead of BEEF_DEFAULT_WEANING_AGE_DAYS (207), which it is defined
    against rather than derived from. A named-scenario default, not a
    measured value.
    """

    CG_RESTRICTION_THRESHOLD_DAYS: int = 21
    """
    Days of restricted intake that must be exceeded before compensatory gain
    triggers. A restriction of exactly this length produces no uplift.

    Value as specified by the BeefGEM source document
    (docs/beef_module/beefgem/RuFaS_BeefGEM_Source_Reference.md, Step D-2),
    which gives no primary citation for it.
    """

    CG_MAX_ADG_MULTIPLIER: float = 1.25
    """
    Ceiling on the compensatory gain ADG multiplier, for biological
    plausibility. Applied both when the factor is set and again inside the
    calculators, so a caller-supplied factor cannot exceed it either.

    Value as specified by the BeefGEM source document
    (docs/beef_module/beefgem/RuFaS_BeefGEM_Source_Reference.md, Step D-2),
    which gives no primary citation for it.
    """

    CG_DECAY_RATE_PER_DAY: float = 0.02
    """
    Decline in the compensatory gain advantage per day once restriction ends,
    in multiplier units. A factor at the 1.25 ceiling returns to 1.0 after 13
    days.

    Value as specified by the BeefGEM source document
    (docs/beef_module/beefgem/RuFaS_BeefGEM_Source_Reference.md, Step D-2),
    which gives no primary citation for it.
    """

    CG_ADG_MULTIPLIER_PER_RESTRICTED_DAY: float = 0.005
    """
    Uplift added to the ADG multiplier for each restricted day beyond
    CG_RESTRICTION_THRESHOLD_DAYS.

    This coefficient has no identified source. The BeefGEM source document
    states only that the factor is set from the restricted-day count "via a
    lookup table" and never provides that table; 0.005 is a linearisation
    adopted in the implementation plan. It should not be treated as
    BeefGEM- or NRC-derived without re-derivation.
    """

    BEEF_THI_HUMIDITY_INTERCEPT: float = 0.55
    """
    Intercept of the humidity term of the temperature-humidity index,
    THI = T_F - (0.55 - 0.0055 x RH) x (T_F - 58) (unitless). Source as cited
    by BeefNRCRequirementsCalculator.calculate_thi (NRC 2016 Ch. 11).
    """

    BEEF_THI_HUMIDITY_SLOPE: float = 0.0055
    """
    Slope of the humidity term of the temperature-humidity index, per
    percentage point of relative humidity (1/%). Same equation and source as
    BEEF_THI_HUMIDITY_INTERCEPT.
    """

    BEEF_THI_REFERENCE_TEMPERATURE_F: float = 58.0
    """
    Reference temperature subtracted from the dry-bulb temperature in the
    temperature-humidity index (°F). Same equation and source as
    BEEF_THI_HUMIDITY_INTERCEPT. In Celsius terms the bracket T_F - 58 equals
    1.8 x T - 26.
    """

    BEEF_THI_BREAKPOINTS: tuple[float, ...] = (72.0, 80.0, 90.0)
    """
    THI anchor points for beef cattle heat stress interpolation. 72 is the
    onset of stress, 80 the moderate class value, 90 the severe. Pairs
    one-to-one with BEEF_HEAT_STRESS_DMI_MULTIPLIERS and
    BEEF_HEAT_STRESS_NEM_MULTIPLIERS.
    """

    BEEF_HEAT_STRESS_DMI_MULTIPLIERS: tuple[float, ...] = (1.00, 0.88, 0.75)
    """
    DMI multiplier at each THI anchor point. Below 72 no reduction applies;
    above 90 the value is clamped. The source document reports these as
    discrete classes; they are interpolated linearly between anchors here so
    daily output is continuous and animals crossing a threshold do not
    produce step artefacts.

    The source's mild-class value of 0.95 is deliberately not an anchor.
    Pinning it at 72 would put a five-point cliff at the onset; it instead
    falls out of the interpolation at THI 75.33, inside the mild band.
    """

    BEEF_HEAT_STRESS_NEM_MULTIPLIERS: tuple[float, ...] = (1.00, 1.12, 1.20)
    """
    Maintenance energy multiplier at each THI anchor point. Same
    interpolation treatment as the DMI multipliers; the source's mild-class
    value of 1.07 falls out at THI 76.67, inside the mild band.
    """

    BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER: float = 1.15
    """
    Scenario lever scaling the calibrated base daily conception
    probability. Not a measured rate. At the calibration reference point
    (BCS 5, 25:1 bull ratio) both adjustment factors are 1.0, so the
    seasonal rate over the 63-day season is 1 - (1 - 0.0404 x m)^63.
    A multiplier of 1.15 yields 95.0%; 0.625 yields 80.0%; the baseline
    1.0 yields 92.56%.

    Note: BEEF_CONCEPTION_BASE_DAILY_PROB documents itself as calibrated
    to a USDA 91.5% seasonal pregnancy rate. The value it actually
    produces at the reference point is 92.56%, a gap of 1.1 percentage
    points. The constant is left unchanged, as altering it would move
    existing cow-calf output.
    """

    BEEF_SCENARIO_LOW_CONCEPTION_MULTIPLIER: float = 0.625
    """
    Scenario lever scaling the calibrated base daily conception
    probability down to an 80.0% seasonal rate. Not a measured rate. Same
    derivation as BEEF_SCENARIO_HIGH_CONCEPTION_MULTIPLIER.
    """

    BEEF_SCENARIO_AGGRESSIVE_CULL_RATE: float = 0.22
    """Annual cow cull fraction for the aggressive-culling scenario. A named-scenario default."""

    BEEF_DEFAULT_BCS_9: float = 5.0
    """Default moderate body condition score on the NRC 2016 beef 1–9 scale (not the dairy 1–5 scale)."""

    # ── COW-CALF BREED TABLE (NRC 2016 Table 19-1 — all 31 breeds) ───────────

    BREED_L_FACTOR: MappingProxyType[str, float] = MappingProxyType(
        {
            # Lactation factor (L) used in NEm = SBW^0.75 × (a1 × BE × L × COMP × SEX + a2).
            # L = 1.0 for non-lactating animals and for high-milk dairy/dual-purpose breeds.
            # L = 1.2 for British and Bos indicus beef breeds during lactation.
            # NRC 2016 Table 19-1.
            "Angus": 1.2,
            "Braford": 1.2,
            "Brahman": 1.2,
            "Brangus": 1.2,
            "Braunvieh": 1.0,
            "Canchim": 1.2,
            "Charolais": 1.2,
            "Chianina": 1.2,
            "Devon": 1.0,
            "Galloway": 1.2,
            "Gelbvieh": 1.0,
            "Gir": 1.2,
            "Guzerat": 1.2,
            "Hereford": 1.0,
            "Holstein": 1.0,
            "Jersey": 1.0,
            "Limousin": 1.2,
            "Longhorn": 1.2,
            "Maine Anjou": 1.2,
            "Nellore": 1.2,
            "Piedmontese": 1.2,
            "Pinzgauer": 1.2,
            "Polled Hereford": 1.2,
            "Red Poll": 1.2,
            "Sahiwal": 1.2,
            "Salers": 1.2,
            "Santa Gertrudis": 1.2,
            "Shorthorn": 1.2,
            "Simmental": 1.0,
            "South Devon": 1.2,
            "Tarentaise": 1.2,
        }
    )
    """NRC 2016 Table 19-1 lactation adjustment factor (L) for NEm. L=1.0 for non-lactating animals."""

    BREED_CBW_KG: MappingProxyType[str, float] = MappingProxyType(
        {
            # Calf birth weight (kg) by breed — NRC 2016 Table 19-1.
            # Used in gestation energy (Eq.19-37) and gravid uterus weight (Eq.19-69).
            "Angus": 31.0,
            "Braford": 36.0,
            "Brahman": 31.0,
            "Brangus": 33.0,
            "Braunvieh": 39.0,
            "Canchim": 32.0,
            "Charolais": 39.0,
            "Chianina": 41.0,
            "Devon": 32.0,
            "Galloway": 36.0,
            "Gelbvieh": 39.0,
            "Gir": 32.0,
            "Guzerat": 32.0,
            "Hereford": 36.0,
            "Holstein": 43.0,
            "Jersey": 32.0,
            "Limousin": 37.0,
            "Longhorn": 33.0,
            "Maine Anjou": 40.0,
            "Nellore": 32.0,
            "Piedmontese": 38.0,
            "Pinzgauer": 38.0,
            "Polled Hereford": 33.0,
            "Red Poll": 36.0,
            "Sahiwal": 38.0,
            "Salers": 35.0,
            "Santa Gertrudis": 33.0,
            "Shorthorn": 37.0,
            "Simmental": 39.0,
            "South Devon": 33.0,
            "Tarentaise": 33.0,
        }
    )
    """NRC 2016 Table 19-1 calf birth weight (kg) by breed. Fallback: BEEF_CALF_BIRTH_WEIGHT_KG."""

    BREED_PEAK_MILK_YIELD_KG_D: MappingProxyType[str, float] = MappingProxyType(
        {
            # Peak milk yield (kg/d) for the Wood lactation curve — NRC 2016 Table 19-1.
            "Angus": 8.0,
            "Braford": 7.0,
            "Brahman": 8.0,
            "Brangus": 8.0,
            "Braunvieh": 12.0,
            "Canchim": 6.0,
            "Charolais": 9.0,
            "Chianina": 6.0,
            "Devon": 8.0,
            "Galloway": 8.0,
            "Gelbvieh": 11.5,
            "Gir": 10.0,
            "Guzerat": 5.0,
            "Hereford": 7.0,
            "Holstein": 43.0,
            "Jersey": 34.0,
            "Limousin": 9.0,
            "Longhorn": 5.0,
            "Maine Anjou": 9.0,
            "Nellore": 7.0,
            "Piedmontese": 7.0,
            "Pinzgauer": 11.0,
            "Polled Hereford": 7.0,
            "Red Poll": 10.0,
            "Sahiwal": 8.0,
            "Salers": 9.0,
            "Santa Gertrudis": 8.0,
            "Shorthorn": 8.5,
            "Simmental": 12.0,
            "South Devon": 8.0,
            "Tarentaise": 9.0,
        }
    )
    """NRC 2016 Table 19-1 breed peak milk yield (PKYD, kg/d) for Wood lactation curve."""

    BREED_MILK_FAT_PCT: MappingProxyType[str, float] = MappingProxyType(
        {
            # Milk fat percentage by breed — NRC 2016 Table 19-1.
            "Angus": 4.0,
            "Braford": 4.0,
            "Brahman": 4.0,
            "Brangus": 4.0,
            "Braunvieh": 4.0,
            "Canchim": 4.0,
            "Charolais": 4.0,
            "Chianina": 4.0,
            "Devon": 3.5,
            "Galloway": 4.0,
            "Gelbvieh": 4.0,
            "Gir": 4.0,
            "Guzerat": 4.0,
            "Hereford": 4.0,
            "Holstein": 3.5,
            "Jersey": 5.2,
            "Limousin": 4.0,
            "Longhorn": 4.0,
            "Maine Anjou": 4.0,
            "Nellore": 4.0,
            "Piedmontese": 4.0,
            "Pinzgauer": 4.0,
            "Polled Hereford": 4.0,
            "Red Poll": 4.0,
            "Sahiwal": 4.0,
            "Salers": 4.0,
            "Santa Gertrudis": 4.0,
            "Shorthorn": 4.0,
            "Simmental": 4.0,
            "South Devon": 4.0,
            "Tarentaise": 4.0,
        }
    )
    """NRC 2016 Table 19-1 milk fat percentage by breed."""

    BREED_MILK_PROTEIN_PCT: MappingProxyType[str, float] = MappingProxyType(
        {
            # Milk protein percentage by breed — NRC 2016 Table 19-1.
            "Angus": 3.8,
            "Braford": 3.8,
            "Brahman": 3.8,
            "Brangus": 3.8,
            "Braunvieh": 3.8,
            "Canchim": 3.8,
            "Charolais": 3.8,
            "Chianina": 3.8,
            "Devon": 3.3,
            "Galloway": 3.8,
            "Gelbvieh": 3.8,
            "Gir": 3.8,
            "Guzerat": 3.8,
            "Hereford": 3.8,
            "Holstein": 3.3,
            "Jersey": 3.9,
            "Limousin": 3.8,
            "Longhorn": 3.8,
            "Maine Anjou": 3.8,
            "Nellore": 3.8,
            "Piedmontese": 3.8,
            "Pinzgauer": 3.8,
            "Polled Hereford": 3.8,
            "Red Poll": 3.8,
            "Sahiwal": 3.8,
            "Salers": 3.8,
            "Santa Gertrudis": 3.8,
            "Shorthorn": 3.8,
            "Simmental": 3.8,
            "South Devon": 3.8,
            "Tarentaise": 3.8,
        }
    )
    """NRC 2016 Table 19-1 milk protein percentage by breed."""

    BREED_MILK_SNF_PCT: MappingProxyType[str, float] = MappingProxyType(
        {
            # Milk solids-not-fat (SNF) percentage by breed — NRC 2016 Table 19-1.
            # All breeds report 8.3% SNF in Table 19-1.
            "Angus": 8.3,
            "Braford": 8.3,
            "Brahman": 8.3,
            "Brangus": 8.3,
            "Braunvieh": 8.3,
            "Canchim": 8.3,
            "Charolais": 8.3,
            "Chianina": 8.3,
            "Devon": 8.3,
            "Galloway": 8.3,
            "Gelbvieh": 8.3,
            "Gir": 8.3,
            "Guzerat": 8.3,
            "Hereford": 8.3,
            "Holstein": 8.3,
            "Jersey": 8.3,
            "Limousin": 8.3,
            "Longhorn": 8.3,
            "Maine Anjou": 8.3,
            "Nellore": 8.3,
            "Piedmontese": 8.3,
            "Pinzgauer": 8.3,
            "Polled Hereford": 8.3,
            "Red Poll": 8.3,
            "Sahiwal": 8.3,
            "Salers": 8.3,
            "Santa Gertrudis": 8.3,
            "Shorthorn": 8.3,
            "Simmental": 8.3,
            "South Devon": 8.3,
            "Tarentaise": 8.3,
        }
    )
    """NRC 2016 Table 19-1 milk solids-not-fat (SNF) percentage by breed. All breeds: 8.3%."""

    WOOD_PEAK_WEEK: int = 8
    """Default week of peak milk yield (T) in the Wood lactation curve — NRC 2016 Ch.19."""

    WOOD_FIRST_CALF_AGE_FACTOR: float = 0.85
    """Wood curve age factor for first-calf heifers (parity == 1) — NRC 2016 Ch.19 Eq.19-22."""

    WOOD_MATURE_AGE_FACTOR: float = 1.0
    """Wood curve age factor for mature cows (parity >= 2) — NRC 2016 Ch.19 Eq.19-22."""

    BEEF_LACTATION_MP_EFFICIENCY: float = 0.65
    """Efficiency of MP use for lactation (and pregnancy) — NRC 2016 Ch.19 Eq.19-28, 19-41."""

    BEEF_PREGNANCY_NE_EFFICIENCY: float = 0.13
    """Efficiency of ME→NE for pregnancy (ky) — NRC 2016 Ch.19 Eq.19-38. Fixed constant."""

    BEEF_DMI_COW_NE_QUAD: float = 0.04997
    """Quadratic NEm coefficient for Eq.10-5 beef cow DMI — NRC 2016 Ch.10."""

    BEEF_DMI_COW_NE_LINEAR: float = 0.04631
    """Linear NEm coefficient for Eq.10-5 beef cow DMI (pregnant/all-cow term) — NRC 2016 Ch.10."""

    BEEF_DMI_COW_INTERCEPT_NP: float = 0.03840
    """Intercept addition to Eq.10-5 for NON-PREGNANT cows only — NRC 2016 Ch.10."""

    BEEF_DMI_COW_LACT_ADJUST: float = 0.2
    """Lactation DMI adjustment factor: +0.2 × Yn (kg milk/d) added to cow DMI — NRC 2016 Ch.10."""

    BEEF_CA_MAINT_COEFF: float = 0.0308
    """Dietary Ca for maintenance: 0.0308 × SBW g/d (= 0.0154/0.50) — NRC 2016 Table 19-3."""

    BEEF_CA_GROWTH_COEFF: float = 0.142
    """Dietary Ca for growth: 0.142 × NPg g/d (= 0.071/0.50) — NRC 2016 Table 19-3."""

    BEEF_CA_LACT_COEFF: float = 2.46
    """Dietary Ca for lactation: 2.46 × Yn g/d (= 1.23/0.50) — NRC 2016 Table 19-3."""

    BEEF_CA_PREG_COEFF: float = 0.3044
    """Dietary Ca for pregnancy: 0.3044 × CBW g/d (= 13.7/90/0.50, last 90d) — NRC 2016 Table 19-3."""

    BEEF_P_MAINT_COEFF: float = 0.02353
    """Dietary P for maintenance: 0.02353 × SBW g/d (= 0.016/0.68) — NRC 2016 Table 19-3."""

    BEEF_P_GROWTH_COEFF: float = 0.05735
    """Dietary P for growth: 0.05735 × NPg g/d (= 0.039/0.68) — NRC 2016 Table 19-3."""

    BEEF_P_LACT_COEFF: float = 1.397
    """Dietary P for lactation: 1.397 × Yn g/d (= 0.95/0.68) — NRC 2016 Table 19-3."""

    BEEF_P_PREG_COEFF: float = 0.1242
    """Dietary P for pregnancy: 0.1242 × CBW g/d (= 7.6/90/0.68, last 90d) — NRC 2016 Table 19-3."""

    BEEF_PREG_LAST_DAYS: int = 90
    """Number of final gestation days during which mineral deposition for pregnancy is active — NRC 2016 Table 19-3."""

    # ===== STOCKER / BACKGROUNDING CONSTANTS (NRC 2016 Ch.10-12) =====

    STOCKER_MIN_ENTRY_WEIGHT_KG: float = 180.0
    """Minimum weaning weight for stocker placement (NRC 2016)."""

    STOCKER_TARGET_EXIT_WEIGHT_KG: float = 350.0
    """NRC 2016: feedlot entry typically 300-400 kg; 350 kg midpoint default."""

    STOCKER_TARGET_ADG_KG_D: float = 0.80
    """NRC 2016 Ch.10: mid-range of 0.35-1.15 kg/d on forage-based diet."""

    STOCKER_MAX_DAYS: int = 210
    """Maximum backgrounding days before forced exit."""

    STOCKER_DEFAULT_LIMIT_FEED_PCT: float = 85.0
    """
    Default dry matter intake ceiling when the stocker diet system is limit-feeding,
    as a percentage of ad libitum intake. BeefGEM source document; not an NRC 2016
    threshold. Limit-feeding programmes in the literature span roughly 80-90% of
    ad libitum, and 85% is the midpoint of that range.
    """

    BEEF_MUD_CONDITION_NONE: str = "none"
    """NRC 2016 mud condition: no mud, multiplier = 1.00 (MUD_NEm_MULTIPLIER_NONE)."""

    BEEF_MUD_CONDITION_MILD: str = "mild"
    """NRC 2016 mud condition: mild mud, multiplier = 1.08 (MUD_NEm_MULTIPLIER_MILD)."""

    BEEF_MUD_CONDITION_SEVERE: str = "severe"
    """NRC 2016 mud condition: severe mud, multiplier = 1.30 (MUD_NEm_MULTIPLIER_SEVERE)."""

    BEEF_DMI_MIN_NE_CONCENTRATION: float = 0.95
    """Minimum NEm concentration (Mcal/kg DM) applied before division in DMI Eq.10-5.
    This is a numerical guard against a near-zero denominator, not an NRC 2016 threshold."""

    # ===== BEEF FINISHING ENTERIC CH4 CONSTANTS (NRC 2016 Ch.16) =====

    BEEF_CH4_GRASS_FED_INTERCEPT: float = 8.25
    """
    Linear enteric CH4 model for grass-finished beef: intercept (g CH4/d). Distinct
    from the Mitscherlich Model 3 curve (MITS_PARAMETER_A/_B, Mills et al. 2003)
    already in animal_constants.py, despite the source document referring to this
    as "Mits3". Provenance for these coefficients is the BeefGEM source document;
    no NRC 2016 equation number has been identified for them.
    """

    BEEF_CH4_GRASS_FED_SLOPE: float = 31.2
    """
    Linear enteric CH4 model for grass-finished beef: slope (g CH4 per kg DMI/d).
    Distinct from the Mitscherlich Model 3 curve (MITS_PARAMETER_A/_B, Mills et al.
    2003) already in animal_constants.py, despite the source document referring to
    this as "Mits3". Provenance for these coefficients is the BeefGEM source
    document; no NRC 2016 equation number has been identified for them.
    """

    BEEF_CH4_STOCKER_FORAGE_INTERCEPT: float = 10.04
    """
    Intercept of the linear enteric CH4 model for stocker cattle on forage
    (g CH4/d). Pinned from the BeefGEM implementation plan. No NRC/NASEM 2016
    equation number has been identified for this pair: the plan cites
    "Eq.6.8", but Chapter 6 of NRC 2016 covers protein and amino acids, and
    the enteric methane equations are Ch.16 (Eq.16-8 and Eq.16-9). The BeefGEM
    source document's own backgrounding rule R-CH4-ENT-003 is Eq.16-8,
    71.5 + 0.12*BW + 0.10*DMI^3 - 244.8*Fat^3, which is a different equation
    taking four inputs. Retained as pinned for traceability; see the module
    docs for the open provenance question.
    """

    BEEF_CH4_STOCKER_FORAGE_SLOPE: float = 23.7
    """
    Slope of the linear enteric CH4 model for stocker cattle on forage
    (g CH4 per kg DMI/d). Same provenance caveat as
    BEEF_CH4_STOCKER_FORAGE_INTERCEPT. Across 6-10 kg DM/d the pair yields
    152-247 g/d, inside the 87-252 g/d NRC 2016 Ch.16 reports for grazing
    beef cattle; it exceeds that ceiling above roughly 10.2 kg DM/d.
    """

    BEEF_CH4_YM_FRACTION: float = 0.030
    """
    Methane conversion factor for grain-finished feedlot cattle, as a
    fraction of gross energy intake. IPCC Tier 2 default for high-grain
    diets; NRC 2016 Table 16-2.
    """

    BEEF_GROSS_ENERGY_MJ_PER_KG_DM: float = 18.45
    """
    Gross energy content of feed dry matter (MJ/kg DM). IPCC default
    used with BEEF_CH4_YM_FRACTION.
    """
    HEIFER_MORTALITY_HEIFERI_FRACTION: float = 2 / 3
    """Fraction of post-wean (heifer) mortality allocated to the HeiferI (pre-breeding) stage.
    The remaining (1 - fraction) is allocated to the HeiferII (post-breeding) stage. Per SME
    guidance, two-thirds of youngstock losses occur before breeding and one-third after, unitless."""
