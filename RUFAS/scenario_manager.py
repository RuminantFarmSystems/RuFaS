# !/usr/bin/env python3


from pathlib import Path
from typing import List, TypedDict


class MetadataPaths(TypedDict):
    """
    Contains the path(s) to the metadata file(s) that will run when a user runs a simulation and the
    prefix(es) the user wants to use to designate the output files from this simulation.

    main.py will import the METADATA_PATHS variable and class and use it to provide execute_simulations() with
    the list of metadata files and prefixes that they want to be used to run simulations.

    Attributes
    ----------
    prefix : str
        The prefix specifying the metadata file used to run the scenario. Will be used to
        generate a name for each of the output files for the scenario run with this metadata path.
    path : Path
        The path to the metadata file used for a simulation.

    Examples
    --------
    Single simulation:
        METADATA_PATHS: List[MetadataPaths] = [{"prefix": "default_scenario",
                                                "path": Path('input/metadata/default_metadata.json')},
                                              ]
        This will use the default_metadata.json file to point to the input
        files specified for this simulation scenario. All output files will have the "default_scenario"
        prefix: e.g. "default_scenario_errors_09-Oct...", "default_scenario_logs_09-Oct...", etc.

    Multiple simulations:
        METADATA_PATHS: List[MetadataPaths] = [{"prefix": "default_scenario",
                                                "path": Path('input/metadata/default_metadata.json')},
                                               {"prefix": "ARL_scenario",
                                                "path": Path('input/metadata/ARL_metadata.json')},
                                              ]
        This will run 2 simulations back to back - the first simulation will use the default_metadata.json
        file to point to one set of input files and will save the generated output files with the "default_scenario"
        prefix. The second simulation will run immediately after with no extra input from the user and will
        use the ARL_metadata.json file and save its output files with the "ARL_scenario" prefix.
    """
    prefix: str
    path: Path


METADATA_PATHS: List[MetadataPaths] = [{"prefix": "ManureTest",
                                        "path": Path('input/metadata/manure_test_metadata.json')}
                                       ]
