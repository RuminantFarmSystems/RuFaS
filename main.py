# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
import traceback
from pathlib import Path

from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.task_manager import TaskManager


def main() -> None:
    cmd_arguments = parse_gnu_args()
    try:
        task_manager = TaskManager()
        task_manager.start(
            "input/metadata/task_manager_metadata.json",
            verbosity=LogVerbosity(cmd_arguments.verbose),
            exclude_info_maps=cmd_arguments.exclude_info_maps,
            output_directory=Path(cmd_arguments.output_dir),
            clear_output_directory=cmd_arguments.clear_output,
            produce_graphics=not cmd_arguments.no_graphics,
        )
    except Exception as e:
        info_map = {
            "class": "No caller class",
            "function": main.__name__,
        }
        output_manager = OutputManager()
        error_message = "This terminal error occurred during runtime. "
        error_message += traceback.format_exc()
        output_manager.add_error(
            f"Dumping all logs from main.py because of error '{e}'",
            error_message,
            info_map,
        )
        output_manager.dump_all_nondata_pools(
            cmd_arguments.output_dir,
            cmd_arguments.exclude_info_maps,
            "block",
        )
        output_manager.add_error(
            "Early termination",
            "Unexpected early termination of the simulation. Please see logs for details.\n",
            info_map,
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
    csv_dir: Path,
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
        csv_dir,
    )
    output_manager.dump_all_nondata_pools(output_dir, exclude_info_maps, format_option)


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args() -> argparse.Namespace:
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser(description="RuFaS: Whole dairy farm simulation")
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)
    parser.add_argument(
        "-g",
        "--no-graphics",
        help="Prevents graphics from generating",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["errors", "warnings", "logs", "credits", "none"],
        default="credits",
        help="Specifies the log type to be printed",
    )
    parser.add_argument(
        "-c",
        "--clear-output",
        help="CAUTION! Clears output directory before running the simulation",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--exclude_info_maps",
        help="Exclude info_maps from the output",
        action="store_true",
    )
    parser.add_argument(
        "-O",
        "--output-dir",
        help="The saving directory for output",
        default="output/",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
