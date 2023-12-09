from RUFAS.config import Config
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines import Feed
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.routines.field.manager.field_manager import FieldManager
from RUFAS.time import Time
from RUFAS.weather import Weather

im = InputManager()
om = OutputManager()


class State:
    def __init__(self, config: Config, weather: Weather, time: Time):
        """
        Description:
            Contains information about the current state of the farm.
            The state object represents the state of the farm at a certain instant in
            time. It contains information arranged in different objects by what routine
            they (mostly) relate to. The state object (or some of its sub-objects) will
            be passed to routines during the simulation, which may access the
            information in the different sub-objects in the state to use in its
            calculations.
            The state object should ONLY store persistent data that WILL be used in
            future calculations and/or reports.
            DO NOT store immediate operands or values that do not NEED to be accessed in
            the future or in an output report in the state object.

        Parameters
        ----------
        config: Config
            Instance of the Config class containing information necessary to initialize the state.
        weather: Weather
            Instance of Weather class containing weather data from InputManager.
        time: Time
            Instance of the Time class containing information necessary to initialize the state.
        """
        feed_class_config = im.get_data("feed")
        self.feed = Feed(feed_class_config)
        manure_class_config = im.get_data("manure_management")
        animal_class_config = im.get_data("animal")
        animal_class_config['manure_management_scenarios'] = manure_class_config['manure_management_scenarios']
        self.animal_manager = AnimalManager(animal_class_config, config, self.feed, weather, time)
        self.manure_manager = ManureManager(self.animal_manager, weather, time, manure_class_config)

        self.field_manager = FieldManager(manure_manager=self.manure_manager)

    def annual_reset(self):
        """
        Description:
            Resets all annual variables that require reset
        """
        self.field_manager.annual_update_routine()

    def annual_mass_balance(self, time):
        pass
