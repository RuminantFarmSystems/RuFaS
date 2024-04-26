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


METADATA_PATHS: List[MetadataPaths] = [
    {"prefix": "default", "path": Path("input/metadata/c1f1_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f1_wcrops_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f2_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f2_wcrops_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f3_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f3_wcrops_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f4_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c1f5_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f10_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f11_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f12_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f13_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f14_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f15_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f16_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f17_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f18_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f19_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f1_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f20_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f21_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f22_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f23_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f24_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f25_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f26_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f27_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f28_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f2_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f3_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f3_wcrops_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f4_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f5_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f6_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f6_wcrops_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f7_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f8_metadata.json")},
    {"prefix": "default", "path": Path("input/metadata/c2f9_metadata.json")},
]
