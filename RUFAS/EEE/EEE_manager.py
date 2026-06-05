from RUFAS.output_manager import OutputManager

from .emissions import EmissionsEstimator
from .energy import EnergyEstimator


class EEEManager:
    """Coordinates the energy and emissions estimations for the EEE module."""

    @staticmethod
    def estimate_all() -> None:
        """Runs all emissions and energy estimations and records their results to the ``OutputManager``."""
        om = OutputManager()
        info_map = {"class": EEEManager.__class__.__name__, "function": EEEManager.estimate_all.__name__}

        om.add_log("Emissions Processing", "Starting processing of emissions.", info_map)
        emissions_estimator = EmissionsEstimator()
        emissions_estimator.estimate_farmgrown_feed_emissions()
        om.add_log("Emissions Processing", "Completed processing of emissions.", info_map)

        om.add_log("Energy Processing", "Starting processing of energy.", info_map)
        EnergyEstimator.estimate_all()
        om.add_log("Energy Processing", "Completed processing of energy.", info_map)
