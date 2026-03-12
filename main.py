#!/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
import sys
import traceback
from pathlib import Path
from typing import Any, Optional

from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.task_manager import TaskManager


def main() -> None:
    """run RuFaS from the command line"""
    cmd_arguments = parse_gnu_args(sys.argv[1:])
    run_rufas(
        metapath = Path(cmd_arguments.path_to_metadata),
        out_dir = Path(cmd_arguments.output_dir),
        log_dir = Path(cmd_arguments.logs_dir),
        verbosity = LogVerbosity(cmd_arguments.verbose),
        keep_infos = not cmd_arguments.exclude_info_maps,
        preclean = cmd_arguments.clear_output,
        graphics = cmd_arguments.no_graphics,
        log = not cmd_arguments.suppress_log_files,
        metadepth = cmd_arguments.metadata_depth_limit
    )

# TODO: move this somewhere else and develop more.
def run_rufas(
        metapath: Path,
        out_dir: Path,
        log_dir: Path,
        verbosity: LogVerbosity = LogVerbosity("credits"),
        keep_infos: bool = True,
        preclean: bool = False,
        graphics: bool = False,
        log: bool = True,
        metadepth: Optional[int] = None,
) -> None:
    """function to run RuFaS model"""
    try:
        task_manager = TaskManager()
        task_manager.start(
            metadata_path = metapath,
            verbosity = verbosity,
            exclude_info_maps = not keep_infos,
            output_directory = out_dir,
            logs_directory = log_dir,
            clear_output_directory = preclean,
            produce_graphics = graphics,
            suppress_log_files = not log,
            metadata_depth_limit = metadepth,
        )
    except Exception as e:
        info_map = {"class": "No caller class", "function": main.__name__}
        output_manager = OutputManager()
        error_message = "This terminal error occurred during runtime. "
        error_message += traceback.format_exc()
        output_manager.add_error(
            f"Dumping all logs from main.py because of error '{e}'",
            error_message,
            info_map,
        )
        output_manager.create_directory(log_dir)
        output_manager.dump_all_nondata_pools(
            log_dir,
            not keep_infos,
            "block",
        )
        output_manager.add_error(
            "Early termination",
            "Unexpected early termination of the simulation. Please see logs for details.\n",
            info_map,
        )
        raise RuntimeError(
            f"An error occurred during simulation: {e} - check error logs in"
            f" '{out_dir}' directory for further details."
        )


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args(args: Any | None = None) -> argparse.Namespace:
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
        "-o",
        "--output-dir",
        help="The saving directory for output",
        default="output/",
    )
    parser.add_argument(
        "-s",
        "--suppress-log-files",
        help="Prevents logs from the Task Manager being written to files",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--logs-dir",
        help="The directory for saving log files too",
        default="output/logs",
    )
    parser.add_argument(
        "-m", "--metadata-depth-limit", help="Overrides the default metadata depth limit in the Input Manager", type=int
    )
    parser.add_argument(
        "-p",
        "--path-to-metadata",
        help="Path to the task manager metadata that will determine the tasks run",
        default="input/task_manager_metadata.json",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
