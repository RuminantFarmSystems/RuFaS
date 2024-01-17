# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
from pathlib import Path
import sys
import random
import traceback
from typing import List
import numpy

from RUFAS.config import Config
from RUFAS.routines.animal.life_cycle.herd_factory import HerdFactory
from RUFAS.scenario_manager import METADATA_PATHS, MetadataPaths
from RUFAS.schema_generator import SchemaGenerator
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity


def main():
    cmd_arguments = parse_gnu_args()
    if cmd_arguments.load_pool:
        load_pool = True
    else:
        load_pool = False
    try:
        run_rufas(
            load_pool,
            produce_graphics=not cmd_arguments.no_graphics,
            format_option=cmd_arguments.format_option,
            verbose=LogVerbosity(cmd_arguments.verbose),
            clear_output=cmd_arguments.clear_output,
            exclude_info_maps=cmd_arguments.exclude_info_maps,
            only_run_validation=cmd_arguments.only_run_validation,
            graphics_dir=Path(cmd_arguments.graphics_dir),
            vars_file_path=Path(cmd_arguments.load_pool),
            output_dir=Path(cmd_arguments.output_dir),
            filters_dir=Path(cmd_arguments.filters_dir),
            csv_dir=Path(cmd_arguments.csv_dir),
            init_herd=cmd_arguments.init_herd,
            save_animals=cmd_arguments.save_animals,
            save_animals_dir=Path(cmd_arguments.save_animals_dir),
            terminate_simulation_post_herd_generation=cmd_arguments.terminate_simulation_post_herd_generation,
            generate_schemas=cmd_arguments.generate_schemas,
        )
    except Exception as e:
        info_map = {"class": "No caller class",
                    "function": main.__name__,
                    }
        output_manager = OutputManager()
        error_message = "This terminal error occurred during runtime. "
        error_message += traceback.format_exc()
        output_manager.add_error(f"Dumping all logs from main.py because of error '{e}'",
                                 error_message,
                                 info_map)
        output_manager.dump_all_nondata_pools(
            Path(cmd_arguments.output_dir), cmd_arguments.exclude_info_maps, cmd_arguments.format_option
        )
        sys.stdout.write("Unexpected early termination of the simulation. Please see logs for details.\n")


def run_rufas(
        load_pool: bool,
        produce_graphics: bool,
        format_option: str,
        verbose: LogVerbosity,
        clear_output: bool,
        exclude_info_maps: bool,
        only_run_validation: bool,
        graphics_dir: Path,
        vars_file_path: Path,
        output_dir: Path,
        filters_dir: Path,
        csv_dir: Path,
        init_herd: bool,
        save_animals: bool,
        save_animals_dir: Path,
        terminate_simulation_post_herd_generation: bool,
        generate_schemas: bool,
) -> None:
    """
    Main function to run RuFaS, with options.

    Parameters
    ----------
    load_pool : bool
        Flag to load json file into Output Manager variables pool for processing.
    produce_graphics : bool
        Produce graphics after simulation.
    format_option : str
        Format for variable_names.txt output file.
    verbose : bool
        Print progress messages while simulation is running.
    clear_output : bool
        Clear output directory before running the simulation.
    exclude_info_maps : bool
        Exclude info_maps from the output.
    only_run_validation : bool
        Validate input data and don't run a simulation.
    graphics_dir : Path
        The directory for saving graphics.
    vars_file_path : Path
        The path to the json file to load into Output Manager variables pool for processing.
    output_dir : Path
        The directory for saving output.
    filters_dir : Path
        The directory for the files containing the keys for filtering.
    csv_dir : Path
        The directory for the csv output files to be saved.
    init_herd: bool
        Initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to JSON files.
    save_animals_dir : Path
        User input indicating the save directory for generated animals.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.
    generate_schemas : bool
        User input indicating if the program should produce input schemas for the Data Collection App and terminate.

    """
    sys.stdout.write("RuFaS: Ruminant Farm Systems Model 2023\n")

    output_manager = OutputManager()
    output_manager.create_directory(output_dir)

    if load_pool:
        run_load_vars_pool(vars_file_path, exclude_info_maps, format_option,
                           produce_graphics, graphics_dir, clear_output, output_dir,
                           filters_dir, csv_dir)
        return

    if clear_output:
        output_manager.clear_output_dir(vars_file_path, output_dir)

    if generate_schemas:
        log_title = "Generating schemas"
        log_message = "Main routine generating new input schemas for the Data Collection App."
        info_map = {
            "class": "main",
            "function": "run_rufas"
        }
        output_manager.add_log(log_title, log_message, info_map)

        schema_generator = SchemaGenerator()
        schema_generator.generate_schemas(None, None)

        log_title = "Completed schema generation"
        log_message = "Main routine completed generating new input schemas for the Data Collection App."
        info_map = {
            "class": "main",
            "function": "run_rufas"
        }
        output_manager.add_log(log_title, log_message, info_map)
        return

    metadata_files: List[MetadataPaths] = METADATA_PATHS
    if only_run_validation:
        run_validation(metadata_files, exclude_info_maps, format_option, verbose, output_dir)
    else:
        execute_simulations(
            metadata_files,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
            format_option,
            verbose,
            output_dir,
            filters_dir,
            csv_dir,
            init_herd,
            save_animals,
            save_animals_dir,
            terminate_simulation_post_herd_generation
        )


