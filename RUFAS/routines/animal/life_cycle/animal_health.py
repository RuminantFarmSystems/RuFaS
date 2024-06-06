class AnimalHealth:
    """
    Abstract class representing animal health and disease risk in RuFaS.
    """

    def __init__(self) -> None:
        pass

    def assess_disease_risk(self, animal_type: str):
        """Base function for disease risk determination."""
        # determine what type of animal it is/what life cycle stage it's in
        # determine its repro status
        # if it's a cow, determine if it's lactating
        # review additional management parameters
        self._calculate_incidence_rate(animal_type, risk_factors=...)
        pass

    def _calculate_incidence_rate(self, animal_type: str, risk_factors: float = None) -> None:
        """Takes risk assessment factors and calculates disease incidence rate"""
        # add hard-coded incidence_rate
        # generate random number to determine if 
        pass
