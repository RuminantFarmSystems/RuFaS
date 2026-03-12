from typing import Optional, assert_type
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.simulation_engine import SimulationEngine
from build.lib.RUFAS.rufas_time import RufasTime

# type RufasSingleton = InputManager | SimulationEngine | OutputManager | RufasTime
#
# def clear_singleton(singleton: RufasSingleton) -> None:
#     if assert_type(singleton, RufasSingleton):
#         print("RufasSingleton found")
#         # get the class object
#         singleton_class = type(singleton)
#         # delete the instance variable
#         delattr(singleton_class, "instance")
#         del singleton
#         # instantiate new instance
#         singleton = singleton_class()

def load_data_manually(
        im : InputManager = InputManager(),
        data: Optional[dict] = None,
) -> None:
    """manually add data to the input manager"""
    pass



if __name__ == '__main__':

    ## ---- Imports ----
    from pathlib import Path
    from RUFAS.input_manager import InputManager
    from RUFAS.output_manager import OutputManager
    from RUFAS.simulation_engine import SimulationEngine#, #SimulationType
    import os

    ## ---- Setup -----
    # TODO: currently, this only works if the external input files have exactly the same
    ## directory structure as the main project's input/ folder.
    ## The model should be able to support other paths, but currently searches for "properties"
    ## differently than the other paths provided by the metadata files.
    eval_root = Path("/home/morrowcj/Docum"
                     "ents/projects/rufas-evaluation/")
    md_path = Path("input/metadata/farm1_wcrops_metadata.json")
    # eval_root = Path("/home/morrowcj/Downloads/RUFAS_INPUT_COPY/")
    # md_path = Path("input/metadata/example_freestall_dairy_metadata.json")

    # # setup parameters
    # md_path = Path("input/metadata/example_freestall_dairy_metadata.json")

    # Initialize the input manager and manually load in the data.
    im = InputManager()
    im.start_data_processing(
        metadata_path = md_path, # bypasses task manager meta data.
        input_root = eval_root,
        # input_root = Path("."), # TODO: why isn't this the default within the function?
        task_id = "random task name" # TODO: why is this required? Should be a default.
    )

    im._reset_singleton()

    # # manually update the simulation_type variable, since the config files don't have this variable.
    # im.pool["config"]["simulation_type"] = "field_and_feed"
    #
    # # initialize other managers
    # om = OutputManager()
    # engine = SimulationEngine(SimulationType("field_and_feed"))
    #
    # ## ---- Run the simulation ----
    #
    # # Run the sim
    # engine.simulate()

    # Collect the output


    ## ---- Scratch ----