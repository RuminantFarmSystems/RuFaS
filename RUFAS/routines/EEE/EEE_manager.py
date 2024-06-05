from .emissions import Emissions


class EEEManager:

    def __init__(self) -> None:
        pass

    @staticmethod
    def estimate_all() -> None:
        """Runs all estimation functions and records all results from them."""
        emissions_estimator = Emissions()
        emissions_estimator.estimate_emissions()
