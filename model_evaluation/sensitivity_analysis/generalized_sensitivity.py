"""
This module will contain the functions needed to apply global sensitivity analyses to the generalized case.

The workhorse of this module is the SALib python package (Herman et al. 2023): https://salib.readthedocs.io/en/latest/

This module uses functional programming instead of object-oriented. This may change down the line.
"""
from SALib import ProblemSpec
from typing import List, Tuple, Optional

def cause_problems(parameters: List[str], bounds: List[Tuple[float, float]],
                   outputs: Optional[List[str]] = None,
                   ) -> ProblemSpec:
    pass
