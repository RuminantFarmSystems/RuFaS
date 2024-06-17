from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase


class DiseaseIncidence:
    """
    Abstract class representing disease risk and incidence assessment in RuFaS.
    """

    def __init__(self) -> None:
        pass

    def assess_disease_risk(self, animal_type: AnimalBase) -> None:
        """Base function for disease risk determination.

        Parameters
        ----------
        animal_type : AnimalBase
            The animal for which the disease risk will be assessed.

        """
        # check for risk factors:
        # - what type of animal it is/what life cycle stage it's in, repro status, if lactating
        # - review additional management parameters
        # - different diseases have different disease risk factors reviewed here

        # if animal doesn't meet all necessary risk factors, return/stop assessment process.
        # else, calculate incidence rate

        # incidence_rate = self._calculate_incidence_rate(risk_factors=...)

        # will_develop_disease = self._will_develop_disease(incidence_rate)
        # tag animal with result of will_develop_disease

        # at_risk_period = self._determine_at_risk_period()
        # unclear if at_risk_period needs to be determined before will_develop_disease is calculated
        pass

    def _calculate_incidence_rate(self, risk_factors: float) -> float:
        """Takes risk assessment factors and calculates disease incidence rate.

        Parameters
        ----------
        risk_factors : float
            The relative risk factors the animal has.

        Returns
        -------
        float
            The incidence rate of the disease.
        """
        # im = InputManager()
        # im.get_data("location.of.baseline_incidence_rate") - get the user-input baseline incidence rate for disease
        # combine relative risk factors with baseline_incidence_rate
        pass

    def _will_develop_disease(incidence_rate: float) -> bool:
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

    def _determine_at_risk_period(self) -> int:
        """Probability mass function to get the risk period."""
        # logic to determine disease start date
        # Is this limited? i.e. if the risk period has already passed is the animal in the clear?
        pass
