from dataclasses import dataclass
from ..data_types.milk_production_record import MilkProductionRecord


@dataclass
class MilkProductionProperties:
    """
    Holds information related to an animal's milk production.

    Attributes
    ----------
    crude_protein_content : float
        Amount of crude/total protein in the milk produced (kg).
    true_protein_content : float
        Amount of true protein in the milk produced (kg).
    fat_content : float
        Amount of fat in the milk produced (kg).
    lactose_content : float
        Amount of lactose in the milk produced (kg).
    milk_production_reduction : float
        Amount of milk daily production is reduced by (kg).
    current_lactation_305_day_milk_produced : float
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

    crude_protein_content: float
    true_protein_content: float
    fat_content: float
    lactose_content: float
    milk_production_reduction: float
    current_lactation_305_day_milk_produced: float
    crude_protein_percent: float
    true_protein_percent: float
    fat_percent: float
    lactose_percent: float
    wood_l: float
    wood_m: float
    wood_n: float
    milk_production_history: list[MilkProductionRecord]
