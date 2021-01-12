"""
RUFAS: Ruminant Farm Systems Model

File name: sand_bedding.py

Description: This module contains the implementation of the SandBedding Class.

Author(s): Yunus Mohammed, ymm26@cornell.edu
"""

from .base_bedding import *

class SandBedding(Bedding):
    """
    Description
    ------------
    Inherits from the Bedding Class. Has a default density of 1500 kg/m3
    
    Attributes
    ----------
    Has all the attributes of Bedding objects
    """   

    def __init__(self, mass, density=1500):
        """
        Initializes a Bedding Object

        Parameter density: The density of the sand bedding. Defaults to 1500 kg/m3
        Precondition: A positive float with units of kg/m3

        Parameter mass: The mass of the sand bedding
        Precondition: A non-negative float with units of kg
        """
        super().__init__(mass,density)

 