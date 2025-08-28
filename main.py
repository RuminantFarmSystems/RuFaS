# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
import sys
from pathlib import Path
from typing import Any

from RUFAS.launching import launch_rufas


def main() -> None:
    cmd_arguments = parse_gnu_args(sys.argv[1:])
    launch_rufas(
        path_to_metadata=Path(cmd_arguments.path_to_metadata),
        verbose=cmd_arguments.verbose,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
        output_dir=Path(cmd_arguments.output_dir),
        logs_dir=Path(cmd_arguments.logs_dir),
        clear_output=cmd_arguments.clear_output,
        no_graphics=cmd_arguments.no_graphics,
        suppress_log_files=cmd_arguments.suppress_log_files,
        metadata_depth_limit=cmd_arguments.metadata_depth_limit,
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
