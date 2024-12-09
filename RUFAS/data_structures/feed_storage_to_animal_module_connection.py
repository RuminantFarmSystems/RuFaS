from dataclasses import dataclass
from enum import Enum

from RUFAS.units import MeasurementUnits


class Category(Enum):
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
    AMINOACIDS = "Aminoacids"
    FORAGE = "Forage"
    CONC = "Conc"
    MILK = "Milk"
    MINERAL = "Mineral"
    VITAMINS = "Vitamins"
    STARTER = "Starter"
    NO = "No"


class NutrientStandard(Enum):
    NASEM = "NASEM"
    NRC = "NRC"


@dataclass
class Feed:
    """
    Base representation of a feed in RuFaS.
    Attributes
    ----------
    rufas_id : int
    Fd_Category : Category
    feed_type : Type
    DM : float
    ash : float
    CP : float
    N_A : float
    N_B : float
    N_C : float
    Kd : float
    dRUP : float
    ADICP : float
    NDICP : float
    ADF : float
    NDF : float
    lignin : float
    starch : float
    EE : float
    calcium : float
    phosphorus : float
    magnesium : float
    potassium : float
    sodium : float
    chlorine : float
    sulfur : float
    is_fat : bool
    is_wetforage : float
    units : MeasurementUnits
    limit : float
    lower_limit : float
    TDN : float
    DE : float
    amount_available : float
        Amount of feed currently or expected to be available (kg).
    on_farm_cost : float
        Price of using the feed that is already on-farm ($ / kg).
    purchase_cost : float
        Price of buying feed from off-farm ($ / kg).
    """

    rufas_id: int
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
    """NASEM-specific representation of a RuFaS feed."""

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
    """NRC-specific representation of a RuFaS feed."""

    non_fiber_carb: float
    PAF: float
