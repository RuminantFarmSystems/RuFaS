from dataclasses import dataclass
from enum import Enum

from RUFAS.units import MeasurementUnits


"""
Every feed in RuFaS has a unique integer ID. They are defined in the Feed Library file used, and are used throughout
other input files and the RuFaS codebase.
"""
RUFAS_ID = int


class Category(Enum):
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


class Type(Enum):
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
        Unique integer identifier for feeds used within the RuFaS model.
    Fd_Category : Category
        Feed category.
    feed_type : Type
        General type or category of the feed.
    DM : float
        Dry matter content of the feed (% dry matter). TODO: wut??
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
        Feed degradation rate of B fraction (% h). TODO: percent per hour?
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
        Starch (%). TODO: percentage of what, dry matter?
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
        Identifier of fat type feed.
    is_wetforage : float
        Identifier of wet forage type feed.
    units : MeasurementUnits
        TODO: document this! Also, is it possible to just have one unit for all feeds, preferable kg?
    limit : float
        TODO: document this. Also, limits by animal type?
    lower_limit : float
        TODO: document this. Also, limits by animal type?
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

    """

    rufas_id: RUFAS_ID
    Fd_Category: Category
    feed_type: Type
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
    is_wetforage: float
    units: MeasurementUnits
    limit: float
    lower_limit: float
    TDN: float
    DE: float

    amount_available: float
    on_farm_cost: float
    purchase_cost: float


@dataclass
class NASEMFeed(Feed):
    """
    NASEM-specific representation of a RuFaS feed.

    Attributes
    ----------
    Name : str
        Feed name.
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
        Digestible energy standard (Mcal/kg). TODO: if using NASEM feeds, should DE_Base always be used instead of DE?
    copper : float  TODO: add descriptiosn to these.
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
    starch_digested : float
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
