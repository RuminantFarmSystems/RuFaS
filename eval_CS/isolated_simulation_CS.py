from pathlib import Path

from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.weather import Weather


class FieldSimulation(SimulationEngine):
    """
    Child class to be used in place of the SimulationEngine, to run isolated agronomy simulations.
    """
    def __init__(self):
        """Initializes the agronomy simulation"""
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime() # requires
        # this call to _initialize_simulation makes this method redundant with super().__init__().
        self._initialize_simulation()

    def simulate(self) -> None:
        """Overload the simulation routines, specific to agronomy simulations."""
        pass

    def _initialize_simulation(self) -> None:
        """Overloads the initialization of the simulation engine, specific to agronomy simulations."""
        ## Maybe just include directly in the init?
        weather_data = self.im.get_data("weather")
        self.om.time = self.time
        self.weather = Weather(weather_data, self.time)
        self.field_manager: FieldManager = FieldManager()

        self.manure_manager: ManureManager = ManureManager(
            self.weather.intercept_mean_temp, self.weather.phase_shift, self.weather.amplitude
        )


    def _daily_simulation(self) -> None:
        """Overloads the daily simulation function, specific to agronomy simulations."""
        pass

    def _formulate_ration(self) -> None:
        """Overloads ration formulation: No rations need formulating in the isolated agronomy simulation"""
        pass


if __name__ == '__main__':
    # setup parameters
    md_path = Path("input/metadata/example_freestall_dairy_metadata.json")

    # Initialize the input manager and manually load in the data.
    im = InputManager()
    im.start_data_processing(
        metadata_path = md_path, # bypasses task manager meta data.
        input_root = Path("."), # TODO: why isn't this the default within the function?
        task_id = "random task name" # TODO: why is this required? Should be some default.
    )

    # Initialize the field simulation engine
    fs = FieldSimulation()