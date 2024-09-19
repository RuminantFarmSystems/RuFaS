from dataclasses import dataclass
from ..data_types.milk_production_record import MilkProductionRecord


@dataclass
class MilkProductionProperties:
    """
    Holds information related to a cow's milk production.

    Attributes
    ----------
    true_protein_content : float
        Amount of true protein in the milk produced (kg).
    fat_content : float
        Amount of fat in the milk produced (kg).
    milk_production_reduction : float
        Amount of milk daily production is reduced by (kg).
    latest_305_day_milk_production : float
        Sum of milk production over the last 305 days of the cow's lactation (kg).
    crude_protein_percent : float
        Percentage of cow's milk that is crude protein by weight.
    true_protein_percent : float
        Percentage of cow's milk that is true protein. TODO: how do true protein and crude protein need to be compared in order to make sure they're valid.
    fat_percent : float
        Percentage of cow's milk that is fat by weight.
    lactose_percent : float
        Percentage of cow's milk that is lactose by weight.
    wood_l : float
        Wood's "l" lactation curve parameter (unitless).
    wood_m : float
        Wood's "m" lactation curve parameter (unitless).
    wood_n : float
        Wood's "n" lactation curve parameter (unitless).
    milk_production_history : list[MilkProductionRecord]
        History of a cow's milk production.

    """

    true_protein_content: float  # Old var name: milk_protein_kg
    fat_content: float  # Old name: milk_fat_kg
    milk_production_reduction: float
    latest_305_day_milk_production: float  # Old var name: latest_milk_production_305days
    crude_protein_percent: float  # Old var name: CP_milk
    true_protein_percent: float  # Old var name: mPrt
    fat_percent: float
    lactose_percent: float  # Old var name: lactose
    wood_l: float
    wood_m: float
    wood_n: float
    milk_production_history: list[MilkProductionRecord]