def run_load_vars_pool(
        vars_file_path: Path,
        exclude_info_maps: bool,
        format_option: str,
        produce_graphics: bool,
        graphics_dir: Path,
        clear_output: bool,
        output_dir: Path,
        filters_dir: Path,
        csv_dir: Path
) -> None:
    """Instantiates Output Manager and triggers loading of the variables pool from the provided file path
    for post-processing.

    Parameters
    ----------
    vars_file_path : Path
        The path to the json file to load into Output Manager variables pool for processing.
    exclude_info_maps : bool
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    format_option : str
        Format for variable_names.txt output file.
    produce_graphics : bool
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path
        The directory for saving graphics.
    clear_output : bool
        Flag for whether or not the user wants to clear the output directory.
    output_dir : Path
        The directory for saving output.
    filters_dir : Path
        The directory for the files containing the keys for filtering.
    csv_dir : Path
        The directory for the csv output files to be saved.
    """
    output_manager = OutputManager()
    if clear_output:
        output_manager.clear_output_dir(vars_file_path, output_dir)
    output_manager.flush_pools()
    output_manager.load_variables_pool_from_file(vars_file_path)
    output_manager.set_metadata_prefix("reload")
    output_manager.save_results(
        output_dir,
        filters_dir,
        exclude_info_maps,
        produce_graphics,
        graphics_dir,
        csv_dir
    )
    output_manager.dump_all_nondata_pools(
        output_dir, exclude_info_maps, format_option
    )


def run_validation(
        metadata_files: List[Path],
        exclude_info_maps: bool,
        format_option: str,
        verbose: LogVerbosity,
        output_dir: Path
) -> None:
    """Instantiates I/O Managers and triggers validation of input data.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        The list of Paths to the metadata files the user entered with which to run the simulation.
    exclude_info_maps : bool, optional
        Flag for whether the user wants to include info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    output_dir : Path
        The directory for saving output.
    """
    info_map = {
        "class": "No caller class",
        "function": run_validation.__name__,
    }
    output_manager = OutputManager()
    input_manager = InputManager()
    output_manager.add_log(
        "Validation only",
        "***Only validating data, no simulation will follow.***",
        info_map,
    )
    output_manager.set_log_verbose(verbose)
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        output_manager.add_log(
            "Validation start",
            f"Validating data for {str(metadata_file['path'])}...\n",
            info_map,
        )
        is_data_valid = input_manager.start_data_processing(
            str(metadata_file["path"]), False
        )
        if is_data_valid:
            output_manager.add_log("Validation", "Data is valid.\n\n", info_map)
        else:
            output_manager.add_warning(
                "Validation",
                f"Data not valid for {metadata_file['path']}.\n\n",
                info_map,
            )
        output_manager.dump_all_nondata_pools(
            output_dir, exclude_info_maps, format_option
        )


def initialize_herd(
        simulation_config: Config,
        init_herd: bool = False,
        save_animals: bool = False,
        save_animals_dir: Path = Path("output/"),
        terminate_simulation_post_herd_generation: bool = False
) -> None:
    """
    Initializes a herd based on the provided simulation configuration.

    Parameters
    ----------
    simulation_config : Config
        Config object containing parameters and settings for the simulation.
    init_herd: bool
        User input indicating whether to initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to JSON files.
    save_animals_dir : Path
        User input indicating the save directory for generated animals.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.

    Returns
    -------
    None

    Notes
    -----
    This function is responsible for setting up the initial state of the herd
    based on the given configuration. It can also save the initialized herd data
    to a specified directory.

    The function utilizes an `OutputManager` for logging various stages and events
    during the initialization process. It also respects the seed settings
    provided in the simulation configuration for consistent results.
    """
    info_map = {
        "class": "No caller class",
        "function": initialize_herd.__name__,
    }
    output_manager = OutputManager()

    if simulation_config.set_seed:
        random.seed(simulation_config.seed)
        numpy.random.seed(simulation_config.seed)

    output_manager.add_log(
        "Herd initialization start",
        "Initializing herd data...\n",
        info_map
    )
    herd_factory = HerdFactory(
        init_herd=init_herd,
        save_animals=save_animals,
        save_animals_path=save_animals_dir)
    herd_factory.initialize_herd()
    output_manager.add_log(
        "Herd initialization complete",
        "Herd data initialized.\n",
        info_map
    )

    if terminate_simulation_post_herd_generation:
        output_manager.add_log("Herd generation only",
                               "***Only generating herd data, no simulation will follow.***",
                               info_map)


