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
    estrus_count: int
    GnRH_injections: int
    PGF_injections: int
    CIDR_injections: int

    semen_num: int
    AI_times: int
    preg_diagnoses: int
    ED_days: int

    num_ai_performed: int
    num_ai_performed_in_ED: int
    num_ai_performed_in_TAI: int
    num_ai_performed_in_SynchED: int
    num_successful_conceptions: int
    num_successful_conceptions_in_ED: int
    num_successful_conceptions_in_TAI: int
    num_successful_conceptions_in_SynchED: int
