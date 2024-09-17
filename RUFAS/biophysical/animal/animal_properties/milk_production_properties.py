from dataclasses import dataclass
from ..data_types.milk_production_record import MilkProductionRecord


@dataclass
class MilkProductionProperties:
    """
    Holds information related to a cow's milk production.

    Attributes
    ----------
    days_in_milk : int
        Number of days the cow has been milking for in the current lactation.
    milk_produced : float
        Milk production of the cow on a single day (kg).
    milk_production_reduction : float
        Amount of milk daily production is reduced by (kg). TODO: previously this value would be negative, I think we should switch to it being positive.
    latest_305_day_milk_production : float
        Sum of milk production over the last 305 days of the cow's lactation (kg).
    crude_protein_percent : float
        Percentage of cow's milk that is crude protein by weight. TODO: double check the "by weight" part.
    true_protein_percent : float
        Percentage of cow's milk that is true protein. TODO: how do true protein and crude protein need to be compared in order to make sure they're valid.
    fat_percent : float
        Percentage of cow's milk that is fat by weight. TODO: double check the "by weight" part.
    lactose_percent : float
        Percentage of cow's milk that is lactose by weight. TODO: double check the "by weight" part.
    lactation_model : str, default "wood"
        Model which will be used to predict milk production (unitless).
    wood_l : float
        Wood's "l" lactation curve parameter (unitless).
    wood_m : float
        Wood's "m" lactation curve parameter (unitless).
    wood_n : float
        Wood's "n" lactation curve parameter (unitless).
    milk_production_history : list[MilkProductionRecord]
        History of a cow's milk production.

    """
    days_in_milk: int
    milk_produced: float  # Old var name: estimated_daily_milk_produced.
    milk_production_reduction: float
    latest_305_day_milk_production: float  # Old var name: latest_milk_production_305days
    crude_protein_percent: float  # Old var name: CP_milk
    true_protein_percent : float  # Old var name: mPrt
    fat_percent: float
    lactose_percent: float  # Old var name: lactose
    lactation_model: str = "wood"  # Old var name: lactation_cuve TODO: should verify if we only want support for Wood's model, or make it an Enum?
    wood_l: float
    wood_m: float
    wood_n: float
    milk_production_history: list[MilkProductionRecord]
