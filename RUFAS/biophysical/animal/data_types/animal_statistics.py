from dataclasses import dataclass


@dataclass
class AnimalStatistics:
    """
    Animal properties that are used for animal statistics.

    phosphorus_excreted : float
        The total amount of phosphorus excreted by the given animal (g).
    enteric_methane_emission : float
        The total amount of enteric methane produced by the given animal (g/day).

    """

    phosphorus_excreted: float = 0.0
    methane_emission: float = 0.0

    ED_days: int = 0
    estrus_count: int = 0
    GnRH_injections: int = 0
    PGF_injections: int = 0
    CIDR_injections: int = 0
    semen_number: int = 0
    AI_times: int = 0
    breeding_to_pregnancy_time: int = 0
    pregnancy_diagnoses: int = 0
    calving_to_pregnancy_time: int = 0
