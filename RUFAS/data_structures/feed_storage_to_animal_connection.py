from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from enum import Enum

from RUFAS.units import MeasurementUnits

"""
Every feed in RuFaS has a unique integer ID. They are defined in the Feed Library file used, and are used throughout
other input files and the RuFaS codebase.
"""
RUFAS_ID = int


class FeedCategorization(Enum):
    """NASEM and NRC categorizations of feeds."""

    ANIMAL_PROTEIN = "Animal Protein"
    BY_PRODUCT_OTHER = "By-Product/Other"
    CALF_LIQUID_FEED = "Calf Liquid Feed"
    ENERGY_SOURCE = "Energy Source"
    FAT_SUPPLEMENT = "Fat Supplement"
    FATTY_ACID_SUPPLEMENT = "Fatty Acid Supplement"
    GRAIN_CROP_FORAGE = "Grain Crop Forage"
    GRASS_LEGUME_FORAGE = "Grass/Legume Forage"
    PASTURE = "Pasture"
    PLANT_PROTEIN = "Plant Protein"
    VITAMIN_MINERAL = "Vitamin/Mineral"
    NPN_SUPPLEMENT = "NPN Supplement"


class FeedComponentType(Enum):
    """NASEM and NRC types of feeds."""

    AMINOACIDS = "Aminoacids"
    FORAGE = "Forage"
    CONC = "Conc"
    MILK = "Milk"
    MINERAL = "Mineral"
    VITAMINS = "Vitamins"
    STARTER = "Starter"
    NO = "No"


class NutrientStandard(Enum):
    """The nutrient standards supported in RuFaS."""

    NASEM = "NASEM"
    NRC = "NRC"


@dataclass
class Feed:
    """
    Base representation of a feed in RuFaS.

    Attributes
    ----------
    rufas_id : RUFAS_ID
        Unique integer identifier for feeds used within the RuFaS model (unitless).
    Fd_Category : FeedCategorization
        Feed category (unitless).
    feed_type : FeedComponentType
        General type or category of the feed (unitless).
    DM : float
        Percentage of fresh mass that is dry matter of the feed.
    ash : float
        Ash contents (% dry matter).
    CP : float
        Crude protein content of the feed (% dry matter).
    N_A : float
        Nitrogen Fraction A (% crude protein).
    N_B : float
        Nitrogen Fraction B (% crude protein).
    N_C : float
        Nitrogen Fraction C (% crude protein).
    Kd : float
        Feed degradation rate of B fraction (% per hour).
    dRUP : float
        Digested rumen undegradable protein (% of rumen undigestable protein).
    ADICP : float
        Acid detergent insoluble nitrogen multiplied by 6.25 (% dry matter).
    NDICP : float
        Neutral detergent insoluble nitrogen multiplied by 6.25 (% dry matter).
    ADF : float
        Acid detergent fiber (% dry matter).
    NDF : float
        Neutral detergent fiber (% dry matter).
    lignin : float
        Acid detergent lignin (% dry matter).
    starch : float
        Starch (% dry matter).
    EE : float
        Ether extract (% dry matter).
    calcium : float
        Calcium (% dry matter).
    phosphorus : float
        Phosphorus (% dry matter).
    magnesium : float
        Magnesium (% dry matter).
    potassium : float
        Potassium (% dry matter).
    sodium : float
        Sodium (% dry matter).
    chlorine : float
        Chlorine (% dry matter).
    sulfur : float
        Sulphur (% dry matter).
    is_fat : bool
        Identifier of fat type feed (unitless).
    is_wetforage : bool
        Identifier of wet forage type feed (unitless).
    units : MeasurementUnits
        The units with which the feed is measured.
    limit : float
        Upper limit of feed that is allowed to be used in a single animal's diet (kg).
    lower_limit : float
        Lower limit of feed that is allowed to be used in a single animal's diet (kg).
    TDN : float
        Total digestible nutrients (% dry matter).
    DE : float
        Digestible energy (Mcal / kg).
    amount_available : float
        Amount of feed currently or expected to be available (kg).
    on_farm_cost : float
        Price of using the feed that is already on-farm ($ / kg).
    purchase_cost : float
        Price of buying feed from off-farm ($ / kg).
    buffer : float
        Fraction of extra feed purchases to account for shrinkage.

    """

    rufas_id: RUFAS_ID
    Fd_Category: FeedCategorization
    feed_type: FeedComponentType
    DM: float
    ash: float
    CP: float
    N_A: float
    N_B: float
    N_C: float
    Kd: float
    dRUP: float
    ADICP: float
    NDICP: float
    ADF: float
    NDF: float
    lignin: float
    starch: float
    EE: float
    calcium: float
    phosphorus: float
    magnesium: float
    potassium: float
    sodium: float
    chlorine: float
    sulfur: float
    is_fat: bool
    is_wetforage: bool
    units: MeasurementUnits
    limit: float
    lower_limit: float
    TDN: float
    DE: float
    amount_available: float
    on_farm_cost: float
    purchase_cost: float
    buffer: float


