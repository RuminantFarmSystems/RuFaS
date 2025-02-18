from dataclasses import dataclass


@dataclass
class AnimalManureExcretions:
    """
    A TypedDict class that specifies the structure of the dictionary of animal manure excretion values.

    Attributes
    ----------
    urea: float
        Concentration of urea in manure (g/L).
    urine: float
        Amount of urine excreted (kg).
    manure_total_ammoniacal_nitrogen: float
        Amount of ammoniacal nitrogen in the manure slurry (kg).
    urine_nitrogen: float
        Amount of nitrogen in urine (kg).
    manure_nitrogen: float
        Amount of nitrogen in manure (kg).
    manure_mass: float
        Amount of manure (kg).
    total_solids: float
        Amount of total solids (kg).
    degradable_volatile_solids: float
        Amount of degradable volatile solids (kg).
    non_degradable_volatile_solids: float
        Amount of non-degradable volatile solids (kg).
    inorganic_phosphorus_fraction: float
        Fraction of water extractable inorganic phosphorus (unitless).
    organic_phosphorus_fraction: float
        Fraction of water extractable organic phosphorus (unitless).
    non_water_inorganic_phosphorus_fraction: float
        Fraction of non-water extractable inorganic phosphorus (unitless).
    non_water_organic_phosphorus_fraction: float
        Fraction of non-water extractable organic phosphorus (unitless).
    phosphorus: float
        Amount of phosphorus excreted in manure (g).
    phosphorus_fraction: float
        Fraction of phosphorus in manure (unitless).
    potassium: float
        Amount of potassium in manure (g).
    enteric_methane_g: float
        The amount of enteric methane (g).

    """

    urea: float = 0.0
    urine: float = 0.0
    manure_total_ammoniacal_nitrogen: float = 0.0
    urine_nitrogen: float = 0.0
    manure_nitrogen: float = 0.0
    manure_mass: float = 0.0
    total_solids: float = 0.0
    degradable_volatile_solids: float = 0.0
    non_degradable_volatile_solids: float = 0.0
    inorganic_phosphorus_fraction: float = 0.0
    organic_phosphorus_fraction: float = 0.0
    non_water_inorganic_phosphorus_fraction: float = 0.0
    non_water_organic_phosphorus_fraction: float = 0.0
    phosphorus: float = 0.0
    phosphorus_fraction: float = 0.0
    potassium: float = 0.0

    def __add__(self, other: "AnimalManureExcretions") -> "AnimalManureExcretions":
        return AnimalManureExcretions(
            self.urea + other.urea,
            self.urine + other.urine,
            self.manure_total_ammoniacal_nitrogen + other.manure_total_ammoniacal_nitrogen,
            self.urine_nitrogen + other.urine_nitrogen,
            self.manure_nitrogen + other.manure_nitrogen,
            self.manure_mass + other.manure_mass,
            self.total_solids + other.total_solids,
            self.degradable_volatile_solids + other.degradable_volatile_solids,
            self.non_degradable_volatile_solids + other.non_degradable_volatile_solids,
            self.inorganic_phosphorus_fraction + other.inorganic_phosphorus_fraction,  # fraction addition?
            self.organic_phosphorus_fraction + other.organic_phosphorus_fraction,
            self.non_water_inorganic_phosphorus_fraction + other.non_water_inorganic_phosphorus_fraction,
            self.non_water_organic_phosphorus_fraction + other.non_water_organic_phosphorus_fraction,
            self.phosphorus + other.phosphorus + other.phosphorus_fraction,
            self.phosphorus_fraction + other.phosphorus_fraction,  # how to handle fraction for addition
            self.potassium + other.potassium,
        )
