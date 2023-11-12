# !/usr/bin/env python3
import argparse
from pathlib import Path
import sys
from typing import Tuple
from multiprocessing import Pool

from RUFAS.scenario_manager import METADATA_PATHS, MetadataPath

import config.global_variables
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.util import Utility


def main():
    cmd_arguments = parse_gnu_args()
    run_rufas(
        produce_graphics=cmd_arguments.produce_graphics,
        format_option=cmd_arguments.format_option,
        verbose=LogVerbosity(cmd_arguments.verbose),
        clear_output=cmd_arguments.clear_output,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
        only_run_validation=cmd_arguments.only_run_validation,
        graphics_dir=Path(cmd_arguments.graphics_dir),
        load_pool=cmd_arguments.load_pool,
    )


def run_rufas(
    produce_graphics: bool = True,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
    clear_output: bool = False,
    exclude_info_maps: bool = False,
    only_run_validation: bool = False,
    graphics_dir: Path = Path(""),
    load_pool: bool = False,
) -> None:
    """Main function to run RuFaS, with options.

    Parameters
    ----------
    produce_graphics : bool, optional, default=True
        Produce graphics after simulation.
    format_option : str, optional, default="verbose"
        Format for variable_names.txt output file.
    verbose : bool, optional, default=True
        Print progress messages while simulation is running.
    clear_output : bool, optional, default=False
        Clear output directory before running the simulation.
    exclude_info_maps : bool, optional, default=False
        Exclude info_maps from the output.
    only_run_validation : bool, optional, default=False
        Validate input data and don't run a simulation.
    graphics_dir : Path, optional, default=Path("")
        The directory for saving graphics.
    load_pool : bool, optional, default=False
        Load json file into Output Manager variables pool for processing.
    """
    sys.stdout.write("RuFaS: Ruminant Farm Systems Model 2023\n")

    if load_pool:
        run_load_vars_pool(
            exclude_info_maps,
            format_option,
            produce_graphics,
            graphics_dir,
            clear_output,
        )
        return

    if clear_output:
        clear_output_dir()

    if only_run_validation:
        args_generator: Tuple[MetadataPath, bool, str, LogVerbosity] = (
            (metadata_file, exclude_info_maps, format_option, verbose)
            for metadata_file in METADATA_PATHS
        )
        with Pool() as pool:
            results = pool.imap_unordered(run_validation_packed, args_generator)
            for _ in results:
                pass
    else:
        args_generator: Tuple[MetadataPath, bool, bool, Path, str, LogVerbosity] = (
            (
                metadata_file,
                exclude_info_maps,
                produce_graphics,
                graphics_dir,
                format_option,
                verbose,
            )
            for metadata_file in METADATA_PATHS
        )
        with Pool() as pool:
            results = pool.imap_unordered(execute_simulation_packed, args_generator)
            for _ in results:
                pass


def clear_output_dir(vars_file_path: Path = None) -> None:
    """Clears the output directory if vars_file_path not in output directory.

    Parameters
    ----------
    vars_file_path : Path, optional, default=None
        Path to file used to load Output Manager vars pool.
    """
    info_map = {
        "class": "No caller class",
        "function": clear_output_dir.__name__,
    }
    output_manager = OutputManager()
    output_dir = Path(config.global_variables.OUT_DIR)
    is_file_found_in_dir = is_file_in_dir(output_dir, vars_file_path)
    if is_file_found_in_dir:
        output_manager.add_error(
            "Can't clear output directory",
            f"{vars_file_path} in output directory.",
            info_map,
        )
    else:
        keep_list = [".keep", "output_filters"]
        Utility.empty_dir(output_dir, keep=keep_list)
        output_manager.add_log(
            "Output directory cleared",
            "No conflicts to clearing output directory.",
            info_map,
        )


def is_file_in_dir(
    dir_path: Path = Path(config.global_variables.OUT_DIR), file_path: Path = None
) -> bool:
    """Checks if a file path is in the provided directory.

    Parameters
    ----------
    dir_path : Path, optional, default=Path(config.global_variables.OUT_DIR)
        Path to the directory to be checked.
    file_path : Path, optional, default=None
        Path to file to be checked.
    """
    if file_path is None:
        return False
    file_path = file_path.resolve()
    directory_path = dir_path.resolve()

    return directory_path == file_path or directory_path in file_path.parents


