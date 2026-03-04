from datetime import date
from pathlib import Path

import requests.models

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
        # TODO: this is redundant with SimulationEngine.__init__() but I can't figure out how to exclude
        ## this function definition without errors.
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime()
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
        self.simulate_animals = False

    def _daily_simulation(self) -> None:
        """Overloads the daily simulation function, specific to agronomy simulations."""
        # TODO: Niko is working on a refactor that will make implementing this
        ## much easier, so I'm going to wait on that.
        manure_applications = self.generate_daily_manure_applications()
        harvested_crops = self.field_manager.daily_update_routine(self.weather, self.time, manure_applications)

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

        return harvested_crops


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

    # get a reference to the output manager
    om = OutputManager()

    # Initialize the field simulation engine
    fs = FieldSimulation()

    # # run a day's simulation
    # fs._daily_simulation()

    # run a year's simulation
    fs._run_simulation_main_loop()

    # TODO - currently this is failing, because FieldSimulation does not have a
    ## manure manager even though the parent function generate_daily_manure_application
    ## depends upon it.