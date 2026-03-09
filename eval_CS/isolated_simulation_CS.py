from datetime import date
from pathlib import Path

import requests.models

from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.weather import Weather


class FieldSimulation(SimulationEngine):
    """
    Child class to be used in place of the SimulationEngine, to run isolated agronomy simulations.
    """
    def __init__(self, store_feed: bool = True) -> None:
        """Initializes the agronomy simulation"""
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime()

        # Temporary attributes
        self._store_feed = store_feed
        self._simulate_animals: bool = False

        self._initialize_simulation()



    @property
    def store_feed(self) -> bool:
        return self._store_feed

    @property
    def simulate_animals(self) -> bool:
        return self._simulate_animals

    def _initialize_simulation(self) -> None:
        """
        Overloads the initialization of the simulation engine, specific to agronomy simulations.

        Details
        -------
        Differs from parent method by:
        1. Skips feed setup (nutrient standard, feed purchasing input)
        2. Changes feed storage setup to be optional
        """
        weather_data = self.im.get_data("weather")
        self.om.time = self.time
        self.weather = Weather(weather_data, self.time)

        self.field_manager: FieldManager = FieldManager()

        # To estimate drydown / nutrient content
        if self.store_feed:
            nutrient_standard = NutrientStandard(self.im.get_data("config.nutrient_standard"))
            feeds_config = self.im.get_data("feed")
            feed_storage_configs = self.im.get_data("feed_storage_configurations")
            feed_storage_instances = self.im.get_data("feed_storage_instances")
            self.feed_manager: FeedManager = FeedManager(
                # TODO: feeds_config and nutrient_standard are are animal-specific
                ## and not necessary for simulating crop attributes. Make
                ## them optional within FieldManager and remove them from this
                ## method.
                feeds_config,
                nutrient_standard,
                feed_storage_configs,
                feed_storage_instances,
            )

    # TODO
    def simulate(self) -> None:
        """Overload the simulation routines, specific to agronomy simulations."""
        pass

    # TODO: Revisit
    ## Rename to _execute_field_only_simulation ?
    def _daily_simulation(self) -> list[HarvestedCrop]:
        """Overloads the daily simulation function, specific to agronomy simulations."""
        harvested_crops = self._execute_daily_field_operations()

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

        return harvested_crops


    def _formulate_ration(self) -> None:
            """Overloads ration formulation: No rations need formulating in the isolated agronomy simulation"""
            pass


if __name__ == '__main__':
    # ---- Setup ----
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

    # ---- Run ----
    # TODO
    # # run a day's simulation
    # fs._daily_simulation()

    # run a year's simulation
    # fs._annual_simulation()

    # run the full simulation loop
    # fs._run_simulation_main_loop()

    # ---- Collect Results ----
    """
    Variables of interest, from discussions with Kristan and Kevin:
    1. Crop biomass yield (pre- and post-drying)
    2. Crop nutrient content: C, N, H2O (pre- and post-drying)
    3. Soil nutrient content: C, N, P, H2O
    4. Soil runoff content: H2O, N, P
    5. Field Emissions: CO2, CH4, N2O
    6. Storage dry matter mass (total and net)
    7. Mass lost from gasses, effluent, and H20
    9. Feed purchased (total and proportion)
    """