def run_load_vars_pool(
    exclude_info_maps: bool = False,
    format_option: str = "verbose",
    produce_graphics: bool = True,
    graphics_dir: Path = Path(""),
    clear_output: bool = False,
) -> None:
    """Instantiates Output Manager and triggers loading of the variables pool from the provided file path
    for post-processing.

    Parameters
    ----------
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics : bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path, optional
        The directory for saving graphics.
    clear_output : bool, optional
        Flag for whether or not the user wants to clear the output directory.
    """
    vars_file_path = Path(input("Enter path to variables json file: ").strip())
    if clear_output:
        clear_output_dir(vars_file_path)
    output_manager = OutputManager()
    output_manager.flush_pools()
    output_manager.load_variables_pool_from_file(vars_file_path)
    output_manager.set_metadata_prefix("reload")
    output_manager.save_results(
        Path(r"output"),
        Path(r"output/output_filters/"),
        exclude_info_maps,
        produce_graphics,
        graphics_dir,
    )
    output_manager.dump_all_nondata_pools(r"output", exclude_info_maps, format_option)


def run_validation_packed(args: Tuple[MetadataPath, bool, str, LogVerbosity]) -> None:
    """
    A wrapper function for 'run_validation' to facilitate parallel processing.

    This function is designed to be compatible with multiprocessing's imap_unordered method.
    It takes a single tuple argument that encapsulates all the arguments needed for the
    'run_validation' function and unpacks them for processing.

    Parameters
    ----------
    args : Tuple[MetadataPath, bool, str, LogVerbosity]
        A tuple containing the arguments for the 'run_validation' function.
        - metadata_file: MetadataPath - The path of the metadata file to be processed.
        - exclude_info_maps: bool - Flag to indicate whether information maps should be excluded.
        - format_option: str - The format option for output files.
        - verbose: LogVerbosity - The verbosity level for logging.
    """
    run_validation(*args)


def run_validation(
    metadata_file: MetadataPath,
    exclude_info_maps: bool = False,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
) -> None:
    """Instantiates I/O Managers and triggers validation of input data.

    Parameters
    ----------
    metadata_files : MetadataPath
        The list of Paths to the metadata files the user entered with which to run the simulation.
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    """
    info_map = {
        "class": "No caller class",
        "function": run_validation.__name__,
    }
    output_manager = OutputManager()
    input_manager = InputManager()
    output_manager.set_metadata_prefix(metadata_file["prefix"])
    output_manager.add_log(
        "Validation only",
        "***Only validating data, no simulation will follow.***",
        info_map,
    )
    output_manager.set_log_verbose(verbose)
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
    output_manager.dump_all_nondata_pools(r"output", exclude_info_maps, format_option)


def execute_simulation_packed(
    args: Tuple[MetadataPath, bool, bool, Path, str, LogVerbosity]
) -> None:
    """
    A wrapper function for 'execute_simulations' designed for parallel processing.

    This function adapts 'execute_simulations' to be compatible with multiprocessing's
    imap_unordered method by accepting a single tuple of arguments. It unpacks these
    arguments and forwards them to 'execute_simulations'.

    Parameters
    ----------
    args : Tuple[MetadataPath, bool, bool, Path, str, LogVerbosity]
        A tuple containing the arguments for the 'execute_simulation' function.
        - metadata_file: MetadataPath - The path of the metadata file for simulation.
        - exclude_info_maps: bool - Flag to exclude information maps in the results.
        - produce_graphics: bool - Flag to determine if graphics should be produced.
        - graphics_dir: Path - Directory path for saving graphics.
        - format_option: str - Formatting option for output files.
        - verbose: LogVerbosity - Verbosity level for logging.
    """
    execute_simulation(*args)


def execute_simulation(
    metadata_file: MetadataPath,
    exclude_info_maps: bool = False,
    produce_graphics: bool = True,
    graphics_dir: Path = Path(""),
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : MetadataPath
        A list of custom TypedDict objects including the specified prefix for the save_results output file
        and the path to the metadata file.

    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics: bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path, optional
        The directory for saving graphics.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    """
    info_map = {
        "class": "No caller class",
        "function": execute_simulation.__name__,
    }
    sys.stdout.write(f"{[metadata_file['prefix']]}Simulating...\n")
    output_manager = OutputManager()
    input_manager = InputManager()
    output_manager.set_log_verbose(verbose)
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
        Path(r"output"),
        Path(r"output/output_filters/"),
        exclude_info_maps,
        produce_graphics,
        graphics_dir,
    )
    output_manager.dump_all_nondata_pools(r"output", exclude_info_maps, format_option)


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
        help="Disable graphics generation",
        action="store_false",
        dest="produce_graphics",
    )
    parser.add_argument(
        "-G",
        "--graphics_dir",
        help="The saving directory for graphics",
        default="graphics",
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
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
