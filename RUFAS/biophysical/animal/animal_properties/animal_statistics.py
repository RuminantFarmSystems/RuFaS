from dataclasses import dataclass


@dataclass
class AnimalStatistics:
    """
    Animal properties that are used for animal statistics.

    phosphorus_excreted : float
        The total amount of phosphorus excreted by the given animal (g).
    methane_emission : float
        The total amount of enteric methane produced by the given animal (g/day).

    """
    phosphorus_excreted: float
    methane_emission: float
