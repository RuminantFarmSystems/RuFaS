# ---- Introduction ----
"""
This file is meant to suggest a restructure of RUFAS's input system that allows for a single point
of entry for model input parameters. This structure is highly flexible and allows for the following
use cases:

    1) changing inputs on the fly, either with command-line options^* or directly from the main
    function within python scripts.

    2) setting specific parameters with config file(s), similar to the way RUFAS already handles JSON inputs but
    the manually specified arguments would take precedence, then the config files, then defaults (below).
    Ideally, these wouldn't have to be JSON files, but more accessible and simple. Perhaps like classic config files of
    the form:

        VAR1 value
        VAR2 value
        LONG_VAR long_value
        AN_EXTREMELY_LONG_VARIABLE_SINCE_THERE_ARE_SO_MANY value
        LIST_VAR val_1 val_2 val_3 ... val_n
        PATH_TO_SUBCONFIG path

    3) reverting to sensible default values (stored in JSON files), expecting users to specify the things
    that they need/want to change.

For simplicity, I've used bare functions and dictionaries where the final form would have
functions placed in their appropriate classes (largely InputManager) and dictionaries would become
more appropriate objects (Struct, class, etc.). Many of the functions are simply placeholders, without
any code, but they have docstrings describing their expected functionality.

Footnotes:
^* main.py already provides access to some command-line options.
"""

# ---- Import statements ----
import os.path
import sys
from pathlib import Path
from typing import NoReturn, Optional, Any

# ---- Global variables (for demonstration only) ----
JSON_PATH_DEFAULT = "input/task_manager_metadata.json"
CONFIG_PATH_DEFAULT = "input/config/config.json"

# ---- Functions ----

def main(**man_args) -> None:
    """
    Run the RUFAS model, with the ability to provide input values in scripts or from the command line.

    :param man_args: (optional) manually-specified named arguments to rufas. Values of provided will supersede
    those specified in config files and model defaults and are superseded by gnu arguments, which have the
    highest priority (see parse_gnu_args below).
    """

    # check for single run (or other task manager stuff)
    if "single_run" in man_args.keys():
        single_run = man_args.pop("single_run")
    else:
        single_run = False

    # parse command line args
    gnu_args = parse_gnu_args(cmdargs = sys.argv[1:])

    # check for user-specified config files
    if "config_path" in man_args:
        config_path = man_args["config_path"]
    elif os.path.isfile(CONFIG_PATH_DEFAULT):
        config_path = CONFIG_PATH_DEFAULT
    else:
        config_path = None

    # combine all the arguments, reverting to defaults where not provided
    all_args = combine_all_inputs(
        gnu_args = gnu_args,
        man_args = man_args,
        config_path = config_path,
        fill_defaults = True
    )

    # pass the arguments to the model
    if single_run:
        run_model(**all_args)
    else:
        multirun_model(**all_args)
        ## OR some other task-manager run type


def run_model(**kwargs) -> None:
    """
    perform a **single** run of the rufas model
    :param kwargs: all input parameters for RUFAS

    Note: I think it is important that there is a function for running RUFAS in the simplest way (only once) to
    facilitate shell scripting, distributed computing, etc. Other functions (and the task manager) can then determine
    how many times and under what additional contexts the model should run.
    """
    pass


def multirun_model(**kwargs) -> None:
    """perform a multi-run of RUFAS"""
    pass


def combine_all_inputs(
        gnu_args: Optional[dict] = None,
        man_args: Optional[dict] = None,
        config_path: Optional[Path | str] = None,
        fill_defaults: bool = True
) -> dict:
    """
    collect all inputs for the RUFAS model
    :param gnu_args: (optional) named GNU inputs
    :param man_args: (optional) named input for the RUFAS model.
    :param config_path: (optional) the path to the JSON file to be parsed.
    :param fill_defaults: should defaults be used to fill in parameters not specified?
    :return: a dictionary with all inputs
    """

    # first, check for command line inputs
    if gnu_args is None:
        gnu_args = {}
    else:
        gnu_args = parse_inputs(**gnu_args)

    # then check for manual inputs
    if man_args is None:
        man_args = {}
    else:
        man_args = parse_inputs(**man_args)

    # add in novel manual inputs
    all_args = merge_arg_dicts(gnu_args, man_args)

    # check for JSON inputs (config files)
    if config_path is None:
        config_args = {} # use default
    else:
        config_args = parse_config_inputs(path = config_path)

    all_args = merge_arg_dicts(all_args, config_args)

    # get any remaining arguments from the defaults
    if fill_defaults:
        default_args = parse_default_args()

        all_args = merge_arg_dicts(all_args, default_args)

    return all_args


def merge_arg_dicts(d1, d2) -> dict:
    """
    merge items from two argument dictionaries
    :param d1: the highest priority dictionary (all items kept)
    :param d2: the lowest priority dictionary (items not in d1 kept)
    :return: a dictionary containing all items in d1 and any items from d2 not contained in d1
    """
    novel = {k: v for k, v in d2.items() if k not in d1.keys()}
    out = {**d1, **novel} # dictionary merge syntax (Python >= 3.5)
    return out


def parse_inputs(**kwargs) -> dict:
    """
    parse keyword arguments and convert them into an appropriate dictionary of RUFAS arguments.
    This function may not be needed, but I wanted to allow for preprocessing/reformatting inputs
    :param kwargs: arguments to be parsed
    :return: a conformant dictionary of RUFAS arguments
    """
    pass


def parse_config_inputs(path: Path | str) -> dict:
    """
    parse RUFAS inputs from a specified config file
    :param path: path to the top-level config file
    :return: a conformant dictionary of RUFAS arguments
    """
    pass


def parse_gnu_args(cmdargs: Optional[Any] = None) -> dict:
    """
    parse command line arguments to RUFAS
    :param cmdargs: arguments from the command line (i.e., sys.argv[1:])
    :return: a conformant dictionary of RUFAS arguments

    Note: this method would be an extension of the parse_gnu_args that already exists in main.py
    but with access to more (most?) arguments.
    """
    pass


def parse_default_args(path: Path | str = JSON_PATH_DEFAULT) -> dict:
    """
    parse the default configuration files for RUFAS inputs
    :param path: path to the top-level default config file
    :return: a conformant dictionary of RUFAS arguments
    """
    pass


# ---- Example script code ----
if __name__ == "__main__":
    # run with defaults
    main()
    # run again, this time without logs and different configs
    main(write_logs = False, config_path = "configs/different_config.json")
    # etc.
    # ...