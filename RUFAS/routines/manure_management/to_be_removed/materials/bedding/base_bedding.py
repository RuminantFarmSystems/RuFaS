"""
RUFAS: Ruminant Farm Systems Model

File name: bedding_classes.py

Description: This module contains the implementation of the base Bedding Class. 
The bedding is a material component of pens and Manure, but may also be found in 
a SandSeparator.

Author(s): Yunus Mohammed, ymm26@cornell.edu
"""


class Bedding:
    """
    Description
    ------------
    An instance of Bedding represents a bedding material from a pen, which may 
    be found in several other components described above. It has the 
    aggregateBedding() method for adding to beddings together. Each instance has 
    the following attributes and their corresponding invariants, getters and 
    setters.

    Attributes
    ----------
    Attribute _density: The density of this bedding
    Invariant: A positive float with units of kg/m3

    Attribute _mass: The mass of the bedding
    Invariant: A non-negative float with units of kg

    Attribute _volume: The volume of the bedding
    Inavariant: A nom-negative float with units of m3
    
    """   

    def __init__(self, mass, density):
        """
        Initializes a Bedding Object

        Parameter density: The density of the bedding.
        Precondition: A positive float with units of kg/m3

        Parameter mass: The mass of the bedding
        Precondition: A non-negative float with units of kg
        """
        self._density = density
        self._mass = mass
        self._setVolume()

    def aggregateBedding(self, other):
        """
        Aggregates another bedding material with this bedding material.

        Parameter other: The other bedding being added to this Bedding
        Preconditon: other must be a Bedding. 
        """
        if not other._mass:
            return

        mass = self._mass + other._mass
        volume = self._volume + other._volume

        self._density = mass / volume
        self._mass = mass
        self._setVolume()


    #getters
    def getMass(self):
        """
        Returns the mass of this bedding
        """
        return self._mass
    
    def getVolume(self):
        """
        Returns the volume of this bedding
        """
        return self._volume

    #setters    
    def setMass(self, mass):
        """
        Sets the _mass attribute to mass.

        Parameter mass: The mass of the bedding
        Precondition: A non-negative float with units of kg
        """
        self._mass = mass
        self._setVolume()

    def _setVolume(self):
        """
        Sets the _volume of this Bedding based on the _density and _mass.
        """
        self._volume = self._mass / self._density