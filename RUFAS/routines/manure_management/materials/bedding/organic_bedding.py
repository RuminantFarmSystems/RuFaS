"""
RUFAS: Ruminant Farm Systems Model

File name: organic_bedding.py

Description: This module contains the implementation of the OrganicBedding 
Class. 

Author(s): Yunus Mohammed, ymm26@cornell.edu
"""

from base_bedding import *

class OrganicBedding(Bedding):
    """
    Description
    ------------
    Inherits from the Bedding Class. Has a default density of 250 kg/m3

    Attributes
    ----------
    Has all the attributes of Bedding objects  
    """   

    def __init__(self, mass, density=250):
        """
        Initializes a Bedding Object

        Parameter density: The density of the organic bedding. Defaults to
        250 kg/m3
        Precondition: A positive float with units of kg/m3

        Parameter mass: The mass of the organic bedding
        Precondition: A non-negative float with units of kg
        """
        super().__init__(mass,density)


    def aggregateBedding(self, other):
        """
        Aggregates another bedding material with this bedding material.

        Parameter other: The other bedding being added to this OrganicBedding
        Preconditon: other must be an OrganicBedding. 
        """
        assert isinstance(other, OrganicBedding), "Argument must be an OrganicBedding, and its not"
        super().aggregateBedding(other)