@dataclass
class NASEMFeed(Feed):
    """
    NASEM-specific representation of a RuFaS feed.

    Attributes
    ----------
    Name : str
        Feed name (unitless).
    RUP : float
        Rumen undegradable protein (% crude protein).
    sol_prot : float
        Soluble protein (% crude protein).
    NDF48 : float
        In vitro 48-hour digestibility (% Neutral Detergent Fiber).
    WSC : float
        Water soluble carbohydrates (% dry matter).
    FA : float
        Fatty acids (% dry matter).
    DE_Base : float
        Digestible energy standard (Mcal / kg).
    copper : float
    iron : float
    manganese : float
    zinc : float
    molibdenum : float
    chromium : float
    cobalt : float
    iodine : float
    selenium : float
    arginine : float
    histidine : float
    isoleucine : float
    leucine : float
    lysine : float
    methionine : float
    phenylalanine : float
    threonine : float
    triptophan : float
    valine : float
    C120_FA : float
    C140_FA : float
    C160_FA : float
    C161_FA : float
    C180_FA : float
    C181t_FA : float
    C181c_FA : float
    C182_FA : float
    C183_FA : float
    otherFA_FA : float
    NPN_source : float
        Non-protein nitrogen fraction (%).
    starch_digested : float
        Base starch digestibility (%).
    FA_dig : float
    P_inorg : float
    P_org : float
    B_Carotene : float
    biotin : float
    choline : float
    niacin : float
    Vit_A : float
    Vit_D : float
    Vit_E : float
    Abs_calcium : float
    Abs_phosphorus : float
    Abs_sodium : float
    Abs_chloride : float
    Abs_potassium : float
    Abs_copper : float
    Abs_iron : float
    Abs_magnesium : float
    Abs_manganesum : float
    Abs_zinc : float

    """

    Name: str
    RUP: float
    sol_prot: float
    NDF48: float
    WSC: float
    FA: float
    DE_Base: float
    copper: float
    iron: float
    manganese: float
    zinc: float
    molibdenum: float
    chromium: float
    cobalt: float
    iodine: float
    selenium: float
    arginine: float
    histidine: float
    isoleucine: float
    leucine: float
    lysine: float
    methionine: float
    phenylalanine: float
    threonine: float
    triptophan: float
    valine: float
    C120_FA: float
    C140_FA: float
    C160_FA: float
    C161_FA: float
    C180_FA: float
    C181t_FA: float
    C181c_FA: float
    C182_FA: float
    C183_FA: float
    otherFA_FA: float
    NPN_source: float
    starch_digested: float
    FA_dig: float
    P_inorg: float
    P_org: float
    B_Carotene: float
    biotin: float
    choline: float
    niacin: float
    Vit_A: float
    Vit_D: float
    Vit_E: float
    Abs_calcium: float
    Abs_phosphorus: float
    Abs_sodium: float
    Abs_chloride: float
    Abs_potassium: float
    Abs_copper: float
    Abs_iron: float
    Abs_magnesium: float
    Abs_manganesum: float
    Abs_zinc: float


