from typing import Optional

from RUFAS.biophysical.animal.animal_health.outcomes import DiseaseOutcomes


class AnimalHealthStatus:
    """
    Calculator class representing the health status of the animal.
    Will be the avenue for communicating data between the Animal object and the animal's health and disease status.
    """

    def __init__(self) -> None:
        # starting list for attribute data needed from Animal object:
        # id
        # breed
        # body_weight
        # daysBorn (age)
        # animal_type (cow, calf, heiferI, etc)
        # is_lactating
        # parity, calving_interval, days_in_preg, other repro status data?
        # other attributes will likely be needed
        self.status: DiseaseOutcomes = DiseaseOutcomes.HEALTHY
        self.disease_start_date: Optional[int] = None
        pass
