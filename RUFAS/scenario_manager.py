# !/usr/bin/env python3

"""
This file contains the path(s) to the metadata file(s) that will run when a user runs a simulation.

main.py will import the METADATA_PATHS variable and use it to provide execute_simulations() with
the list of metadata files that they want to be used to run simulations.

Examples
--------
Single simulation:
    METADATA_PATHS = ['input/metadata/default_metadata.json']
    This will use the default_metadata.json file to point to the input
    files specified for this simulation scenario.
Multiple simulations:
    METADATA_PATHS = ['input/metadata/default_metadata.json', 'input/metadata/ARL_metadata.json']
    This will run 2 simulations back to back - the first simulation will use the default_metadata.json
    file to point to one set of input files. The second simulation will run immediately after with no
    extra input from the user and will use the ARL_metadata.json file
"""

from pathlib import Path
from typing import List, TypedDict


class MetadataPaths(TypedDict):
    prefix: str
    path: Path


METADATA_PATHS: List[MetadataPaths] = [{"prefix": "default_scenario",
                                        "path": Path('input/metadata/default_metadata.json')},
                                       {"prefix": "ARL_scenario",
                                        "path": Path('input/metadata/ARL_metadata.json')},
                                       ]
