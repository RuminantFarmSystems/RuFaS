from dataclasses import dataclass
from ..data_types.milk_production_record import MilkProductionRecord


@dataclass
class MilkProductionProperties:
    """
    Holds information related to an animal's milk production.

    Attributes
    ----------
    true_protein_content : float
        Amount of true protein in the milk produced (kg).
    fat_content : float
        Amount of fat in the milk produced (kg).
    milk_production_reduction : float
        Amount of milk daily production is reduced by (kg).
    milk_production_last_305_days : float
        Sum of milk production over the first 305 days of the animal's current lactation (kg). This value is reset to 0
        when a lactation ends, and is not reset until the 305th day of the next lactation is reached.
    crude_protein_percent : float
        Percentage of milk that is crude protein by weight.
    true_protein_percent : float
        Percentage of milk that is true protein by weight.
    fat_percent : float
        Percentage of milk that is fat by weight.
    lactose_percent : float
        Percentage of milk that is lactose by weight.
    wood_l : float
        Wood's "l" lactation curve parameter (unitless).
    wood_m : float
        Wood's "m" lactation curve parameter (unitless).
    wood_n : float
        Wood's "n" lactation curve parameter (unitless).
    milk_production_history : list[MilkProductionRecord]
        History of milk production.

    """

    true_protein_content: float  # Old var name: milk_protein_kg
    fat_content: float  # Old name: milk_fat_kg
    milk_production_reduction: float
    milk_production_last_305_days: float  # Old var name: latest_milk_production_305days
    crude_protein_percent: float  # Old var name: CP_milk
    true_protein_percent: float  # Old var name: mPrt
    fat_percent: float
    lactose_percent: float  # Old var name: lactose
    wood_l: float
    wood_m: float
    wood_n: float
    milk_production_history: list[MilkProductionRecord]
