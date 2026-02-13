from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.simulation_engine import SimulationEngine

class FieldSimulation(SimulationEngine):
    """
    Class to be used in place of the SimulationEngine, to only run the agronomy simulations.
    """
    def __init__(self):
        """Initializes the agronomy simulation"""
        # self.om = OutputManager()
        # self.im = InputManager()
        # self.time = RufasTime() # requires
        # # this call to _initialize_simulation makes this method redundant with super().__init__().
        # self._initialize_simulation()

        super().__init__() # this calls the overloaded _initialize_simulation instead of OG.

    def _initialize_simulation(self) -> None:
        """Overloads the initialization of the simulation engine, specific to agronomy simulations."""
        ## Maybe just include directly in the init?
        pass

    def simulate(self) -> None:
        """Overload the simulation routines, specific to agronomy simulations."""
        pass

    def _daily_simulation(self) -> None:
        """Overloads the daily simulation function, specific to agronomy simulations."""
        pass

    def _run_simulation(self) -> None:
        """Overloads the annual simulation function, specific to agronomy simulations."""


if __name__ == '__main__':
    fs = FieldSimulation()
    print(hasattr(fs, "feed"))