from RUFAS.output_manager import OutputManager

from .emissions import EmissionsEstimator


class EEEManager:

    def __init__(self) -> None:
        pass

    @staticmethod
    def estimate_all() -> None:
        """Runs all estimation functions and records all results from them."""
        om = OutputManager()
        info_map = {"class": EEEManager.__class__.__name__, "function": EEEManager.estimate_all.__name__}

        om.add_log("Emissions Processing", "Starting processing of emissions.", info_map)
        emissions_estimator = EmissionsEstimator()
        emissions_estimator.estimate_emissions()
        om.add_log("Emissions Processing", "Completed processing of emissions.", info_map)