def execute_simulations(
        metadata_files: List[MetadataPaths],
        exclude_info_maps: bool,
        produce_graphics: bool,
        graphics_dir: Path,
        format_option: str,
        verbose: LogVerbosity,
        output_dir: Path,
        filters_dir: Path,
        csv_dir: Path,
        init_herd: bool,
        save_animals: bool,
        save_animals_dir: Path,
        terminate_simulation_post_herd_generation: bool
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        A list of custom TypedDict objects including the specified prefix for the save_results output file
        and the path to the metadata file.
    exclude_info_maps : bool
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics: bool
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path
        The directory for saving graphics.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    output_dir : Path
        The directory for saving output.
    filters_dir : Path
        The directory for the files containing the keys for filtering.
    csv_dir : Path
        The directory for the csv output files to be saved.
    init_herd: bool
        Initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to JSON files.
    save_animals_dir : Path
        User input indicating the save directory for generated animals.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.
    """
    info_map = {
        "class": "No caller class",
        "function": execute_simulations.__name__,
    }
    sys.stdout.write("Simulating...\n")
    output_manager = OutputManager()
    input_manager = InputManager()
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        output_manager.add_log(
            "Validation start",
            f"Validating data for {str(metadata_file['path'])}...\n",
            info_map,
        )
        output_manager.set_metadata_prefix(metadata_file["prefix"])
        is_data_valid = input_manager.start_data_processing(
            str(metadata_file["path"]), True
        )
        if is_data_valid:
            output_manager.add_log(
                "Validation complete", "Data is valid. \nSimulating...\n", info_map
            )
            simulation_config = Config(input_manager.get_data("config"))
            try:
                initialize_herd(simulation_config=simulation_config,
                                init_herd=init_herd,
                                save_animals=save_animals,
                                save_animals_dir=save_animals_dir,
                                terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation)
            except Exception as e:
                output_manager.dump_all_nondata_pools(path=output_dir, exclude_info_maps=exclude_info_maps,
                                                      format_option=format_option)
                raise e

            if not terminate_simulation_post_herd_generation:
                simulator = SimulationEngine()
                simulator.simulate()
        else:
            output_manager.add_error(
                "Validation complete",
                f"Data not valid for {str(metadata_file['path'])}, simulation not run",
                info_map,
            )
            output_manager.add_error(
                "No simulation run",
                f"Data not valid for {str(metadata_file['path'])}, simulation not run",
                info_map,
            )
        output_manager.save_results(
            output_dir,
            filters_dir,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
            csv_dir
        )
        output_manager.dump_all_nondata_pools(
            output_dir, exclude_info_maps, format_option
        )


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args() -> argparse.Namespace:
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser(description="RuFaS: Whole dairy farm simulation")
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)
    parser.add_argument(
        "-f",
        "--format-option",
        choices=["block", "inline", "verbose", "basic"],
        help="Select formatting option for variable_names.txt file",
    )
    parser.add_argument(
        "-g",
        "--no-graphics",
        help="Prevent graphics from generating",
        action="store_true",
    )
    parser.add_argument(
        "-G",
        "--graphics_dir",
        help="The saving directory for graphics",
        default="output/graphics/",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["errors", "warnings", "logs", "none"],
        default="none",
        help="Specify the log type to be printed",
    )
    parser.add_argument(
        "-c",
        "--clear-output",
        help="Clear output directory before running the simulation",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--exclude_info_maps",
        help="Exclude info_maps from the output",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--only-run-validation",
        help="Only validate the data, don't run a simulation",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--load-pool",
        help="Load the output manager's variables pool from provided path",
        default="",
    )
    parser.add_argument(
        "-O",
        "--output-dir",
        help="The saving directory for output",
        default="output/",
    )
    parser.add_argument(
        "-F",
        "--filters-dir",
        help="The directory for the files containing the keys for filtering",
        default="output/output_filters/",
    )
    parser.add_argument(
        "-C",
        "--csv-dir",
        help="The directory for the csv output files to be saved",
        default="output/CSVs/"
    )
    parser.add_argument(
        "-I",
        "--init_herd",
        help="Select this flag if you want to initialize the herd by generating a herd population through simulation.",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--save_animals",
        help="If the '--init_herd' flag is selected, choose this flag if you want to save the generated herd data into"
             " a JSON file.",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--save_animals_dir",
        help="If '--save_animals' flag is selected, use this flag to specify the directory to save the output animal "
             "population JSON file.",
        default="output/",
    )
    parser.add_argument(
        "-t",
        "--terminate_simulation_post_herd_generation",
        help="Select this flag if you only want to generate a herd, not continuing the simulation afterwards.",
        action="store_true",
    )
    parser.add_argument(
        "-gs",
        "--generate-schemas",
        help="Select this flag to generate input schemas for the data collection app instead of running a simulation.",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
