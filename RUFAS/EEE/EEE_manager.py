from RUFAS.output_manager import OutputManager

from .emissions import EmissionsEstimator
from .energy import EnergyEstimator


class EEEManager:
    """Coordinates the energy and emissions estimations for the EEE module."""

    @staticmethod
    def estimate_all(simulate_animals: bool, simulate_feed: bool, simulate_fields: bool, simulate_manure: bool) -> None:
        """
        Runs all emissions and energy estimations and records their results to the ``OutputManager``.

        Parameters
        ----------
        simulate_animals : bool
            Whether the simulation initialized and used the AnimalManager module.
        simulate_feed : bool
            Whether the simulation initialized and used the FeedManager module
        simulate_fields : bool
            Whether the simulation initialized and used the FieldManager module.
        simulate_manure : bool
            Whether the simulation initialized and used the ManureManager module

        """
        om = OutputManager()
        info_map = {"class": EEEManager.__class__.__name__, "function": EEEManager.estimate_all.__name__}

        if simulate_fields:
            om.add_log("Emissions Processing", "Starting processing of emissions.", info_map)
            emissions_estimator = EmissionsEstimator(
                simulate_animals=simulate_animals,
                simulate_feed=simulate_feed,
                simulate_fields=simulate_fields,
                simulate_manure=simulate_manure,
            )
            emissions_estimator.estimate_farmgrown_feed_emissions()
            om.add_log("Emissions Processing", "Completed processing of emissions.", info_map)

            om.add_log("Energy Processing", "Starting processing of energy.", info_map)
            EnergyEstimator.estimate_all(
                simulate_animals=simulate_animals,
                simulate_feed=simulate_feed,
                simulate_fields=simulate_fields,
                simulate_manure=simulate_manure,
            )
            om.add_log("Energy Processing", "Completed processing of energy.", info_map)

        else:
            om.add_log(
                "No Energy or Emissions processing",
                "Fields not simulated, none of these calculations will be run.",
                info_map,
            )
