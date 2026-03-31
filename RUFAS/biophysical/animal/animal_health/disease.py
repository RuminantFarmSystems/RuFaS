from abc import ABC, abstractmethod

from RUFAS.biophysical.animal.animal_health.animal_health_status import AnimalHealthStatus
from RUFAS.rufas_time import RufasTime


class Disease(ABC):
    """
    Class representing disease simulation.
    """

    def __init__(self) -> None:
        # im.get_data(disease_config)
        # self.baseline_incidence_rate = disease_config.user_input_incedence_rate or 0.0
        self.risk_factors: list[str] = []

    @abstractmethod
    def assess_disease_risk(self, time: RufasTime, animal_health_status: AnimalHealthStatus) -> bool:
        """Base function for disease risk determination.

        Parameters
        ----------
        time : RufasTime
            The point in time in the simulation.
        animal_health_status : AnimalHealthStatus
            The health status of the animal.

        """
        # With a series of logic checks, RuFaS will determine if the animal is at risk of developing a particular
        # disease on a particular simulation day.
        pass

    @abstractmethod
    def calculate_incidence_rate(self) -> float:
        # function to calculate the incidence rate
        # combine relative risk factors with baseline_incidence_rate
        pass

    @abstractmethod
    def will_develop_disease(self, incidence_rate: float) -> bool:
        """Takes in incidence rate and compares it to RNG to deterine if animal will develop disease.

        Parameters
        ----------
        incidence_rate : float
            The incidence rate of the disease.

        Returns
        -------
        bool
            Whether the animal will develop the disease.
        """
        # use rng to generate comparison value
        # compare rng value to incidence
        # return rng < incidence rate
        pass

    @abstractmethod
    def determine_at_risk_period(self, animal_health_status: AnimalHealthStatus) -> int:
        """Probability mass function to get the risk period."""
        # Probability mass function to get the risk period.
        pass

    @abstractmethod
    def immediate_effect(self) -> None:
        pass

    @abstractmethod
    def intermediate_effect(self) -> None:
        pass

    @abstractmethod
    def lasting_effect(self) -> None:
        pass
