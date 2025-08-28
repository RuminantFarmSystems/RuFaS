# !/usr/bin/env python3

"""
This file includes the entry point function to RuFaS.
"""
import traceback
from pathlib import Path

from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.task_manager import TaskManager


def launch_rufas(
        path_to_metadata: Path,
        verbose: str,
        exclude_info_maps: bool,
        output_dir: Path,
        logs_dir: Path,
        clear_output: bool,
        no_graphics: bool,
        suppress_log_files: bool,
        metadata_depth_limit: int | None,
) -> None:
    """Launch simulation with RuFaS.

    Parameters
    ----------
    path_to_metadata
        Path to the metadata file that contains task management inputs.
    verbose
        verbosity type in :func:`RUFAS.output_manager.LogVerbosity`.
    exclude_info_maps
        Flag to exclude information maps.
    output_dir
        Path to the directory where outputs will be saved.
    logs_dir
        Path to the directory where logs from the Task Manager will be saved.
    clear_output
        Whether to clear the output directory.
    no_graphics
        Whether not to produce graphics
    suppress_log_files
        Whether to write logs from the Task Manager to output files.
    metadata_depth_limit
        Override value for maximum metadata properties depth set in Input Manager.

    """

    try:
        task_manager = TaskManager()
        task_manager.start(
            metadata_path=path_to_metadata,
            verbosity=LogVerbosity(verbose),
            exclude_info_maps=exclude_info_maps,
            output_directory=output_dir,
            logs_directory=logs_dir,
            clear_output_directory=clear_output,
            produce_graphics=not no_graphics,
            suppress_log_files=suppress_log_files,
            metadata_depth_limit=metadata_depth_limit,
        )
    except Exception as e:
        info_map = {
            "class": "No caller class",
            "function": launch_rufas.__name__,
        }
        output_manager = OutputManager()
        error_message = "This error occurred during runtime. "
        error_message += traceback.format_exc()
        output_manager.add_error(
            f"Dumping all logs from main.py because of error '{e}'",
            error_message,
            info_map,
        )
        output_manager.create_directory(Path(logs_dir))
        output_manager.dump_all_nondata_pools(
            Path(logs_dir),
            exclude_info_maps,
            "block",
        )
        output_manager.add_error(
            "Early termination",
            "Unexpected early termination of the simulation. Please see logs for details.\n",
            info_map,
        )
        raise RuntimeError(
            f"An error occurred during simulation: {e} - check error logs in"
            f" '{output_dir}' directory for further details."
        )
