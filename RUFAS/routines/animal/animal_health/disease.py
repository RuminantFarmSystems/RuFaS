from RUFAS.routines.animal.animal_health.animal_health_status import AnimalHealthStatus
from RUFAS.time import Time
from abc import ABC


class Disease(ABC):
    """
    Class representing disease simulation.
    """

    def __init__(self):
        # im.get_data(disease_config)
        # self.baseline_incidence_rate = disease_config.user_input_incedence_rate or 0.0
        self.risk_factors: list[str] = []

    def assess_disease_risk(self, time: Time, animal_health_status: AnimalHealthStatus) -> bool:
        """Base function for disease risk determination.

        Parameters
        ----------
        time : Time
            The point in time in the simulation.
        animal_health_status : AnimalHealthStatus
            The health status of the animal.

        """
        # With a series of logic checks, RuFaS will determine if the animal is at risk of developing a particular
        # disease on a particular simulation day.

        pass

    def calculate_incidence_rate(self) -> float:
        # function to calculate the incidence rate
        # combine relative risk factors with baseline_incidence_rate
        pass

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

    def determine_at_risk_period(self, animal_health_status: AnimalHealthStatus) -> int:
        """Probability mass function to get the risk period."""
        # Probability mass function to get the risk period.
        pass

    def immediate_effect(self):
        pass

    def intermediate_effect(self):
        pass

    def lasting_effect(self):
        pass