@dataclass
class NRCFeed(Feed):
    """
    NRC-specific representation of a RuFaS feed.

    Attributes
    ----------
    non_fiber_carb : float
        Non fiber carbohydrates (% dry matter).
    PAF : float
        Processing adjustment factor.

    """

    non_fiber_carb: float
    PAF: float


@dataclass
class TotalInventory:
    """
    Contains information about the amounts of feeds held at the specified date.

    Attributes
    ----------
    available_feeds : list[Feed]
        List of Feeds which are held by the Feed Storage module and are available to feed to animals.
    inventory_date : date
        Date at which the amounts of feeds expected to be held.

    """

    available_feeds: dict[RUFAS_ID, float]
    inventory_date: date


@dataclass
class IdealFeeds:
    """
    Amounts of feeds that would ideally be purchased before the next harvest of a crop.

    Attributes
    ----------
    ideal_feeds : dict[RUFAS_ID, float]
        Amounts of feeds which would ideally be purchased before the next harvest of a crop, where the key is the RuFaS
        Feed ID and the value is the requested feed amount (kg).

    """

    ideal_feeds: dict[RUFAS_ID, float]


@dataclass
class RequestedFeed:
    """
    Total amounts of feed needed for the herd.

    Attributes
    ----------
    requested_feed : dict[RUFAS_ID, float]
        Amounts of feeds to be fed to the herd, where the key is the RuFaS Feed ID and the value is the requested feed
        amount (kg).

    """

    requested_feed: dict[RUFAS_ID, float]

    def __add__(self, other: "RequestedFeed") -> "RequestedFeed":
        if not isinstance(other, RequestedFeed):
            raise NotImplementedError

        combined_feed = defaultdict(float, self.requested_feed)
        for feed_id, amount in other.requested_feed.items():
            combined_feed[feed_id] += amount

        return RequestedFeed(dict(combined_feed))

    def __mul__(self, multiplier: int | float) -> "RequestedFeed":
        is_wrong_type = (not isinstance(multiplier, int)) and (not isinstance(multiplier, float))
        if is_wrong_type:
            raise TypeError("Cannot multiply RequestedFeed object by a non-integer or float.")

        new_feed_amounts = {rufas_id: amount * multiplier for rufas_id, amount in self.requested_feed.items()}
        return RequestedFeed(new_feed_amounts)

    def __rmul__(self, multiplier: int | float) -> "RequestedFeed":
        return multiplier * self


class PurchaseAllowance:
    """
    Limits on amounts of feeds that may be purchased at a given time.

    Attributes
    ----------
    allowances : dict[RUFAS_ID, float]
        Amounts of feeds that may be purchased, where the key is the RuFaS Feed ID and the value is the maximum amount
        of that feed (kg).

    """

    _purchase_allowance_key: str

    def __init__(self, feed_config_data: list[dict[str, int | float]]) -> None:
        self.allowances = self._setup_purchase_allowance(feed_config_data)

    def _setup_purchase_allowance(self, feed_config_data: list[dict[str, int | float]]) -> dict[int, float]:
        return {
            feed_config["purchased_feed"]: feed_config[self._purchase_allowance_key] for feed_config in feed_config_data
        }


class PlanningCycleAllowance(PurchaseAllowance):
    """User-defined limits on feeds that may be purchased between harvests of a crop."""

    _purchase_allowance_key: str = "planning_cycle_allowance"


class AdvancePurchaseAllowance(PurchaseAllowance):
    """User-defined limits on feeds that may be purchased at the beginning of a ration interval."""

    _purchase_allowance_key: str = "advance_purchase_allowance"


class RuntimePurchaseAllowance(PurchaseAllowance):
    """User-defined limits on feeds that may be purchased on a daily basis."""

    _purchase_allowance_key: str = "runtime_purchase_allowance"
